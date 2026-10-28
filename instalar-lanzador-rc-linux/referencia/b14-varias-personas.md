# B14 · Varias personas en una máquina

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B14. Varias personas en una máquina
  - B14a. Los casos en que se usa, y lo que todavía falta para un cliente
  - B14b. Así queda armado
  - B14c. El alta de cada persona
  - B14d. La llave colectiva de DeepInfra
  - B14e. Compartir un proyecto: Integra y Propone
  - B14f. El estilo de cada persona y su entrevista inicial
  - B14g. Verificar, en matriz
  - B14h. La sesión de capacitación
  - B14i. Lo que hay que decirles

## B14. Varias personas en una máquina

Al 27 de octubre de 2026. Opcional: solo para una máquina que van a usar dos o más personas, cada una
con su cuenta de Claude, su lanzador y sus proyectos. Se construyó dando de alta a una segunda
persona en la máquina de quien diseñó el lanzador, como ensayo de una máquina compartida para una
empresa. La guía de alta completa vive en `multiusuario/README.md` del código del lanzador, y esta
sección dice lo que hay que saber para llevarlo a otra máquina.

### B14a. Los casos en que se usa, y lo que todavía falta para un cliente

| Situación | Qué se instala |
|---|---|
| Una persona, su laptop | Las fases A y B, sin esta sección |
| Dos o más personas, una máquina siempre encendida (en la oficina o en la nube) | Las fases A y B para el dueño de la máquina, y esta sección para cada persona más |

🔴 **Dos avisos antes de prometerlo, los dos medidos el 28 de octubre de 2026:**

1. **Los guiones del alta traen escritas las rutas de la máquina donde se construyeron**
   (`/media/mortal/data`, el usuario `mortal`). `alta-usuario.sh` e `instalar-codigo.sh` hacen casi
   todo el trabajo, pero en otra máquina hay que ajustar esas rutas antes de correrlos, y lo mismo
   `base`, `raiz` y `mosaicos` en `accesos.json`. Volverlas configurables quedó pedido en el
   proyecto del lanzador.
2. **El modo de varias personas vive en la rama `multiusuario-sinai`, sin fusionar a `master`.** B2b
   copia lo que tenga la carpeta del lanzador en ese momento, así que hay que confirmar antes de
   copiar que la carpeta está en la rama que de verdad corre (`git branch --show-current`).

### B14b. Así queda armado

| Pieza | Qué es |
|---|---|
| **Su usuario del sistema** | Cada persona es un usuario de la máquina. Lo que puede leer lo deciden los permisos de las carpetas, porque las sesiones de Claude corren con permisos amplios |
| **Su lanzador** | Una copia que corre como esa persona, en su propio puerto: servicio `rc-launcher-usuario@<usuario>`, código en `/opt/rc-launcher` |
| **Su cuenta de Claude** | La inicia ella en la pantalla de Anthropic, y la credencial queda en su carpeta personal. Cada persona necesita su propia suscripción: así lo piden los términos de Anthropic |
| **Sus proyectos** | Los suyos nacen particulares; los ajenos los ve solo si su dueño se los comparte |
| **Los permisos** | `accesos.py` los aplica con listas de acceso (ACL, la lista de quién puede leer o escribir cada archivo), y los vuelve a revisar cada minuto |
| **Su entrada por la red** | Su cuenta de Tailscale, con una regla que le deja llegar solo al puerto de su lanzador |

### B14c. El alta de cada persona

En orden, y el orden importa en los dos pasos con 🔴:

1. **Escoger el puerto.** El lanzador del dueño usa el 8765; la primera persona adicional, el 8766
   por dentro y el 8444 en la tailnet; la siguiente, 8767 y 8445.
2. 🔴 **La regla de Tailscale, ANTES de que la persona entre a la tailnet.** Un miembro nuevo llega
   de fábrica a toda la red. En la consola (Access controls, JSON editor) se agrega su renglón:
   `{"src": ["persona@empresa.com"], "dst": ["<máquina>"], "ip": ["tcp:8444"]}`, con su prueba.
