"""Pruebas de la bitacora automatica. Solo biblioteca estandar.

Se corren con:  python3 -m unittest discover -s bitacora -v
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

_RUTA = Path(__file__).resolve().parent.parent / "bitacora" / "bitacora.py"
_spec = importlib.util.spec_from_file_location("bitacora", _RUTA)
bitacora = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bitacora)


class Base(unittest.TestCase):
    """Cada prueba corre con su propio HOME, asi que no toca el estado real."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.casa = Path(self._tmp.name).resolve()
        self._entorno = mock.patch.dict(
            os.environ,
            {"HOME": str(self.casa), "USERPROFILE": str(self.casa)},
        )
        self._entorno.start()
        # Sin esto, una bateria corrida con BITACORA_EN_CIERRE=1 ya puesto en
        # el ambiente real pasa varias pruebas sin ejercitar nada, porque los
        # subcomandos salen temprano. mock.patch.dict restaura la instantanea
        # original al hacer stop(), asi que borrarla aqui no le quita nada al
        # entorno real fuera de la prueba.
        os.environ.pop("BITACORA_EN_CIERRE", None)
        self.raiz = self.casa / "claude"
        self.raiz.mkdir(parents=True)
        (self.casa / ".claude").mkdir(parents=True)
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({"raiz_proyectos": str(self.raiz)}), encoding="utf-8"
        )

    def tearDown(self):
        self._entorno.stop()
        self._tmp.cleanup()

    def proyecto(self, nombre, con_claude_md=True):
        ruta = self.raiz / nombre
        ruta.mkdir(parents=True, exist_ok=True)
        if con_claude_md:
            (ruta / "CLAUDE.md").write_text("# " + nombre + "\n", encoding="utf-8")
        return ruta.resolve()

    def base_de(self, sid, proy):
        return bitacora._base(sid, proy, self.raiz)

    def fechar(self, ruta, segundos_atras=0):
        """Fija el mtime de forma explicita.

        Nunca comparar fechas por el orden en que se escribieron los archivos:
        dos escrituras seguidas pueden caer en el mismo tick del sistema de
        archivos y la prueba pasa o falla segun la maquina.
        """
        cuando = time.time() - segundos_atras
        os.utime(ruta, (cuando, cuando))

    def _correr(self, funcion, payload, argv=None):
        entrada = io.StringIO(json.dumps(payload))
        salida = io.StringIO()
        with mock.patch.object(sys, "stdin", entrada), \
             mock.patch.object(sys, "stdout", salida):
            codigo = funcion(argv) if argv is not None else funcion()
        return codigo, salida.getvalue()

    def marcar_con(self, payload):
        return self._correr(bitacora.marcar, payload)

    def verificar_con(self, payload):
        return self._correr(bitacora.verificar, payload)

    def pendiente_con(self, payload):
        return self._correr(bitacora.pendiente, payload)

    def pago(self, sid, proy, herramienta="Write", archivo=None, comando=None):
        """Payload de PostToolUse como lo manda Claude Code."""
        entrada = {}
        if archivo is not None:
            entrada["file_path"] = str(archivo)
        if comando is not None:
            entrada["command"] = comando
        return {
            "session_id": sid,
            "cwd": str(proy),
            "tool_name": herramienta,
            "tool_input": entrada,
        }


class EstadoRedirigible(Base):
    def test_las_rutas_de_estado_siguen_al_HOME_de_la_prueba(self):
        self.assertEqual(
            bitacora._dir_marcas(), self.casa / ".cache" / "claude-bitacora"
        )
        self.assertEqual(
            bitacora._ruta_config(), self.casa / ".claude" / "bitacora.json"
        )
        self.assertEqual(
            bitacora._ruta_log(),
            self.casa / ".cache" / "claude-bitacora" / "cierres.log",
        )

    def test_la_raiz_configurada_le_gana_a_la_deducida(self):
        self.assertEqual(bitacora._config()["raiz"], self.raiz)

    def test_sin_configuracion_deduce_la_convencion_del_lanzador(self):
        (self.casa / ".claude" / "bitacora.json").unlink()
        self.assertEqual(bitacora._config()["raiz"], self.casa / "claude")

    def test_configuracion_corrupta_no_revienta(self):
        (self.casa / ".claude" / "bitacora.json").write_text("{ no es json",
                                                             encoding="utf-8")
        self.assertEqual(bitacora._config()["raiz"], self.casa / "claude")

    def test_umbral_no_numerico_cae_al_valor_por_defecto(self):
        """Finding 8: int("seis") revienta con ValueError, fuera del try que
        rodea la lectura del JSON. Sin este freno, un typo del cliente en
        bitacora.json mata marcar/verificar/cerrar/pendiente en CADA
        invocacion, para siempre."""
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({"raiz_proyectos": str(self.raiz), "umbral": "seis"}),
            encoding="utf-8",
        )
        cfg = bitacora._config()
        self.assertEqual(cfg["umbral"], bitacora.UMBRAL_POR_DEFECTO)
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("config invalida", registro)
        self.assertIn("umbral", registro)

    def test_max_recordatorios_no_numerico_cae_al_valor_por_defecto(self):
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({
                "raiz_proyectos": str(self.raiz),
                "max_recordatorios": None,
            }),
            encoding="utf-8",
        )
        cfg = bitacora._config()
        self.assertEqual(
            cfg["max_recordatorios"], bitacora.MAX_RECORDATORIOS_POR_DEFECTO
        )

    def test_el_aviso_de_config_invalida_no_se_repite_en_cada_llamada(self):
        """El typo es persistente: sin este freno, cada hook (potencialmente
        cientos al dia) escribiria la misma linea en cierres.log."""
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({"raiz_proyectos": str(self.raiz), "umbral": "seis"}),
            encoding="utf-8",
        )
        bitacora._config()
        bitacora._config()
        bitacora._config()
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertEqual(registro.count("config invalida"), 1)

    def test_raiz_proyectos_inexistente_se_registra(self):
        """El modo de fallar de este mecanismo es el silencio: con la raiz
        mal apuntada, _proyecto_valido nunca es cierto para nadie y el hook
        nunca dispara, sin ningun error visible salvo que se registre aqui."""
        inexistente = str(self.casa / "no-existe-de-verdad")
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({"raiz_proyectos": inexistente}),
            encoding="utf-8",
        )
        cfg = bitacora._config()
        self.assertEqual(cfg["raiz"], Path(inexistente))
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("config invalida", registro)
        self.assertIn("raiz_proyectos", registro)

    def test_raiz_proyectos_existente_no_avisa(self):
        bitacora._config()
        self.assertFalse(bitacora._ruta_log().exists())


