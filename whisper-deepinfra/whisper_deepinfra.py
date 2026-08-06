#!/usr/bin/env python3
"""
whisper-deepinfra: transcribe (o traduce) audio con openai/whisper-large-v3-turbo
en DeepInfra.

Un solo archivo, biblioteca estandar de Python. No necesita pip install de nada.
Corre igual en Linux, macOS y Windows.

La llave se busca en este orden:
  1. Variable de entorno DEEPINFRA_API_KEY
  2. Archivo ~/.config/deepinfra/credentials
Si no esta en ninguno de los dos, sale con instrucciones de como guardarla.

Uso:
  python3 whisper_deepinfra.py grabacion.mp3
  python3 whisper_deepinfra.py junta.m4a -o junta.txt --idioma es
  python3 whisper_deepinfra.py entrevista.wav --tarea translate -o english.txt
  python3 whisper_deepinfra.py larga.mp3 --simulacion
  python3 whisper_deepinfra.py --estado
  echo "<llave>" | python3 whisper_deepinfra.py --guardar-llave

Audios de mas de 25 MB: el script los comprime a 16 kHz mono con ffmpeg y, si
aun asi no caben, los parte en tramos y une el texto. No hay que hacerlo a mano.

Log de llamadas en ~/.cache/whisper-deepinfra.log
"""
import argparse
import http.client
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ENDPOINT = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3-turbo"
PRECIO_POR_MINUTO = 0.00020  # USD por minuto de audio

# El limite documentado de DeepInfra es 25 MB por llamada. Se manda con margen
# porque el cuerpo multipart agrega encabezados encima del archivo.
LIMITE_ENVIO = 24 * 1024 * 1024

# Al comprimir se usa mp3 mono de 32 kbps: unos 4000 bytes por segundo de audio.
BITRATE_COMPRIMIDO = "32k"
BYTES_POR_SEGUNDO = 4000
SEGUNDOS_POR_TRAMO = 4800  # ~19 MB por tramo, con holgura bajo el limite

# Umbral para sospechar de una transcripcion corta. El habla normal da entre 12
# y 15 caracteres por segundo, asi que 1 por segundo es un piso muy por debajo
# de cualquier grabacion con voz: solo lo cruza un audio casi mudo, un idioma
# forzado que no corresponde, o una respuesta truncada. Debajo de medio minuto
# no se revisa, porque en media frase caben pocos caracteres y es legitimo.
CARACTERES_MINIMOS_POR_SEGUNDO = 1.0
SEGUNDOS_MINIMOS_PARA_REVISAR = 30

RUTA_LOG = Path.home() / ".cache" / "whisper-deepinfra.log"
RUTA_CREDENCIALES = Path.home() / ".config" / "deepinfra" / "credentials"

FORMATOS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".opus", ".wav", ".webm"}

def _comando_guardar():
    """El comando exacto para guardar la llave, en el sistema donde corre."""
    aqui = Path(__file__).resolve()
    if os.name == "nt":
        return f"'TU_LLAVE' | python \"{aqui}\" --guardar-llave"
    return f"printf '%s' 'TU_LLAVE' | python3 \"{aqui}\" --guardar-llave"


INSTRUCCIONES_LLAVE = f"""No hay llave de DeepInfra configurada.

Como conseguirla, son dos minutos:
  1. Entra a https://deepinfra.com y crea tu cuenta (Google o GitHub sirven).
  2. Ve a Dashboard -> API Keys -> New API Key.
  3. Copia la llave.

Como guardarla, sin que quede en el historial del shell:

    {_comando_guardar()}

Queda en {RUTA_CREDENCIALES}, con permisos solo para tu usuario, y la reusan
las demas skills de DeepInfra."""