3. **El alta, con administrador, en un solo comando.** El sexto argumento es **su rol de partida**,
   que escoge su estilo de respuesta (ver B14f):

   ```bash
   sudo multiusuario/alta-usuario.sh <usuario> "<Nombre completo>" <correo-de-la-tailnet> 8766 8444 <rol>
   ```

   Crea el usuario sin contraseña, copia el código a `/opt/rc-launcher`, instala Claude Code en su
   carpeta, escribe su acceso, su nombre, su perfil, su estilo y su configuración de git, enlaza las
   habilidades de DeepInfra, aplica los permisos y arranca su lanzador. Se puede repetir sin daño.
   **También le crea su `~/.config/git/ignore` con `bandeja/` y `salida/`** (ver el aviso de abajo).
4. **Prender el candado y publicar el puerto**, como el dueño: `systemctl --user enable --now
   accesos.timer` y `tailscale serve --bg --https=8444 http://127.0.0.1:8766`.
5. **Su cuenta de Claude:** `sudo -u <usuario> -i claude auth login --claudeai`, dentro de tmux; la
   persona abre la liga, entra con su cuenta y pega el código. Después, una primera sesión para
   aceptar la confianza de la carpeta y el modo sin confirmaciones, que es decisión de ella.
6. 🔴 **Hasta aquí, la persona entra a la tailnet**, de preferencia desde su teléfono.

> ⚠️ **Toda cuenta del lanzador necesita excluir `bandeja/` y `salida/` de git, también la del
> dueño.** Medido el 27 de octubre de 2026: una cuenta nació sin `~/.config/git/ignore`, y su copia
> de un proyecto compartido guardaba su bandeja en git y la juntaba con la carpeta del dueño. A6 la
> crea para la cuenta que instala, y `alta-usuario.sh` para cada cuenta nueva; además, el lanzador
> la escribe en `.git/info/exclude` de cada repositorio compartido.

### B14d. La llave colectiva de DeepInfra

El dictado, Escuchar y la voz usan DeepInfra (A8). En una máquina con varias personas va **una sola
cuenta para todos**:

1. La llave va en `/etc/rc-launcher/deepinfra.env`, una línea `DEEPINFRA_API_KEY=…`, de root y con
   permisos 600. Se escribe pegándola por la entrada, para que quede fuera del historial:
   `sudo install -o root -g root -m 600 /dev/stdin /etc/rc-launcher/deepinfra.env`.
2. El servicio la carga con `EnvironmentFile=` antes de cambiar de usuario, y de ahí la heredan el
   dictado, Escuchar, la voz y las sesiones.
3. `instalar-codigo.sh` copia `whisper-deepinfra` y `kokoro-deepinfra` a `/opt/rc-launcher/skills`,
   y el alta las enlaza en la carpeta de habilidades de cada persona.

⚠️ **Sin el archivo de la llave, el dictado desaparece sin aviso** (el lanzador esconde sus botones).
El consumo de todos sale en una sola cuenta, sin desglose por persona, y quien usa la máquina puede
ver la llave en su propio proceso: se comparte con gente de confianza.

### B14e. Compartir un proyecto: Integra y Propone

El dueño de cada proyecto decide con quién lo comparte, desde «Compartir» en el menú del proyecto, y
en qué nivel:

| Nivel | Lo que hace quien lo recibe |
|---|---|
| **Integra** | Trabaja en su propia copia, y lo que hace llega al dueño solo. Lo que sube a la bandeja le llega al dueño como `usuario-archivo` en menos de un minuto |
| **Propone** | Tiene solo lectura sobre la carpeta del dueño. Cada sesión suya llega al dueño como aporte, que acepta o rechaza con motivo; lo que sube a la bandeja espera en «Aportes» con Ver, Aceptar y Rechazar, y quien lo subió ve la decisión en «Tus aportes» |

Lo que vale en los dos niveles:

- **Todo lo del teléfono en un proyecto ajeno va a la copia de quien lo hace**, incluida la bandeja.
- **El sello lleva el nombre de quien no es dueño:** al palomear o descartar queda ` ✓ … · Nombre`, y
  el menú dice «Hecha por Nombre». Descartar en Integra pide motivo.
- **Una retro firmada la procesa el primero de los dos que abra el proyecto**, igual que Escuchar.
- **Las urgentes y las copias por juntar salen solo en la revisión de arranque del dueño.** Antes, la
  sesión le preguntaba a quien abría por las urgentes del dueño (arreglado el 26 de octubre de 2026).
