---
name: youtube-research
description: Investigar videos de YouTube — extraer transcripción, metadata, o buscar videos por query. Activar cuando el usuario pegue una URL de YouTube, pida transcripción/subtítulos de un video, pida metadata de un video (título, canal, duración, views), o pida "búscame videos de YouTube sobre X / los top N sobre Y".
---

# YouTube Research — transcript, metadata y búsqueda con yt-dlp

Skill para extraer información de YouTube sin abrir el navegador. Cubre tres operaciones: **transcripción** (subtítulos limpios), **metadata** (título/canal/duración/views/descripción), y **búsqueda** (top N videos por query).

Diseño cross-OS: los comandos `yt-dlp` son idénticos en Linux/mac/Windows; el parsing lo hace Claude leyendo los archivos de salida con Read. Único helper: `clean-vtt.js` (Node, garantizado por Claude Code).

## Prerrequisito

`yt-dlp` instalado y en PATH. Verificar con `yt-dlp --version`. Si no está:

- **Linux/mac:** `pip install --user --break-system-packages yt-dlp`
- **Windows:** `winget install -e --id yt-dlp.yt-dlp --accept-source-agreements --accept-package-agreements --silent` (instala también ffmpeg como dependencia — útil para extracción de audio futura)

Node.js viene con Claude Code — no hay prereq adicional.

## Working directory

Siempre usar `/tmp` en Linux/mac o `$env:TEMP` en Windows para archivos intermedios. Nunca dejar residuos en el proyecto del usuario.

## Operación 1 — Metadata de un video

```bash
# Linux/mac
yt-dlp --dump-json --skip-download "<URL>" > /tmp/yt-meta.json

# Windows PowerShell — nota las comillas simples en el template, ver "Gotchas"
yt-dlp --dump-json --skip-download "<URL>" | Out-File -Encoding utf8 "$env:TEMP\yt-meta.json"
```

Luego leer el archivo con Read y extraer: `title`, `channel`, `channel_url`, `duration_string`, `upload_date`, `view_count`, `like_count`, `description`. Los `chapters` (array) están ahí si el video los tiene — útiles para índice navegable.

El JSON es ~5-15 KB por video, cómodo para lectura directa por Claude.

## Operación 2 — Transcripción de un video

```bash
# Linux/mac
cd /tmp && yt-dlp --write-auto-subs --write-subs \
  --sub-langs "<prefs>" --skip-download --sub-format "vtt/best" \
  -o "yt-%(id)s.%(ext)s" "<URL>"

# Windows PowerShell — comillas simples en -o son OBLIGATORIAS, ver Gotchas
cd $env:TEMP; yt-dlp --write-auto-subs --write-subs `
  --sub-langs "<prefs>" --skip-download --sub-format 'vtt/best' `
  -o 'yt-%(id)s.%(ext)s' "<URL>"
```

Preferencias de idioma:
- Video en español → `"es,es-orig,en"`
- Video en inglés → `"en,en-orig,es"`
- Desconocido → `"es,en"`

Si salen múltiples `.vtt`, usar el que mejor corresponda al idioma hablado del video.

Luego limpiar con el helper (mismo comando en los 3 SOs):

```bash
node <skill-dir>/clean-vtt.js /tmp/yt-<id>.en.vtt > /tmp/yt-<id>.txt
```

Donde `<skill-dir>` es `~/.claude/skills/youtube-research` (Linux/mac) o `$env:USERPROFILE\.claude\skills\youtube-research` (Windows).

El cleanup toma la última línea de cada cue (la más completa) y elimina duplicaciones consecutivas — patrón canónico para VTT auto-generado de YouTube.

**Si el usuario pide el resultado como archivo markdown** en el vault/proyecto, estructura:

```markdown
---
titulo: <título>
canal: <channel>
url: <URL>
duracion: <HH:MM:SS>
publicado: <YYYY-MM-DD>
views: <número>
---

# <título>

**Canal:** <canal> · **Duración:** <duración> · **Publicado:** <fecha>

## Descripción

<descripción del video>

## Transcripción

<transcript limpio>
```

## Operación 3 — Búsqueda por query

```bash
# Linux/mac
yt-dlp --dump-json --skip-download "ytsearch<N>:<query>" > /tmp/yt-search.jsonl

# Windows PowerShell
yt-dlp --dump-json --skip-download "ytsearch<N>:<query>" | Out-File -Encoding utf8 "$env:TEMP\yt-search.jsonl"
```

El output es JSONL (un JSON por línea, una línea por video). Leer con Read y presentar tabla markdown al usuario con columnas: `#`, Título, Canal, Duración, Views, URL (`https://youtu.be/<id>`).

Si el usuario pide profundizar en un resultado específico, aplicar Operación 1 o 2 sobre esa URL.

## Gotchas cross-OS

| Síntoma | Causa | Fix |
|---|---|---|
| **Windows:** `id : The term 'id' is not recognized` al usar `-o "yt-%(id)s.%(ext)s"` | PowerShell interpreta `%()` como subexpresión | Usar comillas simples: `-o 'yt-%(id)s.%(ext)s'` |
| `HTTP Error 429: Too Many Requests` al pedir varios idiomas | Rate limit de YouTube | Pedir un solo idioma; esperar 1-2 min si se repite |
| `No subtitles were available` | Video sin subs ni auto-generados | Si es crítico, descargar audio con `-x --audio-format mp3` y transcribir con Whisper; si no, reportar al usuario |
| `Video unavailable / Private video` | Video privado, age-gated, o región | Reportar al usuario, no intentar bypass |
| `Python was not found` (Windows) al ejecutar snippets antiguos | El skill ya no usa Python | Usar `clean-vtt.js` con Node (siempre disponible) |
| `No supported JavaScript runtime` (warning) | yt-dlp nuevo pide JS runtime para algunos formatos | Ignorable para subs+metadata; si falla descarga real instalar `deno` |
| Output VTT vacío | Video con subs solo en idioma distinto al pedido | Re-intentar con `--sub-langs "all"` y verificar qué idiomas regresó |

## Consideraciones de costo de contexto

Transcripts de videos de 30+ min son grandes (10-30k palabras). Antes de leer el transcript completo:

- Si el usuario solo quiere "dime si vale la pena": leer primeros y últimos ~500 chars del `.txt` con `offset`/`limit` de Read, más metadata, y juzgar con eso
- Si el usuario quiere resumen: usar subagent con el transcript completo y pedir síntesis de 300 words
- Si el usuario quiere cita literal: leer con `offset`/`limit` la sección relevante

El transcript limpio se puede guardar en `/tmp/yt-<id>.txt` y referenciar por path en vez de leer completo.

## Cuándo NO usar este skill

- Video detrás de paywall (Netflix, cursos privados): yt-dlp funciona solo para YouTube público
- Cuando el usuario ya pegó el transcript: no re-descargar
- Playlists gigantes (100+ videos): confirmar con el usuario antes de procesar batch
