# A6 y A7 · El gitignore global y la convención de pendientes.md

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A6. Configurar el gitignore global
- A7. Sus pendientes por proyecto, el si-ya-se-hizo

<!-- fin del encabezado agregado al partir -->

## A6. Configurar el gitignore global

**Paso obligatorio, aunque sea invisible.** La carpeta `salida/` (donde el asistente deja
audio de voz sintética para descargar) y la `bandeja/` (archivos subidos desde el teléfono)
viven dentro de los proyectos pero no son código del proyecto. Sin gitignore, un `git add -A`
subiría estos archivos (que pueden ser material sensible: audios de junta, fotos de documentos,
contratos) a los repos privados de GitHub sin que nadie lo note.

**No pisar un gitignore global que ya exista.** Si la máquina ya tenía uno configurado (la
convención más extendida es `~/.gitignore_global`), sus patrones — típicamente `.env`, `*.pem`,
`*.key` — dejarían de aplicar de golpe si se reemplaza sin leerlo primero. El desenlace posible
es un secreto commiteado, justo lo contrario de lo que este paso busca. Se lee el valor actual
y, si ya hay uno, se anexa ahí; solo se configura el nuestro si no había ninguno. Y es
idempotente: no agrega una línea que ya esté.

```bash
ignore="$(git config --global core.excludesFile)"
if [ -z "$ignore" ]; then
  # No había ninguno configurado: el nuestro se vuelve el gitignore global.
  ignore=~/.config/git/ignore
  git config --global core.excludesFile "$ignore"
fi
ignore="${ignore/#\~/$HOME}"
mkdir -p "$(dirname "$ignore")"
touch "$ignore"

grep -qxF 'bandeja/' "$ignore" 2>/dev/null || cat >> "$ignore" << 'EOF'

# Archivos que el lanzador sube desde el teléfono y archivos que el asistente
# genera para que se bajen. Viven dentro del proyecto pero no son código, y
# pueden ser material sensible de cliente. Sin esto, un "git add -A" de
# cualquier sesión los subiría a los repos privados sin que nadie lo note.
bandeja/
salida/
EOF
```

Verificación (sin necesidad de un repositorio git):

```bash
git config --global core.excludesFile
# Debe responder con una ruta (la suya, si ya tenía una; si no, /home/<usuario>/.config/git/ignore)

ignore="$(git config --global core.excludesFile)"
ignore="${ignore/#\~/$HOME}"
grep -q "salida/" "$ignore" && echo "✓ salida/ está en el gitignore" || echo "✗ ERROR: salida/ no encontrado"
grep -q "bandeja/" "$ignore" && echo "✓ bandeja/ está en el gitignore" || echo "✗ ERROR: bandeja/ no encontrado"
```

---

## A7. Sus pendientes por proyecto, el si-ya-se-hizo

**En dos renglones: el calendario aparta el rato, y `pendientes.md` en la raíz de cada
proyecto dice si ya se hizo.** La mitad del calendario ya quedó montada en A5 (los
conectores de Google Calendar / Microsoft 365); esta sección solo la referencia, no la
repite.

> 📌 **Qué hace el cierre automático con el calendario, y qué nunca hace.** Desde que la
> bitácora atiende también esta mitad (A3), al cerrar una sesión puede **poner al día el
> bloque que esa sesión movió** — agregando a la descripción, sin reescribir lo que ya
> decía — y **agendar uno nuevo solo si se lo pidieron**, o si un pendiente nuevo trae fecha
> ya comprometida con alguien más. Un pendiente sin fecha vive en `pendientes.md` y no en el
> calendario.
>
> **Lo que nunca hace, y vale decírselo al cliente, porque es lo que vuelve seguro dejarlo
> corriendo solo:**
>
> - **No borra eventos, ni contesta invitaciones.** No es una promesa de buena conducta: esas
>   herramientas **no están** en la lista con la que corre la sesión que escribe, así que son
>   imposibles y no solo están prohibidas.
> - **No agrega ni quita invitados**, porque mover asistentes manda correo. Lo propone en una
>   línea y lo decide el cliente.
> - **No notifica a nadie.** Toda escritura va con `notificationLevel NONE`. De fábrica ese
>   parámetro es `ALL`, o sea que **actualizar un bloque que ya tiene invitados les manda
>   correo a todos**; sin esa regla, un cierre desatendido acabaría escribiéndole a terceros.
>
> ⚠️ **Para que el cierre sepa cuál bloque tocar, la nota del pendiente tiene que citarlo**,
> que es justo lo que pide el formato de abajo. Sin esa referencia no adivina: se queda
> callado, y como el silencio es también su respuesta normal cuando no hay nada que hacer,
> nadie nota la diferencia.

