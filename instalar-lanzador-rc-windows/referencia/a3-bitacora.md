# A3 · La bitácora automática: bitacora.py, sus ganchos y bitacora.json

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A3. La bitácora automática
  - A3b. Los contactos que salen de cada sesión

<!-- fin del encabezado agregado al partir -->

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
(Get-Item "$hooks\bitacora.py").Length   # debe rondar los 54 KB, no 0
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
- **`respaldo`**: `true` sube cada proyecto a su repositorio privado de GitHub al cerrar
  cada sesión. De fábrica viene apagado; se enciende en A9.
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

### A3b. Los contactos que salen de cada sesión

Al cerrar, la bitácora revisa también si en la sesión apareció una persona con un dato para
localizarla (correo o teléfono), o un dato nuevo de alguien ya conocido (empresa, puesto, otro
teléfono). Con eso hace una de dos cosas:

| En la máquina | Qué pasa |
|---|---|
| Hay `gws` funcionando, que es el caso raro | Busca a la persona en Google Contacts, la crea si falta y le agrega solo los datos nuevos |
| Lo normal en un cliente | Escribe los contactos en `salida/contactos-AAAA-MM-DD.vcf` dentro del proyecto, agregando al final si ese archivo ya existe |

**Cero pasos de instalación:** viene dentro de `bitacora.py` desde el 5 de octubre de 2026.
Lo que sí toca es enseñarle al cliente a importar el archivo, que es un minuto en la
computadora:

1. Abrir `contacts.google.com`.
2. En el menú de la izquierda, **Importar**, escoger el `.vcf` y aceptar.
3. Revisar **Combinar y corregir**, donde Google junta los que ya existían.

> 📌 **Por qué un archivo y no directo a sus contactos.** Escribir en Google Contacts desde una
> sesión exige un cliente de Google Cloud por cuenta, que es justo la barrera que esta guía
> evita desde A5. Composio lo pide igual (medido el 5 de octubre de 2026), y los conectores de
> claude.ai cubren correo, calendario y Drive, sin contactos.

> ⚠️ **El archivo se queda fuera del repositorio**, porque `salida/` está en el gitignore de
> A6, y es lo correcto: trae datos de terceros. Y el lanzador sirve desde `salida/` solo
> audio, así que el `.vcf` se importa desde la computadora y no desde el teléfono.

Comprobar que el `bitacora.py` instalado ya lo trae (una copia vieja da `0`):

```powershell
@(Select-String -Path "$env:USERPROFILE\.claude\hooks\bitacora.py" -Pattern "contactos-").Count
```

