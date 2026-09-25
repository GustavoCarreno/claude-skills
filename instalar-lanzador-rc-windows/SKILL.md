---
name: instalar-lanzador-rc-windows
description: Activar cuando alguien pida instalar, montar o configurar el lanzador rc (rc-launcher) en una laptop o PC con Windows, o dejar lista una máquina Windows para lanzar sesiones de Claude Code desde el teléfono. También cuando pida el lanzador web, la bitácora automática que actualiza CLAUDE.md sola, o publicar el lanzador en su tailnet de Tailscale. Cubre Windows 10 22H2 y Windows 11 con winget.
---

# Instalar el lanzador rc y la bitácora automática en Windows

Deja una laptop con Windows lista para lanzar, retomar y cerrar sesiones de Claude Code
desde el teléfono, y para que el `CLAUDE.md` de cada proyecto se escriba solo al cerrar
cada sesión.

**Procedimiento verificado de punta a punta en la VM `win11-dogfood` la madrugada del 3 de
agosto de 2026.** Para Linux existe el equivalente en `instalar-lanzador-rc-linux`, y ese
está verificado más recientemente.

> ⚠️ **Qué está verificado y qué no, porque importa antes de pararse enfrente de un
> cliente.** Los pasos 0 a 7 se corrieron completos en Windows. Lo que se agregó **después**
> de esa verificación, y **solo está probado en Linux**, es la sección **1b** (las cinco
> preguntas de primer arranque de Claude Code) y la nota de autenticación de la sección 8.
> Son de Claude Code y no del sistema operativo, así que aplican igual, pero **la primera vez
> que se use esta guía en Windows conviene confirmarlas** y corregir aquí lo que salga
> distinto.
>
> **La sección A4 se corrió en Windows el 3 de agosto**, con dos matices que conviene tener
> presentes: los seis IDs de `winget` están **verificados uno por uno**, pero **Node y
> `yt-dlp` ya estaban instalados en esa VM**, así que su instalación no se ejercitó desde
> cero. Todo lo demás de A4 (LibreOffice, Pandoc, Tesseract con su español, Poppler, los
> paquetes de Python y npm, el `NODE_PATH`, el plugin y las cinco pruebas de aceptación) se
> instaló y se probó ahí. **La prueba 5 pasó**: una sesión real generó una presentación
> ejecutiva de cuatro láminas y corrió **tres pasadas de revisión visual** (16 defectos, luego
> 4, luego cero, con medición de píxeles). Es la evidencia de que el camino de A4f funciona
> de verdad y no solo en el papel.

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
| **Dejar dicho qué resultó, sin abrir sesión** (requiere la fase B) | Desde el teléfono, en cada pendiente hay un botón para dictar cómo quedó, y una sección aparte para los recados sueltos del proyecto, los que valen por sí mismos. Se dicta con el teclado del teléfono, así que cuesta cero llamadas al modelo, y la siguiente sesión se entera sola de que hay algo sin leer. **La lista se queda donde estaba al guardar**, para poder recorrerla de corrido |
| **Las transcripciones de sus grabaciones llegan solas** (opcional, requiere la fase B) | Al abrir una sesión desde el teléfono, el asistente revisa la carpeta de Drive donde caen las transcripciones, le dice en un renglón cuáles son de ese proyecto y pregunta si las procesa. Con un sí, quedan guardadas en el proyecto y lo que salga de ellas llega a sus pendientes |
| **La sesión le ofrece el bloque de su agenda** (opcional, requiere la fase B) | Si reservó en el calendario un bloque para ese proyecto y está en curso o empieza en media hora, la sesión se lo resume en dos renglones al abrir y pregunta si lo atienden. Pasa igual si abre la sesión desde el teléfono o en la computadora |

## Antes de empezar


- **La laptop tiene que quedar encendida y con la sesión de Windows iniciada.** No es un
  detalle: si se reinicia de noche y nadie entra, el lanzador deja de existir para el
  teléfono. Ver el paso 4 para lo que sí se puede mitigar y lo que no.
- **Esta guía no supone nada instalado.** Instala Claude Code, Python, Tailscale y levanta la
  red desde cero. Lo único que hay que traer de antemano es una cuenta de Anthropic con un
  plan que incluya Claude Code, y eso se resuelve en el paso 0.
- **Hace falta el teléfono a la mano.** No es opcional ni "para después": es la mitad del
  montaje, y hay pasos que solo se pueden hacer ahí.

## 0. Descarte previo, cinco minutos antes de instalar nada


Sirve para saber si la laptop siquiera es candidata. **Hacerlo antes de sentarse con el
cliente.** Descubrir en el paso 1 que su empresa bloquea las instalaciones es una hora
perdida y una mala primera impresión.

| Revisar | Cómo | Si falla |
|---|---|---|
| Windows 10 (22H2 o más) u 11 | `winver` | En Windows más viejo no hay `winget`; la instalación se vuelve manual y no está cubierta aquí |
| `winget` existe | `winget --version` | Instalar "App Installer" desde la Microsoft Store |
| Permisos de administrador | `net session` en PowerShell normal: si contesta sin error, hay permisos elevados | Sin administrador no se instalan Tailscale ni la tarea programada. **Aquí se para la instalación** hasta que Sistemas dé permisos o dé otra máquina |
| Sin MDM que bloquee | Preguntar, y probar `winget install --id Python.Python.3.12 --silent` | Muchas laptops corporativas bloquean instalaciones globales, servicios sin firmar o clientes de VPN. Es el bloqueo más común y **no tiene rodeo técnico**: hay que hablar con su departamento de Sistemas |
| Cuenta de Anthropic | Iniciar sesión en `claude.ai` | Sin un plan que incluya Claude Code no hay nada que instalar |
| El correo del cliente permite apps de terceros | que **él mismo** entre a `claude.ai/customize/connectors` e intente conectar su calendario | Si su administrador de Google Workspace o Microsoft 365 tiene bloqueadas las apps de terceros, **no hay rodeo técnico**: es conversación con su área de sistemas. Descubrirlo aquí cuesta un minuto; descubrirlo en la cita cuesta la sesión |

> ⚠️ **Los seis renglones dependen de la empresa del cliente, no de nosotros.** Si alguno
> truena, el problema es de gestión, no técnico, y conviene plantearlo así desde el principio
> en vez de intentar rodearlo.

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


| Pieza | Cómo | Verificar |
|---|---|---|
| Claude Code | instalador nativo, ver abajo | `claude --version` |
| Python 3.12 | `winget install --id Python.Python.3.12 --silent` | `python --version` |
| Dependencias | `python -m pip install pywinpty flask waitress` | `python -c "import winpty"` |
| Tailscale | instalador de `tailscale.com/download/windows` | `tailscale status` |

> ⚠️ **`winget` deja el PATH desactualizado en la consola en curso.** Después de instalar,
> **abrir una consola nueva** o el siguiente comando dirá que el programa no existe. Es la
> causa más común de "no me funcionó el paso 1".

> ⚠️ **Si `python` abre la Microsoft Store en vez de correr**, desactivar los alias de
> ejecución de Python en Configuración → Aplicaciones → Alias de ejecución de aplicaciones.

> ⚠️ **`pywinpty` es lo que hace que el cierre desde el teléfono funcione.** Trae binarios;
> si falla la compilación, actualizar `pip` primero. Sin él, la sesión se cierra a medias y
> sigue apareciendo conectada en la app.

## A2. El primer arranque de Claude Code, que es donde más gente se atora


> 🔴 **Este paso decide si el lanzador sirve o no, y es invisible cuando falla.** Claude Code
> recién instalado hace **cinco preguntas de primer arranque**. Una sesión lanzada desde el
> teléfono se queda detenida en la primera de ellas **sin señal de nada**: el botón se
> enciende, la sesión existe, y del otro lado no hay más que un cursor.

> 🔴 **Este paso completo lo tiene que correr una persona con la sesión al frente — no se
> puede delegar a un agente ni a un asistente que actúe en tu nombre.** Es el mismo patrón
> que explica el tropiezo de la pregunta 4, más abajo: de aquí en adelante la guía asume que
> quien instala tiene consola y permisos plenos sobre la máquina. Confirmar la identidad al
> iniciar sesión, marcar la carpeta como confiable y, sobre todo, aceptar el modo sin
> confirmaciones son exactamente las acciones que esas preguntas existen para proteger — un
> agente al que se le delegue esta tarea no tiene esos permisos, y no es un error de la
> instalación: es el diseño funcionando. Para todo lo demás de esta guía sí se puede pedir
> ayuda; para esto, no.

**La receta corta: correr `claude` una vez a mano parado en la raíz de proyectos** y
contestar las cinco. No dentro de un proyecto, **en la raíz**, por lo del renglón 3.

```powershell
cd $env:USERPROFILE\claude
claude          # contestar las cinco, luego /exit
```

| # | Pregunta | Qué escribe |
|---|---|---|
| 1 | Tema de color | `theme` en `%USERPROFILE%\.claude\settings.json` |
| 2 | Método de inicio de sesión | la cuenta en `%USERPROFILE%\.claude.json` |
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
> en la raíz de proyectos.** Si se contesta dentro de un proyecto, **cada proyecto nuevo que
> se cree desde el teléfono se vuelve a atorar** en esa misma pregunta, invisible otra vez.
> Verificado en Linux, en las dos direcciones: con solo un proyecto confiado, uno nuevo se
> detuvo; con la raíz confiada, uno recién creado arrancó directo al prompt.

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

```powershell
@'
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
'@ | Set-Content -Encoding UTF8 "$env:TEMP\confiar.py"

python "$env:TEMP\confiar.py"
```

> ⚠️ **Las rutas van con barra diagonal aunque Windows use contrabarra en todo lo demás**, y ya
> resueltas. La llave se compara como texto, así que una forma distinta de la misma ruta deja la
> bandera al lado de la llave que se lee **y el diálogo sigue saliendo igual**. Por eso el
> fragmento lleva el `resolve()` y la sustitución.

