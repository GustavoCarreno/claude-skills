import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kokoro-deepinfra"))

from kokoro_deepinfra import limpiar_markdown


def test_quita_las_almohadillas_pero_conserva_el_titulo():
    assert limpiar_markdown("## Pendientes urgentes") == "Pendientes urgentes"


def test_quita_la_casilla_sin_palomear():
    assert limpiar_markdown("- [ ] Mandar la carta al broker") == "Mandar la carta al broker"


def test_quita_la_casilla_palomeada():
    assert limpiar_markdown("- [x] Firmar el acuerdo") == "Firmar el acuerdo"


def test_quita_la_casilla_aunque_le_falte_el_espacio():
    assert limpiar_markdown("- [ ]tarea sin espacio") == "tarea sin espacio"


def test_quita_las_marcas_de_enfasis_y_conserva_el_texto():
    assert limpiar_markdown("Es **urgente** y *nuevo* y `exacto`") == "Es urgente y nuevo y exacto"


def test_conserva_el_guion_bajo_dentro_de_una_palabra():
    assert limpiar_markdown("el archivo pendientes_viejos") == "el archivo pendientes_viejos"


def test_de_una_liga_conserva_el_texto_y_tira_la_url():
    assert limpiar_markdown("Ver [el contrato](https://ejemplo.com/a/b)") == "Ver el contrato"


def test_tira_las_imagenes_completas():
    assert limpiar_markdown("Antes ![diagrama](d.png) después") == "Antes  después"


def test_tira_las_reglas_horizontales():
    assert limpiar_markdown("uno\n---\ndos") == "uno\ndos"


def test_quita_la_vineta_y_la_numeracion():
    assert limpiar_markdown("- uno\n2. dos") == "uno\ndos"


def test_quita_la_marca_de_cita():
    assert limpiar_markdown("> una cita") == "una cita"


def test_aplana_la_tabla_por_renglon_y_tira_el_separador():
    entrada = "| Concepto | Monto |\n|---|---|\n| Renta | 25000 |"
    assert limpiar_markdown(entrada) == "Concepto, Monto\nRenta, 25000"


def test_sustituye_el_bloque_de_codigo_por_una_nota_hablada():
    salida = limpiar_markdown("antes\n```python\nprint(1)\n```\ndespués")
    assert "print" not in salida
    assert "bloque de código" in salida


def test_colapsa_los_renglones_en_blanco_repetidos():
    assert limpiar_markdown("uno\n\n\n\ndos") == "uno\n\ndos"


def test_el_texto_sin_markdown_pasa_intacto():
    llano = "Tienes tres pendientes urgentes para hoy."
    assert limpiar_markdown(llano) == llano


from kokoro_deepinfra import trocear, LIMITE_LLAMADA, OBJETIVO_TROZO


def test_un_texto_corto_es_un_solo_pedazo():
    assert trocear("Hola, qué tal.") == ["Hola, qué tal."]


def test_ningun_pedazo_pasa_del_limite_de_la_api():
    texto = ("Esta es una oracion de prueba con su punto final. " * 600)
    for pedazo in trocear(texto):
        assert len(pedazo) <= LIMITE_LLAMADA


def test_corta_en_fin_de_parrafo_cuando_lo_hay():
    izq = "a" * 8000
    der = "b" * 3000
    pedazos = trocear(izq + "\n\n" + der, objetivo=9000)
    assert pedazos[0] == izq
    assert pedazos[1] == der


def test_corta_en_fin_de_oracion_cuando_no_hay_parrafo():
    izq = "a" * 8000 + "."
    der = "b" * 3000
    pedazos = trocear(izq + " " + der, objetivo=9000)
    assert pedazos[0].endswith(".")
    assert pedazos[1] == der


def test_no_pierde_texto_al_trocear():
    texto = ("Oracion numero uno. Oracion numero dos. " * 500)
    unido = " ".join(trocear(texto))
    assert unido.split() == texto.split()


