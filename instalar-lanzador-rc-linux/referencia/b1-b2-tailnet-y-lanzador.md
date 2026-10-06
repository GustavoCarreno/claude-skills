# B1 y B2 · La tailnet, el lanzador y cómo actualizarlo (B2b)

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B1. La tailnet
- B2. El lanzador
  - B2b. Llevarle una versión nueva a una máquina que ya lo tiene

<!-- fin del encabezado agregado al partir -->

## B1. La tailnet


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

## B2. El lanzador


> 🔴 **De dónde sale el código, porque este paso no se puede hacer sin traerlo.** A
> diferencia de `bitacora.py` (A3), **el lanzador NO está en el repo público de skills** y no
> hay URL de la que bajarlo. Vive en un repo privado, y **lo trae quien instala**: por `scp`
> desde tu equipo, en una memoria USB, o clonando el repo privado si la máquina tiene acceso.
> Consíguelo **antes** de empezar esta fase.

```bash
# ORIGEN es la copia del lanzador que TRAJISTE. Ajusta la ruta a donde la dejaste.
ORIGEN=/ruta/a/tu/copia/de/rc-launcher

# el código va al home, no a una ruta de sistema
rsync -a --exclude .venv --exclude __pycache__ --exclude .git \
      "$ORIGEN"/ ~/rc-launcher/

mkdir -p ~/claude          # la raíz de proyectos, que es donde vive el trabajo
```

**Comprobar que llegó completo antes de instalar nada**, porque una copia a medias arranca
igual y falla después, lejos de aquí:

```bash
for f in app.py sessions.py procesos.py requirements.txt templates tests; do
  [ -e ~/rc-launcher/"$f" ] || echo "FALTA: $f"
done
echo "revisión terminada (sin líneas FALTA arriba = completo)"
```

Ya con la copia completa, el entorno:

```bash
cd ~/rc-launcher
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`~/claude` no es negociable sin tocar código: `sessions.py` la calcula como
`Path.home() / "claude"`. Si los proyectos viven en otro disco, poner un symlink ahí.

**Comprobar antes de seguir**, porque si esto falla, nada de lo demás importa:

```bash
cd ~/rc-launcher && .venv/bin/python -m pytest -q
```

Debe pasar **la suite completa, sin una sola falla**. Al 5 de octubre de 2026 son 1188 pruebas
y corren en un segundo. **El número crece con cada versión, así que no lo trates como
contraseña**: lo que importa es que no falle ninguna, en la máquina del cliente, sin tocar
una línea. Eso es lo que demuestra que el código no depende de la máquina donde nació.

> 📌 **Si el proyecto ya tiene `pendientes.md` (A7), el lanzador ya lo pinta y lo palomea
> con el dedo, sin configuración adicional.** No hay ningún paso extra que hacer aquí.

**El nombre de quien usa la máquina**, para que los avisos de arranque le hablen por su nombre
y esperen su respuesta. Sin este archivo dicen "el usuario", que funciona igual:

```bash
mkdir -p ~/.config/rc-launcher
printf '{"nombre": "%s"}\n' "<Nombre del cliente>" > ~/.config/rc-launcher/usuario.json
chmod 600 ~/.config/rc-launcher/usuario.json
```

### B2b. Llevarle una versión nueva a una máquina que ya lo tiene

**Esto es para las actualizaciones, no para la instalación inicial.** El lanzador se mejora
seguido, y el código llegó aquí por copia: **nada se entera solo de que hay una versión
nueva**, así que actualizar es volver a copiar y reiniciar.

```bash
ORIGEN=/ruta/a/tu/copia/de/rc-launcher

rsync -a --delete --exclude .venv --exclude __pycache__ --exclude .git \
      "$ORIGEN"/ ~/rc-launcher/
cd ~/rc-launcher
.venv/bin/pip install -q -r requirements.txt    # por si la versión nueva pide algo más
.venv/bin/python -m pytest -q                   # todas en verde ANTES de reiniciar
sudo systemctl restart rc-launcher
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8765/salud
```

> ✅ **Reiniciar el servicio NO mata las sesiones que estén trabajando**, gracias a
> `KillMode=process` en el unit (B3). Se puede actualizar con el cliente usándolo.

> ⚠️ **El `--delete` es a propósito:** sin él, un archivo que la versión nueva ya eliminó se
> queda en la máquina y puede seguir importándose. Los excluidos están a salvo, así que el
> `.venv` sobrevive.

> 📌 **Lo que una máquina ya instalada recibe con solo este paso**, sin configuración, porque
> es código del lanzador. Al 5 de octubre de 2026:
>
> | Mejora | Qué cambia para el cliente |
> |---|---|
> | El menú abre al primer toque | Antes, tocar una tarjeta del mosaico a veces se quedaba sin abrir el menú: el mosaico se redibuja cada 8 segundos y la orden de abrir se perdía con él. Le pasa sobre todo a un teléfono que llega a la máquina por relevo de Tailscale, que es lo normal fuera de la casa |
> | El menú pesa una fracción | Las respuestas viajan comprimidas y la sección de tareas hechas se pide solo al desplegarla. Un menú de 1.8 MB bajó a 87 KB |
> | Pendientes en cinco grupos | Ver A7b. Lo que urge sale arriba y abierto |
> | Lo urgente, numerado al abrir sesión | La sesión lista lo vencido o lo que vence en 7 días y pregunta por números cuáles ya se hicieron |
> | Sesiones previas con su título real | Antes todas se llamaban igual, porque Claude Code titula con el primer mensaje y el lanzador abre muchas con una instrucción de revisión. Ahora se ve el primer encargo del usuario, y las sesiones de fondo (la bitácora que se escribe sola) dejan de llenar la lista |
> | Los avisos le hablan al cliente por su nombre | Antes decían "Gustavo", escrito fijo. Ahora sale de `usuario.json`, que hay que escribir una vez (ver arriba, en B2). Y en Windows el aviso de arranque ya llega aunque la consola esté en cp1252 |
> | La escucha con permisos cerrados, y en Windows también | La sesión de escucha deja de correr con todos los permisos (ver B9), y en Windows ya existe: antes el cuadro Escuchar aparecía y no arrancaba |
>
> **Las sesiones que ya estaban abiertas conservan el aviso de arranque viejo.** El nuevo sale
> en la siguiente que se abra.

> 🔴 **La pestaña que el teléfono ya tenía abierta sigue corriendo el código anterior.** El
> HTML y su script viajan juntos en la respuesta de la raíz, y una pestaña abierta conserva el
> que le tocó al cargarse: HTMX redibuja pedazos, y el script ya no se vuelve a leer. Tras
> actualizar hay que **recargar** desde el teléfono. Sin eso se está probando código viejo
> contra un servidor nuevo, y eso confunde cualquier diagnóstico.

> ⚠️ **La primera sesión de un proyecto creado con "+ Nuevo proyecto" puede repetir la
> pregunta de confianza de A2, aunque la raíz ya esté confiada.** Es el mismo síntoma, y
> otra vez invisible desde el teléfono: el botón se enciende, la sesión existe, y del otro
> lado solo hay un cursor esperando esa respuesta. Se contesta igual, desde la app del
> teléfono, dentro de esa misma sesión: sí, y ya arranca. **Mejor todavía, adelantarlo: la
> primera vez que se estrena un proyecto nuevo, abrir su primera sesión desde la
> computadora** (`cd ~/claude/<proyecto> && claude`, contestar, `/exit`) antes de tocarlo
> desde el teléfono. Las sesiones siguientes de ese proyecto, y las que se lancen desde el
> teléfono, ya arrancan directo.