class Slug(Base):
    def test_proyecto_simple(self):
        proy = self.proyecto("devops")
        self.assertEqual(bitacora._slug(proy, self.raiz), "devops")

    def test_proyecto_anidado_junta_las_partes_con_guion(self):
        proy = self.proyecto("cliente/subproyecto")
        self.assertEqual(bitacora._slug(proy, self.raiz), "cliente-subproyecto")


class ProyectoValido(Base):
    def test_dentro_de_la_raiz_y_con_claude_md(self):
        proy = self.proyecto("devops")
        self.assertTrue(bitacora._proyecto_valido(proy, self.raiz))

    def test_sin_claude_md_no_es_valido(self):
        proy = self.proyecto("sinbitacora", con_claude_md=False)
        self.assertFalse(bitacora._proyecto_valido(proy, self.raiz))

    def test_fuera_de_la_raiz_no_es_valido(self):
        fuera = self.casa / "otro"
        fuera.mkdir()
        (fuera / "CLAUDE.md").write_text("x", encoding="utf-8")
        self.assertFalse(bitacora._proyecto_valido(fuera.resolve(), self.raiz))

    def test_ruta_nula_no_es_valida(self):
        self.assertFalse(bitacora._proyecto_valido(None, self.raiz))


class HayPendiente(Base):
    def preparar(self, conteo, trabajo_despues_del_md):
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text(str(conteo), encoding="utf-8")
        md = proy / "CLAUDE.md"
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        # Fechas explicitas: el reloj del sistema de archivos no tiene la
        # resolucion suficiente para distinguir dos escrituras seguidas.
        ahora = time.time()
        if trabajo_despues_del_md:
            os.utime(md, (ahora - 60, ahora - 60))
            os.utime(trabajo, (ahora, ahora))
        else:
            os.utime(trabajo, (ahora - 60, ahora - 60))
            os.utime(md, (ahora, ahora))
        return base, proy

    def test_hay_pendiente_cuando_el_trabajo_es_mas_nuevo_que_el_claude_md(self):
        base, proy = self.preparar(conteo=6, trabajo_despues_del_md=True)
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))

    def test_no_hay_pendiente_cuando_el_claude_md_es_mas_nuevo(self):
        base, proy = self.preparar(conteo=6, trabajo_despues_del_md=False)
        self.assertFalse(bitacora._hay_pendiente(base, proy, 6))

    def test_no_hay_pendiente_bajo_el_umbral(self):
        base, proy = self.preparar(conteo=5, trabajo_despues_del_md=True)
        self.assertFalse(bitacora._hay_pendiente(base, proy, 6))

    def test_no_hay_pendiente_sin_marca_de_trabajo(self):
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        self.assertFalse(bitacora._hay_pendiente(base, proy, 6))

    def test_sin_claude_md_todo_trabajo_esta_pendiente(self):
        base, proy = self.preparar(conteo=6, trabajo_despues_del_md=True)
        (proy / "CLAUDE.md").unlink()
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))

    def test_la_marca_bitacora_vieja_ya_no_influye(self):
        """Las marcas .bitacora que queden en disco son inertes."""
        base, proy = self.preparar(conteo=6, trabajo_despues_del_md=True)
        vieja = Path(str(base) + ".bitacora")
        vieja.write_text("", encoding="utf-8")
        os.utime(vieja, (time.time() + 3600, time.time() + 3600))
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))


class CausaA(Base):
    def test_escribir_el_claude_md_con_bash_si_cuenta_como_bitacora(self):
        """El defecto observado cuatro veces: un heredoc no lo reconocia.

        No basta con ejercitar _hay_pendiente en aislamiento: hay que dirigir
        el camino real (marcar() con una llamada Bash) despues de que el
        CLAUDE.md cambiara por fuera de Write/Edit, para que la prueba siga
        vigilando el defecto de verdad y no solo la funcion interna.
        """
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        for _ in range(6):
            self.marcar_con(self.pago("s1", proy, "Write",
                                      archivo=proy / "notas.md"))
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))

        # La bitacora se escribe SIN pasar por Write ni Edit (un heredoc de
        # Bash que ya corrio, por fuera de este proceso). Se fecha la marca
        # de trabajo hacia atras y el CLAUDE.md al frente, en vez de confiar
        # en que el reloj del sistema de archivos distinga dos escrituras
        # seguidas.
        self.fechar(Path(str(base) + ".trabajo"), 60)
        (proy / "CLAUDE.md").write_text("# devops\n\nentrada\n", encoding="utf-8")
        self.fechar(proy / "CLAUDE.md", 0)
        self.assertFalse(bitacora._hay_pendiente(base, proy, 6))

        # Y el camino real, no solo la funcion interna: una herramienta Bash
        # posterior (revisando o continuando trabajo) no debe rearmar la
        # alarma solo por no ser Write ni Edit.
        self.marcar_con(self.pago("s1", proy, "Bash",
                                  comando="grep -n Session CLAUDE.md"))
        self.assertFalse(bitacora._hay_pendiente(base, proy, 6))

    def test_bash_commands_si_avanzan_trabajo_y_generan_pendiente(self):
        """Bash es herramienta de primera clase. Sin Write/Edit, solo Bash genera trabajo."""
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        # NO hay Write/Edit, solo Bash. Debe generar trabajo igual.
        for _ in range(6):
            self.marcar_con(self.pago("s1", proy, "Bash",
                                      comando="python3 -c 'print(1)'"))
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))


