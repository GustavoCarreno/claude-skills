# A4 · El runtime que las skills de documentos dan por hecho, con sus cinco pruebas

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A4. El runtime que las skills dan por hecho
  - A4a. El runtime del sistema
  - A4b. Node, en la versión correcta
  - A4c. Los paquetes de lenguaje
  - A4d. El gotcha que rompe `docx` y `pptx` sin decir por qué
  - A4e. El plugin de documentos
  - A4f. Las cinco pruebas de aceptación

<!-- fin del encabezado agregado al partir -->

## A4. El runtime que las skills dan por hecho


**Este paso existe porque las skills que se entregan instaladas no traen lo que
necesitan para correr.** Se instalan con un comando y eso es gratis, pero por dentro
asumen un runtime que solo viene preinstalado en el entorno de Anthropic. En una
laptop recién comprada no hay nada de eso, y el modo de fallar es el peor posible:
**falla tarde, ya con la persona esperando su documento**.

Lo concreto: `presentacion-elegante` envuelve a `document-skills:pptx`, y su ciclo de
revisión visual necesita LibreOffice y Poppler. `youtube-research` necesita `yt-dlp` y
`ffmpeg`. Sin A4, esas skills aparecen en la lista y no funcionan.

**Son dos capas, y se confunden fácil:** el plugin `document-skills` (que trae las
skills y sus scripts), y el runtime del sistema (que los scripts invocan). Instalar solo
la primera no sirve de nada.

### A4a. El runtime del sistema

```bash
sudo apt-get update
sudo apt-get install -y \
  libreoffice pandoc poppler-utils tesseract-ocr tesseract-ocr-spa ffmpeg
```

Entre 1 y 3 minutos según la conexión, y unos 2.6 GB de disco. Sin licenciamiento de por
medio. **Todo A4 junto (runtime, Node, paquetes y plugin) pesa unos 4 GB.**

> ⚠️ **`tesseract-ocr-spa` va aparte y es fácil olvidarlo.** El paquete base solo trae
> inglés, así que sin él el OCR de un documento en español devuelve basura en vez de
> fallar, que es peor. Verificar con `tesseract --list-langs`, tiene que aparecer `spa`.

### A4b. Node, en la versión correcta

**No sirve el Node de los repos de Ubuntu.** Trae la 18, y `sharp` (que `pptx` usa para
las imágenes) exige 20.9 o mayor. Instalado con `apt`, `require('sharp')` truena con
`Could not load the "sharp" module`, y no al instalar sino al generar la presentación.

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version   # tiene que decir v22.x, no v18.x
```

### A4c. Los paquetes de lenguaje

```bash
# Python. El --break-system-packages NO es opcional en Ubuntu 24.04, ver el aviso abajo.
pip3 install --user --break-system-packages \
  openpyxl pandas "markitdown[pptx]" Pillow defusedxml lxml \
  pytesseract pdf2image pypdf pdfplumber reportlab yt-dlp

# Node
sudo npm install -g docx pptxgenjs react react-dom react-icons sharp
```

> ⚠️ **`pip3 install` a secas falla en Ubuntu 24.04**, con un error de
> `externally-managed-environment` (PEP 668). Un venv tampoco sirve aquí, porque los
> scripts del plugin se invocan con el `python3` del sistema y no verían el venv. La
> salida es `--user --break-system-packages`, que es además lo que ya usa la skill
> `youtube-research`.

> ⚠️ **`~/.local/bin` tiene que estar en el PATH**, o `markitdown` y `yt-dlp` quedan
> instalados pero no se encuentran. Es el mismo aviso de A1, que reaparece aquí.

### A4d. El gotcha que rompe `docx` y `pptx` sin decir por qué

**Un paquete npm instalado global NO se resuelve con `require()` desde una carpeta
cualquiera.** Las skills corren sus scripts desde el proyecto de quien las usa, o sea
desde cualquier lado, así que `require('docx')` falla con `Cannot find module` aunque
`npm list -g` lo muestre instalado. Se arregla con una variable, de una vez y para siempre:

```bash
cat >> ~/.profile <<'EOF'

# Las skills de documentos corren node desde carpetas arbitrarias; sin esto,
# require() no encuentra los paquetes npm globales.
export NODE_PATH="/usr/lib/node_modules"
EOF
```

Abrir una terminal nueva después. **Verificar desde una carpeta que no sea la de
instalación**, que es justo lo que distingue esta prueba:

```bash
cd /tmp && node -e 'require("docx"); require("sharp"); console.log("OK")'
```

### A4e. El plugin de documentos

Los dos slash commands que documenta `presentacion-elegante` funcionan, pero **hay
equivalente de línea de comandos**, que es lo que conviene en una instalación:

```bash
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin list          # debe decir "enabled"
```

### A4f. Las cinco pruebas de aceptación

**No dar A4 por terminado sin correrlas.** Cada una revienta por una pieza distinta, y
la segunda es la que de verdad importa.

| # | Prueba | Qué pieza demuestra |
|---|---|---|
| 1 | Generar un `.docx` y convertirlo a PDF | npm `docx` más `soffice` |
| 2 | Generar un `.xlsx` **con una fórmula y leer su resultado** | LibreOffice recalculando |
| 3 | Generar un `.pptx` y sacarle la imagen de revisión | `pptxgenjs`, `sharp`, `soffice`, `pdftoppm` |
| 4 | Leer un PDF escaneado con OCR | Tesseract con el paquete de español |
| 5 | Correr `presentacion-elegante` de punta a punta | Que todo lo anterior esté bien cableado |

> ⚠️ **La prueba 2 es la filosa y hay que leerla bien.** `openpyxl` escribe la fórmula
> pero **no la evalúa**, así que sin LibreOffice el archivo sale con las celdas de
> resultado **vacías** y nadie se entera hasta que el cliente lo abre. Medido en el banco
> limpio: leído sin recalcular da `A3=None`; tras pasar por LibreOffice da `A3=1540`. Una
> prueba que solo verifique "se generó el archivo" **pasa igual con el defecto adentro**.

El plugin trae sus propios scripts para esto, y conviene usarlos porque es exactamente lo
que va a correr en producción:

```bash
SK=$(ls -d ~/.claude/plugins/cache/*/document-skills/*/skills | head -1)
python3 "$SK/xlsx/scripts/recalc.py" archivo.xlsx        # recalcula y reporta errores
python3 "$SK/pptx/scripts/office/soffice.py" --headless --convert-to pdf archivo.pptx
python3 "$SK/pptx/scripts/thumbnail.py" archivo.pptx     # rejilla de miniaturas
```
