---
name: instalar-lanzador-rc-linux
description: Activar cuando alguien pida instalar, montar o configurar el lanzador rc (rc-launcher) en una máquina Linux, o dejar lista una computadora para lanzar sesiones de Claude Code desde el teléfono. También cuando pida el lanzador web, la bitácora automática que actualiza CLAUDE.md sola, o publicar el lanzador en su tailnet de Tailscale. Cubre Ubuntu y Debian con systemd.
---

# Instalar el lanzador rc y la bitácora automática en Linux

Deja una máquina Linux lista para lanzar, retomar y cerrar sesiones de Claude Code
desde el teléfono, y para que el `CLAUDE.md` de cada proyecto se escriba solo al
cerrar cada sesión.

**Procedimiento verificado de punta a punta en una VM limpia** (Ubuntu Server 24.04.4,
cloud image, sin nada preinstalado). Cada comando de aquí se corrió de verdad, en ese
orden. Para Windows existe el equivalente en `instalar-lanzador-rc-windows`.

> 📌 **A4 se verificó recreando la VM desde cero y corriendo la sección tal como quedó
> escrita**, no reconstruyéndola de una exploración previa. **Las cinco pruebas de aceptación
> pasaron**, incluida la quinta: una sesión real pidió una presentación ejecutiva de cuatro
> láminas, la generó, **corrió el ciclo de revisión visual y corrigió tres defectos de
> maquetación que ella misma detectó** en las imágenes renderizadas. Es la evidencia de que el
> runtime no solo está instalado sino bien cableado.

## Qué queda funcionando


| Capacidad | Cómo se ve para quien lo usa |
|---|---|
| Lanzar sesiones desde el teléfono | Toca un botón y la sesión aparece en su app de Claude |
| Cerrarlas desde el teléfono | Toca cerrar y desaparece de la app |
| Retomar una conversación anterior | El menú del proyecto lista sus sesiones previas |
| Crear un proyecto nuevo | Botón "+ Nuevo proyecto", con nombre y contexto |
| **Hallar un proyecto tecleando su nombre** | Un campo arriba del mosaico deja a la vista los que coinciden y esconde el resto. Con treinta proyectos se llega al que quiere con media palabra, en vez de recorrer la reja entera con el dedo. Da igual mayúsculas y acentos, y el espacio vale por guion |
| Subir archivos desde el teléfono | Caen en `bandeja/` dentro del proyecto |
| **La bitácora se escribe sola** | Al cerrar, el `CLAUDE.md` del proyecto queda actualizado sin pedirlo, su `pendientes.md` también (se crea solo si hubo trabajo abierto), y los bloques de calendario que esa sesión movió quedan al día |
| **Documentos de oficina de verdad** | Pide un Word, un Excel con fórmulas o una presentación y salen archivos que abren en Office |
| **Su correo, su calendario y su Drive** | Pregunta qué le escribieron o pide que le agenden algo, y se resuelve sin salir de la conversación |
| **Más aplicaciones, y correos con adjunto** (opcional, con Composio) | Pide que le mande el contrato anexo al broker, o que actúe en una aplicación que los conectores de claude.ai no cubren, y se resuelve igual, sin salir de la conversación |
| **Sus pendientes por proyecto** | Ve qué falta y palomea lo hecho, desde la computadora o desde el teléfono |
| **Transcribir juntas y escuchar documentos** (opcional, con cuenta propia) | Sube la grabación de una junta y pide la minuta, o pide que le lean un documento para el camino |
| **El audio se escucha con un clic** (requiere la fase B) | Lo que pidió que le leyeran llega como liga: le pica desde el teléfono y suena, sin descargarlo ni buscarlo en el navegador de archivos |
| **Le avisa cuando una tarea termina** (requiere la fase B) | El teléfono suena cuando Claude Code deja de trabajar y se queda esperando, con el nombre del proyecto, qué hizo, y una liga que abre esa misma sesión de un toque. Cubre el hueco que deja la aplicación de Claude, que avisa cuando hay algo que contestar y se calla cuando el trabajo simplemente terminó |
| **Dejar dicho qué resultó, sin abrir sesión** (requiere la fase B) | Desde el teléfono, en cada pendiente hay un botón para dictar cómo quedó, y una sección aparte para los recados sueltos del proyecto, los que valen por sí mismos. Se dicta con el teclado del teléfono, así que cuesta cero llamadas al modelo, y la siguiente sesión se entera sola de que hay algo sin leer. **La lista se queda donde estaba al guardar**, para poder recorrerla de corrido |
| **Las transcripciones de sus grabaciones llegan solas** (opcional, requiere la fase B) | Al abrir una sesión desde el teléfono, el asistente revisa la carpeta de Drive donde caen las transcripciones, le dice en un renglón cuáles son de ese proyecto y pregunta si las procesa. Con un sí, quedan guardadas en el proyecto y lo que salga de ellas llega a sus pendientes |
| **La sesión le ofrece el bloque de su agenda** (opcional, requiere la fase B) | Si reservó en el calendario un bloque para ese proyecto y está en curso o empieza en media hora, la sesión se lo resume en dos renglones al abrir y pregunta si lo atienden. Pasa igual si abre la sesión desde el teléfono o en la computadora |

## El reparto, y conviene decirlo antes de empezar


**La máquina la hace el asistente; la cuenta, la consola de Tailscale y el teléfono
los hace una persona.** No es una limitación técnica que se pueda rodear: crear la
tailnet, aprobar el dispositivo y autenticar la app del teléfono exigen a alguien
frente a un navegador. Planear la sesión de instalación con esa persona presente.

## 0. Descarte previo, cinco minutos antes de instalar nada


| Revisar | Cómo | Si falla |
|---|---|---|
| Distro con systemd | `systemctl --version` | Sin systemd no hay arranque automático; esta guía no lo cubre |
| Ubuntu 22.04+ o Debian 12+ | `lsb_release -ds` | En distros más viejas Python puede ser menor a 3.10 y hay que compilar |
| Python 3.10 o más | `python3 --version` | Ver arriba |
| `sudo` disponible | `sudo -v` | Sin sudo no se instalan paquetes ni unidades de systemd. **Aquí se para la instalación** |
| Cuenta de Anthropic con plan que incluya Claude Code | entrar a `claude.ai` | Sin plan no hay nada que instalar. Contratarlo antes de la cita |
| La máquina va a quedar encendida | preguntar | Si se apaga, el teléfono no encuentra nada. Es una condición del montaje, no un defecto |
| El correo del cliente permite apps de terceros | que **él mismo** entre a `claude.ai/customize/connectors` e intente conectar su calendario | Si su administrador de Google Workspace o Microsoft 365 tiene bloqueadas las apps de terceros, **no hay rodeo técnico**: es conversación con su área de sistemas. Descubrirlo aquí cuesta un minuto; descubrirlo en la cita cuesta la sesión |

> 📌 **Por qué ese renglón del correo está aquí y no en A5, que es donde se conecta.** Es la
> misma lógica que Tailscale: **lo que depende del área de sistemas del cliente es una barrera
> de calificación, no un paso de instalación.** Y no es hipotético — el primer piloto se quedó
> parado semanas esperando que un departamento externo devolviera un archivo. Además de correo
> y calendario, de ahí depende que el cierre automático pueda poner al día sus bloques (A7).

---

# FASE A · La base

**Lo que deja instalado:** Claude Code funcionando, la carpeta de proyectos, la bitácora
automática, el runtime que necesitan las skills de documentos, y el acceso a su correo,
calendario y Drive. **Corresponde al módulo 1 del programa.**

Es entregable completa por sí sola: si el área de sistemas del cliente bloquea Tailscale,
la fase B no se puede montar y **la fase A sigue siendo una entrega íntegra**, no media.

---


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

## A3. La bitácora automática


Es lo que hace que el `CLAUDE.md` de cada proyecto se mantenga solo. Al cerrar la sesión
también atiende el `pendientes.md` del proyecto (A7), y puede crearlo si de la sesión salió
trabajo abierto. Un único archivo de Python, biblioteca estándar, **el mismo que corre en
Windows**.

> 📌 **El cierre también pone al día el calendario, y eso depende de A5.** La sesión que
> escribe la bitácora corre con una **lista cerrada** de herramientas, y las de Google
> Calendar vienen dentro. Si el cliente no conectó su calendario en A5, el cierre
> sencillamente no lo menciona y todo lo demás funciona igual. **Si está en Microsoft 365
> sus herramientas se llaman distinto y no están en la lista**, así que esa mitad se queda
> muda hasta que se extienda con la clave `herramientas` de abajo. Qué hace y qué nunca
> hace con el calendario está en A7.

```bash
mkdir -p ~/.claude/hooks
curl -fsSL https://raw.githubusercontent.com/GustavoCarreno/claude-skills/main/bitacora/bitacora.py \
  -o ~/.claude/hooks/bitacora.py
chmod +x ~/.claude/hooks/bitacora.py
```

> 💡 **Si ya clonaste el repo `claude-skills`** (en vez del one-liner de instalación, que
> lo clona a un temporal y lo borra), cópialo de ahí en su lugar:
> `cp <carpeta-del-clon>/bitacora/bitacora.py ~/.claude/hooks/bitacora.py`.

**Comprobar que llegó completo antes de seguir** — una descarga a medias es justo el
modo de fallar silencioso que este mecanismo no puede tener:

```bash
test -s ~/.claude/hooks/bitacora.py && echo "existe y no está vacío"
python3 ~/.claude/hooks/bitacora.py pendiente < /dev/null; echo "código de salida: $?"
```

El archivo completo pesa unos 30 KB. Si `test -s` no imprime nada, la descarga falló o
quedó vacía; si `python3 ... pendiente` truena con una traza en vez de terminar
limpio, el archivo llegó corrupto o incompleto.

`~/.claude/bitacora.json`:

```json
{ "raiz_proyectos": "/home/<usuario>/claude", "umbral": 6, "max_recordatorios": 2 }
```

- **`raiz_proyectos`**: si apunta mal, el mecanismo **no dispara y no avisa**. Su modo de
  fallar es el silencio.
- **`umbral`**: herramientas de trabajo antes de considerar que hay algo que registrar.
- **`instruccion`** (opcional): el texto que se le pide al asistente. **Para un cliente
  conviene reescribirlo en su vocabulario**; el de fábrica habla de "Session Log" y
  "pipeline", que no son palabras suyas.
- **`herramientas`** (opcional): la lista cerrada con la que corre la sesión que escribe.
  De fábrica trae las de archivo más las de Google Calendar. **Se toca solo para un cliente
  en Microsoft 365**, agregando las suyas. Una lista mal escrita se ignora con aviso, en vez
  de dejar al mecanismo sin herramientas.

> 📌 **Cómo se averiguan los nombres si el cliente está en Microsoft 365, sin adivinarlos.**
> Los nombres reales dependen de cómo se llame su conector, así que se leen de su propia
> máquina: abrir una sesión ahí y pedirle **"dame los nombres exactos de las herramientas de
> calendario que tienes disponibles"**. Contesta con la lista completa, que sigue el patrón
> `mcp__claude_ai_<Conector>__<herramienta>`. Se copian a `herramientas` **junto con las seis
> de archivo** (`Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`), porque la clave reemplaza la
> lista entera, no la extiende.
>
> ⚠️ **Dejar fuera la de borrar y la de contestar invitaciones**, igual que en la lista de
> fábrica. Es lo que vuelve esas dos cosas imposibles en vez de solo prohibidas, y es la
> garantía que se le ofrece al cliente en A7.

Los cuatro hooks, en `~/.claude/settings.json`, dentro de `"hooks"`:

```json
{
  "hooks": {
    "PostToolUse": [{ "matcher": "Write|Edit|NotebookEdit|Bash",
      "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py marcar" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py verificar" }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py cerrar" }] }],
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py pendiente" }] }]
  }
}
```

> ⚠️ **Si `~/.claude/settings.json` ya existe, hay que fusionar, no sobrescribir.** En una
> máquina recién instalada no existe todavía, pero en una que ya usaba Claude Code sí, y
> pisarlo se lleva su configuración por delante.

---

## A4. El runtime que las skills dan por hecho


**Este paso existe porque las skills que se entregan instaladas no traen lo que
necesitan para correr.** Se instalan con un comando y eso es gratis, pero por dentro
asumen un runtime que solo viene preinstalado en el entorno de Anthropic. En una
laptop recién comprada no hay nada de eso, y el modo de fallar es el peor posible:
**falla tarde, ya con la persona esperando su documento**.

Lo concreto: `presentacion-elegante` envuelve a `document-skills:pptx`, y su ciclo de
revisión visual necesita LibreOffice y Poppler. `youtube-research` necesita `yt-dlp` y
`ffmpeg`. Sin A4, esas skills aparecen en la lista y no funcionan.

**Son dos capas, y se confunden fácil:** el plugin `document-skills` (que trae las
skills y sus scripts), y el runtime del sistema (que los scripts invocan). Instalar solo
la primera no sirve de nada.

### A4a. El runtime del sistema

```bash
sudo apt-get update
sudo apt-get install -y \
  libreoffice pandoc poppler-utils tesseract-ocr tesseract-ocr-spa ffmpeg
```

Entre 1 y 3 minutos según la conexión, y unos 2.6 GB de disco. Sin licenciamiento de por
medio. **Todo A4 junto (runtime, Node, paquetes y plugin) pesa unos 4 GB.**

> ⚠️ **`tesseract-ocr-spa` va aparte y es fácil olvidarlo.** El paquete base solo trae
> inglés, así que sin él el OCR de un documento en español devuelve basura en vez de
> fallar, que es peor. Verificar con `tesseract --list-langs`, tiene que aparecer `spa`.

### A4b. Node, en la versión correcta

**No sirve el Node de los repos de Ubuntu.** Trae la 18, y `sharp` (que `pptx` usa para
las imágenes) exige 20.9 o mayor. Instalado con `apt`, `require('sharp')` truena con
`Could not load the "sharp" module`, y no al instalar sino al generar la presentación.

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version   # tiene que decir v22.x, no v18.x
```

### A4c. Los paquetes de lenguaje

```bash
# Python. El --break-system-packages NO es opcional en Ubuntu 24.04, ver el aviso abajo.
pip3 install --user --break-system-packages \
  openpyxl pandas "markitdown[pptx]" Pillow defusedxml lxml \
  pytesseract pdf2image pypdf pdfplumber reportlab yt-dlp

# Node
sudo npm install -g docx pptxgenjs react react-dom react-icons sharp
```

> ⚠️ **`pip3 install` a secas falla en Ubuntu 24.04**, con un error de
> `externally-managed-environment` (PEP 668). Un venv tampoco sirve aquí, porque los
> scripts del plugin se invocan con el `python3` del sistema y no verían el venv. La
> salida es `--user --break-system-packages`, que es además lo que ya usa la skill
> `youtube-research`.

> ⚠️ **`~/.local/bin` tiene que estar en el PATH**, o `markitdown` y `yt-dlp` quedan
> instalados pero no se encuentran. Es el mismo aviso de A1, que reaparece aquí.

### A4d. El gotcha que rompe `docx` y `pptx` sin decir por qué

**Un paquete npm instalado global NO se resuelve con `require()` desde una carpeta
cualquiera.** Las skills corren sus scripts desde el proyecto de quien las usa, o sea
desde cualquier lado, así que `require('docx')` falla con `Cannot find module` aunque
`npm list -g` lo muestre instalado. Se arregla con una variable, de una vez y para siempre:

```bash
cat >> ~/.profile <<'EOF'

# Las skills de documentos corren node desde carpetas arbitrarias; sin esto,
# require() no encuentra los paquetes npm globales.
export NODE_PATH="/usr/lib/node_modules"
EOF
```

Abrir una terminal nueva después. **Verificar desde una carpeta que no sea la de
instalación**, que es justo lo que distingue esta prueba:

```bash
cd /tmp && node -e 'require("docx"); require("sharp"); console.log("OK")'
```

### A4e. El plugin de documentos

Los dos slash commands que documenta `presentacion-elegante` funcionan, pero **hay
equivalente de línea de comandos**, que es lo que conviene en una instalación:

```bash
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin list          # debe decir "enabled"
```

### A4f. Las cinco pruebas de aceptación

**No dar A4 por terminado sin correrlas.** Cada una revienta por una pieza distinta, y
la segunda es la que de verdad importa.

| # | Prueba | Qué pieza demuestra |
|---|---|---|
| 1 | Generar un `.docx` y convertirlo a PDF | npm `docx` más `soffice` |
| 2 | Generar un `.xlsx` **con una fórmula y leer su resultado** | LibreOffice recalculando |
| 3 | Generar un `.pptx` y sacarle la imagen de revisión | `pptxgenjs`, `sharp`, `soffice`, `pdftoppm` |
| 4 | Leer un PDF escaneado con OCR | Tesseract con el paquete de español |
| 5 | Correr `presentacion-elegante` de punta a punta | Que todo lo anterior esté bien cableado |

> ⚠️ **La prueba 2 es la filosa y hay que leerla bien.** `openpyxl` escribe la fórmula
> pero **no la evalúa**, así que sin LibreOffice el archivo sale con las celdas de
> resultado **vacías** y nadie se entera hasta que el cliente lo abre. Medido en el banco
> limpio: leído sin recalcular da `A3=None`; tras pasar por LibreOffice da `A3=1540`. Una
> prueba que solo verifique "se generó el archivo" **pasa igual con el defecto adentro**.

El plugin trae sus propios scripts para esto, y conviene usarlos porque es exactamente lo
que va a correr en producción:

```bash
SK=$(ls -d ~/.claude/plugins/cache/*/document-skills/*/skills | head -1)
python3 "$SK/xlsx/scripts/recalc.py" archivo.xlsx        # recalcula y reporta errores
python3 "$SK/pptx/scripts/office/soffice.py" --headless --convert-to pdf archivo.pptx
python3 "$SK/pptx/scripts/thumbnail.py" archivo.pptx     # rejilla de miniaturas
```

---

## A5. Su correo, su calendario y su Drive


**Lo que deja funcionando:** que pueda decir "¿qué me escribió el broker esta semana?" o
"agéndame con él el martes" y la sesión lo resuelva sin que él salga de la conversación.

> 📌 **El conector de calendario hace doble trabajo.** Además de esto, es lo que le permite
> al cierre automático de la bitácora (A3) dejar al día los bloques que la sesión movió. Si
> este paso se salta, esa mitad del cierre sencillamente no existe, y **no avisa**.

Se hace con los **conectores de claude.ai**, no instalando nada en la máquina. La cuenta que
ya se autenticó en A2 es la misma que los trae, así que **no hay proyecto de nube que crear,
ni credenciales que administrar, ni permisos que pedirle a nadie.**

> 📌 **Por qué esta vía y no un CLI de Google.** La alternativa era instalar un CLI con su
> propio proyecto de Google Cloud por cliente. Se descartó a propósito: **exige que el cliente
> tenga acceso a Google Cloud, y la mayoría no lo tiene**, así que convertía una capacidad
> vendible en un trámite con su área de sistemas. Además esta vía **sirve igual si están en
> Microsoft 365**, que el CLI de Google no cubriría.

### A5a. Conectarlos

**Este paso lo hace el cliente, en su navegador, y no se puede hacer desde la terminal.**

1. Entrar a **`claude.ai/customize/connectors`** con la misma cuenta de A2.
2. Conectar los que apliquen: **Gmail**, **Google Calendar**, **Google Drive**, o
   **Microsoft 365** si su correo es de Microsoft.
3. Completar el consentimiento que pida cada uno.

> ⚠️ **No intentar conectarlos desde `/mcp`, no se puede, y el error confunde.** Gmail,
> Google Calendar y Microsoft 365 **no soportan el OAuth local de Claude Code**, porque el
> proveedor de identidad solo acepta la dirección de retorno que registró claude.ai. Si se
> intenta, la propia herramienta manda a Configuración → Conectores. **No es una falla de la
> instalación.**

> ⚠️ **En planes Team y Enterprise, solo un administrador puede agregar conectores.** Si el
> cliente está en uno de esos y no es administrador, este paso lo tiene que hacer su área de
> sistemas. **Vale preguntarlo en el paso 0**, no descubrirlo con él sentado enfrente.

### A5b. Verificar

Desde la terminal, sin abrir una sesión:

```bash
claude mcp list
```

Deben aparecer con nombre de claude.ai, por ejemplo `claude.ai Gmail`, `claude.ai Google
Calendar` y `claude.ai Google Drive`, todos en `Connected`. Dentro de una sesión, `/mcp` los
lista marcados como provenientes de claude.ai.

> 🔴 **Si no aparecen, casi siempre es el método de autenticación, no el conector.** Los
> conectores **solo se cargan cuando la sesión está autenticada con la suscripción de
> claude.ai**. No se cargan si está activa alguna de estas: `ANTHROPIC_API_KEY`,
> `ANTHROPIC_AUTH_TOKEN`, un `apiKeyHelper`, un proveedor de terceros como Bedrock o Vertex, o
> un `CLAUDE_CODE_OAUTH_TOKEN` generado con `claude setup-token`.
>
> **Diagnóstico:** correr **`/status`** dentro de una sesión para ver cuál está activa. Si es
> una de esas, quitar la variable de entorno o el ajuste, y correr `/login` para elegir la
> cuenta de claude.ai.
>
> **Ojo con esto al montar el arranque automático de la fase B:** si el servicio que lanza las
> sesiones exporta una llave de API, el cliente pierde sus conectores **solo en las sesiones
> lanzadas desde el teléfono**, que es donde menos lo va a entender. Dejar el servicio sin
> esas variables.

### A5c. Qué decirle al cliente, antes de que lo descubra él

**Esto no es opcional, y conviene decirlo en la sesión de entrega**, porque son límites que se
descubren tarde y en mal momento:

- **Los borradores no llevan archivo adjunto.** La herramienta lo declara como limitación
  vigente. Si necesita mandar un adjunto, el borrador se prepara y **él le adjunta el archivo
  a mano antes de enviar**.
- **Verificar cómo queda una respuesta antes de confiarle un hilo importante.** Conviene
  probarlo con un correo propio la primera vez: que llegue dentro de la conversación y no como
  correo suelto.
- **Nada se envía solo.** El flujo natural es dejar el borrador y que él lo revise y lo mande.
  Es una limitación que juega a favor, y vale enmarcarla así.
- **Su organización puede bloquear herramientas.** En planes de empresa, un administrador
  puede marcar una herramienta como bloqueada o de aprobación obligatoria, y Claude Code lo
  respeta. Si algo "no funciona" solo para él, revisar `/mcp`.

### A5d. Cómo apagarlos

Si el cliente quiere que una máquina no vea sus conectores, en `settings.json`:

```json
{ "disableClaudeAiConnectors": true }
```

Basta un `true` en cualquier nivel de configuración para que ganen; un `false` de proyecto no
revierte un `true` de usuario. Para bloquear solo uno, va por nombre en `deniedMcpServers`
(por ejemplo `"claude.ai Gmail"`). Y para apagarlos en una sola corrida:
`ENABLE_CLAUDEAI_MCP_SERVERS=false claude`.

### A5e. Composio, para lo que los conectores no alcanzan (recomendado)

**Lo que deja funcionando:** correos **con archivo adjunto**, que el conector de claude.ai
todavía no permite, y acceso a **más de mil aplicaciones** además de Google y Microsoft. Cada
aplicación se autoriza una vez, en el navegador, y a partir de ahí la sesión la usa sola a
partir de una petición normal ("mándale al broker el contrato anexo").

**Composio (`composio.dev`) es un servicio externo que guarda los permisos de acceso del
cliente a cada aplicación y ejecuta las acciones en su nombre.** Es lo que se le recomienda al
cliente para sus conexiones, porque le ahorra el trámite de credenciales que antes obligaba a
pasar por Google Cloud o por su área de sistemas.

> 📌 **Se suma a A5 y lo deja en su lugar, por una razón concreta:** el cierre automático de la
> bitácora (A3) reconoce el calendario **por el nombre de las herramientas del conector de
> claude.ai** (es lo que mide el renglón de verificación del calendario). Si el calendario
> quedara solo en Composio, esa mitad del cierre dejaría de funcionar sin avisar. Así que
> Gmail, Calendar y Drive se quedan conectados por A5, y Composio entra para lo demás.

> ✅ **Probado el 18 de septiembre de 2026 en una Ubuntu recién instalada**, con la cuenta del
> dueño de la máquina: una sesión, a partir de una petición en lenguaje normal, dejó un
> borrador **dentro de su hilo** con un PDF adjunto **idéntico byte por byte** al original
> (verificado leyendo el correo crudo). El adjunto llega marcado como
> `application/octet-stream` y no como PDF; Gmail lo abre igual.

**Instalación, con el instalador oficial.** Pide `unzip`, que A1 ya dejó instalado; en una
Ubuntu limpia sin él falla con `unzip is required to install Composio CLI`.

```bash
curl -fsSL https://composio.dev/install | bash
exec bash -l            # para que la terminal vea el comando nuevo
composio --version
composio login          # abre el navegador: la cuenta de Composio es DEL CLIENTE
```

Después se autoriza cada aplicación que el cliente quiera usar, una por una. Cada comando
abre el navegador para el consentimiento:

```bash
composio link gmail
composio link googledrive
```

Verificación, dejando intacto lo del cliente:

```bash
composio search "send an email with an attachment" --toolkits gmail --limit 1
```

Debe regresar una herramienta de Gmail. Y la prueba que importa, con el cliente enfrente:
pedirle a una sesión que se deje a sí mismo un borrador con un PDF adjunto, y abrir el
borrador en Gmail para ver el archivo.

> ⚠️ **El instalador también intenta registrar un complemento para Claude Code**, y en una de
> las dos máquinas donde se probó ese registro falló sin detener la instalación. Da igual: la
> sesión usa el comando `composio` directo, que ya queda en `~/.local/bin` y el servicio del
> lanzador ve en su `PATH` (B3). Si el complemento falla, se reintenta con
> `composio setup --target auto --yes`.

**Lo que hay que decirle al cliente, junto con A5c y A8c:** 🔴 **Composio guarda el permiso
de acceso a sus cuentas, y cada acción pasa por sus servidores.** Es la misma clase de aviso
que DeepInfra con el audio, más pesado, porque aquí es su correo. La cuenta es suya y la
conexión se revoca en cualquier momento desde el tablero de Composio o desde la seguridad de
su cuenta de Google. **Revisar el plan vigente en `composio.dev` antes de la entrega**, para
decirle si su uso cabe en el gratuito.

---

## A6. Configurar el gitignore global

**Paso obligatorio, aunque sea invisible.** La carpeta `salida/` (donde el asistente deja
audio de voz sintética para descargar) y la `bandeja/` (archivos subidos desde el teléfono)
viven dentro de los proyectos pero no son código del proyecto. Sin gitignore, un `git add -A`
subiría estos archivos (que pueden ser material sensible: audios de junta, fotos de documentos,
contratos) a los repos privados de GitHub sin que nadie lo note.

**No pisar un gitignore global que ya exista.** Si la máquina ya tenía uno configurado (la
convención más extendida es `~/.gitignore_global`), sus patrones — típicamente `.env`, `*.pem`,
`*.key` — dejarían de aplicar de golpe si se reemplaza sin leerlo primero. El desenlace posible
es un secreto commiteado, justo lo contrario de lo que este paso busca. Se lee el valor actual
y, si ya hay uno, se anexa ahí; solo se configura el nuestro si no había ninguno. Y es
idempotente: no agrega una línea que ya esté.

```bash
ignore="$(git config --global core.excludesFile)"
if [ -z "$ignore" ]; then
  # No había ninguno configurado: el nuestro se vuelve el gitignore global.
  ignore=~/.config/git/ignore
  git config --global core.excludesFile "$ignore"