def preparar_salida():
    """Fuerza UTF-8 en stdout y stderr.

    En Windows la salida redirigida sale en cp1252, que no sabe codificar buena
    parte de Unicode: imprimir la transcripcion reventaba con UnicodeEncodeError
    DESPUES de haber pagado la llamada a la API, o sea perdiendo el texto.
    """
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def codificacion_de_salida():
    """UTF-8 con BOM en Windows, sin BOM en el resto.

    Sin BOM, un .txt en Windows lo malinterpretan PowerShell 5.1 y Excel, que
    asumen la pagina de codigos local y dejan la transcripcion llena de basura.
    """
    return "utf-8-sig" if os.name == "nt" else "utf-8"


def morir(msg, codigo=1):
    print(f"whisper-deepinfra: {msg}", file=sys.stderr)
    sys.exit(codigo)


# --------------------------------------------------------------------------
# Llave
# --------------------------------------------------------------------------

def leer_llave_de_archivo():
    """Lee DEEPINFRA_API_KEY del archivo de credenciales.

    El archivo es sourceable por shell (lineas 'export CLAVE="valor"') para que
    tambien sirva desde bash, pero aqui se parsea a mano porque en Windows no
    hay shell que lo sourcee.
    """
    if not RUTA_CREDENCIALES.exists():
        return None
    try:
        texto = RUTA_CREDENCIALES.read_text(encoding="utf-8")
    except OSError:
        return None
    for linea in texto.splitlines():
        linea = linea.strip()
        if linea.startswith("export "):
            linea = linea[len("export "):].strip()
        nombre, signo, valor = linea.partition("=")
        # El nombre tiene que ser exacto y traer su signo de igual. Con un
        # startswith suelto, un DEEPINFRA_API_KEY_VIEJA de al lado devolvia la
        # llave equivocada y el error aparecia hasta el HTTP 401, mandando a
        # revisar la llave buena en vez de la de junto.
        if signo != "=" or nombre.strip() != "DEEPINFRA_API_KEY":
            continue
        valor = valor.strip().strip('"').strip("'")
        if valor:
            return valor
    return None


def obtener_llave():
    """Devuelve (llave, origen). Sale con instrucciones si no hay ninguna."""
    del_entorno = os.environ.get("DEEPINFRA_API_KEY", "").strip()
    if del_entorno:
        return del_entorno, "entorno"
    del_archivo = leer_llave_de_archivo()
    if del_archivo:
        return del_archivo, str(RUTA_CREDENCIALES)
    morir(INSTRUCCIONES_LLAVE)


def restringir_permisos(ruta, modo=0o600):
    """Deja la ruta accesible solo por su dueño, en los dos sistemas.

    Un directorio necesita 0o700, no 0o600: sin el bit de ejecucion no se puede
    entrar a el y el archivo de adentro queda ilegible.
    """
    try:
        os.chmod(ruta, modo)
    except OSError:
        pass
    if os.name == "nt":
        # En Windows os.chmod solo mueve el bit de solo-lectura, no los permisos
        # reales. icacls si corta la herencia y deja al usuario actual.
        usuario = os.environ.get("USERNAME", "")
        if usuario:
            try:
                subprocess.run(
                    ["icacls", str(ruta), "/inheritance:r",
                     "/grant:r", f"{usuario}:F"],
                    capture_output=True, timeout=20, check=False,
                )
            except (OSError, subprocess.SubprocessError):
                pass


def guardar_llave():
    """Lee la llave de stdin y la escribe en el archivo de credenciales.

    Se lee de stdin a proposito: pasada como argumento quedaria en el historial
    del shell y en la lista de procesos.
    """
    if sys.stdin.isatty():
        print("Pega la llave de DeepInfra y dale Enter:", file=sys.stderr)
    llave = sys.stdin.read().strip()
    if not llave:
        morir("no llego ninguna llave por stdin.")
    if len(llave) < 12 or any(c.isspace() for c in llave):
        morir(f"eso no parece una llave de DeepInfra (llegaron {len(llave)} "
              "caracteres, con espacios o muy corta). Vuelve a copiarla.")

    RUTA_CREDENCIALES.parent.mkdir(parents=True, exist_ok=True)
    restringir_permisos(RUTA_CREDENCIALES.parent, 0o700)

    otras = []
    if RUTA_CREDENCIALES.exists():
        for linea in RUTA_CREDENCIALES.read_text(encoding="utf-8").splitlines():
            if "DEEPINFRA_API_KEY" not in linea:
                otras.append(linea)

    cuerpo = "\n".join(otras + [f'export DEEPINFRA_API_KEY="{llave}"']).strip() + "\n"
    RUTA_CREDENCIALES.write_text(cuerpo, encoding="utf-8")
    restringir_permisos(RUTA_CREDENCIALES)

    print(f"Llave guardada en {RUTA_CREDENCIALES} ({llave[:4]}...{llave[-4:]}, "
          f"{len(llave)} caracteres).")
    return 0


