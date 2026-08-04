#!/usr/bin/env python3
"""
kokoro-deepinfra: convierte texto en voz sintetica con hexgrad/Kokoro-82M
en DeepInfra.

Un solo archivo, biblioteca estandar de Python. No necesita pip install de
nada. Corre igual en Linux, macOS y Windows.

La llave se busca en este orden:
  1. Variable de entorno DEEPINFRA_API_KEY
  2. Archivo ~/.config/deepinfra/credentials
Es la misma llave que usa whisper-deepinfra: quien ya tenga la transcripcion
no la vuelve a dar.

Uso:
  echo "texto" | python3 kokoro_deepinfra.py -o salida/voz.mp3
  python3 kokoro_deepinfra.py documento.md -o salida/documento.mp3
  python3 kokoro_deepinfra.py --estado
  echo "<llave>" | python3 kokoro_deepinfra.py --guardar-llave

Textos de mas de 10,000 caracteres se parten en frontera de oracion y los
pedazos se unen con ffmpeg. No hay que hacerlo a mano.

Log de llamadas en ~/.cache/kokoro-deepinfra.log
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.deepinfra.com/v1/openai/audio/speech"
MODELO = "hexgrad/Kokoro-82M"
PRECIO_POR_MILLON = 0.62  # USD por millon de caracteres

# Medido el 4 ago 2026: 487 caracteres dieron 31.8 s de audio.
CARACTERES_POR_SEGUNDO = 17.2

RUTA_LOG = Path.home() / ".cache" / "kokoro-deepinfra.log"
RUTA_CREDENCIALES = Path.home() / ".config" / "deepinfra" / "credentials"

VOZ_POR_DEFECTO = "em_alex"

# Las 54 que acepta la API, sacadas del propio mensaje de validacion. Se
# valida contra esta lista ANTES de llamar: un nombre mal escrito da un 400
# que se puede evitar sin gastar la llamada.
VOCES = (
    "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore",
    "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
    "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael",
    "am_onyx", "am_puck", "am_santa",
    "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis",
    "ef_dora", "em_alex", "em_santa",
    "ff_siwis",
    "hf_alpha", "hf_beta", "hm_omega", "hm_psi",
    "if_sara", "im_nicola",
    "jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro", "jm_kumo",
    "pf_dora", "pm_alex", "pm_santa",
    "zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi",
    "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang",
)
VOCES_ESPANOL = ("ef_dora", "em_alex", "em_santa")


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
    parte de Unicode: imprimir el resultado reventaba con UnicodeEncodeError
    DESPUES de haber pagado la llamada a la API, o sea perdiendo lo ya cobrado.
    """
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def morir(msg, codigo=1):
    print(f"kokoro-deepinfra: {msg}", file=sys.stderr)
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
        if not linea.startswith("DEEPINFRA_API_KEY"):
            continue
        _, _, valor = linea.partition("=")
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
# ffmpeg
# --------------------------------------------------------------------------

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


# --------------------------------------------------------------------------
# Limpieza de markdown a texto hablado
# --------------------------------------------------------------------------

_RE_BLOQUE_CODIGO = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.M | re.S)
_RE_IMAGEN = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_RE_LIGA = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_RE_ENCABEZADO = re.compile(r"^\s{0,3}#{1,6}\s+")
_RE_CASILLA = re.compile(r"^\s*[-*+]\s+\[[ xX]\]\s*")
_RE_VINETA = re.compile(r"^\s*[-*+]\s+")
_RE_NUMERACION = re.compile(r"^\s*\d+[.)]\s+")
_RE_CITA = re.compile(r"^\s{0,3}>\s?")
# El guion bajo solo cuenta como enfasis si no esta pegado a letras o
# numeros: asi `pendientes_viejos` se lee tal cual y no queda partido.
_RE_ENFASIS = re.compile(r"\*{1,3}|`{1,3}|(?<![A-Za-z0-9])_{1,2}|_{1,2}(?![A-Za-z0-9])")

# Esta cadena rompe a proposito la convencion sin acentos del resto del
# archivo: no es codigo ni comentario, es texto que el modelo de voz va a
# pronunciar, y sin tilde diria "codigo" mal acentuado. No "corregirla".
NOTA_CODIGO = "(Aquí va un bloque de código, que no se lee.)"


def _es_regla_horizontal(linea):
    s = linea.strip()
    return len(s) >= 3 and set(s) in ({"-"}, {"*"}, {"_"})