fi
ignore="${ignore/#\~/$HOME}"
mkdir -p "$(dirname "$ignore")"
touch "$ignore"

grep -qxF 'bandeja/' "$ignore" 2>/dev/null || cat >> "$ignore" << 'EOF'

# Archivos que el lanzador sube desde el teléfono y archivos que el asistente
# genera para que se bajen. Viven dentro del proyecto pero no son código, y
# pueden ser material sensible de cliente. Sin esto, un "git add -A" de
# cualquier sesión los subiría a los repos privados sin que nadie lo note.
bandeja/
salida/
EOF
```

Verificación (sin necesidad de un repositorio git):

```bash
git config --global core.excludesFile
# Debe responder con una ruta (la suya, si ya tenía una; si no, /home/<usuario>/.config/git/ignore)

ignore="$(git config --global core.excludesFile)"
ignore="${ignore/#\~/$HOME}"
grep -q "salida/" "$ignore" && echo "✓ salida/ está en el gitignore" || echo "✗ ERROR: salida/ no encontrado"
grep -q "bandeja/" "$ignore" && echo "✓ bandeja/ está en el gitignore" || echo "✗ ERROR: bandeja/ no encontrado"
```

---

## A7. Sus pendientes por proyecto, el si-ya-se-hizo

**En dos renglones: el calendario aparta el rato, y `pendientes.md` en la raíz de cada
proyecto dice si ya se hizo.** La mitad del calendario ya quedó montada en A5 (los
conectores de Google Calendar / Microsoft 365); esta sección solo la referencia, no la
repite.

> 📌 **Qué hace el cierre automático con el calendario, y qué nunca hace.** Desde que la
> bitácora atiende también esta mitad (A3), al cerrar una sesión puede **poner al día el
> bloque que esa sesión movió** — agregando a la descripción, sin reescribir lo que ya
> decía — y **agendar uno nuevo solo si se lo pidieron**, o si un pendiente nuevo trae fecha
> ya comprometida con alguien más. Un pendiente sin fecha vive en `pendientes.md` y no en el
> calendario.
>
> **Lo que nunca hace, y vale decírselo al cliente, porque es lo que vuelve seguro dejarlo
> corriendo solo:**
>
> - **No borra eventos, ni contesta invitaciones.** No es una promesa de buena conducta: esas
>   herramientas **no están** en la lista con la que corre la sesión que escribe, así que son
>   imposibles y no solo están prohibidas.
> - **No agrega ni quita invitados**, porque mover asistentes manda correo. Lo propone en una
>   línea y lo decide el cliente.
> - **No notifica a nadie.** Toda escritura va con `notificationLevel NONE`. De fábrica ese
>   parámetro es `ALL`, o sea que **actualizar un bloque que ya tiene invitados les manda
>   correo a todos**; sin esa regla, un cierre desatendido acabaría escribiéndole a terceros.
>
> ⚠️ **Para que el cierre sepa cuál bloque tocar, la nota del pendiente tiene que citarlo**,
> que es justo lo que pide el formato de abajo. Sin esa referencia no adivina: se queda
> callado, y como el silencio es también su respuesta normal cuando no hay nada que hacer,
> nadie nota la diferencia.

**Por qué va en la fase A y no en la B: funciona sin lanzador.** El archivo y el asistente
bastan, y el teléfono solo agrega el dedo. Un cliente al que su área de sistemas le bloquee
Tailscale se queda solo con la fase A y **conserva la disciplina completa**.

Se cierra igual que A6: sembrando la convención en `~/.claude/CLAUDE.md` **de forma
aditiva e idempotente**, para que cualquier sesión, en cualquier proyecto de esa máquina,
la conozca sin que haya que explicarla cada vez, y sin arriesgar lo que ya haya en el
archivo:

```bash
claude_md=~/.claude/CLAUDE.md
mkdir -p "$(dirname "$claude_md")"
touch "$claude_md"

grep -q '^## Agenda y avance' "$claude_md" || cat >> "$claude_md" << 'EOF'

## Agenda y avance: el calendario dice CUÁNDO, `pendientes.md` dice SI YA SE HIZO

Cada proyecto puede tener un `pendientes.md` en su raíz. El calendario reserva el bloque;
`pendientes.md` dice si el trabajo ya se hizo.

**El formato:**

```markdown
# Pendientes

## Me toca a mí

- [ ] Título de la tarea
      · dónde · cuánto · cabeza
      Nota con el contexto, y a qué bloque de calendario corresponde.
      » AAAA-MM-DD HH:MM · lo que dictaste desde el teléfono, sin procesar
      » AAAA-MM-DD HH:MM · otra que ya leí  ✓ AAAA-MM-DD HH:MM

## Esperando a alguien

- [ ] Nombre · desde cuándo
      Qué se espera que entregue.

## Hechas

- [x] Tarea ya hecha  ✓ AAAA-MM-DD HH:MM

## Descartados

- [-] Tarea que se decidió no hacer  ✗ AAAA-MM-DD
      El motivo.
```

**El contrato:**

- Una tarea es un renglón que casa con `^\s*-\s\[([ xX])\]\s+(.+)$`. Todo lo demás es
  decoración: encabezados, prosa, viñetas sin casilla.
- Las notas son los renglones siguientes con más sangría.
- **La retroalimentación que dictas desde el teléfono es una nota que empieza con `»`**,
  seguida de la fecha y hora y de `· `. Así: `» 2026-08-09 14:32 · lo llevé, aceptaron dos
  de tres`. La `»` es procedencia y **es permanente**: dice que eso lo dictaste tú, no yo.
  Se reconoce solo al **inicio** del renglón, así que lo que dictes puede llevar otra `»`
  adentro sin confundir nada.
- **Una retroalimentación sin procesar es la que NO termina en ` ✓ AAAA-MM-DD HH:MM`.** Al
  procesarla **agrego** ese sello; **nunca borro el texto que dictaste**. Es el mismo
  registro que los renglones `[x]`, y se protege igual: procesarla es leerla y sellarla, no
  vaciarla.
- **Lo que no cuelga de ningún pendiente va bajo `## Dicho del proyecto`**, con los
  renglones `»` a ras de margen: un recado del proyecto, no una tarea. Se reconocen igual
  que las retroalimentaciones de una tarea —la `»` es procedencia, el sello
  ` ✓ AAAA-MM-DD HH:MM` dice que ya se procesó— y **nunca se borra lo dictado**. La sección
  se crea al final del archivo, y **un `»` a ras de margen no es una tarea ni la nota de
  ninguna**, así que no cuenta ni se pinta como pendiente.
  - El encabezado lleva **exactamente dos almohadillas**. Con `###` la sección deja de
    reconocerse y tus recados dejan de contarse, **sin que nada avise**.
  - La sección **termina en el siguiente encabezado**, del nivel que sea. Si agregas uno
    después, los recados que queden debajo se vuelven invisibles.
  - Dentro de un bloque de código cercado no se lee nada, así que un `#` ahí no la corta.

  Queda así, y el encabezado va **pegado al margen izquierdo**, sin sangría:

