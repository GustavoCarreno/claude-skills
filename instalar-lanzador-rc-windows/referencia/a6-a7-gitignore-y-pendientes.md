# A6 y A7 · El gitignore global y la convención de pendientes.md

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A6. Configurar el gitignore global
- A7. Sus pendientes por proyecto, el si-ya-se-hizo
  - A7b. La matriz: importancia y fechas
  - A7c. Contratos y lo que deja de cobrar

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

```powershell
$ignore = git config --global core.excludesFile
if (-not $ignore) {
  # No había ninguno configurado: el nuestro se vuelve el gitignore global.
  $ignore = "$env:USERPROFILE\.config\git\ignore"
  git config --global core.excludesFile $ignore
}
New-Item -ItemType Directory -Force -Path (Split-Path $ignore) | Out-Null
if (-not (Test-Path $ignore)) { New-Item -ItemType File -Path $ignore | Out-Null }

if (-not (Select-String -Path $ignore -Pattern '^bandeja/$' -Quiet)) {
@"

# Archivos que el lanzador sube desde el teléfono y archivos que el asistente
# genera para que se bajen. Viven dentro del proyecto pero no son código, y
# pueden ser material sensible de cliente. Sin esto, un "git add -A" de
# cualquier sesión los subiría a los repos privados sin que nadie lo note.
bandeja/
salida/
"@ | Add-Content -Path $ignore -Encoding utf8
}
```

Verificación (sin necesidad de un repositorio git):

```powershell
git config --global core.excludesFile
# Debe responder con una ruta (la suya, si ya tenía una; si no, C:\Users\<usuario>\.config\git\ignore)

$ignore = git config --global core.excludesFile
if (Select-String -Path $ignore -Pattern "salida/" -Quiet) { "✓ salida/ está en el gitignore" } else { "✗ ERROR: salida/ no encontrado" }
if (Select-String -Path $ignore -Pattern "bandeja/" -Quiet) { "✓ bandeja/ está en el gitignore" } else { "✗ ERROR: bandeja/ no encontrado" }
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

Se cierra igual que A6: sembrando la convención en `%USERPROFILE%\.claude\CLAUDE.md` **de
forma aditiva e idempotente**, para que cualquier sesión, en cualquier proyecto de esa
máquina, la conozca sin que haya que explicarla cada vez, y sin arriesgar lo que ya haya
en el archivo:

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
New-Item -ItemType Directory -Force -Path (Split-Path $claudeMd) | Out-Null
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd | Out-Null }

if (-not (Select-String -Path $claudeMd -Pattern '^## Agenda y avance' -Quiet)) {
@'

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

```powershell
Get-TimeZone | Select-Object -ExpandProperty Id    # debe ser la zona de quien la va a usar
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
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

> ⚠️ **Guardarlo en UTF-8, el mismo aviso de B5.** Claude Code lo lee como UTF-8; en cp1252
> los acentos llegan rotos. El `-Encoding utf8` de arriba ya lo hace bien.

> ⚠️ **Idempotente, igual que A6: correrlo dos veces no duplica la sección.** Y si
> `%USERPROFILE%\.claude\CLAUDE.md` ya tiene contenido de otro paso (el más obvio: si por
> algún motivo B5 ya corrió antes), esto se anexa, no lo reemplaza.

> 🔴 **El reverso de esa misma moneda, y muerde al ACTUALIZAR una máquina ya instalada:** como
> la guarda es el encabezado, en una máquina que ya trae la sección **este bloque no corre**.
> O sea que **las reglas nuevas del contrato no llegan solas**: el asistente de esa máquina
> sigue con el contrato del día que se instaló, y nada avisa. Al actualizar una instalación
> vieja hay que **agregar a mano lo que le falte**, comparando contra el bloque de aquí.

Verificación de A7: crear un `pendientes.md` de prueba con una tarea, abrir una sesión nueva en
ese proyecto y pedirle que revise sus pendientes. Debe encontrar la tarea sin que se la
describas. Rápido y sin abrir sesión:
`Select-String -Path "$env:USERPROFILE\.claude\CLAUDE.md" -Pattern "pendientes.md" -Quiet`.

Con eso basta para que el asistente cree, redacte, edite y palomee pendientes con sus
herramientas de siempre, sin esperar al lanzador.

### A7b. La matriz: importancia y fechas

Agrega dos cosas al renglón de indicadores de cada pendiente: si importa (`importante` o
`menor`) y, cuando las hay, la fecha límite y el día del bloque reservado. Con eso el lanzador
reparte los pendientes en cinco grupos según urgencia e importancia, y al abrir una sesión
le lista al cliente, numerado, lo que urge (ver B2b).

**Lo que el cliente gana, dicho como él lo vería:** el mosaico dice "2 urgentes", y en el
menú del proyecto esas dos tareas salen arriba y abiertas, con el resto plegado en sus grupos.
Medido en un proyecto de 29 tareas: las 2 urgentes a la vista, las otras 27 plegadas, y los
encabezados de todos los grupos caben en la pantalla del teléfono.

