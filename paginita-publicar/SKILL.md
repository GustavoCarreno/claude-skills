---
name: paginita-publicar
description: Publicar, actualizar, eliminar y listar subpáginas HTML/markdown bajo un slug dueño en paginita.de via HTTP API. Activar cuando el usuario diga "paginita", "página" o "sitio web" en contexto de publicar contenido web (temporal o con nombre), no necesariamente la palabra "paginita". También cuando pida crear una página para ver en celular, compartir por link, publicar algo rápido, o subir un documento como página web.
---

# Paginita — publicar subpáginas via HTTP API

Skill para publicar contenido web bajo el namespace de un slug dueño en `https://paginita.de/<slug>/...`. Usa la API HTTP (3 webhooks: publicar, listar, eliminar) en vez de SSH/SCP directo al host.

## Conceptos clave (distinto al skill legacy)

- Las subpáginas viven **bajo un slug dueño**. URL: `paginita.de/<slug>/<nombre>/` (permanente) o `paginita.de/<slug>/temporales/<uuid>/` (temporal).
- El skill publica bajo un **solo slug dueño por sesión**, determinado por env vars.
- El backend **renderiza markdown server-side** — no se necesita pandoc local. Si el contenido empieza con `<!DOCTYPE` o contiene `<html>`/`<body>`, se detecta como HTML crudo; si no, como markdown.
- La paginita dueña puede ser privada (con clave) — las subpáginas heredan esa clave automáticamente, salvo que pases `clave: "publica"` o una clave propia.

## Credenciales

El skill auto-carga credenciales desde **`~/.config/paginita/credentials`** al inicio de cada operación. Formato (shell-sourceable):

```bash
export PAGINITA_API_KEY="<bearer token hex de 64 chars, del panel admin del slug>"
export PAGINITA_SLUG="gustavo"
export PAGINITA_ENV="prd"   # dev | qas | prd
```

**Solo necesitas el Bearer token** (`PAGINITA_API_KEY`). Los 3 webhooks de subpáginas son endpoints públicos autenticados únicamente por Bearer + match contra `sitios.api_key` en BD. **No uses `x-api-key`** — fue un secreto compartido del sistema retirado el 2026-04-14 para permitir delegar acceso a terceros sin filtrarlo.

### Setup inicial (primera vez o cuando se rota la api_key)

Si no existe `PAGINITA_API_KEY` (archivo ausente o variable vacía tras source):

1. **Pedir al usuario su API key**. Instrucciones para que la obtenga:
   > Visita `https://paginita.de/<slug>/admin/#clave=<clave_admin>` (si no recuerdas tu `clave_admin`, escribe a `hola@paginita.de` — te llega la guía automática con el link a tu panel admin con clave incluida; **no** escribas a `ayuda@paginita.de`, ese buzón es soporte humano). En la sección **"Subpáginas (N/100)"** clic en **"Generar API Key"**. La key te llega por email + se muestra enmascarada en el panel.

2. Cuando el usuario provea la key, **guardarla automáticamente** (no pedirle que edite el archivo a mano):

   ```bash
   mkdir -p ~/.config/paginita
   chmod 700 ~/.config/paginita
   cat > ~/.config/paginita/credentials <<EOF
   export PAGINITA_API_KEY="<key-pegada-por-el-usuario>"
   export PAGINITA_SLUG="<slug>"
   export PAGINITA_ENV="prd"
   EOF
   chmod 600 ~/.config/paginita/credentials
   ```

   - `PAGINITA_SLUG` por defecto `gustavo` (cambiar si el usuario opera otro slug).
   - `PAGINITA_ENV` por defecto `prd`.

3. Si ya existe el archivo pero solo hay que **rotar** la key (panel admin → "Rotar"):
   ```bash
   sed -i 's|^export PAGINITA_API_KEY=.*|export PAGINITA_API_KEY="<nueva-key>"|' ~/.config/paginita/credentials
   ```

4. Tras escribir el archivo, **siempre** sourcear antes de la siguiente operación:
   ```bash
   . ~/.config/paginita/credentials
   ```

Tras el setup, todas las operaciones del skill comienzan con el **preámbulo canónico** (abajo) que sourcea el archivo y resuelve `BASE`/`WEB` por ambiente.

## Endpoints y URL base por ambiente

