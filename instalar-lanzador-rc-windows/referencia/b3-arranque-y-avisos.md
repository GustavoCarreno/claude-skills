# B3 y B3b · Arranque automático, el vigilante y su canal de avisos

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B3. Arranque automático
- B3b. El vigilante y su canal de avisos
  - El canal: dos caminos, y el segundo es el normal
  - El vigilante, como tarea programada cada minuto
  - Comprobarlo, que son dos renglones
  - Del lado del teléfono

<!-- fin del encabezado agregado al partir -->

## B3. Arranque automático


Un `.cmd` envoltorio y una tarea programada que arranca **con la máquina**, sin esperar a que
nadie entre:

```powershell
@"
@echo off
cd /d "%USERPROFILE%\rc-launcher"
"$((Get-Command python.exe).Source)" app.py
"@ | Out-File "$env:USERPROFILE\lanzador.cmd" -Encoding ascii

$accion = New-ScheduledTaskAction -Execute "$env:USERPROFILE\lanzador.cmd"
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
Register-ScheduledTask -TaskName "rc-launcher" -Action $accion -Principal $principal -Force `
  -Trigger @((New-ScheduledTaskTrigger -AtStartup), (New-ScheduledTaskTrigger -AtLogOn))
Start-ScheduledTask -TaskName "rc-launcher"
```

> 🔴 **`LogonType S4U` es lo que hace la promesa honesta, y esta guía enseñaba otra cosa hasta
> el 10 sep 2026.** Decía `schtasks /SC ONLOGON`, que **exige que alguien tenga sesión
> iniciada**: con la laptop encendida y la pantalla bloqueada, el lanzador sencillamente no
> está. S4U corre sin sesión y sin contraseña guardada, así que la laptop encendida basta.
>
> **Con qué se compara:** `/SC ONSTART` con cuenta de usuario se crea y **nunca corre** (queda
> en `267011`, "no ha ejecutado", sin avisar), y por eso la guía había caído en `ONLOGON`. El
> modo que resuelve las dos cosas es S4U, medido el 5 ago 2026 con un reinicio de verdad: la
> máquina arrancó con la sesión cerrada y a los 21 segundos el lanzador ya contestaba por la tailnet.
>
> ⚠️ **Lo que S4U cuesta, y hay que saberlo:** la tarea corre sin credenciales de red, así que
> pierde el acceso a unidades de red compartidas. Lo que el lanzador necesita (disco local y
> salida a internet) funciona igual.

> 📌 **Los dos disparadores son a propósito:** el de arranque cubre la máquina que se prende
> sola tras un corte de luz, y el de inicio de sesión cubre a quien entra después de haberla
> apagado a mano.

> 📌 **Al re-registrar sobre una máquina que ya lo tenía, `Start-ScheduledTask` deja
> `LastTaskResult: 2147946720`**, que es "la petición fue rechazada" y aquí significa nada más
> que **el lanzador anterior seguía corriendo**, con el puerto tomado. Medido el 10 sep 2026, con
> la app contestando `200` todo el tiempo. Para cargar el código nuevo de verdad hay que matar al
> dueño del puerto, y eso está en B2b.

> ⚠️ **`schtasks /run` NO reinicia una tarea que ya corre.** Contesta "is currently running"
> y no hace nada. La secuencia correcta es `schtasks /end` y luego `schtasks /run`.
>
> 🔴 **Y esa secuencia NO basta para recargar el código, cosa que importa cada vez que se
> actualice el lanzador.** `schtasks /end` termina el `.cmd` de la tarea pero **deja vivo al
> `python` que ese `.cmd` lanzó**, así que el proceso viejo conserva el puerto 8765 y el
> `/run` arranca un segundo que no puede escuchar. Las dos órdenes contestan `SUCCESS` y el
> lanzador sigue respondiendo, o sea que **el síntoma es que el código nuevo simplemente no
> está**: una ruta recién agregada devuelve el 404 genérico de Flask, como si no existiera.
> Medido en la VM de dogfooding el 6 ago 2026, con dos `python.exe` vivos a la vez.
>
> Hay que matar al que tiene el puerto, **por PID y no por nombre**, para no llevarse por
> delante otros Python de la máquina del cliente:
>
> ```powershell
> $pid_lanzador = (Get-NetTCPConnection -LocalPort 8765 -State Listen).OwningProcess
> Stop-Process -Id $pid_lanzador -Force
> schtasks /run /tn rc-launcher
> ```
>
> Y comprobar que quedó **uno solo**: `tasklist /fi "imagename eq python.exe"`. En Windows
> viejo sin `Get-NetTCPConnection`, el PID sale de `netstat -ano | findstr :8765`.

## B3b. El vigilante y su canal de avisos

**Esto faltaba entero hasta el 10 sep 2026:** en Windows el vigilante ni siquiera se
instalaba, así que el aviso de "la tarea terminó" era cosa de Linux nada más. Son dos
piezas, y hacen falta las dos.

El vigilante mira cada minuto si alguna sesión cerró su turno, o sea si **Claude Code se
quedó esperando a la persona**, y manda un aviso al teléfono con la liga para abrir esa
misma sesión. Cubre justo el hueco de la aplicación de Claude, que avisa cuando hay algo
que contestar y se calla cuando el trabajo simplemente terminó.

### El canal: dos caminos, y el segundo es el normal

El canal es **ntfy**: una aplicación de teléfono que recibe avisos y un servidor que los
publica. Sin cuenta de correo, sin token de por medio, y con una versión gratuita.

| Camino | Cuándo | Qué se pone en `url` |
|---|---|---|
| **Servidor propio** | La organización ya tiene uno, o el material es delicado | Su dirección, más `usuario` y `clave` |
| **`ntfy.sh`, el público** | Lo demás. Cero infraestructura, cero costo, cero cuenta | `https://ntfy.sh`, con `usuario` y `clave` vacíos |

