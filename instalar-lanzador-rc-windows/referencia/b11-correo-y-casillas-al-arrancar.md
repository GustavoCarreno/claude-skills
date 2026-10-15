# B11 · El correo de la gente del proyecto, y las casillas del arranque

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A5, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B11. El correo de la gente del proyecto, y las casillas del arranque
  - B11a. Lo que tiene que existir antes
  - B11b. La configuración y la etiqueta Procesado
  - B11c. Verificar
  - B11d. Lo que verá al abrir una sesión: una sola lista de casillas
  - B11e. Lo que hay que decirle, y lo que cuesta

## B11. El correo de la gente del proyecto, y las casillas del arranque

**Lo que deja funcionando:** al abrir una sesión nueva en un proyecto, el asistente saca del
contexto del proyecto (su `CLAUDE.md`, `contratos.md`, `pendientes.md` y sus minutas) los dominios
de correo de la gente que participa en él, por ejemplo el de la empresa del cliente. Busca en la
bandeja de entrada los correos de los últimos 3 días que vengan de ahí y que todavía no lleven la
etiqueta **«Procesado»**, y le dice al cliente en un renglón quién escribe y de qué trata cada uno.
Con su sí, lo procesa: lo lee completo, lleva a `pendientes.md` y al `CLAUDE.md` lo que salga de
él, deja en Borradores la respuesta si hace falta (**nunca la envía**) y le pone la etiqueta.

**La etiqueta es lo que evita que el mismo correo se ofrezca dos veces**, en ese proyecto o en
otro. Hace con el correo lo mismo que la subcarpeta «Procesadas» hace con las transcripciones de B7.

> 📌 **Dos reglas que la instrucción ya trae:** para quien escribe desde un correo gratuito
> (`gmail.com`, `outlook.com`) se busca su dirección completa y no el dominio, porque el dominio
> traería a medio mundo; y **el dominio propio del cliente se deja fuera**, porque sus propios
> correos son ruido aquí.

> 📌 **El lanzador sigue sin hablar con Google**, igual que en B7 y B8: solo lee la configuración
> y le redacta la instrucción a la sesión. Quien busca en el correo es el asistente, con la
> herramienta que diga la configuración.

### B11a. Lo que tiene que existir antes

| Requisito | Por qué |
|---|---|
| **El conector de Gmail de A5 en `Connected`** (o Composio con Gmail, A5e) | Con él se busca, se lee, se deja el borrador y se pone la etiqueta |
| **El correo del cliente en Gmail o Google Workspace** | La instrucción dice "busca en Gmail". Para un cliente en Microsoft 365 esta revisión todavía falta: dejar `correo.json` sin escribir |
| **Una copia del lanzador del 14 de octubre de 2026 o posterior** | Es la que trae `correo_sesion.py` y las casillas. Una anterior ignora la configuración en silencio |
| **Proyectos con su gente escrita** | Si el `CLAUDE.md` de un proyecto carece de nombres, empresas o correos, la sesión carece de dominios que buscar y la revisión sale vacía |

```powershell
if (-not (Test-Path "$env:USERPROFILE\rc-launcher\correo_sesion.py")) { "FALTA: correo_sesion.py (llevar una copia nueva con B2b)" }
"revisión terminada"
```

### B11b. La configuración y la etiqueta Procesado

1. **Escribir la configuración.** En la máquina de un cliente la herramienta es el conector de
   Gmail de claude.ai, porque `gws` queda fuera para ellos (exige un proyecto de Google Cloud
   propio):

```powershell
$dir = "$env:USERPROFILE\.config\rc-launcher"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
'{"dias": 3, "etiqueta": "Procesado", "herramienta": "el conector de Gmail de claude.ai"}' |
  Set-Content -Path "$dir\correo.json" -Encoding utf8
```

> 📌 **La marca de orden de bytes que agrega `-Encoding utf8` se tolera**, igual que en B7b y B8b:
> el lanzador lee `correo.json` con `utf-8-sig`.

> 📌 **Las tres claves son opcionales** y tienen valor de fábrica: 3 días, la etiqueta
> «Procesado», y sin herramienta nombrada (la sesión escoge la que tenga). Conviene escribirlas
> igual, para que se vea qué está encendido. Si el cliente contrató Composio y conectó ahí su
> Gmail, la herramienta puede ser `"Composio"`. En la máquina de Gustavo dice
> `"el CLI gws (nunca el conector de Gmail)"`, que es su regla y no viaja.

2. **Crear la etiqueta «Procesado» en su Gmail.** 🔴 **Este paso es indispensable, y es el que se
   olvida.** Sin la etiqueta la búsqueda funciona igual (`-label:Procesado` deja pasar todo), así
   que el primer día nada falla; lo que falla es marcar el correo procesado, y entonces **el mismo
   correo se ofrece en cada sesión durante tres días**. Pasó en el Gmail de Gustavo: la etiqueta
   faltaba y se creó el 14 de octubre de 2026 a las 18:50, al probar la revisión.

   Cualquiera de las dos vías sirve:

   - **En Gmail, desde la computadora:** en la columna izquierda, *Más* → *Crear etiqueta nueva*
     → `Procesado` → *Crear*.
   - **Pidiéndoselo al asistente**, en una sesión cualquiera: *"crea en mi Gmail la etiqueta
     Procesado"*. El conector de Gmail tiene la herramienta para crear etiquetas.

   El nombre tiene que coincidir **letra por letra** con el de `correo.json`, mayúscula incluida.

