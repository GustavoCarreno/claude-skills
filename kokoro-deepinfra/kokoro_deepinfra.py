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
