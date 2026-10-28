---
name: instalar-lanzador-rc-windows
description: Activar cuando alguien pida instalar, montar o configurar el lanzador rc (rc-launcher) en una laptop o PC con Windows, o dejar lista una máquina Windows para lanzar sesiones de Claude Code desde el teléfono. También cuando pida el lanzador web, la bitácora automática que actualiza CLAUDE.md sola, o publicar el lanzador en su tailnet de Tailscale. Cubre Windows 10 22H2 y Windows 11 con winget.
---

# Instalar el lanzador rc y la bitácora automática en Windows

Deja una laptop con Windows lista para lanzar, retomar y cerrar sesiones de Claude Code
desde el teléfono, y para que el `CLAUDE.md` de cada proyecto se escriba solo al cerrar
cada sesión.

**Procedimiento verificado de punta a punta en la VM `win11-dogfood` la madrugada del 3 de
agosto de 2026.** Para Linux existe el equivalente en `instalar-lanzador-rc-linux`, y ese
está verificado más recientemente.

> ⚠️ **Qué está verificado y qué no, porque importa antes de pararse enfrente de un
> cliente.** Los pasos 0 a 7 se corrieron completos en Windows. Lo que se agregó **después**
> de esa verificación, y **solo está probado en Linux**, es la sección **1b** (las cinco
> preguntas de primer arranque de Claude Code) y la nota de autenticación de la sección 8.
> Son de Claude Code y no del sistema operativo, así que aplican igual, pero **la primera vez
> que se use esta guía en Windows conviene confirmarlas** y corregir aquí lo que salga
> distinto.
>
> **La sección A4 se corrió en Windows el 3 de agosto**, con dos matices que conviene tener
> presentes: los seis IDs de `winget` están **verificados uno por uno**, pero **Node y
> `yt-dlp` ya estaban instalados en esa VM**, así que su instalación no se ejercitó desde
> cero. Todo lo demás de A4 (LibreOffice, Pandoc, Tesseract con su español, Poppler, los
> paquetes de Python y npm, el `NODE_PATH`, el plugin y las cinco pruebas de aceptación) se
> instaló y se probó ahí. **La prueba 5 pasó**: una sesión real generó una presentación
> ejecutiva de cuatro láminas y corrió **tres pasadas de revisión visual** (16 defectos, luego
> 4, luego cero, con medición de píxeles). Es la evidencia de que el camino de A4f funciona
> de verdad y no solo en el papel.

## Qué queda funcionando