> 🔴 **Con `ntfy.sh` el tema TIENE que ser un nombre largo y difícil de adivinar**, porque
> ahí un tema es público: quien lo escriba lo lee. El aviso lleva el **nombre del proyecto
> y el título de lo que se hizo**, así que con un tema como `avisos` cualquiera vería de
> qué trabaja el cliente. El comando de abajo lo genera al azar.
>
> ⚠️ **Y hay que decirlo en voz alta antes de elegir**, con la misma franqueza de A5c: en
> el servidor público esos títulos viajan por una máquina ajena. Si el cliente maneja
> material confidencial, o es servidor propio, o el aviso se deja genérico.

```powershell
$carpeta = "$env:USERPROFILE\.config\rc-launcher"
New-Item -ItemType Directory -Force -Path $carpeta | Out-Null
$tema = "rc-" + -join ((1..16) | ForEach-Object { "abcdefghijkmnpqrstuvwxyz23456789"[(Get-Random -Max 32)] })
@"
{
  "url": "https://ntfy.sh",
  "tema": "$tema",
  "usuario": "",
  "clave": "",
  "prioridad": "default",
  "titulo_suelto": "Claude Code"
}
"@ | Out-File "$carpeta\ntfy.json" -Encoding ascii
"El tema es: $tema"
```

> ⚠️ **`-Encoding ascii` a propósito, y conviene saber por qué:** el `utf8` de PowerShell 5.1
> escribe **marca de orden de bytes**, y con ella al frente el archivo deja de ser JSON
> válido para muchos lectores. El lanzador ya la tolera desde el 10 sep 2026, pero la guía
> escribe limpio de todos modos: el contenido es ASCII puro, así que cuesta cero.

**El tema hay que copiarlo**, porque es lo que la persona escribe en su teléfono.

### El vigilante, como tarea programada cada minuto

```powershell
$pythonw = (Get-Command python.exe).Source -replace 'python\.exe$','pythonw.exe'
$carpeta = "$env:USERPROFILE\rc-launcher"

$accion = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$carpeta\watcher.py`"" -WorkingDirectory $carpeta
$ahora = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
$arranque = New-ScheduledTaskTrigger -AtStartup
$arranque.Repetition = $ahora.Repetition
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "rc-watcher" -Action $accion -Trigger @($ahora, $arranque) `
  -Principal $principal -Settings $ajustes -Force
```

