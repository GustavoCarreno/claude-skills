---
name: presentacion-elegante
description: "Use when the user asks to create, generate, build, armar, hacer, or hazme a deck, slides, pptx, presentation, pitch, or diapositivas. Wraps the official pptx skill (document-skills:pptx) with rigid discipline against three failure modes: boring defaults (blue + Arial + title+bullets), skipped visual QA, and placeholder content. Does NOT fire on read-only intent (parsing or extracting text from an existing pptx)."
---

# Presentación Elegante

Skill que se activa cuando se pide crear una presentación desde Claude Code. Envuelve la skill oficial `document-skills:pptx` de Anthropic y fuerza calidad ejecutiva por default.

## Prerrequisito

Esta skill requiere tener instalado el plugin `document-skills` de Anthropic (que contiene la skill `pptx` con paletas, pptxgenjs, scripts de export y QA prompt). Instalación:

```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

También se puede sin la consola interactiva, que es lo práctico al instalar una máquina:

```bash
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
```

Sin ese plugin, esta skill no tiene a qué delegar las mecánicas y no producirá resultados útiles.

> ⚠️ **El plugin NO trae el runtime que sus scripts invocan**, y ese runtime solo viene
> preinstalado en el entorno de Anthropic. En una máquina nueva hacen falta **LibreOffice**
> (`soffice`) y **Poppler** (`pdftoppm`) para el ciclo de revisión visual, más los paquetes
> npm `pptxgenjs` y `sharp`. Con Node instalado global, `require()` no los resuelve desde una
> carpeta cualquiera: hace falta la variable `NODE_PATH` apuntando a `npm root -g`.
>
> El procedimiento completo, por sistema operativo y con sus pruebas de aceptación, está en
> la sección **A4** de las skills `instalar-lanzador-rc-linux` e `instalar-lanzador-rc-windows`.

## Cómo usar esta skill

1. Cargar también la skill oficial `document-skills:pptx`. Ahí viven las mecánicas: paletas de color, font pairings, pptxgenjs patterns, QA prompt, scripts de export. **No las dupliques aquí, referénciala.**
2. Antes de cualquier línea de código, ejecutar la **declaración de compromiso** (sección siguiente).
3. Durante la generación, respetar las 4 no-negociables.
4. Antes de declarar "listo", cerrar el QA loop visual con subagente(s).

## Declaración de compromiso (obligatoria antes de escribir código)

Al agente: antes de escribir la primera línea de pptxgenjs, imprime en el chat **exactamente este bloque**, rellenado con tus elecciones:

```
Compromiso para este deck:
- Paleta: <nombre de la paleta elegida de las 10 del skill pptx oficial>
- Fonts: <header font> / <body font>
- Motif: <elemento visual repetido, una sola línea>
```

Espera confirmación o veto del usuario antes de continuar. Si veta algo, re-elige y vuelve a imprimir el bloque.

## No-negociables

### 1. Contra defaults aburridos

- **Paleta:** elige de las 10 de la skill oficial pptx. **Prohibido** default a Midnight Executive o a "azul genérico". Elige por fit con el tema del deck (Coral Energy para pitch energético, Charcoal Minimal para ejecutivo serio, Forest & Moss para sustentabilidad, Warm Terracotta para cálido-humano, Berry & Cream para premium-femenino, etc.).
- **Font pairing:** **prohibido** Arial/Arial y Calibri/Calibri. Al menos el header con personalidad (Georgia, Cambria, Palatino, Impact, Trebuchet MS).
- **Motif visual:** compromete **uno** y repítelo en cada slide. Opciones: íconos en círculos de color, imágenes con bordes redondeados, half-bleed en un lado, barra lateral de color, borde grueso unilateral, números grandes de sección. **Uno solo**, no mezclar.

### 2. Contra contenido placeholder-ish

- Todo nombre propio, fecha, cifra o stat viene de: la conversación actual, archivos adjuntos por el usuario, memoria del proyecto, o archivos del vault. **Cero invención.**
- Si falta un dato crítico (stat de mercado sin fuente, nombre de stakeholder no mencionado, cifra de financials ausente): **detén la generación y pregunta al usuario.** Nunca fabriques.
- Antes de export final, ejecutar QA textual:
  ```bash
  python -m markitdown output.pptx | grep -iE "\blorem\b|\bipsum\b|\bTODO\b|\[insert|sample text|ejemplo de|\bxxxx\b|\bTBD\b"
  ```
- Si el grep matchea algo: arregla el contenido y vuelve a correr el grep antes de continuar.

### 3. Por slide

- Cada slide tiene **al menos 1 elemento visual no-decorativo** (imagen real, chart con data, ícono con significado, shape que organiza contenido). Decoración gratuita no cuenta.
- **Prohibido** usar "título + bullets" como layout único. Puede aparecer **máximo 1 vez por deck**, nunca más.
- **Layouts varían:** no más de 2 slides consecutivos con el mismo layout. Rotar entre: two-column, icon+text rows, 2x2 grid, half-bleed image, stat callout, comparison columns, timeline, quote slide, section divider.

### 4. Contra QA visual saltado (rígido)

Obligatorio antes de declarar "listo":

1. **Export a imágenes.** El comando depende del sistema, y **usar el equivocado no degrada
   el resultado: lo impide**, porque sin imágenes no hay QA visual y el paso 2 no puede correr.

   **Linux / macOS:**
   ```bash
   python scripts/office/soffice.py --headless --convert-to pdf output.pptx
   rm -f slide-*.jpg
   pdftoppm -jpeg -r 150 output.pdf slide
   ls -1 "$PWD"/slide-*.jpg
   ```

   **Windows PowerShell:**
   ```powershell
   soffice --headless --convert-to pdf output.pptx
   Remove-Item slide-*.jpg -ErrorAction SilentlyContinue
   pdftoppm -jpeg -r 150 output.pdf slide
   Get-ChildItem slide-*.jpg | Select-Object -ExpandProperty FullName
   ```

   > ⚠️ **En Windows NO uses `scripts/office/soffice.py`**, aunque el `SKILL.md` de la skill
   > oficial `pptx` lo diga. Ese script es un shim para el entorno aislado de Anthropic:
   > detecta sockets de dominio Unix bloqueados y compila un `.so` para rodearlos. En Windows
   > truena con `module 'socket' has no attribute 'AF_UNIX'`, **y ahí no hace falta para nada**,
   > porque `soffice` directo funciona y además espera a terminar. Lo mismo aplica a
   > `xlsx/scripts/recalc.py`, que pasa por el mismo shim.
   >
   > **Si `soffice` o `pdftoppm` "no se reconocen" en Windows**, no están en el PATH.
   > LibreOffice se instala en `C:\Program Files\LibreOffice\program` y no se registra solo.

2. **Dispatch subagent** con el prompt de visual QA que trae la skill oficial pptx (sección "Visual QA" de su SKILL.md). Pasa los paths absolutos exactos que imprimió el último comando del paso 1.

3. **Mínimo 1 ciclo completo** fix, re-render y verify, aunque la primera pasada parezca limpia. Nunca saltarse el ciclo.

4. Si el subagent reporta **cero issues en la primera pasada**, dispatch un **segundo subagent** distinto antes de declarar done. La skill oficial ya lo dice textualmente: *"if you found zero issues on first inspection, you weren't looking hard enough"*.

5. No declarar "listo" hasta que **una pasada completa** del subagent reporte cero issues.

## Idioma de los slides

Hereda del contexto. Si el usuario pide la presentación en español, los slides van en español. Si en inglés, en inglés. No defaults, no traducciones automáticas.

## Bypass (para drafts rápidos sin discipline)

Si alguna vez quieres un draft rápido sin toda esta discipline, mueve temporalmente el folder fuera del path de descubrimiento de Claude Code:

**Linux / macOS:**
```bash
mv ~/.claude/skills/presentacion-elegante /tmp/presentacion-elegante-off
```

**Windows PowerShell:**
```powershell
Move-Item $HOME\.claude\skills\presentacion-elegante $env:TEMP\presentacion-elegante-off
```

Reinicia Claude Code y la skill no se cargará. Para reactivar, mueve el folder de regreso a su ubicación original.

Nota: renombrar con prefijo `_` o similar dentro del mismo `~/.claude/skills/` no es suficiente, Claude Code sigue descubriendo folders con `SKILL.md` dentro. Hay que moverlo fuera del path.
