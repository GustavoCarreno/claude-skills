# A10 · Los perfiles del equipo

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- A10. Los perfiles del equipo
  - A10a. Qué son, y por qué se entregan aparte
  - A10b. Copiarlos
  - A10c. Dejar Gabinete como postura por defecto
  - A10d. Verificar
  - A10e. Lo que hay que decirle
  - A10f. Las reglas de redacción y sus barridos

<!-- fin del encabezado agregado al partir -->

## A10. Los perfiles del equipo

### A10a. Qué son, y por qué se entregan aparte

Ocho perfiles que el asistente se pone según el tema, cada uno con lo que un área de empresa sabe
revisar, preguntar y entregar: **GAB** (Gabinete), **GES** (Gestión), **PAS** (Procesos), **MID**
(Mercadotecnia), **ISI** (Infraestructura), **DAS** (Desarrollo), **CYF** (Finanzas, el criterio de dinero; se sumó el 16 de octubre de 2026) y **Tavo** (Tecnología Aplicada con Visión
Organizacional, todos en mesa; se llamó TAO hasta el 16 de octubre de 2026). Gabinete queda como la postura por defecto en todos los proyectos.

📌 **Los perfiles NO viven en este repositorio, que es público.** Son el método de trabajo de quien
instala, y los trae él en cada instalación: la carpeta `perfiles/` de su repositorio privado, con
la versión base y la **ficha del cliente** (`contexto.md`) ya llenada. Esta sección dice cómo se
instalan; el contenido llega con quien instala.

Antes de copiarlos, **el cliente escoge cuáles le sirven.** Conviene que sobre alguno a que falte.

### A10b. Copiarlos

Con la carpeta de perfiles en la máquina del cliente (por `scp`, USB o como se haya traído), en
`$ORIGEN`, y el nombre de la carpeta de su ficha en `$CLIENTE`:

```bash
ORIGEN=~/perfiles          # donde quedó la carpeta perfiles/ que trajo quien instala
CLIENTE=nombre-del-cliente # la carpeta de su ficha, dentro de perfiles/clientes/
mkdir -p ~/.claude/skills
# Una instalación anterior trae el equipo completo como equipo-tao: se aparta, con su ficha
[ -d ~/.claude/skills/equipo-tao ] && mv ~/.claude/skills/equipo-tao ~/.claude/equipo-tao-anterior
cp -r "$ORIGEN"/base/equipo-* ~/.claude/skills/
cp "$ORIGEN/clientes/$CLIENTE/contexto.md" ~/.claude/skills/equipo-tavo/contexto.md
ls -d ~/.claude/skills/equipo-*
```

Para quitar un perfil que el cliente no quiso, se borra su carpeta (por ejemplo
`rm -r ~/.claude/skills/equipo-mid`) y su renglón en la ficha. **Tavo y su ficha se quedan siempre**,
porque los demás leen la ficha desde ahí.

### A10c. Dejar Gabinete como postura por defecto

Se agrega un bloque al `CLAUDE.md` global del cliente. El bloque trae marcas de inicio y fin, y el
fragmento **quita primero el bloque anterior y pone el nuevo**, así que correrlo dos veces deja uno
solo, y una máquina que ya tenía los perfiles recibe la lista al día (con CYF, desde el 16 de
octubre de 2026):

```bash
touch ~/.claude/CLAUDE.md
sed -i '/perfiles-del-equipo: inicio/,/perfiles-del-equipo: fin/d' ~/.claude/CLAUDE.md
cat "$ORIGEN/base/postura-gabinete.md" >> ~/.claude/CLAUDE.md
grep -c "perfiles-del-equipo" ~/.claude/CLAUDE.md   # debe dar 2
```

### A10d. Verificar

| Prueba | Qué se espera |
|---|---|
| En una sesión nueva, escribir `¿qué opina Gestión de lo que tengo pendiente?` | El primer renglón dice «Responde Gestión (GES)» y la respuesta usa los términos de su ficha |
| Escribir `¿en qué debo estar hoy?` | Contesta Gabinete, con recomendación, sin anunciarse |
| Escribir `revísalo con Tavo` sobre cualquier decisión | Una sección por área y cierra con preguntas para el cliente |
| En una sesión nueva, pedir un correo de prueba a un proveedor | Sale pidiendo con tacto, y la sesión corre `servicio.py` sobre el texto antes de dejarlo en Borradores |

