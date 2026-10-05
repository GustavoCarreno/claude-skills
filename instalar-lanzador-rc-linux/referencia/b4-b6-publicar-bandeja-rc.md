# B4, B5 y B6 · Publicarlo en la tailnet, la bandeja y el comando rc

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

<!-- fin del encabezado agregado al partir -->

## B4. Publicarlo en la tailnet


```bash
sudo tailscale serve --bg http://127.0.0.1:8765
tailscale serve status
```

Queda en `https://<nombre>.<tailnet>.ts.net/`, **alcanzable solo desde la tailnet**. Esa
es la URL que se le da a la persona.

## B5. Decirle a las sesiones qué es la bandeja


**Paso corto y fácil de olvidar, y sin él la mitad del valor del lanzador no se usa.** El
lanzador deja lo que se sube desde el teléfono en `bandeja/`, dentro del proyecto. Pero
**nada le dice a la sesión que esa convención existe**: al pedirle "mira lo que subí a la
bandeja" contesta preguntando si te refieres al correo, porque para ella no significa nada.

**Aditivo e idempotente, igual que A6 y A7** (que ya pudo haber escrito en este mismo
archivo, porque la fase A corre antes que esta): se anexa a `~/.claude/CLAUDE.md`, nunca
lo reemplaza.

```bash
claude_md=~/.claude/CLAUDE.md
mkdir -p "$(dirname "$claude_md")"
touch "$claude_md"

grep -q '^## La bandeja' "$claude_md" || cat >> "$claude_md" << 'EOF'

## La bandeja: archivos que subo desde el teléfono


Cada proyecto puede tener una carpeta `bandeja/` en su raíz. Ahí es donde el lanzador rc
deja lo que subo desde el celular: fotos, audios de junta, PDFs, capturas.

**Si menciono "la bandeja", me refiero a esa carpeta del proyecto en el que estás, no a un
correo ni a nada de Gmail.** Revisar `bandeja/` del proyecto actual y trabajar con lo que
haya ahí.

Está en el gitignore, así que no aparece en `git status`. Al terminar de usar un archivo,
yo decido qué hacer con él desde el menú del lanzador, **no moverlo ni borrarlo por
iniciativa propia**, salvo que lo pida.
EOF
```

> ⚠️ **Correrlo dos veces no duplica la sección**, ni pisa la convención de pendientes que
> A7 ya sembró ahí. Es el mismo guardado con `grep` que usan A6 y A7.

Verificación: subir un archivo desde el teléfono, abrir la sesión de ese proyecto y pedirle
que vea la bandeja. Debe encontrarlo sin que le digas la ruta. Rápido y sin teléfono:
`grep -q '^## La bandeja' ~/.claude/CLAUDE.md`.

## B6. El comando `rc`, para lanzar desde la terminal (opcional)

**El camino principal es el teléfono**, y esta sección se puede saltar entera sin perder
nada de lo demás. Sirve para quien ya está frente a una terminal y prefiere teclear en vez
de sacar el celular.

**Lo que importa, y es lo que lo hace seguro: la sesión que nace aquí es la misma que nace
desde el teléfono.** El comando llama al mismo código, así que aparece en el mosaico y se
puede cerrar con el dedo. Dos formas distintas de crear una sesión se separan sin que nadie
lo note, y ahí es donde una sesión se vuelve invisible e inmatable.

```bash
sudo tee /usr/local/bin/rc > /dev/null << 'EOF'
#!/bin/bash
exec /usr/bin/python3 RUTA_DEL_LANZADOR/procesos_tmux.py "$@"
EOF
sudo chmod +x /usr/local/bin/rc
```

Sustituir `RUTA_DEL_LANZADOR` por la carpeta real. Uso:

```bash
rc                      # lista las carpetas disponibles
rc mi-proyecto          # abre la sesión y te deja trabajando DENTRO
rc mi-proyecto -d       # la deja corriendo y te devuelve la terminal
rc mi-proyecto --resume <session-id>
```

Verificación: `rc` sin argumentos lista los proyectos; `rc <alguno> -d` crea la sesión y el
mosaico la muestra en **Activos**.
