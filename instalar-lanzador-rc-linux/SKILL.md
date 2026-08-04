---
name: instalar-lanzador-rc-linux
description: Activar cuando alguien pida instalar, montar o configurar el lanzador rc (rc-launcher) en una máquina Linux, o dejar lista una computadora para lanzar sesiones de Claude Code desde el teléfono. También cuando pida el lanzador web, la bitácora automática que actualiza CLAUDE.md sola, o publicar el lanzador en su tailnet de Tailscale. Cubre Ubuntu y Debian con systemd.
---

# Instalar el lanzador rc y la bitácora automática en Linux

Deja una máquina Linux lista para lanzar, retomar y cerrar sesiones de Claude Code
desde el teléfono, y para que el `CLAUDE.md` de cada proyecto se escriba solo al
cerrar cada sesión.

**Procedimiento verificado de punta a punta en una VM limpia** (Ubuntu Server 24.04.4,
cloud image, sin nada preinstalado). Cada comando de aquí se corrió de verdad, en ese
orden. Para Windows existe el equivalente en `instalar-lanzador-rc-windows`.

## Qué queda funcionando

| Capacidad | Cómo se ve para quien lo usa |
|---|---|
| Lanzar sesiones desde el teléfono | Toca un botón y la sesión aparece en su app de Claude |
| Cerrarlas desde el teléfono | Toca cerrar y desaparece de la app |
| Retomar una conversación anterior | El menú del proyecto lista sus sesiones previas |
| Crear un proyecto nuevo | Botón "+ Nuevo proyecto", con nombre y contexto |
| Subir archivos desde el teléfono | Caen en `bandeja/` dentro del proyecto |
| **La bitácora se escribe sola** | Al cerrar, el `CLAUDE.md` del proyecto queda actualizado sin pedirlo |

## El reparto, y conviene decirlo antes de empezar

**La máquina la hace el asistente; la cuenta, la consola de Tailscale y el teléfono
los hace una persona.** No es una limitación técnica que se pueda rodear: crear la
tailnet, aprobar el dispositivo y autenticar la app del teléfono exigen a alguien
frente a un navegador. Planear la sesión de instalación con esa persona presente.

## 0. Descarte previo, cinco minutos antes de instalar nada

| Revisar | Cómo | Si falla |
|---|---|---|
| Distro con systemd | `systemctl --version` | Sin systemd no hay arranque automático; esta guía no lo cubre |
| Ubuntu 22.04+ o Debian 12+ | `lsb_release -ds` | En distros más viejas Python puede ser menor a 3.10 y hay que compilar |
| Python 3.10 o más | `python3 --version` | Ver arriba |
| `sudo` disponible | `sudo -v` | Sin sudo no se instalan paquetes ni unidades de systemd. **Aquí se para la instalación** |
| Cuenta de Anthropic con plan que incluya Claude Code | entrar a `claude.ai` | Sin plan no hay nada que instalar. Contratarlo antes de la cita |
| La máquina va a quedar encendida | preguntar | Si se apaga, el teléfono no encuentra nada. Es una condición del montaje, no un defecto |

## 1. Prerrequisitos

```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip tmux git curl
curl -fsSL https://claude.ai/install.sh | bash
```

| Pieza | Verificar | Si la verificación falla |
|---|---|---|
| Python con venv | `python3 -m venv --help` | En Debian el módulo va aparte: es el paquete `python3-venv` |
| tmux | `tmux -V` | Es la capa de sesión del lanzador en Linux; sin él no lanza nada |
| Claude Code | `claude --version` | Ver la advertencia del PATH abajo |

> ⚠️ **En Linux NO hace falta Node.js.** El instalador nativo de `claude.ai/install.sh`
> trae su propio runtime y deja el binario en `~/.local/bin/claude`. Es la diferencia
> más grande contra el procedimiento de Windows, donde sí hay que instalar Node.

> ⚠️ **El instalador avisa que `~/.local/bin` no está en el PATH, y hay que hacerle caso:**
> `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`. Abrir una terminal nueva
> después. Esto además reaparece en el paso 4, porque **systemd tampoco hereda ese PATH**.

**Autenticar Claude Code una vez a mano**, corriendo `claude` en una terminal normal y
aceptando sus diálogos de primer arranque. Si no, la primera sesión lanzada desde el
teléfono se queda esperando esos diálogos **sin que nadie lo vea**, porque no hay ventana.