**Sin reinicios para la configuración:** el lanzador lee `correo.json` cada vez que lanza una
sesión, y el gancho de B8b también lo lee, así que las sesiones abiertas a mano con `claude` reciben
la revisión igual. Para apagarla basta con borrar `correo.json`.

### B11c. Verificar

Primero que la configuración se lee y que la instrucción habla del cliente (deben imprimir
`True`, `False` y el nombre del cliente de B2):

```powershell
cd "$env:USERPROFILE\rc-launcher"; python -c "import correo_sesion as c; t = c.instruccion_para_la_sesion('prueba'); print(t is not None); print('Gustavo' in t); import usuario; print(usuario.quien())"
```

Y la prueba completa, con el cliente enfrente:

1. Escoger un proyecto cuyo `CLAUDE.md` nombre a alguien de fuera, con su correo o su empresa.
2. Pedirle a esa persona, o a un colega de su empresa, que le mande un correo corto. **Un correo
   del propio cliente no sirve para probar**, porque la regla deja fuera su dominio. Pasó el 14 de
   octubre de 2026: los correos de prueba de Gustavo, desde sus dos dominios, quedaron fuera los
   dos, y la prueba hubo que hacerla en otro proyecto con un correo real de una clienta.
3. Desde el teléfono, lanzar una sesión nueva en ese proyecto. **El correo debe salir en la lista
   «¿Qué atiendo ahora?»**, con un rótulo que empieza con `Correo`.
4. Marcarlo y dejar que lo procese. En Gmail, **el correo debe quedar con la etiqueta
   «Procesado»**.
5. Lanzar otra sesión nueva en el mismo proyecto: **ese correo ya no debe ofrecerse.**

### B11d. Lo que verá al abrir una sesión: una sola lista de casillas

**Esto viaja solo con el código del lanzador (B2b)**, sin configuración, y cambia cómo pregunta la
sesión todo lo que encontró al arrancar. Hasta el 14 de octubre de 2026 cada revisión preguntaba
por su lado, en texto, y el cliente contestaba varias preguntas seguidas. Ahora:

1. **Primero hace todas las revisiones**: la retroalimentación dictada desde el teléfono, las
   tareas urgentes, las transcripciones de Drive (B7), el bloque de calendario (B8) y el correo
   (esta sección), las que estén encendidas en esa máquina.
2. **Si hay tareas urgentes, van solas y primero**, en una pantalla de casillas que pregunta
   «¿Cuáles ya están hechas?». Ahí marcar quiere decir *ya la hice*, y la sesión palomea las
   marcadas en `pendientes.md`. Por eso van en su propia pantalla: en la siguiente, marcar quiere
   decir otra cosa.
3. **Las revisiones que salieron vacías se dicen en un renglón de texto**, sin pantalla.
4. **Todo lo demás va en una sola lista, «¿Qué atiendo ahora?»**, con una casilla por hallazgo.
   Cada rótulo empieza con su clase (`Transcripción`, `Evento`, `Correo`, `Retro`) y la
   descripción trae el contexto. **Marcar quiere decir atenderlo ahora**; lo que queda sin marcar
   se queda para después.

| Si el cliente… | Pasa esto |
|---|---|
| Marca uno o varios | La sesión los atiende, en orden |
| Deja todo sin marcar y confirma | Todo se queda para después |
| Toca **Omitir** («Skip») | Hoy ninguno. Es la misma salida en las dos pantallas, y por eso las dos pantallas carecen de una opción de "ninguna" |
| Tiene más de cuatro hallazgos | La lista sigue en una segunda pregunta de la misma pantalla, con encabezado `1 de 2`, `2 de 2` |
| Tiene un solo hallazgo | Sale también la opción «Dejarlo para después», porque la herramienta pide dos opciones |

> 📌 **Al retomar una sesión anterior se omite todo esto**, igual que antes: esa conversación ya lo
> vio. Solo las sesiones nuevas hacen las revisiones.

> ⚠️ **Después de copiar el código con B2b, reiniciar el lanzador** como lo dice B2b: `schtasks /end`, matar por PID al `python` que conserva el puerto 8765, y `schtasks /run`. El aviso de
> arranque lo arma el proceso del servicio, así que sin reinicio **las sesiones nuevas salen con el
> aviso viejo y nada lo avisa**. Pasó el 14 de octubre de 2026 a las 18:14: la primera prueba de
> las casillas salió con las preguntas sueltas de antes.

**Probado en sesión real el 14 de octubre de 2026** (lanzador `5164ba2`): la pantalla de urgentes
salió primero y sola, una transcripción se procesó de punta a punta desde la lista, y un evento en
curso salió como único hallazgo con su «Dejarlo para después».

### B11e. Lo que hay que decirle, y lo que cuesta

- **Que escriba a su gente en el proyecto.** La revisión es tan buena como el contexto: un
  proyecto que nombra a su cliente, su empresa y su correo encuentra sus correos solo; uno sin
  nombres sale vacío.
- **Que la etiqueta «Procesado» es suya y se puede tocar.** Quitársela a un correo hace que se
  vuelva a ofrecer en la siguiente sesión; ponérsela a mano lo da por visto.
- **Que el asistente deja borradores y nunca envía.** La respuesta queda en Borradores, y la manda
  él.
- **Cada sesión nueva arranca con una búsqueda en su correo**, aunque salga vacía. Es uso de su
  suscripción, pequeño, igual que las de Drive (B7) y calendario (B8).