class CausaB(Base):
    def sesion_con_bitacora_escrita(self):
        """Seis herramientas de trabajo y luego la bitacora escrita."""
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        for _ in range(6):
            self.marcar_con(self.pago("s1", proy, "Write",
                                      archivo=proy / "notas.md"))
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))
        self.fechar(Path(str(base) + ".trabajo"), 60)
        (proy / "CLAUDE.md").write_text("# devops\n\nentrada\n", encoding="utf-8")
        self.fechar(proy / "CLAUDE.md", 0)
        self.marcar_con(self.pago("s1", proy, "Edit",
                                  archivo=proy / "CLAUDE.md"))
        return base, proy

    def test_al_escribir_la_bitacora_el_conteo_se_reinicia(self):
        base, proy = self.sesion_con_bitacora_escrita()
        self.assertEqual(
            bitacora._leer_entero(Path(str(base) + ".conteo")), 0
        )

    def test_al_escribir_la_bitacora_se_reinician_los_recordatorios(self):
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        recordatorios = Path(str(base) + ".recordatorios")
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        recordatorios.write_text("2", encoding="utf-8")
        for _ in range(6):
            self.marcar_con(self.pago("s1", proy, "Write",
                                      archivo=proy / "notas.md"))
        self.fechar(Path(str(base) + ".trabajo"), 60)
        (proy / "CLAUDE.md").write_text("x", encoding="utf-8")
        self.fechar(proy / "CLAUDE.md", 0)
        self.marcar_con(self.pago("s1", proy, "Edit",
                                  archivo=proy / "CLAUDE.md"))
        self.assertEqual(bitacora._leer_entero(recordatorios), 0)

    def test_verificar_la_bitacora_despues_no_vuelve_a_pedirla(self):
        """El bucle medido el 3 ago 2026 a las 00:45."""
        base, proy = self.sesion_con_bitacora_escrita()
        # Cuatro comprobaciones de que quedo bien escrita.
        for _ in range(4):
            self.marcar_con(self.pago("s1", proy, "Bash",
                                      comando="grep -n Session CLAUDE.md"))
        self.assertFalse(bitacora._hay_pendiente(base, proy, 6))
        codigo, salida = self.verificar_con(
            {"session_id": "s1", "cwd": str(proy)}
        )
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, "")

    def test_el_trabajo_nuevo_despues_de_la_bitacora_si_vuelve_a_contar(self):
        base, proy = self.sesion_con_bitacora_escrita()
        for _ in range(8):
            self.marcar_con(self.pago("s1", proy, "Write",
                                      archivo=proy / "otro.md"))
        self.assertTrue(bitacora._hay_pendiente(base, proy, 6))

    def test_al_arrancar_la_sesion_el_primer_trabajo_si_cuenta(self):
        """Sin marca de trabajo previa no hay nada que reiniciar."""
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        self.marcar_con(self.pago("s1", proy, "Write",
                                  archivo=proy / "notas.md"))
        self.assertEqual(
            bitacora._leer_entero(Path(str(base) + ".conteo")), 1
        )

    def test_plantilla_invalida_no_sube_el_contador_de_recordatorios(self):
        """Regresion (arreglo del 5 ago 2026): el gemelo del defecto de
        marcas. recordatorios.write_text() corria ANTES de armar razon, que
        es lo que revienta con KeyError si bitacora.json trae una plantilla
        invalida. El KeyError no tumba el hook (lo atrapa _punto_de_entrada),
        pero el contador ya habia subido cuando escapaba. Dos vueltas asi
        agotan max_recordatorios y el bloqueo queda mudo el resto de la
        sesion, aunque el usuario corrija su plantilla despues."""
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        ahora = time.time()
        os.utime(proy / "CLAUDE.md", (ahora - 60, ahora - 60))
        os.utime(trabajo, (ahora, ahora))
        recordatorios = Path(str(base) + ".recordatorios")

        ruta_config = self.casa / ".claude" / "bitacora.json"
        config = json.loads(ruta_config.read_text(encoding="utf-8"))
        config["instruccion"] = "plantilla rota {no_existe}"
        ruta_config.write_text(json.dumps(config), encoding="utf-8")

        with self.assertRaises(KeyError):
            self._correr(
                bitacora.verificar, {"session_id": "s1", "cwd": str(proy)}
            )
        self.assertEqual(bitacora._leer_entero(recordatorios), 0)

        # Con la plantilla ya corregida, el bloqueo vuelve a funcionar.
        config["instruccion"] = bitacora.INSTRUCCION_POR_DEFECTO
        ruta_config.write_text(json.dumps(config), encoding="utf-8")
        codigo, salida = self._correr(
            bitacora.verificar, {"session_id": "s1", "cwd": str(proy)}
        )
        self.assertEqual(codigo, 0)
        datos = json.loads(salida)
        self.assertEqual(datos["decision"], "block")
        self.assertEqual(bitacora._leer_entero(recordatorios), 1)


