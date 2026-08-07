---
name: kokoro-deepinfra
description: Convertir texto a voz sintética (leer en voz alta) con Kokoro-82M en DeepInfra. Activar cuando el usuario pida que se le lea algo: "léeme los pendientes urgentes para hoy", "léeme las tareas de la minuta", "pásame esto a audio", "quiero oír este documento en el carro". NO activar cuando el usuario suba un archivo de audio o pida transcribir: eso es lo contrario y va con whisper-deepinfra. NO activar para poner música ni efectos de sonido.
---

# Convertir texto a voz sintética con Kokoro en DeepInfra

Manda el texto a `hexgrad/Kokoro-82M` en DeepInfra y devuelve un MP3. Cuesta **$0.62 USD por
millón de caracteres**, o sea que un documento de 10 páginas (~20 mil caracteres) sale en
alrededor de un centavo de dólar.

El script es un solo archivo de Python de biblioteca estándar. **No hay que instalar nada con
pip.** Vive junto a este documento:

| Sistema | Cómo se invoca |
|---|---|
| Linux, macOS | `python3 ~/.claude/skills/kokoro-deepinfra/kokoro_deepinfra.py` |
| Windows | `python "$env:USERPROFILE\.claude\skills\kokoro-deepinfra\kokoro_deepinfra.py"` |

## Primer uso: conseguir la llave

Correr `--estado` antes de nada. **Es la misma llave que usa `whisper-deepinfra`**: si el
usuario ya la dio para transcribir, el script la encuentra sola en
`~/.config/deepinfra/credentials` y no hay que volver a pedírsela.

Si `--estado` dice `llave: NO CONFIGURADA` y de verdad no hay ninguna, **pedírsela al usuario
con estas palabras**, sin inventar otro procedimiento:

> Para convertir esto a audio necesito una llave de DeepInfra, que es tuya y se cobra a tu
> cuenta. Son dos minutos: entra a https://deepinfra.com, crea la cuenta con Google o GitHub,
> y en **Dashboard → API Keys → New API Key** genera una. Pégamela aquí. Un documento de 10
> páginas te va a costar alrededor de un centavo de dólar.

Cuando la dé, guardarla **por stdin**, nunca como argumento (un argumento queda en el historial
del shell y en la lista de procesos):

```bash
printf '%s' 'LA_LLAVE' | python3 ~/.claude/skills/kokoro-deepinfra/kokoro_deepinfra.py --guardar-llave
```

Queda en `~/.config/deepinfra/credentials` con permisos solo para su usuario, y la comparten
todas las skills de DeepInfra. **No pedirle que edite `~/.profile`, `~/.bashrc` ni ninguna
variable de entorno**: si ya tiene `DEEPINFRA_API_KEY` en el entorno, el script la respeta, pero
no hace falta ponerla ahí.

## Uso

```bash
# Lo normal: un texto ya redactado para el oído (ver la sección de abajo), a archivo
python3 .../kokoro_deepinfra.py texto.md -o salida/pendientes.mp3

# Por stdin, sin dar nombre de archivo: el .mp3 sale con marca de tiempo
echo "Tienes dos pendientes urgentes..." | python3 .../kokoro_deepinfra.py

# Elegir voz y velocidad
python3 .../kokoro_deepinfra.py texto.md --voz ef_dora --velocidad 1.15

# Ver el plan y el costo estimado, sin gastar la llamada
python3 .../kokoro_deepinfra.py texto.md --simulacion
```

| Opción | Default | Para qué |
|---|---|---|
| `-o`, `--salida`, `--output` | `salida/<nombre>.mp3` (o `salida/voz-AAAAMMDD-HHMMSS.mp3` si vino por stdin) | Ruta del MP3 de salida. La carpeta `salida/` se crea sola |
| `--voz`, `--voice` | `em_alex` | Voz a usar. En español solo hay tres, ver abajo |
| `--velocidad`, `--speed` | `1.0` | Velocidad de habla, de `0.25` a `4.0` |
| `--crudo` | — | No limpiar el markdown antes de hablar (por defecto sí se limpia, ver abajo) |
| `--simulacion`, `--dry-run` | — | Plan y costo estimado, sin llamar a la API |
| `--estado` | — | Diagnóstico: llave, ffmpeg, voces, rutas |
| `--guardar-llave` | — | Lee la llave de stdin y la guarda |

**Voces en español, de las 54 que trae el modelo (las demás son de otros idiomas):**

| Voz | Timbre |
|---|---|
| `em_alex` (default) | Masculina |
| `ef_dora` | Femenina |
| `em_santa` | Masculina, temática de Navidad — poco útil fuera de esa temporada |

