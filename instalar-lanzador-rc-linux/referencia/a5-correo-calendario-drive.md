# A5 · Conectores de correo, calendario y Drive, y Composio

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A5. Su correo, su calendario y su Drive
  - A5a. Conectarlos
  - A5b. Verificar
  - A5c. Qué decirle al cliente, antes de que lo descubra él
  - A5d. Cómo apagarlos
  - A5e. Composio, para lo que los conectores no alcanzan (recomendado)

<!-- fin del encabezado agregado al partir -->

## A5. Su correo, su calendario y su Drive


**Lo que deja funcionando:** que pueda decir "¿qué me escribió el broker esta semana?" o
"agéndame con él el martes" y la sesión lo resuelva sin que él salga de la conversación.

> 📌 **El conector de calendario hace doble trabajo.** Además de esto, es lo que le permite
> al cierre automático de la bitácora (A3) dejar al día los bloques que la sesión movió. Si
> este paso se salta, esa mitad del cierre sencillamente no existe, y **no avisa**.

Se hace con los **conectores de claude.ai**, no instalando nada en la máquina. La cuenta que
ya se autenticó en A2 es la misma que los trae, así que **no hay proyecto de nube que crear,
ni credenciales que administrar, ni permisos que pedirle a nadie.**

> 📌 **Por qué esta vía y no un CLI de Google.** La alternativa era instalar un CLI con su
> propio proyecto de Google Cloud por cliente. Se descartó a propósito: **exige que el cliente
> tenga acceso a Google Cloud, y la mayoría no lo tiene**, así que convertía una capacidad
> vendible en un trámite con su área de sistemas. Además esta vía **sirve igual si están en
> Microsoft 365**, que el CLI de Google no cubriría.

### A5a. Conectarlos

**Este paso lo hace el cliente, en su navegador, y no se puede hacer desde la terminal.**

1. Entrar a **`claude.ai/customize/connectors`** con la misma cuenta de A2.
2. Conectar los que apliquen: **Gmail**, **Google Calendar**, **Google Drive**, o
   **Microsoft 365** si su correo es de Microsoft.
3. Completar el consentimiento que pida cada uno.

> ⚠️ **No intentar conectarlos desde `/mcp`, no se puede, y el error confunde.** Gmail,
> Google Calendar y Microsoft 365 **no soportan el OAuth local de Claude Code**, porque el
> proveedor de identidad solo acepta la dirección de retorno que registró claude.ai. Si se
> intenta, la propia herramienta manda a Configuración → Conectores. **No es una falla de la
> instalación.**

> ⚠️ **En planes Team y Enterprise, solo un administrador puede agregar conectores.** Si el
> cliente está en uno de esos y no es administrador, este paso lo tiene que hacer su área de
> sistemas. **Vale preguntarlo en el paso 0**, no descubrirlo con él sentado enfrente.

### A5b. Verificar

Desde la terminal, sin abrir una sesión:

```bash
claude mcp list
```

Deben aparecer con nombre de claude.ai, por ejemplo `claude.ai Gmail`, `claude.ai Google
Calendar` y `claude.ai Google Drive`, todos en `Connected`. Dentro de una sesión, `/mcp` los
lista marcados como provenientes de claude.ai.

> 🔴 **Si no aparecen, casi siempre es el método de autenticación, no el conector.** Los
> conectores **solo se cargan cuando la sesión está autenticada con la suscripción de
> claude.ai**. No se cargan si está activa alguna de estas: `ANTHROPIC_API_KEY`,
> `ANTHROPIC_AUTH_TOKEN`, un `apiKeyHelper`, un proveedor de terceros como Bedrock o Vertex, o
> un `CLAUDE_CODE_OAUTH_TOKEN` generado con `claude setup-token`.
>
> **Diagnóstico:** correr **`/status`** dentro de una sesión para ver cuál está activa. Si es
> una de esas, quitar la variable de entorno o el ajuste, y correr `/login` para elegir la
> cuenta de claude.ai.
>
> **Ojo con esto al montar el arranque automático de la fase B:** si el servicio que lanza las
> sesiones exporta una llave de API, el cliente pierde sus conectores **solo en las sesiones
> lanzadas desde el teléfono**, que es donde menos lo va a entender. Dejar el servicio sin
> esas variables.

### A5c. Qué decirle al cliente, antes de que lo descubra él

**Esto no es opcional, y conviene decirlo en la sesión de entrega**, porque son límites que se
descubren tarde y en mal momento:

- **Los borradores no llevan archivo adjunto.** La herramienta lo declara como limitación
  vigente. Si necesita mandar un adjunto, el borrador se prepara y **él le adjunta el archivo
  a mano antes de enviar**.
