# B14 · Varias personas en una máquina

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B14. Varias personas en una máquina
  - B14a. Lo que hay hoy en Windows
  - B14b. El estilo de partida, a mano
  - B14c. Lo que falta medir en `win11-dogfood`

## B14. Varias personas en una máquina

Al 27 de octubre de 2026. El modo de varias personas (cada una con su usuario, su cuenta de Claude,
su lanzador y sus proyectos, y los niveles Integra y Propone para compartir) **se construyó y se
midió en Linux**. La sección completa está en la B14 de la guía `instalar-lanzador-rc-linux`.

### B14a. Lo que hay hoy en Windows

🔴 **Windows todavía carece del alta de varias personas.** `alta-usuario.sh`, `instalar-codigo.sh` y el
candado de permisos de `accesos.py` son de Linux: usan usuarios del sistema, systemd y las listas de
acceso de Linux (ACL), que en Windows funcionan distinto. O sea que **Propone, que depende de dar
solo lectura sobre la carpeta del dueño, todavía falta en Windows.** Para una empresa con varias
personas en una máquina, hoy la recomendación es una máquina con Linux.

Lo que sí vale en una laptop con Windows y una sola persona, y viaja con B2b:

- **La entrevista inicial de cinco preguntas** y sus seis estilos por rol (Decidir, Asesorar,
  Coordinar, Administrar, Planear y Operar).
- **Excluir `bandeja/` y `salida/` de git**, que A6 ya deja hecho para la cuenta que instala.

### B14b. El estilo de partida, a mano

Sin el alta, el rol se escoge copiando la plantilla y poniendo su nombre de pila. En PowerShell, con
`$Rol` y `$Pila`, leyendo y escribiendo en UTF-8 sin marca de orden de bytes:

```powershell
$Rol  = "decidir"     # decidir, asesorar, coordinar, administrar, planear u operar
$Pila = "Nombre"
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$Origen = "$HOME\rc-launcher\multiusuario\skills\entrevista-inicial\estilos\$Rol.md"
New-Item -ItemType Directory -Force -Path "$HOME\.claude\output-styles" | Out-Null
$Texto = [IO.File]::ReadAllText($Origen, $Utf8).Replace("{{NOMBRE}}", $Pila)
[IO.File]::WriteAllText("$HOME\.claude\output-styles\$Pila.md", $Texto, $Utf8)
```

Y en `$HOME\.claude\settings.json`, la clave `"outputStyle"` con su nombre de pila, que es el `name:`
que la plantilla trae como `{{NOMBRE}}`: `"outputStyle": "Nombre"`. La plantilla viaja con B2b, que
copia el árbol completo del lanzador, incluida la carpeta `multiusuario\`.

### B14c. Lo que falta medir en `win11-dogfood`

- **El fragmento de B14b**, corrido en la VM con una sesión nueva que conteste con el estilo.
- **El modo simulación de la entrevista.** En Linux el candado es `chmod a-w`; en Windows el
  equivalente es `attrib +R` (y `attrib -R` al terminar), y la habilidad hoy trae solo el comando
  de Linux.
- **Las sesiones previas con una ruta con punto.** Claude Code cambia por guion todo lo que es
  distinto de letra o número; en Windows la regla vieja ya cambiaba los dos puntos de la unidad.
- **La cuenta de Claude**, ver B13.
