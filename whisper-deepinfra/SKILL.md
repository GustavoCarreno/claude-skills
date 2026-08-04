---
name: whisper-deepinfra
description: Transcribir audio a texto, o traducirlo a inglés, con Whisper en DeepInfra. Activar cuando el usuario pida transcribir, pasar a texto, o sacar el texto de una grabación, nota de voz, junta, entrevista o audio de WhatsApp. También cuando suba un archivo de audio a la bandeja y pida saber qué dice, o pida el resumen o la minuta de una grabación (primero se transcribe y luego se resume). No activar para generar audio o voz sintética, que es lo contrario.
---

# Transcribir audio con Whisper en DeepInfra

Manda el audio a `openai/whisper-large-v3-turbo` en DeepInfra y devuelve el texto.
Cuesta **$0.00020 USD por minuto**, o sea que una junta de una hora sale en poco más
de un centavo de dólar.

El script es un solo archivo de Python de biblioteca estándar. **No hay que instalar
nada con pip.** Vive junto a este documento:

| Sistema | Cómo se invoca |
|---|---|
| Linux, macOS | `python3 ~/.claude/skills/whisper-deepinfra/whisper_deepinfra.py` |
| Windows | `python "$env:USERPROFILE\.claude\skills\whisper-deepinfra\whisper_deepinfra.py"` |

## Primer uso: conseguir la llave

Correr `--estado` antes de nada. Si dice `llave: NO CONFIGURADA`, **pedírsela al
usuario con estas palabras**, sin inventar otro procedimiento:

> Para transcribir necesito una llave de DeepInfra, que es tuya y se cobra a tu
> cuenta. Son dos minutos: entra a https://deepinfra.com, crea la cuenta con Google
> o GitHub, y en **Dashboard → API Keys → New API Key** genera una. Pégamela aquí.
> Una hora de audio te va a costar alrededor de un centavo de dólar.

Cuando la dé, guardarla **por stdin**, nunca como argumento (un argumento queda en el
historial del shell y en la lista de procesos):

```bash
printf '%s' 'LA_LLAVE' | python3 ~/.claude/skills/whisper-deepinfra/whisper_deepinfra.py --guardar-llave
```

Queda en `~/.config/deepinfra/credentials` con permisos solo para su usuario, y la
reusan las demás skills de DeepInfra. **No pedirle que edite `~/.profile`, `~/.bashrc`
ni ninguna variable de entorno**: si ya tiene `DEEPINFRA_API_KEY` en el entorno, el
script la respeta, pero no hace falta ponerla ahí.

## Uso

```bash
# Lo normal: idioma conocido y salida a archivo
python3 .../whisper_deepinfra.py junta.m4a --idioma es -o junta.txt

# A stdout, autodetectando idioma
python3 .../whisper_deepinfra.py nota.ogg

# Traducir a inglés en vez de transcribir
python3 .../whisper_deepinfra.py presentacion.mp3 --tarea translate -o english.txt

# Ver el plan y el costo sin gastar API
python3 .../whisper_deepinfra.py larga.mp3 --simulacion
```

| Opción | Default | Para qué |
|---|---|---|
| `-o`, `--salida` | stdout | Archivo de texto de salida |
| `--idioma` | autodetectar | ISO-639-1 (`es`, `en`, `fr`…). **Pasarlo siempre que se sepa**: sale más preciso |
| `--tarea` | `transcribe` | `translate` lo pasa a inglés |
| `--simulacion` | — | Plan y costo estimado, sin llamar a la API |
| `--estado` | — | Diagnóstico: llave, ffmpeg, rutas |
| `--guardar-llave` | — | Lee la llave de stdin y la guarda |

Formatos: `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `ogg`, `opus`, `wav`, `webm`.

## Audios largos: ya está resuelto, no partirlos a mano

El límite de DeepInfra es 25 MB por llamada, pero **el script lo maneja solo**. Si el
archivo no cabe, lo recomprime con ffmpeg a 16 kHz mono, que es todo lo que Whisper
aprovecha, y solo si aun así no cabe lo parte en tramos y une el texto.

En la práctica una sola llamada cubre **hasta unos 105 minutos** de audio. Medido: una
junta de 64 minutos y 33 MB baja a 14.8 MB y se resuelve en una llamada, 59 segundos.

> ⚠️ **Cuando sí hay que partir (audios de más de ~1h45m), se pierde una palabra en
> cada corte.** El corte es a tiempo fijo, así que cae donde caiga. Son una o dos
> palabras por frontera, y las fronteras son pocas, pero si el audio es material
> delicado conviene avisarle al usuario en vez de que lo descubra leyendo.

Para audios grandes hace falta **ffmpeg**. Si no está, el script lo dice con el comando
exacto para instalarlo. Es parte del runtime que deja listo la sección A4 de las skills
`instalar-lanzador-rc-linux` y `instalar-lanzador-rc-windows`.

## Si hay que volver a leer el archivo de salida

En Windows el `.txt` se escribe **con BOM**, a propósito: sin él, PowerShell 5.1 y
Excel lo leen con la página de códigos local y la transcripción se ve llena de basura.
Al leerlo de vuelta desde código, usar `encoding="utf-8-sig"`, que funciona con BOM y
sin él. Con `utf-8` a secas aparece un `﻿` pegado al principio del texto.

## Al terminar, reportar

El texto o la ruta del archivo, el idioma detectado y **el costo real**. El script ya lo
imprime. Cada llamada queda anotada en `~/.cache/whisper-deepinfra.log`:

```
2026-08-03 23:58:12	OK 	3869.1s	$0.01290	Audio Cadena.m4a	transcribe	es	cadena.txt
```

Lo gastado hoy:

```bash
awk -F'\t' -v d="$(date +%Y-%m-%d)" '$1 ~ d {gsub(/[$]/,"",$4); s+=$4} END {printf "hoy: $%.5f\n", s}' ~/.cache/whisper-deepinfra.log
```

## Cuándo NO usar esta skill

- **Generar voz o audio (TTS).** Es la tarea contraria, no aplica.
- **Video de YouTube.** Va la skill `youtube-research`, que baja los subtítulos ya
  hechos: es gratis y más exacto que transcribir el audio.
- **Video local.** Sacar primero la pista de audio: `ffmpeg -i video.mp4 -vn -ac 1 audio.mp3`.
- **Leer un PDF o una foto de un documento.** Eso es lectura de imagen, no Whisper.
- **Saber quién dijo qué.** Whisper **no separa hablantes**. Devuelve el texto corrido.
  Si el usuario pide una minuta con nombres, decírselo antes de transcribir, no después.

## Errores comunes

| Lo que sale | Qué pasó |
|---|---|
| `llave: NO CONFIGURADA` | Nunca se guardó. Pedirla y guardarla con `--guardar-llave` |
| `HTTP 401` o `403` | La llave se revocó o se pegó incompleta. Volver a guardarla |
| `HTTP 402` | La cuenta de DeepInfra no tiene saldo. Va a https://deepinfra.com/dash/billing |
| `hace falta ffmpeg` | Audio grande sin ffmpeg instalado. El mensaje trae el comando |
| Transcripción vacía | El archivo no trae voz, o está corrupto. Verificar con `--simulacion` |
