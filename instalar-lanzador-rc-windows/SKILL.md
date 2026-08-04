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
| Subir archivos desde el teléfono | Caen en `bandeja/` dentro del proyecto |
| **La bitácora se escribe sola** | Al cerrar, el `CLAUDE.md` del proyecto queda actualizado sin pedirlo |
| **Documentos de oficina de verdad** | Pide un Word, un Excel con fórmulas o una presentación y salen archivos que abren en Office |

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

> ⚠️ **Los cinco renglones dependen de la empresa del cliente, no de nosotros.** Si alguno
> truena, el problema es de gestión, no técnico, y conviene plantearlo así desde el principio
> en vez de intentar rodearlo.

---

# FASE A · La base

**Lo que deja instalado:** Claude Code funcionando, la carpeta de proyectos, la bitácora
automática y el runtime que necesitan las skills de documentos.
**Corresponde al módulo 1 del programa.**

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

> ⚠️ **La confianza de la carpeta se hereda del padre, y por eso hay que contestarla parado
> en la raíz de proyectos.** Si se contesta dentro de un proyecto, **cada proyecto nuevo que
> se cree desde el teléfono se vuelve a atorar** en esa misma pregunta, invisible otra vez.
> Verificado en Linux, en las dos direcciones: con solo un proyecto confiado, uno nuevo se
> detuvo; con la raíz confiada, uno recién creado arrancó directo al prompt.

## A3. La bitácora automática


Un único archivo de Python, biblioteca estándar, **el mismo que corre en Linux**.

```powershell
$hooks = "$env:USERPROFILE\.claude\hooks"
New-Item -ItemType Directory -Force -Path $hooks
Copy-Item <origen>\bitacora\bitacora.py $hooks\bitacora.py
```

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

Copiar la carpeta del lanzador a `%USERPROFILE%\rc-launcher\` (los `.py` y `templates\`), y
crear la raíz de proyectos:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\claude"
cd $env:USERPROFILE\rc-launcher
python -m pytest -q        # deben pasar todas
python app.py              # debe quedarse escuchando; Ctrl+C para salir
```

La raíz **tiene que ser** `%USERPROFILE%\claude`: `sessions.py` la calcula así y no es
configurable sin tocar código.

## B3. Arranque automático


Un `.cmd` envoltorio y una tarea programada al iniciar sesión:

```powershell
@"
@echo off
cd /d "%USERPROFILE%\rc-launcher"
"$((Get-Command python.exe).Source)" app.py
"@ | Out-File "$env:USERPROFILE\lanzador.cmd" -Encoding ascii

schtasks /Create /TN "rc-launcher" /TR "`"$env:USERPROFILE\lanzador.cmd`"" /SC ONLOGON /F
schtasks /Run /TN "rc-launcher"
```

> ⚠️ **No usar `/SC ONSTART` con una cuenta de usuario.** Se crea, pero **nunca corre**: sin
> contraseña guardada el Programador la deja en "no ha ejecutado" (resultado `267011`) y no
> avisa. Con `ONLOGON` sí funciona, a cambio de exigir que alguien inicie sesión.

> ⚠️ **`schtasks /run` NO reinicia una tarea que ya corre.** Contesta "is currently running"
> y no hace nada. La secuencia correcta es `schtasks /end` y luego `schtasks /run`.

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

Crear `%USERPROFILE%\.claude\CLAUDE.md` con:

```markdown

## La bandeja: archivos que subo desde el teléfono


Cada proyecto puede tener una carpeta `bandeja/` en su raíz. Ahí es donde el lanzador rc deja
lo que subo desde el celular: fotos, audios de junta, PDFs, capturas.

**Si menciono "la bandeja", me refiero a esa carpeta del proyecto en el que estás, no a un
correo ni a nada de Gmail.** Revisar `bandeja/` del proyecto actual y trabajar con lo que
haya ahí.