def test_un_texto_sin_ninguna_frontera_se_corta_a_lo_bruto():
    texto = "a" * 25000
    pedazos = trocear(texto, objetivo=9000)
    assert len(pedazos) == 3
    assert "".join(pedazos) == texto


def test_el_objetivo_deja_margen_bajo_el_limite_duro():
    assert OBJETIVO_TROZO < LIMITE_LLAMADA


def test_diez_mil_caracteres_exactos_es_una_sola_llamada():
    texto = "a" * LIMITE_LLAMADA
    assert trocear(texto) == [texto]


def test_diez_mil_uno_caracteres_ya_se_parte():
    texto = "a" * (LIMITE_LLAMADA + 1)
    pedazos = trocear(texto)
    assert len(pedazos) > 1


# --------------------------------------------------------------------------
# reescribir_xing: el cuadro Xing/Info que miente sobre la duracion
# --------------------------------------------------------------------------
#
# Cabecera real, capturada de un mp3 real de Kokoro (4 ago 2026, el audio del
# reporte de este defecto): version MPEG2 (LSF), Layer III, mono, 64 kbps,
# 24 kHz. Con esos parametros el cuadro completo mide 72*64000//24000 = 192
# bytes, y la etiqueta Xing/Info cae en el byte 13 (offset 9 tras los 4 bytes
# de cabecera, que es lo que le toca a MPEG2-LSF mono). Los dos numeros
# (cabecera y offset) son los mismos que trae el archivo real del reporte,
# no un invento para la prueba. Las banderas por defecto (0x0F) tambien son
# las reales: el archivo del reporte trae los cuatro campos opcionales
# (cuadros, bytes, TOC, calidad).
_CABECERA_REAL = bytes([0xFF, 0xF3, 0x84, 0xC4])
_TAMANIO_FRAME_REAL = 192
_OFFSET_TAG_REAL = 13  # 4 (cabecera) + 9 (side-info de MPEG2-LSF mono)
_FRAMES_OFFSET_REAL = _OFFSET_TAG_REAL + 8   # firma(4) + flags(4)
_BYTES_OFFSET_REAL = _FRAMES_OFFSET_REAL + 4
_TOC_OFFSET_REAL = _BYTES_OFFSET_REAL + 4

from kokoro_deepinfra import reescribir_xing


def _cuadro(firma=None, tamanio=_TAMANIO_FRAME_REAL, offset_tag=_OFFSET_TAG_REAL,
            cabecera=_CABECERA_REAL, relleno=b"\x00", flags=0x0F,
            frames_declarados=175, bytes_declarados=31272):
    """Arma un cuadro MPEG sintetico con la cabecera real, con o sin Xing/Info.

    `firma` None deja el cuadro sin etiqueta (relleno liso, como un cuadro de
    audio real). Con una firma (b"Xing" o b"Info") la siembra en el offset
    exacto donde el reproductor real la encontro, junto con `flags` y los
    campos que esas banderas dicen que vienen despues (cuadros y bytes
    declarados, mentirosos a proposito por defecto -- son los mismos 175 /
    31272 del archivo real -- y una tabla de posiciones en ceros, que
    tampoco importa lo que traiga: es justo lo que `reescribir_xing` debe
    sobreescribir).
    """
    cuerpo = bytearray(relleno * (tamanio - len(cabecera)))
    if firma is not None:
        pos = offset_tag - len(cabecera)
        cuerpo[pos:pos + 4] = firma
        campo = pos + 4
        cuerpo[campo:campo + 4] = flags.to_bytes(4, "big")
        campo += 4
        if flags & 0x0001:
            cuerpo[campo:campo + 4] = frames_declarados.to_bytes(4, "big")
            campo += 4
        if flags & 0x0002:
            cuerpo[campo:campo + 4] = bytes_declarados.to_bytes(4, "big")
            campo += 4
        if flags & 0x0004:
            campo += 100  # tabla de posiciones: se deja en ceros a proposito
        if flags & 0x0008:
            campo += 4  # indicador de calidad: no se toca nunca, se deja en ceros
    return cabecera + bytes(cuerpo)


