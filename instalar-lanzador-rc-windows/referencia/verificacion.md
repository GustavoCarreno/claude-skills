# 7 · La verificación completa, en orden

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- 7. Verificación, en orden

<!-- fin del encabezado agregado al partir -->

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
