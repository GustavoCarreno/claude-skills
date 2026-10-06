# B9 · La escucha en vivo durante una junta (todavía solo en Linux)

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

<!-- fin del encabezado agregado al partir -->

## B9. La escucha en vivo

En Linux, el menú de cada proyecto trae un cuadro **Escuchar**: el teléfono graba una junta,
Whisper la pasa a texto y una sesión de Claude deja tarjetas con respuestas, datos y
compromisos en la misma pantalla. Está descrita en la guía de Linux, sección B9.

> 🔴 **En Windows todavía falta construirla, y el cuadro aparece igual en el menú.** La sesión
> de escucha arranca, se vigila y se termina con `tmux`, que en Windows falta. Leído en el código
> el 5 de octubre de 2026: al tocar **Escuchar** la sesión de escucha queda sin arrancar. **Hay
> que decirle al cliente que ese cuadro todavía es para Linux**, antes de que lo toque en una
> junta.

Cuando se construya para Windows, esta sección se escribe aquí con lo que se mida en
`win11-dogfood`. Lo que ya se sabe que habrá que comprobar: que `claude.exe` recibe la
instrucción inicial por winpty, que la herramienta Monitor funciona, que Chrome del teléfono
da el micrófono por el HTTPS de `tailscale serve`, y matar por PID al `python` viejo al
actualizar (B2b).
