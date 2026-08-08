#!/usr/bin/env python3
"""Bitacora automatica del CLAUDE.md. Un solo archivo, Linux y Windows.

Resuelve los cuatro puntos que bloqueaban impartir esto a un cliente:

1. **La ruta raiz ya no esta clavada.** Se configura, y si no hay configuracion
   se deduce. Importa porque el modo de fallar de este mecanismo es salir en
   silencio: con la raiz equivocada nunca dispara y nadie se entera.
2. **Corre igual en Windows**, que era el bloqueo del stack de Sergio.
3. **Sin `jq`.** Era una instalacion extra que en una laptop corporativa pasa por
   un departamento de Sistemas ajeno.
4. **El texto de la instruccion es configurable**, porque el original esta
   redactado en el vocabulario de Gustavo (Session Log, pipeline) y un ejecutivo
   necesita el suyo.

Subcomandos, uno por hook:

    bitacora.py marcar        PostToolUse   lleva la cuenta de trabajo sin registrar
    bitacora.py verificar     Stop          pide la bitacora antes de terminar
    bitacora.py cerrar        SessionEnd    la escribe al cerrar la sesion
    bitacora.py pendiente     SessionStart  recoge lo que quedo sin registrar
    bitacora.py cerrar --proyecto <ruta>    para el lanzador, que no sabe el id
    bitacora.py escribir <sid> <ruta>       interno: la sesion que escribe

Configuracion opcional en ~/.claude/bitacora.json:

    {"raiz_proyectos": "C:/Users/gusta/claude", "umbral": 6,
     "max_recordatorios": 2, "instruccion": "...", "herramientas": [...]}
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import shutil

# Se calculan en cada llamada, no al importar. Un valor congelado al importar
# haria imposible que las pruebas redirijan el estado, y ademas amarraria el
# script al HOME que tuviera el proceso en ese instante.
def _ruta_config():
    return Path.home() / ".claude" / "bitacora.json"


def _dir_marcas():
    return Path.home() / ".cache" / "claude-bitacora"


def _ruta_log():
    return _dir_marcas() / "cierres.log"

VENTANA_CIERRE = 120      # segundos en que un segundo disparo se toma por duplicado
RETENCION_DIAS = 3
TIEMPO_CIERRE = 600

# Lo que la sesion escritora puede tocar. Es una lista cerrada: lo que no
# aparece aqui queda bloqueado, porque en modo -p nadie puede conceder un
# permiso que se pida a media corrida.
#
# Las de calendario estan por el punto 6 de la instruccion. Se escogieron una
# por una: delete_event y respond_to_event NO estan a proposito, para que
# borrar un evento y contestar una invitacion sean imposibles y no solo esten
# prohibidos en la prosa. Lo que si depende de la prosa es no mover invitados
# y notificar con NONE, porque ambos son parametros de update_event y no
# herramientas aparte.
#
# Ojo si el cliente esta en Microsoft 365: sus herramientas se llaman distinto
# y no estan aqui, asi que el punto 6 se queda mudo. Se extiende con la clave
# "herramientas" de ~/.claude/bitacora.json.
HERRAMIENTAS_CIERRE = [
    "Read", "Write", "Edit", "Bash", "Glob", "Grep",
    "mcp__claude_ai_Google_Calendar__list_calendars",
    "mcp__claude_ai_Google_Calendar__list_events",
    "mcp__claude_ai_Google_Calendar__search_events",
    "mcp__claude_ai_Google_Calendar__get_event",
    "mcp__claude_ai_Google_Calendar__update_event",
    "mcp__claude_ai_Google_Calendar__create_event",
]

INSTRUCCION_POR_DEFECTO ="""Escribe la bitacora de la sesion en {archivo}, sin que el usuario tenga que pedirlo:

1. Agrega la entrada del dia al Session Log de ese archivo, o actualiza la de hoy si ya existe.
2. Respeta el formato, la estructura y el estilo que el archivo ya usa. No inventes secciones nuevas ni reescribas lo viejo.
3. Registra lo que se decidio, lo que se entrego y lo que quedo pendiente, con quien depende cada pendiente.
4. Si algo de esta sesion cambia el pipeline, el estado del proyecto o los proximos pasos, actualiza tambien esa parte.
5. Atiende tambien {pendientes}, la lista de pendientes del proyecto:
   - Si ese archivo YA EXISTE: palomea las tareas que esta sesion hizo y verifico, y tambien las del usuario de las que en la sesion quedo constancia de que ya se hicieron (te lo dijo con todas sus letras, o lo comprobaste por tu cuenta). ANTE LA DUDA NO PALOMEES: anota en la nota de la tarea lo que se supo y dejasela a el. Al palomear agrega " ✓ AAAA-MM-DD HH:MM" con hora local al final del texto de la tarea, y si fue por constancia di en la nota de donde salio. Agrega las tareas nuevas que salieron de esta sesion, en la seccion que corresponda segun quien deba mover, con sus indicadores. NO descartes, NO reordenes, y NUNCA borres un renglon [x] ni [-]: son un registro que el usuario creo con el dedo. Conserva el fin de linea y la marca de orden de bytes que el archivo ya traiga.
   - Si NO EXISTE: crealo solo si de esta sesion salio trabajo abierto de verdad, con el formato de la convencion. Si el proyecto quedo quieto, no crees nada y no lo menciones.
6. Atiende tambien el calendario, porque es la otra mitad de la convencion: el calendario dice CUANDO y pendientes.md dice SI YA SE HIZO. Toca unicamente los bloques que esta sesion movio de verdad. Cual es suele estar citado en CLAUDE.md o en la nota del pendiente.
   - COMO ENCUENTRAS EL BLOQUE, en este orden: primero la cita en la nota del pendiente o en CLAUDE.md; si no hay cita, buscalo con search_events por el nombre del pendiente o del proyecto. ACTUA SOLO SI HAY UNA COINCIDENCIA CLARA. Con dos plausibles o con ninguna, no toques nada y dilo en una linea: equivocarse de bloque es peor que no hacer nada.
   - DEJA LA CITA ESCRITA en la nota del pendiente, con la fecha del bloque, cada vez que identifiques o agendes uno. Es lo que hace que la proxima sesion no tenga que adivinar, y lo que sostiene solo el enganche entre los dos archivos.
   - ACTUALIZA el bloque que ya existe cuando la sesion produjo material que se va a usar en el, cuando cambio de que trata, o cuando cambiaron sus supuestos. Pon al dia la descripcion AGREGANDO, sin reescribir ni borrar lo que ya decia, y cita ahi la ruta de lo que se genero en vez de adjuntarlo. Verifica leyendo el evento de vuelta: la respuesta de la escritura no es prueba de que quedo.
   - SIEMPRE con notificationLevel NONE, en toda escritura. De fabrica es ALL, o sea que actualizar un bloque que ya tiene invitados les manda correo a todos, sin que nadie lo haya pedido y desde una sesion que corre sola.
   - AGENDA un bloque nuevo solo si el usuario lo pidio en la sesion, o si un pendiente nuevo trae fecha ya comprometida con alguien mas. Un pendiente sin fecha vive en pendientes.md y no en el calendario.
   - NO AGREGUES NI QUITES INVITADOS. Mover asistentes manda correo y eso sale de la maquina. Se propone en una linea y lo decide el usuario.
   - NO BORRES eventos por iniciativa propia, aunque su pendiente ya se haya cerrado. Dilo en una linea al final y que el decida. La herramienta de borrar tampoco esta disponible aqui, a proposito.
   - Si no tienes herramientas de calendario, o no hubo nada que tocar, no lo menciones.