> ⚠️ **Correrlo con las sesiones de Claude Code cerradas.** Ese archivo lo comparte Claude Code
> entero y lo reescribe al salir, así que una sesión abierta puede pisar la siembra sin avisar.

> 📌 **Y para los proyectos que nazcan después**, el mismo fragmento sirve tal cual, o se le pide
> al asistente que lo corra. Lo que jamás hace falta es contestar la pregunta a mano en cada uno.

## A3. La bitácora automática


Al cerrar la sesión también atiende el `pendientes.md` del proyecto (A7), y puede crearlo si
de la sesión salió trabajo abierto. Un único archivo de Python, biblioteca estándar, **el
mismo que corre en Linux**.

> 📌 **El cierre también pone al día el calendario, y eso depende de A5.** La sesión que
> escribe la bitácora corre con una **lista cerrada** de herramientas, y las de Google
> Calendar vienen dentro. Si el cliente no conectó su calendario en A5, el cierre
> sencillamente no lo menciona y todo lo demás funciona igual. **Si está en Microsoft 365
> sus herramientas se llaman distinto y no están en la lista**, así que esa mitad se queda
> muda hasta que se extienda con la clave `herramientas` de abajo. Qué hace y qué nunca
> hace con el calendario está en A7.

```powershell
$hooks = "$env:USERPROFILE\.claude\hooks"
New-Item -ItemType Directory -Force -Path $hooks
Invoke-WebRequest -UseBasicParsing `
  -Uri "https://raw.githubusercontent.com/GustavoCarreno/claude-skills/main/bitacora/bitacora.py" `
  -OutFile "$hooks\bitacora.py"
```

> 💡 **Si ya clonaste el repo `claude-skills`** (en vez del one-liner de instalación, que
> lo clona a un temporal y lo borra), cópialo de ahí en su lugar:
> `Copy-Item <carpeta-del-clon>\bitacora\bitacora.py "$hooks\bitacora.py"`.

**Comprobar que llegó completo antes de seguir** — una descarga a medias es justo el
modo de fallar silencioso que este mecanismo no puede tener:

```powershell
(Get-Item "$hooks\bitacora.py").Length   # debe rondar los 30 KB, no 0
'' | python "$hooks\bitacora.py" pendiente
"código de salida: $LASTEXITCODE"
```

Si el tamaño sale en 0 o vacío, la descarga falló; si el `python` truena con una traza
en vez de terminar limpio, el archivo llegó corrupto o incompleto.

Configuración en `%USERPROFILE%\.claude\bitacora.json`:

```json
{ "raiz_proyectos": "C:/Users/<usuario>/claude", "umbral": 6, "max_recordatorios": 2 }
```

- **`raiz_proyectos`** con barras diagonales. Si apunta mal, el mecanismo **no dispara y no
  avisa**: su modo de fallar es el silencio.
- **`umbral`**: llamadas de herramienta antes de considerar que hay algo que registrar.
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

Los cuatro hooks van en `%USERPROFILE%\.claude\settings.json`, dentro de `"hooks"`,
sustituyendo `<python>` y `<usuario>`:

```json
{
  "hooks": {
    "PostToolUse": [{ "matcher": "Write|Edit|NotebookEdit|Bash",
      "hooks": [{ "type": "command", "command": "\"<python>\" \"C:\\Users\\<usuario>\\.claude\\hooks\\bitacora.py\" marcar" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "\"<python>\" \"C:\\Users\\<usuario>\\.claude\\hooks\\bitacora.py\" verificar" }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "\"<python>\" \"C:\\Users\\<usuario>\\.claude\\hooks\\bitacora.py\" cerrar" }] }],
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "\"<python>\" \"C:\\Users\\<usuario>\\.claude\\hooks\\bitacora.py\" pendiente" }] }]
  }
}
```

> ⚠️ **Si `settings.json` ya existe, fusionar, no sobrescribir.** El primer arranque del paso
> 1b ya escribió cosas ahí.

---

## A4. El runtime que las skills dan por hecho


**Este paso existe porque las skills que se entregan instaladas no traen lo que
necesitan para correr.** Se instalan con un comando y eso es gratis, pero por dentro
asumen un runtime que solo viene preinstalado en el entorno de Anthropic. En una laptop
recién comprada no hay nada de eso, y **falla tarde, ya con la persona esperando su
documento**.

Lo concreto: `presentacion-elegante` envuelve a `document-skills:pptx`, y su ciclo de
revisión visual necesita LibreOffice y Poppler. `youtube-research` necesita `yt-dlp` y
`ffmpeg`. Sin A4, esas skills aparecen en la lista y no funcionan.

**Son dos capas:** el plugin `document-skills` (que trae las skills y sus scripts) y el
runtime del sistema (que esos scripts invocan). Instalar solo la primera no sirve de nada.

> ✅ **Poppler sí existe para Windows y está en `winget`.** Es `oschwartz10612.Poppler`, la
> compilación que la propia documentación de `pdf2image` recomienda. **No hace falta aceptar
> ninguna degradación del ciclo de revisión visual**, que era la duda abierta antes de
> medirlo en la VM.

### A4a. Todo lo que sale de winget

```powershell
$ids = @(
  "TheDocumentFoundation.LibreOffice",
  "JohnMacFarlane.Pandoc",
  "tesseract-ocr.tesseract",
  "oschwartz10612.Poppler",
  "OpenJS.NodeJS",
  "yt-dlp.yt-dlp"
)
foreach ($id in $ids) {
  winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
}
```

**IDs verificados en la VM**, no supuestos. Dos notas sobre elecciones que no son obvias:

- **`tesseract-ocr.tesseract` es el oficial y va en 5.5**, más nuevo que el de UB Mannheim
  (`UB-Mannheim.TesseractOCR`, en 5.4). Cualquiera de los dos sirve; se prefiere el oficial.
- **`yt-dlp.yt-dlp` arrastra `ffmpeg` como dependencia**, así que no hay que instalarlo
  aparte. Es el que necesita `youtube-research`.

> ⚠️ **`winget` deja el PATH viejo en la consola en curso**, el mismo aviso de A1. Abrir una
> consola nueva antes de verificar nada de aquí.

### A4b. Los dos que NO se registran solos en el PATH

**Medido en la VM: LibreOffice y Tesseract se instalan en `Program Files` y no se agregan
al PATH.** Poppler y Pandoc sí lo hacen. Como las skills los invocan por nombre, sin esto
fallan con "no se reconoce el comando":

```powershell
$agregar = @("C:\Program Files\LibreOffice\program", "C:\Program Files\Tesseract-OCR")
$actual = [Environment]::GetEnvironmentVariable("Path", "User")
foreach ($d in $agregar) {
  if ((Test-Path $d) -and ($actual -notlike "*$d*")) { $actual = $actual.TrimEnd(";") + ";" + $d }
}
[Environment]::SetEnvironmentVariable("Path", $actual, "User")
```

### A4c. El español de Tesseract, que no viene incluido

**El paquete instala solo `eng` y `osd`.** Sin esto, el OCR de un documento en español
devuelve basura en vez de fallar, que es peor porque nadie lo nota:

```powershell
Invoke-WebRequest -UseBasicParsing `
  -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata" `
  -OutFile "C:\Program Files\Tesseract-OCR\tessdata\spa.traineddata"
```

Son unos 18 MB. Verificar con `tesseract --list-langs`, tiene que aparecer `spa`.

### A4d. Los paquetes de lenguaje

```powershell
python -m pip install openpyxl pandas "markitdown[pptx]" Pillow defusedxml lxml `
                     pytesseract pdf2image pypdf pdfplumber reportlab

npm install -g docx pptxgenjs react react-dom react-icons sharp

# require() no resuelve paquetes npm globales desde una carpeta cualquiera
[Environment]::SetEnvironmentVariable("NODE_PATH", (npm root -g).Trim(), "User")
```

> 📌 **En Windows `pip install` a secas sí funciona.** No aplica el
> `externally-managed-environment` (PEP 668) que obliga a `--break-system-packages` en
> Ubuntu 24.04, así que el comando es más corto que el de Linux. Es de las pocas cosas que
> aquí salen más fáciles.

> ⚠️ **`NODE_PATH` no es opcional.** `docx` y `pptxgenjs` quedan instalados global, pero las
> skills corren sus scripts desde el proyecto de quien las usa, y desde ahí `require()` no
> los encuentra. Verificar en una consola nueva, **parado en otra carpeta**:
> `cd $env:TEMP; node -e "require('docx'); require('sharp'); console.log('OK')"`.

### A4e. El plugin de documentos

```powershell
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin list          # debe decir "enabled"
```

### A4f. Lo que hay que hacer distinto que en Linux

> ⚠️ **Los scripts auxiliares del plugin NO corren en Windows, y hay que saberlo antes de
> seguir su documentación al pie de la letra.** `xlsx/scripts/recalc.py` y
> `pptx/scripts/thumbnail.py` fallan con
> `module 'socket' has no attribute 'AF_UNIX'`, porque los dos pasan por
> `pptx/scripts/office/soffice.py`, que es un shim pensado para el entorno aislado de
> Anthropic (detecta sockets de dominio Unix bloqueados y compila un `.so` para rodearlos).
> Nada de eso existe en Windows.
>
> **La buena noticia es que ahí ese shim no hace falta para nada: `soffice` directo
> funciona.** Donde la documentación del plugin diga
> `python scripts/office/soffice.py ...`, en Windows va `soffice` a secas.
> (`pptx/scripts/clean.py` sí corre, porque no toca LibreOffice.)

```powershell
# Recalcular un Excel (el equivalente de recalc.py)
soffice --headless --convert-to xlsx --outdir recalculado archivo.xlsx

# Revisión visual de una presentación (el equivalente de thumbnail.py)
soffice --headless --convert-to pdf --outdir rev archivo.pptx
pdftoppm -jpeg -r 150 rev\archivo.pdf rev\diapo
```

