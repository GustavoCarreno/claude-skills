# B15 · La junta con guion, Dialogar, la voz y el mosaico (al 17 de noviembre de 2026)

Lo que el lanzador ganó del 22 de octubre al 13 de noviembre de 2026. Casi todo es código que
viaja con B2b, sin configuración; lo que pide un paso propio lo dice. **En Windows, cada pieza
lleva su estado medido**, porque varias se construyeron y probaron solo en Linux. Lo que diga
«sin medir» se le dice así al cliente, antes de prometérselo.

## Contenido de este archivo

- B15a. La escucha lee el evento de la junta y su guion
- B15b. El resumen de Escuchar, guardado y por diferencias
- B15c. Dialogar
- B15d. El botón atrás y la tarjeta que dice «Escuchando»
- B15e. «Abre» y el proyecto, por voz
- B15f. El rescate del toque y el mosaico ancho
- B15g. Dictar la descripción al crear un proyecto
- B15h. Opcional: la voz en la propia máquina (Kokoro)
- B15i. Opcional: el resumen por la API, con el crédito del plan
- B15j. Verificar

---

### B15a. La escucha lee el evento de la junta y su guion

Al tocar Empezar en Escuchar, junto con el resumen del proyecto corre una lectura aparte que
busca el evento del calendario en curso o de los próximos 30 minutos y saca dos tarjetas:
**«Junta en curso»** (quién, a qué hora, para qué) y **«Guion de hoy»**, si la descripción del
evento trae la liga a un guion. De una paginita del propio proyecto toma la fuente de la carpeta;
otra liga la abre con la herramienta de leer páginas web.

- **Requisito:** `calendario.json` de B8. Sin él, la lectura se salta y la escucha arranca igual.
- **En Windows va por el conector de Google Calendar de claude.ai**, porque `gws` falta.
- **Viaja solo `escucha_sesion.py`** con B2b.
- Medido en Linux: unos 114 s en un proyecto grande, en paralelo con el resumen.
- 🟡 **Windows: sin medir.**

**Lo que hay que decirle al cliente:** si quiere que la escucha llegue preparada, el evento de la
junta lleva en su descripción la liga al guion o a las notas. Es la costumbre que más rinde.

### B15b. El resumen de Escuchar, guardado y por diferencias

El resumen que Escuchar arma al empezar ya se guarda por proyecto, y la siguiente junta lo pone al
día leyendo solo lo que cambió en `CLAUDE.md`, `pendientes.md` y `contratos.md`.

- Se guarda en `%USERPROFILE%\.local\state\rc-launcher\resumenes\<proyecto>.json`, con el commit
  de git del proyecto.
- **Se rehace completo** sin guardado previo, con más de 7 días, con un cambio de más de 150 mil
  caracteres **o en un proyecto sin git**. O sea que A9 (el respaldo en GitHub, que pone git en
  cada proyecto) también es lo que abarata el resumen.
- **La sección Compromisos la arma el código** desde `pendientes.md`: lo que le deben al cliente,
  vencido primero, y lo que le deben a él, la espera más vieja primero. Sale igual con o sin
  modelo, y deja de perder vencidos.
- Secciones nuevas: quiénes son y quién decide, alcance, última junta, vocabulario del cliente y
  temas delicados (estos solo en tarjetas privadas).
- Viaja `resumen_proyecto.py`, nuevo.
- Medido en Linux: de 19 a 33 s. 🟡 **Windows: sin medir.**

### B15c. Dialogar

Botón nuevo junto a Escuchar. Es la escucha en modo conversación: no graba la sala; un toque
empieza a hablar y otro envía, **o se envía solo tras 1.5 s de silencio**, que detecta el propio
teléfono con un modelo pequeño de detección de voz (Silero). La sesión contesta solo lo que se
le pregunta, la respuesta se oye por partes (la primera oración suena primero), se guarda en
`transcripciones\AAAA-MM-DD-HHMM-dialogo.txt` del proyecto, y el diálogo se cierra solo tras 15
minutos sin turnos.

🔴 **La diferencia de Windows, dicha de frente.** En Linux, Dialogar habla con **la sesión real
del proyecto**, la que el cliente abrió con Nueva sesión, y conoce la conversación en curso. Eso
se construyó tecleando en `tmux`, que Windows no tiene. **En Windows, Dialogar abre una sesión
aparte**: conoce el proyecto (su `CLAUDE.md`, sus pendientes, sus archivos) y desconoce lo que se
dijo en la sesión abierta. Para el cliente se explica así: «Dialogar sabe todo lo de su proyecto,
y lo que platicó hace rato en la otra ventana no lo ve».

