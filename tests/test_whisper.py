import json
import sys
from http.client import RemoteDisconnected
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "whisper-deepinfra"))

import whisper_deepinfra as w


# --------------------------------------------------------------------------
# Lectura de la llave desde el archivo de credenciales
# --------------------------------------------------------------------------

@pytest.fixture
def credenciales(tmp_path, monkeypatch):
    """Apunta el lector al archivo de credenciales a un temporal."""
    ruta = tmp_path / "credentials"
    monkeypatch.setattr(w, "RUTA_CREDENCIALES", ruta)
    return ruta


def test_lee_la_llave_de_la_linea_exportable(credenciales):
    credenciales.write_text('export DEEPINFRA_API_KEY="abc123"\n', encoding="utf-8")
    assert w.leer_llave_de_archivo() == "abc123"


def test_lee_la_llave_sin_export_ni_comillas(credenciales):
    credenciales.write_text("DEEPINFRA_API_KEY=abc123\n", encoding="utf-8")
    assert w.leer_llave_de_archivo() == "abc123"


def test_ignora_una_variable_de_nombre_parecido(credenciales):
    """DEEPINFRA_API_KEY_VIEJA no es DEEPINFRA_API_KEY.

    Con el prefijo suelto se devolvia la llave equivocada y el error llegaba
    hasta un HTTP 401, que manda a revisar la llave buena en vez de la de al lado.
    """
    credenciales.write_text(
        'export DEEPINFRA_API_KEY_VIEJA="la-de-antes"\n'
        'export DEEPINFRA_API_KEY="la-buena"\n',
        encoding="utf-8")
    assert w.leer_llave_de_archivo() == "la-buena"


def test_no_se_queda_con_una_variable_parecida_cuando_no_esta_la_buena(credenciales):
    credenciales.write_text('export DEEPINFRA_API_KEY_VIEJA="la-de-antes"\n',
                            encoding="utf-8")
    assert w.leer_llave_de_archivo() is None


def test_ignora_el_nombre_suelto_sin_signo_de_igual(credenciales):
    credenciales.write_text("DEEPINFRA_API_KEY\n", encoding="utf-8")
    assert w.leer_llave_de_archivo() is None


def test_devuelve_nada_si_no_hay_archivo(credenciales):
    assert w.leer_llave_de_archivo() is None


# --------------------------------------------------------------------------
# Reintento ante cortes de red que no son URLError
# --------------------------------------------------------------------------

class RespuestaFalsa:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _urlopen_que_falla(errores, respuesta, registro):
    """Levanta cada error de la lista y luego contesta bien."""
    def falso(pedido, timeout=None):
        registro.append(1)
        if len(registro) <= len(errores):
            raise errores[len(registro) - 1]
        return RespuestaFalsa(respuesta)
    return falso


@pytest.fixture
def audio(tmp_path):
    ruta = tmp_path / "grabacion.mp3"
    ruta.write_bytes(b"no es audio de verdad, pero se manda igual")
    return ruta


@pytest.mark.parametrize("error", [
    TimeoutError("timed out"),
    RemoteDisconnected("Remote end closed connection without response"),
    ConnectionResetError("connection reset by peer"),
])
def test_reintenta_cuando_la_red_corta_con_algo_que_no_es_urlerror(
        audio, monkeypatch, error):
    """Ninguno de estos tres es URLError y los tres pasan de verdad.

    El timeout de la lectura salta como TimeoutError, y un corte a media
    respuesta llega como RemoteDisconnected o ConnectionResetError. Sin
    atraparlos se escapaban como traza cruda, con la llamada ya pagada.
    """
    registro = []
    monkeypatch.setattr(w.urllib.request, "urlopen",
                        _urlopen_que_falla([error], {"text": "hola"}, registro))
    monkeypatch.setattr(w.time, "sleep", lambda _: None)

    datos = w.transcribir_archivo(audio, "llave", "transcribe", None)

    assert datos["text"] == "hola"
    assert len(registro) == 2


def test_se_rinde_con_mensaje_claro_si_la_red_nunca_levanta(audio, monkeypatch):
    registro = []
    errores = [TimeoutError("timed out")] * 3
    monkeypatch.setattr(w.urllib.request, "urlopen",
                        _urlopen_que_falla(errores, {"text": "x"}, registro))
    monkeypatch.setattr(w.time, "sleep", lambda _: None)

    with pytest.raises(SystemExit):
        w.transcribir_archivo(audio, "llave", "transcribe", None)
    assert len(registro) == 3


# --------------------------------------------------------------------------
# Aviso de transcripcion sospechosamente corta
# --------------------------------------------------------------------------

def test_una_transcripcion_de_largo_normal_no_avisa():
    assert w.revisar_longitud(900, 60) is None


def test_avisa_cuando_devuelve_un_puñado_de_caracteres_de_un_audio_largo():
    """El caso real: reporto exito con 11 caracteres de una grabacion entera."""
    aviso = w.revisar_longitud(11, 300)
    assert aviso is not None
    assert "11" in aviso


def test_no_avisa_si_no_se_conoce_la_duracion():
    assert w.revisar_longitud(11, None) is None


def test_no_avisa_con_un_audio_de_unos_segundos():
    """En media frase caben pocos caracteres y eso es legitimo."""
    assert w.revisar_longitud(5, 20) is None


def test_el_umbral_es_un_caracter_por_segundo():
    assert w.revisar_longitud(60, 60) is None
    assert w.revisar_longitud(59, 60) is not None


def test_el_aviso_dice_cuanto_duraba_el_audio():
    aviso = w.revisar_longitud(11, 300)
    assert "300" in aviso or "5.0 min" in aviso