def _id3v2(cuerpo=b"algo de metadata que no es audio"):
    """Cabecera ID3v2 minima (tamanio syncsafe, sin footer) seguida de `cuerpo`."""
    tam = len(cuerpo)
    tam_syncsafe = bytes([
        (tam >> 21) & 0x7F, (tam >> 14) & 0x7F, (tam >> 7) & 0x7F, tam & 0x7F,
    ])
    return b"ID3" + bytes([4, 0, 0]) + tam_syncsafe + cuerpo


def test_reescribe_el_cuadro_con_etiqueta_xing_en_vez_de_quitarlo():
    # El "resto" no parsea como cuadros MPEG (es texto), asi que el
    # recorrido de reescribir_xing solo cuenta el propio cuadro Xing: 1
    # cuadro, 192 bytes. Nada se quita: el archivo queda del mismo tamanio y
    # la cola no se toca.
    resto = b"AUDIO-REAL-QUE-SIGUE" * 20
    datos = _cuadro(firma=b"Xing") + resto
    resultado = reescribir_xing(datos)
    assert len(resultado) == len(datos)
    assert resultado[_TAMANIO_FRAME_REAL:] == resto
    assert resultado[_OFFSET_TAG_REAL:_OFFSET_TAG_REAL + 4] == b"Xing"
    assert int.from_bytes(resultado[_FRAMES_OFFSET_REAL:_FRAMES_OFFSET_REAL + 4], "big") == 1
    assert int.from_bytes(resultado[_BYTES_OFFSET_REAL:_BYTES_OFFSET_REAL + 4], "big") == _TAMANIO_FRAME_REAL


def test_reescribe_el_cuadro_con_etiqueta_info_en_vez_de_quitarlo():
    resto = b"OTRO-PEDAZO-DE-AUDIO" * 20
    datos = _cuadro(firma=b"Info") + resto
    resultado = reescribir_xing(datos)
    assert len(resultado) == len(datos)
    assert resultado[_TAMANIO_FRAME_REAL:] == resto
    assert resultado[_OFFSET_TAG_REAL:_OFFSET_TAG_REAL + 4] == b"Info"


def test_no_toca_nada_si_el_primer_cuadro_no_trae_xing_ni_info():
    # Mismo header/tamanio de un cuadro real, pero sin la firma en su offset:
    # es un cuadro de audio de verdad, no debe tocarse.
    datos = _cuadro(firma=None) + b"MAS-AUDIO" * 10
    assert reescribir_xing(datos) == datos


def test_no_toca_nada_si_no_hay_ningun_cuadro_mpeg_reconocible():
    datos = b"esto no es mp3, es basura de otra API" * 5
    assert reescribir_xing(datos) == datos


def test_archivo_vacio_no_revienta():
    assert reescribir_xing(b"") == b""


def test_archivo_de_unos_pocos_bytes_no_revienta():
    for datos in (b"", b"\xff", b"\xff\xf3", b"\xff\xf3\x84", b"X"):
        assert reescribir_xing(datos) == datos


def test_respuesta_de_error_json_disfrazada_no_revienta():
    # Forma real de un error de la API (400/500) que igual podria llegar aqui
    # si algun dia se llama antes de validar parece_mp3(): no debe tronar.
    datos = b'{"message":"1 validation error for KokoroTextToSpeechIn"}'
    assert reescribir_xing(datos) == datos


def test_conserva_el_id3v2_intacto_y_solo_reescribe_los_campos_del_cuadro_xing():
    id3 = _id3v2()
    resto = b"cola-de-audio-real" * 5
    datos = id3 + _cuadro(firma=b"Xing") + resto
    resultado = reescribir_xing(datos)
    assert len(resultado) == len(datos)
    assert resultado.startswith(id3)
    assert resultado[len(id3) + _TAMANIO_FRAME_REAL:] == resto
    offset_tag = len(id3) + _OFFSET_TAG_REAL
    assert resultado[offset_tag:offset_tag + 4] == b"Xing"


