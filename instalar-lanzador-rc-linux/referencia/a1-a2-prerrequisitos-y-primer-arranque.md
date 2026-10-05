# A1 y A2 · Prerrequisitos y el primer arranque de Claude Code, con la confianza de la carpeta

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A1. Prerrequisitos
- A2. El primer arranque de Claude Code, que es donde más gente se atora

<!-- fin del encabezado agregado al partir -->

## A1. Prerrequisitos


```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip tmux git curl unzip
curl -fsSL https://claude.ai/install.sh | bash
```

| Pieza | Verificar | Si la verificación falla |
|---|---|---|
| Python con venv | `python3 -m venv --help` | En Debian el módulo va aparte: es el paquete `python3-venv` |
| tmux | `tmux -V` | Es la capa de sesión del lanzador en Linux; sin él no lanza nada |
| unzip | `unzip -v` | Lo pide el instalador de Composio (A5e); en una Ubuntu limpia falta |
| Claude Code | `claude --version` | Ver la advertencia del PATH abajo |

> ⚠️ **Claude Code en Linux no necesita Node.js, pero el paso A4 sí.** El instalador
> nativo de `claude.ai/install.sh` trae su propio runtime y deja el binario en
> `~/.local/bin/claude`, así que para *lanzar sesiones* no hace falta Node. En cambio las
> skills de documentos (`docx`, `pptx`) sí lo usan, así que **si se va a hacer A4, y casi
> siempre se hace, Node entra como prerrequisito de todos modos** y conviene instalarlo
> aquí. Ojo con la versión: **la de los repos de Ubuntu 24.04 es demasiado vieja**, ver A4.

> ⚠️ **El instalador avisa que `~/.local/bin` no está en el PATH, y hay que hacerle caso:**
> `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`. Abrir una terminal nueva
> después. Esto además reaparece en el paso 4, porque **systemd tampoco hereda ese PATH**.

## A2. El primer arranque de Claude Code, que es donde más gente se atora


> 🔴 **Este paso es el que decide si el lanzador sirve o no, y es invisible cuando falla.**
> Claude Code recién instalado hace **cinco preguntas de primer arranque**. Una sesión
> lanzada desde el teléfono se queda detenida en la primera de ellas **sin señal de nada**:
> el botón se enciende, la sesión existe, y del otro lado no hay más que un cursor. Medido
> en la instalación limpia, una por una.

> 🔴 **Este paso completo lo tiene que correr una persona con la sesión al frente — no se
> puede delegar a un agente ni a un asistente que actúe en tu nombre.** Es el mismo patrón
> que explica el tropiezo de la pregunta 4, más abajo: de aquí en adelante la guía asume que
> quien instala tiene consola y permisos plenos sobre la máquina. Las dos formas de resolver
> la autenticación en una máquina sin pantalla que se describen más abajo (editar
> `~/.claude.json` a mano para marcar el onboarding como hecho, o automatizar la respuesta a
> las cinco preguntas con tmux) exigen exactamente los permisos que esas preguntas existen
> para proteger — un agente al que se le delegue esta tarea no los tiene, y no es un error de
> la instalación: es el diseño funcionando. Para todo lo demás de esta guía sí se puede pedir
> ayuda; para esto, no.

**La receta corta: correr `claude` una vez a mano parado en la raíz de proyectos** y
contestar las cinco. No en un proyecto, **en la raíz**, por lo del renglón 3 de la tabla.

```bash
cd ~/claude && claude          # contestar las cinco, luego /exit
```

| # | Pregunta | Qué escribe |
|---|---|---|
| 1 | Tema de color | `theme` en `~/.claude/settings.json` |
| 2 | Método de inicio de sesión | la cuenta en `~/.claude.json` |
| 3 | **¿Confías en esta carpeta?** | `projects.<ruta>.hasTrustDialogAccepted` |
| 4 | Aceptar el modo de permisos omitidos | `skipDangerousModePermissionPrompt` |
| 5 | Renderizador de pantalla completa | `fullscreenUpsellSeenCount` |

> 🔴 **La pregunta 4 es una aceptación de responsabilidad, y solo la puede dar el dueño de
> la máquina, en persona.** Acepta el modo sin confirmaciones: en él, Claude Code puede
> crear, editar y borrar archivos, y correr comandos, sin pedir aprobación antes de cada
> uno. No es un trámite del instalador ni algo que se conteste "por default": es una
> decisión informada sobre lo que puede pasar en su propio equipo. Si quien tiene el teclado
> enfrente en este momento no es el dueño de la máquina, se detiene aquí hasta que lo sea —
> ni el instalador ni un agente delegado la aceptan en su lugar.

> ⚠️ **La confianza de la carpeta se hereda del padre, y por eso hay que contestarla parado
> en `~/claude`.** Si se contesta dentro de un proyecto, **cada proyecto nuevo que se cree
> desde el teléfono se vuelve a atorar** en esa misma pregunta, invisible otra vez.
> Verificado en las dos direcciones: con solo un proyecto confiado, uno nuevo se detuvo; con
> la raíz confiada, uno recién creado arrancó directo al prompt.