```markdown
## Dicho del proyecto

» 2026-08-09 21:40 · el cliente movió la junta al martes
» 2026-08-08 09:12 · ya no urge lo del respaldo  ✓ 2026-08-09 10:05
```
- **Si la tarea tiene un bloque de calendario, la nota lo cita con su fecha.** Es lo que
  engancha las dos mitades: sin esa referencia, al cerrar la sesión no hay forma de saber cuál
  bloque poner al día. Cuando yo identifico o agendo uno, dejo la cita escrita ahí mismo, para
  que la próxima vez no haya que adivinar.
- **Sin identificadores** en el renglón (nada de `id: 4f2a`): el archivo se tiene que poder
  leer y editar a mano.
- Quien palomea agrega ` ✓ AAAA-MM-DD HH:MM` al final, con hora local. Al despalomear se
  quita.

> ⚠️ **Esa hora la pone la máquina donde corre el lanzador, así que su reloj y su zona
> horaria acaban escritos en el archivo del cliente.** Medido el 13 de agosto de 2026 en una
> máquina de pruebas que había quedado en UTC: palomeaba con **siete horas de adelanto** sobre
> la hora local, y nada avisaba, porque un sello con fecha y hora se ve correcto aunque diga
> otra cosa. **Comprobar la zona antes de entregar la máquina**, que cuesta un renglón:

```bash
timedatectl | grep "Time zone"     # debe decir la zona de quien la va a usar
```
- **En Windows el archivo llega con fin de línea CRLF y hay que conservarlo** al reescribir.
- **Palomeo lo que hice yo mismo y verifiqué, y también lo tuyo cuando en la sesión quedó
  constancia de que ya se hizo** (me lo dijiste con todas sus letras, o lo comprobé por mi
  cuenta). **Ante la duda no palomeo:** anoto en la nota lo que se supo y lo palomeas tú. Un
  palomeo puesto por suposición vuelve inservible la señal entera. Y si palomeo algo tuyo por
  constancia, digo en la nota de dónde salió esa constancia, para que puedas distinguir tu
  propio dedo de una deducción mía.
- **Tareas gruesas: una por entregable, no una por bloque de calendario.**

**`## Me toca a mí` es lo que puedes avanzar hoy; `## Esperando a alguien` es lo que depende
de que otra persona conteste, firme, pague o entregue**, con nombre y desde cuándo.

> ⚠️ **La trampa donde esto se rompe solo:** *"dar seguimiento a Fulano"* **sí te toca a ti**;
> lo que va en `Esperando` es la entrega de Fulano, no el empujón. Solo pasa a ser espera
> cuando ya se le empujó varias veces sin respuesta.

**Los tres indicadores** de `Me toca a mí`, en su propio renglón después del título, con
`· ` al inicio y entre ellos. Vocabulario cerrado, sin inventar palabras nuevas:

| Criterio | Valores |
|---|---|
| **Dónde** | `computadora` · `teléfono` · `en persona` |
| **Cuánto** | `minutos` (menos de 15) · `una hora` (hasta un par) · `sesión larga` (media jornada o más) |
| **Cabeza** | `concentración` · `trámite` |

Ante la duda, **escoger el valor mayor**: es peor prometer minutos y que se vaya la tarde.
La **prioridad se queda fuera a propósito**, ya la expresa el orden del archivo, que tú
controlas a mano.

**Descartar** es el tercer estado, para lo que se decidió no hacer: se marca `[-]` y se
mueve al final bajo `## Descartados`, con ` ✗ AAAA-MM-DD` y el motivo en la nota. `[-]` no
casa con la expresión de arriba, así que deja de contar y de pintarse solo.

> 🔴 **REGLA QUE NO SE PUEDE ROMPER: al reescribir un `pendientes.md`, NUNCA borrar los
> renglones `[x]` ni `[-]`.** Son un registro de lo que ya se cerró; una reescritura que se
> los lleva por delante lo destruye en silencio, y si el archivo nunca se confirmó en git, no
> hay forma de recuperarlo.
>
> **Y de ahí sale la otra: confirmar el archivo en git de verdad**, no dar por hecho que
> alguien lo hará. "Queda versionado" solo es cierto si alguien lo confirma.

Al arrancar una sesión en un proyecto, reviso su `pendientes.md` para saber qué ya se hizo,
en vez de preguntar o suponer.
EOF
```

> ⚠️ **Idempotente, igual que A6: correrlo dos veces no duplica la sección.** Y si
> `~/.claude/CLAUDE.md` ya tiene contenido de otro paso (el más obvio: si por algún motivo
> B5 ya corrió antes), esto se anexa, no lo reemplaza.

> 🔴 **El reverso de esa misma moneda, y muerde al ACTUALIZAR una máquina ya instalada:** como
> la guarda es el encabezado, en una máquina que ya trae la sección **este bloque no corre**.
> O sea que **las reglas nuevas del contrato no llegan solas**: el asistente de esa máquina
> sigue con el contrato del día que se instaló, y nada avisa. Al actualizar una instalación
> vieja hay que **agregar a mano lo que le falte**, comparando contra el bloque de aquí.

Verificación: crear un `pendientes.md` de prueba con una tarea, abrir una sesión nueva en
ese proyecto y pedirle que revise sus pendientes. Debe encontrar la tarea sin que se la
describas. Rápido y sin abrir sesión: `grep -q "pendientes.md" ~/.claude/CLAUDE.md`.

Con eso basta para que el asistente cree, redacte, edite y palomee pendientes con sus
herramientas de siempre, sin esperar al lanzador.

---

## A8. Transcribir juntas y escuchar documentos, dos capacidades que se pagan aparte

**Entre las skills que ya trae instaladas hay dos que cuestan dinero, y ninguna guía lo
dice.** Sin esta sección, la primera vez que el cliente suba la grabación de una junta y
pida la minuta, la skill le va a pedir una llave que no sabía que necesitaba. Mejor
que lo sepa antes de instalar, no a media entrega.

**Qué dejan hacer, en sus palabras:**

- Sube el audio de una junta o una nota de voz y pide "transcribe esto" o "hazme la
  minuta": regresa el texto.
- Pide "léeme este documento" o "pásamelo a audio para el camino": regresa un MP3.

Las dos usan **DeepInfra**, un servicio externo, y **con la cuenta del propio cliente**,
no la nuestra: el consumo se cobra a su tarjeta, no a la de Gustavo.

### A8a. Conseguir la cuenta y guardar la llave

El primer uso de cualquiera de las dos la pide, con este texto ya escrito en la propia
skill (no hay que redactarlo de nuevo):

> Para transcribir necesito una llave de DeepInfra, que es tuya y se cobra a tu cuenta.
> Son dos minutos: entra a https://deepinfra.com, crea la cuenta con Google o GitHub, y
> en **Dashboard → API Keys → New API Key** genera una. Pégamela aquí. Una hora de audio
> te va a costar alrededor de un centavo de dólar.

La llave se guarda **por entrada estándar, nunca como argumento** del comando (un
argumento queda en el historial del shell y en la lista de procesos):

```bash
printf '%s' 'LA_LLAVE' | python3 ~/.claude/skills/whisper-deepinfra/whisper_deepinfra.py --guardar-llave
```

Queda en `~/.config/deepinfra/credentials`, con permisos solo para su usuario. **Es una
sola llave para las dos capacidades**: quien ya la dio para transcribir no la vuelve a
dar para escuchar un documento, y viceversa.

### A8b. Cuánto cuesta, con cifras reales

| Capacidad | Precio | Aterrizado |
|---|---|---|
| Transcribir una grabación | $0.00020 USD por minuto | una junta de una hora, poco más de un centavo de dólar ($0.012) |
| Convertir un documento a audio | $0.62 USD por millón de caracteres | un documento de 10 páginas (~20 mil caracteres), alrededor de un centavo de dólar |

> 📌 **Si además se contrató la fase B, el audio se escucha con un clic.** El MP3 cae en
> `salida/` del proyecto y el lanzador lo sirve por una liga, así que desde el teléfono se
> toca y suena, en vez de descargarlo y buscarlo en el navegador de archivos. Sin la fase B
> la capacidad funciona igual, solo que el audio llega como archivo adjunto. Se verifica en
> el renglón 14.

### A8c. Lo que hay que decirle, antes de que lo descubra él

🔴 **El audio de sus juntas y el texto de sus documentos salen de su computadora y se
procesan en DeepInfra, un tercero.** No es información que se quede en su máquina.
Conviene decirlo en la sesión de entrega, junto con lo de A5c, antes de que suba la
grabación de una junta con terceros delicados.

**Son opcionales.** Sin la cuenta, las dos capacidades quedan dormidas y todo lo demás
(el lanzador, la bitácora, los documentos de oficina, los conectores) sigue funcionando
igual. La cuenta se puede crear después, la primera vez que de verdad las necesite.

---

# FASE B · La red y el teléfono

**Lo que deja instalado:** la tailnet del cliente, el lanzador publicado y la bandeja.
**Corresponde al módulo 3 del programa.**

**No empezar esta fase sin la A terminada y verificada.** Y si el paso 0 detectó que la
empresa bloquea Tailscale o las instalaciones, esta fase no procede: eso se supo antes de
la primera sesión justamente para no descubrirlo aquí.

---


## B1. La tailnet


**Sin la red, todo lo demás se instala bien y no sirve para nada**, porque el teléfono
no encuentra la máquina.

**Si es un cliente, crea su propia tailnet, no se une a la nuestra.** Meter la máquina
de un cliente en nuestra red la pone junto a los ambientes de producción de otros. Su
red es suya, y así se la lleva el día que deje de trabajar con nosotros.

```bash
curl -fsSL https://tailscale.com/install.sh | sudo sh
sudo tailscale up --hostname=<nombre-corto-de-la-maquina>
```

`tailscale up` **se queda esperando** e imprime una URL de `login.tailscale.com`. Alguien
tiene que abrirla en un navegador donde esa cuenta esté iniciada. Ese es el primer punto
donde el asistente no puede seguir solo.

> 💡 **Para no dejar la terminal colgada:** lanzarlo de fondo y leer la URL del archivo.
> `sudo nohup tailscale up --hostname=<nombre> > /tmp/tsup.log 2>&1 &` y luego
> `cat /tmp/tsup.log`.

**El teléfono es la otra mitad del montaje.** Dos apps, las dos de la tienda:

1. **Tailscale**, con **la misma cuenta** de la tailnet. Al terminar, `tailscale status`
   en la máquina debe listar también el teléfono.
2. **Claude**, la app oficial de Anthropic, con la misma cuenta que se autenticó arriba.
   **Es con la que se abre la sesión**: el lanzador solo la enciende, la conversación
   ocurre en esa app.

> ⚠️ **Son dos canales distintos, y entenderlo ahorra diagnósticos.** La tailnet solo
> sirve para alcanzar **la página del lanzador**. La sesión de Claude no viaja por la
> tailnet: el teléfono se conecta a ella por la infraestructura de Anthropic. O sea que
> "no abre la página" y "no aparece la sesión" son fallas distintas.

**Los tres interruptores de la consola de administración** viven en `login.tailscale.com`,
no en la máquina, y sin ellos la instalación termina sin errores y no funciona:

| Interruptor | Dónde | Comprobar |
|---|---|---|
| **MagicDNS** | consola → DNS | `tailscale dns status` debe decir `MagicDNS: enabled tailnet-wide` |
| **Certificados HTTPS** | consola → DNS | El paso 5 falla con un mensaje explícito si están apagados |
| **Aprobación para publicar** | la imprime el propio comando | Si el paso 5 imprime una URL de aprobación, abrirla y aceptar |

## B2. El lanzador


> 🔴 **De dónde sale el código, porque este paso no se puede hacer sin traerlo.** A
> diferencia de `bitacora.py` (A3), **el lanzador NO está en el repo público de skills** y no
> hay URL de la que bajarlo. Vive en un repo privado, y **lo trae quien instala**: por `scp`
> desde tu equipo, en una memoria USB, o clonando el repo privado si la máquina tiene acceso.
> Consíguelo **antes** de empezar esta fase.

```bash
# ORIGEN es la copia del lanzador que TRAJISTE. Ajusta la ruta a donde la dejaste.
ORIGEN=/ruta/a/tu/copia/de/rc-launcher

