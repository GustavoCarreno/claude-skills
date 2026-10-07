# B10 · El proyecto principal, la tarjeta Hoy y el repaso diario de GES

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B10a. El proyecto principal
- B10b. La tarjeta Hoy y las esperas
- B10c. El repaso diario de GES
- B10d. Verificación

Las tres piezas salieron del lanzador el 6 de octubre de 2026 y se usan juntas: el principal
es el proyecto que agrupa a los demás, la tarjeta Hoy dice qué toca en el día, y GES es el
repaso que cada mañana busca promesas sin tarea. **Las tres llegan con el código del
lanzador (B2)**; lo único que se configura a mano es el archivo que enciende a GES, en B10c.

## B10a. El proyecto principal

Es el proyecto donde el cliente concentra la administración de todo lo demás. Para un
gerente de operaciones con veinte naves sería el proyecto de la administración general, el
que no es de una nave en particular. **Va hasta arriba del mosaico** esté fijado o no, a todo
lo ancho, y es **donde GES anota lo que carece de dueño claro**.

**Cómo se escoge:** desde el teléfono, tocar el proyecto y en su menú **Hacer principal**. Uno
solo a la vez: escoger otro reemplaza al anterior, y el mismo botón dice **Quitar como
principal** cuando ya lo es. Queda guardado en `%USERPROFILE%\.config\rc-launcher\principal.json`.

**Al instalar:** crear ese proyecto con "+ Nuevo proyecto" (o como carpeta bajo
`%USERPROFILE%\claude` con su `CLAUDE.md`) y escogerlo como principal **antes** de encender a GES en B10c. Así GES
nace sabiendo dónde dejar lo que encuentre.

> 📌 **Sin principal, todo funciona igual**, con dos diferencias: la tarjeta Hoy va sola, y
> GES deja cada tarea en el proyecto al que pertenece y se salta las que carecen de dueño.

## B10b. La tarjeta Hoy y las esperas

**Cero pasos de instalación: se enciende sola.** Junto al principal, arriba del mosaico,
aparece la tarjeta **Hoy**, también en el teléfono. Trae tres cosas:

| Qué | De dónde sale |
|---|---|
| Las facturas por emitir, en rojo | Las claves `factura` y `última factura` de los `contratos.md` (A7c). El botón **Ya la emití** escribe la fecha de hoy en la ficha |
| Las tres primeras tareas de *Hacer ya* | La matriz de A7b. La cuenta lleva a la lista completa en Enfoque |
| El estado de GES, con su botón | B10c. Sin GES encendido, este renglón falta |

Con las tres en cero dice **Todo al día** y se queda chica.

**Las esperas en la tarjeta del principal.** Debajo del principal salen las tres esperas más
viejas de todos los proyectos, como **Esperando a alguien · N**. Cada una abre su proyecto en
esa tarea, y la cuenta lleva a la lista completa de Enfoque. Salen de la sección `## Esperando
a alguien` de cada `pendientes.md` (A7), así que en una máquina nueva aparecen en cuanto el
cliente tenga esperas escritas.

> ⚠️ **Al cliente, las esperas se le presentan como lo que hoy trae la tarjeta, sin
> prometerlas como definitivas.** Su forma se escogió el 6 de octubre de 2026 para tener algo
> útil mientras tanto, y puede cambiar en una versión siguiente.

> 📌 **El botón Ya la emití es la única escritura del lanzador en `contratos.md`.** Existe para
> el día en que el cliente factura directo en el portal del SAT sin abrir sesión: sin el botón,
> el renglón rojo seguiría encendido con la factura ya emitida. Conserva la marca de orden de
> bytes y el fin de línea del archivo.

## B10c. El repaso diario de GES

GES (Gestión, Entregas y Seguimiento) es un repaso que busca **promesas que se están cayendo
calladas**: compromisos con fecha escrita en una nota y sin `vence`, o promesas en la prosa
del `CLAUDE.md` ("le mandaré el contrato el viernes") sin tarea en `pendientes.md`. Lo que
encuentra lo vuelve tarea, con la nota "Anotada por GES el AAAA-MM-DD" y de dónde salió.

**Cuándo corre:** la primera vez en el día que alguien abre el lanzador. Recargar la página
lo deja quieto, y el botón **Repasar con GES** de la tarjeta Hoy lo vuelve a lanzar cuando el
cliente quiera. **Corre con la suscripción, como uso normal**, porque lo dispara una persona
al abrir la página: cero llaves de API y cero procesos revisando en segundo plano.