# --------------------------------------------------------------------------
# ffmpeg / ffprobe
# --------------------------------------------------------------------------

def duracion_segundos(ruta):
    """Duracion con ffprobe. None si ffprobe no esta o el archivo no se deja leer."""
    if not shutil.which("ffprobe"):
        return None
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(ruta)],
            capture_output=True, text=True, timeout=60,
        )
        return float(r.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def exigir_ffmpeg(motivo):
    if shutil.which("ffmpeg"):
        return
    if os.name == "nt":
        arreglo = "winget install --id Gyan.FFmpeg -e"
    else:
        arreglo = "sudo apt install ffmpeg"
    morir(f"{motivo}, y para eso hace falta ffmpeg, que no esta instalado.\n"
          f"Instalalo con:  {arreglo}\n"
          "(Es parte del runtime que instala la seccion A4 de las skills de "
          "instalacion del lanzador rc.)")


def comprimir(origen, destino):
    """Reduce a mp3 mono de 16 kHz, que es todo lo que Whisper aprovecha."""
    r = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(origen),
         "-vn", "-ac", "1", "-ar", "16000", "-b:a", BITRATE_COMPRIMIDO,
         str(destino)],
        capture_output=True, text=True, timeout=3600,
    )
    if r.returncode != 0 or not destino.exists():
        morir(f"ffmpeg no pudo comprimir el audio: {r.stderr.strip()[:400]}")
    return destino


def partir(origen, carpeta, segundos):
    """Parte en tramos parejos. Devuelve la lista ordenada de tramos."""
    patron = carpeta / "tramo_%03d.mp3"
    r = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(origen),
         "-f", "segment", "-segment_time", str(segundos), "-c", "copy",
         str(patron)],
        capture_output=True, text=True, timeout=3600,
    )
    tramos = sorted(carpeta.glob("tramo_*.mp3"))
    if r.returncode != 0 or not tramos:
        morir(f"ffmpeg no pudo partir el audio: {r.stderr.strip()[:400]}")
    return tramos


def planear(ruta_audio, carpeta_trabajo, forzar_comprimir=False):
    """Decide que se le va a mandar a la API.

    Devuelve (lista_de_archivos, nota_para_el_usuario).
    """
    tam = ruta_audio.stat().st_size
    if tam <= LIMITE_ENVIO and not forzar_comprimir:
        return [ruta_audio], "se manda tal cual"

    motivo = (f"el audio pesa {tam / 1024 / 1024:.1f} MB y el limite por llamada "
              "es 25 MB")
    exigir_ffmpeg(motivo)

    comprimido = comprimir(ruta_audio, carpeta_trabajo / "comprimido.mp3")
    tam_comp = comprimido.stat().st_size
    nota = (f"comprimido de {tam / 1024 / 1024:.1f} MB a "
            f"{tam_comp / 1024 / 1024:.1f} MB (16 kHz mono)")

    if tam_comp <= LIMITE_ENVIO:
        return [comprimido], nota

    tramos = partir(comprimido, carpeta_trabajo, SEGUNDOS_POR_TRAMO)
    grandes = [t for t in tramos if t.stat().st_size > LIMITE_ENVIO]
    if grandes:
        morir("un tramo quedo por encima del limite aun despues de comprimir. "
              "Reporta el caso: puede ser un formato que ffmpeg no recodifico.")
    return tramos, f"{nota}, y partido en {len(tramos)} tramos"


