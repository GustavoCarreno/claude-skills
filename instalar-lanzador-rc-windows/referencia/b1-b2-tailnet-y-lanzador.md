# B1 y B2 · La tailnet, el lanzador y cómo actualizarlo (B2b)

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B1. La tailnet, desde cero
  - 2.1 Crear la tailnet y meter la laptop
  - 2.2 El teléfono, que es la mitad del montaje
  - 2.3 Los tres interruptores de la consola de administración
  - 2.4 Modo desatendido
- B2. El lanzador
  - B2b. Llevarle una versión nueva a una máquina que ya lo tiene

<!-- fin del encabezado agregado al partir -->

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

Al 5 de octubre de 2026 son 1171 pruebas (medidas en Linux). **El número crece con cada versión, así que no lo
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

> 📌 **Lo que una máquina ya instalada recibe con solo este paso**, sin configuración, porque
> es código del lanzador. Al 5 de octubre de 2026:
>
> | Mejora | Qué cambia para el cliente |
> |---|---|
> | El menú abre al primer toque | Antes, tocar una tarjeta del mosaico a veces se quedaba sin abrir el menú: el mosaico se redibuja cada 8 segundos y la orden de abrir se perdía con él. Le pasa sobre todo a un teléfono que llega a la máquina por relevo de Tailscale, que es lo normal fuera de la casa |
> | El menú pesa una fracción | Las respuestas viajan comprimidas y la sección de tareas hechas se pide solo al desplegarla. Un menú de 1.8 MB bajó a 87 KB |
> | Pendientes en cinco grupos | Ver A7b. Lo que urge sale arriba y abierto |
> | Lo urgente, numerado al abrir sesión | La sesión lista lo vencido o lo que vence en 7 días y pregunta por números cuáles ya se hicieron |
> | Sesiones previas con su título real | Antes todas se llamaban igual, porque Claude Code titula con el primer mensaje y el lanzador abre muchas con una instrucción de revisión. Ahora se ve el primer encargo del usuario, y las sesiones de fondo (la bitácora que se escribe sola) dejan de llenar la lista |
>
> **Las sesiones que ya estaban abiertas conservan el aviso de arranque viejo.** El nuevo sale
> en la siguiente que se abra.
> 
> ⚠️ **Sin medir en Windows todavía:** los títulos de sesiones previas y la compresión. Las dos son biblioteca estándar de Python y la misma lógica que en Linux, pero las 1171 pruebas corrieron solo ahí. Correrlas aquí con B2 y revisar los renglones 18 y 22 de la verificación.

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