class Escritor(Base):
    def test_lanzar_escritura_desprende_el_proceso_y_no_espera(self):
        proy = self.proyecto("devops")
        capturado = {}

        class ProcesoFalso:
            pid = 4321

        def popen_falso(argumentos, **kwargs):
            capturado["argumentos"] = argumentos
            capturado["kwargs"] = kwargs
            return ProcesoFalso()

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            bitacora._lanzar_escritura("s1", proy, bitacora._config())

        self.assertIn("escribir", capturado["argumentos"])
        self.assertIn("s1", capturado["argumentos"])
        self.assertIn(str(proy), capturado["argumentos"])
        # El hook no puede quedarse esperando: nada de tuberias abiertas.
        self.assertEqual(
            capturado["kwargs"]["stdout"], bitacora.subprocess.DEVNULL
        )
        if os.name == "nt":
            self.assertIn("creationflags", capturado["kwargs"])
        else:
            self.assertTrue(capturado["kwargs"]["start_new_session"])

    def test_escribir_invoca_claude_con_el_prompt_por_stdin(self):
        proy = self.proyecto("devops")
        capturado = {}

        class ProcesoFalso:
            returncode = 0

            def communicate(self, entrada=None, timeout=None):
                capturado["entrada"] = entrada
                capturado["timeout"] = timeout
                return b"", b""

        def popen_falso(argumentos, **kwargs):
            capturado["argumentos"] = argumentos
            capturado["cwd"] = kwargs.get("cwd")
            capturado["env"] = kwargs.get("env")
            return ProcesoFalso()

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        self.assertIn("--resume", capturado["argumentos"])
        self.assertIn("s1", capturado["argumentos"])
        # El prompt va por STDIN. Como argumento posicional falla con rc=0, o
        # sea en silencio, y no escribe nada.
        self.assertIn(b"bitacora", capturado["entrada"].lower())
        self.assertEqual(capturado["cwd"], str(proy))
        self.assertEqual(capturado["env"]["BITACORA_EN_CIERRE"], "1")
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre terminado", registro)

    def test_escribir_mata_el_proceso_cuando_vence_el_plazo(self):
        proy = self.proyecto("devops")
        matado = {"si": False}

        class ProcesoFalso:
            returncode = None

            def communicate(self, entrada=None, timeout=None):
                if not matado["si"]:
                    raise bitacora.subprocess.TimeoutExpired("claude", 600)
                return b"", b""

            def kill(self):
                matado["si"] = True

        with mock.patch.object(bitacora.subprocess, "Popen",
                               lambda *a, **k: ProcesoFalso()):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        self.assertTrue(matado["si"])
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre vencido", registro)

    def test_escribir_registra_el_fallo_en_vez_de_callarselo(self):
        proy = self.proyecto("devops")

        def popen_que_truena(*a, **k):
            raise FileNotFoundError("claude")

        with mock.patch.object(bitacora.subprocess, "Popen", popen_que_truena):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre fallo", registro)
        self.assertIn("FileNotFoundError", registro)

    def test_escribir_ignora_un_proyecto_fuera_de_la_raiz(self):
        fuera = self.casa / "otro"
        fuera.mkdir()
        (fuera / "CLAUDE.md").write_text("x", encoding="utf-8")
        llamado = {"si": False}

        def popen_falso(*a, **k):
            llamado["si"] = True

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            self.assertEqual(bitacora.escribir(["s1", str(fuera)]), 0)
        self.assertFalse(llamado["si"])

    def test_escribir_registra_una_plantilla_de_instruccion_invalida(self):
        """Una plantilla mala en bitacora.json no puede desaparecer en silencio.

        escribir corre dentro de un proceso desprendido con stdout/stderr en
        DEVNULL: si el .format() de la instruccion revienta antes del try que
        rodea a Popen, el error de antes se habria ido al vacio sin que nadie
        se enterara, exactamente el escenario de "fallo con rc=0 y no escribio
        nada durante semanas" que este mecanismo existe para evitar.
        """
        proy = self.proyecto("devops")
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({
                "raiz_proyectos": str(self.raiz),
                "instruccion": "escribe la bitacora en {archivio}",
            }),
            encoding="utf-8",
        )
        llamado = {"si": False}

        def popen_falso(*a, **k):
            llamado["si"] = True

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        # No debe siquiera intentar lanzar Claude Code con una instruccion mal
        # formada.
        self.assertFalse(llamado["si"])
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre fallo", registro)
        # El mensaje tiene que nombrar la causa (plantilla), no confundirse
        # con el mensaje generico de "no se pudo lanzar Claude Code".
        self.assertIn("plantilla", registro)
        self.assertIn("KeyError", registro)


class Idempotencia(Base):
    """El cierre se dispara por dos rutas casi a la vez.

    La llamada explicita del lanzador antes de matar, y el hook SessionEnd
    cuando alcanza a correr. Sin la guarda salen dos sesiones headless
    escribiendo el mismo CLAUDE.md al mismo tiempo, que es una carrera de
    escritura real.
    """

    def con_trabajo_pendiente(self):
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        self.fechar(proy / "CLAUDE.md", 60)
        self.fechar(trabajo, 0)
        return base, proy

    def test_el_segundo_disparo_seguido_no_lanza_otra_escritura(self):
        base, proy = self.con_trabajo_pendiente()
        lanzados = []
        with mock.patch.object(bitacora, "_lanzar_escritura",
                               lambda s, p, c: lanzados.append(s)):
            bitacora._cerrar_uno("s1", proy, bitacora._config())
            bitacora._cerrar_uno("s1", proy, bitacora._config())
        self.assertEqual(lanzados, ["s1"])
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre disparado", registro)
        # El registro dice que se callo, no se lo guarda: un mecanismo
        # desatendido tiene que distinguir "no habia nada que hacer" de "si
        # habia, pero ya lo cubrio alguien mas".
        self.assertIn("cierre omitido", registro)

    def test_pasada_la_ventana_si_se_vuelve_a_disparar(self):
        base, proy = self.con_trabajo_pendiente()
        lanzados = []
        with mock.patch.object(bitacora, "_lanzar_escritura",
                               lambda s, p, c: lanzados.append(s)):
            bitacora._cerrar_uno("s1", proy, bitacora._config())
            self.fechar(Path(str(base) + ".cierre-intentado"),
                        bitacora.VENTANA_CIERRE + 10)
            # La guarda de proyecto (independiente de la de sesion) tambien
            # tiene que verse vencida, o seguiria bloqueando el reintento:
            # protege el CLAUDE.md, no la sesion que dispara el cierre.
            marca_proy = bitacora._marca_proyecto_cerrando(proy, self.raiz)
            self.fechar(marca_proy, bitacora.TIEMPO_CIERRE + 10)
            bitacora._cerrar_uno("s1", proy, bitacora._config())
        self.assertEqual(lanzados, ["s1", "s1"])