# --------------------------------------------------------------------------
# Llamada a la API
# --------------------------------------------------------------------------

def armar_multipart(ruta, campos):
    """Arma un cuerpo multipart/form-data. Devuelve (cuerpo, content_type)."""
    frontera = f"----whisper{uuid.uuid4().hex}"
    sep = f"--{frontera}".encode()
    partes = []

    for nombre, valor in campos.items():
        partes.append(sep)
        partes.append(f'Content-Disposition: form-data; name="{nombre}"'.encode())
        partes.append(b"")
        partes.append(str(valor).encode("utf-8"))

    tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
    partes.append(sep)
    partes.append(
        f'Content-Disposition: form-data; name="audio"; filename="{ruta.name}"'
        .encode("utf-8"))
    partes.append(f"Content-Type: {tipo}".encode())
    partes.append(b"")

    cuerpo = b"\r\n".join(partes) + b"\r\n"
    cuerpo += ruta.read_bytes()
    cuerpo += f"\r\n--{frontera}--\r\n".encode()
    return cuerpo, f"multipart/form-data; boundary={frontera}"


def transcribir_archivo(ruta, llave, tarea, idioma, intentos=3):
    """Una llamada a la API. Devuelve el JSON de respuesta."""
    campos = {"task": tarea}
    if idioma:
        campos["language"] = idioma
    cuerpo, content_type = armar_multipart(ruta, campos)

    ultimo_error = ""
    for intento in range(1, intentos + 1):
        pedido = urllib.request.Request(
            ENDPOINT, data=cuerpo, method="POST",
            headers={
                "Authorization": f"Bearer {llave}",
                "Content-Type": content_type,
                "Content-Length": str(len(cuerpo)),
            },
        )
        try:
            with urllib.request.urlopen(pedido, timeout=900) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", "replace")[:400].replace("\n", " ")
            if e.code in (401, 403):
                morir(f"HTTP {e.code}: la llave de DeepInfra no fue aceptada. "
                      f"Vuelve a guardarla con --guardar-llave. Detalle: {detalle}")
            if e.code == 402:
                morir("HTTP 402: la cuenta de DeepInfra no tiene saldo. "
                      "Agrega credito en https://deepinfra.com/dash/billing")
            ultimo_error = f"HTTP {e.code}: {detalle}"
            if e.code not in (408, 409, 429, 500, 502, 503, 504):
                morir(ultimo_error)
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead,
                http.client.RemoteDisconnected, ConnectionResetError) as e:
            # Ninguna de las cuatro ultimas es URLError: el timeout de 900s salta
            # como TimeoutError durante la lectura de la respuesta, y un corte de
            # conexion a media respuesta llega como IncompleteRead o
            # RemoteDisconnected (que a su vez hereda de ConnectionResetError, se
            # listan las dos para que quede explicito). Sin este bloque ampliado
            # se escapaban como traza cruda, ya pagada la llamada.
            detalle = getattr(e, "reason", None)
            ultimo_error = f"error de red: {detalle if detalle else e}"
        except json.JSONDecodeError as e:
            ultimo_error = f"respuesta no-JSON: {e}"

        if intento < intentos:
            espera = 5 * intento
            print(f"  reintento {intento + 1}/{intentos} en {espera}s "
                  f"({ultimo_error})", file=sys.stderr)
            time.sleep(espera)

    morir(f"la API no respondio bien tras {intentos} intentos. {ultimo_error}")


def revisar_longitud(caracteres, duracion_segundos):
    """Devuelve un aviso si la transcripcion salio sospechosamente corta.

    Es un aviso, no una falla: el texto ya se pago y se entrega igual. Solo
    existe porque una transcripcion real reporto exito con 11 caracteres, y sin
    esto el unico sintoma era un archivo de salida que nadie volvio a abrir.
    """
    if not duracion_segundos or duracion_segundos < SEGUNDOS_MINIMOS_PARA_REVISAR:
        return None
    if caracteres >= duracion_segundos * CARACTERES_MINIMOS_POR_SEGUNDO:
        return None
    return (f"aviso: la transcripcion trae solo {caracteres:,} caracteres para "
            f"{duracion_segundos:.0f} s de audio ({duracion_segundos / 60:.1f} min). "
            "Revisala antes de usarla: puede ser un audio casi mudo, un --idioma "
            "que no corresponde, o una respuesta cortada. El texto se entrega "
            "igual, la llamada ya se pago.")


