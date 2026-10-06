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

> 📌 **A4 se verificó recreando la VM desde cero y corriendo la sección tal como quedó
> escrita**, no reconstruyéndola de una exploración previa. **Las cinco pruebas de aceptación
> pasaron**, incluida la quinta: una sesión real pidió una presentación ejecutiva de cuatro
> láminas, la generó, **corrió el ciclo de revisión visual y corrigió tres defectos de
> maquetación que ella misma detectó** en las imágenes renderizadas. Es la evidencia de que el
> runtime no solo está instalado sino bien cableado.

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
| **Al abrir una sesión, lo que urge sale numerado** (requiere la fase B) | Si hay pendientes vencidos o que vencen en la semana, la sesión los lista con número y pregunta cuáles ya están hechos. Se contesta con los números y ella palomea los demás |
| **Sus contactos, al día** | Las personas que aparecieron en la sesión, con su correo o su teléfono, quedan al cerrar en un archivo de contactos listo para importar a Google Contacts |
| **Lo que deja de cobrar, a la vista** (opcional, requiere la fase B) | Cada proyecto lleva sus contratos en un archivo, y la pantalla Contratos del lanzador suma lo que vence y avisa cuándo buscar al siguiente cliente |
| **Datos a la mano durante una junta** (opcional, requiere la fase B, todavía en prueba) | El teléfono escucha la conversación y en la misma pantalla van saliendo tarjetas con respuestas, datos y compromisos. Ver B9 antes de ofrecerlo |
| **Transcribir juntas y escuchar documentos** (opcional, con cuenta propia) | Sube la grabación de una junta y pide la minuta, o pide que le lean un documento para el camino |
| **El audio se escucha con un clic** (requiere la fase B) | Lo que pidió que le leyeran llega como liga: le pica desde el teléfono y suena, sin descargarlo ni buscarlo en el navegador de archivos |
| **Le avisa cuando una tarea termina** (requiere la fase B) | El teléfono suena cuando Claude Code deja de trabajar y se queda esperando, con el nombre del proyecto, qué hizo, y una liga que abre esa misma sesión de un toque. Cubre el hueco que deja la aplicación de Claude, que avisa cuando hay algo que contestar y se calla cuando el trabajo simplemente terminó |
| **Dejar dicho qué resultó, sin abrir sesión** (requiere la fase B) | Desde el teléfono, en cada pendiente hay un botón para dictar cómo quedó, y una sección aparte para los recados sueltos del proyecto, los que valen por sí mismos. Se dicta con el teclado del teléfono, así que cuesta cero llamadas al modelo, y la siguiente sesión se entera sola de que hay algo sin leer. **La lista se queda donde estaba al guardar**, para poder recorrerla de corrido |
| **Las transcripciones de sus grabaciones llegan solas** (opcional, requiere la fase B) | Al abrir una sesión desde el teléfono, el asistente revisa la carpeta de Drive donde caen las transcripciones, le dice en un renglón cuáles son de ese proyecto y pregunta si las procesa. Con un sí, quedan guardadas en el proyecto y lo que salga de ellas llega a sus pendientes |
| **La sesión le ofrece el bloque de su agenda** (opcional, requiere la fase B) | Si reservó en el calendario un bloque para ese proyecto y está en curso o empieza en media hora, la sesión se lo resume en dos renglones al abrir y pregunta si lo atienden. Pasa igual si abre la sesión desde el teléfono o en la computadora |

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
| El correo del cliente permite apps de terceros | que **él mismo** entre a `claude.ai/customize/connectors` e intente conectar su calendario | Si su administrador de Google Workspace o Microsoft 365 tiene bloqueadas las apps de terceros, **no hay rodeo técnico**: es conversación con su área de sistemas. Descubrirlo aquí cuesta un minuto; descubrirlo en la cita cuesta la sesión |

> 📌 **Por qué ese renglón del correo está aquí y no en A5, que es donde se conecta.** Es la
> misma lógica que Tailscale: **lo que depende del área de sistemas del cliente es una barrera
> de calificación, no un paso de instalación.** Y no es hipotético — el primer piloto se quedó
> parado semanas esperando que un departamento externo devolviera un archivo. Además de correo
> y calendario, de ahí depende que el cierre automático pueda poner al día sus bloques (A7).

---

# FASE A · La base

**Lo que deja instalado:** Claude Code funcionando, la carpeta de proyectos, la bitácora
automática, el runtime que necesitan las skills de documentos, y el acceso a su correo,
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
| B8 | [`referencia/b8-calendario-al-arrancar.md`](referencia/b8-calendario-al-arrancar.md) | El bloque de calendario al arrancar (opcional) |
| B9 | [`referencia/b9-escucha-en-vivo.md`](referencia/b9-escucha-en-vivo.md) | La escucha en vivo durante una junta (opcional, en prueba) |

