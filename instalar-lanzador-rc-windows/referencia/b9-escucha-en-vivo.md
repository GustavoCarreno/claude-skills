# B9 · La escucha en vivo durante una junta (opcional)

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B9. La escucha en vivo
  - B9a. Lo que la sesión de escucha puede hacer con una orden, y lo que no
  - B9b. Lo que tiene que existir antes
  - B9c. El teléfono, que es donde se cae
  - B9d. Compartir las tarjetas con los presentes (opcional)
  - B9e. Verificar
  - B9f. Lo que cuesta, y lo que hay que decirle

<!-- fin del encabezado agregado al partir -->

## B9. La escucha en vivo

El menú de cada proyecto trae un cuadro **Escuchar**. Abre una pantalla oscura donde el
teléfono graba la conversación por pedazos; cada pedazo pasa por Whisper (la cuenta de A8) y
una sesión de Claude lo va leyendo con el proyecto a la mano. En la misma pantalla salen
**tarjetas**: una respuesta a lo que alguien preguntó, un dato del proyecto que viene al caso,
un aviso o un compromiso. Al tocar **Terminar** sale una tarjeta de cierre con los
compromisos, y la junta queda guardada en `transcripciones/` del proyecto, con su libreta
(compromisos, cifras, temas en espera y preguntas sin contestar).

**La sesión empieza a escuchar en unos 18 segundos** desde el 11 de octubre de 2026. Antes
esperaba a que terminara el resumen del proyecto, que tarda de 55 a 215 segundos; ahora el
resumen se prepara en paralelo, la barra dice «Resumen del proyecto en camino», y mientras
llega la sesión contesta buscando en la carpeta del proyecto. La tarjeta de presentación sale
cuando el resumen está listo.

Los botones de abajo cambian cómo se usa:

| Botón | Qué hace |
|---|---|
| **Atiende lo dicho** | Corta el pedazo en curso y le pide a la sesión atención sobre lo que se acaba de decir. Toda marca lleva tarjeta; medido el 2 de octubre de 2026, la tarjeta llega en una mediana de 9 segundos. Hasta el 11 de octubre de 2026 se llamaba «Atender lo dicho» |
| **Atiende lo que diré** | **Se mantiene presionado** mientras el cliente le habla al asistente, y al soltar se envía. Mientras se sostiene, la grabación de la junta se pausa y el botón dice «Escuchando… suelta para enviar»; al soltar dice «Atendiendo…» hasta que llega la tarjeta. Lo que se dice ahí es una **orden**: una pregunta o un encargo (ver B9a). La respuesta sale siempre con el rótulo *Solo tú*, aunque la junta comparta tarjetas. Un toque de menos de medio segundo se descarta, y a los 60 segundos se envía solo |
| **Voz para «Atiende lo que diré»** | Interruptor en la portada y en el menú ⋮, apagado de entrada. Prendido, la respuesta a cada orden **se oye** en el teléfono además de escribirse, y el botón dice «🔊 Atiende lo que diré». Las demás tarjetas siguen en silencio. Medido en Windows el 11 de octubre de 2026: la voz suena de 7 a 18 segundos después de la tarjeta (en Linux, unos 3.5). La voz se salta las comillas y los símbolos: conserva acentos, ñ y los signos de pregunta y admiración, los guiones largos, los paréntesis y el punto medio se vuelven pausa, PO-26-002 se dice «PO 26 002» y % se dice «por ciento» |
| **Compartir** y **Compartir todo** | Abren el menú de compartir del teléfono con una tarjeta o con todas. Corre en el navegador, sin pasar por el servidor |

Las ligas que traiga una tarjeta (un documento de Drive, una paginita) se pueden tocar.

**Cero pasos de instalación del lado del lanzador:** llega con el código de B2 o de B2b.

### B9a. Lo que la sesión de escucha puede hacer con una orden, y lo que no

Lo único que entra a la sesión de escucha es el audio, así que cualquiera en la sala puede
dictarle una instrucción en voz alta. Por eso hay dos reglas, y la segunda es la que la
garantiza:

1. **La sesión actúa solo con una orden**, o sea con lo que llega del botón «Atiende lo que
   diré», que sostiene el cliente. Lo que oye en la plática nunca dispara una acción, aunque
   alguien en la sala la pida.
2. **Corre con permisos cerrados** (desde el 5 de octubre de 2026): lo que está fuera de su
   lista se le niega en silencio, sin preguntar. Y cada comando que escribe algo **exige una
   orden pendiente del botón**: sin ella sale con código 3 y se niega.

Desde el 11 de octubre de 2026 una orden puede **actuar**, además de contestar:

