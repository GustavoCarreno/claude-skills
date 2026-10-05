# A4 · El runtime que las skills de documentos dan por hecho, con sus cinco pruebas

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A4. El runtime que las skills dan por hecho
  - A4a. Todo lo que sale de winget
  - A4b. Los dos que NO se registran solos en el PATH
  - A4c. El español de Tesseract, que no viene incluido
  - A4d. Los paquetes de lenguaje
  - A4e. El plugin de documentos
  - A4f. Lo que hay que hacer distinto que en Linux
  - A4g. Las cinco pruebas de aceptación

<!-- fin del encabezado agregado al partir -->

## A4. El runtime que las skills dan por hecho


**Este paso existe porque las skills que se entregan instaladas no traen lo que
necesitan para correr.** Se instalan con un comando y eso es gratis, pero por dentro
asumen un runtime que solo viene preinstalado en el entorno de Anthropic. En una laptop
recién comprada no hay nada de eso, y **falla tarde, ya con la persona esperando su
documento**.

Lo concreto: `presentacion-elegante` envuelve a `document-skills:pptx`, y su ciclo de
revisión visual necesita LibreOffice y Poppler. `youtube-research` necesita `yt-dlp` y
`ffmpeg`. Sin A4, esas skills aparecen en la lista y no funcionan.

**Son dos capas:** el plugin `document-skills` (que trae las skills y sus scripts) y el
runtime del sistema (que esos scripts invocan). Instalar solo la primera no sirve de nada.

> ✅ **Poppler sí existe para Windows y está en `winget`.** Es `oschwartz10612.Poppler`, la
> compilación que la propia documentación de `pdf2image` recomienda. **No hace falta aceptar
> ninguna degradación del ciclo de revisión visual**, que era la duda abierta antes de
> medirlo en la VM.

### A4a. Todo lo que sale de winget

```powershell
$ids = @(
  "TheDocumentFoundation.LibreOffice",
  "JohnMacFarlane.Pandoc",
  "tesseract-ocr.tesseract",
  "oschwartz10612.Poppler",
  "OpenJS.NodeJS",
  "yt-dlp.yt-dlp"
)
foreach ($id in $ids) {
  winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
}
```

**IDs verificados en la VM**, no supuestos. Dos notas sobre elecciones que no son obvias:

- **`tesseract-ocr.tesseract` es el oficial y va en 5.5**, más nuevo que el de UB Mannheim
  (`UB-Mannheim.TesseractOCR`, en 5.4). Cualquiera de los dos sirve; se prefiere el oficial.
- **`yt-dlp.yt-dlp` arrastra `ffmpeg` como dependencia**, así que no hay que instalarlo
  aparte. Es el que necesita `youtube-research`.

> ⚠️ **`winget` deja el PATH viejo en la consola en curso**, el mismo aviso de A1. Abrir una
> consola nueva antes de verificar nada de aquí.

### A4b. Los dos que NO se registran solos en el PATH

**Medido en la VM: LibreOffice y Tesseract se instalan en `Program Files` y no se agregan
al PATH.** Poppler y Pandoc sí lo hacen. Como las skills los invocan por nombre, sin esto
fallan con "no se reconoce el comando":

```powershell
$agregar = @("C:\Program Files\LibreOffice\program", "C:\Program Files\Tesseract-OCR")
$actual = [Environment]::GetEnvironmentVariable("Path", "User")
foreach ($d in $agregar) {
  if ((Test-Path $d) -and ($actual -notlike "*$d*")) { $actual = $actual.TrimEnd(";") + ";" + $d }
}
[Environment]::SetEnvironmentVariable("Path", $actual, "User")
```

### A4c. El español de Tesseract, que no viene incluido

**El paquete instala solo `eng` y `osd`.** Sin esto, el OCR de un documento en español
devuelve basura en vez de fallar, que es peor porque nadie lo nota:

```powershell
Invoke-WebRequest -UseBasicParsing `
  -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata" `
  -OutFile "C:\Program Files\Tesseract-OCR\tessdata\spa.traineddata"