def test_no_toca_nada_si_el_cuadro_declarado_se_sale_del_archivo():
    # Cabecera real + Xing en su offset, pero el archivo se corta antes de
    # completar el cuadro entero (192 bytes) -> no hay que confiar en un
    # tamanio de cuadro que no cabe en lo que de verdad llego.
    datos = _cuadro(firma=b"Xing")[:100]
    assert reescribir_xing(datos) == datos


def test_layer_distinto_de_tres_no_se_toca_aunque_tenga_xing():
    # Layer II (layer_id=10) con la firma Xing en un offset cualquiera: no es
    # el caso que este arreglo cubre (Xing/Info solo aplica a Layer III), asi
    # que debe dejarse intacto en vez de adivinar un tamanio de cuadro.
    cabecera_layer2 = bytes([0xFF, 0xF5, 0x84, 0xC4])  # layer_id=10=LayerII
    datos = cabecera_layer2 + b"\x00" * 50 + b"Xing" + b"\x00" * 100
    assert reescribir_xing(datos) == datos


def test_no_toca_nada_si_las_banderas_no_declaran_el_campo_de_cuadros():
    # Xing presente, pero sin la bandera de "cuadros" (flags=0x0002, solo
    # bytes): sin ese campo no hay nada que corrija el sintoma que motivo
    # este arreglo (la duracion declarada), asi que mejor no tocar nada en
    # vez de reescribir solo un campo que ningun reproductor usa para la
    # duracion.
    datos = _cuadro(firma=b"Xing", flags=0x0002) + b"cola-de-audio" * 10
    assert reescribir_xing(datos) == datos


def test_reescribe_cuadros_y_bytes_reales_recorriendo_el_archivo():
    # 1 cuadro Xing + 9 cuadros de audio "reales" (mismo tamanio, generados
    # con la misma cabecera, como los produce un flujo real): el recorrido
    # debe contar los 10 y sumar sus 192 bytes cada uno.
    n_extra = 9
    cuadro_normal = _cuadro(firma=None)
    datos = _cuadro(firma=b"Xing") + cuadro_normal * n_extra
    total_cuadros_esperado = 1 + n_extra
    total_bytes_esperado = _TAMANIO_FRAME_REAL * total_cuadros_esperado

    resultado = reescribir_xing(datos)

    assert len(resultado) == len(datos)
    assert int.from_bytes(resultado[_FRAMES_OFFSET_REAL:_FRAMES_OFFSET_REAL + 4], "big") == total_cuadros_esperado
    assert int.from_bytes(resultado[_BYTES_OFFSET_REAL:_BYTES_OFFSET_REAL + 4], "big") == total_bytes_esperado
    # Solo se toca el primer cuadro: los 9 de "audio" quedan byte por byte
    # identicos.
    assert resultado[_TAMANIO_FRAME_REAL:] == datos[_TAMANIO_FRAME_REAL:]


def test_la_tabla_de_posiciones_queda_creciente_y_cubre_todo_el_archivo():
    n_extra = 49  # 50 cuadros en total: comodo para repartir en centesimos
    cuadro_normal = _cuadro(firma=None)
    datos = _cuadro(firma=b"Xing") + cuadro_normal * n_extra

    resultado = reescribir_xing(datos)
    toc = resultado[_TOC_OFFSET_REAL:_TOC_OFFSET_REAL + 100]

    assert len(toc) == 100
    assert toc[0] == 0
    assert all(toc[i] <= toc[i + 1] for i in range(99))  # no decreciente
    assert toc[-1] >= 250  # el ultimo centesimo cae cerca del final (escala 0-255)


