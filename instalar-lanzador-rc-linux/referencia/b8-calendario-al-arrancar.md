# B8 · El bloque de calendario al arrancar (opcional)

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B8. El bloque de calendario al arrancar (opcional)
  - B8a. Lo que tiene que existir antes
  - B8b. La configuración y el gancho
  - B8c. Verificar
  - B8d. Lo que hay que decirle, y lo que cuesta
  - B8e. La agenda de hoy en el lanzador
  - B8f. La liga de cada evento a su proyecto

<!-- fin del encabezado agregado al partir -->

## B8. El bloque de calendario al arrancar (opcional)

**Lo que deja funcionando:** el cliente reserva en su calendario un bloque para un proyecto, por
ejemplo *"Marán · Carta al broker de LG"* de 10:00 a 12:00. Al abrir una sesión en ese proyecto
mientras el bloque está en curso, o hasta 30 minutos antes de que empiece, el asistente lo
encuentra solo, lee su descripción y la tarea de `pendientes.md` que le corresponde, **resume en
dos renglones qué toca y pregunta «¿Lo atendemos?»**. Empieza a trabajar solo con un sí.

**Es la mitad que le faltaba a A7:** allá quedó escrito que el calendario dice cuándo y
`pendientes.md` dice si ya se hizo. Con esto, la sesión junta las dos cosas sin que el cliente
tenga que pedir que se revise la agenda.

**Trae dos piezas, y conviene instalar las dos:**

| Pieza | Qué hace |
|---|---|
| **La configuración del calendario** (`calendario.json`) | Le dice al lanzador qué calendarios revisar. Sin ella, la revisión se queda apagada y la sesión arranca como antes |
| **El aviso para las sesiones abiertas a mano** (`aviso_arranque.py`) | Un *gancho* de Claude Code, o sea un programa que Claude Code corre solo en cierto momento; este corre al iniciar la sesión. Le entrega el mismo aviso a una sesión abierta con `claude` en la terminal o en VS Code, que hasta ahora arrancaba sin él |

> 📌 **El gancho también le lleva a esas sesiones las otras dos revisiones**, la retroalimentación
> dictada desde el teléfono y las transcripciones de B7. Con el lanzador el aviso llega como
> primera instrucción y la sesión lo atiende sola; con `claude` directo llega como contexto y se
> atiende al primer mensaje, aunque sea un "hola". **Se calla a propósito en dos casos:** al
> compactar la conversación, para no repetirlo a media sesión, y en las sesiones del lanzador,
> que ya lo traen (llevan `RC_LANZADOR=1` en el entorno).

> 📌 **El lanzador sigue sin hablar con Google**, igual que en B7: solo lee la configuración y le
> redacta la instrucción a la sesión. Quien consulta el calendario es el asistente, y la
> instrucción dice "revisa en Google Calendar" sin nombrar herramienta, así que **sirve cualquiera
> de las tres vías** que tenga la máquina:
>
> | Vía | Cuándo |
> |---|---|
> | **El conector de Google Calendar de claude.ai** (A5) | La de fábrica, y la que casi todo cliente va a tener |
> | **Composio** (A5e) | Si el cliente lo contrató y conectó ahí su Google Calendar. Una sola llamada consulta varios calendarios a la vez |
> | **`gws`**, la herramienta de línea de comandos de Google Workspace | Solo en la máquina que ya lo tenga configurado. Exige un proyecto de Google Cloud propio, y por eso queda fuera como vía de fábrica |
>
> **Probadas las tres el 25 de septiembre de 2026**, cada una con el identificador de un
> calendario secundario y con `primary`, y las tres encontraron el mismo bloque en curso.

### B8a. Lo que tiene que existir antes

| Requisito | Por qué |
|---|---|
| **Una vía al calendario**: el conector de A5 en `Connected`, Composio con Google Calendar conectado, o `gws` configurado | Con ella se buscan los eventos. Basta una |
| **Una copia del lanzador del 25 de septiembre de 2026 o posterior** | Es la que trae `calendario_sesion.py` y `aviso_arranque.py`. Una anterior ignora la configuración en silencio |
| **La convención del título**, explicada al cliente | Ver B8d. Sin ella la sesión decide por la descripción y se equivoca más |

```bash
for f in calendario_sesion.py aviso_arranque.py; do [ -e ~/rc-launcher/$f ] || echo "FALTA: $f"; done; echo "revisión terminada"
```

### B8b. La configuración y el gancho