| Capacidad | Cómo se ve para quien lo usa |
|---|---|
| Lanzar sesiones desde el teléfono | Toca un botón y la sesión aparece en su app de Claude |
| Cerrarlas desde el teléfono | Toca cerrar y desaparece de la app |
| Retomar una conversación anterior | El menú del proyecto lista sus sesiones previas |
| Crear un proyecto nuevo | Botón "+ Nuevo proyecto", con nombre y contexto |
| **Hallar un proyecto tecleando su nombre** | Un campo arriba del mosaico deja a la vista los que coinciden y esconde el resto. Con treinta proyectos se llega al que quiere con media palabra, en vez de recorrer la reja entera con el dedo. Da igual mayúsculas y acentos, y el espacio vale por guion |
| Subir archivos desde el teléfono | Caen en `bandeja/` dentro del proyecto |
| **La bitácora se escribe sola** | Al cerrar, el `CLAUDE.md` del proyecto queda actualizado sin pedirlo, su `pendientes.md` también (se crea solo si hubo trabajo abierto), y los bloques de calendario que esa sesión movió quedan al día |
| **Documentos de oficina de verdad** | Pide un Word, un Excel con fórmulas o una presentación y salen archivos que abren en Office |
| **Su correo, su calendario y su Drive** | Pregunta qué le escribieron o pide que le agenden algo, y se resuelve sin salir de la conversación |
| **Más aplicaciones, y correos con adjunto** (opcional, con Composio) | Pide que le mande el contrato anexo al broker, o que actúe en una aplicación que los conectores de claude.ai no cubren, y se resuelve igual, sin salir de la conversación |
| **Sus pendientes por proyecto** | Ve qué falta y palomea lo hecho, desde la computadora o desde el teléfono |
| **Sus pendientes, ordenados por lo que urge** (requiere la fase B) | En el menú de cada proyecto los pendientes salen en cinco grupos según urgencia e importancia, cada uno plegable y con su cuenta. Lo que urge queda arriba y abierto, a un toque |
| **Al abrir una sesión, lo que urge sale numerado** (requiere la fase B) | Si hay pendientes vencidos o que vencen en la semana, la sesión nueva los lista con número y pregunta cuáles ya están hechos en una pantalla de casillas. Se marcan los hechos y ella los palomea. Lo demás que encontró al arrancar (retroalimentación, transcripciones, agenda, correo) sale después en una sola lista, «¿Qué atiendo ahora?». Ver B11d. Al retomar una sesión anterior se omite, porque esa conversación ya lo vio |
| **Una sesión rápida, sin revisión de arranque** (requiere la fase B) | En el menú de un proyecto sin sesión, debajo de Nueva sesión, el botón «Sesión rápida · sin revisión de arranque» abre una sesión nueva que entra directo y se salta la revisión de urgentes, transcripciones, agenda y correo, igual que al retomar una anterior. Sirve para entrar a pedir algo concreto. Desde un evento de la agenda se queda fuera, porque ahí la sesión es para atenderlo |
| **Sus contactos, al día** | Las personas que aparecieron en la sesión, con su correo o su teléfono, quedan al cerrar en un archivo de contactos listo para importar a Google Contacts |
| **Su trabajo, respaldado solo** | Al cerrar cada sesión, el proyecto se sube a su propio repositorio privado de GitHub. Si la computadora se descompone, en una nueva se recupera todo con un comando |
| **Un equipo completo, para quien trabaja sin equipo** | Le habla a Gestión, a Procesos o a Gabinete por su nombre, o entran solos cuando el tema es suyo. Cada uno revisa, pregunta y entrega lo que un área de empresa haría, en los términos de su propio negocio |
| **Lo que deja de cobrar, a la vista** (opcional, requiere la fase B) | Cada proyecto lleva sus contratos en un archivo, y la pantalla Contratos del lanzador suma lo que vence y avisa cuándo buscar al siguiente cliente |
| **Datos a la mano durante una junta** (opcional, requiere la fase B) | El teléfono escucha la conversación y en la misma pantalla van saliendo tarjetas con respuestas, datos y compromisos. Con el botón «Atiende lo que diré», que se mantiene presionado, le pregunta o le encarga algo: mover un evento, dejar un borrador, buscar un documento o dejarle un recado al proyecto, y si quiere oye la respuesta. Ver B9 antes de ofrecerlo |
| **Transcribir juntas y escuchar documentos** (opcional, con cuenta propia) | Sube la grabación de una junta y pide la minuta, o pide que le lean un documento para el camino |
| **El audio se escucha con un clic** (requiere la fase B) | Lo que pidió que le leyeran llega como liga: le pica desde el teléfono y suena, sin descargarlo ni buscarlo en el navegador de archivos |
| **Dejar dicho qué resultó, sin abrir sesión** (requiere la fase B) | Desde el teléfono, en cada pendiente hay un botón para dictar cómo quedó, y una sección aparte para los recados sueltos del proyecto, los que valen por sí mismos. Se dicta con el teclado del teléfono, así que cuesta cero llamadas al modelo, y la siguiente sesión se entera sola de que hay algo sin leer. **La lista se queda donde estaba al guardar**, para poder recorrerla de corrido |
| **Las transcripciones de sus grabaciones llegan solas** (opcional, requiere la fase B) | Al abrir una sesión nueva desde el teléfono, el asistente revisa la carpeta de Drive donde caen las transcripciones, le dice en un renglón cuáles son de ese proyecto y pregunta si las procesa. Con un sí, quedan guardadas en el proyecto y lo que salga de ellas llega a sus pendientes. Al retomar una sesión anterior la revisión se omite |
| **Los correos de su gente, al abrir el proyecto** (opcional, requiere la fase B) | Al abrir una sesión nueva, el asistente busca en su Gmail los correos recientes de la gente de ese proyecto que todavía no lleven la etiqueta «Procesado», y le dice en un renglón quién escribe y de qué. Con un sí, lleva lo que salga a sus pendientes, deja la respuesta en Borradores sin enviarla y lo etiqueta para no volver a ofrecerlo. Ver B11 |
| **La sesión le ofrece el bloque de su agenda** (opcional, requiere la fase B) | Si reservó en el calendario un bloque para ese proyecto y está en curso o empieza en media hora, la sesión nueva se lo resume en dos renglones al abrir y pregunta si lo atienden. Pasa igual si abre la sesión desde el teléfono o en la computadora, y se omite al retomar una sesión anterior. Un bloque propio que ya se atendió en otra sesión lleva « ✓» al final del título y deja de ofrecerse |
| **Sus compromisos de hoy, en amarillo** (opcional, requiere la fase B) | Debajo de Principal y Hoy, la sección «En la agenda de hoy» sube las tarjetas de los proyectos con un evento pendiente hoy, con la hora y el título. Un toque abre el proyecto con el evento nombrado, y la sesión nueva se lo ofrece aunque falten horas. Deja de contar al terminar, al traer la « ✓», o cuando dice que sí en la sesión. Ver B8e. En Windows, quitar la tarjeta al decir que sí depende de un arreglo pendiente del lanzador (ver B8f) |
| **Del calendario a su proyecto, en un toque** (requiere la fase B) | Los eventos que la sesión crea llevan al final de la descripción una liga que abre el lanzador en ese proyecto con el evento nombrado. La toca desde la notificación del calendario. Ver B8f |
| **La junta completa, al abrir el proyecto** (requiere la fase B y la escucha) | Al terminar una junta, la siguiente sesión le ofrece en una sola casilla la transcripción de la escucha, la de su grabadora en Drive si la hay, y las capturas de pantalla que tomó en ese rato. Con un sí la procesa completa, leyendo las capturas que cambian. Ver B12. En Windows las capturas dependen de un arreglo pendiente del lanzador (ver B12) |
| **Su proyecto principal, hasta arriba** (requiere la fase B) | Escoge con un clic el proyecto que agrupa a los demás. Va arriba del mosaico, y debajo trae las tres esperas más viejas de todos sus proyectos |
| **Lo de hoy, en una tarjeta** (requiere la fase B) | Junto al principal, la tarjeta Hoy junta las facturas que toca emitir, las tres tareas más urgentes y el estado del repaso del día |
| **Una tarea se atiende sin salir de lo que está viendo** (requiere la fase B) | Tocar una tarea en el principal, en la tarjeta Hoy o en Enfoque abre su ficha: la nota completa, lo que dictó y los botones Hecha, Descartar y Dejar retro. Se resuelve ahí, sin abrir la lista entera del proyecto, y la tarea desaparece de la tarjeta en el acto |
| **Las facturas que toca emitir, en rojo** (requiere la fase B) | Cada contrato mensual dice qué día se factura. Cuando llega el día, sale en rojo arriba de todo, y un botón la da por emitida |
| **Un repaso diario de sus promesas** (opcional, requiere la fase B) | La primera vez que abre el lanzador en el día, un repaso busca lo que prometió con fecha y quedó sin tarea, y lo anota en sus pendientes. Un botón lo vuelve a correr cuando quiera |