def _es_separador_de_tabla(linea):
    s = linea.strip().strip("|").strip()
    return bool(s) and set(s) <= set("-: |")


def _aplanar_tabla(linea):
    celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
    return ", ".join(c for c in celdas if c)


def limpiar_markdown(texto):
    """Convierte markdown en texto apto para leerse en voz alta.

    No es un parser: es un quitamarcas. Lo que importa es que no se pronuncien
    almohadillas, asteriscos, corchetes de casilla ni URLs, que es lo que
    vuelve insufrible un documento dictado.
    """
    texto = _RE_BLOQUE_CODIGO.sub("\n" + NOTA_CODIGO + "\n", texto)
    texto = _RE_IMAGEN.sub("", texto)
    texto = _RE_LIGA.sub(r"\1", texto)

    renglones = []
    for linea in texto.splitlines():
        if _es_regla_horizontal(linea) or _es_separador_de_tabla(linea):
            continue
        if linea.lstrip().startswith("|"):
            linea = _aplanar_tabla(linea)
        linea = _RE_CITA.sub("", linea)
        linea = _RE_ENCABEZADO.sub("", linea)
        # La casilla va antes que la vineta: `- [ ] x` empieza con vineta, y
        # al reves quedaria un `[ ]` suelto que si se pronuncia.
        linea = _RE_CASILLA.sub("", linea)
        linea = _RE_VINETA.sub("", linea)
        linea = _RE_NUMERACION.sub("", linea)
        linea = _RE_ENFASIS.sub("", linea)
        renglones.append(linea.rstrip())

    salida = "\n".join(renglones)
    salida = re.sub(r"\n{3,}", "\n\n", salida)
    return salida.strip()


# --------------------------------------------------------------------------
# Troceo
# --------------------------------------------------------------------------

# Limite duro de la API, medido el 4 ago 2026: manda 400 con
# "String should have at most 10000 characters".
LIMITE_LLAMADA = 10000
# Se apunta abajo del limite para no quedar al filo por un corte que caiga
# tarde en la ventana.
OBJETIVO_TROZO = 9000

# En orden de preferencia. Cortar en fin de parrafo suena mejor que en fin de
# oracion, y ambos mucho mejor que a caracter fijo.
FRONTERAS = ("\n\n", ". ", ".\n", "? ", "?\n", "! ", "!\n", "… ", "\n", " ")


def _mejor_corte(texto, objetivo):
    """Posicion donde cortar, buscando hacia atras desde el objetivo.

    Se exige que el corte caiga despues de la mitad de la ventana: si no,
    un texto con una sola frontera al principio produciria pedazos ridiculos
    y multiplicaria las llamadas.
    """
    ventana = texto[:objetivo]
    for frontera in FRONTERAS:
        pos = ventana.rfind(frontera)
        if pos > objetivo // 2:
            return pos + len(frontera)
    return objetivo


def trocear(texto, objetivo=OBJETIVO_TROZO):
    """Parte el texto en pedazos que quepan en una llamada.

    A diferencia de whisper-deepinfra, que corta el audio a tiempo fijo y
    pierde una palabra en cada frontera, aqui el corte cae en puntuacion y no
    se pierde nada.
    """
    if len(texto) <= objetivo:
        return [texto]

    pedazos = []
    resto = texto
    while len(resto) > objetivo:
        corte = _mejor_corte(resto, objetivo)
        pedazos.append(resto[:corte].strip())
        resto = resto[corte:].lstrip()
    if resto:
        pedazos.append(resto)
    return pedazos


# --------------------------------------------------------------------------
# Llamada a la API
# --------------------------------------------------------------------------

def hablar_pedazo(texto, llave, voz, velocidad, intentos=3):
    """Una llamada a la API. Devuelve los bytes del MP3."""
    cuerpo = json.dumps({
        "model": MODELO,
        "input": texto,
        "voice": voz,
        # SIEMPRE mp3. El default de la API es WAV, y 2,000 caracteres pesan
        # 5.6 MB en WAV contra ~200 KB en mp3.
        "response_format": "mp3",
        "speed": velocidad,
    }).encode("utf-8")

    ultimo_error = ""
    for intento in range(1, intentos + 1):
        pedido = urllib.request.Request(
            ENDPOINT, data=cuerpo, method="POST",
            headers={
                "Authorization": f"Bearer {llave}",
                "Content-Type": "application/json",
                "Content-Length": str(len(cuerpo)),
            },
        )
        try:
            with urllib.request.urlopen(pedido, timeout=900) as r:
                audio = r.read()
            if not audio:
                ultimo_error = "la API devolvio una respuesta vacia"
            else:
                return audio
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
        except urllib.error.URLError as e:
            ultimo_error = f"error de red: {e.reason}"

        if intento < intentos:
            espera = 5 * intento
            print(f"  reintento {intento + 1}/{intentos} en {espera}s "
                  f"({ultimo_error})", file=sys.stderr)
            time.sleep(espera)

    morir(f"la API no respondio bien tras {intentos} intentos. {ultimo_error}")