# el código va al home, no a una ruta de sistema
rsync -a --exclude .venv --exclude __pycache__ --exclude .git \
      "$ORIGEN"/ ~/rc-launcher/

mkdir -p ~/claude          # la raíz de proyectos, que es donde vive el trabajo
```

**Comprobar que llegó completo antes de instalar nada**, porque una copia a medias arranca
igual y falla después, lejos de aquí:

```bash
for f in app.py sessions.py procesos.py requirements.txt templates tests; do
  [ -e ~/rc-launcher/"$f" ] || echo "FALTA: $f"
done
echo "revisión terminada (sin líneas FALTA arriba = completo)"
```

Ya con la copia completa, el entorno:

```bash
cd ~/rc-launcher
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`~/claude` no es negociable sin tocar código: `sessions.py` la calcula como
`Path.home() / "claude"`. Si los proyectos viven en otro disco, poner un symlink ahí.

**Comprobar antes de seguir**, porque si esto falla, nada de lo demás importa:

```bash
cd ~/rc-launcher && .venv/bin/python -m pytest -q
```

Debe pasar **la suite completa, sin una sola falla**. Al 17 de agosto de 2026 son 622 pruebas
y corren en un segundo. **El número crece con cada versión, así que no lo trates como
contraseña**: lo que importa es que no falle ninguna, en la máquina del cliente, sin tocar
una línea. Eso es lo que demuestra que el código no depende de la máquina donde nació.

> 📌 **Si el proyecto ya tiene `pendientes.md` (A7), el lanzador ya lo pinta y lo palomea
> con el dedo, sin configuración adicional.** No hay ningún paso extra que hacer aquí.

### B2b. Llevarle una versión nueva a una máquina que ya lo tiene

**Esto es para las actualizaciones, no para la instalación inicial.** El lanzador se mejora
seguido, y el código llegó aquí por copia: **nada se entera solo de que hay una versión
nueva**, así que actualizar es volver a copiar y reiniciar.

```bash
ORIGEN=/ruta/a/tu/copia/de/rc-launcher

rsync -a --delete --exclude .venv --exclude __pycache__ --exclude .git \
      "$ORIGEN"/ ~/rc-launcher/
cd ~/rc-launcher
.venv/bin/pip install -q -r requirements.txt    # por si la versión nueva pide algo más
.venv/bin/python -m pytest -q                   # todas en verde ANTES de reiniciar
sudo systemctl restart rc-launcher
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/salud
```

> ✅ **Reiniciar el servicio NO mata las sesiones que estén trabajando**, gracias a
> `KillMode=process` en el unit (B3). Se puede actualizar con el cliente usándolo.

> ⚠️ **El `--delete` es a propósito:** sin él, un archivo que la versión nueva ya eliminó se
> queda en la máquina y puede seguir importándose. Los excluidos están a salvo, así que el
> `.venv` sobrevive.

> 🔴 **La pestaña que el teléfono ya tenía abierta sigue corriendo el código anterior.** El
> HTML y su script viajan juntos en la respuesta de la raíz, y una pestaña abierta conserva el
> que le tocó al cargarse: HTMX redibuja pedazos, y el script ya no se vuelve a leer. Tras
> actualizar hay que **recargar** desde el teléfono. Sin eso se está probando código viejo
> contra un servidor nuevo, y eso confunde cualquier diagnóstico.

> ⚠️ **La primera sesión de un proyecto creado con "+ Nuevo proyecto" puede repetir la
> pregunta de confianza de A2, aunque la raíz ya esté confiada.** Es el mismo síntoma, y
> otra vez invisible desde el teléfono: el botón se enciende, la sesión existe, y del otro
> lado solo hay un cursor esperando esa respuesta. Se contesta igual, desde la app del
> teléfono, dentro de esa misma sesión: sí, y ya arranca. **Mejor todavía, adelantarlo: la
> primera vez que se estrena un proyecto nuevo, abrir su primera sesión desde la
> computadora** (`cd ~/claude/<proyecto> && claude`, contestar, `/exit`) antes de tocarlo
> desde el teléfono. Las sesiones siguientes de ese proyecto, y las que se lancen desde el
> teléfono, ya arrancan directo.

## B3. Arranque automático


Dos unidades de systemd **a nivel de sistema** con `User=`, no unidades de usuario.
Sustituir `<usuario>` en las cuatro apariciones:

```ini
# /etc/systemd/system/rc-launcher.service
[Unit]
Description=rc session launcher
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=simple
User=<usuario>
Environment=PATH=/home/<usuario>/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WorkingDirectory=/home/<usuario>/rc-launcher
ExecStart=/home/<usuario>/rc-launcher/.venv/bin/python /home/<usuario>/rc-launcher/app.py
Restart=on-failure
RestartSec=5
KillMode=process

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/rc-watcher.service        (Type=oneshot, mismo User/PATH/WorkingDirectory)
ExecStart=/home/<usuario>/rc-launcher/.venv/bin/python /home/<usuario>/rc-launcher/watcher.py

# /etc/systemd/system/rc-watcher.timer
[Timer]
OnBootSec=2min
OnUnitActiveSec=1min
AccuracySec=15s
Persistent=true
[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rc-launcher.service rc-watcher.timer
```

> ⚠️ **`KillMode=process` es obligatorio, no una preferencia.** Sin él systemd usa
> `control-group` y manda SIGTERM a **todo** el cgroup en cada `systemctl restart`. Como
> el servidor de tmux es único por usuario, si el servicio lo arrancó primero, **cada
> sesión rc de la máquina muere al reiniciar el servicio**, incluidas las abiertas a mano.

> ⚠️ **`Environment=PATH=` con `~/.local/bin` adelante es obligatorio.** Una unidad sin
> él no hereda el PATH interactivo y no encuentra `claude`. Falla **en silencio** si el
> comando que lo invoca usa `;` en vez de `&&`.

> ⚠️ **`systemctl status rc-launcher` NO mide la app.** Reporta el cgroup entero, con
> todas las sesiones adentro. Para medirla:
> `ps -o rss -p $(systemctl show -p MainPID --value rc-launcher.service)`.

## B3b. El canal de avisos, para que el vigilante sirva de algo

**Esto faltaba hasta el 10 sep 2026**, y es un hueco que conviene entender antes de
saltárselo: **B3 habilita `rc-watcher.timer`, que corre cada minuto**, y su trabajo es
avisar cuando una tarea termina, o sea cuando Claude Code se queda esperando a la
persona. Sin este paso el vigilante corre, detecta el turno cerrado, **intenta avisar y
falla**, porque le falta a dónde mandar. Y como un envío fallido se deja sin marcar a
propósito, para reintentarlo, **el error se repite cada minuto** en el registro del
sistema, donde el usuario jamás lo ve.

El canal es **ntfy**: una aplicación de teléfono que recibe avisos y un servidor que los
publica. Sin cuenta de correo, sin token de por medio, y con una versión gratuita.

### Dos caminos, y el segundo es el normal

| Camino | Cuándo | Qué se pone en `url` |
|---|---|---|
| **Servidor propio** | La organización ya tiene uno, o el material es delicado | Su dirección, más `usuario` y `clave` |
| **`ntfy.sh`, el público** | Lo demás. Cero infraestructura, cero costo, cero cuenta | `https://ntfy.sh`, con `usuario` y `clave` vacíos |

> 🔴 **Con `ntfy.sh` el tema TIENE que ser un nombre largo y difícil de adivinar**, porque
> ahí un tema es público: quien lo escriba lo lee. El aviso lleva el **nombre del proyecto
> y el título de lo que se hizo**, así que con un tema como `avisos` cualquiera vería de
> qué trabaja el cliente. El comando de abajo lo genera al azar.
>
> ⚠️ **Y hay que decirlo en voz alta antes de elegir**, con la misma franqueza de A5c: en
> el servidor público esos títulos viajan por una máquina ajena. Si el cliente maneja
> material confidencial, o es servidor propio, o el aviso se deja genérico.

### Dejarlo configurado

```bash
mkdir -p ~/.config/rc-launcher
TEMA="rc-$(head -c 18 /dev/urandom | base64 | tr -dc 'a-z0-9' | head -c 16)"
cat > ~/.config/rc-launcher/ntfy.json <<EOF
{
  "url": "https://ntfy.sh",
  "tema": "$TEMA",
  "usuario": "",
  "clave": "",
  "prioridad": "default",
  "titulo_suelto": "Claude Code"
}
EOF
chmod 600 ~/.config/rc-launcher/ntfy.json
echo "El tema es: $TEMA"
```

**El tema hay que copiarlo**, porque es lo que la persona escribe en su teléfono. Con
servidor propio se cambian `url`, `usuario` y `clave`, y el tema puede ser legible.

### Del lado del teléfono

Instalar **ntfy** (Play Store, App Store o F-Droid), tocar **Agregar suscripción** y
escribir el tema. Con servidor propio, marcar **Usar otro servidor** y poner la dirección
con su usuario y contraseña.

### Comprobarlo, que es un renglón

```bash
cd ~/rc-launcher && .venv/bin/python -c "
import avisos
print(avisos.enviar('Prueba de instalación\nSi ves esto en el teléfono, el canal quedó.'))
"
```

Sale `(True, 'avisado')` **y el aviso llega al teléfono**. Las dos cosas: el `True` dice
que el servidor lo aceptó, y solo el teléfono dice que la suscripción está bien escrita.

> 📌 **Si sale `(False, ...)`, el mensaje dice cuál de las tres cosas falló**: falta el
> archivo, el servidor contestó un código (un 401 es usuario o clave), o la red. Un
> `403` en `ntfy.sh` suele ser un tema con mayúsculas o con caracteres raros.

## B4. Publicarlo en la tailnet


```bash
sudo tailscale serve --bg http://127.0.0.1:8765
tailscale serve status
```

Queda en `https://<nombre>.<tailnet>.ts.net/`, **alcanzable solo desde la tailnet**. Esa
es la URL que se le da a la persona.

## B5. Decirle a las sesiones qué es la bandeja


**Paso corto y fácil de olvidar, y sin él la mitad del valor del lanzador no se usa.** El
lanzador deja lo que se sube desde el teléfono en `bandeja/`, dentro del proyecto. Pero
**nada le dice a la sesión que esa convención existe**: al pedirle "mira lo que subí a la
bandeja" contesta preguntando si te refieres al correo, porque para ella no significa nada.

**Aditivo e idempotente, igual que A6 y A7** (que ya pudo haber escrito en este mismo
archivo, porque la fase A corre antes que esta): se anexa a `~/.claude/CLAUDE.md`, nunca
lo reemplaza.

