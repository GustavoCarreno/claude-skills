# B15 · La junta con guion, Dialogar, la voz y el mosaico (al 17 de noviembre de 2026)

Lo que el lanzador ganó del 22 de octubre al 13 de noviembre de 2026. Casi todo es código que
viaja con B2b, sin configuración; lo que pide un paso propio lo dice. Todo se construyó y se
probó en Linux, en la máquina de Gustavo, y Dialogar y «Abre» por voz los usa él a diario desde su
teléfono.

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
- Va con `gws` donde exista, y si no con el conector de Google Calendar de claude.ai.
- **Viaja solo `escucha_sesion.py`** con B2b.
- Medido: unos 114 s en un proyecto grande, en paralelo con el resumen. Con el conector en vez de
  `gws`, sin medir.

**Lo que hay que decirle al cliente:** si quiere que la escucha llegue preparada, el evento de la
junta lleva en su descripción la liga al guion o a las notas. Es la costumbre que más rinde.

### B15b. El resumen de Escuchar, guardado y por diferencias

El resumen que Escuchar arma al empezar ya se guarda por proyecto, y la siguiente junta lo pone al
día leyendo solo lo que cambió en `CLAUDE.md`, `pendientes.md` y `contratos.md`.

- Se guarda en `~/.local/state/rc-launcher/resumenes/<proyecto>.json`, con el commit
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
- Medido: de 19 a 33 s, y por diferencias cuesta una fracción del completo cuando va por la API
  (B15i).

### B15c. Dialogar

Botón nuevo junto a Escuchar. Es la escucha en modo conversación: no graba la sala; un toque
empieza a hablar y otro envía, **o se envía solo tras 1.5 s de silencio**, que detecta el propio
teléfono con un modelo pequeño de detección de voz (Silero). La sesión contesta solo lo que se
le pregunta, la respuesta se oye por partes (la primera oración suena primero), se guarda en
`transcripciones/AAAA-MM-DD-HHMM-dialogo.txt` del proyecto, y el diálogo se cierra solo tras 15
minutos sin turnos.

**Dialogar habla con la sesión real del proyecto**, la que el cliente abrió con Nueva sesión o
Sesión rápida, y conoce la conversación en curso. Lo dicho se teclea en esa sesión de `tmux` con
un prefijo de voz, y la respuesta se lee de su registro. Si no hay sesión abierta, abre una rápida
que se queda viva. Antes de teclear revisa la pantalla: si la sesión tiene casillas abiertas
esperando respuesta, lo avisa en voz y espera; si está trabajando, espera hasta 5 minutos. Todo por
voz y sin candado de herramientas, decidido por Gustavo: lo que la sesión puede hacer, lo puede
hacer por Dialogar.

Un reinicio del lanzador a media respuesta ya es seguro: el turno queda anotado y se retoma al
arrancar. Aun así, antes de reiniciar conviene comprobar que no haya junta abierta (B2b).

- **Viajan con B2b:** `dialogo_real.py`, `sesion_viva.py`, `vad.py`, la carpeta `vad/` (16.7 MB,
  con `SHA256SUMS`) y `templates/_escucha.html`. Sin `vad/` funciona igual, con el segundo toque
  para enviar.
- **La voz de la respuesta** va por la voz local de B15h si está instalada (la primera oración
  suena en menos de un segundo), y si no por DeepInfra (A8), que cuesta centavos por respuesta y
  tarda de 5 a 30 s.
- **Un iPhone puede bloquear la voz** que no sale de un toque; ahí queda el botón «▶ Oír».
- Medido: de 18 a 36 s por turno, de enviar a oír la respuesta completa.

### B15d. El botón atrás y la tarjeta que dice «Escuchando»

- El botón atrás del teléfono, desde Escuchar o Dialogar, regresa a Proyectos y deja cerrada la
  pantalla; antes la volvía a abrir. Viaja con `templates/_escucha.html` y `templates/index.html`.
- La tarjeta del proyecto dice **«● Escuchando · N min»** o **«🎙 Dialogando · N min»** mientras
  dura.
- Medido con guion de navegador y confirmado por Gustavo en su teléfono.

### B15e. «Abre» y el proyecto, por voz

Dentro de «Filtrar proyectos» aparece un micrófono. Se dice **«Abre adco»** y se abre el menú del
proyecto, igual que al tocar su tarjeta.

- **Pide la llave de DeepInfra de A8.** Sin llave, el filtro se queda sin micrófono.
- La orden se entiende con reglas de texto, sin modelo de lenguaje; cuesta una fracción de centavo
  de dólar de transcripción.