> 📌 **`soffice.exe` sí espera a terminar en Windows**, o sea que el archivo ya existe
> cuando el comando regresa y no hace falta meter una espera artificial. Se comprobó
> revisando el archivo inmediatamente después. `soffice.com` se comporta igual.

### A4g. Las cinco pruebas de aceptación

**No dar A4 por terminado sin correrlas.** Cada una revienta por una pieza distinta.

| # | Prueba | Qué pieza demuestra |
|---|---|---|
| 1 | Generar un `.docx` y convertirlo a PDF | npm `docx` más `soffice` |
| 2 | Generar un `.xlsx` **con una fórmula y leer su resultado** | LibreOffice recalculando |
| 3 | Generar un `.pptx` y sacarle la imagen de revisión | `pptxgenjs`, `sharp`, `soffice`, `pdftoppm` |
| 4 | Leer un PDF escaneado con OCR | Tesseract con el español de A4c |
| 5 | Correr `presentacion-elegante` de punta a punta | Que todo lo anterior esté bien cableado |

> ⚠️ **La prueba 2 es la filosa y hay que leerla bien.** `openpyxl` escribe la fórmula pero
> **no la evalúa**, así que sin LibreOffice el archivo sale con las celdas de resultado
> **vacías** y nadie se entera hasta que el cliente lo abre. Medido en la VM: leído sin
> recalcular da `A3=None`; tras pasar por LibreOffice da `A3=1540`. Una prueba que solo
> verifique "se generó el archivo" **pasa igual con el defecto adentro**.

> ⚠️ **En la prueba 4, `pytesseract` puede no encontrar el ejecutable** aunque esté en el
> PATH del sistema. Si pasa, fijarlo explícito en el script:
> `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`.

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

🔴 **En Windows el camino es otro, porque el instalador del comando `composio` rechaza
Windows.** Medido el 24 de septiembre de 2026 leyendo el instalador oficial: detecta Windows y
sale con *"Windows is not supported. Use WSL"*. En vez del comando se usa el **servidor MCP
remoto de Composio**, que Claude Code agrega con una sola línea (MCP es el protocolo con el
que Claude Code se conecta a servicios externos):

```powershell
claude mcp add --scope user --transport http composio https://connect.composio.dev/mcp
```

Después, dentro de una sesión: `/mcp`, escoger `composio` y autenticar. Abre el navegador, y
**la cuenta de Composio es del cliente**. Las aplicaciones se autorizan desde la misma sesión
la primera vez que se piden, o en el tablero de `composio.dev`.

Verificación: `claude mcp list` debe mostrar `composio` en `Connected`. Con `--scope user`
queda disponible en todos sus proyectos, incluidas las sesiones que lance el teléfono.

> ✅ **Probada el 24 de septiembre de 2026 en `win11-dogfood`**, con la cuenta del dueño de la
> máquina: la autenticación de `/mcp` completó, y dos borradores salieron con su PDF adjunto
> **idéntico byte por byte** al original, marcado como `application/pdf` (verificado leyendo el
> correo crudo). Uno de 1.4 KB y otro de **339 KB**, que es el tamaño de un contrato escaneado.
>
> ⚠️ **Lo que cuesta: el de 339 KB tardó 13 minutos**, porque la sesión tuvo que descubrir cómo
> subir el archivo. Por esta vía el archivo vive en la laptop y el servicio está lejos, así que
> lo que funcionó fue pedirle al área de trabajo remota de Composio una dirección de subida y
> mandarle el archivo directo desde Windows. **El camino que hay que evitar** es convertir el
> archivo a texto y pasarlo por la conversación: sirvió con el de 1.4 KB y con un contrato real
> se topa con el límite de lo que el modelo escribe de una vez. Vale avisarle al cliente que el
> primer adjunto grande tarda, y en Linux el comando `composio` lo resuelve directo.

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

```powershell
$ignore = git config --global core.excludesFile
if (-not $ignore) {
  # No había ninguno configurado: el nuestro se vuelve el gitignore global.
  $ignore = "$env:USERPROFILE\.config\git\ignore"
  git config --global core.excludesFile $ignore
}
New-Item -ItemType Directory -Force -Path (Split-Path $ignore) | Out-Null
if (-not (Test-Path $ignore)) { New-Item -ItemType File -Path $ignore | Out-Null }

if (-not (Select-String -Path $ignore -Pattern '^bandeja/$' -Quiet)) {
@"

# Archivos que el lanzador sube desde el teléfono y archivos que el asistente
# genera para que se bajen. Viven dentro del proyecto pero no son código, y
# pueden ser material sensible de cliente. Sin esto, un "git add -A" de
# cualquier sesión los subiría a los repos privados sin que nadie lo note.
bandeja/
salida/
"@ | Add-Content -Path $ignore -Encoding utf8
}
```

Verificación (sin necesidad de un repositorio git):

```powershell
git config --global core.excludesFile
# Debe responder con una ruta (la suya, si ya tenía una; si no, C:\Users\<usuario>\.config\git\ignore)

$ignore = git config --global core.excludesFile
if (Select-String -Path $ignore -Pattern "salida/" -Quiet) { "✓ salida/ está en el gitignore" } else { "✗ ERROR: salida/ no encontrado" }
if (Select-String -Path $ignore -Pattern "bandeja/" -Quiet) { "✓ bandeja/ está en el gitignore" } else { "✗ ERROR: bandeja/ no encontrado" }
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

Se cierra igual que A6: sembrando la convención en `%USERPROFILE%\.claude\CLAUDE.md` **de
forma aditiva e idempotente**, para que cualquier sesión, en cualquier proyecto de esa
máquina, la conozca sin que haya que explicarla cada vez, y sin arriesgar lo que ya haya
en el archivo:

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
New-Item -ItemType Directory -Force -Path (Split-Path $claudeMd) | Out-Null
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd | Out-Null }

if (-not (Select-String -Path $claudeMd -Pattern '^## Agenda y avance' -Quiet)) {
@'

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

```powershell
Get-TimeZone | Select-Object -ExpandProperty Id    # debe ser la zona de quien la va a usar
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
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

> ⚠️ **Guardarlo en UTF-8, el mismo aviso de B5.** Claude Code lo lee como UTF-8; en cp1252
> los acentos llegan rotos. El `-Encoding utf8` de arriba ya lo hace bien.

> ⚠️ **Idempotente, igual que A6: correrlo dos veces no duplica la sección.** Y si
> `%USERPROFILE%\.claude\CLAUDE.md` ya tiene contenido de otro paso (el más obvio: si por
> algún motivo B5 ya corrió antes), esto se anexa, no lo reemplaza.

> 🔴 **El reverso de esa misma moneda, y muerde al ACTUALIZAR una máquina ya instalada:** como
> la guarda es el encabezado, en una máquina que ya trae la sección **este bloque no corre**.
> O sea que **las reglas nuevas del contrato no llegan solas**: el asistente de esa máquina
> sigue con el contrato del día que se instaló, y nada avisa. Al actualizar una instalación
> vieja hay que **agregar a mano lo que le falte**, comparando contra el bloque de aquí.

Verificación: crear un `pendientes.md` de prueba con una tarea, abrir una sesión nueva en
ese proyecto y pedirle que revise sus pendientes. Debe encontrar la tarea sin que se la
describas. Rápido y sin abrir sesión:
`Select-String -Path "$env:USERPROFILE\.claude\CLAUDE.md" -Pattern "pendientes.md" -Quiet`.

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
argumento queda en el historial de PowerShell):

```powershell
'LA_LLAVE' | python "$env:USERPROFILE\.claude\skills\whisper-deepinfra\whisper_deepinfra.py" --guardar-llave
```

Queda en `%USERPROFILE%\.config\deepinfra\credentials`. **Es una sola llave para las dos
capacidades**: quien ya la dio para transcribir no la vuelve a dar para escuchar un
documento, y viceversa.

### A8b. Cuánto cuesta, con cifras reales

| Capacidad | Precio | Aterrizado |
|---|---|---|
| Transcribir una grabación | $0.00020 USD por minuto | una junta de una hora, poco más de un centavo de dólar ($0.012) |
| Convertir un documento a audio | $0.62 USD por millón de caracteres | un documento de 10 páginas (~20 mil caracteres), alrededor de un centavo de dólar |