**Se enciende con un archivo, y sin él el lanzador queda como antes:**

```powershell
$b = "$env:USERPROFILE\.config\rc-launcher\barrido.json"
New-Item -ItemType Directory -Force -Path (Split-Path $b) | Out-Null
if (-not (Test-Path $b)) { '{}' | Set-Content -Path $b -Encoding utf8 }
```

> ⚠️ **Se escribe en la consola de la máquina, o se copia como archivo.** El 6 de octubre de 2026,
> escribirlo con `Set-Content` a través de SSH perdió las comillas de un `barrido.json` con
> `instruccion` y lo dejó vacío. `{}` carece de comillas y sale bien de cualquier forma; uno con
> claves se prepara como archivo y se copia. La marca de orden de bytes que agrega PowerShell
> 5.1 es indiferente: el lanzador la tolera.

Para un cliente, `{}` basta: solo GES, con lo que carece de dueño cayendo en el principal de
B10a. El archivo admite dos claves más, y casi nunca hacen falta:

- **`instruccion`**: la ruta a un archivo con un encargo propio que corre antes de GES, en el
  principal. Solo donde exista un encargo así escrito.
- **`proyecto`**: el proyecto donde cae lo que carece de dueño, **solo cuando falta el
  principal**. El clic de B10a siempre gana.

> 🔴 **Antes de encenderlo, decirle al cliente que GES escribe en sus `pendientes.md` y los
> confirma en git**, un commit por proyecto con el mensaje "GES: …". Antes de subir, comprueba
> que cada repositorio sea privado. Lo que nunca hace: palomear, descartar, reordenar ni tocar
> los renglones `[x]` y `[-]`.

**Tres avisos que salieron midiendo:**

1. **Sin `gws` los borradores de Gmail quedan fuera** del repaso, y GES lo dice en su resumen.
   Es lo normal en un cliente (A5).
2. **Una carpeta sin git queda sin commit**, y su `pendientes.md` se escribe igual.
3. **Cuánto tarda:** medido en `win11-dogfood` el 6 de octubre de 2026, la apertura lanzó el
   repaso en 0.36 segundos y GES tardó 33 segundos con 11 proyectos, conservó el fin de línea
   CRLF y escribió su nota. En una máquina en uso con 49 proyectos tarda casi 3 minutos. Cada
   corrida tiene un tope de 25 minutos.

**Dónde mirar cuando algo falla:** cada corrida deja su registro en
`%USERPROFILE%\.local\state\rc-launcher\barrido\`, uno por corrida, con la fecha y la hora
en el nombre, en UTF-8.

## B10d. Verificación

1. **El principal:** desde el teléfono, en el menú del proyecto escogido, **Hacer principal**.
   Al cerrar el menú, ese proyecto queda hasta arriba, a todo lo ancho.
2. **La tarjeta Hoy:** aparece junto al principal. En una máquina recién instalada lo normal
   es **Todo al día**.
3. **GES:** con `barrido.json` ya escrito, abrir la raíz del lanzador. El renglón de GES dice
   **Barrido del día corriendo desde las …**, y al terminar cambia a **GES hace … · todo en
   orden hoy** o **· N cosas nuevas hoy**. Cuando encontró algo, Enfoque trae arriba la
   sección **Lo que encontró GES hoy**, con cada tarea abriendo su proyecto. **GES falló** o
   **GES se cortó sin terminar** mandan a leer el registro de B10c.
4. **La factura:** en un proyecto de prueba (`prueba-factura`), un `contratos.md` así, con el
   `desde` en un mes ya pasado y sin `última factura`:

   ```markdown
   # Contratos

   ## Prueba
   cliente: Prueba
   etapa: firmado
   cobro: 1000 MXN al mes · desde 2026-09-01
   factura: día 1 del mes
   ```

   La tarjeta Hoy pinta en rojo **Factura por emitir: Prueba, Prueba · tocaba el …**. Al
   tocar **Ya la emití** y confirmar, desaparece y la ficha gana `última factura: <hoy>`.
   Medido contra el código del lanzador el 6 de octubre de 2026. Al terminar, se borra el
   proyecto de prueba.

> ⚠️ **Sin medir todavía en Windows, y conviene hacerlo al instalar:** el clic de Hacer principal
> y el botón Ya la emití, los dos desde el teléfono por la tailnet. Las pruebas automáticas de
> los dos pasan en `win11-dogfood`; lo que falta es el dedo.