def unir(pedazos_mp3, destino, carpeta_trabajo):
    """Une varios MP3 en uno solo con el demuxer de concat de ffmpeg."""
    lista = carpeta_trabajo / "lista.txt"
    # ffmpeg quiere rutas con las comillas simples escapadas; se escriben
    # absolutas para no depender del directorio de trabajo.
    lista.write_text(
        "".join(f"file '{str(p).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'\n"
                for p in pedazos_mp3),
        encoding="utf-8")
    r = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat",
         "-safe", "0", "-i", str(lista), "-c", "copy", str(destino)],
        capture_output=True, text=True, timeout=3600,
    )
    if r.returncode != 0 or not destino.exists():
        morir(f"ffmpeg no pudo unir los pedazos: {r.stderr.strip()[:400]}")
    return destino


# --------------------------------------------------------------------------
# Log, estado y ruta de salida
# --------------------------------------------------------------------------

CARPETA_SALIDA = "salida"


def ruta_de_salida_por_defecto(ruta_entrada):
    """salida/<nombre>.mp3, o salida/voz-AAAAMMDD-HHMM.mp3 si vino por stdin.

    Relativa al directorio de trabajo, que en una sesion del lanzador es la
    raiz del proyecto. La marca de tiempo evita que dos peticiones seguidas
    se pisen, que con "leeme los pendientes" pasaria a diario.
    """
    carpeta = Path.cwd() / CARPETA_SALIDA
    if ruta_entrada is not None:
        return carpeta / (ruta_entrada.stem + ".mp3")
    return carpeta / f"voz-{time.strftime('%Y%m%d-%H%M%S')}.mp3"


def anotar_log(origen, voz, caracteres, costo, salida, ok):
    RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    estado = "OK " if ok else "ERR"
    with RUTA_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{ts}\t{estado}\t{caracteres}c\t${costo:.5f}\t{origen}"
                f"\t{voz}\t{salida}\n")


def mostrar_estado():
    llave_entorno = bool(os.environ.get("DEEPINFRA_API_KEY", "").strip())
    llave_archivo = leer_llave_de_archivo()
    if llave_entorno:
        origen = "variable de entorno DEEPINFRA_API_KEY"
    elif llave_archivo:
        origen = str(RUTA_CREDENCIALES)
    else:
        origen = "NO CONFIGURADA"

    ffmpeg = (shutil.which("ffmpeg")
              or "NO INSTALADO (solo hace falta para textos > "
                 f"{LIMITE_LLAMADA:,} caracteres)")
    hay_cred = "existe" if RUTA_CREDENCIALES.exists() else "no existe"
    hay_log = "existe" if RUTA_LOG.exists() else "todavia sin llamadas"

    print(f"llave         : {origen}")
    print(f"credenciales  : {RUTA_CREDENCIALES} ({hay_cred})")
    print(f"ffmpeg        : {ffmpeg}")
    print(f"voz default   : {VOZ_POR_DEFECTO}")
    print(f"voces español : {', '.join(VOCES_ESPANOL)}")
    print(f"python        : {sys.version.split()[0]} ({sys.executable})")
    print(f"log           : {RUTA_LOG} ({hay_log})")
    return 0 if (llave_entorno or llave_archivo) else 1


# --------------------------------------------------------------------------