> ⚠️ **En una máquina sin pantalla (un servidor, una VM, una mini PC en un rack) eso no
> alcanza**, porque el flujo abre un navegador y luego **pide de vuelta un código pegado**.
> La receta que sí funciona es dejar el proceso esperando dentro de tmux, para poder
> teclearle el código después:
>
> ```bash
> tmux new-session -d -s login -x 500 -y 40 "claude auth login --claudeai"
> sleep 10
> tmux capture-pane -t login -p | grep -o 'https://claude.com/cai/oauth/authorize[^ ]*'
> # la persona abre esa URL, copia el codigo, y se lo tecleas al proceso:
> tmux send-keys -t login '<codigo>' Enter
> claude auth status        # debe reportar la cuenta
> ```
>
> **El `-x 500` no es capricho:** con el ancho normal `capture-pane` parte la URL en varias
> líneas y el `grep` devuelve un pedazo inservible. Y **la URL va amarrada a ese intento**
> (trae su `code_challenge` y su `state`), así que no sirve regenerarla por otro lado ni
> reusar una vieja.

> ⚠️ **No matar procesos con `pkill -f "claude auth login"`:** el patrón aparece en la propia
> línea de comando que lo ejecuta, así que **se mata a sí mismo** (y con él la sesión SSH,
> que devuelve 255 sin explicar nada). Matar por PID con `pgrep` primero.

## 2. La tailnet

**Sin la red, todo lo demás se instala bien y no sirve para nada**, porque el teléfono
no encuentra la máquina.

**Si es un cliente, crea su propia tailnet, no se une a la nuestra.** Meter la máquina
de un cliente en nuestra red la pone junto a los ambientes de producción de otros. Su
red es suya, y así se la lleva el día que deje de trabajar con nosotros.

```bash
curl -fsSL https://tailscale.com/install.sh | sudo sh
sudo tailscale up --hostname=<nombre-corto-de-la-maquina>
```

`tailscale up` **se queda esperando** e imprime una URL de `login.tailscale.com`. Alguien
tiene que abrirla en un navegador donde esa cuenta esté iniciada. Ese es el primer punto
donde el asistente no puede seguir solo.

> 💡 **Para no dejar la terminal colgada:** lanzarlo de fondo y leer la URL del archivo.
> `sudo nohup tailscale up --hostname=<nombre> > /tmp/tsup.log 2>&1 &` y luego
> `cat /tmp/tsup.log`.

**El teléfono es la otra mitad del montaje.** Dos apps, las dos de la tienda:

1. **Tailscale**, con **la misma cuenta** de la tailnet. Al terminar, `tailscale status`
   en la máquina debe listar también el teléfono.
2. **Claude**, la app oficial de Anthropic, con la misma cuenta que se autenticó arriba.
   **Es con la que se abre la sesión**: el lanzador solo la enciende, la conversación
   ocurre en esa app.

> ⚠️ **Son dos canales distintos, y entenderlo ahorra diagnósticos.** La tailnet solo
> sirve para alcanzar **la página del lanzador**. La sesión de Claude no viaja por la
> tailnet: el teléfono se conecta a ella por la infraestructura de Anthropic. O sea que
> "no abre la página" y "no aparece la sesión" son fallas distintas.

**Los tres interruptores de la consola de administración** viven en `login.tailscale.com`,
no en la máquina, y sin ellos la instalación termina sin errores y no funciona:

| Interruptor | Dónde | Comprobar |
|---|---|---|
| **MagicDNS** | consola → DNS | `tailscale dns status` debe decir `MagicDNS: enabled tailnet-wide` |
| **Certificados HTTPS** | consola → DNS | El paso 5 falla con un mensaje explícito si están apagados |
| **Aprobación para publicar** | la imprime el propio comando | Si el paso 5 imprime una URL de aprobación, abrirla y aceptar |

## 3. El lanzador

```bash
# el código va al home, no a una ruta de sistema
rsync -a --exclude .venv --exclude __pycache__ --exclude .git \
      <origen>/rc-launcher/ ~/rc-launcher/

cd ~/rc-launcher
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

mkdir -p ~/claude          # la raíz de proyectos, que es donde vive el trabajo
```

`~/claude` no es negociable sin tocar código: `sessions.py` la calcula como
`Path.home() / "claude"`. Si los proyectos viven en otro disco, poner un symlink ahí.

**Comprobar antes de seguir**, porque si esto falla, nada de lo demás importa:

```bash
cd ~/rc-launcher && .venv/bin/python -m pytest -q
```

Debe pasar la suite completa. En la VM limpia pasaron 327 de 327 en medio segundo, sin
tocar una línea, que es la prueba de que el código no depende de la máquina donde nació.

## 4. Arranque automático

Dos unidades de systemd **a nivel de sistema** con `User=`, no unidades de usuario.
Sustituir `<usuario>` en las cuatro apariciones:

