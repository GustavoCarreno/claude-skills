# A1 y A2 · Prerrequisitos y el primer arranque de Claude Code, con la confianza de la carpeta

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A1. Prerrequisitos
- A2. El primer arranque de Claude Code, que es donde más gente se atora

<!-- fin del encabezado agregado al partir -->

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
