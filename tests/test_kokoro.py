import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "kokoro-deepinfra"))

from kokoro_deepinfra import limpiar_markdown


def test_quita_las_almohadillas_pero_conserva_el_titulo():
    assert limpiar_markdown("## Pendientes urgentes") == "Pendientes urgentes"


def test_quita_la_casilla_sin_palomear():
    assert limpiar_markdown("- [ ] Mandar la carta al broker") == "Mandar la carta al broker"


def test_quita_la_casilla_palomeada():
    assert limpiar_markdown("- [x] Firmar el acuerdo") == "Firmar el acuerdo"


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