## Antes de empezar


- **La laptop tiene que quedar encendida y con la sesión de Windows iniciada.** No es un
  detalle: si se reinicia de noche y nadie entra, el lanzador deja de existir para el
  teléfono. Ver el paso 4 para lo que sí se puede mitigar y lo que no.
- **Esta guía no supone nada instalado.** Instala Claude Code, Python, Tailscale y levanta la
  red desde cero. Lo único que hay que traer de antemano es una cuenta de Anthropic con un
  plan que incluya Claude Code, y eso se resuelve en el paso 0.
- **Hace falta el teléfono a la mano.** No es opcional ni "para después": es la mitad del
  montaje, y hay pasos que solo se pueden hacer ahí.

## 0. Descarte previo, cinco minutos antes de instalar nada


Sirve para saber si la laptop siquiera es candidata. **Hacerlo antes de sentarse con el
cliente.** Descubrir en el paso 1 que su empresa bloquea las instalaciones es una hora
perdida y una mala primera impresión.

| Revisar | Cómo | Si falla |
|---|---|---|
| Windows 10 (22H2 o más) u 11 | `winver` | En Windows más viejo no hay `winget`; la instalación se vuelve manual y no está cubierta aquí |
| `winget` existe | `winget --version` | Instalar "App Installer" desde la Microsoft Store |
| Permisos de administrador | `net session` en PowerShell normal: si contesta sin error, hay permisos elevados | Sin administrador no se instalan Tailscale ni la tarea programada. **Aquí se para la instalación** hasta que Sistemas dé permisos o dé otra máquina |
| Sin MDM que bloquee | Preguntar, y probar `winget install --id Python.Python.3.12 --silent` | Muchas laptops corporativas bloquean instalaciones globales, servicios sin firmar o clientes de VPN. Es el bloqueo más común y **no tiene rodeo técnico**: hay que hablar con su departamento de Sistemas |
| Cuenta de Anthropic | Iniciar sesión en `claude.ai` | Sin un plan que incluya Claude Code no hay nada que instalar |
| El correo del cliente permite apps de terceros | que **él mismo** entre a `claude.ai/customize/connectors` e intente conectar su calendario | Si su administrador de Google Workspace o Microsoft 365 tiene bloqueadas las apps de terceros, **no hay rodeo técnico**: es conversación con su área de sistemas. Descubrirlo aquí cuesta un minuto; descubrirlo en la cita cuesta la sesión |