```

Son unos 18 MB. Verificar con `tesseract --list-langs`, tiene que aparecer `spa`.

### A4d. Los paquetes de lenguaje

```powershell
python -m pip install openpyxl pandas "markitdown[pptx]" Pillow defusedxml lxml `
                     pytesseract pdf2image pypdf pdfplumber reportlab

npm install -g docx pptxgenjs react react-dom react-icons sharp

# require() no resuelve paquetes npm globales desde una carpeta cualquiera
[Environment]::SetEnvironmentVariable("NODE_PATH", (npm root -g).Trim(), "User")
```

> 📌 **En Windows `pip install` a secas sí funciona.** No aplica el
> `externally-managed-environment` (PEP 668) que obliga a `--break-system-packages` en
> Ubuntu 24.04, así que el comando es más corto que el de Linux. Es de las pocas cosas que
> aquí salen más fáciles.

> ⚠️ **`NODE_PATH` no es opcional.** `docx` y `pptxgenjs` quedan instalados global, pero las
> skills corren sus scripts desde el proyecto de quien las usa, y desde ahí `require()` no
> los encuentra. Verificar en una consola nueva, **parado en otra carpeta**:
> `cd $env:TEMP; node -e "require('docx'); require('sharp'); console.log('OK')"`.

### A4e. El plugin de documentos

```powershell
claude plugin marketplace add anthropics/skills
claude plugin install document-skills@anthropic-agent-skills
claude plugin list          # debe decir "enabled"
```

### A4f. Lo que hay que hacer distinto que en Linux

> ⚠️ **Los scripts auxiliares del plugin NO corren en Windows, y hay que saberlo antes de
> seguir su documentación al pie de la letra.** `xlsx/scripts/recalc.py` y
> `pptx/scripts/thumbnail.py` fallan con
> `module 'socket' has no attribute 'AF_UNIX'`, porque los dos pasan por
> `pptx/scripts/office/soffice.py`, que es un shim pensado para el entorno aislado de
> Anthropic (detecta sockets de dominio Unix bloqueados y compila un `.so` para rodearlos).
> Nada de eso existe en Windows.
>
> **La buena noticia es que ahí ese shim no hace falta para nada: `soffice` directo
> funciona.** Donde la documentación del plugin diga
> `python scripts/office/soffice.py ...`, en Windows va `soffice` a secas.
> (`pptx/scripts/clean.py` sí corre, porque no toca LibreOffice.)

```powershell
# Recalcular un Excel (el equivalente de recalc.py)
soffice --headless --convert-to xlsx --outdir recalculado archivo.xlsx

# Revisión visual de una presentación (el equivalente de thumbnail.py)
soffice --headless --convert-to pdf --outdir rev archivo.pptx
pdftoppm -jpeg -r 150 rev\archivo.pdf rev\diapo
```

> 📌 **`soffice.exe` sí espera a terminar en Windows**, o sea que el archivo ya existe
> cuando el comando regresa y no hace falta meter una espera artificial. Se comprobó
> revisando el archivo inmediatamente después. `soffice.com` se comporta igual.

### A4g. Las cinco pruebas de aceptación

**No dar A4 por terminado sin correrlas.** Cada una revienta por una pieza distinta.

| # | Prueba | Qué pieza demuestra |
|---|---|---|
| 1 | Generar un `.docx` y convertirlo a PDF | npm `docx` más `soffice` |
| 2 | Generar un `.xlsx` **con una fórmula y leer su resultado** | LibreOffice recalculando |
| 3 | Generar un `.pptx` y sacarle la imagen de revisión | `pptxgenjs`, `sharp`, `soffice`, `pdftoppm` |
| 4 | Leer un PDF escaneado con OCR | Tesseract con el español de A4c |
| 5 | Correr `presentacion-elegante` de punta a punta | Que todo lo anterior esté bien cableado |

> ⚠️ **La prueba 2 es la filosa y hay que leerla bien.** `openpyxl` escribe la fórmula pero
> **no la evalúa**, así que sin LibreOffice el archivo sale con las celdas de resultado
> **vacías** y nadie se entera hasta que el cliente lo abre. Medido en la VM: leído sin
> recalcular da `A3=None`; tras pasar por LibreOffice da `A3=1540`. Una prueba que solo
> verifique "se generó el archivo" **pasa igual con el defecto adentro**.

> ⚠️ **En la prueba 4, `pytesseract` puede no encontrar el ejecutable** aunque esté en el
> PATH del sistema. Si pasa, fijarlo explícito en el script:
> `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`.
