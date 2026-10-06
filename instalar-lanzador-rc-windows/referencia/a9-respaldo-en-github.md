# A9 · El respaldo de cada proyecto en GitHub

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A9. El respaldo de cada proyecto en GitHub
  - A9a. La cuenta de GitHub, que es del cliente
  - A9b. Instalar `gh` y darle la cuenta
  - A9c. Encenderlo
  - A9d. El primer respaldo de lo que ya existe
  - A9e. Verificar
  - A9f. Cómo se recupera todo en una máquina nueva
  - A9g. Lo que hay que decirle

<!-- fin del encabezado agregado al partir -->

## A9. El respaldo de cada proyecto en GitHub

> 🔴 **Esta sección es obligatoria, aunque el cliente diga que no la necesita.** En agosto de
> 2026 a un cliente le tronó el disco de la laptop y perdió su carpeta de proyectos entera:
> la memoria de meses de trabajo, sin una copia en otro lado. El programa vende justo esa
> memoria acumulada, así que una instalación sin respaldo entrega algo que una falla de disco
> borra en un segundo.

**Qué hace, una vez encendido:** al cerrar cada sesión, la bitácora confirma en git lo que
cambió en ese proyecto y lo sube a **un repositorio privado de GitHub del propio cliente, uno
por proyecto**, con el nombre de la carpeta. Un proyecto nuevo estrena su repositorio solo, en
su primer cierre. Corre en código, sin modelo, así que **cuesta cero uso de Claude**, y en la
prueba tardó de 2 a 6 segundos.

Las tres reglas que lo vuelven seguro de dejar corriendo solo:

| Situación | Qué hace |
|---|---|
| El repositorio remoto es **público** | Se salta el proyecto completo, sin confirmar ni subir. Un proyecto de cliente lleva contratos y montos |
| No puede comprobar que el remoto sea privado (sin red, sin `gh`) | Confirma en la máquina y **se queda sin subir** hasta comprobarlo |
| El proyecto vive dentro del repositorio de otra carpeta | Lo deja intacto |

**Cuando algo falla, el cliente se entera:** el resultado queda en
`~/.cache/claude-bitacora/cierres.log`, y la siguiente sesión que abra en ese proyecto le dice
en una línea que el respaldo está fallando y que, mientras tanto, su trabajo vive solo en esa
computadora. Con el siguiente respaldo bueno el aviso desaparece. **Se probó así el 5 de
octubre de 2026**, contra GitHub real: falla registrada, aviso al arrancar, arreglo, subida y
aviso borrado.

> ⚠️ **En Windows está sin medir todavía.** El código es el mismo y corre con la biblioteca
> estándar de Python, pero la prueba contra GitHub se hizo en Linux el 5 de octubre de 2026.
> Correr A9e y A9f completas en `win11-dogfood` antes de prometerlo en una laptop con Windows.

### A9a. La cuenta de GitHub, que es del cliente

**La cuenta es suya, a su nombre y con su correo**, igual que la tailnet de B1: el día que deje
de trabajar con nosotros, sus repositorios se van con él. GitHub da repositorios privados sin
límite en el plan gratuito. **Encender la verificación en dos pasos** al crearla, porque esa
cuenta guarda copia de todo su trabajo.

### A9b. Instalar `gh` y darle la cuenta

```powershell
winget install --id GitHub.cli -e --accept-source-agreements --accept-package-agreements
# cerrar y abrir PowerShell para que gh entre al PATH
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
git config --global user.name "<Nombre del cliente>"
git config --global user.email "<su correo>"
```

`gh auth login` imprime un código y abre el navegador: **ahí entra el cliente con su cuenta**,
y es otro de los puntos donde el asistente se detiene y espera a una persona.

> 🔴 **`gh auth setup-git` es el paso que se olvida, y si falta, el respaldo se queda en la máquina.** Deja a
> git usando la credencial de `gh` con su ruta completa. Medido el 5 de octubre de 2026: sin
> esa línea, el cierre confirmó en la máquina y falló al subir con *could not read Username*.
> Con ella, sube igual desde el cierre de sesión que desde el servicio del lanzador, que corre
> con un ambiente mínimo.

### A9c. Encenderlo

El respaldo viene apagado en `bitacora.py`, así que una máquina que ya lo tenía se queda igual
hasta que alguien lo prende. Se agrega `"respaldo": true` al `bitacora.json` de A3, sin tocar
lo demás:

```powershell
python -c "import json,pathlib; p=pathlib.Path.home()/'.claude'/'bitacora.json'; d=json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {}; d['respaldo']=True; p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8'); print(d)"
```

Requiere el `bitacora.py` del 5 de octubre de 2026 o más nuevo. Una copia vieja lo ignora en
silencio, así que se comprueba:

```powershell
Select-String -Path "$env:USERPROFILE\.claude\hooks\bitacora.py" -Pattern "def respaldar_proyecto" -Quiet   # True
```

Si da otra cosa, volver a bajar `bitacora.py` como en A3.

### A9d. El primer respaldo de lo que ya existe

Los proyectos que ya estaban en la carpeta se respaldan solos en su siguiente cierre. Para no
esperar, este bloque los respalda todos de una vez y enseña el resultado:

```powershell
Get-ChildItem "$env:USERPROFILE\claude" -Directory | Where-Object { Test-Path (Join-Path $_.FullName "CLAUDE.md") } | ForEach-Object {
  Write-Host "Respaldando $($_.Name)"
  python "$env:USERPROFILE\.claude\hooks\bitacora.py" respaldar $_.FullName
}
Get-Content "$env:USERPROFILE\.cache\claude-bitacora\cierres.log" -Tail 20 | Select-String "respaldo"
```

Cada proyecto debe decir `respaldo listo  subido`. Uno que diga `fallo` trae el motivo en el
mismo renglón.

### A9e. Verificar

```powershell
gh repo list --visibility private --limit 100
```

Debe listar un repositorio por cada proyecto, **todos privados**. Y la prueba que cuenta: en un
proyecto de prueba, crear un archivo, abrir y cerrar una sesión de Claude Code, esperar unos
segundos y ver el archivo en `github.com/<usuario>/<proyecto>`.

### A9f. Cómo se recupera todo en una máquina nueva

Es la razón de esta sección, y conviene ensayarla una vez con el cliente presente. En la máquina
nueva, con A1 a A9b hechas y la misma cuenta de GitHub:

```powershell
gh repo list <usuario-de-github> --visibility private --limit 500 --json name -q ".[].name" | ForEach-Object {
  if (-not (Test-Path "$env:USERPROFILE\claude\$_")) { gh repo clone "<usuario-de-github>/$_" "$env:USERPROFILE\claude\$_" }
}
```

### A9g. Lo que hay que decirle

- **GitHub guarda una copia de sus archivos.** Es un servicio de Microsoft, en Estados Unidos, y
  los repositorios privados solo los ve su cuenta. Es la misma clase de revelación que el audio
  en A8c, y se dice antes de encenderlo.
- **`bandeja/` y `salida/` quedan fuera del respaldo**, por el gitignore de A6. Lo que suba desde
  el teléfono vive solo en la máquina **hasta que lo mueva a una carpeta del proyecto**. Conviene
  decírselo con esas palabras, porque la bandeja es justo por donde llegan los contratos.
- **Un archivo de más de 100 MB detiene la subida de ese proyecto**, porque GitHub los rechaza.
  El aviso al arrancar lo dice; la salida es sacar ese archivo del proyecto o agregarlo al
  `.gitignore` del proyecto.
- **El historial completo queda guardado**, con un "Respaldo automático" por cierre. Si un día
  borra algo por error, se recupera de ahí.