```
prd → https://auto.carreno.kia.mx  (dominio web: paginita.de)
qas → https://qas.auto.carreno.kia.mx  (dominio web: qas.paginita.de)
dev → https://dev.auto.carreno.kia.mx  (dominio web: dev.paginita.de)
```

**Preámbulo canónico** — pegar al inicio de cada bloque shell que use el skill:

```bash
[ -f ~/.config/paginita/credentials ] && . ~/.config/paginita/credentials
: "${PAGINITA_API_KEY:?falta PAGINITA_API_KEY — correr setup inicial}"
: "${PAGINITA_SLUG:=gustavo}"
: "${PAGINITA_ENV:=prd}"
case "$PAGINITA_ENV" in
  prd) BASE="https://auto.carreno.kia.mx";   WEB="https://paginita.de" ;;
  qas) BASE="https://qas.auto.carreno.kia.mx"; WEB="https://qas.paginita.de" ;;
  dev) BASE="https://dev.auto.carreno.kia.mx"; WEB="https://dev.paginita.de" ;;
  *) echo "PAGINITA_ENV inválido" >&2; exit 2 ;;
esac
```

## Lógica de decisión: temporal vs permanente

```
¿El usuario proporcionó un nombre (o slug corto tipo "reporte-al-jefe")?
  Sí → Permanente. No preguntar, proceder.
  No → Confirmar: "¿La publico como temporal? (expira en 7 días)" antes de proceder.
```

## Operaciones

### Publicar (crear o actualizar — es idempotente por slug+nombre)

El mismo endpoint hace crear y actualizar. Si el `nombre` ya existe bajo ese slug, reemplaza el contenido.

**Markdown (sin nombre → temporal):**

```bash
# Asumiendo $BASE, $WEB definidos; $CONTENIDO = archivo .md o string inline
curl -sS -X POST "$BASE/webhook/paginita-publicar-subpagina" \
  -H "Authorization: Bearer $PAGINITA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -cn --arg slug "$PAGINITA_SLUG" --rawfile c "$CONTENIDO" \
        '{slug:$slug, contenido:$c}')"
```

**HTML o markdown con nombre → permanente:**

```bash
curl -sS -X POST "$BASE/webhook/paginita-publicar-subpagina" \
  -H "Authorization: Bearer $PAGINITA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -cn --arg slug "$PAGINITA_SLUG" --arg nombre "reporte-al-jefe" \
        --rawfile c "$CONTENIDO" \
        '{slug:$slug, nombre:$nombre, contenido:$c}')"
```

**Parámetros opcionales del payload:**

- `nombre` — si se omite, temporal. Regex: `^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$`. Nombres reservados (ej. `admin`, `fotos`, `facturas`, `memes`) devuelven 409.
- `expira_en_dias` — solo temporales, default 7, max 365. Con `nombre` presente devuelve 422.
- `clave` — `"publica"` fuerza sin cifrado (incluso si la paginita dueña tiene clave); cualquier string 3-60 chars fija una clave propia; ausente hereda de la paginita dueña.
- `chat` — bool, activa widget chat en la subpágina (solo si el slug ya tiene `chat_webhook_url`).

**Respuesta 200:**

```json
{
  "url": "https://paginita.de/gustavo/reporte-al-jefe/",
  "tipo": "permanente",
  "cifrada": true,
  "tamano_bytes": 28456,
  "expira_en": null
}
```

**Códigos de error:** 401 auth · 403 api_key_slug_mismatch · 409 nombre reservado o conflicto filesystem · 413 >500KB · 422 validación/sanitización · 429 cuota (100 activas) o rate limit (60/hora) · 500 falla interna.

Devolver al usuario **solo la URL completa** (`.url` de la respuesta). Si es temporal, mencionar que expira en 7 días (o el valor de `expira_en_dias` que se pasó).

**Si la paginita dueña es privada**, devolver URL con `#clave=<clave>` — el frontend descifra automáticamente. Ejemplo: `https://paginita.de/gustavo/reporte/#clave=miclave`. El usuario puede obtener su clave con `SELECT clave FROM paginita.perfiles p JOIN paginita.usuarios u ON p.usuario_id=u.id WHERE u.slug='<slug>'` — o reconocerla si ya la recuerda.

### Listar subpáginas