---

## 7. Verificación, en orden

La lista completa de comprobaciones vive en [`referencia/verificacion.md`](referencia/verificacion.md).
**No se entrega una máquina sin recorrerla entera**, en ese orden, porque cada renglón da por
hecho que el anterior pasó.

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
| La primera sesión se queda colgada | Claude Code no pasó por su primer arranque; está detenido en una de las cinco preguntas, sin ventana donde verlas. Ver A2 |
| Un proyecto nuevo se cuelga la primera vez, incluso con la raíz confiada | Si pasa con TODOS los proyectos nuevos: la confianza se aceptó dentro de un proyecto y no en la raíz `~/claude`, no se hereda (ver A2). Si es solo el primero de un proyecto creado desde "+ Nuevo proyecto": es normal, contestar desde el teléfono o adelantarlo abriendo la primera sesión desde la computadora (ver B2) |
| Un proyecto que llevaba meses trabajando empieza a pedir la confianza | Le corrieron `git init`, y la herencia se corta en la raíz de cada repositorio. El flag de permisos omitidos tampoco lo salta. Se siembra la llave con el fragmento de A2 |
| Se le pidió a un agente que hiciera el primer arranque y se quedó a medias | A2 no se puede delegar; exige a una persona con la sesión al frente, sobre todo para la pregunta 4. Ver A2 |
| Aparece "acepta toda la responsabilidad" y nadie sabe si contestar | Es la pregunta 4 de A2 (modo sin confirmaciones); solo la acepta el dueño de la máquina, en persona. Ver A2 |
| La bitácora nunca escribe y no avisa | `raiz_proyectos` apunta a una carpeta que no existe |
| "Le pedí la bandeja y me habló de Gmail" | Falta la sección "La bandeja" de B5 en `~/.claude/CLAUDE.md` |
| "Le pedí sus pendientes y no sabe qué son" | Falta la sección de A7 en `~/.claude/CLAUDE.md` |
| Los conectores no aparecen en `/mcp` | La sesión no está autenticada con la suscripción. Correr `/status`. Ver A5b |
| No deja conectar Gmail desde `/mcp` | Es lo esperado: va en claude.ai, no en la terminal. Ver A5a |
| El borrador salió sin el archivo adjunto | Limitación vigente del conector; se adjunta a mano antes de enviar. Ver A5c |
| Pide una llave de DeepInfra que el cliente no esperaba | No se le explicó A8 en la entrega. Es opcional y con su propia cuenta; explicarle y seguir cuando la tenga |
| La misma transcripción se ofrece en cada sesión | No se movió a `Procesadas`: la subcarpeta falta, se llama distinto, o el conector no completó el movimiento. Ver B7c |
| Hay transcripciones en Drive y la sesión arranca sin mencionarlas | La sesión se abrió a mano y falta el gancho de B8b, falta `transcripciones.json`, o la copia del lanzador es anterior al 22 de septiembre de 2026. Ver B7 |
| Hay un bloque en curso y la sesión arranca sin ofrecerlo | A la sesión le falta una vía al calendario (ver B8a), falta `calendario.json`, el título del evento no empieza con el nombre de la carpeta seguido de `·`, el evento es de día completo, o la copia del lanzador es anterior al 25 de septiembre de 2026. Ver B8 |
| La sesión espera el sí de "Gustavo" | La copia del lanzador trae el nombre fijo en la instrucción. Llevarle una corregida con B2b. Ver B8c |
| `unzip is required to install Composio CLI` | Falta `unzip`; está en A1 |
| `Cannot find module 'docx'` o `'pptxgenjs'` | Falta `NODE_PATH`. Están instalados global, pero `require()` no los ve desde otra carpeta. Ver A4d |
| `Could not load the "sharp" module` | Node 18 de los repos de Ubuntu. `sharp` pide 20.9 o mayor. Ver A4b |
| `externally-managed-environment` al instalar con pip | Falta `--user --break-system-packages`. Ver A4c |
| El Excel sale con las celdas de resultado vacías | Falta LibreOffice, o no se pasó por `recalc.py`. `openpyxl` escribe la fórmula pero no la evalúa. Ver A4f |
| El OCR devuelve basura en un documento en español | Falta `tesseract-ocr-spa`; el paquete base solo trae inglés. Ver A4a |
| `presentacion-elegante` no produce nada útil | Falta el plugin `document-skills`; la skill no tiene a qué delegar. Ver A4e |