Está en el gitignore, así que no aparece en `git status`. Al terminar de usar un archivo, yo
decido qué hacer con él desde el menú del lanzador, **no moverlo ni borrarlo por iniciativa
propia**, salvo que lo pida.
```

> ⚠️ **Guardarlo en UTF-8, no en el default del Bloc de notas.** Claude Code lo lee como
> UTF-8; en cp1252 los acentos llegan rotos. Con PowerShell: `Set-Content -Encoding utf8`.

## 7. Verificación, en orden

> **Cómo se reparte por fases:** los renglones 1, 2, 7 y 8 cierran la **fase A** (el servicio
> local, la bitácora y el runtime de documentos); del 3 al 6 cierran la **fase B**, y
> necesitan el teléfono. Si solo se contrató la fase A, la verificación termina en el 8 y eso
> es una entrega completa.


| # | Qué | Cómo | Esperado |
|---|---|---|---|
| 1 | La app responde | `Invoke-WebRequest http://127.0.0.1:8765/salud` | 200 |
| 2 | La puerta cierra | `Invoke-WebRequest http://127.0.0.1:8765/` | **403** |
| 3 | Se ve desde el teléfono | abrir la URL de la tailnet | aparecen los proyectos |
| 4 | Lanza | tocar un proyecto → "Nueva sesión" | en 5 s el botón queda encendido y la sesión aparece en la app de Claude |
| 5 | Cierra | tocar el proyecto → "Terminar sesión" | desaparece de la app |
| 6 | Retoma | tocar un proyecto apagado | lista sus sesiones previas |
| 7 | La bitácora | ver el recuadro de abajo, que tiene truco | el `CLAUDE.md` de ese proyecto trae una entrada nueva |
| 8 | El runtime de documentos | las cinco pruebas de A4g | los cinco archivos salen bien, **con el Excel trayendo resultados y no celdas vacías** |

> ⚠️ **El 403 del renglón 2 es la respuesta correcta, no una falla.** La raíz exige la
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
| La primera sesión se queda colgada | Claude Code no pasó por su primer arranque; está detenido en una de las cinco preguntas, sin ventana donde verlas. Ver 1b |
| Cada proyecto nuevo se cuelga la primera vez | La confianza se aceptó dentro de un proyecto y no en la raíz. Ver 1b |
| La sesión no cierra desde el teléfono | Falta `pywinpty` |
| La tarea programada "nunca ha ejecutado" (`267011`) | Se creó con `/SC ONSTART` sin contraseña guardada; usar `ONLOGON` |
| Reiniciar la tarea no hace nada | `schtasks /run` sobre una tarea corriendo no reinicia; primero `/end` |
| El nodo desaparece de la tailnet en la pantalla de contraseña | Falta `tailscale set --unattended=true` |
| La raíz da 403 y parece roto | Es correcto sin identidad de Tailscale; medir con `/salud` |
| Acentos rotos en el `CLAUDE.md` global | Se guardó en cp1252; usar `Set-Content -Encoding utf8` |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| `soffice` o `tesseract` "no se reconoce" | Se instalan en `Program Files` sin registrarse en el PATH. Ver A4b |
| `module 'socket' has no attribute 'AF_UNIX'` | Se corrió un script auxiliar del plugin, que es solo para Linux. Usar `soffice` directo. Ver A4f |
| `Cannot find module 'docx'` o `'pptxgenjs'` | Falta `NODE_PATH`. Ver A4d |
| El Excel sale con las celdas de resultado vacías | Falta LibreOffice o no se recalculó. `openpyxl` escribe la fórmula pero no la evalúa. Ver A4g |
| El OCR devuelve basura en un documento en español | Falta `spa.traineddata`; el paquete solo trae inglés. Ver A4c |
| `presentacion-elegante` no produce nada útil | Falta el plugin `document-skills`; la skill no tiene a qué delegar. Ver A4e |