1. **Sacar el identificador de cada calendario**, en Google Calendar desde la computadora: los
   tres puntos junto al nombre del calendario → *Configuración y uso compartido* → sección
   *Integrar el calendario* → *ID del calendario*. El calendario principal no hace falta
   buscarlo: su identificador es `primary`.
2. **Escribir la configuración**, sustituyendo el identificador:

```bash
mkdir -p ~/.config/rc-launcher
cat > ~/.config/rc-launcher/calendario.json << 'FIN'
{"calendarios": [
  {"nombre": "Trabajo", "id": "EL_ID_DEL_CALENDARIO_DE_TRABAJO"},
  {"nombre": "principal", "id": "primary"}
], "minutos_antes": 30}
FIN
```

> ⚠️ **El principal va en la lista aunque el cliente tenga un calendario aparte para el
> trabajo.** Las invitaciones de sus clientes caen en el principal, porque el dueño de ese
> evento es quien invita. Si solo tiene el principal, la lista lleva ese renglón y ya.

3. **Registrar el gancho** en `~/.claude/settings.json`. Este fragmento lo agrega sin tocar lo
   demás, y no lo duplica si ya estaba:

```bash
python3 - << 'FIN'
import json, pathlib, shutil
cfg = pathlib.Path.home() / ".claude" / "settings.json"
orden = f"/usr/bin/python3 {pathlib.Path.home()}/rc-launcher/aviso_arranque.py"
shutil.copy(cfg, str(cfg) + ".bak")            # respaldo antes de tocar nada
datos = json.loads(cfg.read_text(encoding="utf-8"))
inicio = datos.setdefault("hooks", {}).setdefault("SessionStart", [])
ya = any(h.get("command") == orden for g in inicio for h in g.get("hooks", []))
if not ya:
    inicio.append({"hooks": [{"type": "command", "command": orden}]})
cfg.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
print("ya estaba" if ya else "registrado")
FIN
```

> 📌 **Va con el Python del sistema y no con el del lanzador**, porque el gancho usa solo la
> biblioteca estándar. Y queda junto al gancho `pendiente` de la bitácora (A3); los dos corren al
> iniciar y cada uno hace lo suyo.

**Sin reinicios:** el lanzador lee `calendario.json` cada vez que lanza una sesión, y Claude Code
lee `settings.json` al abrir cada sesión. Para apagar la revisión basta con borrar
`calendario.json`.

### B8c. Verificar

Primero que la configuración se lee y que la instrucción habla del cliente (deben imprimir
`True`, luego `False`, y luego el nombre del cliente que se escribió en B2):

```bash
cd ~/rc-launcher && .venv/bin/python -c "import calendario_sesion as c; t = c.instruccion_para_la_sesion('prueba'); print(t is not None); print('Gustavo' in t); import usuario; print(usuario.quien())"
```

> 🔴 **Si el segundo renglón imprime `True`, la copia del lanzador es anterior al 5 de octubre
> de 2026** y le dice a la sesión que espere el sí de "Gustavo", el nombre de quien la construyó.
> Llevarle una copia nueva con B2b antes de entregar. **Si el tercero imprime `el usuario`**,
> falta el `usuario.json` de B2: funciona igual, pero la sesión le habla al cliente sin su
> nombre.

Luego que el gancho habla y que se calla con la marca del lanzador (el primero imprime un
renglón que empieza con `{"hookSpecificOutput"`, el segundo nada):

```bash
P='{"source":"startup","cwd":"'$HOME'/claude/<proyecto>"}'
echo "$P" | env -u RC_LANZADOR python3 ~/rc-launcher/aviso_arranque.py | head -c 60; echo
echo "$P" | RC_LANZADOR=1 python3 ~/rc-launcher/aviso_arranque.py | head -c 60; echo "(vacío arriba = correcto)"
```

Y la prueba completa, con el cliente enfrente:

1. Crear en su calendario un evento que empiece en 10 minutos, titulado
   `<proyecto> · Prueba de instalación`, con una descripción de una línea.
2. Desde el teléfono, lanzar una sesión nueva en ese proyecto. **La sesión debe resumir el
   evento y preguntar «¿Lo atendemos?»**, por su propia cuenta.
3. En la computadora, abrir `claude` directo en esa carpeta y escribir "hola". **Debe ofrecer el
   mismo evento.**
4. Borrar el evento de prueba.

### B8d. Lo que hay que decirle, y lo que cuesta