- Viajan `orden_voz.py`, `templates/_script_voz.html` y la carpeta `vad/`.
- El detector de silencio arranca solo con la identidad que pone `tailscale serve` (B4); por la
  dirección local sin identidad se queda callado.
- Medido: 3.6 s del toque al menú, y Gustavo lo usa en su teléfono.

### B15f. El rescate del toque y el mosaico ancho

- **El rescate del toque:** al tocar una tarjeta sale «Abriendo <proyecto>…»; si el menú tarda 3 s
  se pide otra vez (hasta dos), y después se avisa. El redibujo de cada 8 s se detiene mientras el
  dedo está encima. Cada toque de más de 2 s se anota en
  `~/.local/state/rc-launcher/toques.jsonl`, que es lo primero que se revisa si el
  cliente dice que «a veces no abre». Cubre sobre todo al teléfono que llega por relevo de
  Tailscale, fuera de casa. Viaja `toques.py`, nuevo. Medido en bat: el mosaico bajó de 0.75 a 0.30 s.
- **El mosaico ancho:** en una pantalla de 1,024 px o más, el mosaico llega a 1,600 px con las
  columnas que quepan (6 en un monitor grande, 2 en un teléfono). Es solo CSS. 🟢

### B15g. Dictar la descripción al crear un proyecto

En «+ Nuevo proyecto», bajo «¿De qué se trata?», un botón Dictar pasa a texto lo que se dice. Si
la transcripción falla, el audio se conserva en
`~/.local/state/rc-launcher/dictados/`. **Pide la llave de DeepInfra de A8**; sin ella
el botón se omite.

### B15h. Opcional: la voz en la propia máquina (Kokoro)

La voz de las respuestas (Dialogar y «Atiende lo que diré») sale primero de Kokoro en la propia
máquina, gratis y en 1 a 5 s, con DeepInfra de respaldo. Sin instalarlo, todo sigue por DeepInfra.

```bash
sudo apt install -y ffmpeg espeak-ng
cd ~/rc-launcher/multiusuario
sudo ./instalar-kokoro.sh          # PyTorch solo para procesador, kokoro y el modelo
```

Deja unos 1.8 GB en `/opt/rc-launcher/kokoro`, de solo lectura, y le sirve a toda cuenta del
lanzador de esa máquina. Cada cuenta arranca su servidor de voz al empezar una junta con voz (1.1
GB de memoria mientras vive, se apaga solo a los 30 minutos sin uso). Medido: la primera voz en
unos 10 s, las siguientes en 1 a 4.7 s.

Tropiezos medidos: la instalación de PyTorch tarda unos 7 minutos y la de kokoro 4; **nunca correr
dos instalaciones a la vez**, que se atoran sin avisar. El modelo baja de Hugging Face, que a veces
va a medio megabyte por segundo; el guion reanuda la descarga si se corta.

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
3. Guardar la llave en `~/.config/anthropic/credentials` (con permisos 600), con el renglón
   `ANTHROPIC_API_KEY=…`.

🔴 **La llave nunca va en una variable de entorno.** Con `ANTHROPIC_API_KEY` en el entorno, las
sesiones de Claude Code dejan la suscripción y cobran todo por API. El lanzador la lee solo de ese
archivo, anota el gasto en `~/.local/state/rc-launcher/api/gasto.jsonl` y se detiene a los 140
dólares en el mes. Medido con cadena: 1.13 dólares un resumen completo con Sonnet 5.5, de 0.06 a 0.08
por diferencias.

### B15j. Verificar

Con B2b hecho y la pestaña del teléfono **recargada** (la abierta antes sigue con el código viejo):

1. **Escuchar con guion:** crear un evento que empiece en 10 minutos, con la liga a una paginita
   del proyecto en la descripción. Tocar Escuchar, Empezar: deben salir «Junta en curso» y «Guion
   de hoy».
2. **El resumen por diferencias:** en un proyecto con git, dos escuchas seguidas. La segunda tarda
   menos y el archivo de `resumenes/` cambia de commit.
3. **Dialogar:** un toque, una pregunta, silencio: se envía solo y la respuesta se oye. Terminar, y
   el botón atrás desde Proyectos sale del lanzador.
4. **«Abre» por voz:** la página trae el micrófono en el filtro; decir «Abre» y el nombre de un
   proyecto abre su menú.
5. **Dictar al crear proyecto:** el texto dictado aparece en «¿De qué se trata?».
6. **Después de la batería de B2,** `tmux ls` y la app de Claude del cliente deben tener las
   mismas sesiones que antes. Una de más quiere decir que una prueba tocó
   sesiones reales de esa máquina.
