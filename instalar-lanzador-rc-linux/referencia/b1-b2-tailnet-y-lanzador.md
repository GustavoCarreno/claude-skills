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
> hay URL de la que bajarlo. Vive en un repo privado, y **lo trae quien instala**. Consíguelo
> **antes** de empezar esta fase.
>
> 🔴 **Y la copia se arma con `exportar-para-cliente.sh`, nunca copiando la carpeta del
> lanzador completa** (desde el 17 de noviembre de 2026). La carpeta de trabajo del lanzador
> trae, junto al código, la bitácora y los pendientes de quien lo construye, sus diálogos
> grabados, sus diseños con ligas y claves, y los archivos de otras personas. Copiarla entera
> le entrega todo eso al cliente. El guion copia solo lo confirmado en git que el lanzador
> necesita para correr y para pasar su batería, escribe `VERSION` con el commit y la fecha, y
> avisa en rojo si algo de la cuenta de quien instala se coló:
>
> ```bash
> # en la máquina de quien instala, dentro del repo del lanzador
> ./exportar-para-cliente.sh /ruta/destino/rc-launcher
> ```
>
> **Usarlo siempre con carpeta destino.** Sin ella intenta armar un `.zip` con `zip`, y en una
> máquina que carece de `zip` deja un archivo de 0 bytes sin marcar error (medido el 17 de
> noviembre de 2026; pedido el arreglo en lanzador). El aviso rojo nombra hoy tres archivos
> que se quedan a sabiendas: el propio guion y dos del modo de varias personas
> (`multiusuario/README.md` y `alta-usuario.sh`), que traen de ejemplo un correo de la casa.
> Para una sola persona en la máquina, ese modo sobra. Medido: 166 archivos, commit `71b2e3d`.
>
> La copia ya armada viaja a la máquina del cliente por `scp`, en una memoria USB o como
> `.tar`.

```bash
# ORIGEN es la copia que armó exportar-para-cliente.sh y TRAJISTE. Ajusta la ruta.
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

**Y la versión que llegó**, que es lo primero que se pregunta cuando algo falla:

```bash
cat ~/rc-launcher/VERSION     # commit y fecha de la copia
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