> ⚠️ **Los seis renglones dependen de la empresa del cliente, no de nosotros.** Si alguno
> truena, el problema es de gestión, no técnico, y conviene plantearlo así desde el principio
> en vez de intentar rodearlo.

> 📌 **Por qué ese renglón del correo está aquí y no en A5, que es donde se conecta.** Es la
> misma lógica que Tailscale: **lo que depende del área de sistemas del cliente es una barrera
> de calificación, no un paso de instalación.** Y no es hipotético — el primer piloto se quedó
> parado semanas esperando que un departamento externo devolviera un archivo. Además de correo
> y calendario, de ahí depende que el cierre automático pueda poner al día sus bloques (A7).

---

# FASE A · La base

**Lo que deja instalado:** Claude Code funcionando, la carpeta de proyectos, la bitácora
automática con el respaldo en GitHub, el runtime que necesitan las skills de documentos, y el acceso a su correo,
calendario y Drive. **Corresponde al módulo 1 del programa.**

Es entregable completa por sí sola: si el área de sistemas del cliente bloquea Tailscale,
la fase B no se puede montar y **la fase A sigue siendo una entrega íntegra**, no media.

## Cómo se recorre esta guía

Esta guía está partida en archivos, uno por sección grande, para que cada paso se lea
completo. **La regla de uso es una sola: antes de ejecutar una sección, abre su archivo y
léelo de punta a punta**, porque los avisos que evitan las fallas calladas suelen venir
después del comando. Las secciones se recorren en el orden de las tablas, y cuando un
archivo cite otra sección (A3, B2b…), aquí está dónde vive.


