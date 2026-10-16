# A10 · Los perfiles del equipo

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A10. Los perfiles del equipo
  - A10a. Qué son, y por qué se entregan aparte
  - A10b. Copiarlos
  - A10c. Dejar Gabinete como postura por defecto
  - A10d. Verificar
  - A10e. Lo que hay que decirle

<!-- fin del encabezado agregado al partir -->

## A10. Los perfiles del equipo

### A10a. Qué son, y por qué se entregan aparte

Ocho perfiles que el asistente se pone según el tema, cada uno con lo que un área de empresa sabe
revisar, preguntar y entregar: **GAB** (Gabinete), **GES** (Gestión), **PAS** (Procesos), **MID**
(Mercadotecnia), **ISI** (Infraestructura), **DAS** (Desarrollo), **CYF** (Finanzas, el criterio de dinero; se sumó el 16 de octubre de 2026) y **Tavo** (Tecnología Aplicada con Visión
Organizacional, todos en mesa; se llamó TAO hasta el 16 de octubre de 2026). Gabinete queda como la postura por defecto en todos los proyectos.

📌 **Los perfiles NO viven en este repositorio, que es público.** Son el método de trabajo de quien
instala, y los trae él en cada instalación: la carpeta `perfiles\` de su repositorio privado, con
la versión base y la **ficha del cliente** (`contexto.md`) ya llenada. Esta sección dice cómo se
instalan; el contenido llega con quien instala.

Antes de copiarlos, **el cliente escoge cuáles le sirven.** Conviene que sobre alguno a que falte.

> ⚠️ **Los archivos llevan acentos, así que viajan como archivos** (`scp` desde Linux, USB o una
> carpeta compartida), nunca pegados dentro de un `.ps1`. PowerShell 5.1 lee un script sin marca de
> orden de bytes como ANSI y convierte el `·` y los acentos en basura. Pasó el 11 de octubre de 2026
> con una ficha de contrato en la VM de prueba.

### A10b. Copiarlos

En PowerShell, con la carpeta de perfiles ya en la máquina en `$Origen` y el nombre de la carpeta
de la ficha en `$Cliente`:

```powershell
$Origen  = "$HOME\perfiles"       # donde quedó la carpeta perfiles\ que trajo quien instala
$Cliente = "nombre-del-cliente"   # la carpeta de su ficha, dentro de perfiles\clientes\
$Skills  = "$HOME\.claude\skills"
New-Item -ItemType Directory -Force -Path $Skills | Out-Null
# Una instalación anterior trae el equipo completo como equipo-tao: se aparta, con su ficha
if (Test-Path "$Skills\equipo-tao") { Move-Item "$Skills\equipo-tao" "$HOME\.claude\equipo-tao-anterior" }
Get-ChildItem "$Origen\base" -Directory -Filter "equipo-*" | ForEach-Object {
  Copy-Item $_.FullName -Destination $Skills -Recurse -Force
}
Copy-Item "$Origen\clientes\$Cliente\contexto.md" "$Skills\equipo-tavo\contexto.md" -Force
Get-ChildItem $Skills -Directory -Filter "equipo-*" | Select-Object Name
```

Para quitar un perfil que el cliente no quiso, se borra su carpeta (por ejemplo
`Remove-Item -Recurse "$Skills\equipo-mid"`) y su renglón en la ficha. **Tavo y su ficha se quedan
siempre**, porque los demás leen la ficha desde ahí.

### A10c. Dejar Gabinete como postura por defecto

Se agrega un bloque al `CLAUDE.md` global del cliente, leyendo y escribiendo en UTF-8 sin marca de
orden de bytes (con `Add-Content` de PowerShell 5.1 los acentos se dañan). El fragmento **quita
primero el bloque anterior y pone el nuevo**, así que correrlo dos veces deja uno solo, y una
máquina que ya tenía los perfiles recibe la lista al día (con CYF, desde el 16 de octubre de 2026):

```powershell
$Global = "$HOME\.claude\CLAUDE.md"
$Utf8   = New-Object System.Text.UTF8Encoding($false)
if (-not (Test-Path $Global)) { [IO.File]::WriteAllText($Global, "", $Utf8) }
$Actual = [IO.File]::ReadAllText($Global, $Utf8)
$Actual = [regex]::Replace($Actual, "(?s)<!-- perfiles-del-equipo: inicio -->.*?<!-- perfiles-del-equipo: fin -->\r?\n?", "")
$Bloque = [IO.File]::ReadAllText("$Origen\base\postura-gabinete.md", $Utf8)
[IO.File]::WriteAllText($Global, $Actual + $Bloque, $Utf8)
(Select-String -Path $Global -Pattern "perfiles-del-equipo").Count   # debe dar 2
```

### A10d. Verificar

| Prueba | Qué se espera |
|---|---|
| En una sesión nueva, escribir `¿qué opina Gestión de lo que tengo pendiente?` | El primer renglón dice «Responde Gestión (GES)» y la respuesta usa los términos de su ficha |
| Escribir `¿en qué debo estar hoy?` | Contesta Gabinete, con recomendación, sin anunciarse |
| Escribir `revísalo con Tavo` sobre cualquier decisión | Una sección por área y cierra con preguntas para el cliente |
| Abrir `$HOME\.claude\CLAUDE.md` en el Bloc de notas | Los acentos del bloque se ven bien |

Si un perfil se queda callado, la causa casi siempre es la carpeta: tiene que ser
`$HOME\.claude\skills\equipo-ges\SKILL.md`, con el `SKILL.md` adentro de su carpeta.

### A10e. Lo que hay que decirle

- Les habla por su nombre o su apodo: *«¿qué opina Gestión?»*, *«pásalo por Procesos»*,
  *«revísalo con Tecnología»*. Si no los llama, entran solos cuando el tema es suyo.
- **La ficha es suya**: si cambia de puesto, de jefe o de forma de trabajar, se le pide al
  asistente que la ponga al día.
- Todo lo que va a un tercero pasa antes por su visto bueno, y los correos quedan en Borradores.