| Con una orden puede | Queda negado siempre |
|---|---|
| Leer la junta y los archivos del proyecto | Leer cualquier otro archivo de la máquina |
| Escribir su libreta y las tarjetas | Escribir o borrar en el proyecto, salvo los recados de abajo |
| Buscar en internet | Abrir conexiones por su cuenta (`curl` y parecidos) |
| Leer el correo del cliente, por persona o por dominio | Mandar, responder o reenviar correo |
| **Dejar un borrador de correo** en su buzón, que el cliente revisa y manda él | Mandar o borrar un borrador |
| Leer el calendario | Borrar eventos o contestar invitaciones |
| **Crear y mover eventos**, en Google Calendar y en Outlook. **Los invitados reciben aviso del cambio**, y la lista de invitados queda como estaba | |
| **Buscar, leer y crear documentos en Drive** (o buscar en SharePoint). Un documento nuevo va a la raíz con un nombre que empieza con el proyecto, y la tarjeta trae la liga | Compartir, mover, cambiar o borrar archivos |
| **Dejar un recado en `pendientes.md`**: en una tarea si su título se reconoce sin duda, o en «Dicho del proyecto». Es la misma escritura que «Dejar retro» del teléfono, y solo agrega | |
| **Buscar y generar paginitas**, solo si la máquina tiene `~/.config/paginita/credentials`. La que genera sale cifrada, con su clave en la liga | Borrar paginitas |

> ⚠️ **Al 11 de octubre de 2026 la instrucción le pide a la sesión poner un evento nuevo en el
> calendario «Trabajo» cuando la orden omite en cuál**, que es el calendario de quien la
> construyó. En una cuenta sin ese calendario, el destino de un evento nuevo está sin medir.
> Hasta que se corrija en el lanzador, conviene que el cliente diga en la orden en qué
> calendario lo quiere, y probarlo en B9e.

Si la orden deja duda (dos eventos posibles, una hora que no se entendió), la sesión **pregunta
en la tarjeta** y espera otra orden. Procesar una transcripción se queda fuera de la junta: la
orden queda como recado y la procesa la siguiente sesión normal.

**Cómo deja los borradores.** Primero intenta con `gws`; si `gws` falta en la máquina (código 4),
usa el conector de Gmail o de Outlook de claude.ai (A5). **En la máquina de un cliente lo normal
es el conector**, y funciona igual. `gws` directo queda fuera de su lista, así que nunca le sirve
para mandar.

Medido el 11 de octubre de 2026 en Linux con una sesión real, desde que se suelta el botón hasta la
tarjeta: crear un evento 13.5 s, moverlo 13 s, un borrador 14 s, un recado 7.5 s, buscar una
paginita 10.5 s y generarla 17.5 s. Y medido con `claude -p`: los permisos niegan las variantes de
un comando permitido que llevan `>`, `;`, `$(...)` o `&&`.

> ⚠️ **Lo que sigue abierto, y conviene decírselo al cliente:** cuando la junta comparte sus
> tarjetas con los presentes (B9d), un dato que la sesión saca de los archivos del proyecto
> puede llegar a ellos, aunque sea interno. Lo del correo y el calendario se queda privado
> siempre. Hasta que eso cambie, **compartir con los presentes conviene solo en juntas donde
> todo lo escrito en el proyecto se puede saber**; en las demás, la escucha se usa sin compartir
> y las tarjetas se quedan en el teléfono del cliente.

### B9b. Lo que tiene que existir antes

| Pieza | De dónde sale | Si falta |
|---|---|---|
| Git for Windows, con su Git Bash | A1 | La sesión corre sus comandos en Git Bash: leer la junta y escribir tarjetas |
| Claude Code al día, con sesión iniciada y la herramienta Monitor | A2 | Con una versión vieja la sesión arranca sin el modo de permisos cerrados. Medido con la 2.1.290 |
| La llave de DeepInfra | A8 | Cada pedazo de audio pasa por Whisper. Sin llave, la pantalla lo dice en la portada |
| La skill `kokoro-deepinfra` | A8, junto con Whisper | Solo para la voz. Usa la misma llave. Sin ella, la tarjeta llega igual y la barra dice que la voz falló |
| Los conectores de claude.ai | A5 | Para las órdenes que actúan: **Calendar** para eventos, **Gmail** (u Outlook) para borradores, **Drive** para documentos. El que falte se lleva esas órdenes, y lo demás funciona |
| `gws` | Opcional | Sin él los borradores van por el conector. **Para un cliente, lo normal es sin `gws`** |
| `%USERPROFILE%\.config\paginita\credentials` | Opcional, la skill `paginita-publicar` | Sin el archivo la sesión carece de la instrucción y del permiso de paginita, y lo demás queda igual |
| El lanzador publicado por HTTPS | B4 | Android da el micrófono solo a una página segura, y `tailscale serve` es la que la vuelve segura |