```bash
claude_md=~/.claude/CLAUDE.md
mkdir -p "$(dirname "$claude_md")"
touch "$claude_md"

grep -q '^## La bandeja' "$claude_md" || cat >> "$claude_md" << 'EOF'

## La bandeja: archivos que subo desde el teléfono


Cada proyecto puede tener una carpeta `bandeja/` en su raíz. Ahí es donde el lanzador rc
deja lo que subo desde el celular: fotos, audios de junta, PDFs, capturas.

**Si menciono "la bandeja", me refiero a esa carpeta del proyecto en el que estás, no a un
correo ni a nada de Gmail.** Revisar `bandeja/` del proyecto actual y trabajar con lo que
haya ahí.

Está en el gitignore, así que no aparece en `git status`. Al terminar de usar un archivo,
yo decido qué hacer con él desde el menú del lanzador, **no moverlo ni borrarlo por
iniciativa propia**, salvo que lo pida.
EOF
```

> ⚠️ **Correrlo dos veces no duplica la sección**, ni pisa la convención de pendientes que
> A7 ya sembró ahí. Es el mismo guardado con `grep` que usan A6 y A7.

Verificación: subir un archivo desde el teléfono, abrir la sesión de ese proyecto y pedirle
que vea la bandeja. Debe encontrarlo sin que le digas la ruta. Rápido y sin teléfono:
`grep -q '^## La bandeja' ~/.claude/CLAUDE.md`.

## B6. El comando `rc`, para lanzar desde la terminal (opcional)

**El camino principal es el teléfono**, y esta sección se puede saltar entera sin perder
nada de lo demás. Sirve para quien ya está frente a una terminal y prefiere teclear en vez
de sacar el celular.

**Lo que importa, y es lo que lo hace seguro: la sesión que nace aquí es la misma que nace
desde el teléfono.** El comando llama al mismo código, así que aparece en el mosaico y se
puede cerrar con el dedo. Dos formas distintas de crear una sesión se separan sin que nadie
lo note, y ahí es donde una sesión se vuelve invisible e inmatable.

```bash
sudo tee /usr/local/bin/rc > /dev/null << 'EOF'
#!/bin/bash
exec /usr/bin/python3 RUTA_DEL_LANZADOR/procesos_tmux.py "$@"
EOF
sudo chmod +x /usr/local/bin/rc
```

Sustituir `RUTA_DEL_LANZADOR` por la carpeta real. Uso:

```bash
rc                      # lista las carpetas disponibles
rc mi-proyecto          # abre la sesión y te deja trabajando DENTRO
rc mi-proyecto -d       # la deja corriendo y te devuelve la terminal
rc mi-proyecto --resume <session-id>
```

Verificación: `rc` sin argumentos lista los proyectos; `rc <alguno> -d` crea la sesión y el
mosaico la muestra en **Activos**.

## B7. Las transcripciones que llegan a Drive (opcional)

**Lo que deja funcionando:** el cliente graba una junta con una grabadora o una aplicación que
deja la transcripción en una carpeta de su Google Drive. Al abrir una sesión desde el teléfono,
el asistente revisa esa carpeta **antes de cualquier otra cosa**, decide cuáles tratan de ese
proyecto (primero por el nombre, y si hay duda, leyendo solo el resumen del principio), las
resume en un renglón cada una y **pregunta si las procesa**. Con un sí:

1. la guarda en `transcripciones/` del proyecto, con la fecha `AAAA-MM-DD` al inicio del nombre;
2. lleva a `pendientes.md` y al `CLAUDE.md` lo que salga de ella;
3. la mueve en Drive a la subcarpeta `Procesadas`, **para que ningún otro proyecto se la vuelva
   a ofrecer**.

**Es la continuación natural de A8:** allá el cliente sube el audio y pide la minuta; aquí la
transcripción ya existe y lo que se automatiza es encontrarla y archivarla en el proyecto
correcto.

> 📌 **Lo reciben las sesiones que nacen del lanzador**, o sea las del teléfono y las del
> comando `rc` (B6). **Una sesión abierta directo en la terminal o en VS Code lo recibe solo si
> está instalado el gancho de B8b**; sin él, arranca sin el aviso.
> Y **el lanzador en sí nunca habla con Google**: solo lee un archivo de configuración y le
> redacta la instrucción a la sesión. Quien lista, lee y mueve en Drive es el asistente, con el
> conector de A5.

### B7a. Lo que tiene que existir antes

| Requisito | Por qué |
|---|---|
| **Algo que deje las transcripciones en una carpeta de Drive** | El lanzador revisa la carpeta y le es indiferente de dónde llegan. El montaje de referencia es una grabadora Comulytic con una automatización de Zapier (un servicio que conecta aplicaciones entre sí) que copia cada transcripción a Drive. Conviene que cada archivo traiga la **fecha y un título** en el nombre, que es con lo que el asistente decide sin abrirlo |
| **El conector de Google Drive de A5**, en `Connected` | Con él se lista la carpeta, se lee el archivo y se mueve a `Procesadas`. Composio (A5e) también sirve, si el Drive está conectado ahí, y `gws` en la máquina que ya lo tenga configurado |
| **Una copia del lanzador del 22 de septiembre de 2026 o posterior** | Es la que trae `transcripciones_drive.py`. Una anterior ignora la configuración en silencio |

Comprobar la copia:

```bash
[ -e ~/rc-launcher/transcripciones_drive.py ] && echo "trae la revisión" || echo "copia anterior al 22 de septiembre de 2026"
```

### B7b. La carpeta y la configuración

1. **En Drive, con la cuenta del cliente:** crear la carpeta donde caerán las transcripciones
   (el nombre sugerido es `Transcripciones`) y **dentro de ella una subcarpeta llamada
   exactamente `Procesadas`**, porque ese es el nombre que usa la instrucción.
2. **Copiar el identificador de la carpeta** desde la barra de direcciones del navegador: es lo
   que va después de `drive.google.com/drive/folders/`.
3. **Escribir la configuración** en `~/.config/rc-launcher/transcripciones.json`, sustituyendo el identificador:

```bash
mkdir -p ~/.config/rc-launcher
cat > ~/.config/rc-launcher/transcripciones.json << 'EOF'
{"carpeta": "Transcripciones", "carpeta_id": "EL_ID_DE_LA_CARPETA"}
EOF
```

**Sin reinicios:** el lanzador lee ese archivo cada vez que lanza una sesión. Y para
apagar la revisión basta con borrarlo; la sesión vuelve a arrancar exactamente como antes.

### B7c. Verificar

Primero que la configuración se lee (debe imprimir `True`):

```bash
cd ~/rc-launcher && .venv/bin/python -c "import transcripciones_drive as t; print(t.instruccion_para_la_sesion('prueba') is not None)"
```

Luego la prueba completa, que conviene hacer con el cliente enfrente:

1. Dejar en la carpeta de Drive un archivo de prueba cuyo nombre diga de qué proyecto es, por
   ejemplo `2026-09-24 Prueba de instalación para <proyecto>.txt`.
2. Desde el teléfono, lanzar una sesión nueva en ese proyecto. **Lo primero que debe decir la
   sesión** es que encontró esa transcripción, con su resumen en un renglón, y preguntar si la
   procesa.
3. Contestar que sí, y comprobar las dos mitades: el archivo en `transcripciones/` del proyecto
   con la fecha al inicio, y **en Drive, el archivo ya dentro de `Procesadas`**.

> ✅ **Probado el 24 de septiembre de 2026 en `win11-dogfood`, con el aviso real del lanzador:**
> la sesión encontró la transcripción, la guardó en `transcripciones/` con la fecha al inicio,
> llevó el acuerdo a `pendientes.md` y **la movió a `Procesadas` con el conector de Drive de
> claude.ai**, cambiando su carpeta padre. Se confirmó leyendo el archivo en Drive, no el reporte
> de la sesión.
>
> ⚠️ **El síntoma que delata un fallo:** si el archivo se queda en la carpeta principal, cada
> sesión de cada proyecto lo va a volver a ofrecer. Por eso este paso se revisa antes de
> entregar.

### B7d. Lo que cuesta, y lo que hay que decirle

- **Cada sesión lanzada arranca con una consulta a Drive**, aunque la carpeta esté vacía. Es uso
  de su suscripción, pequeño, y se paga en cada arranque.
- **Un archivo ajeno a todos los proyectos se revisa para siempre** (la bienvenida de la
  grabadora es el caso típico). Moverlo a `Procesadas` a mano, o borrarlo.
- 🔴 **Lo grabado sale de su equipo**: la transcripción la hace el servicio de la grabadora y la
  guarda Drive. Y **el consentimiento de las personas grabadas corre por su cuenta**, igual que
  en A8c. Decirlo en la entrega, antes de que grabe una junta con terceros.

## B8. El bloque de calendario al arrancar (opcional)

**Lo que deja funcionando:** el cliente reserva en su calendario un bloque para un proyecto, por
ejemplo *"Marán · Carta al broker de LG"* de 10:00 a 12:00. Al abrir una sesión en ese proyecto
mientras el bloque está en curso, o hasta 30 minutos antes de que empiece, el asistente lo
encuentra solo, lee su descripción y la tarea de `pendientes.md` que le corresponde, **resume en
dos renglones qué toca y pregunta «¿Lo atendemos?»**. Empieza a trabajar solo con un sí.

**Es la mitad que le faltaba a A7:** allá quedó escrito que el calendario dice cuándo y
`pendientes.md` dice si ya se hizo. Con esto, la sesión junta las dos cosas sin que el cliente
tenga que pedir que se revise la agenda.

**Trae dos piezas, y conviene instalar las dos:**

| Pieza | Qué hace |
|---|---|
| **La configuración del calendario** (`calendario.json`) | Le dice al lanzador qué calendarios revisar. Sin ella, la revisión se queda apagada y la sesión arranca como antes |
| **El aviso para las sesiones abiertas a mano** (`aviso_arranque.py`) | Un *gancho* de Claude Code, o sea un programa que Claude Code corre solo en cierto momento; este corre al iniciar la sesión. Le entrega el mismo aviso a una sesión abierta con `claude` en la terminal o en VS Code, que hasta ahora arrancaba sin él |

> 📌 **El gancho también le lleva a esas sesiones las otras dos revisiones**, la retroalimentación
> dictada desde el teléfono y las transcripciones de B7. Con el lanzador el aviso llega como
> primera instrucción y la sesión lo atiende sola; con `claude` directo llega como contexto y se
> atiende al primer mensaje, aunque sea un "hola". **Se calla a propósito en dos casos:** al
> compactar la conversación, para no repetirlo a media sesión, y en las sesiones del lanzador,
> que ya lo traen (llevan `RC_LANZADOR=1` en el entorno).

> 📌 **El lanzador sigue sin hablar con Google**, igual que en B7: solo lee la configuración y le
> redacta la instrucción a la sesión. Quien consulta el calendario es el asistente, y la
> instrucción dice "revisa en Google Calendar" sin nombrar herramienta, así que **sirve cualquiera
> de las tres vías** que tenga la máquina:
>
> | Vía | Cuándo |
> |---|---|
> | **El conector de Google Calendar de claude.ai** (A5) | La de fábrica, y la que casi todo cliente va a tener |
> | **Composio** (A5e) | Si el cliente lo contrató y conectó ahí su Google Calendar. Una sola llamada consulta varios calendarios a la vez |
> | **`gws`**, la herramienta de línea de comandos de Google Workspace | Solo en la máquina que ya lo tenga configurado. Exige un proyecto de Google Cloud propio, y por eso queda fuera como vía de fábrica |
>
> **Probadas las tres el 25 de septiembre de 2026**, cada una con el identificador de un
> calendario secundario y con `primary`, y las tres encontraron el mismo bloque en curso.