> 🔴 **`schtasks /SC MINUTE` aquí NO sirve, y falla del modo más caro: se crea, dice
> `SUCCESS`, y jamás corre.** Medido en la VM de dogfooding el 10 sep 2026: la tarea queda con
> `Last Result: 267011` y última corrida en `30/11/1999`, o sea nunca, porque nace con
> `LogonType: Interactive` y **esa máquina tiene la sesión cerrada**. Ni `/RU` con `/NP`
> lo arregla: sigue saliendo `Interactive`.
>
> **Lo que sí funciona es S4U**, que es justo el modo en que ya está el lanzador desde B3, y por
> eso el bloque va con `Register-ScheduledTask` en vez de `schtasks`. Verificado en la misma
> sesión: `LogonType: S4U`, `UltimoResultado: 0`, con la máquina encendida y la sesión cerrada.
>
> 📌 **Es la misma familia del aviso de B3 sobre `ONSTART`**, y conviene leerlo así: en Windows,
> una tarea que debe correr con la laptop encendida y sin sesión abierta **siempre** termina
> necesitando S4U.

> 🔴 **`pythonw.exe` y jamás `python.exe`, y esto decide si el cliente lo tolera o lo
> apaga.** Con `python.exe` una tarea que corre **cada minuto** abre una ventana negra de
> consola cada minuto, encima de lo que la persona esté haciendo. `pythonw.exe` es el mismo
> intérprete sin consola. Viene junto al otro, en la misma carpeta.

> 🔴 **El disparador `-Once -At (Get-Date)` es el que hace que empiece HOY, y sin él la tarea
> queda muda hasta el próximo reinicio.** Medido en la VM el 10 sep 2026: con `-AtStartup` como
> único disparador, la repetición se registra pero **jamás arranca**, porque una repetición
> empieza a contar cuando su disparador dispara, y la máquina ya estaba encendida. El síntoma
> exacto es `NextRunTime` **vacío** con la tarea en `Ready`, que se lee como si estuviera bien.
> Con el disparador de ahora, `NextRunTime` sale con hora concreta, a un minuto.
>
> **El de arranque se queda igual**, para el día que la máquina se apague: cubre el reinicio, y
> el otro cubre hoy.

> ⚠️ **`-AllowStartIfOnBatteries` y `-DontStopIfGoingOnBatteries` importan justo en el cliente
> que esto busca**, que trabaja en una laptop: de fábrica, Windows **se salta las tareas
> programadas cuando el equipo anda con batería**, así que el aviso desaparecería precisamente
> cuando la persona está fuera del escritorio.

> ⚠️ **El lanzador y el vigilante son tareas distintas**, y conviene tenerlo claro: el lanzador
> es un servidor que vive todo el día, y el vigilante es un vistazo que corre y termina.
> Meterlos en la misma tarea deja al vigilante sin correr.

### Comprobarlo, que son dos renglones

```powershell
cd "$env:USERPROFILE\rc-launcher"
python -c "import avisos; print(avisos.enviar('Prueba de instalación\nSi ves esto en el teléfono, el canal quedó.'))"
(Get-ScheduledTaskInfo -TaskName "rc-watcher") | Select-Object LastRunTime, LastTaskResult, NextRunTime
```

Lo primero sale `(True, 'avisado')` **y el aviso llega al teléfono**. Las dos cosas: el
`True` dice que el servidor lo aceptó, y solo el teléfono dice que la suscripción está
bien escrita. Lo segundo tiene que reportar tres cosas: `LastTaskResult` en **`0`**, una `LastRunTime` de hace
menos de un minuto, y **`NextRunTime` con hora**. **Un `267011` con fecha de 1999 significa que
la tarea jamás corrió**, y **una `NextRunTime` vacía significa que ya sólo correría tras un
reinicio**;
los dos recuadros rojos de arriba dicen por qué.

> 📌 **Si sale `(False, ...)`, el mensaje dice cuál de las tres cosas falló**: falta el
> archivo, el servidor contestó un código (un 401 es usuario o clave), o la red. Un
> `403` en `ntfy.sh` suele ser un tema con mayúsculas o con caracteres raros.

### Del lado del teléfono

Instalar **ntfy** (Play Store, App Store o F-Droid), tocar **Agregar suscripción** y
escribir el tema. Con servidor propio, marcar **Usar otro servidor** y poner la dirección
con su usuario y contraseña.
