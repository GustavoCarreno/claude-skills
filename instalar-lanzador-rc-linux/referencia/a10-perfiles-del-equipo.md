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

<!-- fin del encabezado agregado al partir -->

## A10. Los perfiles del equipo

### A10a. Qué son, y por qué se entregan aparte

Siete perfiles que el asistente se pone según el tema, cada uno con lo que un área de empresa sabe
revisar, preguntar y entregar: **GAB** (Gabinete), **GES** (Gestión), **PAS** (Procesos), **MID**
(Mercadotecnia), **ISI** (Infraestructura), **DAS** (Desarrollo) y **TAO** (Tecnología, todos en
mesa). Gabinete queda como la postura por defecto en todos los proyectos.

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
cp -r "$ORIGEN"/base/equipo-* ~/.claude/skills/
cp "$ORIGEN/clientes/$CLIENTE/contexto.md" ~/.claude/skills/equipo-tao/contexto.md
ls -d ~/.claude/skills/equipo-*
```

Para quitar un perfil que el cliente no quiso, se borra su carpeta (por ejemplo
`rm -r ~/.claude/skills/equipo-mid`) y su renglón en la ficha. **TAO y su ficha se quedan siempre**,
porque los demás leen la ficha desde ahí.

### A10c. Dejar Gabinete como postura por defecto

Se agrega un bloque al `CLAUDE.md` global del cliente, una sola vez. El bloque trae marcas de inicio
y fin, así que correrlo dos veces lo deja igual:

```bash
touch ~/.claude/CLAUDE.md
grep -q "perfiles-del-equipo: inicio" ~/.claude/CLAUDE.md \
  || cat "$ORIGEN/base/postura-gabinete.md" >> ~/.claude/CLAUDE.md
grep -c "perfiles-del-equipo" ~/.claude/CLAUDE.md   # debe dar 2
```

### A10d. Verificar

| Prueba | Qué se espera |
|---|---|
| En una sesión nueva, escribir `¿qué opina Gestión de lo que tengo pendiente?` | El primer renglón dice «Responde Gestión (GES)» y la respuesta usa los términos de su ficha |
| Escribir `¿en qué debo estar hoy?` | Contesta Gabinete, con recomendación, sin anunciarse |
| Escribir `revísalo con TAO` sobre cualquier decisión | Una sección por área y cierra con preguntas para el cliente |

Si un perfil se queda callado, la causa casi siempre es la carpeta: tiene que ser
`~/.claude/skills/equipo-ges/SKILL.md`, con el `SKILL.md` adentro de su carpeta.

### A10e. Lo que hay que decirle

- Les habla por su nombre o su apodo: *«¿qué opina Gestión?»*, *«pásalo por Procesos»*,
  *«revísalo con Tecnología»*. Si no los llama, entran solos cuando el tema es suyo.
- **La ficha es suya**: si cambia de puesto, de jefe o de forma de trabajar, se le pide al
  asistente que la ponga al día.
- Todo lo que va a un tercero pasa antes por su visto bueno, y los correos quedan en Borradores.