### B8a. Lo que tiene que existir antes

| Requisito | Por qué |
|---|---|
| **Una vía al calendario**: el conector de A5 en `Connected`, Composio con Google Calendar conectado, o `gws` configurado | Con ella se buscan los eventos. Basta una |
| **Una copia del lanzador del 25 de septiembre de 2026 o posterior** | Es la que trae `calendario_sesion.py` y `aviso_arranque.py`. Una anterior ignora la configuración en silencio |
| **La convención del título**, explicada al cliente | Ver B8d. Sin ella la sesión decide por la descripción y se equivoca más |

```bash
for f in calendario_sesion.py aviso_arranque.py; do [ -e ~/rc-launcher/$f ] || echo "FALTA: $f"; done; echo "revisión terminada"
```

### B8b. La configuración y el gancho

1. **Sacar el identificador de cada calendario**, en Google Calendar desde la computadora: los
   tres puntos junto al nombre del calendario → *Configuración y uso compartido* → sección
   *Integrar el calendario* → *ID del calendario*. El calendario principal no hace falta
   buscarlo: su identificador es `primary`.
2. **Escribir la configuración**, sustituyendo el identificador:

```bash
mkdir -p ~/.config/rc-launcher
cat > ~/.config/rc-launcher/calendario.json << 'FIN'
{"calendarios": [
  {"nombre": "Trabajo", "id": "EL_ID_DEL_CALENDARIO_DE_TRABAJO"},
  {"nombre": "principal", "id": "primary"}
], "minutos_antes": 30}
FIN
```

> ⚠️ **El principal va en la lista aunque el cliente tenga un calendario aparte para el
> trabajo.** Las invitaciones de sus clientes caen en el principal, porque el dueño de ese
> evento es quien invita. Si solo tiene el principal, la lista lleva ese renglón y ya.

3. **Registrar el gancho** en `~/.claude/settings.json`. Este fragmento lo agrega sin tocar lo
   demás, y no lo duplica si ya estaba:

```bash
python3 - << 'FIN'
import json, pathlib, shutil
cfg = pathlib.Path.home() / ".claude" / "settings.json"
orden = f"/usr/bin/python3 {pathlib.Path.home()}/rc-launcher/aviso_arranque.py"
shutil.copy(cfg, str(cfg) + ".bak")            # respaldo antes de tocar nada
datos = json.loads(cfg.read_text(encoding="utf-8"))
inicio = datos.setdefault("hooks", {}).setdefault("SessionStart", [])
ya = any(h.get("command") == orden for g in inicio for h in g.get("hooks", []))
if not ya:
    inicio.append({"hooks": [{"type": "command", "command": orden}]})
cfg.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
print("ya estaba" if ya else "registrado")
FIN
```

> 📌 **Va con el Python del sistema y no con el del lanzador**, porque el gancho usa solo la
> biblioteca estándar. Y queda junto al gancho `pendiente` de la bitácora (A3); los dos corren al
> iniciar y cada uno hace lo suyo.

**Sin reinicios:** el lanzador lee `calendario.json` cada vez que lanza una sesión, y Claude Code
lee `settings.json` al abrir cada sesión. Para apagar la revisión basta con borrar
`calendario.json`.

### B8c. Verificar

Primero que la configuración se lee y que la instrucción habla del cliente (deben imprimir
`True` y luego `False`):

```bash
cd ~/rc-launcher && .venv/bin/python -c "import calendario_sesion as c; t = c.instruccion_para_la_sesion('prueba'); print(t is not None); print('Gustavo' in t)"
```

> 🔴 **Si el segundo renglón imprime `True`, la copia del lanzador todavía le dice a la sesión
> que espere el sí de "Gustavo"**, que es el nombre de quien la construyó. En la máquina de otra
> persona eso confunde a la sesión y al cliente. Llevarle una copia corregida con B2b antes de
> entregar.

Luego que el gancho habla y que se calla con la marca del lanzador (el primero imprime un
renglón que empieza con `{"hookSpecificOutput"`, el segundo nada):

```bash
P='{"source":"startup","cwd":"'$HOME'/claude/<proyecto>"}'
echo "$P" | env -u RC_LANZADOR python3 ~/rc-launcher/aviso_arranque.py | head -c 60; echo
echo "$P" | RC_LANZADOR=1 python3 ~/rc-launcher/aviso_arranque.py | head -c 60; echo "(vacío arriba = correcto)"
```

Y la prueba completa, con el cliente enfrente:

1. Crear en su calendario un evento que empiece en 10 minutos, titulado
   `<proyecto> · Prueba de instalación`, con una descripción de una línea.
2. Desde el teléfono, lanzar una sesión nueva en ese proyecto. **La sesión debe resumir el
   evento y preguntar «¿Lo atendemos?»**, por su propia cuenta.
3. En la computadora, abrir `claude` directo en esa carpeta y escribir "hola". **Debe ofrecer el
   mismo evento.**
4. Borrar el evento de prueba.

### B8d. Lo que hay que decirle, y lo que cuesta

- **La convención del título:** *nombre de la carpeta del proyecto, un punto medio, y qué toca*,
  como `Marán · Carta al broker de LG`. Es con lo que la sesión decide de qué proyecto es el
  evento. El punto medio `·` sale en el teléfono dejando presionado el punto, y en la computadora
  vale copiarlo de un evento anterior.
- **Conviene ofrecerle un calendario aparte para el trabajo**, que puede compartir con su equipo
  o con su asistente sin enseñar lo personal. Es lo que usa Gustavo desde el 25 de septiembre de
  2026.
- **Los eventos de día completo se quedan fuera a propósito**: son cumpleaños, vacaciones y
  recordatorios, y ofrecerlos al arrancar estorbaría.
- **Cada sesión arranca con una consulta al calendario**, aunque no haya bloque. Es uso de su
  suscripción, pequeño, y se paga en cada arranque, igual que la de Drive en B7.

## 7. Verificación, en orden

> **Cómo se reparte por fases:** los renglones 1, 2, 3, 10, 10b, 11, 12, 12b y 13 cierran la **fase A**
> (el gitignore, la convención de pendientes, el servicio local, la bitácora, el runtime de
> documentos, los conectores, Composio y la cuenta de DeepInfra); del 4 al 9b, más el 14, el 15, el 16, el 17 y el 18,
> cierran la **fase B**, y necesitan el teléfono. Si solo se contrató la fase A, la verificación
> termina en el 13 y eso es una entrega completa.


Cada paso falla distinto, así que conviene hacerlos en orden y no saltarse ninguno.

| # | Qué | Cómo | Esperado |
|---|---|---|---|
| 1 | Gitignore global | `git config --global core.excludesFile` + `grep "salida/" ~/.config/git/ignore` | ruta + sin error |
| 2 | Convención de pendientes | `grep -q "pendientes.md" ~/.claude/CLAUDE.md` | encuentra la sección |
| 3 | El servicio vive | `systemctl is-active rc-launcher rc-watcher.timer` | `active` las dos |
| 4 | La app responde | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/salud` | `200` |
| 5 | La puerta cierra | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/` | **`403`** |
| 6 | Se ve desde el teléfono | abrir la URL de la tailnet | aparecen los proyectos |
| 7 | Lanza | tocar un proyecto → "Nueva sesión" | en 5 s el botón queda encendido y la sesión aparece en la app de Claude |
| 8 | Cierra | tocar el proyecto → "Terminar sesión" | desaparece de la app |
| 9 | Retoma | tocar un proyecto apagado | lista sus sesiones previas |
| 9b | El aviso llega | terminar una tarea desde el teléfono y esperar 3 minutos sin contestar | llega la notificación con el nombre del proyecto, y al tocarla abre esa sesión |
| 10 | La bitácora | ver el recuadro de abajo, que tiene truco | el `CLAUDE.md` de ese proyecto trae una entrada nueva |
| 10b | La bitácora trae lo del calendario | `grep -c "Google_Calendar" ~/.claude/hooks/bitacora.py` | **`6`**. Menos que eso es una copia vieja bajada en A3 |
| 11 | El runtime de documentos | las cinco pruebas de A4f | los cinco archivos salen bien, **con el Excel trayendo resultados y no celdas vacías** |
| 12 | Los conectores | `claude mcp list` | `claude.ai Gmail`, `Google Calendar` y `Google Drive` en `Connected` |
| 13 | La cuenta de DeepInfra (opcional) | `python3 ~/.claude/skills/whisper-deepinfra/whisper_deepinfra.py --estado` | `llave: CONFIGURADA` si el cliente ya la dio; `NO CONFIGURADA` es correcto si todavía no la necesita |
| 14 | El audio se escucha con un clic (solo si ya usó la voz sintética) | ver el recuadro de abajo | el navegador del teléfono lo **reproduce**, no lo descarga |
| 15 | Dejar dicho, y que la lista se quede quieta | ver el recuadro de abajo | el recado queda escrito en el `pendientes.md` con su `»`, y el menú sigue mostrando la misma tarea |
| 16 | El filtro rápido del mosaico | ver el recuadro de abajo | teclear parte de un nombre deja a la vista solo los que coinciden, y la ✕ devuelve el mosaico completo |
| 12b | Composio (opcional, A5e) | `composio search "send an email with an attachment" --toolkits gmail --limit 1` | regresa una herramienta de Gmail; si el cliente no lo contrató, se salta |
| 17 | Las transcripciones de Drive (opcional, B7) | los tres pasos de B7c | la sesión ofrece la de prueba al arrancar, y al procesarla queda en `transcripciones/` y en `Procesadas` |
| 18 | El bloque de calendario (opcional, B8) | los tres bloques de B8c | la instrucción imprime `True` y `False`, el gancho habla y se calla con la marca, y la sesión ofrece el evento de prueba desde el teléfono y desde `claude` directo |


> 📌 **Por qué el renglón del calendario mira el archivo y no el comportamiento.** Comprobar
> que el cierre de verdad toca un bloque exige cerrar una sesión que haya movido uno, y su
> respuesta normal cuando no hay nada que hacer es **quedarse callado**, o sea que un fallo
> se ve igual que un acierto. Lo que sí distingue una cosa de otra en un segundo es si el
> `bitacora.py` que quedó instalado trae las herramientas de calendario: si no las trae, el
> `curl` de A3 sirvió una copia vieja y esa mitad **nunca** va a funcionar.

> 📌 **Cómo se comprueba el renglón 14, y por qué no basta con que conteste 200.** El lanzador
> sirve lo que hay en `salida/` por `GET /audio/<proyecto>/<archivo>`. Lo que decide si el
> navegador lo toca o lo baja son tres cabeceras, así que se miran las tres:
>
> ```bash
> curl -sS -o /dev/null -D - "http://127.0.0.1:8765/audio/<proyecto>/<archivo>.mp3" \
>   -H "Tailscale-User-Login: <el correo del dueño de la tailnet>" \
>   | grep -i -E "^HTTP|content-type|content-disposition|accept-ranges"
> ```
>
> Esperado: `200`, `content-type: audio/mpeg`, `content-disposition: **inline**` (nunca
> `attachment`, que fuerza la descarga) y `accept-ranges: bytes`, que es lo que permite
> adelantar dentro de un audio largo. **La prueba de verdad es picarle a la liga desde el
> teléfono**, porque el comportamiento final lo decide su navegador.
>
> ⚠️ **Sin el encabezado de identidad contesta 403, y eso es correcto**, igual que el renglón
> 5. Desde el teléfono lo inyecta Tailscale solo. Es también lo que hace que esa liga **no
> sirva para compartirle el audio a un tercero**: para eso va el archivo adjunto.