> 📌 **Si además se contrató la fase B, el audio se escucha con un clic.** El MP3 cae en
> `salida\` del proyecto y el lanzador lo sirve por una liga, así que desde el teléfono se
> toca y suena, en vez de descargarlo y buscarlo en el navegador de archivos. Sin la fase B
> la capacidad funciona igual, solo que el audio llega como archivo adjunto. Se verifica en
> el renglón 13.

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


## B1. La tailnet, desde cero


Es la parte que se suele dar por hecha y no lo está. **Sin la red, todo lo demás se instala
bien y no sirve para nada**, porque el teléfono no encuentra la laptop.

**El cliente crea su propia tailnet, no se une a la nuestra.** El motivo no es de comodidad:
meter la máquina de un cliente en nuestra red la pone junto a los ambientes de producción de
otros clientes. Su red es suya, y así se la lleva consigo el día que deje de trabajar con
nosotros.

### 2.1 Crear la tailnet y meter la laptop

En `login.tailscale.com`, crear la cuenta con el correo del cliente. El plan gratuito cubre
de sobra dos equipos; conviene confirmar los límites vigentes porque cambian.

```powershell
& "C:\Program Files\Tailscale\tailscale.exe" up
& "C:\Program Files\Tailscale\tailscale.exe" status
```

`status` debe listar la laptop. Si dice que el dispositivo está pendiente de aprobación, hay
que aprobarlo en la consola: algunas tailnets traen aprobación manual activada.

### 2.2 El teléfono, que es la mitad del montaje

1. **Tailscale**, con **la misma cuenta** de la tailnet. Al terminar, `tailscale status` en
   la laptop debe listar también el teléfono.
2. **Claude**, la app oficial de Anthropic, con la misma cuenta que se autenticó en la
   laptop. **Es con la que se abre la sesión**: el lanzador solo la enciende, la conversación
   ocurre en esa app.

> ⚠️ **Son dos canales distintos y conviene entenderlo para diagnosticar.** La tailnet solo
> sirve para alcanzar **la página del lanzador**. La sesión de Claude no viaja por la
> tailnet: el teléfono se conecta a ella por la infraestructura de Anthropic. O sea que "no
> abre la página" y "no aparece la sesión" son fallas distintas, con causas distintas.

### 2.3 Los tres interruptores de la consola de administración

Viven en `login.tailscale.com`, **no en la laptop**, y sin ellos la instalación termina sin
errores y no funciona. Es la falla más desconcertante, porque todo lo local se ve bien.

| Interruptor | Dónde | Comprobar |
|---|---|---|
| **MagicDNS** | consola → DNS | `tailscale dns status` debe decir `MagicDNS: enabled tailnet-wide` |
| **Certificados HTTPS** | consola → DNS | El paso 5 falla con un mensaje explícito si están apagados |
| **Aprobación para publicar** | la imprime el propio comando | Si el paso 5 imprime una URL de aprobación, abrirla y aceptar |

MagicDNS suele venir encendido en tailnets nuevas y los certificados HTTPS no. Comprobar los
dos: cuesta un comando, y no hacerlo cuesta un diagnóstico a ciegas.

### 2.4 Modo desatendido

```powershell
& "C:\Program Files\Tailscale\tailscale.exe" set --unattended=true
```

Sin esto, **mientras nadie inicie sesión en Windows la máquina entera desaparece de la
tailnet** y el teléfono no encuentra nada. Medido: 12 minutos en la pantalla de contraseña,
con el nodo marcado `offline` todo ese tiempo.

## B2. El lanzador


> ✅ **Ya es el mismo código que en Linux.** Hasta el 3 de agosto de 2026 Windows corría una
> variante aparte que había que armar a mano; con la unificación quedó **una sola base con
> dos implementaciones de la capa de proceso detrás de la misma interfaz** (`procesos.py`
> escoge entre `procesos_tmux.py` y `procesos_windows.py`). **Copiar la carpeta completa, sin
> mezclar archivos de ningún otro lado.**

> 🔴 **De dónde sale el código, porque este paso no se puede hacer sin traerlo.** A
> diferencia de `bitacora.py` (A3), **el lanzador NO está en el repo público de skills** y no
> hay URL de la que bajarlo. Vive en un repo privado, y **lo trae quien instala**: por red
> desde tu equipo, en una memoria USB, o clonando el repo privado si la máquina tiene acceso.
> Consíguelo **antes** de empezar esta fase.

```powershell
# $ORIGEN es la copia del lanzador que TRAJISTE. Ajusta la ruta a donde la dejaste.
$ORIGEN = "D:\ruta\a\tu\copia\de\rc-launcher"

# el código va al perfil del usuario, no a Archivos de programa
robocopy $ORIGEN "$env:USERPROFILE\rc-launcher" /E /XD .venv __pycache__ .git

New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\claude"
```

> ⚠️ **`robocopy` sale con código 1 cuando copió bien.** No es un error: usa 0 para "nada
> que copiar" y 1 para "copió archivos". Solo de 8 para arriba hay falla real.

**Comprobar que llegó completo antes de seguir**, porque una copia a medias arranca igual y
falla después, lejos de aquí:

```powershell
foreach ($f in "app.py","sessions.py","procesos.py","procesos_windows.py","requirements.txt","templates","tests") {
  if (-not (Test-Path "$env:USERPROFILE\rc-launcher\$f")) { "FALTA: $f" }
}
"revisión terminada (sin líneas FALTA arriba = completo)"
```

Ya con la copia completa:

```powershell
cd $env:USERPROFILE\rc-launcher
python -m pytest -q        # deben pasar todas, sin una sola falla
python app.py              # debe quedarse escuchando; Ctrl+C para salir
```

Al 17 de agosto de 2026 son 622 pruebas. **El número crece con cada versión, así que no lo
trates como contraseña**: lo que importa es que no falle ninguna.

> ⚠️ **Si fallan por rutas demasiado largas, no es defecto del lanzador.** Windows corta en
> 260 caracteres por omisión, y el esquema que codifica sesiones incrusta la ruta absoluta
> como nombre de carpeta. Apunta `TMP` a una ruta corta y vuelve a correrlas. **No toques el
> registro de una máquina de cliente para esto**: eso pide aprobación de su área de sistemas,
> y de todos modos el cliente nunca corre estas pruebas.

La raíz **tiene que ser** `%USERPROFILE%\claude`: `sessions.py` la calcula así y no es
configurable sin tocar código.

> 📌 **Si el proyecto ya tiene `pendientes.md` (A7), el lanzador ya lo pinta y lo palomea
> con el dedo, sin configuración adicional.** No hay ningún paso extra que hacer aquí.

### B2b. Llevarle una versión nueva a una máquina que ya lo tiene

**Esto es para las actualizaciones, no para la instalación inicial.** El lanzador se mejora
seguido, y el código llegó aquí por copia: **nada se entera solo de que hay una versión
nueva**, así que actualizar es volver a copiar y reiniciar.

```powershell
$ORIGEN = "D:\ruta\a\tu\copia\de\rc-launcher"

robocopy $ORIGEN "$env:USERPROFILE\rc-launcher" /E /PURGE /XD .venv __pycache__ .git
cd $env:USERPROFILE\rc-launcher
python -m pip install -q -r requirements.txt   # por si la versión nueva pide algo más
python -m pytest -q                            # todas en verde ANTES de reiniciar
```

> 🔴 **Reiniciar la tarea programada NO basta, y este es el error que más caro sale.**
> `schtasks /end` termina el `.cmd` pero **deja vivo al `python` que ese `.cmd` lanzó**, que
> conserva el puerto 8765; el `/run` arranca otro que nunca escucha. Las dos órdenes contestan
> `SUCCESS` y el lanzador sigue respondiendo, **con el código viejo**. Hay que matar por PID
> al proceso que tiene el puerto, nunca por nombre, para no llevarse otros Python de esa
> máquina. El procedimiento completo está en B3.

> ⚠️ **`/PURGE` es a propósito:** sin él, un archivo que la versión nueva ya eliminó se queda
> en la máquina y puede seguir importándose. **Lo excluido con `/XD` está a salvo**, medido el
> 13 de agosto de 2026 con una carpeta sembrada a propósito: sobrevivió al `/PURGE` mientras el
> archivo obsoleto sí desapareció. (En Windows la instalación va sin entorno virtual, con el
> Python del sistema, así que ahí `.venv` solo aparece si alguien lo creó a mano.)

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
> computadora** (`cd $env:USERPROFILE\claude\<proyecto>`, `claude`, contestar, `/exit`)
> antes de tocarlo desde el teléfono. Las sesiones siguientes de ese proyecto, y las que se
> lancen desde el teléfono, ya arrancan directo.

## B3. Arranque automático


Un `.cmd` envoltorio y una tarea programada que arranca **con la máquina**, sin esperar a que
nadie entre:

```powershell
@"
@echo off
cd /d "%USERPROFILE%\rc-launcher"
"$((Get-Command python.exe).Source)" app.py
"@ | Out-File "$env:USERPROFILE\lanzador.cmd" -Encoding ascii

$accion = New-ScheduledTaskAction -Execute "$env:USERPROFILE\lanzador.cmd"
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
Register-ScheduledTask -TaskName "rc-launcher" -Action $accion -Principal $principal -Force `
  -Trigger @((New-ScheduledTaskTrigger -AtStartup), (New-ScheduledTaskTrigger -AtLogOn))
Start-ScheduledTask -TaskName "rc-launcher"
```

> 🔴 **`LogonType S4U` es lo que hace la promesa honesta, y esta guía enseñaba otra cosa hasta
> el 10 sep 2026.** Decía `schtasks /SC ONLOGON`, que **exige que alguien tenga sesión
> iniciada**: con la laptop encendida y la pantalla bloqueada, el lanzador sencillamente no
> está. S4U corre sin sesión y sin contraseña guardada, así que la laptop encendida basta.
>
> **Con qué se compara:** `/SC ONSTART` con cuenta de usuario se crea y **nunca corre** (queda
> en `267011`, "no ha ejecutado", sin avisar), y por eso la guía había caído en `ONLOGON`. El
> modo que resuelve las dos cosas es S4U, medido el 5 ago 2026 con un reinicio de verdad: la
> máquina arrancó con la sesión cerrada y a los 21 segundos el lanzador ya contestaba por la tailnet.
>
> ⚠️ **Lo que S4U cuesta, y hay que saberlo:** la tarea corre sin credenciales de red, así que
> pierde el acceso a unidades de red compartidas. Lo que el lanzador necesita (disco local y
> salida a internet) funciona igual.

> 📌 **Los dos disparadores son a propósito:** el de arranque cubre la máquina que se prende
> sola tras un corte de luz, y el de inicio de sesión cubre a quien entra después de haberla
> apagado a mano.

> 📌 **Al re-registrar sobre una máquina que ya lo tenía, `Start-ScheduledTask` deja
> `LastTaskResult: 2147946720`**, que es "la petición fue rechazada" y aquí significa nada más
> que **el lanzador anterior seguía corriendo**, con el puerto tomado. Medido el 10 sep 2026, con
> la app contestando `200` todo el tiempo. Para cargar el código nuevo de verdad hay que matar al
> dueño del puerto, y eso está en B2b.