**Por qué va en la fase A y no en la B: funciona sin lanzador.** El archivo y el asistente
bastan, y el teléfono solo agrega el dedo. Un cliente al que su área de sistemas le bloquee
Tailscale se queda solo con la fase A y **conserva la disciplina completa**.

Se cierra igual que A6: sembrando la convención en `~/.claude/CLAUDE.md` **de forma
aditiva e idempotente**, para que cualquier sesión, en cualquier proyecto de esa máquina,
la conozca sin que haya que explicarla cada vez, y sin arriesgar lo que ya haya en el
archivo:

```bash
claude_md=~/.claude/CLAUDE.md
mkdir -p "$(dirname "$claude_md")"
touch "$claude_md"

grep -q '^## Agenda y avance' "$claude_md" || cat >> "$claude_md" << 'EOF'

## Agenda y avance: el calendario dice CUÁNDO, `pendientes.md` dice SI YA SE HIZO

Cada proyecto puede tener un `pendientes.md` en su raíz. El calendario reserva el bloque;
`pendientes.md` dice si el trabajo ya se hizo.

**El formato:**

```markdown
# Pendientes

## Me toca a mí

- [ ] Título de la tarea
      · dónde · cuánto · cabeza
      Nota con el contexto, y a qué bloque de calendario corresponde.
      » AAAA-MM-DD HH:MM · lo que dictaste desde el teléfono, sin procesar
      » AAAA-MM-DD HH:MM · otra que ya leí  ✓ AAAA-MM-DD HH:MM

## Esperando a alguien

- [ ] Nombre · desde cuándo
      Qué se espera que entregue.

## Hechas

- [x] Tarea ya hecha  ✓ AAAA-MM-DD HH:MM

## Descartados

- [-] Tarea que se decidió no hacer  ✗ AAAA-MM-DD
      El motivo.
```

**El contrato:**

- Una tarea es un renglón que casa con `^\s*-\s\[([ xX])\]\s+(.+)$`. Todo lo demás es
  decoración: encabezados, prosa, viñetas sin casilla.
- Las notas son los renglones siguientes con más sangría.
- **La retroalimentación que dictas desde el teléfono es una nota que empieza con `»`**,
  seguida de la fecha y hora y de `· `. Así: `» 2026-08-09 14:32 · lo llevé, aceptaron dos
  de tres`. La `»` es procedencia y **es permanente**: dice que eso lo dictaste tú, no yo.
  Se reconoce solo al **inicio** del renglón, así que lo que dictes puede llevar otra `»`
  adentro sin confundir nada.
- **Una retroalimentación sin procesar es la que NO termina en ` ✓ AAAA-MM-DD HH:MM`.** Al
  procesarla **agrego** ese sello; **nunca borro el texto que dictaste**. Es el mismo
  registro que los renglones `[x]`, y se protege igual: procesarla es leerla y sellarla, no
  vaciarla.
- **Lo que no cuelga de ningún pendiente va bajo `## Dicho del proyecto`**, con los
  renglones `»` a ras de margen: un recado del proyecto, no una tarea. Se reconocen igual
  que las retroalimentaciones de una tarea —la `»` es procedencia, el sello
  ` ✓ AAAA-MM-DD HH:MM` dice que ya se procesó— y **nunca se borra lo dictado**. La sección
  se crea al final del archivo, y **un `»` a ras de margen no es una tarea ni la nota de
  ninguna**, así que no cuenta ni se pinta como pendiente.
  - El encabezado lleva **exactamente dos almohadillas**. Con `###` la sección deja de
    reconocerse y tus recados dejan de contarse, **sin que nada avise**.
  - La sección **termina en el siguiente encabezado**, del nivel que sea. Si agregas uno
    después, los recados que queden debajo se vuelven invisibles.
  - Dentro de un bloque de código cercado no se lee nada, así que un `#` ahí no la corta.

  Queda así, y el encabezado va **pegado al margen izquierdo**, sin sangría:

```markdown
## Dicho del proyecto

» 2026-08-09 21:40 · el cliente movió la junta al martes
» 2026-08-08 09:12 · ya no urge lo del respaldo  ✓ 2026-08-09 10:05
```
- **Si la tarea tiene un bloque de calendario, la nota lo cita con su fecha.** Es lo que
  engancha las dos mitades: sin esa referencia, al cerrar la sesión no hay forma de saber cuál
  bloque poner al día. Cuando yo identifico o agendo uno, dejo la cita escrita ahí mismo, para
  que la próxima vez no haya que adivinar.
- **Sin identificadores** en el renglón (nada de `id: 4f2a`): el archivo se tiene que poder
  leer y editar a mano.
- Quien palomea agrega ` ✓ AAAA-MM-DD HH:MM` al final, con hora local. Al despalomear se
  quita.

