# B4, B5 y B6 · Publicarlo en la tailnet, la bandeja y el comando rc

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B4. Publicarlo en la tailnet
- B5. Decirle a las sesiones qué es la bandeja
- B6. El comando `rc`, para lanzar desde la terminal (opcional)

<!-- fin del encabezado agregado al partir -->

## B4. Publicarlo en la tailnet


```powershell
& "C:\Program Files\Tailscale\tailscale.exe" serve --bg http://127.0.0.1:8765
& "C:\Program Files\Tailscale\tailscale.exe" serve status
```

Queda en `https://<nombre-del-equipo>.<tailnet>.ts.net/`, **alcanzable solo desde la
tailnet**. Esa es la URL que se le da al usuario.

## B5. Decirle a las sesiones qué es la bandeja


**Paso corto y fácil de olvidar, y sin él la mitad del valor del lanzador no se usa.** El
lanzador deja lo que se sube desde el teléfono en `bandeja/`, dentro del proyecto. Pero
**nada le dice a la sesión que esa convención existe**: al pedirle "mira lo que subí a la
bandeja" contesta preguntando si te refieres al correo.

**Aditivo e idempotente, igual que A6 y A7** (que ya pudo haber escrito en este mismo
archivo, porque la fase A corre antes que esta): se anexa a
`%USERPROFILE%\.claude\CLAUDE.md`, nunca lo reemplaza.

```powershell
$claudeMd = "$env:USERPROFILE\.claude\CLAUDE.md"
New-Item -ItemType Directory -Force -Path (Split-Path $claudeMd) | Out-Null
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd | Out-Null }

if (-not (Select-String -Path $claudeMd -Pattern '^## La bandeja' -Quiet)) {
@'

## La bandeja: archivos que subo desde el teléfono


Cada proyecto puede tener una carpeta `bandeja/` en su raíz. Ahí es donde el lanzador rc deja
lo que subo desde el celular: fotos, audios de junta, PDFs, capturas.

**Si menciono "la bandeja", me refiero a esa carpeta del proyecto en el que estás, no a un
correo ni a nada de Gmail.** Revisar `bandeja/` del proyecto actual y trabajar con lo que
haya ahí.

Está en el gitignore, así que no aparece en `git status`. Al terminar de usar un archivo, yo
decido qué hacer con él desde el menú del lanzador, **no moverlo ni borrarlo por iniciativa
propia**, salvo que lo pida.
'@ | Add-Content -Path $claudeMd -Encoding utf8
}
```

> ⚠️ **Guardarlo en UTF-8, no en el default del Bloc de notas.** Claude Code lo lee como
> UTF-8; en cp1252 los acentos llegan rotos. El `-Encoding utf8` de arriba ya lo hace bien.

> ⚠️ **Correrlo dos veces no duplica la sección**, ni pisa la convención de pendientes que
> A7 ya sembró ahí. Es el mismo guardado con `Select-String` que usan A6 y A7.

Verificación: subir un archivo desde el teléfono, abrir la sesión de ese proyecto y pedirle
que vea la bandeja. Debe encontrarlo sin que le digas la ruta. Rápido y sin teléfono:
`Select-String -Path "$env:USERPROFILE\.claude\CLAUDE.md" -Pattern "La bandeja" -Quiet`.

## B6. El comando `rc`, para lanzar desde la terminal (opcional)

**El camino principal es el teléfono**, y esta sección se puede saltar entera sin perder
nada de lo demás. Sirve para quien ya está frente a una terminal y prefiere teclear en vez
de sacar el celular.

**Lo que importa, y es lo que lo hace seguro: la sesión que nace aquí es la misma que nace
desde el teléfono.** El comando llama al mismo código, así que aparece en el mosaico y se
puede cerrar con el dedo. Dos formas distintas de crear una sesión se separan sin que nadie
lo note, y ahí es donde una sesión se vuelve invisible e inmatable.

Windows necesita además **desde dónde** llamarlo: de fábrica no trae servidor SSH
encendido, así que esto es para quien se sienta frente a la máquina, o para quien encienda
OpenSSH a propósito. Es la razón principal por la que esta sección es opcional.

Crear `%USERPROFILE%\bin\rc.cmd` (y asegurarse de que esa carpeta esté en el `PATH`):

```powershell
$bin = "$env:USERPROFILE\bin"
New-Item -ItemType Directory -Force -Path $bin | Out-Null
@"
@echo off
python "RUTA_DEL_LANZADOR\procesos_windows.py" %*
"@ | Set-Content -Path "$bin\rc.cmd" -Encoding ascii
```

Sustituir `RUTA_DEL_LANZADOR` por la carpeta real. Uso:

```
rc                      :: lista las carpetas disponibles
rc mi-proyecto          :: crea la sesión y devuelve la terminal
rc mi-proyecto --resume <session-id>
```

> ⚠️ **En Windows la sesión SIEMPRE nace desprendida**, o sea que el comando la crea y te
> devuelve el símbolo del sistema; no te deja trabajando dentro como en Linux. Quedarse
> adentro exige que la consola hospede la terminal falsa, y eso está sin construir. `-d` se
> acepta igual, para que el mismo tecleo funcione en las dos plataformas.

> 🔴 **Y un gotcha que costó medir: la sesión tiene que desprenderse del Job de Windows, o
> muere con la consola que la lanzó.** Ya viene resuelto en el código
> (`CREATE_BREAKAWAY_FROM_JOB`); se menciona porque el síntoma es desconcertante — la ficha
> de la sesión queda escrita y el proceso ya no existe.

Verificación: `rc` sin argumentos lista los proyectos; `rc <alguno>` crea la sesión, el
mosaico la muestra en **Activos**, y **sigue viva después de cerrar esa consola**.