- **Viajan con B2b:** `dialogo_real.py`, `sesion_viva.py`, `vad.py`, la carpeta `vad\` (16.7 MB,
  con `SHA256SUMS`) y `templates\_escucha.html`. Sin `vad\` funciona igual, con el segundo toque
  para enviar.
- **La voz de la respuesta va por DeepInfra** (A8), porque la voz local de B15h es de Linux. Cuesta
  centavos por respuesta y tarda de 5 a 30 s en sonar, contra menos de un segundo en Linux con la
  voz local.
- **Un iPhone puede bloquear la voz** que no sale de un toque; ahí queda el botón «▶ Oír».
- 🟡 **Windows: sin medir.** En Linux, de 17 a 36 s de enviar a oír.

### B15d. El botón atrás y la tarjeta que dice «Escuchando»

- El botón atrás del teléfono, desde Escuchar o Dialogar, regresa a Proyectos y deja cerrada la
  pantalla; antes la volvía a abrir. Viaja con `templates\_escucha.html` y `templates\index.html`.
- La tarjeta del proyecto dice **«● Escuchando · N min»** o **«🎙 Dialogando · N min»** mientras
  dura.
- Es solo de la página, así que debería valer igual en Windows. 🟡 **Sin medir.**

### B15e. «Abre» y el proyecto, por voz

Dentro de «Filtrar proyectos» aparece un micrófono. Se dice **«Abre adco»** y se abre el menú del
proyecto, igual que al tocar su tarjeta.

- **Pide la llave de DeepInfra de A8.** Sin llave, el filtro se queda sin micrófono.
- La orden se entiende con reglas de texto, sin modelo de lenguaje; cuesta una fracción de centavo
  de dólar de transcripción.
- Viajan `orden_voz.py`, `templates\_script_voz.html` y la carpeta `vad\`.
- El detector de silencio arranca solo con la identidad que pone `tailscale serve` (B4); por la
  dirección local sin identidad se queda callado.
- Medido en Linux: 3.6 s del toque al menú, y Gustavo lo usa en su teléfono. 🟡 **Windows: sin
  medir.**

### B15f. El rescate del toque y el mosaico ancho

- **El rescate del toque:** al tocar una tarjeta sale «Abriendo <proyecto>…»; si el menú tarda 3 s
  se pide otra vez (hasta dos), y después se avisa. El redibujo de cada 8 s se detiene mientras el
  dedo está encima. Cada toque de más de 2 s se anota en
  `%USERPROFILE%\.local\state\rc-launcher\toques.jsonl`, que es lo primero que se revisa si el
  cliente dice que «a veces no abre». Cubre sobre todo al teléfono que llega por relevo de
  Tailscale, fuera de casa. Viaja `toques.py`, nuevo. 🟡 **Windows: sin medir.**
- **El mosaico ancho:** en una pantalla de 1,024 px o más, el mosaico llega a 1,600 px con las
  columnas que quepan (6 en un monitor grande, 2 en un teléfono). Es solo CSS. 🟢

### B15g. Dictar la descripción al crear un proyecto

En «+ Nuevo proyecto», bajo «¿De qué se trata?», un botón Dictar pasa a texto lo que se dice. Si
la transcripción falla, el audio se conserva en
`%USERPROFILE%\.local\state\rc-launcher\dictados\`. **Pide la llave de DeepInfra de A8**; sin ella
el botón se omite. 🟡 **Windows: sin medir.**

### B15h. Opcional: la voz en la propia máquina (Kokoro)

En Linux, la voz de las respuestas puede salir de la propia máquina, gratis y en uno a cinco
segundos, con DeepInfra de respaldo. **En Windows queda fuera por ahora:** el instalador es de
Linux y el servidor de voz usa un tipo de conexión que solo existe ahí. La voz sigue por
DeepInfra, que funciona y cuesta centavos. Si el cliente usa mucho Dialogar, es la razón de más
peso para recomendarle Linux.

### B15i. Opcional: el resumen por la API, con el crédito del plan

Los planes **Max, Ultra y Team** de Claude traen un crédito mensual de API (100, 200, y 20 o 100 por
asiento, respectivamente). Con una llave, el resumen de Escuchar va por la API: 25 s contra 116 s,
pagado con ese crédito. **Pro y Enterprise no traen crédito**: con ellos el resumen sigue por la
suscripción, sin pasos extra.

Si el cliente tiene uno de esos planes:

1. En la Consola de Anthropic (página distinta de la configuración de claude.ai), crear un espacio
   de trabajo propio con tope de gasto y una llave dentro de él.
2. **Comprobar que la Consola tenga cero tarjetas**, para que al acabarse el crédito la API se
   detenga en vez de cobrar.
3. Guardar la llave en `%USERPROFILE%\.config\anthropic\credentials`, con el renglón
   `ANTHROPIC_API_KEY=…`.

🔴 **La llave nunca va en una variable de entorno.** Con `ANTHROPIC_API_KEY` en el entorno, las
sesiones de Claude Code dejan la suscripción y cobran todo por API. El lanzador la lee solo de ese
archivo, anota el gasto y se detiene a los 140 dólares en el mes. 🟡 **Windows: sin medir.**

### B15j. Verificar

Con B2b hecho y la pestaña del teléfono **recargada** (la abierta antes sigue con el código viejo):

1. **Escuchar con guion:** crear un evento que empiece en 10 minutos, con la liga a una paginita
   del proyecto en la descripción. Tocar Escuchar, Empezar: deben salir «Junta en curso» y «Guion
   de hoy».
2. **El resumen por diferencias:** en un proyecto con git, dos escuchas seguidas. La segunda tarda
   menos y el archivo de `resumenes\` cambia de commit.
3. **Dialogar:** un toque, una pregunta, silencio: se envía solo y la respuesta se oye. Terminar, y
   el botón atrás desde Proyectos sale del lanzador.
4. **«Abre» por voz:** la página trae el micrófono en el filtro; decir «Abre» y el nombre de un
   proyecto abre su menú.
5. **Dictar al crear proyecto:** el texto dictado aparece en «¿De qué se trata?».
6. **Después de la batería de B2,** la lista de sesiones del lanzador y la app de Claude del
   cliente deben tener las mismas sesiones que antes. Una de más quiere decir que una prueba tocó
   sesiones reales de esa máquina.