class Paridad(Base):
    def sesion_huerfana(self, proy, sid="vieja"):
        base = self.base_de(sid, proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        ahora = time.time()
        os.utime(proy / "CLAUDE.md", (ahora - 60, ahora - 60))
        os.utime(trabajo, (ahora, ahora))
        return base

    def test_pendiente_emite_el_json_que_claude_code_espera(self):
        proy = self.proyecto("devops")
        self.sesion_huerfana(proy)
        codigo, salida = self.pendiente_con(
            {"session_id": "nueva", "cwd": str(proy)}
        )
        self.assertEqual(codigo, 0)
        datos = json.loads(salida)
        self.assertEqual(
            datos["hookSpecificOutput"]["hookEventName"], "SessionStart"
        )
        aviso = datos["hookSpecificOutput"]["additionalContext"]
        self.assertIn("BITACORA PENDIENTE", aviso)
        self.assertIn("vieja", aviso)
        # La instruccion completa viaja en el aviso, no solo el numero.
        self.assertIn("Session Log", aviso)

    def test_pendiente_emite_ascii_puro_aunque_la_instruccion_tenga_acentos(self):
        """Finding 1: sys.stdout en Windows es la codepage local (cp1252),
        no UTF-8, porque el stdout del hook es un pipe. ensure_ascii=True (el
        default de json.dumps, que aqui se dejaba de lado con
        ensure_ascii=False) evita tanto el mojibake como el
        UnicodeEncodeError que tumbaria el hook."""
        instruccion_con_acento = "Escribe la bitacóra en {archivo}."
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({
                "raiz_proyectos": str(self.raiz),
                "instruccion": instruccion_con_acento,
            }),
            encoding="utf-8",
        )
        proy = self.proyecto("devops")
        self.sesion_huerfana(proy)
        codigo, salida = self.pendiente_con(
            {"session_id": "nueva", "cwd": str(proy)}
        )
        self.assertEqual(codigo, 0)
        # Puro ASCII en la salida cruda: nada por encima de 0x7F.
        self.assertTrue(all(ord(c) < 128 for c in salida))
        datos = json.loads(salida)
        aviso = datos["hookSpecificOutput"]["additionalContext"]
        self.assertIn("bitacóra", aviso)

    def test_pendiente_ignora_la_sesion_en_curso(self):
        proy = self.proyecto("devops")
        self.sesion_huerfana(proy, sid="actual")
        codigo, salida = self.pendiente_con(
            {"session_id": "actual", "cwd": str(proy)}
        )
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, "")

    def test_pendiente_calla_durante_el_cierre(self):
        """Guarda anti recursion. La version de Windows no la tenia."""
        proy = self.proyecto("devops")
        self.sesion_huerfana(proy)
        with mock.patch.dict(os.environ, {"BITACORA_EN_CIERRE": "1"}):
            codigo, salida = self.pendiente_con(
                {"session_id": "nueva", "cwd": str(proy)}
            )
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, "")

    def test_verificar_calla_durante_el_cierre(self):
        proy = self.proyecto("devops")
        self.sesion_huerfana(proy, sid="s1")
        with mock.patch.dict(os.environ, {"BITACORA_EN_CIERRE": "1"}):
            codigo, salida = self.verificar_con(
                {"session_id": "s1", "cwd": str(proy)}
            )
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, "")

    def test_la_limpieza_de_marcas_respeta_el_registro_de_cierres(self):
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        registro = bitacora._ruta_log()
        registro.write_text("historia\n", encoding="utf-8")
        viejo = time.time() - 10 * 86400
        os.utime(registro, (viejo, viejo))
        basura = bitacora._dir_marcas() / "s9__x.conteo"
        basura.write_text("1", encoding="utf-8")
        os.utime(basura, (viejo, viejo))

        bitacora._limpiar_marcas_viejas()

        self.assertTrue(registro.exists())
        self.assertFalse(basura.exists())

    def test_los_comandos_de_git_no_cuentan_como_trabajo(self):
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        for comando in ("git commit -m x", "gh pr create",
                        "cd /tmp && git push"):
            self.marcar_con(self.pago("s1", proy, "Bash", comando=comando))
        self.assertEqual(
            bitacora._leer_entero(Path(str(base) + ".conteo")), 0
        )


class LanzamientoQueFalla(Base):
    """Finding 3: un Popen que revienta al lanzar el escritor no puede dejar
    "cierre disparado" como ultima linea del log, ni bloquear el reintento."""

    def con_trabajo_pendiente(self):
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        self.fechar(proy / "CLAUDE.md", 60)
        self.fechar(trabajo, 0)
        return base, proy

    def test_el_fallo_de_lanzamiento_se_registra_y_no_dice_disparado(self):
        base, proy = self.con_trabajo_pendiente()
        with mock.patch.object(
            bitacora, "_lanzar_escritura",
            mock.Mock(side_effect=OSError("no se pudo lanzar el proceso")),
        ):
            bitacora._cerrar_uno("s1", proy, bitacora._config())

        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre no lanzado", registro)
        self.assertNotIn("cierre disparado", registro)

    def test_el_fallo_de_lanzamiento_no_bloquea_el_reintento(self):
        """.cierre-intentado solo se toca DESPUES de que el lanzamiento tuvo
        exito, asi que un fallo puede reintentarse de inmediato."""
        base, proy = self.con_trabajo_pendiente()
        lanzados = []
        primero = mock.Mock(side_effect=OSError("truena"))
        segundo = lambda s, p, c: lanzados.append(s)

        with mock.patch.object(bitacora, "_lanzar_escritura", primero):
            bitacora._cerrar_uno("s1", proy, bitacora._config())
        self.assertFalse(
            Path(str(base) + ".cierre-intentado").exists()
        )

        with mock.patch.object(bitacora, "_lanzar_escritura", segundo):
            bitacora._cerrar_uno("s1", proy, bitacora._config())
        self.assertEqual(lanzados, ["s1"])

    def test_el_fallo_de_lanzamiento_libera_la_marca_de_proyecto(self):
        """Sin liberar la marca de inmediato, el proyecto entero quedaria
        bloqueado hasta TIEMPO_CIERRE aunque nunca hubo escritor corriendo."""
        base, proy = self.con_trabajo_pendiente()
        with mock.patch.object(
            bitacora, "_lanzar_escritura",
            mock.Mock(side_effect=OSError("truena")),
        ):
            bitacora._cerrar_uno("s1", proy, bitacora._config())

        marca_proy = bitacora._marca_proyecto_cerrando(proy, self.raiz)
        self.assertFalse(marca_proy.exists())