def anotar_log(audio, tarea, idioma, duracion, costo, salida, ok, sospechosa=False):
    RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    estado = ("OK?" if sospechosa else "OK ") if ok else "ERR"
    dur = f"{duracion:.1f}s" if duracion is not None else "?s"
    destino = str(salida) if salida else "stdout"
    with RUTA_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts}\t{estado}\t{dur}\t${costo:.5f}\t{audio.name}\t{tarea}"
                f"\t{idioma}\t{destino}\n")


# --------------------------------------------------------------------------
# Estado
# --------------------------------------------------------------------------

def mostrar_estado():
    llave_entorno = bool(os.environ.get("DEEPINFRA_API_KEY", "").strip())
    llave_archivo = leer_llave_de_archivo()
    if llave_entorno:
        origen = "variable de entorno DEEPINFRA_API_KEY"
    elif llave_archivo:
        origen = str(RUTA_CREDENCIALES)
    else:
        origen = "NO CONFIGURADA"

    ffmpeg = shutil.which("ffmpeg") or "NO INSTALADO (hace falta para audios > 25 MB)"
    ffprobe = shutil.which("ffprobe") or "NO INSTALADO (sin el, no hay costo estimado)"
    hay_cred = "existe" if RUTA_CREDENCIALES.exists() else "no existe"
    hay_log = "existe" if RUTA_LOG.exists() else "todavia sin llamadas"

    print(f"llave         : {origen}")
    print(f"credenciales  : {RUTA_CREDENCIALES} ({hay_cred})")
    print(f"ffmpeg        : {ffmpeg}")
    print(f"ffprobe       : {ffprobe}")
    print(f"python        : {sys.version.split()[0]} ({sys.executable})")
    print(f"log           : {RUTA_LOG} ({hay_log})")
    return 0 if (llave_entorno or llave_archivo) else 1


# --------------------------------------------------------------------------