> ⚠️ **`schtasks /run` NO reinicia una tarea que ya corre.** Contesta "is currently running"
> y no hace nada. La secuencia correcta es `schtasks /end` y luego `schtasks /run`.
>
> 🔴 **Y esa secuencia NO basta para recargar el código, cosa que importa cada vez que se
> actualice el lanzador.** `schtasks /end` termina el `.cmd` de la tarea pero **deja vivo al
> `python` que ese `.cmd` lanzó**, así que el proceso viejo conserva el puerto 8765 y el
> `/run` arranca un segundo que no puede escuchar. Las dos órdenes contestan `SUCCESS` y el
> lanzador sigue respondiendo, o sea que **el síntoma es que el código nuevo simplemente no
> está**: una ruta recién agregada devuelve el 404 genérico de Flask, como si no existiera.
> Medido en la VM de dogfooding el 6 ago 2026, con dos `python.exe` vivos a la vez.
>
> Hay que matar al que tiene el puerto, **por PID y no por nombre**, para no llevarse por
> delante otros Python de la máquina del cliente:
>
> ```powershell
> $pid_lanzador = (Get-NetTCPConnection -LocalPort 8765 -State Listen).OwningProcess
> Stop-Process -Id $pid_lanzador -Force
> schtasks /run /tn rc-launcher
> ```
>
> Y comprobar que quedó **uno solo**: `tasklist /fi "imagename eq python.exe"`. En Windows
> viejo sin `Get-NetTCPConnection`, el PID sale de `netstat -ano | findstr :8765`.

## B3b. El vigilante y su canal de avisos

**Esto faltaba entero hasta el 10 sep 2026:** en Windows el vigilante ni siquiera se
instalaba, así que el aviso de "la tarea terminó" era cosa de Linux nada más. Son dos
piezas, y hacen falta las dos.

El vigilante mira cada minuto si alguna sesión cerró su turno, o sea si **Claude Code se
quedó esperando a la persona**, y manda un aviso al teléfono con la liga para abrir esa
misma sesión. Cubre justo el hueco de la aplicación de Claude, que avisa cuando hay algo
que contestar y se calla cuando el trabajo simplemente terminó.

### El canal: dos caminos, y el segundo es el normal

El canal es **ntfy**: una aplicación de teléfono que recibe avisos y un servidor que los
publica. Sin cuenta de correo, sin token de por medio, y con una versión gratuita.

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

```powershell
$carpeta = "$env:USERPROFILE\.config\rc-launcher"
New-Item -ItemType Directory -Force -Path $carpeta | Out-Null
$tema = "rc-" + -join ((1..16) | ForEach-Object { "abcdefghijkmnpqrstuvwxyz23456789"[(Get-Random -Max 32)] })
@"
{
  "url": "https://ntfy.sh",
  "tema": "$tema",
  "usuario": "",
  "clave": "",
  "prioridad": "default",
  "titulo_suelto": "Claude Code"
}
"@ | Out-File "$carpeta\ntfy.json" -Encoding ascii
"El tema es: $tema"
```

> ⚠️ **`-Encoding ascii` a propósito, y conviene saber por qué:** el `utf8` de PowerShell 5.1
> escribe **marca de orden de bytes**, y con ella al frente el archivo deja de ser JSON
> válido para muchos lectores. El lanzador ya la tolera desde el 10 sep 2026, pero la guía
> escribe limpio de todos modos: el contenido es ASCII puro, así que cuesta cero.

**El tema hay que copiarlo**, porque es lo que la persona escribe en su teléfono.

### El vigilante, como tarea programada cada minuto

```powershell
$pythonw = (Get-Command python.exe).Source -replace 'python\.exe$','pythonw.exe'
$carpeta = "$env:USERPROFILE\rc-launcher"

$accion = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$carpeta\watcher.py`"" -WorkingDirectory $carpeta
$ahora = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$arranque = New-ScheduledTaskTrigger -AtStartup
$arranque.Repetition = $ahora.Repetition
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "rc-watcher" -Action $accion -Trigger @($ahora, $arranque) `
  -Principal $principal -Settings $ajustes -Force
```

> 🔴 **`schtasks /SC MINUTE` aquí NO sirve, y falla del modo más caro: se crea, dice
> `SUCCESS`, y jamás corre.** Medido en la VM de dogfooding el 10 sep 2026: la tarea queda con
> `Last Result: 267011` y última corrida en `30/11/1999`, o sea nunca, porque nace con
> `LogonType: Interactive` y **esa máquina tiene la sesión cerrada**. Ni `/RU` con `/NP`
> lo arregla: sigue saliendo `Interactive`.
>
> **Lo que sí funciona es S4U**, que es justo el modo en que ya está el lanzador desde B3, y por
> eso el bloque va con `Register-ScheduledTask` en vez de `schtasks`. Verificado en la misma
> sesión: `LogonType: S4U`, `UltimoResultado: 0`, con la máquina encendida y la sesión cerrada.
>
> 📌 **Es la misma familia del aviso de B3 sobre `ONSTART`**, y conviene leerlo así: en Windows,
> una tarea que debe correr con la laptop encendida y sin sesión abierta **siempre** termina
> necesitando S4U.

> 🔴 **`pythonw.exe` y jamás `python.exe`, y esto decide si el cliente lo tolera o lo
> apaga.** Con `python.exe` una tarea que corre **cada minuto** abre una ventana negra de
> consola cada minuto, encima de lo que la persona esté haciendo. `pythonw.exe` es el mismo
> intérprete sin consola. Viene junto al otro, en la misma carpeta.

> 🔴 **El disparador `-Once -At (Get-Date)` es el que hace que empiece HOY, y sin él la tarea
> queda muda hasta el próximo reinicio.** Medido en la VM el 10 sep 2026: con `-AtStartup` como
> único disparador, la repetición se registra pero **jamás arranca**, porque una repetición
> empieza a contar cuando su disparador dispara, y la máquina ya estaba encendida. El síntoma
> exacto es `NextRunTime` **vacío** con la tarea en `Ready`, que se lee como si estuviera bien.
> Con el disparador de ahora, `NextRunTime` sale con hora concreta, a un minuto.
>
> **El de arranque se queda igual**, para el día que la máquina se apague: cubre el reinicio, y
> el otro cubre hoy.

> ⚠️ **`-AllowStartIfOnBatteries` y `-DontStopIfGoingOnBatteries` importan justo en el cliente
> que esto busca**, que trabaja en una laptop: de fábrica, Windows **se salta las tareas
> programadas cuando el equipo anda con batería**, así que el aviso desaparecería precisamente
> cuando la persona está fuera del escritorio.

> ⚠️ **El lanzador y el vigilante son tareas distintas**, y conviene tenerlo claro: el lanzador
> es un servidor que vive todo el día, y el vigilante es un vistazo que corre y termina.
> Meterlos en la misma tarea deja al vigilante sin correr.

### Comprobarlo, que son dos renglones

```powershell
cd "$env:USERPROFILE\rc-launcher"
python -c "import avisos; print(avisos.enviar('Prueba de instalación\nSi ves esto en el teléfono, el canal quedó.'))"
(Get-ScheduledTaskInfo -TaskName "rc-watcher") | Select-Object LastRunTime, LastTaskResult, NextRunTime
```

Lo primero sale `(True, 'avisado')` **y el aviso llega al teléfono**. Las dos cosas: el
`True` dice que el servidor lo aceptó, y solo el teléfono dice que la suscripción está
bien escrita. Lo segundo tiene que reportar tres cosas: `LastTaskResult` en **`0`**, una `LastRunTime` de hace
menos de un minuto, y **`NextRunTime` con hora**. **Un `267011` con fecha de 1999 significa que
la tarea jamás corrió**, y **una `NextRunTime` vacía significa que ya sólo correría tras un
reinicio**;
los dos recuadros rojos de arriba dicen por qué.

> 📌 **Si sale `(False, ...)`, el mensaje dice cuál de las tres cosas falló**: falta el
> archivo, el servidor contestó un código (un 401 es usuario o clave), o la red. Un
> `403` en `ntfy.sh` suele ser un tema con mayúsculas o con caracteres raros.

### Del lado del teléfono

Instalar **ntfy** (Play Store, App Store o F-Droid), tocar **Agregar suscripción** y
escribir el tema. Con servidor propio, marcar **Usar otro servidor** y poner la dirección
con su usuario y contraseña.

## B4. Publicarlo en la tailnet


```powershell
& "C:\Program Files\Tailscale\tailscale.exe" serve --bg http://127.0.0.1:8765
& "C:\Program Files\Tailscale\tailscale.exe" serve status
```

Queda en `https://<nombre-del-equipo>.<tailnet>.ts.net/`, **alcanzable solo desde la
tailnet**. Esa es la URL que se le da al usuario.

## B5. Decirle a las sesiones qué es la bandeja


**Paso corto y fácil de olvidar, y sin él la mitad del valor del lanzador no se usa.** El
lanzador deja lo que se sube desde el teléfono en `bandeja/`, dentro del proyecto. Pero
**nada le dice a la sesión que esa convención existe**: al pedirle "mira lo que subí a la
bandeja" contesta preguntando si te refieres al correo.

**Aditivo e idempotente, igual que A6 y A7** (que ya pudo haber escrito en este mismo
archivo, porque la fase A corre antes que esta): se anexa a
`%USERPROFILE%\.claude\CLAUDE.md`, nunca lo reemplaza.

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
New-Item -ItemType Directory -Force -Path (Split-Path $claudeMd) | Out-Null
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd | Out-Null }