- **Verificar cómo queda una respuesta antes de confiarle un hilo importante.** Conviene
  probarlo con un correo propio la primera vez: que llegue dentro de la conversación y no como
  correo suelto.
- **Nada se envía solo.** El flujo natural es dejar el borrador y que él lo revise y lo mande.
  Es una limitación que juega a favor, y vale enmarcarla así.
- **Su organización puede bloquear herramientas.** En planes de empresa, un administrador
  puede marcar una herramienta como bloqueada o de aprobación obligatoria, y Claude Code lo
  respeta. Si algo "no funciona" solo para él, revisar `/mcp`.

### A5d. Cómo apagarlos

Si el cliente quiere que una máquina no vea sus conectores, en `settings.json`:

```json
{ "disableClaudeAiConnectors": true }
```

Basta un `true` en cualquier nivel de configuración para que ganen; un `false` de proyecto no
revierte un `true` de usuario. Para bloquear solo uno, va por nombre en `deniedMcpServers`
(por ejemplo `"claude.ai Gmail"`). Y para apagarlos en una sola corrida:
`ENABLE_CLAUDEAI_MCP_SERVERS=false claude`.

### A5e. Composio, para lo que los conectores no alcanzan (recomendado)

**Lo que deja funcionando:** correos **con archivo adjunto**, que el conector de claude.ai
todavía no permite, y acceso a **más de mil aplicaciones** además de Google y Microsoft. Cada
aplicación se autoriza una vez, en el navegador, y a partir de ahí la sesión la usa sola a
partir de una petición normal ("mándale al broker el contrato anexo").

**Composio (`composio.dev`) es un servicio externo que guarda los permisos de acceso del
cliente a cada aplicación y ejecuta las acciones en su nombre.** Es lo que se le recomienda al
cliente para sus conexiones, porque le ahorra el trámite de credenciales que antes obligaba a
pasar por Google Cloud o por su área de sistemas.

> 📌 **Se suma a A5 y lo deja en su lugar, por una razón concreta:** el cierre automático de la
> bitácora (A3) reconoce el calendario **por el nombre de las herramientas del conector de
> claude.ai** (es lo que mide el renglón de verificación del calendario). Si el calendario
> quedara solo en Composio, esa mitad del cierre dejaría de funcionar sin avisar. Así que
> Gmail, Calendar y Drive se quedan conectados por A5, y Composio entra para lo demás.

> ✅ **Probado el 18 de septiembre de 2026 en una Ubuntu recién instalada**, con la cuenta del
> dueño de la máquina: una sesión, a partir de una petición en lenguaje normal, dejó un
> borrador **dentro de su hilo** con un PDF adjunto **idéntico byte por byte** al original
> (verificado leyendo el correo crudo). El adjunto llega marcado como
> `application/octet-stream` y no como PDF; Gmail lo abre igual.

**Instalación, con el instalador oficial.** Pide `unzip`, que A1 ya dejó instalado; en una
Ubuntu limpia sin él falla con `unzip is required to install Composio CLI`.

```bash
curl -fsSL https://composio.dev/install | bash
exec bash -l            # para que la terminal vea el comando nuevo
composio --version
composio login          # abre el navegador: la cuenta de Composio es DEL CLIENTE
```

Después se autoriza cada aplicación que el cliente quiera usar, una por una. Cada comando
abre el navegador para el consentimiento:

```bash
composio link gmail
composio link googledrive
```

Verificación, dejando intacto lo del cliente:

```bash
composio search "send an email with an attachment" --toolkits gmail --limit 1
```

Debe regresar una herramienta de Gmail. Y la prueba que importa, con el cliente enfrente:
pedirle a una sesión que se deje a sí mismo un borrador con un PDF adjunto, y abrir el
borrador en Gmail para ver el archivo.

> ⚠️ **El instalador también intenta registrar un complemento para Claude Code**, y en una de
> las dos máquinas donde se probó ese registro falló sin detener la instalación. Da igual: la
> sesión usa el comando `composio` directo, que ya queda en `~/.local/bin` y el servicio del
> lanzador ve en su `PATH` (B3). Si el complemento falla, se reintenta con
> `composio setup --target auto --yes`.

**Lo que hay que decirle al cliente, junto con A5c y A8c:** 🔴 **Composio guarda el permiso
de acceso a sus cuentas, y cada acción pasa por sus servidores.** Es la misma clase de aviso
que DeepInfra con el audio, más pesado, porque aquí es su correo. La cuenta es suya y la
conexión se revoca en cualquier momento desde el tablero de Composio o desde la seguridad de
su cuenta de Google. **Revisar el plan vigente en `composio.dev` antes de la entrega**, para
decirle si su uso cabe en el gratuito.