| Sección | Archivo | Qué deja |
|---|---|---|
| A1 y A2 | [`referencia/a1-a2-prerrequisitos-y-primer-arranque.md`](referencia/a1-a2-prerrequisitos-y-primer-arranque.md) | Prerrequisitos y el primer arranque de Claude Code, con la confianza de la carpeta |
| A3 | [`referencia/a3-bitacora.md`](referencia/a3-bitacora.md) | La bitácora automática: bitacora.py, sus ganchos y bitacora.json |
| A4 | [`referencia/a4-runtime-de-documentos.md`](referencia/a4-runtime-de-documentos.md) | El runtime que las skills de documentos dan por hecho, con sus cinco pruebas |
| A5 | [`referencia/a5-correo-calendario-drive.md`](referencia/a5-correo-calendario-drive.md) | Conectores de correo, calendario y Drive, y Composio |
| A6 y A7 | [`referencia/a6-a7-gitignore-y-pendientes.md`](referencia/a6-a7-gitignore-y-pendientes.md) | El gitignore global y la convención de pendientes.md |
| A8 | [`referencia/a8-deepinfra.md`](referencia/a8-deepinfra.md) | Transcripción y voz con la cuenta propia de DeepInfra |
| A9 | [`referencia/a9-respaldo-en-github.md`](referencia/a9-respaldo-en-github.md) | El respaldo de cada proyecto en su propio repositorio privado de GitHub, y cómo se recupera todo en una máquina nueva. **Obligatoria** |
| A10 | [`referencia/a10-perfiles-del-equipo.md`](referencia/a10-perfiles-del-equipo.md) | Los ocho perfiles del equipo (GAB, GES, PAS, MID, ISI, DAS, CYF y Tavo), con Gabinete como postura por defecto, y las reglas de redacción con sus barridos (A10f). El contenido lo trae quien instala, desde su repositorio privado |

---

# FASE B · La red y el teléfono

**Lo que deja instalado:** la tailnet del cliente, el lanzador publicado y la bandeja.
**Corresponde al módulo 3 del programa.**

**No empezar esta fase sin la A terminada y verificada.** Y si el paso 0 detectó que la
empresa bloquea Tailscale o las instalaciones, esta fase no procede: eso se supo antes de
la primera sesión justamente para no descubrirlo aquí.

| Sección | Archivo | Qué deja |
|---|---|---|
| B1 y B2 | [`referencia/b1-b2-tailnet-y-lanzador.md`](referencia/b1-b2-tailnet-y-lanzador.md) | La tailnet, el lanzador y cómo actualizarlo (B2b) |
| B3 y B3b | [`referencia/b3-arranque-y-avisos.md`](referencia/b3-arranque-y-avisos.md) | Arranque automático, el vigilante y su canal de avisos |
| B4, B5 y B6 | [`referencia/b4-b6-publicar-bandeja-rc.md`](referencia/b4-b6-publicar-bandeja-rc.md) | Publicarlo en la tailnet, la bandeja y el comando rc |
| B7 | [`referencia/b7-transcripciones-de-drive.md`](referencia/b7-transcripciones-de-drive.md) | Las transcripciones que llegan a Drive (opcional) |
| B8 | [`referencia/b8-calendario-al-arrancar.md`](referencia/b8-calendario-al-arrancar.md) | El bloque de calendario al arrancar, la agenda de hoy en el lanzador y la liga de cada evento (opcional) |
| B9 | [`referencia/b9-escucha-en-vivo.md`](referencia/b9-escucha-en-vivo.md) | La escucha en vivo durante una junta (opcional) |
| B10 | [`referencia/b10-principal-hoy-y-ges.md`](referencia/b10-principal-hoy-y-ges.md) | El proyecto principal, la tarjeta Hoy y el repaso diario de GES |
| B11 | [`referencia/b11-correo-y-casillas-al-arrancar.md`](referencia/b11-correo-y-casillas-al-arrancar.md) | El correo de la gente del proyecto, y las casillas del arranque (el correo es opcional) |
| B12 | [`referencia/b12-junta-completa-al-arrancar.md`](referencia/b12-junta-completa-al-arrancar.md) | La junta completa al arrancar: la escucha, Drive y las capturas de pantalla, en una casilla |
| B13 | [`referencia/b13-cuenta-de-claude.md`](referencia/b13-cuenta-de-claude.md) | Cuando la cuenta de Claude pide volver a entrar: el aviso 3 días antes (en Windows, solo el aviso) |
| B14 | [`referencia/b14-varias-personas.md`](referencia/b14-varias-personas.md) | Varias personas en una máquina: lo que hay hoy en Windows y el estilo de partida a mano (opcional) |