def main():
    preparar_salida()
    ap = argparse.ArgumentParser(
        description="Transcribe audio con whisper-large-v3-turbo en DeepInfra.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("audio", nargs="?", help="Ruta del archivo de audio.")
    ap.add_argument("-o", "--salida", "--output", dest="salida", default=None,
                    help="Archivo de texto de salida (default: stdout).")
    ap.add_argument("--idioma", "--language", dest="idioma", default=None,
                    help="Codigo ISO-639-1 (es, en, fr...). Default: autodetectar. "
                         "Pasarlo mejora la precision cuando ya se sabe.")
    ap.add_argument("--tarea", "--task", dest="tarea",
                    choices=["transcribe", "translate"], default="transcribe",
                    help="'transcribe' conserva el idioma; 'translate' pasa a ingles.")
    ap.add_argument("--simulacion", "--dry-run", dest="simulacion",
                    action="store_true",
                    help="Muestra el plan y el costo estimado sin llamar a la API.")
    ap.add_argument("--comprimir", action="store_true",
                    help="Comprimir siempre, aunque el archivo ya quepa.")
    ap.add_argument("--guardar-llave", action="store_true",
                    help="Lee la llave de DeepInfra por stdin y la guarda.")
    ap.add_argument("--estado", action="store_true",
                    help="Reporta llave, ffmpeg y rutas, sin transcribir.")
    args = ap.parse_args()

    if args.guardar_llave:
        return guardar_llave()
    if args.estado:
        return mostrar_estado()
    if not args.audio:
        ap.error("falta la ruta del audio (o usa --estado / --guardar-llave).")

    ruta_audio = Path(args.audio).expanduser().resolve()
    if not ruta_audio.exists():
        morir(f"archivo no encontrado: {ruta_audio}")
    if ruta_audio.suffix.lower() not in FORMATOS:
        print(f"whisper-deepinfra: aviso, extension '{ruta_audio.suffix}' fuera de "
              f"las soportadas ({', '.join(sorted(FORMATOS))}). Se intenta igual.",
              file=sys.stderr)

    duracion = duracion_segundos(ruta_audio)
    costo = PRECIO_POR_MINUTO * (duracion / 60) if duracion is not None else None
    ruta_salida = Path(args.salida).expanduser().resolve() if args.salida else None
    if ruta_salida:
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    tam = ruta_audio.stat().st_size
    with tempfile.TemporaryDirectory(prefix="whisper-deepinfra-") as tmp:
        carpeta = Path(tmp)

        if args.simulacion:
            necesita = tam > LIMITE_ENVIO or args.comprimir
            plan = ("comprimir con ffmpeg y partir si hace falta"
                    if necesita else "se manda tal cual, en una sola llamada")
            print(json.dumps({
                "endpoint": ENDPOINT,
                "archivo": str(ruta_audio),
                "tamano_mb": round(tam / 1024 / 1024, 2),
                "duracion_seg": round(duracion, 1) if duracion is not None
                                else "desconocida (falta ffprobe)",
                "tarea": args.tarea,
                "idioma": args.idioma or "autodetectar",
                "plan": plan,
                "ffmpeg": bool(shutil.which("ffmpeg")),
                "costo_estimado_usd": round(costo, 5) if costo is not None
                                      else "desconocido",
            }, indent=2, ensure_ascii=False))
            return 0

        llave, _ = obtener_llave()
        piezas, nota = planear(ruta_audio, carpeta, args.comprimir)
        if len(piezas) > 1 or piezas[0] != ruta_audio:
            print(f"whisper-deepinfra: {nota}.", file=sys.stderr)

        textos = []
        idioma_detectado = args.idioma or "?"
        duracion_real = 0.0
        for i, pieza in enumerate(piezas, 1):
            if len(piezas) > 1:
                print(f"whisper-deepinfra: tramo {i}/{len(piezas)}...",
                      file=sys.stderr)
            datos = transcribir_archivo(pieza, llave, args.tarea, args.idioma)
            texto = (datos.get("text") or datos.get("transcription") or "").strip()
            if not texto and len(piezas) == 1:
                anotar_log(ruta_audio, args.tarea, idioma_detectado, duracion,
                           costo or 0, ruta_salida, ok=False)
                morir(f"la respuesta no trae texto. Claves recibidas: "
                      f"{list(datos.keys())}")
            textos.append(texto)
            if datos.get("language"):
                idioma_detectado = datos["language"]
            if datos.get("duration"):
                duracion_real += float(datos["duration"])

    texto_final = "\n\n".join(t for t in textos if t).strip()
    if not texto_final:
        anotar_log(ruta_audio, args.tarea, idioma_detectado, duracion, costo or 0,
                   ruta_salida, ok=False)
        morir("la transcripcion salio vacia. Verifica que el audio tenga voz.")

    duracion_final = duracion_real or duracion
    costo_final = (PRECIO_POR_MINUTO * (duracion_final / 60)
                   if duracion_final else (costo or 0))
    aviso = revisar_longitud(len(texto_final), duracion_final)
    anotar_log(ruta_audio, args.tarea, idioma_detectado, duracion_final,
               costo_final, ruta_salida, ok=True, sospechosa=bool(aviso))
    if aviso:
        print(f"whisper-deepinfra: {aviso}", file=sys.stderr)

    if ruta_salida:
        ruta_salida.write_text(texto_final + "\n", encoding=codificacion_de_salida())
        print(f"OK -> {ruta_salida}  ({len(texto_final):,} caracteres, "
              f"idioma={idioma_detectado}, ~${costo_final:.5f} USD)")
    else:
        print(texto_final)
        print(f"whisper-deepinfra: {len(texto_final):,} caracteres, "
              f"idioma={idioma_detectado}, ~${costo_final:.5f} USD", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