def main():
    preparar_salida()
    ap = argparse.ArgumentParser(
        description="Convierte texto en voz sintetica con Kokoro-82M en DeepInfra.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("texto", nargs="?",
                    help="Archivo .txt o .md. Sin el, lee de stdin.")
    ap.add_argument("-o", "--salida", "--output", dest="salida", default=None,
                    help="Ruta del MP3. Default: salida/<nombre>.mp3")
    ap.add_argument("--voz", "--voice", dest="voz", default=VOZ_POR_DEFECTO,
                    help=f"Voz. Default {VOZ_POR_DEFECTO}. "
                         f"En español: {', '.join(VOCES_ESPANOL)}.")
    ap.add_argument("--velocidad", "--speed", dest="velocidad", type=float,
                    default=1.0, help="Velocidad de habla. Default 1.0.")
    ap.add_argument("--crudo", action="store_true",
                    help="No limpiar el markdown antes de hablar.")
    ap.add_argument("--simulacion", "--dry-run", dest="simulacion",
                    action="store_true",
                    help="Plan y costo estimado, sin llamar a la API.")
    ap.add_argument("--guardar-llave", action="store_true",
                    help="Lee la llave de DeepInfra por stdin y la guarda.")
    ap.add_argument("--estado", action="store_true",
                    help="Reporta llave, ffmpeg y voces, sin hablar.")
    args = ap.parse_args()

    if args.guardar_llave:
        return guardar_llave()
    if args.estado:
        return mostrar_estado()

    if args.voz not in VOCES:
        morir(f"voz desconocida: {args.voz}. En español hay tres: "
              f"{', '.join(VOCES_ESPANOL)}.")

    # Entrada: archivo si lo dieron, stdin si no.
    ruta_entrada = None
    if args.texto:
        ruta_entrada = Path(args.texto).expanduser().resolve()
        if not ruta_entrada.exists():
            morir(f"archivo no encontrado: {ruta_entrada}")
        # utf-8-sig y no utf-8: un .txt escrito en Windows por
        # whisper-deepinfra lleva BOM a proposito.
        texto = ruta_entrada.read_text(encoding="utf-8-sig")
    else:
        if sys.stdin.isatty():
            morir("no llego texto. Pasa un archivo o canaliza texto por stdin.")
        texto = sys.stdin.read()

    if not args.crudo:
        texto = limpiar_markdown(texto)
    texto = texto.strip()
    if not texto:
        morir("el texto quedo vacio despues de limpiarlo. Nada que hablar.")

    caracteres = len(texto)
    costo = PRECIO_POR_MILLON * caracteres / 1_000_000
    pedazos = trocear(texto)
    origen = ruta_entrada.name if ruta_entrada else "stdin"

    ruta_salida = (Path(args.salida).expanduser().resolve() if args.salida
                   else ruta_de_salida_por_defecto(ruta_entrada))

    if args.simulacion:
        print(json.dumps({
            "endpoint": ENDPOINT,
            "modelo": MODELO,
            "origen": origen,
            "caracteres": caracteres,
            "llamadas": len(pedazos),
            "voz": args.voz,
            "duracion_estimada_seg": round(caracteres / CARACTERES_POR_SEGUNDO, 1),
            "necesita_ffmpeg": len(pedazos) > 1,
            "salida": str(ruta_salida),
            "costo_estimado_usd": round(costo, 5),
        }, indent=2, ensure_ascii=False))
        return 0

    llave, _ = obtener_llave()
    if len(pedazos) > 1:
        exigir_ffmpeg(f"el texto trae {caracteres:,} caracteres y hay que "
                      f"partirlo en {len(pedazos)} pedazos")

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="kokoro-deepinfra-") as tmp:
        carpeta = Path(tmp)
        archivos = []
        for i, pedazo in enumerate(pedazos, 1):
            if len(pedazos) > 1:
                print(f"kokoro-deepinfra: pedazo {i}/{len(pedazos)}...",
                      file=sys.stderr)
            audio = hablar_pedazo(pedazo, llave, args.voz, args.velocidad)
            destino = carpeta / f"pedazo_{i:03d}.mp3"
            destino.write_bytes(audio)
            archivos.append(destino)

        if len(archivos) == 1:
            shutil.copyfile(archivos[0], ruta_salida)
        else:
            unir(archivos, ruta_salida, carpeta)

    if not ruta_salida.exists() or ruta_salida.stat().st_size == 0:
        anotar_log(origen, args.voz, caracteres, costo, ruta_salida, ok=False)
        morir("el MP3 salio vacio. Reporta el caso.")

    anotar_log(origen, args.voz, caracteres, costo, ruta_salida, ok=True)
    mb = ruta_salida.stat().st_size / 1024 / 1024
    print(f"OK -> {ruta_salida}  ({caracteres:,} caracteres, {mb:.1f} MB, "
          f"voz={args.voz}, {len(pedazos)} llamada(s), ~${costo:.5f} USD)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