---

## 7. Verificación, en orden

La lista completa de comprobaciones vive en [`referencia/verificacion.md`](referencia/verificacion.md).
**No se entrega una máquina sin recorrerla entera**, en ese orden, porque cada renglón da por
hecho que el anterior pasó.

## 8. Lo que NO resuelve esta instalación


Decirlo antes de instalarla en casa de un cliente:

- **La puerta es la identidad de Tailscale**, y solo eso. El lanzador sí valida quién entra
  (encabezado `Tailscale-User-Login`, y `%USERPROFILE%\.config\rc-launcher\acceso.json`
  extiende la lista), pero **quien esté en la tailnet y en esa lista puede lanzar sesiones
  con acceso completo al disco de esa persona**. Es el permiso más fuerte del montaje. Para
  un cliente cuyo departamento de Sistemas puede meter otros equipos a la red, conviene
  revisar `acceso.json` explícitamente en vez de confiar en la pertenencia a la tailnet.
- **Si la laptop se reinicia y nadie inicia sesión, no hay lanzador.** El modo desatendido de
  Tailscale sube la red, pero **no las tareas de usuario**, que necesitan contraseña
  guardada. Es el hueco conocido de Windows y no tiene arreglo limpio desde aquí.
- **La bitácora la escribe un modelo**, así que consume tokens de la cuenta del usuario cada
  vez que cierra una sesión con trabajo pendiente.
- **Depende de cosas que no controlamos.** Si la empresa bloquea Tailscale, las instalaciones
  globales o los servicios sin firmar, este montaje no tiene rodeo técnico. El paso 0 existe
  para descubrirlo antes de la cita, no durante.
- **La tailnet queda a nombre del cliente**, o sea que él administra sus interruptores y sus
  dispositivos. Es deliberado, pero significa que un cambio suyo puede tumbar el acceso sin
  que nosotros nos enteremos.
- **Un proyecto cuya carpeta se renombre con la sesión viva** desaparece del grid y esa
  sesión queda inmatable desde el teléfono. Hay que cerrarla desde la máquina.

## Errores comunes


