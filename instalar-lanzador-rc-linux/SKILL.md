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
| Subir archivos desde el teléfono | Caen en `bandeja/` dentro del proyecto |
| **La bitácora se escribe sola** | Al cerrar, el `CLAUDE.md` del proyecto queda actualizado sin pedirlo, y su `pendientes.md` también (se crea solo si hubo trabajo abierto) |
| **Documentos de oficina de verdad** | Pide un Word, un Excel con fórmulas o una presentación y salen archivos que abren en Office |
| **Su correo, su calendario y su Drive** | Pregunta qué le escribieron o pide que le agenden algo, y se resuelve sin salir de la conversación |
| **Sus pendientes por proyecto** | Ve qué falta y palomea lo hecho, desde la computadora o desde el teléfono |
| **Transcribir juntas y escuchar documentos** (opcional, con cuenta propia) | Sube la grabación de una junta y pide la minuta, o pide que le lean un documento para el camino |

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
sudo apt-get install -y python3-venv python3-pip tmux git curl
curl -fsSL https://claude.ai/install.sh | bash
```

| Pieza | Verificar | Si la verificación falla |
|---|---|---|
| Python con venv | `python3 -m venv --help` | En Debian el módulo va aparte: es el paquete `python3-venv` |
| tmux | `tmux -V` | Es la capa de sesión del lanzador en Linux; sin él no lanza nada |
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

```bash
mkdir -p ~/.claude/hooks
cp <origen>/bitacora/bitacora.py ~/.claude/hooks/bitacora.py
chmod +x ~/.claude/hooks/bitacora.py
```

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
- **Sin identificadores** en el renglón (nada de `id: 4f2a`): el archivo se tiene que poder
  leer y editar a mano.
- Quien palomea agrega ` ✓ AAAA-MM-DD HH:MM` al final, con hora local. Al despalomear se
  quita.
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
> renglones `[x]` ni `[-]`.** Son un registro que creaste con el dedo; una reescritura que se
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


```bash
# el código va al home, no a una ruta de sistema
rsync -a --exclude .venv --exclude __pycache__ --exclude .git \
      <origen>/rc-launcher/ ~/rc-launcher/

cd ~/rc-launcher
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

mkdir -p ~/claude          # la raíz de proyectos, que es donde vive el trabajo
```

`~/claude` no es negociable sin tocar código: `sessions.py` la calcula como
`Path.home() / "claude"`. Si los proyectos viven en otro disco, poner un symlink ahí.

**Comprobar antes de seguir**, porque si esto falla, nada de lo demás importa:

```bash
cd ~/rc-launcher && .venv/bin/python -m pytest -q
```

Debe pasar la suite completa. En la VM limpia pasaron 327 de 327 en medio segundo, sin
tocar una línea, que es la prueba de que el código no depende de la máquina donde nació.

> 📌 **Si el proyecto ya tiene `pendientes.md` (A7), el lanzador ya lo pinta y lo palomea
> con el dedo, sin configuración adicional.** No hay ningún paso extra que hacer aquí.

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

## 7. Verificación, en orden

> **Cómo se reparte por fases:** los renglones 1, 2, 3, 10, 11, 12 y 13 cierran la **fase A**
> (el gitignore, la convención de pendientes, el servicio local, la bitácora, el runtime de
> documentos, los conectores y la cuenta de DeepInfra); del 4 al 9 cierran la **fase B**, y
> necesitan el teléfono. Si solo se contrató la fase A, la verificación termina en el 13 y eso
> es una entrega completa.


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
| 10 | La bitácora | ver el recuadro de abajo, que tiene truco | el `CLAUDE.md` de ese proyecto trae una entrada nueva |
| 11 | El runtime de documentos | las cinco pruebas de A4f | los cinco archivos salen bien, **con el Excel trayendo resultados y no celdas vacías** |
| 12 | Los conectores | `claude mcp list` | `claude.ai Gmail`, `Google Calendar` y `Google Drive` en `Connected` |
| 13 | La cuenta de DeepInfra (opcional) | `python3 ~/.claude/skills/whisper-deepinfra/whisper_deepinfra.py --estado` | `llave: CONFIGURADA` si el cliente ya la dio; `NO CONFIGURADA` es correcto si todavía no la necesita |

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
| Se le pidió a un agente que hiciera el primer arranque y se quedó a medias | A2 no se puede delegar; exige a una persona con la sesión al frente, sobre todo para la pregunta 4. Ver A2 |
| Aparece "acepta toda la responsabilidad" y nadie sabe si contestar | Es la pregunta 4 de A2 (modo sin confirmaciones); solo la acepta el dueño de la máquina, en persona. Ver A2 |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| "Le pedí la bandeja y me habló de Gmail" | Falta la sección "La bandeja" de B5 en `~/.claude/CLAUDE.md` |
| "Le pedí sus pendientes y no sabe qué son" | Falta la sección de A7 en `~/.claude/CLAUDE.md` |
| Los conectores no aparecen en `/mcp` | La sesión no está autenticada con la suscripción. Correr `/status`. Ver A5b |
| No deja conectar Gmail desde `/mcp` | Es lo esperado: va en claude.ai, no en la terminal. Ver A5a |
| El borrador salió sin el archivo adjunto | Limitación vigente del conector; se adjunta a mano antes de enviar. Ver A5c |
| Pide una llave de DeepInfra que el cliente no esperaba | No se le explicó A8 en la entrega. Es opcional y con su propia cuenta; explicarle y seguir cuando la tenga |
| `Cannot find module 'docx'` o `'pptxgenjs'` | Falta `NODE_PATH`. Están instalados global, pero `require()` no los ve desde otra carpeta. Ver A4d |
| `Could not load the "sharp" module` | Node 18 de los repos de Ubuntu. `sharp` pide 20.9 o mayor. Ver A4b |
| `externally-managed-environment` al instalar con pip | Falta `--user --break-system-packages`. Ver A4c |
| El Excel sale con las celdas de resultado vacías | Falta LibreOffice, o no se pasó por `recalc.py`. `openpyxl` escribe la fórmula pero no la evalúa. Ver A4f |
| El OCR devuelve basura en un documento en español | Falta `tesseract-ocr-spa`; el paquete base solo trae inglés. Ver A4a |
| `presentacion-elegante` no produce nada útil | Falta el plugin `document-skills`; la skill no tiene a qué delegar. Ver A4e |