Si un perfil se queda callado, la causa casi siempre es la carpeta: tiene que ser
`~/.claude/skills/equipo-ges/SKILL.md`, con el `SKILL.md` adentro de su carpeta.

### A10e. Lo que hay que decirle

- Les habla por su nombre o su apodo: *«¿qué opina Gestión?»*, *«pásalo por Procesos»*,
  *«revísalo con Tecnología»*. Si no los llama, entran solos cuando el tema es suyo.
- **La ficha es suya**: si cambia de puesto, de jefe o de forma de trabajar, se le pide al
  asistente que la ponga al día.
- Todo lo que va a un tercero pasa antes por su visto bueno, y los correos quedan en Borradores.
- **Cuando corrija cómo escribe su asistente**, la corrección se queda como regla con su fecha, y si
  se repite entra a la lista del barrido. Puede pedirlo así: *«que no se vuelva a repetir»*.

### A10f. Las reglas de redacción y sus barridos

Al 28 de octubre de 2026. Tres piezas que viajan en la misma carpeta `perfiles/base/`:

| Pieza | Qué es | Dónde queda |
|---|---|---|
| `reglas-redaccion.md` | Las reglas del método: se pide y no se ordena, preguntas con signos, sin jerga o definida, sin frases hechas, cero dobles negativos, guion con cada referencia ligada, cuándo correr los barridos y el ciclo de corrección | Al final del `CLAUDE.md` global, con marcas |
| `reglas-regionales-norte.md` | «Si te acomoda» y el doble sentido, para quien escribe a gente del norte de México. **Se pregunta al cliente** si las quiere | Igual, con sus propias marcas |
| `barridos/` | `servicio.py` (tono mandón) y `albures.py` (doble sentido), con sus listas de frases en `servicio-frases.txt` y `albures-frases.txt`, que el cliente puede ampliar | `~/.claude/barridos/` |
| `reglas-catalogo.md` | Las reglas personales que se le ofrecen en la entrevista inicial (horas en am y pm, «buen día», sin rayas largas, la familia con mayúscula, estadounidense) | `~/.claude/reglas-catalogo.md` |

El fragmento **quita primero los bloques anteriores y pone los nuevos**, así que correrlo dos veces
deja uno de cada uno, y **conserva las listas de frases que el cliente ya amplió**. Con ``$ORIGEN`` de A10b:

```bash
NORTE=si                   # "si" agrega las reglas del norte de México; "no" las deja fuera
mkdir -p ~/.claude/barridos
cp "$ORIGEN"/base/barridos/*.py ~/.claude/barridos/
for f in "$ORIGEN"/base/barridos/*-frases.txt; do   # las listas que el cliente ya amplió se conservan
  [ -f ~/.claude/barridos/"$(basename "$f")" ] || cp "$f" ~/.claude/barridos/
done
cp "$ORIGEN/base/reglas-catalogo.md" ~/.claude/reglas-catalogo.md
touch ~/.claude/CLAUDE.md
sed -i '/reglas-de-redaccion: inicio/,/reglas-de-redaccion: fin/d;/reglas-regionales-norte: inicio/,/reglas-regionales-norte: fin/d' ~/.claude/CLAUDE.md
cat "$ORIGEN/base/reglas-redaccion.md" >> ~/.claude/CLAUDE.md
[ "$NORTE" = si ] && cat "$ORIGEN/base/reglas-regionales-norte.md" >> ~/.claude/CLAUDE.md
grep -c "reglas-de-redaccion\|reglas-regionales-norte" ~/.claude/CLAUDE.md   # 4 con el norte, 2 sin él
python3 ~/.claude/barridos/servicio.py --probar && python3 ~/.claude/barridos/albures.py --probar
```

✅ **Medido el 28 de octubre de 2026** con una carpeta personal desechable: dos corridas dejan un solo
bloque de cada uno, una frase agregada a `servicio-frases.txt` sobrevive la segunda corrida, y los dos
`--probar` contestan «sabe fallar: sí».