> ⚠️ **Esa hora la pone la máquina donde corre el lanzador, así que su reloj y su zona
> horaria acaban escritos en el archivo del cliente.** Medido el 13 de agosto de 2026 en una
> máquina de pruebas que había quedado en UTC: palomeaba con **siete horas de adelanto** sobre
> la hora local, y nada avisaba, porque un sello con fecha y hora se ve correcto aunque diga
> otra cosa. **Comprobar la zona antes de entregar la máquina**, que cuesta un renglón:

```bash
timedatectl | grep "Time zone"     # debe decir la zona de quien la va a usar
```
- **En Windows el archivo llega con fin de línea CRLF y hay que conservarlo** al reescribir.
- **Palomeo lo que hice yo mismo y verifiqué, y también lo tuyo cuando en la sesión quedó
  constancia de que ya se hizo** (me lo dijiste con todas sus letras, o lo comprobé por mi
  cuenta). **Ante la duda no palomeo:** anoto en la nota lo que se supo y lo palomeas tú. Un
  palomeo puesto por suposición vuelve inservible la señal entera. Y si palomeo algo tuyo por
  constancia, digo en la nota de dónde salió esa constancia, para que puedas distinguir tu
  propio dedo de una deducción mía.
- **Tareas gruesas: una por entregable, no una por bloque de calendario.**

**`## Me toca a mí` es lo que puedes avanzar hoy; `## Esperando a alguien` es lo que depende
de que otra persona conteste, firme, pague o entregue**, con nombre y desde cuándo.

> ⚠️ **La trampa donde esto se rompe solo:** *"dar seguimiento a Fulano"* **sí te toca a ti**;
> lo que va en `Esperando` es la entrega de Fulano, no el empujón. Solo pasa a ser espera
> cuando ya se le empujó varias veces sin respuesta.

**Los tres indicadores** de `Me toca a mí`, en su propio renglón después del título, con
`· ` al inicio y entre ellos. Vocabulario cerrado, sin inventar palabras nuevas:

| Criterio | Valores |
|---|---|
| **Dónde** | `computadora` · `teléfono` · `en persona` |
| **Cuánto** | `minutos` (menos de 15) · `una hora` (hasta un par) · `sesión larga` (media jornada o más) |
| **Cabeza** | `concentración` · `trámite` |

Ante la duda, **escoger el valor mayor**: es peor prometer minutos y que se vaya la tarde.
La **prioridad se queda fuera a propósito**, ya la expresa el orden del archivo, que tú
controlas a mano.

**Descartar** es el tercer estado, para lo que se decidió no hacer: se marca `[-]` y se
mueve al final bajo `## Descartados`, con ` ✗ AAAA-MM-DD` y el motivo en la nota. `[-]` no
casa con la expresión de arriba, así que deja de contar y de pintarse solo.

> 🔴 **REGLA QUE NO SE PUEDE ROMPER: al reescribir un `pendientes.md`, NUNCA borrar los
> renglones `[x]` ni `[-]`.** Son un registro de lo que ya se cerró; una reescritura que se
> los lleva por delante lo destruye en silencio, y si el archivo nunca se confirmó en git, no
> hay forma de recuperarlo.
>
> **Y de ahí sale la otra: confirmar el archivo en git de verdad**, no dar por hecho que
> alguien lo hará. "Queda versionado" solo es cierto si alguien lo confirma.

Al arrancar una sesión en un proyecto, reviso su `pendientes.md` para saber qué ya se hizo,
en vez de preguntar o suponer.
EOF
```

> ⚠️ **Idempotente, igual que A6: correrlo dos veces no duplica la sección.** Y si
> `~/.claude/CLAUDE.md` ya tiene contenido de otro paso (el más obvio: si por algún motivo
> B5 ya corrió antes), esto se anexa, no lo reemplaza.

> 🔴 **El reverso de esa misma moneda, y muerde al ACTUALIZAR una máquina ya instalada:** como
> la guarda es el encabezado, en una máquina que ya trae la sección **este bloque no corre**.
> O sea que **las reglas nuevas del contrato no llegan solas**: el asistente de esa máquina
> sigue con el contrato del día que se instaló, y nada avisa. Al actualizar una instalación
> vieja hay que **agregar a mano lo que le falte**, comparando contra el bloque de aquí.

Verificación: crear un `pendientes.md` de prueba con una tarea, abrir una sesión nueva en
ese proyecto y pedirle que revise sus pendientes. Debe encontrar la tarea sin que se la
describas. Rápido y sin abrir sesión: `grep -q "pendientes.md" ~/.claude/CLAUDE.md`.

Con eso basta para que el asistente cree, redacte, edite y palomee pendientes con sus
herramientas de siempre, sin esperar al lanzador.