> 📌 **Cómo se comprueba el renglón 15, que es de dos mitades.** La primera se mide desde la
> máquina: el menú de un proyecto con pendientes tiene que traer el ancla con la que el menú
> sabe a dónde volver, una por tarea.
>
> ```bash
> curl -s -H "Tailscale-User-Login: <el correo del dueño de la tailnet>" \
>   http://127.0.0.1:8765/menu/<proyecto> | grep -c "data-renglon="
> ```
>
> Un número mayor que cero es lo esperado. Un cero significa que ese proyecto tiene la lista
> vacía, así que hay que probar con uno que sí tenga tareas abiertas.
>
> **La segunda mitad es del teléfono, y es la que de verdad importa:** abrir un proyecto con
> una lista larga, bajar hasta una tarea del fondo, tocar "✎ Dejar retro", dictar algo y
> guardar. La tarea tiene que quedarse **a la misma altura de la pantalla**, con lo dictado ya
> pintado debajo de ella. Si la vista salta al primer pendiente, esa copia del lanzador es
> anterior al 13 de agosto de 2026.
>
> ⚠️ **La `»` con la que se guarda una retro significa "esto lo dictó el dueño de la máquina",
> y es permanente.** Al probarlo se escribe en su archivo de verdad: hacerlo en un proyecto de
> prueba, o avisarle que ese renglón se queda.

> 📌 **Cómo se comprueba el renglón 16, y desde dónde se corre.** Hay un guion que lo mide
> completo, y **corre en la máquina de quien instala, apuntada a la del cliente por la
> tailnet**: usa Playwright, que esta instalación deja fuera a propósito. Viaja dentro de la
> copia del lanzador que trajiste, así que ya lo tienes.
>
> ```bash
> ORIGEN=/ruta/a/tu/copia/de/rc-launcher      # la misma de B2
>
> RC_BASE=https://<la-maquina>.<tu-tailnet>.ts.net \
>   node "$ORIGEN"/docs/superpowers/verificacion/2026-08-17-filtro-rapido-de-proyectos.js
> ```
>
> Son **14 comprobaciones** a 390 px de ancho, que es un teléfono, y deja una captura en
> `/tmp/filtro-390.png` para verlo con los ojos. ✅ **El guion solo lee el mosaico y teclea en un
> campo**, así que se puede correr contra una máquina en uso: al revés del renglón 15, aquí queda
> cero rastro en los archivos del cliente.
>
> 🔴 **Dos ajustes antes de la primera corrida, y los dos fallan señalando el lugar equivocado:**
>
> - **El correo de la identidad va escrito dentro del guion** (`Tailscale-User-Login`, en las
>   primeras líneas). Con el correo de otra tailnet el lanzador contesta 403 y el guion se queda
>   esperando un mosaico que jamás llega. Va el correo del dueño de la tailnet del cliente.
> - **Pide al menos 4 proyectos para significar algo.** Con uno o dos, "filtrar recorta la lista"
>   pasa en verde por vacuidad, y eso se lee como si el filtro estuviera roto. El guion **para y lo
>   dice con palabras**, saliendo con código 2 en vez de reportar fallas falsas. Una instalación
>   recién hecha suele estar justo ahí: sembrar unas carpetas con su `CLAUDE.md` bajo la raíz de
>   proyectos, que además la deja más parecida a una máquina en uso.
>
> **Y la mitad del dedo, que es la que el cliente va a vivir:** desde el teléfono, teclear parte de
> un nombre, ver que los encabezados de Activos y Fijados se esconden y queda una sola rejilla,
> **esperar los 8 segundos del redibujado** y comprobar que lo tecleado y el recorte siguen ahí.
> Si a los 8 segundos reaparecen los proyectos escondidos, o vuelve el botón de "+ Nuevo proyecto",
> esa copia del lanzador es anterior al 17 de agosto de 2026.

> ⚠️ **La prueba de la bitácora hay que pedirla bien o parece rota.** El umbral cuenta
> **llamadas de herramienta, no archivos**: pedir "crea seis archivos" lo resuelve un
> asistente con **un solo comando de Bash**, o sea una sola llamada, y el mecanismo se calla
> con razón. Pedirlo así: *"usa la herramienta Write seis veces seguidas, una por archivo,
> sin Bash ni heredocs"*. Y **leer los conteos de uno en uno**
> (`for f in ~/.cache/claude-bitacora/*.conteo; do echo "$f = $(cat $f)"; done`): un `cat`
> con comodín concatena los de varias sesiones y un "1" y un "3" se leen como "13".
>
> Cuando sí dispara, el conteo **vuelve a cero** al terminar. No es que se haya perdido: es
> la guarda que evita el bucle de reescribir la bitácora para callar una alarma que la
> propia escritura vuelve a encender. Lo que hay que mirar es el tamaño del `CLAUDE.md`.

> ⚠️ **El 403 del renglón 5 es la respuesta correcta, no una falla.** La raíz exige la
> identidad que inyecta Tailscale (`Tailscale-User-Login`), que por `curl` desde la propia
> máquina no existe. **Usar `/salud` para medir salud, nunca la raíz.**

**Si el teléfono dice que no carga:** revisar **primero el Tailscale del teléfono**, que es
la causa más probable y la más barata de descartar. Después, de más barato a más caro:
`tailscale status` debe listar el teléfono, `tailscale dns status` debe traer MagicDNS
encendido, y `tailscale serve status` debe mostrar la publicación del paso 5.

**Dónde mirar cuando la bitácora no cuadra:** todo vive en `~/.cache/claude-bitacora/`.
`cierres.log` es el canal de estado, con una línea por evento, y distingue "no había nada
que hacer" de "lo intenté y falló". `escritor-<sid>.log` es la transcripción completa de
la sesión que escribió esa bitácora.

> ⚠️ **`rc=0` no significa que se haya escrito.** Verificar siempre el archivo, no el
> código de salida.

## 8. Lo que NO resuelve esta instalación


Decirlo antes de instalarla en casa de alguien más:

- **Quien alcance el lanzador puede lanzar sesiones con acceso completo al disco de esa
  persona.** Es el permiso más fuerte de todo el montaje. La puerta es la identidad de
  Tailscale, y `~/.config/rc-launcher/acceso.json` extiende la lista de quién entra.
- **Si la máquina se apaga, no hay lanzador.** Es una condición del montaje.
- **La bitácora la escribe un modelo**, así que consume tokens de la cuenta de esa persona
  cada vez que cierra una sesión con trabajo pendiente.
- **Depende de cosas que no controlamos.** Si la empresa bloquea Tailscale, no hay rodeo
  técnico. El paso 0 existe para descubrirlo antes de la cita, no durante.
- **La tailnet queda a nombre suyo**, o sea que él administra sus interruptores. Es
  deliberado, pero significa que un cambio suyo puede tumbar el acceso sin que nos
  enteremos.
- **Un proyecto cuya carpeta se renombre con la sesión viva** desaparece del grid y esa
  sesión queda inmatable desde el teléfono. Se cierra con `tmux kill-session` a mano.

## Errores comunes


| Síntoma | Causa real |
|---|---|
| `claude: command not found` desde el servicio | Falta `Environment=PATH=` con `~/.local/bin` en la unidad |
| Reiniciar el servicio mata todas las sesiones | Falta `KillMode=process` |
| La raíz da 403 y parece roto | Es correcto sin identidad de Tailscale; medir con `/salud` |
| El teléfono no abre la página | Tailscale del teléfono apagado, o MagicDNS apagado en la consola |
| La primera sesión se queda colgada | Claude Code no pasó por su primer arranque; está detenido en una de las cinco preguntas, sin ventana donde verlas. Ver A2 |
| Un proyecto nuevo se cuelga la primera vez, incluso con la raíz confiada | Si pasa con TODOS los proyectos nuevos: la confianza se aceptó dentro de un proyecto y no en la raíz `~/claude`, no se hereda (ver A2). Si es solo el primero de un proyecto creado desde "+ Nuevo proyecto": es normal, contestar desde el teléfono o adelantarlo abriendo la primera sesión desde la computadora (ver B2) |
| Un proyecto que llevaba meses trabajando empieza a pedir la confianza | Le corrieron `git init`, y la herencia se corta en la raíz de cada repositorio. El flag de permisos omitidos tampoco lo salta. Se siembra la llave con el fragmento de A2 |
| Se le pidió a un agente que hiciera el primer arranque y se quedó a medias | A2 no se puede delegar; exige a una persona con la sesión al frente, sobre todo para la pregunta 4. Ver A2 |
| Aparece "acepta toda la responsabilidad" y nadie sabe si contestar | Es la pregunta 4 de A2 (modo sin confirmaciones); solo la acepta el dueño de la máquina, en persona. Ver A2 |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| "Le pedí la bandeja y me habló de Gmail" | Falta la sección "La bandeja" de B5 en `~/.claude/CLAUDE.md` |
| "Le pedí sus pendientes y no sabe qué son" | Falta la sección de A7 en `~/.claude/CLAUDE.md` |
| Los conectores no aparecen en `/mcp` | La sesión no está autenticada con la suscripción. Correr `/status`. Ver A5b |
| No deja conectar Gmail desde `/mcp` | Es lo esperado: va en claude.ai, no en la terminal. Ver A5a |
| El borrador salió sin el archivo adjunto | Limitación vigente del conector; se adjunta a mano antes de enviar. Ver A5c |
| Pide una llave de DeepInfra que el cliente no esperaba | No se le explicó A8 en la entrega. Es opcional y con su propia cuenta; explicarle y seguir cuando la tenga |
| La misma transcripción se ofrece en cada sesión | No se movió a `Procesadas`: la subcarpeta falta, se llama distinto, o el conector no completó el movimiento. Ver B7c |
| Hay transcripciones en Drive y la sesión arranca sin mencionarlas | La sesión se abrió a mano y falta el gancho de B8b, falta `transcripciones.json`, o la copia del lanzador es anterior al 22 de septiembre de 2026. Ver B7 |
| Hay un bloque en curso y la sesión arranca sin ofrecerlo | A la sesión le falta una vía al calendario (ver B8a), falta `calendario.json`, el título del evento no empieza con el nombre de la carpeta seguido de `·`, el evento es de día completo, o la copia del lanzador es anterior al 25 de septiembre de 2026. Ver B8 |
| La sesión espera el sí de "Gustavo" | La copia del lanzador trae el nombre fijo en la instrucción. Llevarle una corregida con B2b. Ver B8c |
| `unzip is required to install Composio CLI` | Falta `unzip`; está en A1 |
| `Cannot find module 'docx'` o `'pptxgenjs'` | Falta `NODE_PATH`. Están instalados global, pero `require()` no los ve desde otra carpeta. Ver A4d |
| `Could not load the "sharp" module` | Node 18 de los repos de Ubuntu. `sharp` pide 20.9 o mayor. Ver A4b |
| `externally-managed-environment` al instalar con pip | Falta `--user --break-system-packages`. Ver A4c |
| El Excel sale con las celdas de resultado vacías | Falta LibreOffice, o no se pasó por `recalc.py`. `openpyxl` escribe la fórmula pero no la evalúa. Ver A4f |
| El OCR devuelve basura en un documento en español | Falta `tesseract-ocr-spa`; el paquete base solo trae inglés. Ver A4a |
| `presentacion-elegante` no produce nada útil | Falta el plugin `document-skills`; la skill no tiene a qué delegar. Ver A4e |