class GuardaDeProyecto(Base):
    """Finding 4: la idempotencia por sesion no alcanza cuando el recurso
    compartido es el CLAUDE.md de un proyecto y "cerrar --proyecto" itera
    varias sesiones pendientes a la vez."""

    def dos_sesiones_pendientes(self, proy):
        for sid in ("s1", "s2"):
            base = self.base_de(sid, proy)
            bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
            Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
            trabajo = Path(str(base) + ".trabajo")
            trabajo.write_text("", encoding="utf-8")
            self.fechar(proy / "CLAUDE.md", 60)
            self.fechar(trabajo, 0)

    def test_una_sesion_corriendo_bloquea_a_otra_del_mismo_proyecto(self):
        proy = self.proyecto("devops")
        self.dos_sesiones_pendientes(proy)
        lanzados = []
        with mock.patch.object(bitacora, "_lanzar_escritura",
                               lambda s, p, c: lanzados.append(s)):
            bitacora._cerrar_uno("s1", proy, bitacora._config())
            bitacora._cerrar_uno("s2", proy, bitacora._config())

        # Solo la primera sesion lanzo un escritor: la marca de proyecto
        # (no la de sesion, que es por sid y no las distingue) bloqueo a s2.
        self.assertEqual(lanzados, ["s1"])
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre no lanzado", registro)

    def test_al_terminar_escribir_libera_la_marca_para_la_otra_sesion(self):
        """escribir() quita la marca de proyecto en su finally, sin importar
        por donde salga, para que la siguiente sesion pendiente no quede
        bloqueada esperando a un escritor que ya termino."""
        proy = self.proyecto("devops")
        base = self.base_de("s1", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        self.fechar(proy / "CLAUDE.md", 60)
        self.fechar(trabajo, 0)

        marca_proy = bitacora._marca_proyecto_cerrando(proy, self.raiz)
        bitacora._tocar(marca_proy)
        self.assertTrue(marca_proy.exists())

        class ProcesoFalso:
            returncode = 0

            def communicate(self, entrada=None, timeout=None):
                return b"", b""

        with mock.patch.object(bitacora.subprocess, "Popen",
                               lambda *a, **k: ProcesoFalso()):
            bitacora.escribir(["s1", str(proy)])

        self.assertFalse(marca_proy.exists())

    def test_la_marca_de_proyecto_vencida_se_ignora_y_se_registra(self):
        proy = self.proyecto("devops")
        self.dos_sesiones_pendientes(proy)
        marca_proy = bitacora._marca_proyecto_cerrando(proy, self.raiz)
        bitacora._tocar(marca_proy)
        self.fechar(marca_proy, bitacora.TIEMPO_CIERRE + 10)

        lanzados = []
        with mock.patch.object(bitacora, "_lanzar_escritura",
                               lambda s, p, c: lanzados.append(s)):
            bitacora._cerrar_uno("s1", proy, bitacora._config())

        self.assertEqual(lanzados, ["s1"])
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("vencida", registro)

    def test_el_nombre_de_la_marca_no_choca_con_el_glob_de_trabajo(self):
        """cerrar --proyecto y pendiente() listan sesiones con
        *__{slug}.trabajo. La marca de proyecto no debe aparecer ahi."""
        proy = self.proyecto("devops")
        marca_proy = bitacora._marca_proyecto_cerrando(proy, self.raiz)
        bitacora._tocar(marca_proy)
        slug = bitacora._slug(proy, self.raiz)
        coincidencias = list(
            bitacora._dir_marcas().glob(f"*__{slug}.trabajo")
        )
        self.assertEqual(coincidencias, [])


class Transcripcion(Base):
    """Finding 9: cierres.log es el unico canal de diagnostico y
    INSTALACION.md manda ahi al cliente. La transcripcion completa del
    modelo va aparte, para no enterrar las lineas de estado."""

    def test_la_transcripcion_del_escritor_no_va_a_cierres_log(self):
        proy = self.proyecto("devops")
        capturado = {}

        class ProcesoFalso:
            returncode = 0

            def communicate(self, entrada=None, timeout=None):
                return b"", b""

        def popen_falso(argumentos, **kwargs):
            capturado["stdout"] = kwargs.get("stdout")
            return ProcesoFalso()

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        transcripcion = bitacora._ruta_transcripcion("s1")
        self.assertTrue(transcripcion.exists())
        # El Popen escribio a la transcripcion, no a cierres.log.
        self.assertNotEqual(capturado["stdout"].name, str(bitacora._ruta_log()))

        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("cierre terminado", registro)
        # La linea de estado dice donde quedo la transcripcion, para que se
        # pueda encontrar.
        self.assertIn(str(transcripcion), registro)


class DespachoYManejoDeErrores(Base):
    """Finding 10: main() no tenia cobertura, solo se verificaba con
    corridas reales."""

    def test_main_despacha_los_cinco_subcomandos(self):
        proy = self.proyecto("devops")
        casos = {
            "marcar": ("marcar", None),
            "verificar": ("verificar", None),
            "cerrar": ("cerrar", []),
            "pendiente": ("pendiente", None),
            "escribir": ("escribir", []),
        }
        for orden, (nombre_funcion, argumento) in casos.items():
            with mock.patch.object(
                bitacora, nombre_funcion, mock.Mock(return_value=0)
            ) as funcion_falsa:
                with mock.patch.object(sys, "argv", ["bitacora.py", orden]):
                    codigo = bitacora.main()
                self.assertEqual(codigo, 0)
                funcion_falsa.assert_called_once()

    def test_main_sin_argumentos_imprime_el_doc_y_regresa_1(self):
        with mock.patch.object(sys, "argv", ["bitacora.py"]):
            entrada = io.StringIO()
            salida = io.StringIO()
            with mock.patch.object(sys, "stdin", entrada), \
                 mock.patch.object(sys, "stdout", salida):
                codigo = bitacora.main()
        self.assertEqual(codigo, 1)

    def test_orden_no_reconocida_regresa_1(self):
        with mock.patch.object(sys, "argv", ["bitacora.py", "algomas"]):
            codigo = bitacora.main()
        self.assertEqual(codigo, 1)

    def test_una_excepcion_no_atrapada_se_registra_y_no_revienta(self):
        """Finding 2: _tocar y conteo.write_text (entre otras escrituras) no
        estan blindadas. Un OSError real (disco lleno, permisos, antivirus)
        no puede escapar del proceso sin dejar rastro."""
        with mock.patch.object(
            bitacora, "main", mock.Mock(side_effect=OSError("disco lleno"))
        ):
            codigo = bitacora._punto_de_entrada()
        self.assertEqual(codigo, 0)
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("fallo no atrapado", registro)
        self.assertIn("disco lleno", registro)

    def test_si_ni_el_registro_funciona_sigue_sin_reventar(self):
        """_apuntar puede fallar por la misma causa que main(): va en su
        propio try/except para que un log roto no tumbe el envoltorio."""
        with mock.patch.object(
            bitacora, "main", mock.Mock(side_effect=RuntimeError("x"))
        ), mock.patch.object(
            bitacora, "_apuntar", mock.Mock(side_effect=OSError("sin permiso"))
        ):
            codigo = bitacora._punto_de_entrada()
        self.assertEqual(codigo, 0)

    def test_marcar_falla_por_io_se_registra_en_vez_de_perderse(self):
        """El disparador concreto del finding: _tocar sin blindar revienta
        en marcar() en cuanto ~/.cache no se puede escribir."""
        proy = self.proyecto("devops")
        payload = self.pago("s1", proy, "Write", archivo=proy / "notas.md")
        entrada = io.StringIO(json.dumps(payload))
        with mock.patch.object(sys, "stdin", entrada), \
             mock.patch.object(sys, "argv", ["bitacora.py", "marcar"]), \
             mock.patch.object(
                 bitacora, "_tocar",
                 mock.Mock(side_effect=OSError("cache de solo lectura")),
             ):
            codigo = bitacora._punto_de_entrada()
        self.assertEqual(codigo, 0)
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        self.assertIn("fallo no atrapado", registro)


class DetachDeWindows(Base):
    """Finding 10: la rama de Windows de _lanzar_escritura no tenia
    cobertura en Linux. subprocess.DETACHED_PROCESS y
    CREATE_NEW_PROCESS_GROUP no existen fuera de Windows, asi que la
    implementacion usa getattr(..., 0) para poder probarla aqui.

    Las banderas viven en _extras_de_lanzamiento(), separada a proposito de
    la resolucion de rutas: mockear os.name en bloque revienta cualquier
    Path() que dependa de el (Path.home(), .resolve()...), asi que probar la
    rama de Windows exige no tocar pathlib mientras el parche esta activo.
    """

    def test_creationflags_se_pasa_en_windows(self):
        with mock.patch.object(bitacora.os, "name", "nt"):
            extras = bitacora._extras_de_lanzamiento()
        self.assertIn("creationflags", extras)
        self.assertNotIn("start_new_session", extras)

    def test_start_new_session_en_no_windows(self):
        with mock.patch.object(bitacora.os, "name", "posix"):
            extras = bitacora._extras_de_lanzamiento()
        self.assertTrue(extras["start_new_session"])
        self.assertNotIn("creationflags", extras)


class FormatoDeMarcaDeTiempo(Base):
    def test_apuntar_usa_directivas_explicitas_no_C99(self):
        bitacora._apuntar("linea de prueba")
        registro = bitacora._ruta_log().read_text(encoding="utf-8")
        primera_linea = registro.splitlines()[0]
        marca = primera_linea.split("  ", 1)[0]
        # "%Y-%m-%d %H:%M:%S": 19 caracteres, parseable sin directivas C99.
        import datetime
        datetime.datetime.strptime(marca, "%Y-%m-%d %H:%M:%S")


class InstruccionConPendientes(Base):
    def test_la_instruccion_de_fabrica_nombra_los_dos_archivos(self):
        cfg = bitacora._config()
        texto = cfg["instruccion"].format(
            archivo="/x/CLAUDE.md", pendientes="/x/pendientes.md"
        )
        self.assertIn("/x/CLAUDE.md", texto)
        self.assertIn("/x/pendientes.md", texto)

    def test_una_instruccion_propia_sin_pendientes_sigue_sirviendo(self):
        """Retrocompatibilidad. El bitacora.json de un cliente escrito antes de
        este cambio no usa {pendientes} y no tiene por que romperse: format
        ignora los kwargs que la plantilla no ocupa."""
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({
                "raiz_proyectos": str(self.raiz),
                "instruccion": "Escribe la bitacora en {archivo}.",
            }),
            encoding="utf-8",
        )
        cfg = bitacora._config()
        texto = cfg["instruccion"].format(
            archivo="/x/CLAUDE.md", pendientes="/x/pendientes.md"
        )
        self.assertEqual(texto, "Escribe la bitacora en /x/CLAUDE.md.")

    def test_el_cierre_le_manda_al_asistente_la_ruta_de_pendientes(self):
        """El punto 5 tiene que llegar por stdin al proceso que escribe."""
        proy = self.proyecto("devops")
        capturado = {}

        class ProcesoFalso:
            returncode = 0

            def communicate(self, entrada=None, timeout=None):
                capturado["entrada"] = entrada
                return b"", b""

        def popen_falso(argumentos, **kwargs):
            return ProcesoFalso()

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        prompt = capturado["entrada"].decode("utf-8")
        self.assertIn(str(proy / "pendientes.md"), prompt)

    def test_el_aviso_de_arranque_tambien_nombra_pendientes(self):
        proy = self.proyecto("devops")
        base = self.base_de("vieja", proy)
        bitacora._dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("9", encoding="utf-8")
        trabajo = Path(str(base) + ".trabajo")
        trabajo.write_text("", encoding="utf-8")
        ahora = time.time()
        os.utime(proy / "CLAUDE.md", (ahora - 60, ahora - 60))
        os.utime(trabajo, (ahora, ahora))

        codigo, salida = self._correr(
            bitacora.pendiente, {"session_id": "nueva", "cwd": str(proy)}
        )
        self.assertEqual(codigo, 0)
        contexto = json.loads(salida)["hookSpecificOutput"]["additionalContext"]
        self.assertIn(str(proy / "pendientes.md"), contexto)
        salida.encode("ascii")   # stdout del hook es cp1252 en Windows