```bash
curl -sS "$BASE/webhook/paginita-listar-subpaginas?slug=$PAGINITA_SLUG" \
  -H "Authorization: Bearer $PAGINITA_API_KEY"
```

**Respuesta 200:** objeto con `total`, `limite` (100), `subpaginas[]` con cada item `{nombre, tipo, url, tamano_bytes, cifrada, chat, creada_en, actualizada_en, expira_en}`.

Presentar al usuario en formato compacto: nombre, tipo, fecha, URL. Agrupar temporales y permanentes si ayuda legibilidad.

### Eliminar (hard delete)

```bash
curl -sS -X DELETE "$BASE/webhook/paginita-eliminar-subpagina" \
  -H "Authorization: Bearer $PAGINITA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -cn --arg slug "$PAGINITA_SLUG" --arg nombre "reporte-al-jefe" \
        '{slug:$slug, nombre:$nombre}')"
```

Para temporales, el `nombre` es el UUID (último segmento de la URL). Confirmar con el usuario antes de eliminar si no es obvio que lo solicitó explícitamente.

**Respuesta 200:** `{"eliminada": true, "url_previa": "..."}` · 404 si no existe · 401 auth.

### Actualizar

No hay operación separada — es la misma que publicar con el mismo `slug + nombre`. La API es idempotente. `actualizada_en` avanza, `creada_en` se preserva.

## Formatos de entrada

### Markdown

Pasar el contenido tal cual al campo `contenido`. El backend renderiza con `marked@4` + template paginita (Space Mono, responsive, estética consistente con la marca). No requiere preproceso local.

### HTML crudo

Pasar tal cual. Se detecta por el inicio del contenido (`<!DOCTYPE`, `<html>`, o `<body>`). La sanitización server-side strippea scripts inline, `on*` handlers, iframes, `javascript:` URIs. Conservan: tags semánticos, imágenes, CSS inline y `<style>`, clases, data-*, links a dominios en la whitelist CDN.

### Archivos en disco

Leer con `--rawfile` de `jq` (ver snippets arriba). Para HTML multi-archivo (con CSS/JS separado), consolidar a un solo archivo autocontenido antes de enviar — la API solo acepta un HTML/markdown por subpágina.

## Después de publicar

- Siempre devolver la URL completa.
- Si es temporal, mencionar la fecha de expiración (del campo `expira_en` en la respuesta).
- Si la paginita dueña tiene clave y no se forzó `"publica"`, adjuntar `#clave=<clave>` a la URL entregada para acceso sin fricción.

## Troubleshooting común

| Síntoma | Causa probable | Arreglo |
|---|---|---|
| 401 `auth_invalido` | `PAGINITA_API_KEY` vencida o mala | Rotar key desde panel admin, actualizar env var |
| 403 `api_key_slug_mismatch` | `PAGINITA_SLUG` no coincide con dueño de la api_key | Verificar slug con `curl ...listar?slug=X` |
| 413 | Contenido >500KB | Dividir en varias subpáginas, o comprimir assets |
| 422 `sanitizacion_fallida` | HTML con solo tags prohibidos | Revisar contenido — evitar scripts inline, usar tags semánticos |
| 429 `cuota_excedida` | Ya tienes 100 subpáginas activas | Listar y eliminar viejas |
| 429 `rate_limit` | >60 POSTs en 1 hora | Esperar |
| 409 `nombre_conflicto_filesystem` | Directorio existe en host sin fila BD (ej. directorio manual) | Elegir otro nombre |

## Nota histórica

Este skill reemplaza al anterior que publicaba vía SSH/SCP directo al host PRD (a `/temporales/<uuid>.html` o `/<slug>/`). El modelo cambió:
- URLs de temporales pasaron de `paginita.de/temporales/<uuid>.html` a `paginita.de/<slug>/temporales/<uuid>/`.
- URLs fijas pasaron de `paginita.de/<slug>/` (slug top-level nuevo) a `paginita.de/<slug>/<nombre>/` (subpágina de un slug existente).
- Ya no se crean slugs top-level desde este skill — solo subpáginas bajo un slug existente.
- El renderizado markdown ahora es server-side (marked@4) con template paginita oficial.

Si necesitas publicar bajo un slug top-level nuevo (onboarding de un nuevo dueño de paginita), eso se hace via email al registro oficial (`perfil@paginita.de`), no con este skill.