```ini
# /etc/systemd/system/rc-launcher.service
[Unit]
Description=rc session launcher
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=simple
User=<usuario>
Environment=PATH=/home/<usuario>/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WorkingDirectory=/home/<usuario>/rc-launcher
ExecStart=/home/<usuario>/rc-launcher/.venv/bin/python /home/<usuario>/rc-launcher/app.py
Restart=on-failure
RestartSec=5
KillMode=process

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/rc-watcher.service        (Type=oneshot, mismo User/PATH/WorkingDirectory)
ExecStart=/home/<usuario>/rc-launcher/.venv/bin/python /home/<usuario>/rc-launcher/watcher.py

# /etc/systemd/system/rc-watcher.timer
[Timer]
OnBootSec=2min
OnUnitActiveSec=1min
AccuracySec=15s
Persistent=true
[Install]
WantedBy=timers.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rc-launcher.service rc-watcher.timer
```

> ⚠️ **`KillMode=process` es obligatorio, no una preferencia.** Sin él systemd usa
> `control-group` y manda SIGTERM a **todo** el cgroup en cada `systemctl restart`. Como
> el servidor de tmux es único por usuario, si el servicio lo arrancó primero, **cada
> sesión rc de la máquina muere al reiniciar el servicio**, incluidas las abiertas a mano.

> ⚠️ **`Environment=PATH=` con `~/.local/bin` adelante es obligatorio.** Una unidad sin
> él no hereda el PATH interactivo y no encuentra `claude`. Falla **en silencio** si el
> comando que lo invoca usa `;` en vez de `&&`.

> ⚠️ **`systemctl status rc-launcher` NO mide la app.** Reporta el cgroup entero, con
> todas las sesiones adentro. Para medirla:
> `ps -o rss -p $(systemctl show -p MainPID --value rc-launcher.service)`.

## 5. Publicarlo en la tailnet

```bash
sudo tailscale serve --bg http://127.0.0.1:8765
tailscale serve status
```

Queda en `https://<nombre>.<tailnet>.ts.net/`, **alcanzable solo desde la tailnet**. Esa
es la URL que se le da a la persona.

## 6. La bitácora automática

Es lo que hace que el `CLAUDE.md` de cada proyecto se mantenga solo. Un único archivo de
Python, biblioteca estándar, **el mismo que corre en Windows**.

```bash
mkdir -p ~/.claude/hooks
cp <origen>/bitacora/bitacora.py ~/.claude/hooks/bitacora.py
chmod +x ~/.claude/hooks/bitacora.py
```

`~/.claude/bitacora.json`:

```json
{ "raiz_proyectos": "/home/<usuario>/claude", "umbral": 6, "max_recordatorios": 2 }
```

- **`raiz_proyectos`**: si apunta mal, el mecanismo **no dispara y no avisa**. Su modo de
  fallar es el silencio.
- **`umbral`**: herramientas de trabajo antes de considerar que hay algo que registrar.
- **`instruccion`** (opcional): el texto que se le pide al asistente. **Para un cliente
  conviene reescribirlo en su vocabulario**; el de fábrica habla de "Session Log" y
  "pipeline", que no son palabras suyas.

Los cuatro hooks, en `~/.claude/settings.json`, dentro de `"hooks"`:

```json
{
  "hooks": {
    "PostToolUse": [{ "matcher": "Write|Edit|NotebookEdit|Bash",
      "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py marcar" }] }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py verificar" }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py cerrar" }] }],
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "python3 /home/<usuario>/.claude/hooks/bitacora.py pendiente" }] }]
  }
}
```

> ⚠️ **Si `~/.claude/settings.json` ya existe, hay que fusionar, no sobrescribir.** En una
> máquina recién instalada no existe todavía, pero en una que ya usaba Claude Code sí, y
> pisarlo se lleva su configuración por delante.

## 6b. Decirle a las sesiones qué es la bandeja

**Paso corto y fácil de olvidar, y sin él la mitad del valor del lanzador no se usa.** El
lanzador deja lo que se sube desde el teléfono en `bandeja/`, dentro del proyecto. Pero
**nada le dice a la sesión que esa convención existe**: al pedirle "mira lo que subí a la
bandeja" contesta preguntando si te refieres al correo, porque para ella no significa nada.

Se cierra con `~/.claude/CLAUDE.md`, que aplica a todos los proyectos de esa máquina:

```markdown
## La bandeja: archivos que subo desde el teléfono

Cada proyecto puede tener una carpeta `bandeja/` en su raíz. Ahí es donde el lanzador rc
deja lo que subo desde el celular: fotos, audios de junta, PDFs, capturas.

**Si menciono "la bandeja", me refiero a esa carpeta del proyecto en el que estás, no a un
correo ni a nada de Gmail.** Revisar `bandeja/` del proyecto actual y trabajar con lo que
haya ahí.

Está en el gitignore, así que no aparece en `git status`. Al terminar de usar un archivo,
yo decido qué hacer con él desde el menú del lanzador, **no moverlo ni borrarlo por
iniciativa propia**, salvo que lo pida.
```

Verificación: subir un archivo desde el teléfono, abrir la sesión de ese proyecto y pedirle
que vea la bandeja. Debe encontrarlo sin que le digas la ruta.

## 7. Verificación, en orden

Cada paso falla distinto, así que conviene hacerlos en orden y no saltarse ninguno.

| # | Qué | Cómo | Esperado |
|---|---|---|---|
| 1 | El servicio vive | `systemctl is-active rc-launcher rc-watcher.timer` | `active` las dos |
| 2 | La app responde | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/salud` | `200` |
| 3 | La puerta cierra | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8765/` | **`403`** |
| 4 | Se ve desde el teléfono | abrir la URL de la tailnet | aparecen los proyectos |
| 5 | Lanza | tocar un proyecto → "Nueva sesión" | en 5 s el botón queda encendido y la sesión aparece en la app de Claude |
| 6 | Cierra | tocar el proyecto → "Terminar sesión" | desaparece de la app |
| 7 | Retoma | tocar un proyecto apagado | lista sus sesiones previas |
| 8 | La bitácora | trabajar en una sesión (6+ archivos escritos), cerrarla desde el lanzador | el `CLAUDE.md` de ese proyecto trae una entrada nueva |

> ⚠️ **El 403 del renglón 3 es la respuesta correcta, no una falla.** La raíz exige la
> identidad que inyecta Tailscale (`Tailscale-User-Login`), que por `curl` desde la propia
> máquina no existe. **Usar `/salud` para medir salud, nunca la raíz.**

**Si el teléfono dice que no carga:** revisar **primero el Tailscale del teléfono**, que es
la causa más probable y la más barata de descartar. Después, de más barato a más caro:
`tailscale status` debe listar el teléfono, `tailscale dns status` debe traer MagicDNS
encendido, y `tailscale serve status` debe mostrar la publicación del paso 5.

**Dónde mirar cuando la bitácora no cuadra:** todo vive en `~/.cache/claude-bitacora/`.
`cierres.log` es el canal de estado, con una línea por evento, y distingue "no había nada
que hacer" de "lo intenté y falló". `escritor-<sid>.log` es la transcripción completa de
la sesión que escribió esa bitácora.

> ⚠️ **`rc=0` no significa que se haya escrito.** Verificar siempre el archivo, no el
> código de salida.

## 8. Lo que NO resuelve esta instalación

Decirlo antes de instalarla en casa de alguien más:

- **Quien alcance el lanzador puede lanzar sesiones con acceso completo al disco de esa
  persona.** Es el permiso más fuerte de todo el montaje. La puerta es la identidad de
  Tailscale, y `~/.config/rc-launcher/acceso.json` extiende la lista de quién entra.
- **Si la máquina se apaga, no hay lanzador.** Es una condición del montaje.
- **La bitácora la escribe un modelo**, así que consume tokens de la cuenta de esa persona
  cada vez que cierra una sesión con trabajo pendiente.
- **Depende de cosas que no controlamos.** Si la empresa bloquea Tailscale, no hay rodeo
  técnico. El paso 0 existe para descubrirlo antes de la cita, no durante.
- **La tailnet queda a nombre suyo**, o sea que él administra sus interruptores. Es
  deliberado, pero significa que un cambio suyo puede tumbar el acceso sin que nos
  enteremos.
- **Un proyecto cuya carpeta se renombre con la sesión viva** desaparece del grid y esa
  sesión queda inmatable desde el teléfono. Se cierra con `tmux kill-session` a mano.

## Errores comunes

| Síntoma | Causa real |
|---|---|
| `claude: command not found` desde el servicio | Falta `Environment=PATH=` con `~/.local/bin` en la unidad |
| Reiniciar el servicio mata todas las sesiones | Falta `KillMode=process` |
| La raíz da 403 y parece roto | Es correcto sin identidad de Tailscale; medir con `/salud` |
| El teléfono no abre la página | Tailscale del teléfono apagado, o MagicDNS apagado en la consola |
| La primera sesión se queda colgada | Claude Code nunca se autenticó a mano; no hay ventana donde aceptar sus diálogos |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| "Le pedí la bandeja y me habló de Gmail" | Falta el `~/.claude/CLAUDE.md` del paso 6b |