def test_el_archivo_real_del_reporte_deja_de_declarar_los_175_cuadros_falsos():
    """Reproduce el defecto reportado con el mp3 real (sin llamar a la API).

    El archivo de ejemplo trae la cabecera real de Kokoro: declara 175
    cuadros / 4.20s / 31,272 bytes cuando el audio real mide bastante mas.
    Aqui se arma solo el primer cuadro con esos bytes exactos (capturados
    del archivo real del reporte) para no commitear un binario de 400 KB al
    repo; el resto del archivo se representa con datos de relleno que NO
    parsean como cuadros MPEG (0x12 no es 0xFF), asi que el recorrido de
    reescribir_xing solo puede contar el propio cuadro Xing -- lo que
    importa para esta prueba es que los 175 cuadros / 31,272 bytes
    FALSOS ya no aparecen en la cabecera, y que el archivo no se corrompe
    (mismo tamanio, misma cola de bytes).
    """
    # Los primeros 40 bytes tal cual salieron del archivo real (`data[:40]`
    # leido con Read del mp3 del reporte), completados a los 192 bytes del
    # cuadro con relleno: reescribir_xing solo necesita ver hasta el offset
    # de la firma para decidir, el resto del cuadro no importa.
    inicio_real = bytes([
        0xFF, 0xF3, 0x84, 0xC4, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00,
    ]) + b"Xing" + bytes([
        0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00, 0xAF, 0x00, 0x00, 0x7A,
        0x28, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 0x08, 0x0B, 0x0D, 0x0F,
        0x12, 0x14,
    ])
    assert len(inicio_real) < _TAMANIO_FRAME_REAL
    primer_cuadro_real = inicio_real + b"\x00" * (_TAMANIO_FRAME_REAL - len(inicio_real))
    resto_real = b"\x12\x34" * 100000  # ~51s de "audio" a efectos de esta prueba
    datos = primer_cuadro_real + resto_real

    assert datos[13:17] == b"Xing"  # el mismo byte 13 que reporto el usuario
    assert int.from_bytes(datos[21:25], "big") == 175  # los cuadros falsos del reporte
    assert int.from_bytes(datos[25:29], "big") == 31272  # los bytes falsos del reporte

    resultado = reescribir_xing(datos)

    # Nada se quita ni se corrompe: mismo tamanio, misma cola de bytes.
    assert len(resultado) == len(datos)
    assert resultado[_TAMANIO_FRAME_REAL:] == resto_real
    assert resultado[13:17] == b"Xing"
    # Los 175 cuadros / 31,272 bytes falsos ya no estan. Como `resto_real`
    # no parsea como cuadros MPEG, lo unico contable es el propio cuadro
    # Xing (1 cuadro, 192 bytes) -- lo que demuestra que la cabecera se
    # reescribio con lo que de verdad se pudo recorrer, no con el numero
    # viejo.
    assert int.from_bytes(resultado[21:25], "big") == 1
    assert int.from_bytes(resultado[25:29], "big") == _TAMANIO_FRAME_REAL


# --------------------------------------------------------------------------
# unir(): que la verificacion de duracion siga funcionando con encabezados
# Xing ya reescritos (correctos, no removidos), sin dar falsos positivos ni
# dejar de atrapar un pedazo truncado. Requiere ffmpeg/ffprobe de verdad: se
# salta si no estan.
# --------------------------------------------------------------------------

_TIENE_FFMPEG = shutil.which("ffmpeg") and shutil.which("ffprobe")


class _FalloDeUnion(Exception):
    pass


def _registrar_fallo_de_prueba(msg, codigo=1):
    raise _FalloDeUnion(msg)


def _generar_pedazo_real(ruta, duracion_seg):
    """Un mp3 real y corto (tono, no silencio: silencio puro a veces se
    codifica sin generar cuadro Xing) via ffmpeg, con su cabecera Xing ya
    reescrita, igual que lo deja hablar_pedazo() antes de guardarlo."""
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", f"sine=frequency=440:duration={duracion_seg}",
         "-ar", "24000", "-ac", "1", "-b:a", "64k", str(ruta)],
        check=True, capture_output=True,
    )
    datos = reescribir_xing(ruta.read_bytes())
    ruta.write_bytes(datos)
    return datos


