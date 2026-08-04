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