class HerramientasDelEscritor(Base):
    """El punto 6 de la instruccion pide tocar el calendario, y la sesion
    escritora corre con una lista cerrada de herramientas. Si las dos se
    desacoplan, la instruccion queda muda: pide algo que la sesion no puede
    hacer, y como el propio punto 6 dice "si no hubo nada que tocar no lo
    menciones", nadie se entera nunca.

    Por eso estas pruebas miran el argumento que de verdad LLEGA a Popen por
    el camino real de escribir(), y no la constante suelta.
    """

    def _allowed_tools_de_una_corrida_real(self):
        proy = self.proyecto("devops")
        capturado = {}

        class ProcesoFalso:
            returncode = 0

            def communicate(self, entrada=None, timeout=None):
                return b"", b""

        def popen_falso(argumentos, **kwargs):
            capturado["argumentos"] = argumentos
            return ProcesoFalso()

        with mock.patch.object(bitacora.subprocess, "Popen", popen_falso):
            self.assertEqual(bitacora.escribir(["s1", str(proy)]), 0)

        argumentos = capturado["argumentos"]
        return argumentos[argumentos.index("--allowedTools") + 1].split(",")

    def test_el_escritor_recibe_las_herramientas_de_calendario(self):
        permitidas = self._allowed_tools_de_una_corrida_real()
        for herramienta in ("update_event", "create_event", "get_event",
                            "search_events", "list_events"):
            self.assertIn(
                "mcp__claude_ai_Google_Calendar__" + herramienta, permitidas,
                "sin esta herramienta el punto 6 de la instruccion no puede "
                "hacer nada, y falla en silencio",
            )

    def test_el_escritor_conserva_las_herramientas_de_archivo(self):
        """Lo de calendario se agrego a la lista, no la reemplazo: sin estas
        no se escribe ni el CLAUDE.md ni el pendientes.md, que es el 100% del
        valor del mecanismo."""
        permitidas = self._allowed_tools_de_una_corrida_real()
        for herramienta in ("Read", "Write", "Edit", "Bash", "Glob", "Grep"):
            self.assertIn(herramienta, permitidas)

    def test_el_escritor_no_puede_borrar_un_evento(self):
        """La prohibicion de borrar no descansa en que el modelo obedezca la
        prosa: la herramienta no esta, asi que borrar es imposible. Lo mismo
        con contestar invitaciones, que le hablaria a terceros."""
        permitidas = self._allowed_tools_de_una_corrida_real()
        self.assertNotIn(
            "mcp__claude_ai_Google_Calendar__delete_event", permitidas)
        self.assertNotIn(
            "mcp__claude_ai_Google_Calendar__respond_to_event", permitidas)

    def test_la_instruccion_exige_no_notificar(self):
        """Este si depende de la prosa, porque notificationLevel es un
        parametro de update_event y no una herramienta aparte. De fabrica es
        ALL, o sea que actualizar un bloque con invitados les manda correo."""
        cfg = bitacora._config()
        texto = cfg["instruccion"].format(archivo="/x/CLAUDE.md",
                                          pendientes="/x/pendientes.md")
        self.assertIn("notificationLevel NONE", texto)

    def test_la_instruccion_sabe_encontrar_el_bloque_sin_cita(self):
        """El enganche entre los dos archivos es una cita que casi nadie
        escribe, asi que sin salida de emergencia el punto 6 no dispara nunca.
        La salida es buscar, pero acotada: una sola coincidencia clara."""
        cfg = bitacora._config()
        texto = cfg["instruccion"].format(archivo="/x/CLAUDE.md",
                                          pendientes="/x/pendientes.md")
        self.assertIn("search_events", texto)
        self.assertIn("UNA COINCIDENCIA CLARA", texto)

    def test_la_instruccion_deja_la_cita_escrita(self):
        """Lo que hace que la convencion se sostenga sola: identificado el
        bloque una vez, queda anotado y la proxima no adivina."""
        cfg = bitacora._config()
        texto = cfg["instruccion"].format(archivo="/x/CLAUDE.md",
                                          pendientes="/x/pendientes.md")
        self.assertIn("DEJA LA CITA ESCRITA", texto)

    def test_una_lista_propia_reemplaza_la_de_fabrica(self):
        """Para el cliente que esta en Microsoft 365, cuyas herramientas se
        llaman distinto y no vienen en la lista de fabrica."""
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({
                "raiz_proyectos": str(self.raiz),
                "herramientas": ["Read", "Write", "otra_cosa"],
            }),
            encoding="utf-8",
        )
        self.assertEqual(bitacora._config()["herramientas"],
                         ["Read", "Write", "otra_cosa"])

    def test_una_lista_invalida_no_deja_al_escritor_sin_herramientas(self):
        """Una clave mal escrita no puede dejar mudo al mecanismo: se avisa y
        se usa la de fabrica, en vez de mandar una lista rota a Popen."""
        (self.casa / ".claude" / "bitacora.json").write_text(
            json.dumps({
                "raiz_proyectos": str(self.raiz),
                "herramientas": "Read,Write",
            }),
            encoding="utf-8",
        )
        self.assertEqual(bitacora._config()["herramientas"],
                         bitacora.HERRAMIENTAS_CIERRE)


if __name__ == "__main__":
    unittest.main()