**Las esperas van en un grupo aparte**, ordenadas de la más vieja a la más nueva, y al pie
sale un grupo con lo que quedó fuera de las dos secciones, para que una tarea escrita bajo
otro encabezado se vea. Conviene explicárselo así al cliente, porque meter las esperas en la
matriz las mandaría todas a *Por clasificar*.

La convención va en un bloque propio, con su propia guarda, para que una máquina que ya tenía
A7 la reciba con solo correr esto:

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
if (-not (Select-String -Path $claudeMd -Pattern '^## La matriz de los pendientes' -Quiet)) {
@'

## La matriz de los pendientes: urgencia e importancia

Las tareas de `## Me toca a mí` llevan un cuarto indicador en su renglón de indicadores,
**Importancia**, con dos valores cerrados: `importante` · `menor`. Sin esa palabra la tarea
cae en *Por clasificar*. Las de `## Esperando a alguien` la omiten, porque dependen de otra
persona.

Dos fechas opcionales en el mismo renglón. Son datos, así que quedan fuera del vocabulario
cerrado:

- `vence AAAA-MM-DD`: la fecha límite. La escribo en cuanto me entero del plazo.
- `bloque AAAA-MM-DD`: el día del bloque reservado en el calendario. La escribo en el mismo
  acto en que creo el evento.

Así queda un renglón completo: `· computadora · una hora · trámite · importante · vence 2026-11-03`

**La urgencia se calcula contra el día de hoy y nunca se guarda.** Es urgente lo vencido, lo
que vence en los próximos 7 días y lo que tiene su bloque hoy o mañana. Ninguna palabra del
archivo dice "urgente": lo decide el lanzador al leer las fechas, así que una fecha puesta
hace meses sigue diciendo lo correcto hoy.

Los cinco grupos que salen de cruzar urgencia e importancia:

| Grupo | Cruce |
|---|---|
| Hacer ya | urgente e importante |
| Apartarle hora | importante, sin prisa |
| Quitárselo de encima | urgente y menor |
| Hacerlo si sobra tiempo | menor y sin prisa |
| Por clasificar | le falta la palabra de importancia |

El verbo *descartar* se reserva para marcar `[-]` una tarea que se decidió no hacer, y por eso
ningún grupo se llama así.

**El año va escrito en las fechas**, también en la prosa de las notas y en el "desde cuándo"
de las esperas (`· desde el 23 de abril de 2026`): una fecha sin año se vuelve ambigua en un
mes.
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

> 📌 **El formato de A7 se queda igual.** Esto agrega una palabra y dos fechas opcionales al
> mismo renglón; un `pendientes.md` sin ellas sigue funcionando, con sus tareas en *Por
> clasificar*.

### A7c. Contratos y lo que deja de cobrar

Cada proyecto puede llevar un `contratos.md` con el dinero y las fechas de cada trato, y la
pantalla **Contratos** del lanzador (fase B) suma lo que vence y avisa cuándo buscar al
siguiente cliente. Funciona sin acceso al correo: la fecha del último contacto la escribe la
sesión, así que un buzón corporativo bloqueado es indiferente.

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
if (-not (Select-String -Path $claudeMd -Pattern '^## Contratos y oportunidades' -Quiet)) {
@'

## Contratos y oportunidades: `contratos.md`

Cada proyecto puede llevar en su raíz un `contratos.md` con el dinero y las fechas de cada
trato. Lo escribo yo; la pantalla Contratos del lanzador solo lo lee, y calcula al pintar lo
que se deja de cobrar.

```markdown
# Contratos

## Renta de la nave 12
cliente: Nombre del cliente
etapa: firmado
contacto: Nombre de la persona
cobro: 55000 MXN al mes · del 2026-08-14 al 2027-08-13
último contacto: 2026-09-15
```

1. **Un contrato empieza con `## Título`.** Sus datos son los renglones `clave: valor` hasta el
   primer renglón en blanco; lo que sigue es relato.
2. **Diez claves:** `cliente` y `etapa` siempre; `probabilidad` (0 a 100) en las etapas
   abiertas; `cobro` una o varias veces; y opcionales `contacto`, `último contacto`, `aviso`
   (días), `sobre`, `factura` y `última factura`.
3. **Seis etapas, vocabulario cerrado:** `prospecto · propuesta · negociación · firmado ·
   pausado · perdido`. **Terminado se calcula** a partir de las fechas y nunca se escribe.
4. **`cobro` tiene cuatro formas:** `<monto> <MXN|USD> al mes · del A al B`,
   `al mes · desde A`, `una vez · A` y `una vez · contra entrega`, con una nota opcional tras
   otro `·`. Fechas siempre `AAAA-MM-DD`. Un `desde` o un `contra entrega` le quitan al
   contrato su fecha de fin: si el trato tiene fin, esos cobros van en un contrato aparte.
5. **Se escribe el subtotal antes de impuestos**, y solo la parte propia cuando hay socio.
6. **Un bono o una orden de cambio con criterio propio es un contrato aparte**, con su etapa.
7. **Un cobro ya hecho se deja con su fecha pasada** y se conserva: es registro, igual que
   los renglones `[x]` de `pendientes.md`.
8. **Al hablar con un cliente o prospecto, actualizo `último contacto`.** La pantalla nunca
   lee el correo: esa fecha la escribe la sesión.
9. **Las esperas siguen en `## Esperando a alguien` de `pendientes.md`**, fuera de la ficha.
10. **Una oportunidad sin carpeta propia vive en la carpeta `prospectos`**, con su propio
    `contratos.md`.
11. **Antes de confirmar un `contratos.md` en git, compruebo que el repositorio sea privado**,
    porque lleva montos de clientes.
12. **`factura` dice cuándo se emite cada mensualidad**, con una de dos formas: `día N del
    mes` (del 1 al 31) o `primer <día de la semana> del mes`, como `primer lunes del mes`. **`última
    factura` es la fecha AAAA-MM-DD de la más reciente emitida.** Con las dos, el lanzador pinta en
    rojo, arriba de todo, la factura que toca o ya venció. Al emitir una en sesión, actualizo
    `última factura`; el botón Ya la emití del lanzador también la escribe, y es la única clave
    que el lanzador escribe en este archivo.
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

**Las facturas por emitir, en una máquina que ya tenía esta sección.** El bloque de arriba se
salta entero cuando la sección ya existe, así que la regla 12 llega aparte, con su propia
guarda:

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
if (-not (Select-String -Path $claudeMd -Pattern 'ltima factura' -Quiet)) {
@'
12. **`factura` dice cuándo se emite cada mensualidad**, con una de dos formas: `día N del
    mes` (del 1 al 31) o `primer <día de la semana> del mes`, como `primer lunes del mes`. **`última
    factura` es la fecha AAAA-MM-DD de la más reciente emitida.** Con las dos, el lanzador pinta en
    rojo, arriba de todo, la factura que toca o ya venció. Al emitir una en sesión, actualizo
    `última factura`; el botón Ya la emití del lanzador también la escribe, y es la única clave
    que el lanzador escribe en este archivo.
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

**Al armar las fichas del cliente, cada contrato mensual lleva sus dos claves**, porque sin
`factura` el lanzador carece de fecha contra la cual avisar:

```markdown
cobro: 55000 MXN al mes · del 2026-08-14 al 2027-08-13
factura: día 1 del mes
última factura: 2026-10-01
```

> 📌 **De dónde sale:** el 5 de octubre de 2026 una mensualidad se pasó sin facturar, y la
> pantalla lo pasó por alto. El renglón rojo y el botón viven en la tarjeta Hoy (B10b).

**La configuración de la pantalla**, en un archivo aparte. Si falta, la pantalla usa los
valores de fábrica (pesos, 90 días de aviso, 12 meses a la vista, 30 días sin contacto y la
palabra "cliente"), sin avisar:

```powershell
$cfg = "$env:USERPROFILE\.config\rc-launcher\contratos.json"
New-Item -ItemType Directory -Force -Path (Split-Path $cfg) | Out-Null
if (-not (Test-Path $cfg)) {
@'
{
  "moneda": "MXN",
  "tipo_de_cambio": {"valor": 17.1277, "fecha": "2026-09-15"},
  "aviso_dias": 90,
  "meses": 12,
  "dias_contacto": 30,
  "palabra_cliente": "cliente"
}
'@ | Set-Content -Path $cfg -Encoding utf8
}
```

**Antes de escribirla, cuatro preguntas al cliente**, porque los valores de fábrica son los de
un consultor y el cliente puede ser otra cosa:

| Pregunta | Clave |
|---|---|
| ¿En qué moneda cobra casi todo? La renta industrial suele ir en dólares | `moneda` |
| ¿Cuántos días antes del fin de un contrato empieza a buscar el siguiente? | `aviso_dias` |
| ¿Cuántos meses quiere ver hacia adelante? (máximo 36) | `meses` |
| ¿Cómo le dice a quien le paga: cliente, inquilino? | `palabra_cliente` |

> ⚠️ **El tipo de cambio va siempre con su fecha.** La pantalla enseña cuántos días tiene, y un
> valor sin fecha se ignora. Al actualizarlo, se cambian los dos juntos.

> 📌 **En un negocio de rentas, la carpeta es el inmueble y cada inquilino es un contrato
> adentro.** Los prospectos sin inmueble van en la carpeta `prospectos`.

**Verificación de A7b y A7c:**

```powershell
@(Select-String -Path "$env:USERPROFILE\.claude\CLAUDE.md" -Pattern "^## La matriz de los pendientes|^## Contratos y oportunidades").Count   # debe dar 2
```

Y con el lanzador ya montado, la pantalla `/contratos` de la tailnet contesta `200` aunque
ningún proyecto tenga todavía su `contratos.md`.