- **La convención del título:** *nombre de la carpeta del proyecto, un punto medio, y qué toca*,
  como `Marán · Carta al broker de LG`. Es con lo que la sesión decide de qué proyecto es el
  evento. El punto medio `·` sale en el teléfono dejando presionado el punto, y en la computadora
  vale copiarlo de un evento anterior.
- **Conviene ofrecerle un calendario aparte para el trabajo**, que puede compartir con su equipo
  o con su asistente sin enseñar lo personal. Es lo que usa Gustavo desde el 25 de septiembre de
  2026.
- **Que el « ✓» al final de un título lo pone la sesión** (desde el 14 de octubre de 2026,
  lanzador `1af5655`). Cuando dice que sí a un bloque propio, la sesión agrega « ✓» al final del
  título y un renglón «Atendido en sesión el AAAA-MM-DD HH:MM» al final de la descripción, con
  las notificaciones apagadas y el color y los invitados como estaban. Así la siguiente sesión
  deja de ofrecérselo. Quitarle la marca hace que se vuelva a ofrecer. **Propio** quiere decir
  que él lo organiza (`organizer.self`): en una invitación el creador también sale con su nombre,
  así que el creador sirve de poco para distinguirlo. Las invitaciones de un cliente se quedan
  intactas: la que coincide en inicio y fin con un bloque propio se omite, porque el propio la
  representa, y la que va sola se ofrece en cada arranque.
- **Los eventos de día completo se quedan fuera a propósito**: son cumpleaños, vacaciones y
  recordatorios, y ofrecerlos al arrancar estorbaría.
- **Cada sesión arranca con una consulta al calendario**, aunque no haya bloque. Es uso de su
  suscripción, pequeño, y se paga en cada arranque, igual que la de Drive en B7.

### B8e. La agenda de hoy en el lanzador

**Lo que deja funcionando:** en la portada del lanzador, debajo de Principal y Hoy, una sección
**«En la agenda de hoy»** sube en amarillo las tarjetas de los proyectos que tienen un compromiso
pendiente hoy, ordenadas por la hora, con la hora y el título del evento en la tarjeta. Tocar una
abre el menú de siempre de ese proyecto, con el evento nombrado arriba; un toque en *Nueva sesión*
arranca la sesión, que le ofrece **ese** evento aunque caiga fuera de la ventana de 30 minutos de
B8.

| Un evento deja de contar cuando… | Por qué |
|---|---|
| Ya terminó | Su hora pasó |
| Trae « ✓» al final del título | Se atendió en otra sesión (B8d) |
| La sesión recibió el sí a «¿Lo atendemos?» | La sesión corre `agenda.py atendido <id>`, que la instrucción de B8 ya le pide |

**Lanzar la sesión solo lo deja pendiente**, a propósito: hasta que el cliente diga que sí, el
compromiso sigue en pie. Un evento cuyo título carece del nombre de un proyecto se queda fuera de
las tarjetas, porque marcaría una que nada tiene que ver.

**Una tarjeta cuyo proyecto ya tiene sesión abierta pasa a fondo verde**, el mismo de *Activos*, y
conserva la barra amarilla de la izquierda y la hora en amarillo: el fondo dice que ya se atiende y
la barra que hay agenda hoy. Sin sesión se queda amarilla. Antes solo cambiaba el borde, y no se
distinguía de un vistazo cuáles estaban abiertas (lanzador `2286864`, 16 de octubre de 2026, 1408
pruebas). **Viaja con B2b** en un solo renglón de `templates/_estilos.css`, sin rutas, dependencias
ni configuración nuevas.

**Quien lee el calendario es Claude, con la suscripción del cliente**, igual que en B8: el
lanzador nunca habla con Google. La lectura corre con `claude -p` en la primera apertura del día y
con el botón *Actualizar*, y se guarda en `~/.local/state/rc-launcher/agenda/hoy.json`. Usa `gws`
si la máquina lo tiene y el conector de Google Calendar si no, que es el caso de casi todo cliente.
**Medido en la máquina de Gustavo: 33 segundos y 6 eventos.** Una agenda que es de otro día se
pinta vacía y avisa que está vieja, para que nunca parezca completa siendo de ayer.

**Viaja sola con B2b** (lanzador `9e1f53f` a `75de62e`, 15 de octubre de 2026, 1406 pruebas):
`agenda.py` es nuevo, y cambian `app.py`, `barrido.py`, `barrido_correr.py`,
`calendario_sesion.py`, `pendientes.py`, `procesos_tmux.py`, `procesos_windows.py`, `sessions.py`
y cuatro plantillas. **Depende de `calendario.json` (B8b): sin él la sección desaparece** y el
lanzador queda como antes. **Pide el reinicio del final de B2b.**