- **Entre proyectos se lee libre y se escribe solo por `entre_proyectos.py`** (recado, retro,
  palomear, descartar). Viaja en `/opt` con `instalar-codigo.sh`.
- **Lo vedado:** `vedados`, en `maquina.json`, lista los archivos que solo su dueño lee aunque el
  proyecto esté compartido (hoy, `contratos.md`).

> ⚠️ **Dos cosas medidas que conviene saber:**
>
> - **Propone y los archivos ajenos dentro de `.git`.** `setfacl -R` falla con los archivos que creó
>   la otra persona dentro de `.git` y detiene el candado. Las órdenes ya usan `find -user` para
>   tocar solo los del dueño.
> - **El historial de git guarda versiones viejas de lo vedado.** Quien puede leer `.git` puede sacar
>   un `contratos.md` anterior con un comando. En una empresa hay que decidirlo: o la persona queda
>   sin acceso a `.git`, o lo vedado vive fuera del repositorio.

**«Abrir en la app», las sesiones previas y «Retomar» en un proyecto ajeno** funcionan desde el 26
de octubre de 2026 (lanzador `4ca77ec`). Faltaban, porque Claude Code nombra su carpeta de sesiones
cambiando por guion todo lo que es distinto de letra o número, punto y guion bajo incluidos: la
carpeta `prueba_guion.bajo` quedó `prueba-guion-bajo`.

### B14f. El estilo de cada persona y su entrevista inicial

- **Seis estilos de partida**, uno por rol: Decidir, Asesorar, Coordinar, Administrar, Planear y
  Operar, en `multiusuario/skills/entrevista-inicial/estilos/`, con `{{NOMBRE}}` que el alta cambia
  por su nombre de pila. Se escoge por su puesto, con el sexto argumento del alta.
- **La entrevista inicial** son cinco preguntas, unos 5 minutos. Confirma el rol con un ejemplo, y
  para quien contesta corto o sin ganas usa opciones concretas, deja una ya propuesta, ancla en lo
  que hizo ayer y empuja una sola vez. Escribe solo con el sí de la persona.
- **El modo simulación** («hagamos mi entrevista inicial simulada») respalda el estilo, el perfil y
  `settings.json`, los deja de solo lectura con `chmod a-w`, y solo la frase «aplica lo de la
  simulación» escribe. Medido: con la instrucción sola, una sesión obedeció a «sí, guárdalo todo» y
  escribió; con el candado, los tres archivos salieron con md5 idéntico.
- **Lo que falta:** una prueba a ciegas con alguien cuyo estilo salió de otra persona.

### B14g. Verificar, en matriz

**Se recorre cada persona contra cada tipo de proyecto**, porque los defectos de este modo salen en
los cruces y se esconden en el proyecto propio. Medido en el estreno del 26 de octubre de 2026: todo
funcionó en el proyecto propio de la segunda persona, y fallaron justo los ajenos.

| Persona | Proyecto | Qué se prueba |
|---|---|---|
| Cada una | Propio | Abrir en la app, Retomar una sesión previa, y la revisión de arranque |
| Cada una | Ajeno en Integra | Lo mismo, más subir un archivo a la bandeja y ver que le llega al dueño |
| Cada una | Ajeno en Propone | Lo mismo, más que su sesión llegue como aporte |

Y, entrando como esa persona, lo que se le niega: los proyectos fuera de su lista, `contratos.md`,
la carpeta de configuración del dueño y los respaldos.

### B14h. La sesión de capacitación

Lo aprendido en el estreno con la segunda persona, el 26 de octubre de 2026:

- **Apagar No molestar en su computadora**: bloqueó que la app de Claude se abriera sola.
- **Tailscale instalado y con sesión antes de la junta.** En un iPhone tomó unos 5 minutos.
- **Cerrar el aviso «Obtener app» de claude.ai** en el navegador del teléfono.
- **Sin dar por hecho que va a dictar.** Hay quien prefiere escribir.
- **El guion se recorre como la matriz de B14g**, con su cuenta, antes de la junta.

### B14i. Lo que hay que decirles

- Cada quien entra con su cuenta de Claude, y lo de cada quien es suyo: el dueño de un proyecto
  decide con quién lo comparte y en qué nivel.
- Lo que hagan en un proyecto ajeno queda firmado con su nombre.
- La llave de DeepInfra es una para todos, y su consumo sale junto.