> 🔴 **Pero la herencia SE CORTA EN LA RAÍZ DE CADA REPOSITORIO DE GIT, así que contestarla una
> vez en la raíz alcanza solo mientras los proyectos sean carpetas simples.** En cuanto una sesión
> le corre `git init` a un proyecto, el siguiente arranque **vuelve a pedir la suya**. Medido el 13
> de agosto de 2026 en una carpeta desechable, cambiando una sola variable:
>
> | Carpeta de prueba bajo una raíz ya confiada | Resultado |
> |---|---|
> | Sin `git init` | arranca callada, o sea que hereda |
> | La misma, **con** `git init` | sale la pantalla completa, palabra por palabra, incluido el `No, exit` |
> | La misma, con la llave sembrada | arranca callada |
>
> 🔴 **Y `--dangerously-skip-permissions` tampoco lo salta, que es lo que lo vuelve un tapón:** la
> puerta de confianza se evalúa **antes** que los permisos, y el lanzador arranca cada sesión con
> ese flag. Por eso el síntoma desde el teléfono es un botón encendido y una sesión que se queda
> esperando para siempre.
>
> ✅ **Lo que sí queda cubierto, y conviene decirlo con la misma claridad: el camino del teléfono
> entra directo.** El lanzador siembra esa llave antes de cada arranque, con la ruta ya resuelta
> (fase B). **El hueco se ve cuando el cliente abre una sesión desde su propia computadora**, en un
> proyecto que ya sea repo de git. O sea que es un pendiente de la entrega, y jamás un bloqueo del
> uso diario.

**Cómo se cierra, sin volver a contestar la pregunta proyecto por proyecto.** Es la salida que el
propio programa documenta en su mensaje de error (*"or set
projects[...].hasTrustDialogAccepted: true"*). Esto siembra la raíz y todos los proyectos que ya
existan:

```bash
python3 - <<'PY'
import json, pathlib, shutil
raiz = pathlib.Path.home() / "claude"          # la raíz de proyectos
cfg  = pathlib.Path.home() / ".claude.json"
shutil.copy(cfg, str(cfg) + ".bak")            # respaldo antes de tocar nada
datos = json.loads(cfg.read_text(encoding="utf-8"))
proyectos = datos.setdefault("projects", {})
nuevos = 0
for carpeta in [raiz] + sorted(d for d in raiz.iterdir() if d.is_dir()):
    ruta = str(carpeta.resolve()).replace("\\", "/")
    e = proyectos.get(ruta)
    if not isinstance(e, dict):
        e = {"allowedTools": [], "mcpServers": {}, "enabledMcpjsonServers": [],
             "disabledMcpjsonServers": [], "history": []}
    if not e.get("hasTrustDialogAccepted"):
        nuevos += 1
    e["hasTrustDialogAccepted"] = True
    proyectos[ruta] = e
cfg.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
print("carpetas confiadas ahora:", nuevos)
PY
```

> ⚠️ **Va la RUTA REAL, ya resuelta, y con barras diagonales.** La llave se compara como texto: si
> la raíz de proyectos es un enlace a otro disco, sembrar la forma con el enlace deja la bandera al
> lado de la llave que se lee **y el diálogo sigue saliendo igual**. Costó 12 registros huérfanos
> descubrirlo, el 13 de agosto de 2026, y por eso el fragmento lleva el `resolve()`.

> ⚠️ **Correrlo con las sesiones de Claude Code cerradas.** Ese archivo lo comparte Claude Code
> entero y lo reescribe al salir, así que una sesión abierta puede pisar la siembra sin avisar.

> 📌 **Y para los proyectos que nazcan después**, el mismo fragmento sirve tal cual, o se le pide
> al asistente que lo corra. Lo que jamás hace falta es contestar la pregunta a mano en cada uno.

**En una máquina sin pantalla** (un servidor, una VM, una mini PC en un rack) hay que
manejar ese primer arranque desde otra terminal, porque el paso de inicio de sesión **abre
un navegador y luego pide de vuelta un código pegado**:

```bash
tmux new-session -d -s primera -x 200 -y 40 "cd ~/claude && exec claude"
sleep 10
tmux capture-pane -t primera -p | tail -20          # ver en qué pregunta va
tmux send-keys -t primera Down                       # mover el cursor
tmux send-keys -t primera Enter                      # confirmar
```

> ⚠️ **Mover y confirmar van en dos comandos, con una pausa.** Mandar `Down Enter` juntos se
> come la flecha y confirma la opción que estaba, que en la pregunta 4 es **"No, exit"** y
> mata la sesión.

> ⚠️ **Crear el pane ancho (`-x 200` o más).** Con el ancho normal `capture-pane` parte las
> URL largas en varias líneas y lo que se copia no sirve.

> ⚠️ **`claude auth login --claudeai` NO sustituye a este paso.** Autentica de verdad
> (`claude auth status` reporta la cuenta), pero **no marca el onboarding como hecho**, así
> que el primer arranque vuelve a preguntar el método de inicio de sesión desde cero. Si ya
> se autenticó por ahí, se puede saltar esa pregunta poniendo `hasCompletedOnboarding: true`
> y `lastOnboardingVersion` en `~/.claude.json` **sin tocar el resto del archivo**, que trae
> la credencial.

> ⚠️ **No matar procesos con `pkill -f "claude auth login"`:** el patrón aparece en la propia
> línea de comando que lo ejecuta, así que **se mata a sí mismo**, y con él la sesión SSH,
> que devuelve 255 sin explicar nada. Matar por PID con `pgrep` primero.

> 💡 **Si el proceso de inicio de sesión tiene que sobrevivir a la terminal**, es más
> confiable una tubería con nombre que tmux, porque no depende de que siga vivo un servidor
> de terminal: `mkfifo /tmp/authpipe`, arrancarlo con `setsid ... < /tmp/authpipe`, sostener
> el fifo con `setsid bash -c "sleep 3600 > /tmp/authpipe"`, y meter el código con
> `printf '%s\n' "<codigo>" > /tmp/authpipe`. **El código va amarrado a ese intento** (trae
> su `code_challenge` y su `state`): si el proceso muere, ese código ya no sirve y hay que
> pedir otro.