if (-not (Select-String -Path $claudeMd -Pattern '^## La bandeja' -Quiet)) {
@'

## La bandeja: archivos que subo desde el teléfono


Cada proyecto puede tener una carpeta `bandeja/` en su raíz. Ahí es donde el lanzador rc deja
lo que subo desde el celular: fotos, audios de junta, PDFs, capturas.

**Si menciono "la bandeja", me refiero a esa carpeta del proyecto en el que estás, no a un
correo ni a nada de Gmail.** Revisar `bandeja/` del proyecto actual y trabajar con lo que
haya ahí.

Está en el gitignore, así que no aparece en `git status`. Al terminar de usar un archivo, yo
decido qué hacer con él desde el menú del lanzador, **no moverlo ni borrarlo por iniciativa
propia**, salvo que lo pida.
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

> ⚠️ **Guardarlo en UTF-8, no en el default del Bloc de notas.** Claude Code lo lee como
> UTF-8; en cp1252 los acentos llegan rotos. El `-Encoding utf8` de arriba ya lo hace bien.

> ⚠️ **Correrlo dos veces no duplica la sección**, ni pisa la convención de pendientes que
> A7 ya sembró ahí. Es el mismo guardado con `Select-String` que usan A6 y A7.

Verificación: subir un archivo desde el teléfono, abrir la sesión de ese proyecto y pedirle
que vea la bandeja. Debe encontrarlo sin que le digas la ruta. Rápido y sin teléfono:
`Select-String -Path "$env:USERPROFILE\.claude\CLAUDE.md" -Pattern "La bandeja" -Quiet`.

## B6. El comando `rc`, para lanzar desde la terminal (opcional)

**El camino principal es el teléfono**, y esta sección se puede saltar entera sin perder
nada de lo demás. Sirve para quien ya está frente a una terminal y prefiere teclear en vez
de sacar el celular.

**Lo que importa, y es lo que lo hace seguro: la sesión que nace aquí es la misma que nace
desde el teléfono.** El comando llama al mismo código, así que aparece en el mosaico y se
puede cerrar con el dedo. Dos formas distintas de crear una sesión se separan sin que nadie
lo note, y ahí es donde una sesión se vuelve invisible e inmatable.

Windows necesita además **desde dónde** llamarlo: de fábrica no trae servidor SSH
encendido, así que esto es para quien se sienta frente a la máquina, o para quien encienda
OpenSSH a propósito. Es la razón principal por la que esta sección es opcional.

Crear `%USERPROFILE%\bin\rc.cmd` (y asegurarse de que esa carpeta esté en el `PATH`):

```powershell
$bin = "$env:USERPROFILE\bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null
@"
@echo off
python "RUTA_DEL_LANZADOR\procesos_windows.py" %*
"@ | Set-Content -Path "$bin\rc.cmd" -Encoding ascii
```

Sustituir `RUTA_DEL_LANZADOR` por la carpeta real. Uso:

```
rc                      :: lista las carpetas disponibles
rc mi-proyecto          :: crea la sesión y devuelve la terminal
rc mi-proyecto --resume <session-id>
```

> ⚠️ **En Windows la sesión SIEMPRE nace desprendida**, o sea que el comando la crea y te
> devuelve el símbolo del sistema; no te deja trabajando dentro como en Linux. Quedarse
> adentro exige que la consola hospede la terminal falsa, y eso está sin construir. `-d` se
> acepta igual, para que el mismo tecleo funcione en las dos plataformas.

> 🔴 **Y un gotcha que costó medir: la sesión tiene que desprenderse del Job de Windows, o
> muere con la consola que la lanzó.** Ya viene resuelto en el código
> (`CREATE_BREAKAWAY_FROM_JOB`); se menciona porque el síntoma es desconcertante — la ficha
> de la sesión queda escrita y el proceso ya no existe.

Verificación: `rc` sin argumentos lista los proyectos; `rc <alguno>` crea la sesión, el
mosaico la muestra en **Activos**, y **sigue viva después de cerrar esa consola**.

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

```powershell
if (Test-Path "$env:USERPROFILE\rc-launcher\transcripciones_drive.py") { "trae la revisión" } else { "copia anterior al 22 de septiembre de 2026" }
```

### B7b. La carpeta y la configuración

1. **En Drive, con la cuenta del cliente:** crear la carpeta donde caerán las transcripciones
   (el nombre sugerido es `Transcripciones`) y **dentro de ella una subcarpeta llamada
   exactamente `Procesadas`**, porque ese es el nombre que usa la instrucción.
2. **Copiar el identificador de la carpeta** desde la barra de direcciones del navegador: es lo
   que va después de `drive.google.com/drive/folders/`.
3. **Escribir la configuración** en `%USERPROFILE%\.config\rc-launcher\transcripciones.json`, sustituyendo el identificador:

```powershell
$dir = "$env:USERPROFILE\.config\rc-launcher"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
'{"carpeta": "Transcripciones", "carpeta_id": "EL_ID_DE_LA_CARPETA"}' |
  Set-Content -Path "$dir\transcripciones.json" -Encoding utf8
```

> 📌 **El `-Encoding utf8` de PowerShell 5.1 escribe una marca de orden de bytes al inicio del
> archivo.** El lanzador la tolera (lee con `utf-8-sig`), así que no hace falta quitarla.

**Sin reinicios:** el lanzador lee ese archivo cada vez que lanza una sesión. Y para
apagar la revisión basta con borrarlo; la sesión vuelve a arrancar exactamente como antes.

### B7c. Verificar

Primero que la configuración se lee (debe imprimir `True`):

```powershell
cd "$env:USERPROFILE\rc-launcher"; python -c "import transcripciones_drive as t; print(t.instruccion_para_la_sesion('prueba') is not None)"
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

```powershell
foreach ($f in "calendario_sesion.py","aviso_arranque.py") {
  if (-not (Test-Path "$env:USERPROFILE\rc-launcher\$f")) { "FALTA: $f" }
}
"revisión terminada"
```

### B8b. La configuración y el gancho

1. **Sacar el identificador de cada calendario**, en Google Calendar desde la computadora: los
   tres puntos junto al nombre del calendario → *Configuración y uso compartido* → sección
   *Integrar el calendario* → *ID del calendario*. El calendario principal no hace falta
   buscarlo: su identificador es `primary`.
2. **Escribir la configuración**, sustituyendo el identificador:

```powershell
$dir = "$env:USERPROFILE\.config\rc-launcher"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
'{"calendarios": [{"nombre": "Trabajo", "id": "EL_ID_DEL_CALENDARIO_DE_TRABAJO"}, {"nombre": "principal", "id": "primary"}], "minutos_antes": 30}' |
  Set-Content -Path "$dir\calendario.json" -Encoding utf8
```

> 📌 **La marca de orden de bytes que agrega `-Encoding utf8` se tolera**, igual que en B7b.

> ⚠️ **El principal va en la lista aunque el cliente tenga un calendario aparte para el
> trabajo.** Las invitaciones de sus clientes caen en el principal, porque el dueño de ese
> evento es quien invita. Si solo tiene el principal, la lista lleva ese renglón y ya.

3. **Registrar el gancho** en `%USERPROFILE%\.claude\settings.json`. Este fragmento lo agrega
   sin tocar lo demás, y no lo duplica si ya estaba. Toma la ruta del Python con el que se
   corre, que es el mismo `<python>` de A3:

```powershell
@'
import json, pathlib, shutil, sys
cfg = pathlib.Path.home() / ".claude" / "settings.json"
gancho = pathlib.Path.home() / "rc-launcher" / "aviso_arranque.py"
orden = f'"{sys.executable}" -X utf8 "{gancho}"'
shutil.copy(cfg, str(cfg) + ".bak")            # respaldo antes de tocar nada
datos = json.loads(cfg.read_text(encoding="utf-8"))
inicio = datos.setdefault("hooks", {}).setdefault("SessionStart", [])
ya = any(h.get("command") == orden for g in inicio for h in g.get("hooks", []))
if not ya:
    inicio.append({"hooks": [{"type": "command", "command": orden}]})
cfg.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
print("ya estaba" if ya else "registrado")
'@ | Set-Content -Encoding UTF8 "$env:TEMP\registrar_gancho.py"

python "$env:TEMP\registrar_gancho.py"
```

> 🔴 **El `-X utf8` NO es opcional en Windows.** Sin él, Python escribe la salida del gancho en la
> codificación de la consola de Windows (cp1252) y no en UTF-8, que es lo que lee Claude Code. El
> aviso lleva acentos y comillas `«»`, así que llega ilegible y **la sesión arranca sin él, sin
> mostrar error**. Medido el 25 de septiembre de 2026 simulando esa codificación: la salida deja
> de ser UTF-8 válido en el byte 137, justo en la primera `«`.

> 📌 **Basta cualquier Python de la máquina**, porque el gancho usa solo la biblioteca
> estándar. Y queda junto al gancho `pendiente` de la bitácora (A3); los dos corren al
> iniciar y cada uno hace lo suyo.

**Sin reinicios:** el lanzador lee `calendario.json` cada vez que lanza una sesión, y Claude Code
lee `settings.json` al abrir cada sesión. Para apagar la revisión basta con borrar
`calendario.json`.

### B8c. Verificar

Primero que la configuración se lee y que la instrucción habla del cliente (deben imprimir
`True` y luego `False`):

```powershell
cd "$env:USERPROFILE\rc-launcher"; python -c "import calendario_sesion as c; t = c.instruccion_para_la_sesion('prueba'); print(t is not None); print('Gustavo' in t)"
```

> 🔴 **Si el segundo renglón imprime `True`, la copia del lanzador todavía le dice a la sesión
> que espere el sí de "Gustavo"**, que es el nombre de quien la construyó. En la máquina de otra
> persona eso confunde a la sesión y al cliente. Llevarle una copia corregida con B2b antes de
> entregar.

Luego que el gancho habla y que se calla con la marca del lanzador (el primero imprime un
renglón que empieza con `{"hookSpecificOutput"`, el segundo nada):

```powershell
$P = @{source="startup"; cwd="$env:USERPROFILE\claude\<proyecto>"} | ConvertTo-Json -Compress
$G = "$env:USERPROFILE\rc-launcher\aviso_arranque.py"
$env:RC_LANZADOR = $null; ($P | python -X utf8 $G).Substring(0, 30)
$env:RC_LANZADOR = "1";   $P | python -X utf8 $G; "(vacío arriba = correcto)"
$env:RC_LANZADOR = $null
```

Y la prueba completa, con el cliente enfrente:

1. Crear en su calendario un evento que empiece en 10 minutos, titulado
   `<proyecto> · Prueba de instalación`, con una descripción de una línea.
2. Desde el teléfono, lanzar una sesión nueva en ese proyecto. **La sesión debe resumir el
   evento y preguntar «¿Lo atendemos?»**, por su propia cuenta.
3. En la computadora, abrir `claude` directo en esa carpeta y escribir "hola". **Debe ofrecer el
   mismo evento.**
4. **Mirar que el aviso salga una sola vez en la sesión del teléfono.** Si sale dos veces, la
   marca `RC_LANZADOR` se perdió en el camino del supervisor a `claude.exe` y el gancho habló
   además del lanzador (ver el aviso de abajo).
5. Borrar el evento de prueba.

> ⚠️ **Sin medir todavía en Windows, y es lo que decide el paso 4:** el lanzador le pasa la marca
> al supervisor por el entorno, y falta comprobar en `win11-dogfood` que `claude.exe` la hereda a
> través de winpty. Si se pierde, el costo es un aviso repetido, sin daño; el arreglo es del
> lado del lanzador.

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

> **Cómo se reparte por fases:** los renglones 1, 2, 3, 9, 9b, 10, 11, 11b y 12 cierran la **fase A**
> (gitignore, la convención de pendientes, el servicio local, la bitácora, el runtime de
> documentos, los conectores, Composio y la cuenta de DeepInfra); del 4 al 8, más el 13, el 14, el 15, el 16 y el 17,
> cierran la **fase B**, y necesitan el teléfono. Si solo se contrató la fase A, la verificación
> termina en el 12 y eso es una entrega completa.


| # | Qué | Cómo | Esperado |
|---|---|---|---|
| 1 | Gitignore global | `git config --global core.excludesFile` + `Select-String ... "salida/"` | ruta + sin error |
| 2 | Convención de pendientes | `Select-String -Path "$env:USERPROFILE\.claude\CLAUDE.md" -Pattern "pendientes.md" -Quiet` | encuentra la sección |
| 3 | La app responde | `Invoke-WebRequest http://127.0.0.1:8765/salud` | 200 |
| 4 | La puerta cierra | `Invoke-WebRequest http://127.0.0.1:8765/` | **403** |
| 5 | Se ve desde el teléfono | abrir la URL de la tailnet | aparecen los proyectos |
| 6 | Lanza | tocar un proyecto → "Nueva sesión" | en 5 s el botón queda encendido y la sesión aparece en la app de Claude |
| 7 | Cierra | tocar el proyecto → "Terminar sesión" | desaparece de la app |
| 8 | Retoma | tocar un proyecto apagado | lista sus sesiones previas |
| 9 | La bitácora | ver el recuadro de abajo, que tiene truco | el `CLAUDE.md` de ese proyecto trae una entrada nueva |
| 9b | La bitácora trae lo del calendario | `@(Select-String -Path "$env:USERPROFILE\.claude\hooks\bitacora.py" -Pattern "Google_Calendar").Count` | **`6`**. Menos que eso es una copia vieja bajada en A3 |
| 10 | El runtime de documentos | las cinco pruebas de A4g | los cinco archivos salen bien, **con el Excel trayendo resultados y no celdas vacías** |
| 11 | Los conectores | `claude mcp list` | `claude.ai Gmail`, `Google Calendar` y `Google Drive` en `Connected` |
| 12 | La cuenta de DeepInfra (opcional) | `python "$env:USERPROFILE\.claude\skills\whisper-deepinfra\whisper_deepinfra.py" --estado` | `llave: CONFIGURADA` si el cliente ya la dio; `NO CONFIGURADA` es correcto si todavía no la necesita |
| 13 | El audio se escucha con un clic (solo si ya usó la voz sintética) | ver el recuadro de abajo | el navegador del teléfono lo **reproduce**, no lo descarga |
| 14 | Dejar dicho, y que la lista se quede quieta | ver el recuadro de abajo | el recado queda escrito en el `pendientes.md` con su `»`, y el menú sigue mostrando la misma tarea |
| 15 | El filtro rápido del mosaico | ver el recuadro de abajo | teclear parte de un nombre deja a la vista solo los que coinciden, y la ✕ devuelve el mosaico completo |
| 11b | Composio (opcional, A5e) | `claude mcp list` | `composio` en `Connected`; si el cliente no lo contrató, se salta |
| 16 | Las transcripciones de Drive (opcional, B7) | los tres pasos de B7c | la sesión ofrece la de prueba al arrancar, y al procesarla queda en `transcripciones/` y en `Procesadas` |
| 17 | El bloque de calendario (opcional, B8) | los tres bloques de B8c | la instrucción imprime `True` y `False`, el gancho habla y se calla con la marca, y la sesión ofrece el evento de prueba desde el teléfono y desde `claude` directo |


> 📌 **Por qué el renglón del calendario mira el archivo y no el comportamiento.** Comprobar
> que el cierre de verdad toca un bloque exige cerrar una sesión que haya movido uno, y su
> respuesta normal cuando no hay nada que hacer es **quedarse callado**, o sea que un fallo
> se ve igual que un acierto. Lo que sí distingue una cosa de otra en un segundo es si el
> `bitacora.py` que quedó instalado trae las herramientas de calendario: si no las trae, el
> `curl` de A3 sirvió una copia vieja y esa mitad **nunca** va a funcionar.

> 📌 **Cómo se comprueba el renglón 13, y por qué no basta con que conteste 200.** El lanzador
> sirve lo que hay en `salida\` por `GET /audio/<proyecto>/<archivo>`. Lo que decide si el
> navegador lo toca o lo baja son tres cabeceras, así que se miran las tres:
>
> ```powershell
> $r = Invoke-WebRequest "http://127.0.0.1:8765/audio/<proyecto>/<archivo>.mp3" `
>        -Headers @{ "Tailscale-User-Login" = "<el correo del dueño de la tailnet>" }
> $r.StatusCode
> $r.Headers["Content-Type"]; $r.Headers["Content-Disposition"]; $r.Headers["Accept-Ranges"]
> ```
>
> Esperado: `200`, `audio/mpeg`, `**inline**` (nunca `attachment`, que fuerza la descarga) y
> `bytes`, que es lo que permite adelantar dentro de un audio largo. **La prueba de verdad es
> picarle a la liga desde el teléfono**, porque el comportamiento final lo decide su navegador.
>
> ⚠️ **Sin el encabezado de identidad contesta 403, y eso es correcto**, igual que el renglón
> 4. Desde el teléfono lo inyecta Tailscale solo. Es también lo que hace que esa liga **no
> sirva para compartirle el audio a un tercero**: para eso va el archivo adjunto.

> 📌 **Cómo se comprueba el renglón 14, que es de dos mitades.** La primera se mide desde la
> máquina: el menú de un proyecto con pendientes tiene que traer el ancla con la que el menú
> sabe a dónde volver, una por tarea.
>
> ```powershell
> $r = Invoke-WebRequest -Uri "http://127.0.0.1:8765/menu/<proyecto>" `
>   -Headers @{"Tailscale-User-Login"="<el correo del dueño de la tailnet>"}
> ([regex]::Matches($r.Content, "data-renglon=")).Count
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

> 📌 **Cómo se comprueba el renglón 15, y desde dónde se corre.** Hay un guion que lo mide
> completo, y **corre en la máquina de quien instala, apuntada a la laptop del cliente por la
> tailnet**: usa Playwright, que esta instalación deja fuera a propósito. Viaja dentro de la copia
> del lanzador que trajiste, así que ya lo tienes. **Así se verificó `win11-dogfood` el 17 de
> agosto de 2026, desde Linux y por la tailnet, con las 14 en verde.**
>
> ```bash
> # desde la máquina Linux de quien instala, no desde la laptop del cliente
> ORIGEN=/ruta/a/tu/copia/de/rc-launcher
>
> RC_BASE=https://<la-laptop>.<tu-tailnet>.ts.net \
>   node "$ORIGEN"/docs/superpowers/verificacion/2026-08-17-filtro-rapido-de-proyectos.js
> ```
>
> Son **14 comprobaciones** a 390 px de ancho, que es un teléfono, y deja una captura para verlo
> con los ojos. ✅ **El guion solo lee el mosaico y teclea en un campo**, así que se puede correr
> contra una máquina en uso: al revés del renglón 14, aquí queda cero rastro en los archivos del
> cliente.
>
> 🔴 **Tres ajustes antes de la primera corrida, y los tres fallan señalando el lugar equivocado:**
>
> - **El correo de la identidad va escrito dentro del guion** (`Tailscale-User-Login`, en las
>   primeras líneas). Con el correo de otra tailnet el lanzador contesta 403 y el guion se queda
>   esperando un mosaico que jamás llega. Va el correo del dueño de la tailnet del cliente.
> - **Pide al menos 4 proyectos para significar algo.** Con uno o dos, "filtrar recorta la lista"
>   pasa en verde por vacuidad, y eso se lee como si el filtro estuviera roto. El guion **para y lo
>   dice con palabras**, saliendo con código 2 en vez de reportar fallas falsas. Una instalación
>   recién hecha suele estar justo ahí: sembrar unas carpetas con su `CLAUDE.md` bajo la raíz de
>   proyectos, que además la deja más parecida a una máquina en uso.
> - **Si quien instala trabaja desde Windows**, la primera línea del guion busca Playwright en la
>   ruta global de Linux (`/usr/lib/node_modules/playwright`) y hay que apuntarla a donde viva ahí.
>   Lo cómodo es correrlo desde una máquina Linux, que es como se hizo.
>
> **Y la mitad del dedo, que es la que el cliente va a vivir:** desde el teléfono, teclear parte de
> un nombre, ver que los encabezados de Activos y Fijados se esconden y queda una sola rejilla,
> **esperar los 8 segundos del redibujado** y comprobar que lo tecleado y el recorte siguen ahí.
> Si a los 8 segundos reaparecen los proyectos escondidos, o vuelve el botón de "+ Nuevo proyecto",
> esa copia del lanzador es anterior al 17 de agosto de 2026.

> ⚠️ **El 403 del renglón 4 es la respuesta correcta, no una falla.** La raíz exige la
> identidad que inyecta Tailscale, que en local no existe. **Medir salud con `/salud`, nunca
> con la raíz.**

> ⚠️ **La prueba de la bitácora hay que pedirla bien o parece rota.** El umbral cuenta
> **llamadas de herramienta, no archivos**: pedir "crea seis archivos" lo resuelve el
> asistente con **un solo comando**, y el mecanismo se calla con razón. Pedirlo así: *"usa la
> herramienta Write seis veces seguidas, una por archivo, sin comandos de shell"*. Al
> terminar el conteo **vuelve a cero**, que es la guarda contra el bucle de reescribir la
> bitácora para callar una alarma que la propia escritura enciende: lo que hay que mirar es
> el tamaño del `CLAUDE.md`.

**Si el teléfono dice que no carga o que está fuera de línea:** revisar **primero el
Tailscale del teléfono**, que es la causa más probable y la más barata de descartar. Después,
de más barato a más caro: `tailscale status` debe listar el teléfono, `tailscale dns status`
debe traer MagicDNS encendido, y `tailscale serve status` debe mostrar la publicación.

**Si la sesión no cierra** y sigue apareciendo conectada, el supervisor no está cerrando por
`/exit`: revisar que `pywinpty` esté instalado.

**Dónde mirar cuando la bitácora no cuadra:** todo vive en
`%USERPROFILE%\.cache\claude-bitacora\`. `cierres.log` es el canal de estado, una línea por
evento, y distingue "no había nada que hacer" de "lo intenté y se rompió".
`escritor-<sid>.log` es la transcripción de la sesión que escribió esa bitácora. Los de
transcripción se borran solos a los tres días; `cierres.log` no.

> ⚠️ **`rc=0` no significa que se haya escrito.** Verificar siempre el archivo, no el código
> de salida. Un cierre que falló con `rc=0` costó un diagnóstico completo el 2 de agosto.

## 8. Lo que NO resuelve esta instalación


Decirlo antes de instalarla en casa de un cliente:

- **La puerta es la identidad de Tailscale**, y solo eso. El lanzador sí valida quién entra
  (encabezado `Tailscale-User-Login`, y `%USERPROFILE%\.config\rc-launcher\acceso.json`
  extiende la lista), pero **quien esté en la tailnet y en esa lista puede lanzar sesiones
  con acceso completo al disco de esa persona**. Es el permiso más fuerte del montaje. Para
  un cliente cuyo departamento de Sistemas puede meter otros equipos a la red, conviene
  revisar `acceso.json` explícitamente en vez de confiar en la pertenencia a la tailnet.
- **Si la laptop se reinicia y nadie inicia sesión, no hay lanzador.** El modo desatendido de
  Tailscale sube la red, pero **no las tareas de usuario**, que necesitan contraseña
  guardada. Es el hueco conocido de Windows y no tiene arreglo limpio desde aquí.
- **La bitácora la escribe un modelo**, así que consume tokens de la cuenta del usuario cada
  vez que cierra una sesión con trabajo pendiente.
- **Depende de cosas que no controlamos.** Si la empresa bloquea Tailscale, las instalaciones
  globales o los servicios sin firmar, este montaje no tiene rodeo técnico. El paso 0 existe
  para descubrirlo antes de la cita, no durante.
- **La tailnet queda a nombre del cliente**, o sea que él administra sus interruptores y sus
  dispositivos. Es deliberado, pero significa que un cambio suyo puede tumbar el acceso sin
  que nosotros nos enteremos.
- **Un proyecto cuya carpeta se renombre con la sesión viva** desaparece del grid y esa
  sesión queda inmatable desde el teléfono. Hay que cerrarla desde la máquina.

## Errores comunes


| Síntoma | Causa real |
|---|---|
| "No me funcionó el paso 1" | `winget` dejó el PATH viejo en esa consola; abrir una nueva |
| `python` abre la Microsoft Store | Alias de ejecución de Python activos en Configuración |
| La primera sesión se queda colgada | Claude Code no pasó por su primer arranque; está detenido en una de las cinco preguntas, sin ventana donde verlas. Ver A2 |
| Un proyecto nuevo se cuelga la primera vez, incluso con la raíz confiada | Si pasa con TODOS los proyectos nuevos: la confianza se aceptó dentro de un proyecto y no en la raíz, no se hereda (ver A2). Si es solo el primero de un proyecto creado desde "+ Nuevo proyecto": es normal, contestar desde el teléfono o adelantarlo abriendo la primera sesión desde la computadora (ver B2) |
| Un proyecto que llevaba meses trabajando empieza a pedir la confianza | Le corrieron `git init`, y la herencia se corta en la raíz de cada repositorio. El flag de permisos omitidos tampoco lo salta. Se siembra la llave con el fragmento de A2 |
| Se le pidió a un agente que hiciera el primer arranque y se quedó a medias | A2 no se puede delegar; exige a una persona con la sesión al frente, sobre todo para la pregunta 4. Ver A2 |
| Aparece "acepta toda la responsabilidad" y nadie sabe si contestar | Es la pregunta 4 de A2 (modo sin confirmaciones); solo la acepta el dueño de la máquina, en persona. Ver A2 |
| La sesión no cierra desde el teléfono | Falta `pywinpty` |
| La tarea programada "nunca ha ejecutado" (`267011`) | Nació con `LogonType: Interactive` y nadie tiene sesión iniciada. Pasa con `/SC ONSTART` y también con `/SC MINUTE`, con `/RU` y `/NP` incluidos. Se arregla registrándola con `New-ScheduledTaskPrincipal -LogonType S4U`, como hacen B3 y B3b |
| Reiniciar la tarea no hace nada | `schtasks /run` sobre una tarea corriendo no reinicia; primero `/end` |
| Se actualizó el código y el lanzador sigue con el viejo (una ruta nueva da 404) | `schtasks /end` deja vivo al `python` hijo, que conserva el puerto. Matar por PID al que escucha el 8765 y volver a lanzar la tarea. Ver B3 |
| El nodo desaparece de la tailnet en la pantalla de contraseña | Falta `tailscale set --unattended=true` |
| La raíz da 403 y parece roto | Es correcto sin identidad de Tailscale; medir con `/salud` |
| Acentos rotos en el `CLAUDE.md` global | Se guardó en cp1252. Abrir con VS Code o Notepad++ y guardar como UTF-8, o desde PowerShell: `$f="$env:USERPROFILE\.claude\CLAUDE.md"; $c=[System.IO.File]::ReadAllText($f,[System.Text.Encoding]::GetEncoding('cp1252')); [System.IO.File]::WriteAllText($f, $c, [System.Text.Encoding]::UTF8)` |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| "Le pedí sus pendientes y no sabe qué son" | Falta la sección de A7 en `%USERPROFILE%\.claude\CLAUDE.md` |
| Los conectores no aparecen en `/mcp` | La sesión no está autenticada con la suscripción. Correr `/status`. Ver A5b |
| No deja conectar Gmail desde `/mcp` | Es lo esperado: va en claude.ai, no en la terminal. Ver A5a |
| El borrador salió sin el archivo adjunto | Limitación vigente del conector; se adjunta a mano antes de enviar. Ver A5c |
| Pide una llave de DeepInfra que el cliente no esperaba | No se le explicó A8 en la entrega. Es opcional y con su propia cuenta; explicarle y seguir cuando la tenga |
| La misma transcripción se ofrece en cada sesión | No se movió a `Procesadas`: la subcarpeta falta, se llama distinto, o el conector no completó el movimiento. Ver B7c |
| Hay transcripciones en Drive y la sesión arranca sin mencionarlas | La sesión se abrió a mano y falta el gancho de B8b, falta `transcripciones.json`, o la copia del lanzador es anterior al 22 de septiembre de 2026. Ver B7 |
| Hay un bloque en curso y la sesión arranca sin ofrecerlo | A la sesión le falta una vía al calendario (ver B8a), falta `calendario.json`, el título del evento no empieza con el nombre de la carpeta seguido de `·`, el evento es de día completo, o la copia del lanzador es anterior al 25 de septiembre de 2026. Ver B8 |
| La sesión espera el sí de "Gustavo" | La copia del lanzador trae el nombre fijo en la instrucción. Llevarle una corregida con B2b. Ver B8c |
| La sesión abierta con `claude` directo arranca sin aviso, y desde el teléfono sí lo trae | Al gancho le falta el `-X utf8`: su salida llega en cp1252 y Claude Code la descarta en silencio. Ver B8b |
| El aviso sale dos veces en la sesión del teléfono | La marca `RC_LANZADOR` se pierde entre el supervisor y `claude.exe`. Es inofensivo; reportarlo para arreglarlo en el lanzador. Ver B8c |
| `Windows is not supported. Use WSL` al instalar Composio | Es lo esperado: en Windows va por el servidor MCP remoto. Ver A5e |
| `soffice` o `tesseract` "no se reconoce" | Se instalan en `Program Files` sin registrarse en el PATH. Ver A4b |
| `module 'socket' has no attribute 'AF_UNIX'` | Se corrió un script auxiliar del plugin, que es solo para Linux. Usar `soffice` directo. Ver A4f |
| `Cannot find module 'docx'` o `'pptxgenjs'` | Falta `NODE_PATH`. Ver A4d |
| El Excel sale con las celdas de resultado vacías | Falta LibreOffice o no se recalculó. `openpyxl` escribe la fórmula pero no la evalúa. Ver A4g |
| El OCR devuelve basura en un documento en español | Falta `spa.traineddata`; el paquete solo trae inglés. Ver A4c |
| `presentacion-elegante` no produce nada útil | Falta el plugin `document-skills`; la skill no tiene a qué delegar. Ver A4e |