@pytest.mark.skipif(not _TIENE_FFMPEG, reason="requiere ffmpeg/ffprobe instalados")
def test_unir_construye_un_mp3_correcto_con_pedazos_con_cabecera_corregida():
    from kokoro_deepinfra import unir, duracion_segundos

    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp)
        p1 = carpeta / "pedazo_001.mp3"
        p2 = carpeta / "pedazo_002.mp3"
        _generar_pedazo_real(p1, 1.0)
        _generar_pedazo_real(p2, 1.5)
        # duracion_segundos() decodifica paquete por paquete, sin importarle
        # la cabecera Xing (ver su propio docstring): la verificacion de
        # unir() no debe romperse ni de casualidad porque cada pedazo ahora
        # SI trae una cabecera Xing (reescrita con sus valores reales, ya
        # no removida como antes).
        assert duracion_segundos(p1) == pytest.approx(1.0, abs=0.2)
        assert duracion_segundos(p2) == pytest.approx(1.5, abs=0.2)

        destino = carpeta / "final.mp3"
        resultado = unir([p1, p2], destino, carpeta, _registrar_fallo_de_prueba)

        assert resultado == destino
        assert destino.exists()
        final = duracion_segundos(destino)
        assert final is not None
        assert final == pytest.approx(2.5, abs=0.2)


@pytest.mark.skipif(not _TIENE_FFMPEG, reason="requiere ffmpeg/ffprobe instalados")
def test_unir_sigue_atrapando_un_pedazo_truncado_con_encabezados_corregidos():
    from kokoro_deepinfra import unir, duracion_segundos

    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp)
        p1 = carpeta / "pedazo_001.mp3"
        p2 = carpeta / "pedazo_002.mp3"
        _generar_pedazo_real(p1, 2.0)
        _generar_pedazo_real(p2, 2.0)
        # Se trunca el segundo pedazo por debajo de un cuadro completo (192
        # bytes a este bitrate/samplerate): simula una respuesta de la API
        # que se corto a medio camino, tan temprano que ni ffprobe le saca
        # duracion. Con la cabecera Xing ya corregida (no removida), para
        # probar que esta verificacion no se rompe con encabezados nuevos.
        completo = p2.read_bytes()
        p2.write_bytes(completo[:100])
        assert duracion_segundos(p2) is None  # confirma que la prueba es valida

        destino = carpeta / "final.mp3"
        with pytest.raises(_FalloDeUnion, match="corrupto"):
            unir([p1, p2], destino, carpeta, _registrar_fallo_de_prueba)
        # fallar() debe haber limpiado el destino a medias.
        assert not destino.exists()


# --------------------------------------------------------------------------
# Lectura de la llave desde el archivo de credenciales
# --------------------------------------------------------------------------

import kokoro_deepinfra as k


@pytest.fixture
def credenciales(tmp_path, monkeypatch):
    """Apunta el lector del archivo de credenciales a un temporal."""
    ruta = tmp_path / "credentials"
    monkeypatch.setattr(k, "RUTA_CREDENCIALES", ruta)
    return ruta


def test_lee_la_llave_de_la_linea_exportable(credenciales):
    credenciales.write_text('export DEEPINFRA_API_KEY="abc123"\n', encoding="utf-8")
    assert k.leer_llave_de_archivo() == "abc123"


def test_ignora_una_variable_de_nombre_parecido(credenciales):
    """El mismo defecto que su gemela whisper-deepinfra, arreglado igual."""
    credenciales.write_text(
        'export DEEPINFRA_API_KEY_VIEJA="la-de-antes"\n'
        'export DEEPINFRA_API_KEY="la-buena"\n',
        encoding="utf-8")
    assert k.leer_llave_de_archivo() == "la-buena"


def test_no_se_queda_con_una_variable_parecida_cuando_no_esta_la_buena(credenciales):
    credenciales.write_text('export DEEPINFRA_API_KEY_VIEJA="la-de-antes"\n',
                            encoding="utf-8")
    assert k.leer_llave_de_archivo() is None


def test_ignora_el_nombre_suelto_sin_signo_de_igual(credenciales):
    credenciales.write_text("DEEPINFRA_API_KEY\n", encoding="utf-8")
    assert k.leer_llave_de_archivo() is None
