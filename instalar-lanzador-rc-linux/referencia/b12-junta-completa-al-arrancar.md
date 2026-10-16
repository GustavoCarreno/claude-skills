# B12 · La junta completa al arrancar: escucha, Drive y capturas

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B12. La junta completa al arrancar
  - B12a. Lo que tiene que existir antes
  - B12b. La carpeta de capturas, y marcar las juntas viejas
  - B12c. Verificar
  - B12d. Lo que hay que decirle, y lo que cuesta

## B12. La junta completa al arrancar

**Lo que deja funcionando:** el cliente termina una junta. La escucha del lanzador (B9) dejó en
`transcripciones/` del proyecto su transcripción, sus tarjetas y su libreta; si graba la junta con
una grabadora que manda la transcripción a Drive, esa llegó a la carpeta de B7; y durante la
llamada tomó capturas de las pantallas que le compartieron. **Las tres cosas son de la misma junta.**
Al abrir la siguiente sesión en ese proyecto, el asistente encuentra la junta sin procesar, la junta
con su transcripción de Drive por la hora, cuenta las capturas tomadas en ese rato y la ofrece en
**una sola casilla**, con clase `Junta`, en la lista «¿Qué atiendo ahora?» de B11d.

Con un sí, la procesa completa: lee la transcripción, las tarjetas (sobre todo las de compromiso) y
la libreta; guarda la de Drive y la mueve a «Procesadas»; copia las capturas a
`transcripciones/AAAA-MM-DD-HHMM-capturas/` y lee las que cambian respecto a la anterior, usando la
transcripción para saber qué se veía en cada momento; lleva lo que salga a `pendientes.md` y al
`CLAUDE.md`, citando la captura cuando una pantalla sostiene un dato; y al final anota la junta en
`transcripciones/procesadas.txt` para dejar de ofrecerla.

> 📌 **Es la sexta revisión del arranque**, después de la retroalimentación, las urgentes, Drive,
> el calendario y el correo. A diferencia de esas, **la calcula el lanzador completa y sin
> Google**: todo vive en el disco del proyecto. Por eso corre en cualquier máquina sin
> configuración, y el cruce con Drive sale solo donde B7 está encendida.

**Cómo se arma la ventana de la junta**, que es lo que decide qué capturas son suyas:

| Fuente | Inicio | Fin |
|---|---|---|
| La escucha | la hora del primer renglón | la del último |
| La transcripción de Drive | la hora del nombre menos la última marca del texto | la hora del nombre, que está en UTC |

Las capturas que cuentan son las de **la unión de las dos ventanas, más dos minutos en cada
orilla**, y la hora de cada captura sale de la fecha del archivo. Va la unión porque cada fuente
arranca cuando el cliente la prende: en la junta con que se midió, la escucha registró *"aquí
compartir la pantalla"* cuatro minutos antes de que empezara la grabación de Drive.

**Construida en el lanzador el 15 de octubre de 2026** (fusión `b4fcc0f`). Ensayada ese día con
sesión real en la máquina de Gustavo: una sola casilla con *"3 capturas, 2 con cambios"*; al
procesar copió las tres, movió la transcripción de Drive a «Procesadas», leyó las dos que cambian y
citó una cifra que solo estaba en una captura.

### B12a. Lo que tiene que existir antes

| Requisito | Por qué |
|---|---|
| **Una copia del lanzador del 15 de octubre de 2026 o posterior** (B2b) | Es la que trae `juntas_sesion.py`. Viajan también cambios en `pendientes.py` y `transcripciones_drive.py`, y **pide el reinicio del final de B2b**, porque el aviso de arranque lo arma el servicio |
| **La escucha de B9** | Es la que deja las juntas. Sin ella la revisión sale vacía siempre, sin daño |
| **Pillow en el `python3` del sistema** | Con ella el comando compara cada captura con la anterior y la sesión lee solo las que cambian. Ya la instala A4. Sin ella todas salen como «cambia» y la sesión las lee todas, con tope de 40 |
| **B7, si quiere el cruce con Drive** | Opcional. Sin B7 la sesión revisa solo lo local |

```bash
[ -e ~/rc-launcher/juntas_sesion.py ] || echo "FALTA: juntas_sesion.py"
python3 -c "import PIL; print('Pillow', PIL.__version__)"
```

> ⚠️ **El comando va con el `python3` del sistema y no con el `.venv` del lanzador**, a propósito:
> el `.venv` carece de Pillow. Es el `python3` en el que A4 instaló sus paquetes.

### B12b. La carpeta de capturas, y marcar las juntas viejas

**La carpeta de fábrica es `~/Pictures/Screenshots`**, que es donde Ubuntu deja las capturas con
la tecla Imprimir pantalla. Si el cliente guarda en otra, se escribe una sola vez:

```bash
ls -d ~/Pictures/Screenshots 2>/dev/null || echo "Sin carpeta de fábrica: escribir capturas.json"
# Solo si guarda en otra carpeta:
mkdir -p ~/.config/rc-launcher
echo '{"carpeta": "/home/USUARIO/ruta/de/sus/capturas"}' > ~/.config/rc-launcher/capturas.json
```

**En una máquina que ya usaba la escucha, marcar las juntas viejas antes de la primera sesión**,
o la siguiente sesión de cada proyecto ofrecerá todas las juntas guardadas desde el principio:

```bash
python3 ~/rc-launcher/juntas_sesion.py sembrar --antes-de "$(date +%Y-%m-%dT%H:%M)"
```

Imprime cuántas marcó (en la máquina de Gustavo fueron 22). Cada una queda en el
`transcripciones/procesadas.txt` de su proyecto con la leyenda de que se marcó al instalar. **En
una instalación nueva sobra**, porque todavía hay cero juntas.

### B12c. Verificar

Con el cliente enfrente, en un proyecto desechable:

1. Abrir Escuchar en ese proyecto (B9), decir dos frases y, mientras corre, tomar dos capturas de
   pantalla distintas. Tocar Terminar.
2. Lanzar una sesión nueva en ese proyecto. **Debe salir una casilla que empieza con `Junta`**, con
   la cuenta de capturas en la descripción.
3. Marcarla. La sesión debe copiar las capturas a `transcripciones/AAAA-MM-DD-HHMM-capturas/`,
   leerlas, y al final correr el comando `procesada`.
4. Lanzar otra sesión nueva: **la junta ya no debe ofrecerse.**

```bash
cat ~/claude/<proyecto>/transcripciones/procesadas.txt   # debe traer la junta de la prueba
```

### B12d. Lo que hay que decirle, y lo que cuesta

- **Que tome capturas durante la junta**, con la tecla de siempre, en vez de pedir el archivo
  después. El asistente las junta solo por la hora. Una captura de un momento escogido vale más que
  diez seguidas: el filtro descarta las repetidas, y cuando cada captura es distinta las lee todas.
- **Que la junta se procesa una vez.** Para volver a ofrecerla basta quitar su renglón de
  `transcripciones/procesadas.txt`.
- **Que las capturas quedan dentro del proyecto**, en `transcripciones/`, y con el respaldo de A9
  suben a su repositorio privado. Si una pantalla compartida trae datos de un tercero, eso viaja
  con ellas.
- **Lo que cuesta:** leer imágenes usa más de su suscripción que leer texto. Por eso el tope de 40
  y la comparación con la anterior.
