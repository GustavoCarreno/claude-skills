# Claude Skills — Gustavo Carreño

> Skills de Claude Code que uso a diario y comparto con colegas, clientes y amigos.

## ¿Qué es esto?

Este repo contiene un conjunto de **skills** que he escrito para mi propio uso con [Claude Code](https://www.anthropic.com/claude-code), y que comparto públicamente para quien quiera ampliar sus capacidades con Claude.

Una skill en Claude Code es un folder con un archivo `SKILL.md` adentro que contiene instrucciones especializadas. Cuando Claude Code detecta que una skill es relevante para la tarea actual, la carga y aplica sus instrucciones al responder. Es como darle a Claude un "manual de estilo" específico para cierto tipo de trabajo — puede ser escribir una carta formal, analizar un contrato, redactar un correo, o cualquier otra tarea repetible donde la estructura y el tono importan.

Si quieres usar estas skills, sigue la sección **Instalación** abajo.

## Instalación rápida — Windows

Abre **PowerShell** (o la terminal integrada de VS Code con perfil PowerShell) y corre:

```powershell
iwr -useb https://raw.githubusercontent.com/GustavoCarreno/claude-skills/main/install.ps1 | iex
```

Eso descarga el script, lo ejecuta, y deja las skills en `%USERPROFILE%\.claude\skills\`. Después corre `/exit` y luego `claude` dentro de Claude Code para que las cargue.

**Si PowerShell bloquea el script** con un error `SecurityError: UnauthorizedAccess`, corre primero este comando one-time:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Responde `Y` a la confirmación y después repite el `iwr ... | iex`. Esta configuración solo afecta a tu usuario, no al sistema, no requiere admin, y es la política que Microsoft recomienda para máquinas de desarrollo.

### Instalación explícita paso a paso — Windows

Si prefieres ver cada paso por separado, o el one-liner no te funciona:

```powershell
git clone https://github.com/GustavoCarreno/claude-skills $env:TEMP\claude-skills-tmp
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills" | Out-Null
Copy-Item -Recurse -Force "$env:TEMP\claude-skills-tmp\comunicados-formales-es-mx" "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force "$env:TEMP\claude-skills-tmp\comunicados-formales-respaldo" "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse -Force "$env:TEMP\claude-skills-tmp\youtube-research" "$env:USERPROFILE\.claude\skills\"
Remove-Item -Recurse -Force "$env:TEMP\claude-skills-tmp"
```

Clone al temporal, create skills dir, copy de las skills, cleanup. Funciona sin necesidad de ejecutar `install.ps1`.

**Requisito:** Git for Windows debe estar instalado. Si no lo tienes, bájalo de [git-scm.com/download/win](https://git-scm.com/download/win).

## Instalación — Linux / macOS

Abre una terminal y corre:

```bash
curl -fsSL https://raw.githubusercontent.com/GustavoCarreno/claude-skills/main/install.sh | bash
```

Eso descarga el script bash, lo ejecuta, y deja las skills en `~/.claude/skills/`. Después corre `/exit` y luego `claude` dentro de Claude Code para que las cargue.

## Catálogo de skills disponibles

### `comunicados-formales-es-mx`

Redacción de cartas y comunicados formales en el registro comercial-legal mexicano. Ideal para cartas a clientes, notificaciones contractuales, comunicaciones con stakeholders (brokers, inquilinos, proveedores) con gravedad media-alta donde el tono importa y la relación se quiere preservar.

Aplica la estructura clásica de carta formal mexicana — lugar y fecha, destinatario, referencia, saludo, cuerpo en 3-5 párrafos, cierre institucional, firma, bloque de acuse — y usa frases idiomáticas del registro mexicano como *"Por medio de la presente"*, *"En seguimiento a"*, *"Solicitamos atentamente su apoyo"*, *"Sin otro particular por el momento"*.

**Ejemplo de uso en Claude Code:**

> *"Carga la skill comunicados-formales-es-mx. Luego escríbeme una carta formal al inquilino de la nave 42 solicitándole ajustar el patrón de circulación de sus tractocamiones, referenciando la cláusula 4.2 del contrato, con tono colegial que preserve la relación. Contexto: llevan 3 años en el parque sin incidentes."*

### `comunicados-formales-respaldo`

Skill de respaldo para el momento Matrix: si la skill declarativa (`comunicados-formales-es-mx`) no produce suficiente diferencia visible, esta la reemplaza. En lugar de reglas, contiene **3 ejemplos completos** de cartas formales mexicanas que el agente imita directamente por pattern-matching:

1. **Observación contractual a broker intermediario** — tractocamiones dañando concreto, tono colegial, acuse de recibo
2. **Solicitud de aclaración a proveedor de mantenimiento** — impermeabilización incompleta, solicitud de visita técnica
3. **Notificación de cambio de condición a inquilino** — trabajos de rehabilitación vial, acceso temporal restringido

Ambas skills (`comunicados-formales-es-mx` y `comunicados-formales-respaldo`) se instalan automáticamente con el one-liner de instalación. Solo se activa una a la vez — usar la de respaldo solo si la primaria no produce mejora visible.

### `youtube-research`

Investigación de videos de YouTube desde Claude Code: extraer **transcripción** limpia, **metadata** (título, canal, duración, views, descripción) y **búsqueda** por query (top N videos sobre un tema). Útil para digerir un video sin verlo completo, resumir charlas largas, o investigar un tema sin salir del agente.

**Prerrequisito adicional:** instalar [yt-dlp](https://github.com/yt-dlp/yt-dlp). La skill te avisa si no está. Instalación:

- **Windows:** `winget install -e --id yt-dlp.yt-dlp --accept-source-agreements --accept-package-agreements --silent` (instala también `ffmpeg` como dependencia, útil si después quieres extraer audio)
- **Linux / macOS:** `pip install --user --break-system-packages yt-dlp`

**Ejemplos de uso en Claude Code:**

> *"Tráeme la transcripción de https://youtu.be/XXXXX y dame un resumen con insights, crítica y opinión."*

> *"Búscame los top 5 videos de YouTube sobre 'parques industriales en Mexicali' y dame la tabla con URLs."*

> *"De este video https://youtu.be/XXXXX, dame solo la metadata — no necesito el transcript."*

La skill incluye un helper Node (`clean-vtt.js`) que limpia los subtítulos VTT auto-generados de YouTube con el algoritmo canónico (última línea de cada cue + dedupe consecutivo). Funciona idéntico en Windows, Linux y macOS porque Node.js ya viene con Claude Code.

## Actualizar skills a la versión más reciente

Re-corre el mismo comando de instalación que usaste originalmente. El script sobrescribe cada skill con la versión más reciente del repo. No hay proceso separado de "update" — la instalación idempotente es el update.

## Licencia

[MIT](./LICENSE). Puedes usar, copiar, modificar y redistribuir estas skills libremente, solo preservando el aviso de copyright y la licencia. Sin warranty.

## Contribuir

Si eres cliente, colaborador o amigo y quieres proponer una skill nueva, abre un [issue](https://github.com/GustavoCarreno/claude-skills/issues) con la propuesta: qué hace la skill, para qué tipo de tarea aplica, y un ejemplo de uso. Si ya tienes el código, adelante con un PR.

Si quieres escribir skills propias para tu negocio (sin compartirlas aquí), Claude tiene documentación oficial en [support.claude.com/en/articles/12512198-creating-custom-skills](https://support.claude.com/en/articles/12512198-creating-custom-skills).

## Contacto

- **GitHub:** [@GustavoCarreno](https://github.com/GustavoCarreno)
- **Web:** [carreno.com](https://carreno.com)