> 📌 **En Windows la sesión de escucha la hospeda el mismo supervisor de B3** que mantiene vivas
> las sesiones de trabajo, en su modo para la escucha, y su ficha queda en la carpeta de la junta
> para que el mosaico la ignore. **Terminar le escribe `/exit`** y, si no cierra, la apaga a la
> fuerza. Y el comando de tarjetas va con la ruta real de Python, porque en Windows `python3` es
> el acceso directo de la tienda de Microsoft.

### B9c. El teléfono, que es donde se cae

Lo que salió midiendo, y conviene hacerlo con el cliente antes de su primera junta:

1. **Chrome en el teléfono.** Es el navegador con el que se midió.
2. **El permiso del micrófono se da una vez por sitio, y conviene darlo antes:** abrir la
   pantalla, tocar empezar y escoger *Allow while visiting the site*. Una ventana flotante de
   otra aplicación encima (un chat, un lector de pantalla) bloquea ese diálogo.
3. **La pantalla del teléfono tiene que quedar encendida y la página a la vista.** Con la
   pantalla apagada el micrófono sigue grabando, pero el envío se congela y el audio llega de
   golpe al volver a prenderla, o sea que las tarjetas llegan tarde.
4. **Al empezar, la sesión escucha en unos 18 segundos.** El resumen del proyecto llega
   después, y la barra lo dice mientras tanto. La espera de uno a cuatro minutos que había antes
   del 11 de octubre de 2026 desapareció.
5. **«Atiende lo que diré» se mantiene presionado.** En Chrome de Android el menú del teléfono
   queda anulado sobre ese botón, así que sostenerlo funciona (probado por Gustavo el 11 de
   octubre de 2026). Conviene que el cliente lo ensaye una vez antes de la junta.
6. **La voz suena sola**, porque en esa página ya se tocaron Empezar y el botón. Si Chrome se
   niega, la tarjeta trae **▶ Oír** y la barra pide tocarlo. Para que se oiga, el volumen de
   medios del teléfono tiene que estar arriba.
7. **Un correo se dicta mal.** Whisper pierde la palabra «arroba», así que «gustavo arroba
   carreno punto com» llega como «gustavo.carreno.com». En una orden de borrador conviene nombrar
   a la persona («déjale un borrador a Arturo Ledesma») para que la sesión busque su correo, o
   revisar el destinatario en la tarjeta antes de mandar el borrador.

> 📌 **Whisper inventa "Gracias." en el silencio** y devuelve texto vacío en un pedazo sin voz.
> El lanzador ya descarta las dos cosas, así que en pantalla se ven como silencio y no como
> error.

### B9d. Compartir las tarjetas con los presentes (opcional)

Con esto, al empezar aparecen dos casillas, **Mandar las tarjetas a los presentes** e
**Incluir los avisos**, y un recuadro con un código QR. Quien lo escanea recibe las tarjetas en
su teléfono por ntfy (la misma aplicación de B3b), en un tema con nombre al azar.

**Exige un servidor ntfy propio**, porque el público de `ntfy.sh` carece de los permisos que
esto usa: lectura anónima de los temas `junta-*` y un usuario que solo escriba en ellos.
Teniéndolo, la configuración es un archivo:

```powershell
$c = "$env:USERPROFILE\.config\rc-launcher\compartir.json"
'{"servidor": "https://<su-servidor-ntfy>", "usuario": "<usuario-que-solo-escribe-en-junta>", "clave": "<su-clave>"}' |
  Set-Content -Path $c -Encoding utf8
```

**Sin el archivo, la pantalla queda como antes**, sin las casillas.

> 📌 **Lo que sale del correo o del calendario nunca se manda solo.** Esas tarjetas llevan el
> rótulo *Solo tú*, y para mandarlas está el botón **Mandar a los presentes** de cada una.
> Importa porque la sesión de escucha sí lee el correo y el calendario del cliente cuando el
> tema lo pide. Lo que viene de los archivos del proyecto sí se manda, así que un dato interno
> del proyecto puede llegar a los presentes: conviene decírselo al cliente.
>
> ⚠️ **Quien escanea tarde se pierde lo anterior**, porque cada tarjeta se publica sin
> guardarse en el servidor. Y en iPhone el aviso llega solo si la página se agregó a la
> pantalla de inicio.

> 🔴 **Aviso para quien pruebe esto a mano:** un guion que importe `escucha_ntfy` sin fijar
> antes `escucha_ntfy.CONFIG` a una ruta temporal escribe sobre el `compartir.json` real.
> Pasó el 28 de septiembre de 2026.

### B9e. Verificar