## El script limpia el markdown solo, pero eso no es "redactar para el oído"

Por defecto (`--crudo` lo desactiva) el script quita almohadillas de encabezado, viñetas,
numeración, casillas `- [ ]`, corchetes de liga (deja solo el texto visible), imágenes, bloques
de código (los reemplaza con un aviso corto), citas `>`, reglas horizontales, y aplana tablas a
texto separado por comas. Es un quitamarcas mecánico: evita que Kokoro pronuncie "almohadilla" o
"asterisco". **No reescribe nada.** Pasarle un `pendientes.md` sin retocar sale limpio de
símbolos, pero no bien narrado — sigue sonando a lista leída en voz alta, no a alguien hablando.
Por eso sigue haciendo falta la sección de abajo, que es trabajo del asistente, no del script.

## Textos largos: el script los parte solo, y sin perder palabras

El límite de la API es 10,000 caracteres por llamada, **contados en caracteres, no en bytes**:
el español acentuado no cuesta el doble. Un texto de 10,000 caracteres o menos va en **una sola
llamada**, sin necesitar `ffmpeg` — ese umbral es el límite duro de la API, no el tamaño de cada
pedazo cuando sí hay que partir. Una llamada cubre unos 10.9 minutos de audio. Si el texto no
cabe, el script lo parte en frontera de párrafo o de oración, apuntando cada pedazo a 9,000
caracteres (no a los 10,000 del límite, para darle holgura a la búsqueda de esa frontera), y une
los pedazos con `ffmpeg`, verificando con `ffprobe` que la duración final coincida con la suma
de los pedazos — para atrapar el caso de que `ffmpeg` reporte éxito habiendo tirado alguno. A
diferencia de `whisper-deepinfra`, que corta el audio a tiempo fijo y siempre pierde una palabra
en cada frontera, aquí el corte cae en puntuación y en el caso normal no se pierde nada — solo
si un tramo de miles de caracteres no trae ninguna frontera cercana (un bloque sin puntos ni
espacios, poco realista en prosa) el corte cae a carácter fijo, como último recurso.

**`ffmpeg` solo hace falta para textos de más de 10,000 caracteres.** Como lo normal son
respuestas cortas (los pendientes del día, un resumen, unos párrafos), lo normal es no
necesitarlo nunca. Si hace falta y no está, el script lo dice con el comando exacto para
instalarlo — es parte del runtime que deja listo la sección A4 de las skills
`instalar-lanzador-rc-linux` y `instalar-lanzador-rc-windows`.

## Redactar para el oído, no para la pantalla

**Lo normal es que el texto lo escribas tú, no que salga de un archivo tal cual.**
"Léeme los pendientes urgentes para hoy" significa: leer `pendientes.md`, filtrar lo
urgente, y **redactar una versión hablada**. El script solo convierte; qué se dice lo
decides tú.

Un texto pensado para leerse en pantalla suena mal dictado. Las reglas:

- **Anuncia la cantidad antes de enumerar.** "Tienes tres pendientes urgentes", y luego
  los tres. Quien escucha no puede echar un ojo a la lista para saber cuántos faltan.
- **Fechas habladas.** "El martes doce de agosto", no `2026-08-12`.
- **Montos y números hablados.** "Veinticinco mil pesos", no `$25,000.00`.
- **Nada de rutas, URLs, ni identificadores.** No se dictan en voz alta. Si hace falta
  referirse a un archivo, dilo por su nombre común.
- **Sin viñetas ni encabezados.** Encadena con conectores: "primero…", "el segundo…",
  "y por último…".
- **Frases cortas.** Una idea por oración. Sin paréntesis anidados ni incisos largos:
  quien escucha no puede releer.
- **Cierra diciendo lo que sigue**, si aplica. Es lo último que se le queda.

**Ejemplo de la diferencia.** En pantalla:

    ## Pendientes urgentes
    - [ ] Mandar la carta al broker (bloque: mar 12 ago, 10:00)
    - [ ] Firmar el acuerdo — vence 2026-08-15

Para el oído:

    Tienes dos pendientes urgentes. El primero, mandar la carta al broker, que tienes
    bloqueado el martes doce de agosto a las diez de la mañana. El segundo, firmar el
    acuerdo, que vence el viernes quince. El que corre prisa es el del acuerdo.

## Al terminar: mándale el audio, no le digas dónde quedó

El MP3 queda en `salida/` del proyecto, pero **no lo dejes ahí esperando a que lo busque:
mándaselo**. Es un archivo que pidió oír, así que entregarlo es parte de haber terminado,
no un trámite aparte que él tenga que solicitar.

