# B3 y B3b · Arranque automático, el vigilante y su canal de avisos

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B3. Arranque automático
- B3b. El canal de avisos, para que el vigilante sirva de algo
  - Dos caminos, y el segundo es el normal
  - Dejarlo configurado
  - Del lado del teléfono
  - Comprobarlo, que es un renglón

<!-- fin del encabezado agregado al partir -->

## B3. Arranque automático


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

## B3b. El canal de avisos, para que el vigilante sirva de algo

**Esto faltaba hasta el 10 sep 2026**, y es un hueco que conviene entender antes de
saltárselo: **B3 habilita `rc-watcher.timer`, que corre cada minuto**, y su trabajo es
avisar cuando una tarea termina, o sea cuando Claude Code se queda esperando a la
persona. Sin este paso el vigilante corre, detecta el turno cerrado, **intenta avisar y
falla**, porque le falta a dónde mandar. Y como un envío fallido se deja sin marcar a
propósito, para reintentarlo, **el error se repite cada minuto** en el registro del
sistema, donde el usuario jamás lo ve.

El canal es **ntfy**: una aplicación de teléfono que recibe avisos y un servidor que los
publica. Sin cuenta de correo, sin token de por medio, y con una versión gratuita.

### Dos caminos, y el segundo es el normal

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

### Dejarlo configurado

```bash
mkdir -p ~/.config/rc-launcher
TEMA="rc-$(head -c 18 /dev/urandom | base64 | tr -dc 'a-z0-9' | head -c 16)"
cat > ~/.config/rc-launcher/ntfy.json <<EOF
{
  "url": "https://ntfy.sh",
  "tema": "$TEMA",
  "usuario": "",
  "clave": "",
  "prioridad": "default",
  "titulo_suelto": "Claude Code"
}
EOF
chmod 600 ~/.config/rc-launcher/ntfy.json
echo "El tema es: $TEMA"
```

**El tema hay que copiarlo**, porque es lo que la persona escribe en su teléfono. Con
servidor propio se cambian `url`, `usuario` y `clave`, y el tema puede ser legible.

### Del lado del teléfono

Instalar **ntfy** (Play Store, App Store o F-Droid), tocar **Agregar suscripción** y
escribir el tema. Con servidor propio, marcar **Usar otro servidor** y poner la dirección
con su usuario y contraseña.

### Comprobarlo, que es un renglón

```bash
cd ~/rc-launcher && .venv/bin/python -c "
import avisos
print(avisos.enviar('Prueba de instalación\nSi ves esto en el teléfono, el canal quedó.'))
"
```

Sale `(True, 'avisado')` **y el aviso llega al teléfono**. Las dos cosas: el `True` dice
que el servidor lo aceptó, y solo el teléfono dice que la suscripción está bien escrita.

> 📌 **Si sale `(False, ...)`, el mensaje dice cuál de las tres cosas falló**: falta el
> archivo, el servidor contestó un código (un 401 es usuario o clave), o la red. Un
> `403` en `ntfy.sh` suele ser un tema con mayúsculas o con caracteres raros.