**Medido el 5 de octubre de 2026 en `win11-dogfood`**, con una sesión de escucha real lanzada por
el mismo código que usa el lanzador: la tarjeta de presentación salió a los 16 segundos, una
pregunta dictada se contestó con la cifra exacta en segundos, el compromiso salió como tarjeta, la
marca de "Atender lo dicho" se contestó, los acentos llegaron intactos y **Terminar** dejó la sesión
apagada. La batería del lanzador pasa completa en Windows (1187 pruebas).

1. **Con navegador, desde la máquina de quien instala**: los guiones
   `docs/superpowers/verificacion/2026-09-26-escucha-en-vivo/guion.js` y
   `docs/superpowers/verificacion/2026-09-27-escucha-compartida/guion.js` de la copia del
   lanzador, cada uno con su `servidor_de_prueba.py`. El segundo necesita `RC_IDENTIDAD` con el
   correo de la tailnet.
2. **Con el dedo, que es lo único que prueba el micrófono:** en un proyecto de prueba, abrir
   Escuchar desde el teléfono, dar el permiso, decir en voz alta una pregunta cuya respuesta esté
   en el `CLAUDE.md` del proyecto y tocar **Atiende lo dicho**. Debe salir una tarjeta con la
   respuesta. Luego **Terminar**, y ver la tarjeta de cierre y el archivo nuevo en
   `transcripciones/`.
3. **Atiende lo que diré, con la voz prendida:** en la portada prender **Voz para «Atiende lo que
   diré»**, empezar, sostener el botón, preguntar algo del `CLAUDE.md` del proyecto y soltar.
   Debe decir «Atendiendo…», llegar la tarjeta con el rótulo *Solo tú*, y oírse la respuesta.
4. **Una orden que actúe sobre algo desechable:** sostener el botón y pedir «déjale un recado
   al proyecto: prueba de la escucha». Debe aparecer en «Dicho del proyecto» de su
   `pendientes.md`. Si hay tiempo, pedir un evento de prueba para mañana, verlo en el
   calendario y borrarlo a mano. Y un borrador a la propia dirección del cliente, que se borra
   después: así se prueba el camino del conector.
5. **Compartir**, también con el dedo: el botón abre el menú de compartir del teléfono.


> ✅ **La orden, la voz y las órdenes que actúan, medidas en Windows el 11 de octubre de 2026**
> en `win11-dogfood`, con la VM igual que la de un cliente (sin `gws` y sin paginita) y Gustavo
> desde el teléfono. El resumen llegó a los 25 segundos y la primera orden se contestó antes de
> eso. De soltar el botón a la tarjeta: una pregunta del `CLAUDE.md` en 10 s, un recado en 8 s,
> un borrador **por el conector de Gmail** en 17 s, y un evento en el calendario principal en
> 12 s. **Las cinco respuestas se oyeron**, o sea que el proceso de la voz sobrevive en Windows y
> encuentra la skill de Kokoro en `%USERPROFILE%`. **En Windows la voz tarda más:** de 7 a 18
> segundos después de la tarjeta, contra 3.5 en Linux. La batería pasa completa (1315 pruebas ese día, 1329 con la ficha de la tarde).

> ✅ **El micrófono del teléfono contra Windows, medido por Gustavo el 5 de octubre de 2026.**
> La primera prueba cazó un defecto: la transcripción llamaba a `python3`, que en Windows es el
> acceso directo de la tienda, y cada pedazo salía con *"Python was not found"*. Con el lanzador
> corregido (ese mismo día), la pregunta dicha en voz alta llegó transcrita con sus signos y la
> marca se contestó con una tarjeta. **Una copia del lanzador anterior a esa fecha transcribe cero
> en Windows**, incluidos los recados dictados del teléfono: actualizarla con B2b.

### B9f. Lo que cuesta, y lo que hay que decirle

- **La transcripción se paga en DeepInfra**, igual que en A8: una junta de una hora sale en
  alrededor de un centavo de dólar.
- **La voz se paga en DeepInfra** con la misma llave: 0.62 dólares por millón de caracteres,
  o sea unas dos milésimas de centavo por respuesta.
- **La sesión de escucha gasta del plan de Claude del cliente** mientras dura la junta, como
  cualquier otra sesión.
- **Las órdenes de calendario les avisan a los invitados.** Si el cliente mueve una junta con
  terceros desde la escucha, ellos reciben el cambio por correo. Decírselo antes de su primera
  junta.
- **Un borrador nunca sale solo.** Queda en su buzón y lo manda el cliente.
- **El audio sale del teléfono hacia la máquina del cliente y de ahí a DeepInfra.** Es la misma
  revelación de A8c, y la de siempre con una grabación: **avisar a los presentes que se está
  escuchando** le toca al cliente.