Acompáñalo de una línea corta con lo que necesita saber: qué es, cuánto dura, y el costo,
que el script ya imprime.

Si el entorno no permite mandar archivos, entonces sí reporta la ruta local del archivo.

### Si la máquina tiene el lanzador rc, mándale también la liga

Escuchar desde el teléfono un archivo adjunto significa descargarlo, buscarlo en el navegador
de archivos y abrirlo. **Con una liga le pica y suena.** El lanzador sirve lo que hay en
`salida/` por `GET /audio/<proyecto>/<archivo>`, con el tipo y los rangos correctos para que el
navegador lo reproduzca en vez de bajarlo.

Comprobar que existe, y sacar el nombre del equipo, **sin clavarlo**:

```bash
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/salud   # 200 = el lanzador corre
tailscale status --json | jq -r '.Self.DNSName' | sed 's/\.$//'         # el nombre del equipo
```

Si el primero no da `200`, esa máquina no tiene el lanzador: entrega el archivo y ya. Si sí, la
liga es `https://<nombre-del-equipo>/audio/<proyecto>/<archivo>`, y va **además** del archivo, no
en su lugar: el adjunto sigue siendo la forma de reenviárselo a alguien más.

> ⚠️ **La liga solo abre desde un equipo de la misma tailnet.** El lanzador exige la identidad
> que verifica Tailscale en todas sus rutas, así que sin ella contesta 403. Eso es lo que la
> hace segura, y también lo que la vuelve inútil para compartir el audio con un tercero: para
> eso va el archivo.

> ⚠️ **El MP3 cae dentro de la carpeta del proyecto, y por defecto se subiría con un
> `git add -A`.** Quien instale esta skill sola, con el catálogo completo del one-liner pero
> sin la skill del lanzador (`instalar-lanzador-rc-linux` / `-windows`), no tiene protección:
> `salida/` solo queda fuera de `git status` si esa otra skill corrió su sección **A6**
> (gitignore global). Antes de generar audio en un proyecto con repo git, confirmar que
> `salida/` está en el gitignore global, o avisarle a quien esté instalando que le falta ese
> paso.

Cada llamada queda anotada en `~/.cache/kokoro-deepinfra.log`:

```
2026-08-04 14:32:07	OK 	1842c	$0.00114	pendientes.md	em_alex	salida/pendientes.mp3
```

Lo gastado hoy:

```bash
awk -F'\t' -v d="$(date +%Y-%m-%d)" '$1 ~ d {gsub(/[$]/,"",$4); s+=$4} END {printf "hoy: $%.5f\n", s}' ~/.cache/kokoro-deepinfra.log
```

## Cuándo NO usar esta skill

- **Cuando llega un audio.** Si el usuario sube una grabación, quiere **texto**: eso es
  `whisper-deepinfra`. No le devuelvas audio.
- **Como asistente de voz.** Esto no contesta hablando en el momento. Se pide, se genera,
  y el audio se le manda directo. Sirve para "prepárame esto y me lo oigo en el camino"; no
  sirve para preguntar y recibir respuesta hablada mientras maneja. **No lo prometas.**
- **Para música o efectos de sonido.** El modelo solo lee texto.
- **Para un idioma sin voz decente.** Kokoro trae 54 voces pero **solo tres en español**
  (`ef_dora`, `em_alex`, `em_santa`, y la última es temática de Navidad). Si el texto está
  en un idioma raro, dilo antes de gastar la llamada.

## Errores comunes

| Lo que sale | Qué pasó |
|---|---|
| `No hay llave de DeepInfra configurada.` | Nunca se guardó (ni aquí ni en `whisper-deepinfra`). El mensaje trae los pasos para conseguirla y guardarla. (`--estado` la resume distinto, como `llave: NO CONFIGURADA`) |
| `HTTP 401` o `403` | La llave se revocó o se pegó incompleta. Volver a guardarla |
| `HTTP 402` | La cuenta de DeepInfra no tiene saldo. Va a https://deepinfra.com/dash/billing |
| `voz desconocida: ...` | Nombre de voz mal escrito. En español solo hay tres: `ef_dora`, `em_alex`, `em_santa` |
| `velocidad fuera de rango: ...` | Fuera de `0.25`–`4.0` |
| `hace falta ffmpeg` | El texto pasó de 10,000 caracteres y hay que partirlo. El mensaje trae el comando para instalarlo |
| `el texto quedo vacio despues de limpiarlo` | El archivo solo traía markdown o código, nada de prosa que leer |
| `la salida es un directorio, no un archivo` | `-o` apuntó a una carpeta que ya existe, no a un nombre de archivo |
