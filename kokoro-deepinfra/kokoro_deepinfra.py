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
import http.client
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

# Medido el 4 ago 2026, voz em_alex (el default) leyendo prosa real: 487
# caracteres dieron 31.8 s de audio, o sea 487 / 31.8 = 15.3 caracteres/s.
CARACTERES_POR_SEGUNDO = 15.3

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

    Partir o no se decide contra el limite duro de la API (LIMITE_LLAMADA,
    10,000 caracteres), no contra `objetivo`: un texto de 9,500 caracteres
    cabe en una sola llamada y no debe arrastrar el prerrequisito de ffmpeg
    solo por pasar de OBJETIVO_TROZO. Una vez que SI hay que partir, cada
    corte SI apunta a `objetivo` (9,000 por defecto), que le da holgura a
    _mejor_corte() para buscar una frontera de oracion en vez de cortar
    justo al filo del limite duro.

    A diferencia de whisper-deepinfra, que corta el audio a tiempo fijo y
    pierde una palabra en cada frontera, aqui el corte cae en puntuacion (o,
    a falta de ninguna frontera cercana, a caracter fijo en `objetivo`, ver
    _mejor_corte) y en el caso normal no se pierde nada.
    """
    if len(texto) <= LIMITE_LLAMADA:
        return [texto]

    pedazos = []
    resto = texto
    while len(resto) > LIMITE_LLAMADA:
        corte = _mejor_corte(resto, objetivo)
        pedazos.append(resto[:corte].strip())
        resto = resto[corte:].lstrip()
    if resto:
        pedazos.append(resto)
    return pedazos


# --------------------------------------------------------------------------
# Llamada a la API
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Cabecera Xing/Info que miente sobre la duracion
# --------------------------------------------------------------------------
#
# Kokoro (via DeepInfra) escribe, en el PRIMER cuadro MPEG de cada mp3 que
# entrega, una cabecera Xing/Info (el formato estandar que LAME usa para
# declarar cuadros totales, bytes totales y una tabla de posiciones) con lo
# que llevaba generado al arrancar, y nunca la actualiza. Medido el 4 ago
# 2026 con un audio real de Kokoro: la cabecera declaraba 175 cuadros
# (4.20s, 31,272 bytes) para un archivo de 2,384 cuadros reales (57.2s,
# 408,768 bytes). Un reproductor que le cree a la cabecera (la mayoria: es
# la razon de ser del formato, evitarle al reproductor tener que decodificar
# el archivo entero para saber cuanto dura) trunca la reproduccion en el
# segundo 4. `ffmpeg`/`ffprobe` no caen en esto porque decodifican cuadro
# por cuadro sin importarles la cabecera, por eso el defecto paso
# inadvertido durante el desarrollo, y por eso tampoco sirven para verificar
# el arreglo: hay que leer la cabecera a mano, como la lee un reproductor.
#
# INTENTO ANTERIOR (insuficiente, ver docs/.../arreglo-encabezado-xing.md):
# quitar el cuadro completo, razonando que sin cabecera Xing un reproductor
# calcula la duracion dividiendo tamanio de archivo entre tasa de bits. Ese
# razonamiento solo vale con tasa CONSTANTE, y el flujo de Kokoro es de tasa
# VARIABLE: midiendo el mismo archivo real, los cuadros van de 8 a 160 kbps.
# Sin la cabecera, un reproductor asume la tasa del PRIMER cuadro (8 kbps
# aqui) para todo el archivo, y announce una duracion inflada (los 6:50
# reportados por el usuario para 57s reales son exactamente eso: 57.2s reales
# * ~160/8 ~= tamanio/8kbps).
#
# El arreglo correcto: REESCRIBIR la cabecera con los valores verdaderos, no
# quitarla. Un flujo de tasa variable NECESITA esa cabecera; es justo para
# eso que existe. Se recorre el archivo cuadro por cuadro (la misma cuenta
# que hace un decodificador real) para saber cuantos cuadros y bytes hay de
# verdad, se escriben esos numeros en los campos de la cabecera, y se
# reconstruye la tabla de posiciones (TOC) para que arrastrar la barra de
# reproduccion siga cayendo en el lugar correcto.

# [MPEG1 Layer I, II, III], indice 0 = "free", no usable para calcular tamanio.
_BITRATES_V1_L1 = (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448)
_BITRATES_V1_L2 = (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384)
_BITRATES_V1_L3 = (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320)
# MPEG2/2.5, Layer I; Layer II y III comparten tabla.
_BITRATES_V2_L1 = (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256)
_BITRATES_V2_L2L3 = (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160)

_SAMPLERATES = {
    1: (44100, 48000, 32000),    # MPEG1
    2: (22050, 24000, 16000),    # MPEG2 (LSF)
    2.5: (11025, 12000, 8000),   # MPEG2.5
}

# Offset de la cabecera Xing/Info dentro del cuadro (contando desde el inicio
# del cuadro, DESPUES de los 4 bytes de la cabecera MPEG), segun version y
# canal. Tabla estandar (la misma que usa ffmpeg en mp3_parse_vbr_tags): el
# tag se siembra donde iria la side-info de Layer III, que cambia de tamanio
# entre MPEG1/MPEG2 y entre mono/estereo.
_OFFSET_XING = {
    (1, False): 32, (1, True): 17,   # MPEG1: estereo/joint/dual, mono
    (2, False): 17, (2, True): 9,    # MPEG2 y MPEG2.5 (LSF): igual en los dos
}


def _saltar_id3v2(datos):
    """Bytes que ocupa un ID3v2 al inicio de `datos`, o 0 si no hay ninguno.

    El tamanio en la cabecera ID3v2 es "syncsafe" (4 bytes de 7 bits utiles
    cada uno, el bit alto siempre en 0) para que un cuadro MPEG nunca pueda
    contener por accidente la secuencia de sync 0xFF dentro del tamanio.
    """
    if len(datos) < 10 or datos[:3] != b"ID3":
        return 0
    tam_bytes = datos[6:10]
    if any(b & 0x80 for b in tam_bytes):
        return 0  # tamanio invalido, no es syncsafe: mejor no confiar
    tam = (tam_bytes[0] << 21) | (tam_bytes[1] << 14) | (tam_bytes[2] << 7) | tam_bytes[3]
    pie = 10 if (datos[5] & 0x10) else 0  # bit de "footer presente"
    return 10 + tam + pie


def _analizar_cabecera_frame(cab):
    """Parsea 4 bytes de cabecera MPEG. None si no es una cabecera valida.

    Devuelve version (1, 2 o 2.5), layer (1, 2 o 3), mono, y el tamanio en
    bytes del cuadro completo (cabecera incluida). Cualquier campo
    "reservado" o "free"/"bad" (que no permite calcular un tamanio confiable)
    hace que devuelva None: preferible no reconocer un cuadro real a
    calcularle un tamanio inventado.
    """
    if len(cab) < 4 or cab[0] != 0xFF or (cab[1] & 0xE0) != 0xE0:
        return None

    version_id = (cab[1] >> 3) & 0x03
    layer_id = (cab[1] >> 1) & 0x03
    if version_id == 1 or layer_id == 0:
        return None  # ambos "01"/"00" son valores reservados

    version = {0: 2.5, 2: 2, 3: 1}[version_id]
    layer = {1: 3, 2: 2, 3: 1}[layer_id]

    bitrate_idx = (cab[2] >> 4) & 0x0F
    samplerate_idx = (cab[2] >> 2) & 0x03
    if bitrate_idx in (0, 15) or samplerate_idx == 3:
        return None  # free, bad o reservado

    if version == 1:
        tabla = {1: _BITRATES_V1_L1, 2: _BITRATES_V1_L2, 3: _BITRATES_V1_L3}[layer]
    else:
        tabla = {1: _BITRATES_V2_L1, 2: _BITRATES_V2_L2L3, 3: _BITRATES_V2_L2L3}[layer]
    bitrate_kbps = tabla[bitrate_idx]
    samplerate = _SAMPLERATES[version][samplerate_idx]
    if bitrate_kbps == 0 or samplerate == 0:
        return None

    padding = (cab[2] >> 1) & 0x01
    modo = (cab[3] >> 6) & 0x03
    mono = modo == 3

    if layer == 1:
        tamanio = (12 * bitrate_kbps * 1000 // samplerate + padding) * 4
    else:
        multiplicador = 144 if version == 1 else 72
        tamanio = multiplicador * bitrate_kbps * 1000 // samplerate + padding

    return {"version": version, "layer": layer, "mono": mono, "tamanio": tamanio}


# Ventana en la que se busca el primer cuadro tras el ID3 (si lo hay). Kokoro
# no deja basura entre el ID3 y el primer cuadro, pero se deja margen por si
# algun dia hay padding: mejor buscar un poco que rendirse al primer byte que
# no calza y dejar pasar la cabecera mentirosa sin tocar.
_VENTANA_BUSQUEDA_FRAME = 4096


def _localizar_primer_frame(datos, desde):
    """(posicion, info) del primer cuadro MPEG valido desde `desde`, o (None, None)."""
    limite = min(len(datos) - 4, desde + _VENTANA_BUSQUEDA_FRAME)
    i = desde
    while i <= limite:
        if datos[i] == 0xFF and (datos[i + 1] & 0xE0) == 0xE0:
            info = _analizar_cabecera_frame(datos[i:i + 4])
            if info is not None:
                return i, info
        i += 1
    return None, None


# Banderas del campo `flags` de la cabecera Xing/Info (formato LAME
# estandar): que campos opcionales trae, en este orden fijo.
_XING_FRAMES = 0x0001
_XING_BYTES = 0x0002
_XING_TOC = 0x0004
_XING_CALIDAD = 0x0008


def _recorrer_cuadros(datos, desde):
    """Camina cuadro por cuadro desde `desde` hasta donde deje de poder.

    Es la misma cuenta que hace un decodificador real: cada cuadro se valida
    por su propia cabecera de 4 bytes (la tasa de bits puede cambiar de un
    cuadro a otro, es justo lo que hace variable al flujo), y su tamanio
    dice donde empieza el siguiente. Se detiene, SIN error, en el primer
    punto que no parsea como cuadro MPEG valido o que se saldria del
    archivo: eso es el final del audio real (o basura/metadata de cola, que
    tampoco hay que contar como audio).

    Devuelve (offsets, total_bytes): `offsets[i]` es la posicion, relativa a
    `desde`, donde empieza el cuadro i-esimo (0-indexado, el cuadro 0 es el
    que trae la propia cabecera Xing si la hay), y `total_bytes` es cuanto
    ocupan todos los cuadros caminados juntos.
    """
    offsets = []
    cursor = desde
    n = len(datos)
    while cursor + 4 <= n:
        info = _analizar_cabecera_frame(datos[cursor:cursor + 4])
        if info is None:
            break
        tamanio = info["tamanio"]
        if tamanio <= 0 or cursor + tamanio > n:
            break
        offsets.append(cursor - desde)
        cursor += tamanio
    return offsets, cursor - desde


def reescribir_xing(datos):
    """Reescribe (NO quita) el cuadro Xing/Info inicial de un mp3, si lo trae.

    Corrige los campos que declaran cuadros totales, bytes totales y la
    tabla de posiciones (TOC) con los valores reales, obtenidos recorriendo
    el archivo cuadro por cuadro. Ver la nota extensa arriba: un flujo de
    tasa variable como el de Kokoro NECESITA esta cabecera, asi que quitarla
    cambia una mentira por otra.

    Conservador a proposito, con el mismo criterio que tenia la version
    anterior de esta funcion cuando quitaba el cuadro: localiza el primer
    cuadro MPEG (tras cualquier ID3v2 inicial), y solo toca algo si en el
    offset exacto que le corresponde segun su version/canal trae de verdad
    la firma "Xing" o "Info" Y declara el campo de cuadros (el que de verdad
    mueve la aguja de la duracion declarada). Ante cualquier cosa que no
    calce exactamente con lo esperado (cabecera irreconocible, tamanio que
    se sale del archivo, campos que no caben en el cuadro, mas de 4 GB de
    audio) devuelve `datos` intactos: es preferible entregar un archivo con
    la duracion mal declarada que uno corrupto.
    """
    if len(datos) < 4:
        return datos

    inicio_id3 = _saltar_id3v2(datos)
    pos, info = _localizar_primer_frame(datos, inicio_id3)
    if pos is None or info["layer"] != 3:
        return datos

    offset_tag = _OFFSET_XING.get((info["version"] if info["version"] != 2.5 else 2, info["mono"]))
    if offset_tag is None:
        return datos
    inicio_tag = pos + 4 + offset_tag
    if inicio_tag + 8 > len(datos):
        return datos
    if datos[inicio_tag:inicio_tag + 4] not in (b"Xing", b"Info"):
        return datos

    fin_frame = pos + info["tamanio"]
    if info["tamanio"] <= 0 or fin_frame > len(datos):
        return datos

    flags = int.from_bytes(datos[inicio_tag + 4:inicio_tag + 8], "big")
    cursor_campo = inicio_tag + 8
    frames_offset = bytes_offset = toc_offset = None
    if flags & _XING_FRAMES:
        frames_offset = cursor_campo
        cursor_campo += 4
    if flags & _XING_BYTES:
        bytes_offset = cursor_campo
        cursor_campo += 4
    if flags & _XING_TOC:
        toc_offset = cursor_campo
        cursor_campo += 100
    if flags & _XING_CALIDAD:
        cursor_campo += 4  # indicador de calidad: no se toca, no hay como recalcularlo

    # Los campos que las banderas dicen que trae tienen que caber dentro del
    # propio cuadro (y del archivo). Si no caben, esto no es la cabecera que
    # se espera y es mas seguro no tocarla.
    if cursor_campo > fin_frame or cursor_campo > len(datos):
        return datos

    # Sin el campo de cuadros no hay nada que corregir: es el que un
    # reproductor usa para calcular la duracion (cuadros * muestras por
    # cuadro / frecuencia de muestreo). Tocar bytes o TOC sin el no arregla
    # el sintoma que motivo este arreglo.
    if frames_offset is None:
        return datos

    offsets, total_bytes = _recorrer_cuadros(datos, pos)
    total_cuadros = len(offsets)
    # El propio cuadro Xing ya se cuenta como el primero de `offsets` (el
    # recorrido empieza justo en `pos`). Si ni siquiera ese se pudo contar,
    # o si el recorrido midio menos que el tamanio ya validado de ese mismo
    # cuadro, algo no calza con lo de arriba: mejor no tocar nada.
    if total_cuadros < 1 or total_bytes < info["tamanio"] or total_bytes > 0xFFFFFFFF:
        return datos

    salida = bytearray(datos)
    salida[frames_offset:frames_offset + 4] = total_cuadros.to_bytes(4, "big")
    if bytes_offset is not None:
        salida[bytes_offset:bytes_offset + 4] = total_bytes.to_bytes(4, "big")
    if toc_offset is not None:
        tabla = bytearray(100)
        for i in range(100):
            idx = min(int(i * total_cuadros / 100), total_cuadros - 1)
            valor = (offsets[idx] * 256 // total_bytes) if total_bytes > 0 else 0
            tabla[i] = min(255, max(0, valor))
        salida[toc_offset:toc_offset + 100] = tabla

    return bytes(salida)


def parece_mp3(datos):
    """Firma barata: ID3v2 al inicio, o una cabecera de frame MPEG (0xFFEx).

    No decodifica el audio, solo descarta que la API haya devuelto un cuerpo
    de error (JSON, HTML, texto plano) disfrazado de HTTP 200. Encontrado en
    la revision: sin esto, ese cuerpo se copiaba tal cual y se reportaba
    "OK ->" con un MP3 que no lo es.
    """
    if len(datos) < 2:
        return False
    if datos[:3] == b"ID3":
        return True
    return datos[0] == 0xFF and (datos[1] & 0xE0) == 0xE0


def duracion_segundos(ruta):
    """Duracion REAL en segundos, sumando la duracion de cada paquete de audio.

    A proposito NO usa `-show_entries format=duration` (ni `stream=duration`,
    que para este caso da el mismo numero: los dos leen la cabecera que el
    propio archivo declara, no lo que de verdad contiene). Medido el 4 ago
    2026: un MP3 real de Kokoro de 483.6s decodificados (verificado con
    `ffmpeg -i archivo -f null -`) declaraba 595.22s en su cabecera, 23% de
    mas. Con esa lectura, la verificacion de mas abajo comparaba "la suma de
    numeros inflados" contra "un numero correcto" y acusaba perdida de audio
    SIEMPRE, incluso en uniones perfectas (el defecto critico que este
    archivo arregla).

    En vez de confiar en la cabecera, se le pide a ffprobe la duracion de
    CADA paquete (`packet=duration_time`) y se suman: eso obliga a recorrer
    el archivo entero leyendo cada frame real, la misma cuenta que hace un
    decodificador de verdad. Verificado contra `ffmpeg -f null -` en un
    archivo de 24 kHz mono (lo que produce Kokoro) sin cabecera Xing: los dos
    metodos coinciden al centesimo de segundo (600.048s vs 600.04s en un
    archivo de 10 minutos), y sale barata: ~0.2s para esos 10 minutos, del
    orden de las ~900x tiempo real medidas para el camino de decodificar
    completo.

    Formato de salida `default=nokey=1:noprint_wrappers=1`, no csv: un
    paquete con SIDE_DATA (visto en la practica, "Skip Samples" del primer
    frame) le agrega una columna extra en csv y deja coma colgada al final
    de esa linea, que revienta el float() de esa sola linea y hace que TODA
    la suma se pierda por una excepcion silenciosa. El formato default no
    tiene columnas, no le pasa.

    None si ffprobe no esta instalado, o si no se pudo leer NINGUN paquete
    (archivo vacio, cabecera irreconocible, etc., la señal mas fuerte de que
    esta corrupto). Mismo patron defensivo que whisper_deepinfra.py: nunca
    truena, solo deja de poder verificar cuando la herramienta falta.
    """
    if not shutil.which("ffprobe"):
        return None
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "packet=duration_time",
             "-of", "default=nokey=1:noprint_wrappers=1", str(ruta)],
            capture_output=True, text=True, timeout=60,
        )
        total = 0.0
        vistos = 0
        for linea in r.stdout.splitlines():
            linea = linea.strip()
            if not linea or linea == "N/A":
                continue
            total += float(linea)
            vistos += 1
        return total if vistos > 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def hablar_pedazo(texto, llave, voz, velocidad, registrar_fallo, intentos=3):
    """Una llamada a la API. Devuelve los bytes del MP3.

    registrar_fallo(msg) se llama en vez de morir() directo: para cuando esta
    funcion decide morir ya pudo haberse hecho (y pagado) una llamada, y quien
    la invoca es responsable de dejar rastro en el log antes de salir.
    """
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
            elif not parece_mp3(audio):
                ultimo_error = (f"la API devolvio {len(audio)} bytes que no "
                                 "parecen mp3 (sin firma ID3 ni cabecera MPEG)")
            else:
                # Se aplica aqui, a CADA pedazo que llega de la API (no solo
                # al archivo final: ver el segundo llamado en main(), tras
                # unir()). Este primer llamado deja cada pedazo, por su
                # cuenta, con una cabecera que ya describe su propia
                # duracion correctamente. Ver reescribir_xing().
                return reescribir_xing(audio)
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", "replace")[:400].replace("\n", " ")
            if e.code in (401, 403):
                registrar_fallo(
                    f"HTTP {e.code}: la llave de DeepInfra no fue aceptada. "
                    f"Vuelve a guardarla con --guardar-llave. Detalle: {detalle}")
            if e.code == 402:
                registrar_fallo(
                    "HTTP 402: la cuenta de DeepInfra no tiene saldo. "
                    "Agrega credito en https://deepinfra.com/dash/billing")
            ultimo_error = f"HTTP {e.code}: {detalle}"
            if e.code not in (408, 409, 429, 500, 502, 503, 504):
                registrar_fallo(ultimo_error)
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead,
                http.client.RemoteDisconnected, ConnectionResetError) as e:
            # Ninguna de las tres ultimas es URLError: el timeout de 900s salta
            # como TimeoutError durante la lectura de la respuesta, y un corte
            # de conexion a media respuesta llega como IncompleteRead o
            # RemoteDisconnected (que a su vez hereda de ConnectionResetError,
            # se listan las tres para que quede explicito). Sin este bloque
            # ampliado se escapaban como traza cruda, ya pagada la llamada.
            detalle = getattr(e, "reason", None)
            ultimo_error = f"error de red: {detalle if detalle else e}"

        if intento < intentos:
            espera = 5 * intento
            print(f"  reintento {intento + 1}/{intentos} en {espera}s "
                  f"({ultimo_error})", file=sys.stderr)
            time.sleep(espera)

    registrar_fallo(f"la API no respondio bien tras {intentos} intentos. {ultimo_error}")


def unir(pedazos_mp3, destino, carpeta_trabajo, registrar_fallo):
    """Une varios MP3 en uno solo con el demuxer de concat de ffmpeg."""

    def fallar(msg):
        # No dejar un MP3 corrupto esperando en el destino final: es un
        # documento leido en voz alta al que le falta un pedazo, reproducible
        # y sin nada que lo marque como malo. Encontrado en la revision: un
        # lote de 4 pedazos con el ultimo truncado dejaba en salida/ un MP3
        # de 9.1s (perfectamente reproducible) donde debian ir 12 completos.
        # Todo el trabajo de detectar la corrupcion (abajo) se perdia en la
        # ultima pulgada si el archivo se quedaba ahi.
        try:
            if destino.exists():
                destino.unlink()
        except OSError:
            pass
        registrar_fallo(msg)

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
        fallar(f"ffmpeg no pudo unir los pedazos: {r.stderr.strip()[:400]}")

    # Verificacion barata de que la union no perdio pedazos. Encontrado en la
    # revision: un pedazo corrupto puede dejar a ffmpeg en returncode 0, con
    # el destino existente, pero mas corto de lo que le toca. Si ffprobe no
    # esta, no se verifica y sigue: mejor no verificar que tronar por falta
    # de una herramienta opcional.
    #
    # OJO (segunda vuelta de revision): "ffprobe esta pero no pudo medir un
    # pedazo" NO es lo mismo que "ffprobe no esta". Lo primero es la señal
    # mas fuerte de que ese pedazo esta corrupto (un mp3 truncado por debajo
    # de ~500 bytes ni siquiera deja que ffprobe le saque su propia
    # duracion), y apagar la verificacion completa en ese caso dejaba pasar
    # en silencio justo la corrupcion mas severa. Se separan las dos
    # situaciones: la ausencia de la herramienta se checa una sola vez, y a
    # partir de ahi cualquier duracion no medible (de un pedazo o del
    # resultado) es un fallo, no un "no se pudo verificar".
    if shutil.which("ffprobe"):
        duraciones = []
        for p in pedazos_mp3:
            d = duracion_segundos(p)
            if d is None:
                fallar(
                    f"ffprobe no pudo medir la duracion de {p.name}, que es "
                    "la señal mas fuerte de que ese pedazo quedo corrupto. "
                    "Reporta el caso, no uses este archivo.")
            duraciones.append(d)

        esperada = sum(duraciones)
        final = duracion_segundos(destino)
        if final is None:
            fallar(
                f"ffmpeg genero {destino.name} pero ffprobe no pudo medir su "
                "duracion. Reporta el caso, no uses este archivo.")

        # Medido: una union limpia con "-c copy" no pierde nada (probado con
        # clips de silencio, duracion final == suma exacta). El margen es
        # angosto a propósito: uno generoso (se probo 2s fijos) dejaba pasar
        # sin aviso el caso de la revision (3s esperados, 1.04s reales).
        margen = max(1.0, esperada * 0.03)
        if final < esperada - margen:
            fallar(
                f"la union parece incompleta: se esperaban ~{esperada:.1f}s "
                f"de audio ({len(pedazos_mp3)} pedazos) y el resultado dura "
                f"solo {final:.1f}s. Reporta el caso, no uses este archivo.")
    return destino


# --------------------------------------------------------------------------
# Log, estado y ruta de salida
# --------------------------------------------------------------------------

CARPETA_SALIDA = "salida"


def ruta_de_salida_por_defecto(ruta_entrada):
    """salida/<nombre>.mp3, o salida/voz-AAAAMMDD-HHMMSS.mp3 si vino por stdin.

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

    # 0.25-4.0: el rango de la API de voz de OpenAI, que este endpoint imita
    # (ENDPOINT termina en /openai/audio/speech). Sin esto, "-9" viajaba hasta
    # la API tal cual, gastaba la llamada y regresaba un 400.
    if not (0.25 <= args.velocidad <= 4.0):
        morir(f"velocidad fuera de rango: {args.velocidad}. Va de 0.25 a 4.0.")

    # Se valida aqui, antes de leer texto ni de llamar a la API: apuntar -o a
    # un directorio existente tronaba con traza cruda hasta el final, ya
    # gastada la llamada.
    if args.salida:
        ruta_pedida = Path(args.salida).expanduser().resolve()
        if ruta_pedida.is_dir():
            morir(f"la salida es un directorio, no un archivo: {ruta_pedida}")

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

    # Se recuerda si la carpeta ya existia ANTES de este intento: si el
    # fallo deja "salida/" vacia y fuimos nosotros quienes la creamos ahorita,
    # no hay que dejarla huerfana. Si ya tenia cosas (de una corrida previa),
    # no se toca.
    carpeta_salida_previa = ruta_salida.parent.exists()
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    def registrar_fallo(msg, codigo=1):
        """Como morir(), pero deja un renglon ERR en el log antes de salir.

        Encontrado en la revision: una corrida que fallaba en el pedazo 3 de 7
        no dejaba ningun rastro, o sea llamadas ya pagadas sin registro. A
        partir de aqui (ya se pudo haber llamado a la API) se usa esto en vez
        de morir() directo.
        """
        anotar_log(origen, args.voz, caracteres, costo, ruta_salida, ok=False)
        # Si la API fallo antes de escribir nada (o unir() ya limpio su
        # propio destino a medias), no dejar una carpeta "salida/" vacia
        # recien creada solo por este intento fallido.
        if not carpeta_salida_previa:
            try:
                if (ruta_salida.parent.exists()
                        and not any(ruta_salida.parent.iterdir())):
                    ruta_salida.parent.rmdir()
            except OSError:
                pass
        morir(msg, codigo)

    with tempfile.TemporaryDirectory(prefix="kokoro-deepinfra-") as tmp:
        carpeta = Path(tmp)
        archivos = []
        for i, pedazo in enumerate(pedazos, 1):
            if len(pedazos) > 1:
                print(f"kokoro-deepinfra: pedazo {i}/{len(pedazos)}...",
                      file=sys.stderr)
            audio = hablar_pedazo(pedazo, llave, args.voz, args.velocidad,
                                   registrar_fallo)
            destino = carpeta / f"pedazo_{i:03d}.mp3"
            destino.write_bytes(audio)
            archivos.append(destino)

        if len(archivos) == 1:
            shutil.copyfile(archivos[0], ruta_salida)
        else:
            unir(archivos, ruta_salida, carpeta, registrar_fallo)

    if not ruta_salida.exists() or ruta_salida.stat().st_size == 0:
        registrar_fallo("el MP3 salio vacio. Reporta el caso.")

    # Segundo llamado a reescribir_xing(), ahora sobre el archivo FINAL que
    # queda en disco, no solo sobre cada pedazo (el llamado de arriba, en
    # hablar_pedazo). Importa cuando hubo varios pedazos: `unir()` los pega
    # con "-c copy", asi que el resultado hereda tal cual la cabecera del
    # primer pedazo, que solo describe la duracion de ESE pedazo. Sin este
    # segundo llamado, el archivo unido volveria a mentir. En el caso de un
    # solo pedazo es un no-op (ya quedo correcto arriba), pero es mas simple
    # aplicarlo siempre que distinguir los dos caminos.
    datos_finales = ruta_salida.read_bytes()
    datos_arreglados = reescribir_xing(datos_finales)
    if datos_arreglados != datos_finales:
        ruta_salida.write_bytes(datos_arreglados)

    anotar_log(origen, args.voz, caracteres, costo, ruta_salida, ok=True)
    mb = ruta_salida.stat().st_size / 1024 / 1024
    print(f"OK -> {ruta_salida}  ({caracteres:,} caracteres, {mb:.1f} MB, "
          f"voz={args.voz}, {len(pedazos)} llamada(s), ~${costo:.5f} USD)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