> 📌 **Cada lanzamiento queda anotado** en `~/.local/state/rc-launcher/lanzamientos.jsonl`, con su
> origen (`mosaico`, `liga` o `agenda`). Sirve para saber en un par de semanas cuál de las entradas
> usa el cliente de verdad.

### B8f. La liga de cada evento a su proyecto

**Lo que deja funcionando:** cada evento que la sesión crea para un proyecto lleva al final de su
descripción un renglón *"Abrir en el lanzador: https://…"*. El cliente lo toca desde la
notificación del calendario o desde el evento, y el lanzador le abre el menú de ese proyecto con el
evento nombrado; un toque en *Nueva sesión* arranca la sesión, que le ofrece ese evento.

> 📌 **La liga abre el menú y deja el lanzamiento en un toque**, a propósito. Lanzar es una orden
> que cambia algo, y una liga que lanzara sola se dispararía con la vista previa del teléfono o con
> dos toques seguidos.

La sesión arma la liga con un comando que saca el nombre de la máquina de `tailscale status`:

```bash
python3 ~/rc-launcher/agenda.py liga <proyecto> <nombre del calendario> <id del evento>
```

El nombre del calendario es el que lleva en `calendario.json` («Trabajo», «principal»). Imprime el
renglón completo, listo para agregarse a la descripción.

**Para que las sesiones lo hagan solas, la regla va en el `CLAUDE.md` global.** Va aquí y no en A7
porque necesita el lanzador publicado en la tailnet, o sea la fase B. Sembrarla, de forma aditiva e
idempotente:

```bash
grep -q '^### La liga al lanzador en cada evento' ~/.claude/CLAUDE.md || cat >> ~/.claude/CLAUDE.md << EOF

### La liga al lanzador en cada evento

Al crear un evento de un proyecto, le agrego al final de la descripción la liga que abre el
lanzador en ese proyecto. Se crea el evento, se toma el id que devuelve, y se corre
\`python3 $HOME/rc-launcher/agenda.py liga <proyecto> <calendario> <id>\`, con el nombre del
calendario como está en \`~/.config/rc-launcher/calendario.json\`. Imprime el renglón completo, que
se agrega al final de la descripción sin avisar a los invitados (sendUpdates en none, o
notificaciones en NONE con el conector).

- Va solo en eventos propios sin invitados de otro dominio, porque la liga deja ver el nombre de la
  máquina y de la red privada. Esas juntas suelen tener su propio evento de notas a la misma hora,
  que sí la lleva.
- En una serie se pone en cada instancia que se toque, y el evento principal de la serie se queda
  como está: cambiar su descripción reescribe la de todas las instancias.
EOF
grep -c '^### La liga al lanzador en cada evento' ~/.claude/CLAUDE.md   # debe dar 1
```

> ⚠️ **El heredoc va sin comillas en `EOF`** para que `$HOME` quede escrito con la ruta real; por
> eso las comillas invertidas van escapadas.

> 📌 **La sección de la agenda cuenta los eventos de hoy que se quedaron sin liga**, así que uno que
> se olvidó se ve. La sesión de la escucha (B9) todavía crea eventos sin ella: lo hace con sus
> propias instrucciones, y está pedido en el lanzador.

### Verificar B8e y B8f

```bash
python3 ~/rc-launcher/agenda.py liga <proyecto> principal prueba123   # imprime «Abrir en el lanzador: https://…/?abrir=…»
```

Y con el cliente enfrente:

1. Crear en el calendario un evento de hoy, en un par de horas, titulado
   `<proyecto> · Prueba de la agenda`.
2. Abrir el lanzador y tocar *Actualizar* en «En la agenda de hoy». En menos de un minuto **la
   tarjeta del proyecto debe subir en amarillo**, con la hora y el título.
3. Pedirle en una sesión que le agregue la liga a ese evento. Tocar la liga desde el teléfono:
   **debe abrir el menú del proyecto con el evento nombrado.**
4. *Nueva sesión*: la sesión debe ofrecer el evento aunque falten más de 30 minutos.
   Antes de contestar, recargar el lanzador con esa sesión abierta: **la tarjeta debe verse con
   fondo verde y la barra amarilla a la izquierda.** Contestar que
   sí, y recargar el lanzador: **la tarjeta debe dejar la agenda.**
5. Borrar el evento de prueba.