| Síntoma | Causa real |
|---|---|
| "No me funcionó el paso 1" | `winget` dejó el PATH viejo en esa consola; abrir una nueva |
| `python` abre la Microsoft Store | Alias de ejecución de Python activos en Configuración |
| La primera sesión se queda colgada | Claude Code no pasó por su primer arranque; está detenido en una de las cinco preguntas, sin ventana donde verlas. Ver A2 |
| Un proyecto nuevo se cuelga la primera vez, incluso con la raíz confiada | Si pasa con TODOS los proyectos nuevos: la confianza se aceptó dentro de un proyecto y no en la raíz, no se hereda (ver A2). Si es solo el primero de un proyecto creado desde "+ Nuevo proyecto": es normal, contestar desde el teléfono o adelantarlo abriendo la primera sesión desde la computadora (ver B2) |
| Un proyecto que llevaba meses trabajando empieza a pedir la confianza | Le corrieron `git init`, y la herencia se corta en la raíz de cada repositorio. El flag de permisos omitidos tampoco lo salta. Se siembra la llave con el fragmento de A2 |
| Se le pidió a un agente que hiciera el primer arranque y se quedó a medias | A2 no se puede delegar; exige a una persona con la sesión al frente, sobre todo para la pregunta 4. Ver A2 |
| Aparece "acepta toda la responsabilidad" y nadie sabe si contestar | Es la pregunta 4 de A2 (modo sin confirmaciones); solo la acepta el dueño de la máquina, en persona. Ver A2 |
| La sesión no cierra desde el teléfono | Falta `pywinpty` |
| La tarea programada "nunca ha ejecutado" (`267011`) | Nació con `LogonType: Interactive` y nadie tiene sesión iniciada. Pasa con `/SC ONSTART` y también con `/SC MINUTE`, con `/RU` y `/NP` incluidos. Se arregla registrándola con `New-ScheduledTaskPrincipal -LogonType S4U`, como hacen B3 y B3b |
| Reiniciar la tarea no hace nada | `schtasks /run` sobre una tarea corriendo no reinicia; primero `/end` |
| Se actualizó el código y el lanzador sigue con el viejo (una ruta nueva da 404) | `schtasks /end` deja vivo al `python` hijo, que conserva el puerto. Matar por PID al que escucha el 8765 y volver a lanzar la tarea. Ver B3 |
| El nodo desaparece de la tailnet en la pantalla de contraseña | Falta `tailscale set --unattended=true` |
| La raíz da 403 y parece roto | Es correcto sin identidad de Tailscale; medir con `/salud` |
| Acentos rotos en el `CLAUDE.md` global | Se guardó en cp1252. Abrir con VS Code o Notepad++ y guardar como UTF-8, o desde PowerShell: `$f="$env:USERPROFILE\.claude\CLAUDE.md"; $c=[System.IO.File]::ReadAllText($f,[System.Text.Encoding]::GetEncoding('cp1252')); [System.IO.File]::WriteAllText($f, $c, [System.Text.Encoding]::UTF8)` |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| "Le pedí sus pendientes y no sabe qué son" | Falta la sección de A7 en `%USERPROFILE%\.claude\CLAUDE.md` |
| Los conectores no aparecen en `/mcp` | La sesión no está autenticada con la suscripción. Correr `/status`. Ver A5b |
| No deja conectar Gmail desde `/mcp` | Es lo esperado: va en claude.ai, no en la terminal. Ver A5a |
| El borrador salió sin el archivo adjunto | Limitación vigente del conector; se adjunta a mano antes de enviar. Ver A5c |
| Pide una llave de DeepInfra que el cliente no esperaba | No se le explicó A8 en la entrega. Es opcional y con su propia cuenta; explicarle y seguir cuando la tenga |
| La misma transcripción se ofrece en cada sesión | No se movió a `Procesadas`: la subcarpeta falta, se llama distinto, o el conector no completó el movimiento. Ver B7c |
| Hay transcripciones en Drive y la sesión arranca sin mencionarlas | La sesión se abrió a mano y falta el gancho de B8b, falta `transcripciones.json`, o la copia del lanzador es anterior al 22 de septiembre de 2026. Ver B7 |
| Hay un bloque en curso y la sesión arranca sin ofrecerlo | A la sesión le falta una vía al calendario (ver B8a), falta `calendario.json`, el título del evento no empieza con el nombre de la carpeta seguido de `·`, el evento es de día completo, o la copia del lanzador es anterior al 25 de septiembre de 2026. Ver B8 |
| «En la agenda de hoy» falta en la portada | Falta `calendario.json`, la copia del lanzador es anterior al 15 de octubre de 2026, o faltó el reinicio de B2b. Ver B8e |
| Un evento de hoy sin tarjeta en la agenda | Su título carece del nombre de la carpeta del proyecto seguido de `·`, o la lectura del día es vieja: tocar Actualizar. Ver B8e |
| La sesión crea eventos sin la liga | Falta la sección de B8f en el `CLAUDE.md` global, o el evento lleva invitados de otro dominio, que se queda sin liga a propósito |
| Una junta de la escucha se ofrece en cada sesión | La sesión cerró sin correr el comando `procesada`. Ver B12 |
| Al instalar, cada proyecto ofrece juntas de hace meses | Faltó `sembrar` en una máquina que ya usaba la escucha. Ver B12b |
| La casilla de la junta dice cero capturas | Las capturas se guardan fuera de la carpeta de fábrica: escribir `capturas.json`. Ver B12b |
| La sesión espera el sí de "Gustavo" | La copia del lanzador trae el nombre fijo en la instrucción. Llevarle una corregida con B2b. Ver B8c |
| Un correo de su gente llega y la sesión arranca sin ofrecerlo | Falta `correo.json`, el `CLAUDE.md` del proyecto carece de esa persona o de su empresa, el correo vino del propio dominio del cliente (se deja fuera a propósito), ya trae la etiqueta «Procesado», o la copia del lanzador es anterior al 14 de octubre de 2026. Ver B11 |
| El mismo correo se ofrece en cada sesión | Falta crear la etiqueta «Procesado» en Gmail, o su nombre difiere del de `correo.json`. Ver B11b |
| Las preguntas del arranque salen sueltas, sin casillas | El lanzador sigue corriendo el código viejo: faltó reiniciarlo después de B2b. Ver B11d |
| La factura sigue en rojo con la factura ya emitida | Falta `última factura` con la fecha de la emitida. Tocar Ya la emití, o escribirla en la ficha. Ver A7c |
| Un contrato mensual sin aviso de factura | Le falta la clave `factura`, o trae una forma que el lanzador ignora. Las válidas son `día N del mes` y `primer <día> del mes`. Ver A7c |
| El renglón de GES falta en la tarjeta Hoy | Falta `barrido.json`. Ver B10c |
| GES se queda en "todavía sin correr" | Hoy todavía falta la primera apertura de la raíz del lanzador; recargar una pestaña vieja deja quieto el repaso. Tocar Repasar con GES. Ver B10c |
| La sesión vuelve a pedir la bitácora ya escrita | El `bitacora.py` es anterior al 6 de octubre de 2026, o el `instruccion` propio de `bitacora.json` carece de `{revisado}`. Ver A3c |
| La sesión abierta con `claude` directo arranca sin aviso, y desde el teléfono sí lo trae | Al gancho le falta el `-X utf8`: su salida llega en cp1252 y Claude Code la descarta en silencio. Ver B8b |
| El aviso sale dos veces en la sesión del teléfono | La marca `RC_LANZADOR` se pierde entre el supervisor y `claude.exe`. Es inofensivo; reportarlo para arreglarlo en el lanzador. Ver B8c |
| `Windows is not supported. Use WSL` al instalar Composio | Es lo esperado: en Windows va por el servidor MCP remoto. Ver A5e |
| `soffice` o `tesseract` "no se reconoce" | Se instalan en `Program Files` sin registrarse en el PATH. Ver A4b |
| `module 'socket' has no attribute 'AF_UNIX'` | Se corrió un script auxiliar del plugin, que es solo para Linux. Usar `soffice` directo. Ver A4f |
| `Cannot find module 'docx'` o `'pptxgenjs'` | Falta `NODE_PATH`. Ver A4d |
| El Excel sale con las celdas de resultado vacías | Falta LibreOffice o no se recalculó. `openpyxl` escribe la fórmula pero no la evalúa. Ver A4g |
| El OCR devuelve basura en un documento en español | Falta `spa.traineddata`; el paquete solo trae inglés. Ver A4c |
| `presentacion-elegante` no produce nada útil | Falta el plugin `document-skills`; la skill no tiene a qué delegar. Ver A4e |
