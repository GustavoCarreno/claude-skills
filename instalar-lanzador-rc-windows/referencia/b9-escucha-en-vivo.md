# B9 · La escucha en vivo durante una junta (opcional)

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B9. La escucha en vivo
  - B9a. Lo que la sesión de escucha puede hacer, y lo que no
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

Dos botones cambian cómo se usa:

| Botón | Qué hace |
|---|---|
| **Atender lo dicho** | Corta el pedazo en curso y le pide a la sesión atención sobre lo que se acaba de decir. Toda marca lleva tarjeta; medido el 2 de octubre de 2026, la tarjeta llega en una mediana de 9 segundos |
| **Compartir** y **Compartir todo** | Abren el menú de compartir del teléfono con una tarjeta o con todas. Corre en el navegador, sin pasar por el servidor |

**Cero pasos de instalación del lado del lanzador:** llega con el código de B2 o de B2b.

### B9a. Lo que la sesión de escucha puede hacer, y lo que no

Lo único que entra a la sesión de escucha es el audio, así que cualquiera en la sala puede
dictarle una instrucción en voz alta. **Desde el 5 de octubre de 2026 corre con permisos
cerrados**: lo que está fuera de su lista se le niega en silencio, sin preguntar.

| Puede | Queda negado |
|---|---|
| Leer la junta y los archivos del proyecto | Leer cualquier otro archivo de la máquina |
| Escribir su libreta y las tarjetas | Escribir o borrar en el proyecto |
| Buscar en internet | Abrir conexiones por su cuenta (`curl` y parecidos) |
| Leer el correo y el calendario del cliente | Mandar correos, crear o mover eventos |

Medido ese día con sesiones reales en Linux y en Windows: lo negado quedó negado, y la
pregunta, el compromiso y la marca se contestaron sin que la sesión pidiera un solo permiso.

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
4. **Al empezar hay una espera** mientras la sesión lee el proyecto: medida de 71 a 215
   segundos. La página lo dice ("alrededor de un minuto, a veces dos"), y conviene empezar
   antes de que llegue la gente.

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
   en el `CLAUDE.md` del proyecto y tocar **Atender lo dicho**. Debe salir una tarjeta con la
   respuesta. Luego **Terminar**, y ver la tarjeta de cierre y el archivo nuevo en
   `transcripciones/`.
3. **Compartir**, también con el dedo: el botón abre el menú de compartir del teléfono.

> ⚠️ **El micrófono del teléfono contra una máquina con Windows está sin medir todavía.** Lo
> medido es la sesión de escucha; la página es la misma que en Linux, pero falta probarla de
> punta a punta con el teléfono.

### B9f. Lo que cuesta, y lo que hay que decirle

- **La transcripción se paga en DeepInfra**, igual que en A8: una junta de una hora sale en
  alrededor de un centavo de dólar.
- **La sesión de escucha gasta del plan de Claude del cliente** mientras dura la junta, como
  cualquier otra sesión.
- **El audio sale del teléfono hacia la máquina del cliente y de ahí a DeepInfra.** Es la misma
  revelación de A8c, y la de siempre con una grabación: **avisar a los presentes que se está
  escuchando** le toca al cliente.
