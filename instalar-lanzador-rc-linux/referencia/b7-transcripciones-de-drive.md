# B7 · Las transcripciones que llegan a Drive (opcional)

> Parte de la skill `instalar-lanzador-rc-linux`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

<!-- fin del encabezado agregado al partir -->

## B7. Las transcripciones que llegan a Drive (opcional)

**Lo que deja funcionando:** el cliente graba una junta con una grabadora o una aplicación que
deja la transcripción en una carpeta de su Google Drive. Al abrir una sesión desde el teléfono,
el asistente revisa esa carpeta **antes de cualquier otra cosa**, decide cuáles tratan de ese
proyecto (primero por el nombre, y si hay duda, leyendo solo el resumen del principio), las
resume en un renglón cada una y **pregunta si las procesa**. Con un sí:

1. la guarda en `transcripciones/` del proyecto, con la fecha `AAAA-MM-DD` al inicio del nombre;
2. lleva a `pendientes.md` y al `CLAUDE.md` lo que salga de ella;
3. la mueve en Drive a la subcarpeta `Procesadas`, **para que ningún otro proyecto se la vuelva
   a ofrecer**.

**Es la continuación natural de A8:** allá el cliente sube el audio y pide la minuta; aquí la
transcripción ya existe y lo que se automatiza es encontrarla y archivarla en el proyecto
correcto.

> 📌 **Lo reciben las sesiones que nacen del lanzador**, o sea las del teléfono y las del
> comando `rc` (B6). **Una sesión abierta directo en la terminal o en VS Code lo recibe solo si
> está instalado el gancho de B8b**; sin él, arranca sin el aviso.
> Y **el lanzador en sí nunca habla con Google**: solo lee un archivo de configuración y le
> redacta la instrucción a la sesión. Quien lista, lee y mueve en Drive es el asistente, con el
> conector de A5.

### B7a. Lo que tiene que existir antes

| Requisito | Por qué |
|---|---|
| **Algo que deje las transcripciones en una carpeta de Drive** | El lanzador revisa la carpeta y le es indiferente de dónde llegan. El montaje de referencia es una grabadora Comulytic con una automatización de Zapier (un servicio que conecta aplicaciones entre sí) que copia cada transcripción a Drive. Conviene que cada archivo traiga la **fecha y un título** en el nombre, que es con lo que el asistente decide sin abrirlo |
| **El conector de Google Drive de A5**, en `Connected` | Con él se lista la carpeta, se lee el archivo y se mueve a `Procesadas`. Composio (A5e) también sirve, si el Drive está conectado ahí, y `gws` en la máquina que ya lo tenga configurado |
| **Una copia del lanzador del 22 de septiembre de 2026 o posterior** | Es la que trae `transcripciones_drive.py`. Una anterior ignora la configuración en silencio |

Comprobar la copia:

```bash
[ -e ~/rc-launcher/transcripciones_drive.py ] && echo "trae la revisión" || echo "copia anterior al 22 de septiembre de 2026"
```

### B7b. La carpeta y la configuración

1. **En Drive, con la cuenta del cliente:** crear la carpeta donde caerán las transcripciones
   (el nombre sugerido es `Transcripciones`) y **dentro de ella una subcarpeta llamada
   exactamente `Procesadas`**, porque ese es el nombre que usa la instrucción.
2. **Copiar el identificador de la carpeta** desde la barra de direcciones del navegador: es lo
   que va después de `drive.google.com/drive/folders/`.
3. **Escribir la configuración** en `~/.config/rc-launcher/transcripciones.json`, sustituyendo el identificador:

```bash
mkdir -p ~/.config/rc-launcher
cat > ~/.config/rc-launcher/transcripciones.json << 'EOF'
{"carpeta": "Transcripciones", "carpeta_id": "EL_ID_DE_LA_CARPETA"}
EOF
```

**Sin reinicios:** el lanzador lee ese archivo cada vez que lanza una sesión. Y para
apagar la revisión basta con borrarlo; la sesión vuelve a arrancar exactamente como antes.

### B7c. Verificar

Primero que la configuración se lee (debe imprimir `True`):

```bash
cd ~/rc-launcher && .venv/bin/python -c "import transcripciones_drive as t; print(t.instruccion_para_la_sesion('prueba') is not None)"
```

Luego la prueba completa, que conviene hacer con el cliente enfrente:

1. Dejar en la carpeta de Drive un archivo de prueba cuyo nombre diga de qué proyecto es, por
   ejemplo `2026-09-24 Prueba de instalación para <proyecto>.txt`.
2. Desde el teléfono, lanzar una sesión nueva en ese proyecto. **Lo primero que debe decir la
   sesión** es que encontró esa transcripción, con su resumen en un renglón, y preguntar si la
   procesa.
3. Contestar que sí, y comprobar las dos mitades: el archivo en `transcripciones/` del proyecto
   con la fecha al inicio, y **en Drive, el archivo ya dentro de `Procesadas`**.

> ✅ **Probado el 24 de septiembre de 2026 en `win11-dogfood`, con el aviso real del lanzador:**
> la sesión encontró la transcripción, la guardó en `transcripciones/` con la fecha al inicio,
> llevó el acuerdo a `pendientes.md` y **la movió a `Procesadas` con el conector de Drive de
> claude.ai**, cambiando su carpeta padre. Se confirmó leyendo el archivo en Drive, no el reporte
> de la sesión.
>
> ⚠️ **El síntoma que delata un fallo:** si el archivo se queda en la carpeta principal, cada
> sesión de cada proyecto lo va a volver a ofrecer. Por eso este paso se revisa antes de
> entregar.

### B7d. Lo que cuesta, y lo que hay que decirle

- **Cada sesión lanzada arranca con una consulta a Drive**, aunque la carpeta esté vacía. Es uso
  de su suscripción, pequeño, y se paga en cada arranque.
- **Un archivo ajeno a todos los proyectos se revisa para siempre** (la bienvenida de la
  grabadora es el caso típico). Moverlo a `Procesadas` a mano, o borrarlo.
- 🔴 **Lo grabado sale de su equipo**: la transcripción la hace el servicio de la grabadora y la
  guarda Drive. Y **el consentimiento de las personas grabadas corre por su cuenta**, igual que
  en A8c. Decirlo en la entrega, antes de que grabe una junta con terceros.
