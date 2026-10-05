# 7 · La verificación completa, en orden

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- 7. Verificación, en orden

<!-- fin del encabezado agregado al partir -->

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
