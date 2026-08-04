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
import re

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