Debe pasar **la suite completa, sin una sola falla**. Al 28 de octubre de 2026 son 1730 pruebas
y corren en unos seis minutos en el iMac. **El número crece con cada versión, así que no lo trates como
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
> es código del lanzador. Al 19 de octubre de 2026:
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
> | El proyecto principal | Uno de sus proyectos, escogido con un clic en el menú (Hacer principal), va hasta arriba del mosaico. Ver B10a |
> | La tarjeta Hoy | Junto al principal: las facturas por emitir, las tres primeras de *Hacer ya* y el estado de GES. Se enciende sola. Ver B10b |
> | Las esperas en el principal | Las tres esperas más viejas de todos los proyectos, debajo del principal. Ver B10b |
> | Las facturas por emitir | En rojo arriba de todo, con el botón Ya la emití. **Pide las claves `factura` y `última factura` en cada contrato mensual**, y la regla 12 de A7c en el `CLAUDE.md` global |
> | El repaso diario de GES | **Queda apagado hasta escribir `barrido.json`**, que es el único paso de configuración de esta lista. Ver B10c |
> | La escucha empieza en 18 segundos, y atiende órdenes | Al 11 de octubre de 2026: la sesión de escucha arranca sin esperar el resumen, gana el botón «Atiende lo que diré» (mantener presionado), la voz opcional para sus respuestas, y órdenes que crean y mueven eventos, dejan borradores, usan Drive y dejan recados. Ver B9. Viajan cuatro archivos nuevos (`escucha_voz.py`, `escucha_borrador.py`, `escucha_recado.py`, `escucha_paginita.py`), y el `--delete` del paso los trae junto con lo demás |
> | La revisión de arranque, solo en sesiones nuevas | Al 7 de octubre de 2026: urgentes, transcripciones, agenda y retroalimentación se revisan al abrir una sesión nueva. Al retomar una anterior la sesión arranca directo, porque esa conversación ya lo vio |
> | La ficha de una tarea | Al 11 de octubre de 2026: tocar una tarea en el principal, en Hoy o en Enfoque abre su ficha con Hecha, Descartar, Dejar retro y Abrir el proyecto, en vez del menú con toda la lista. En cada cuadrante de Enfoque los botones se ven siempre. Ver B10b. Viajan dos plantillas nuevas (`templates/_ficha.html` y `templates/_script_enfoque_cuadrante.html`); `templates/_script_abrir_y_bajar.html` se retiró, y si queda en una máquina vieja estorba en cero, porque ya nadie lo incluye |
> | La voz sin comillas | La voz de «Atiende lo que diré» deja de leer comillas, guiones y símbolos: Kokoro decía «tilde» antes y después de lo citado. Ver B9 |
> | Las casillas del arranque | Al 14 de octubre de 2026: lo urgente se contesta en una pantalla de casillas, «¿Cuáles ya están hechas?», y todo lo demás que encontró la revisión de arranque sale junto en una sola lista, «¿Qué atiendo ahora?». Ver B11d. **Pide el reinicio del final de este paso**, o las sesiones nuevas siguen con las preguntas sueltas de antes |
> | Urgentes que ya llegaron, y bloques ya atendidos | Al 14 de octubre de 2026 (lanzador `0ea2c09` y `1af5655`): «¿Cuáles ya están hechas?» pregunta solo por las urgentes vencidas, que vencen hoy o con su bloque hoy, aunque el mosaico siga contando todas; y la revisión de calendario salta el bloque propio que ya trae « ✓» en el título. Ver B11d y B8d. **Pide el mismo reinicio** |
> | El correo de su gente al arrancar | Viaja `correo_sesion.py`, pero **queda apagado hasta escribir `correo.json` y crear la etiqueta «Procesado» en Gmail**. Ver B11b |
> | La agenda de hoy y la liga de cada evento | Al 15 de octubre de 2026 (lanzador `9e1f53f` a `75de62e`): «En la agenda de hoy» en la portada, con las tarjetas amarillas de los proyectos que tienen un evento pendiente hoy, y la liga que abre un proyecto con su evento. Viaja `agenda.py`, nuevo. **Queda apagada sin `calendario.json`**, y la liga pide además la sección de B8f en el `CLAUDE.md` global. Ver B8e y B8f. **Pide el reinicio** |
> | La junta completa al arrancar | Al 15 de octubre de 2026 (fusión `b4fcc0f`): la sexta revisión del arranque ofrece cada junta de la escucha sin procesar, con su transcripción de Drive y sus capturas. Viaja `juntas_sesion.py`, nuevo. **En una máquina que ya usaba la escucha, correr `sembrar`** antes de la primera sesión. Ver B12. **Pide el reinicio** |
> | La tarjeta del principal, en amarillo con su evento | Al 16 de octubre de 2026 (lanzador `b8e5b4f`): el proyecto principal también se pinta de amarillo cuando tiene un evento pendiente hoy, y de verde con la barra amarilla si ya tiene sesión. Antes se quedaba sin color, porque es una envoltura con el botón adentro. Viaja `templates/_tile_principal.html` con `templates/_estilos.css`. Ver B8e |
> | Títulos de sesión sin «[Image: …]» | Al 16 de octubre de 2026 (lanzador `929daa4`): cuando una sesión leía una imagen, la tarjeta y las sesiones previas podían titularse «[Image: original 2040x1760…]», porque Claude Code guarda lo que regresa la herramienta como si fuera un mensaje del usuario. Ahora esas entradas se saltan y sale el encargo real. Viaja solo `sessions.py`, y se comporta igual en Windows porque lee el mismo formato de Claude Code |
> | La sesión rápida | Al 19 de octubre de 2026 (lanzador `6825d44`): el botón «Sesión rápida · sin revisión de arranque» del menú abre una sesión nueva sin el aviso de arranque, y el gancho de arranque también se calla. El registro `lanzamientos.jsonl` lo anota con `"rapida": true`. Viajan `app.py`, `sessions.py`, `procesos_tmux.py`, `procesos_windows.py`, `agenda.py`, `templates/_menu.html` y `templates/_estilos.css`. **Pide el reinicio** |
> | El menú regresa a su tarjeta | Al 27 de octubre de 2026 (lanzador `1bfd932`): cerrar el menú de un proyecto deja la página en la tarjeta donde se tocó. Antes, en Chrome de Android, abrir un proyecto desde Principal, Fijados o la agenda y lanzar la sesión mandaba la página hasta el fondo, a la copia del proyecto en Todos, porque el mosaico se redibuja cada 8 s y el navegador devolvía el foco a esa copia al cerrar la ventana. Medido con el salto provocado: antes de 838 a 5431 px, con el arreglo se queda en 838. Viaja solo `templates/_script_menu.html`, sin pasos nuevos, y **se ve hasta recargar la pestaña del teléfono** (ver el aviso de abajo) |
> | La cuenta de Claude que vence | Al 27 de octubre de 2026 (lanzador `946d9af`): aviso en ámbar 3 días antes de que venza la cuenta, y en rojo con «Volver a entrar» desde el teléfono cuando una sesión se atora en «Login expired». Viajan `cuenta.py`, `templates/_cuenta.html` y `templates/_cuenta_entrar.html`. Ver B13. **Pide el reinicio** |
> | El arranque busca evidencia antes de preguntar | Al 28 de octubre de 2026 (lanzador `caecbd0`): antes de «¿Cuáles ya están hechas?», la sesión revisa los correos enviados (con `gws` donde exista, y si no con el conector de Gmail), el calendario (eventos con « ✓» o con «Atendido en sesión»), el historial de git y los archivos del proyecto, y las notas de cada tarea. Palomea sola lo comprobado, con una nota «palomeada por la sesión al arrancar el AAAA-MM-DD: <evidencia>», lo dice en un renglón «Ya estaban hechas y las palomeé:» y pregunta solo por lo demás. Con la retroalimentación dictada hace lo mismo: sella la que ya quedó atendida, sin borrar lo dictado. Ante la duda, pregunta. Viaja solo `pendientes.py`, sin configuración nueva, y vale igual por el lanzador que por `claude` directo con el gancho de arranque. El arranque tarda entre medio minuto y un minuto más cuando hay urgentes, dentro de la suscripción. Ver B11d. **Pide el reinicio**. |
> | La escucha lee el evento y su guion | Al 22 de octubre de 2026 (lanzador `d732236`): al empezar una junta, una lectura aparte busca el evento en curso y su guion. Viaja solo `escucha_sesion.py`. **Pide `calendario.json` de B8.** Ver B15a. |
> | El resumen de Escuchar, guardado | Al 1 de noviembre de 2026: el resumen se guarda por proyecto y se pone al día por diferencias, con Compromisos armados por código. Viaja `resumen_proyecto.py`, nuevo. Ver B15b. |
> | Dialogar | Al 1 y 2 de noviembre de 2026: botón junto a Escuchar, envío al callar y voz por partes. Viajan `dialogo_real.py`, `sesion_viva.py`, `vad.py`, la carpeta `vad/` y `templates/_escucha.html`. Ver B15c. **Pide el reinicio**. |
> | El botón atrás y la tarjeta «Escuchando» | Al 2 de noviembre de 2026 (lanzador `17a880a`): atrás regresa a Proyectos sin reabrir Escuchar ni Dialogar, y la tarjeta dice cuánto lleva la junta. Solo de la página: **se ve hasta recargar la pestaña del teléfono**. Ver B15d. |
> | «Abre» por voz | Al 8 de noviembre de 2026: micrófono en «Filtrar proyectos». Viajan `orden_voz.py` y `templates/_script_voz.html`. **Pide la llave de A8.** Ver B15e. |
> | El mosaico ancho | Al 9 de noviembre de 2026: desde 1,024 px el mosaico usa las columnas que quepan. Solo CSS (`templates/_estilos.css`, `templates/index.html`). |
> | El rescate del toque | Al 13 de noviembre de 2026: «Abriendo…», reintento a los 3 s y registro de toques lentos. Viaja `toques.py`, nuevo. Ver B15f. |
> | Dictar al crear un proyecto | Al 14 de octubre de 2026 (lanzador `736c101`): botón Dictar bajo «¿De qué se trata?». **Pide la llave de A8.** Ver B15g. |
>
> **Las sesiones que ya estaban abiertas conservan el aviso de arranque viejo.** El nuevo sale
> en la siguiente que se abra.

> 🔴 **Actualizar y reiniciar van en el mismo paso, y nunca con una junta abierta** (2 de
> noviembre de 2026). La voz, la bitácora y el repaso corren como procesos aparte y toman el código
> nuevo en cuanto se copia, aunque el servicio siga con el viejo; entre la copia y el reinicio,
> la página y la voz quedan desfasadas. Antes de reiniciar, comprobar que no haya Escuchar ni
> Dialogar abiertos:
>
> ```bash
> cd ~/rc-launcher && .venv/bin/python -c "import escucha; print(escucha.juntas_abiertas())"
> ```
>
> Debe imprimir una lista vacía. Y después de la batería, `tmux ls` debe mostrar las mismas
> sesiones que antes: una de más quiere decir que una prueba tocó sesiones reales.


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