Si de verdad no hubo nada que valga la pena registrar, dilo en una linea y termina sin escribir nada."""


# --------------------------------------------------------------------------
# Configuracion

def _ejecutable_claude():
    """Donde vive Claude Code.

    Los hooks NO heredan el PATH interactivo, ni en Linux ni en Windows: un hook
    que solo invoque "claude" falla con FileNotFoundError y, si nadie registra el
    error, el mecanismo entero queda inservible sin que se note. Es la misma
    familia del gotcha del PATH en las unidades de systemd.
    """
    hallado = shutil.which("claude")
    if hallado:
        return hallado
    candidatos = []
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidatos.append(Path(appdata) / "npm" / "claude.cmd")
        candidatos.append(Path.home() / "AppData" / "Roaming" / "npm" / "claude.cmd")
        candidatos.append(Path.home() / ".local" / "bin" / "claude.exe")
    else:
        candidatos.append(Path.home() / ".local" / "bin" / "claude")
        candidatos.append(Path("/usr/local/bin/claude"))
    for ruta in candidatos:
        if ruta.exists():
            return str(ruta)
    return "claude"      # ultimo recurso: que falle con un error visible


UMBRAL_POR_DEFECTO = 6
MAX_RECORDATORIOS_POR_DEFECTO = 2


def _avisar_una_vez(clave, mensaje):
    """Registra un problema de configuracion sin inundar cierres.log.

    Un typo en bitacora.json es persistente: sin este freno, cada invocacion
    de cada hook (potencialmente cientos al dia) escribiria la misma linea.
    El marcador vive junto a las demas marcas y lo barre la limpieza de tres
    dias, asi que el aviso puede volver a salir si el problema sigue vivo
    mucho tiempo despues, en vez de desaparecer para siempre tras la primera
    vez.
    """
    try:
        marcador = _dir_marcas() / f"aviso-{clave}"
        if marcador.exists():
            return
        _tocar(marcador)
    except OSError:
        pass
    _apuntar(mensaje)


def _entero_config(datos, clave, defecto):
    """int() tolerante: un valor invalido no puede tumbar todos los hooks.

    int("seis") revienta con ValueError. Sin este freno eso escapa de _config
    y mata marcar/verificar/cerrar/pendiente en cada llamada, para siempre,
    hasta que alguien note que el mecanismo dejo de escribir nada.
    """
    valor = datos.get(clave, defecto)
    try:
        return int(valor)
    except (TypeError, ValueError):
        _avisar_una_vez(
            f"config-{clave}",
            f"config invalida  {clave}={valor!r} no es un numero, se usa "
            f"el valor por defecto {defecto}",
        )
        return defecto


def _config():
    datos = {}
    try:
        with open(_ruta_config(), encoding="utf-8") as fh:
            cargado = json.load(fh)
        if isinstance(cargado, dict):
            datos = cargado
    except (OSError, json.JSONDecodeError):
        pass

    raiz = datos.get("raiz_proyectos")
    if not raiz:
        # Sin configuracion, la convencion del lanzador: <perfil>/claude.
        raiz = str(Path.home() / "claude")
    raiz_path = Path(raiz)
    if not raiz_path.exists():
        # El modo de fallar de este mecanismo es el silencio: con la raiz
        # mal apuntada, _proyecto_valido nunca es cierto para nadie y el
        # hook nunca dispara para ningun proyecto, sin ningun error visible.
        _avisar_una_vez(
            "raiz-proyectos",
            f"config invalida  raiz_proyectos={raiz!r} no existe en este "
            "equipo, el mecanismo no va a disparar para ningun proyecto "
            "hasta que se corrija",
        )
    return {
        "raiz": raiz_path,
        "claude_bin": datos.get("claude_bin") or _ejecutable_claude(),
        "umbral": _entero_config(datos, "umbral", UMBRAL_POR_DEFECTO),
        "max_recordatorios": _entero_config(
            datos, "max_recordatorios", MAX_RECORDATORIOS_POR_DEFECTO
        ),
        "instruccion": datos.get("instruccion") or INSTRUCCION_POR_DEFECTO,
        "herramientas": _lista_config(datos, "herramientas", HERRAMIENTAS_CIERRE),
    }


def _lista_config(datos, clave, defecto):
    """Una lista de la configuracion, o la de fabrica si no sirve.

    Se valida en vez de confiar: una clave mal escrita (una cadena suelta,
    una lista con numeros) dejaria la sesion escritora sin sus herramientas
    de siempre, y este mecanismo no puede fallar en silencio.
    """
    valor = datos.get(clave)
    if isinstance(valor, list) and valor and all(
        isinstance(x, str) and x.strip() for x in valor
    ):
        return [x.strip() for x in valor]
    if valor is not None:
        _avisar_una_vez(
            f"config-{clave}",
            f"config invalida  {clave}={valor!r} no es una lista de textos, "
            "se usa la de fabrica",
        )
    return list(defecto)


# --------------------------------------------------------------------------
# Marcas

def _resolver(ruta):
    try:
        return Path(ruta).resolve()
    except (OSError, RuntimeError):
        return None


def _proyecto_valido(proy, raiz):
    """Del ecosistema configurado y con CLAUDE.md propio que mantener."""
    if proy is None:
        return False
    try:
        proy.relative_to(raiz.resolve())
    except (ValueError, OSError):
        return False
    return (proy / "CLAUDE.md").is_file()


def _slug(proy, raiz):
    relativa = proy.relative_to(raiz.resolve())
    return "-".join(relativa.parts)


def _base(sid, proy, raiz):
    return _dir_marcas() / f"{sid}__{_slug(proy, raiz)}"


def _leer_entero(ruta):
    try:
        return int(ruta.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 0


def _tocar(ruta):
    _dir_marcas().mkdir(parents=True, exist_ok=True)
    ruta.write_text("", encoding="utf-8")


def _mtime(ruta):
    try:
        return ruta.stat().st_mtime
    except OSError:
        return None


def _hay_pendiente(base, proy, umbral):
    """Hubo trabajo real que todavia no se registro.

    Se compara contra el mtime real del CLAUDE.md, no contra una marca que
    escriba el hook. Antes se marcaba solo cuando la escritura pasaba por Write
    o Edit, asi que escribir la bitacora con un heredoc o con sed la contaba
    como trabajo, o sea al reves. Observado cuatro veces entre julio y agosto
    de 2026.
    """
    if _leer_entero(Path(str(base) + ".conteo")) < umbral:
        return False
    trabajo = _mtime(Path(str(base) + ".trabajo"))
    if trabajo is None:
        return False
    escrito = _mtime(proy / "CLAUDE.md")
    return escrito is None or trabajo > escrito


def _payload():
    try:
        crudo = sys.stdin.read()
    except Exception:
        return {}
    try:
        datos = json.loads(crudo)
    except (json.JSONDecodeError, TypeError):
        return {}
    return datos if isinstance(datos, dict) else {}


def _contexto(datos, cfg):
    """(session_id, ruta del proyecto) o (None, None) si no aplica."""
    sid = datos.get("session_id")
    bruto = datos.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    proy = _resolver(bruto)
    if not sid or not _proyecto_valido(proy, cfg["raiz"]):
        return None, None
    return sid, proy


# --------------------------------------------------------------------------
# Subcomandos

def marcar():
    cfg = _config()
    datos = _payload()
    sid, proy = _contexto(datos, cfg)
    if not sid:
        return 0

    base = _base(sid, proy, cfg["raiz"])

    # Causa B del defecto de marcas. Si el CLAUDE.md quedo mas nuevo que el
    # ultimo trabajo, la bitacora ya se escribio y esta herramienta es parte de
    # la verificacion que sigue. Contarla rearma la alarma que se acaba de
    # apagar, y reescribir la bitacora para callarla la vuelve a disparar: es
    # un bucle, no un aviso suelto. Medido el 3 ago 2026 a las 00:45.
    #
    # Se toca .trabajo ademas de poner el conteo en cero. Sin eso, el CLAUDE.md
    # quedaria mas nuevo para siempre y el trabajo real posterior no volveria a
    # contarse nunca.
    trabajo = Path(str(base) + ".trabajo")
    marca_trabajo = _mtime(trabajo)
    escrito = _mtime(proy / "CLAUDE.md")
    if marca_trabajo is not None and escrito is not None and escrito > marca_trabajo:
        _dir_marcas().mkdir(parents=True, exist_ok=True)
        Path(str(base) + ".conteo").write_text("0", encoding="utf-8")
        recordatorios = Path(str(base) + ".recordatorios")
        if recordatorios.exists():
            recordatorios.write_text("0", encoding="utf-8")
        _tocar(trabajo)
        return 0

    entrada = datos.get("tool_input") or {}

    # Registrar el trabajo no es trabajo: sin esto, el commit que va despues de
    # escribir la bitacora la volveria a marcar como desactualizada.
    if datos.get("tool_name") == "Bash":
        cmd = (entrada.get("command") or "").strip()
        if cmd.startswith("cd "):
            cmd = cmd[3:]
        if " && " in cmd:
            cmd = cmd.split(" && ", 1)[1]
        if cmd.startswith(("git ", "gh ")):
            return 0

    conteo = Path(str(base) + ".conteo")
    _dir_marcas().mkdir(parents=True, exist_ok=True)
    conteo.write_text(str(_leer_entero(conteo) + 1), encoding="utf-8")
    _tocar(trabajo)
    return 0


def _limpiar_marcas_viejas():
    corte = time.time() - RETENCION_DIAS * 86400
    if not _dir_marcas().is_dir():
        return
    for ruta in _dir_marcas().iterdir():
        if ruta.name == _ruta_log().name:
            continue
        try:
            if ruta.is_file() and ruta.stat().st_mtime < corte:
                ruta.unlink()
        except OSError:
            pass


def verificar():
    if os.environ.get("BITACORA_EN_CIERRE") == "1":
        return 0        # la sesion que escribe la bitacora no se bloquea a si misma

    cfg = _config()
    datos = _payload()
    sid, proy = _contexto(datos, cfg)
    if not sid:
        return 0

    _limpiar_marcas_viejas()
    base = _base(sid, proy, cfg["raiz"])
    recordatorios = Path(str(base) + ".recordatorios")

    if _leer_entero(Path(str(base) + ".conteo")) < cfg["umbral"]:
        return 0

    if not _hay_pendiente(base, proy, cfg["umbral"]):
        # Se rearma el contador SOLO cuando la bitacora si se escribio. Sin esto
        # el tope se agota una vez y el hook queda mudo el resto de la sesion,
        # justo cuando mas material hay que registrar.
        if recordatorios.exists():
            recordatorios.write_text("0", encoding="utf-8")
        return 0

    if _leer_entero(recordatorios) >= cfg["max_recordatorios"]:
        return 0

    # razon se arma ANTES de subir el contador de recordatorios, a proposito.
    # cfg["instruccion"].format() puede reventar con KeyError si el
    # bitacora.json del usuario trae una plantilla invalida; ese error no
    # tumba el hook (lo atrapa _punto_de_entrada), pero si esto se hiciera al
    # reves el contador ya habria subido antes del fallo. Como la config
    # invalida es persistente, dos vueltas agotan max_recordatorios y el
    # bloqueo queda mudo el resto de la sesion aunque el usuario corrija su
    # plantilla, que es el mismo modo de fallar en silencio que este
    # mecanismo entero intenta evitar.
    razon = (
        "Antes de cerrar la sesion: esta sesion tuvo trabajo real y todavia no se "
        f"escribe su bitacora en {proy / 'CLAUDE.md'}.\n\n"
        + cfg["instruccion"].format(
            archivo=proy / "CLAUDE.md", pendientes=proy / "pendientes.md"
        )
    )
    _dir_marcas().mkdir(parents=True, exist_ok=True)
    recordatorios.write_text(str(_leer_entero(recordatorios) + 1), encoding="utf-8")
    print(json.dumps({"decision": "block", "reason": razon}))
    return 0


def _apuntar(texto):
    _dir_marcas().mkdir(parents=True, exist_ok=True)
    # Directivas explicitas, no "%F %T": son C99 y funcionan bajo la UCRT de
    # Windows, pero no hay necesidad de depender de eso pudiendo ser literal.
    marca = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(_ruta_log(), "a", encoding="utf-8") as fh:
        fh.write(f"{marca}  {texto}\n")


def _ruta_transcripcion(sid):
    """La salida completa (stdout+stderr) del escritor headless, por sesion.

    cierres.log es el UNICO canal de diagnostico de este mecanismo y
    INSTALACION.md manda ahi al cliente. Si ademas carga la transcripcion
    completa del modelo (parrafos largos), las lineas de estado quedan
    enterradas entre ellos. Separar el transcript no es cosmetico: es
    proteger el canal que existe para que un fallo nunca sea invisible.
    """
    return _dir_marcas() / f"escritor-{sid}.log"


def _marca_proyecto_cerrando(proy, raiz):
    """Marca de PROYECTO: hay un escritor corriendo para el, sin importar
    que sesion lo disparo.

    La guarda .cierre-intentado en _cerrar_uno es por sesion. Pero
    "cerrar --proyecto" (la ruta del lanzador) itera TODAS las sesiones con
    trabajo pendiente de un proyecto -- las marcas de trabajo viven 3 dias,
    asi que puede haber varias a la vez -- y sin esta marca de proyecto, un
    solo "cerrar --proyecto" fan-out varios escritores sobre el mismo
    CLAUDE.md al mismo tiempo. Es una carrera de escritura real, no teorica:
    paso en la sesion del 2 de agosto de 2026.

    El nombre no lleva "__" seguido de ".trabajo": a proposito, para no
    coincidir con el patron "<sid>__<slug>.trabajo" que usan tanto
    "cerrar --proyecto" como pendiente() para listar sesiones. La limpieza
    de tres dias la barre igual que cualquier otra marca, por mtime, sin
    necesitar caso especial.
    """
    return _dir_marcas() / f"proyecto-cerrando__{_slug(proy, raiz)}"


def _extras_de_lanzamiento():
    """Las banderas de Popen para desprender el proceso, aisladas del resto.

    Separada de _lanzar_escritura a proposito, sin tocar pathlib: mockear
    os.name en bloque revienta cualquier Path() que dependa de el
    (resolve(), expanduser(), incluso operaciones internas de "/"), asi que
    para poder probar la rama de Windows en Linux, la resolucion de rutas de
    _lanzar_escritura tiene que quedar completamente fuera de esta funcion.

    getattr con defecto, no el atributo directo: subprocess.DETACHED_PROCESS
    y CREATE_NEW_PROCESS_GROUP no existen fuera de Windows, y esta rama
    tiene que poder probarse en Linux simulando os.name="nt" sin reventar
    con AttributeError.
    """
    if os.name == "nt":
        return {
            "creationflags": (
                getattr(subprocess, "DETACHED_PROCESS", 0)
                | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            )
        }
    return {"start_new_session": True}


def _lanzar_escritura(sid, proy, cfg):
    """Dispara la escritura y regresa de inmediato.

    Antes esto lanzaba un hilo no demonio, o sea que el proceso del hook no
    podia salir hasta que terminara la sesion headless: hasta 600 segundos,
    contra los 10 que le da SessionEnd. Funcionaba por suerte, no por diseno.

    Ahora lanza un proceso desprendido que corre este mismo archivo con el
    subcomando "escribir", y ese proceso es el que espera. El hook no espera a
    nadie.

    cfg no se usa aqui: el disparador no necesita la configuracion, solo el
    proceso desprendido (escribir) la vuelve a leer por su cuenta. Se conserva
    en la firma a proposito, para no romper a quien ya la llama con tres
    argumentos; no es un descuido que valga "limpiar".
    """
    argumentos = [
        sys.executable, str(Path(__file__).resolve()), "escribir", sid, str(proy)
    ]
    extras = _extras_de_lanzamiento()
    subprocess.Popen(
        argumentos,
        cwd=str(proy),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        **extras,
    )


def escribir(argv):
    """La sesion headless que de verdad escribe la bitacora.

    Corre en un proceso propio, desprendido del hook. Tambien sirve para
    diagnosticar a mano:  bitacora.py escribir <session-id> <ruta-proyecto>

    Un hook de SessionEnd no puede hacer trabajar al modelo de la sesion que
    termina, porque en ese punto ya salio del loop. Por eso esto no "pide" la
    bitacora: retoma esa misma sesion y la escribe.
    """
    if len(argv) < 2:
        _apuntar("escribir sin argumentos suficientes")
        return 1

    cfg = _config()
    sid = argv[0]
    proy = _resolver(argv[1])

    # La marca de proyecto se calcula ya, no solo tras validar: si el
    # lanzamiento la creo, este proceso es el unico responsable de quitarla,
    # sin importar por donde salga (proyecto invalido, plantilla mala,
    # excepcion). Sin el finally de abajo, cualquier salida temprana deja el
    # proyecto entero bloqueado hasta que venza TIEMPO_CIERRE.
    marca_proy = None
    if proy is not None:
        try:
            marca_proy = _marca_proyecto_cerrando(proy, cfg["raiz"])
        except (ValueError, OSError):
            marca_proy = None

    try:
        if not _proyecto_valido(proy, cfg["raiz"]):
            _apuntar(f"escribir omitido  proyecto no valido  {argv[1]}")
            return 0

        try:
            instruccion = cfg["instruccion"].format(
                archivo=proy / "CLAUDE.md", pendientes=proy / "pendientes.md"
            )
        except Exception as error:
            # Separado del try de abajo a proposito: si esto revienta, el
            # proceso nunca llega a abrir Claude Code, asi que el registro
            # tiene que decir "plantilla mala" y no confundirse con un fallo
            # de lanzamiento.
            _apuntar(f"cierre fallo  plantilla de instruccion invalida  {error!r}  sid={sid}")
            return 0

        entorno = dict(os.environ, BITACORA_EN_CIERRE="1")
        transcripcion = _ruta_transcripcion(sid)
        proceso = None
        try:
            _dir_marcas().mkdir(parents=True, exist_ok=True)
            with open(transcripcion, "a", encoding="utf-8") as registro:
                proceso = subprocess.Popen(
                    [cfg["claude_bin"], "-p", "--resume", sid,
                     "--permission-mode", "acceptEdits",
                     "--allowedTools", ",".join(cfg["herramientas"])],
                    cwd=str(proy), env=entorno,
                    stdin=subprocess.PIPE, stdout=registro, stderr=registro,
                )
                # El prompt va por STDIN, no como argumento posicional: en
                # modo --resume la forma posicional falla con "No deferred
                # tool marker found in the resumed session" y ademas sale con
                # rc=0, o sea que el fallo es silencioso.
                proceso.communicate(instruccion.encode("utf-8"),
                                    timeout=TIEMPO_CIERRE)
            _apuntar(
                f"cierre terminado  rc={proceso.returncode}  sid={sid}  "
                f"transcripcion={transcripcion}"
            )
        except subprocess.TimeoutExpired:
            # communicate NO mata el proceso al vencer el plazo, solo deja de
            # esperarlo. Sin este kill queda una sesion de Claude Code colgada.
            if proceso is not None:
                try:
                    proceso.kill()
                    proceso.communicate()
                except Exception:
                    pass
            _apuntar(
                f"cierre vencido  a los {TIEMPO_CIERRE}s  sid={sid}  "
                f"transcripcion={transcripcion}"
            )
        except Exception as error:
            _apuntar(f"cierre fallo  {error!r}  sid={sid}  transcripcion={transcripcion}")
        return 0
    finally:
        if marca_proy is not None:
            try:
                marca_proy.unlink()
            except OSError:
                pass


def cerrar(argv):
    if os.environ.get("BITACORA_EN_CIERRE") == "1":
        return 0        # la sesion que escribe la bitacora no dispara otra

    cfg = _config()

    # Modo por proyecto: el lanzador sabe que proyecto cierra pero no el id de
    # la sesion de Claude Code.
    if argv and argv[0] == "--proyecto":
        if len(argv) < 2:
            return 0
        proy = _resolver(argv[1])
        if not _proyecto_valido(proy, cfg["raiz"]):
            return 0
        slug = _slug(proy, cfg["raiz"])
        if not _dir_marcas().is_dir():
            return 0
        for marca in _dir_marcas().glob(f"*__{slug}.trabajo"):
            base = Path(str(marca)[: -len(".trabajo")])
            if not _hay_pendiente(base, proy, cfg["umbral"]):
                continue
            sid = base.name.split("__", 1)[0]
            _cerrar_uno(sid, proy, cfg)
        return 0

    datos = _payload()
    sid, proy = _contexto(datos, cfg)
    if not sid:
        return 0
    _cerrar_uno(sid, proy, cfg)
    return 0


def _cerrar_uno(sid, proy, cfg):
    base = _base(sid, proy, cfg["raiz"])
    if not _hay_pendiente(base, proy, cfg["umbral"]):
        return

    # Idempotencia POR SESION: el cierre puede dispararse por dos rutas casi
    # a la vez (la llamada del lanzador y el hook SessionEnd) para la MISMA
    # sesion. Sin esta guarda salen dos escritores sobre el mismo CLAUDE.md.
    intento = Path(str(base) + ".cierre-intentado")
    anterior = _mtime(intento)
    if anterior is not None:
        edad = int(time.time() - anterior)
        if edad < VENTANA_CIERRE:
            _apuntar(f"cierre omitido  ya se intento hace {edad}s  sid={sid}")
            return

    # Idempotencia POR PROYECTO: protege el recurso real (el CLAUDE.md), no
    # solo la sesion que dispara el cierre. "cerrar --proyecto" itera TODAS
    # las sesiones con trabajo pendiente de un proyecto, asi que la guarda de
    # arriba no alcanza: dos sesiones distintas del mismo proyecto pasan cada
    # una su propia comprobacion y lanzan dos escritores igual. Un escritor
    # que se cuelgue no bloquea para siempre: pasado TIEMPO_CIERRE (el mismo
    # plazo que le da communicate) se trata como abandonado.
    marca_proy = _marca_proyecto_cerrando(proy, cfg["raiz"])
    corriendo = _mtime(marca_proy)
    if corriendo is not None:
        edad_proy = int(time.time() - corriendo)
        if edad_proy < TIEMPO_CIERRE:
            _apuntar(
                f"cierre no lanzado  ya hay un escritor corriendo en el "
                f"proyecto hace {edad_proy}s  sid={sid}"
            )
            return
        _apuntar(
            f"marca de proyecto vencida hace {edad_proy}s, se ignora  sid={sid}"
        )

    _tocar(marca_proy)
    try:
        _lanzar_escritura(sid, proy, cfg)
    except Exception as error:
        # Un lanzamiento que revienta no puede dejar "cierre disparado" como
        # ultima linea: se leeria como "sigue corriendo", y sin esto
        # .cierre-intentado seguiria bloqueando el reintento otros 120s pese
        # a que nunca hubo escritor. Se limpia la marca de proyecto ya, sin
        # esperar a que venza sola.
        _apuntar(f"cierre no lanzado  {error!r}  sid={sid}")
        try:
            marca_proy.unlink()
        except OSError:
            pass
        return

    _apuntar(f"cierre disparado  sid={sid}  proy={proy}")
    _tocar(intento)


def pendiente():
    """SessionStart: red de seguridad para sesiones que murieron sin registrar.

    Si una sesion anterior de este proyecto murio de forma abrupta no se
    disparo ni Stop ni SessionEnd, pero las marcas en disco sobreviven a esa
    muerte, asi que aqui se detecta y se recoge. En el peor caso se registra
    una sesion tarde, que es mejor que perderla.
    """
    if os.environ.get("BITACORA_EN_CIERRE") == "1":
        return 0        # la sesion que escribe la bitacora no se avisa a si misma

    cfg = _config()
    datos = _payload()
    bruto = datos.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    proy = _resolver(bruto)
    if not _proyecto_valido(proy, cfg["raiz"]):
        return 0
    if not _dir_marcas().is_dir():
        return 0

    slug = _slug(proy, cfg["raiz"])
    sesion_actual = datos.get("session_id")
    huerfanas = []
    for marca in _dir_marcas().glob(f"*__{slug}.trabajo"):
        base = Path(str(marca)[: -len(".trabajo")])
        sid = base.name.split("__", 1)[0]
        if sid == sesion_actual:
            continue
        if _hay_pendiente(base, proy, cfg["umbral"]):
            huerfanas.append(sid)

    if not huerfanas:
        return 0

    instruccion = cfg["instruccion"].format(
        archivo=proy / "CLAUDE.md", pendientes=proy / "pendientes.md"
    )
    aviso = (
        "AVISO DE BITACORA PENDIENTE.\n\n"
        f"{len(huerfanas)} sesion(es) anterior(es) de este proyecto terminaron "
        "sin registrar su trabajo, probablemente porque el proceso murio sin "
        f"cierre limpio. Identificadores: {' '.join(huerfanas)}.\n\n"
        "Antes de arrancar con lo que el usuario pida, avisale en una linea que "
        "hay bitacora pendiente y ofrece recuperarla. Si acepta, revisa esas "
        "sesiones o el historial de git del proyecto para reconstruir que paso, "
        "y despues:\n\n"
        f"{instruccion}\n\n"
        "No lo hagas sin avisarle: puede que prefiera atender primero lo suyo."
    )
    # ensure_ascii por defecto (True): la salida queda pura ASCII con \uXXXX
    # para lo que no lo sea. sys.stdout en Windows es la codepage local del
    # sistema (cp1252), no UTF-8, porque el stdout del hook es un pipe. Sin
    # esto, un acento en la instruccion configurada revienta con
    # UnicodeEncodeError o sale como mojibake, y el fallo cae en el mismo
    # camino silencioso de un error no atrapado.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": aviso,
        }
    }))
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    orden, resto = sys.argv[1], sys.argv[2:]
    if orden == "marcar":
        return marcar()
    if orden == "verificar":
        return verificar()
    if orden == "cerrar":
        return cerrar(resto)
    if orden == "pendiente":
        return pendiente()
    if orden == "escribir":
        return escribir(resto)
    print(f"orden no reconocida: {orden}", file=sys.stderr)
    return 1


def _punto_de_entrada():
    """Envoltura de main() que nunca deja escapar una excepcion.

    _tocar y conteo.write_text (entre otras escrituras de marcar/verificar/
    cerrar/pendiente) no estan blindadas: un ~/.cache sin permisos, disco
    lleno, o un antivirus de Windows bloqueando el archivo revientan con
    OSError en CADA invocacion de marcar. Sin este envoltorio esa excepcion
    solo llegaba a stderr, que Claude Code no muestra, asi que el mecanismo
    quedaba muerto para siempre sin dejar rastro en cierres.log.

    _apuntar tambien puede fallar (la misma causa: sin permisos, disco
    lleno), asi que va en su propio try/except: un log roto no puede
    impedir que este envoltorio termine limpio.
    """
    try:
        return main()
    except Exception as error:
        try:
            _apuntar(f"fallo no atrapado  {error!r}")
        except Exception:
            pass
        # Nunca tumbar la sesion del usuario por un fallo de la bitacora.
        print(f"bitacora: {error!r}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(_punto_de_entrada())
