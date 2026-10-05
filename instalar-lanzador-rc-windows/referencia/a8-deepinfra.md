# A8 · Transcripción y voz con la cuenta propia de DeepInfra

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

<!-- fin del encabezado agregado al partir -->

## A8. Transcribir juntas y escuchar documentos, dos capacidades que se pagan aparte

**Entre las skills que ya trae instaladas hay dos que cuestan dinero, y ninguna guía lo
dice.** Sin esta sección, la primera vez que el cliente suba la grabación de una junta y
pida la minuta, la skill le va a pedir una llave que no sabía que necesitaba. Mejor
que lo sepa antes de instalar, no a media entrega.

**Qué dejan hacer, en sus palabras:**

- Sube el audio de una junta o una nota de voz y pide "transcribe esto" o "hazme la
  minuta": regresa el texto.
- Pide "léeme este documento" o "pásamelo a audio para el camino": regresa un MP3.

Las dos usan **DeepInfra**, un servicio externo, y **con la cuenta del propio cliente**,
no la nuestra: el consumo se cobra a su tarjeta, no a la de Gustavo.

### A8a. Conseguir la cuenta y guardar la llave

El primer uso de cualquiera de las dos la pide, con este texto ya escrito en la propia
skill (no hay que redactarlo de nuevo):

> Para transcribir necesito una llave de DeepInfra, que es tuya y se cobra a tu cuenta.
> Son dos minutos: entra a https://deepinfra.com, crea la cuenta con Google o GitHub, y
> en **Dashboard → API Keys → New API Key** genera una. Pégamela aquí. Una hora de audio
> te va a costar alrededor de un centavo de dólar.

La llave se guarda **por entrada estándar, nunca como argumento** del comando (un
argumento queda en el historial de PowerShell):

```powershell
'LA_LLAVE' | python "$env:USERPROFILE\.claude\skills\whisper-deepinfra\whisper_deepinfra.py" --guardar-llave
```

Queda en `%USERPROFILE%\.config\deepinfra\credentials`. **Es una sola llave para las dos
capacidades**: quien ya la dio para transcribir no la vuelve a dar para escuchar un
documento, y viceversa.

### A8b. Cuánto cuesta, con cifras reales

| Capacidad | Precio | Aterrizado |
|---|---|---|
| Transcribir una grabación | $0.00020 USD por minuto | una junta de una hora, poco más de un centavo de dólar ($0.012) |
| Convertir un documento a audio | $0.62 USD por millón de caracteres | un documento de 10 páginas (~20 mil caracteres), alrededor de un centavo de dólar |

> 📌 **Si además se contrató la fase B, el audio se escucha con un clic.** El MP3 cae en
> `salida\` del proyecto y el lanzador lo sirve por una liga, así que desde el teléfono se
> toca y suena, en vez de descargarlo y buscarlo en el navegador de archivos. Sin la fase B
> la capacidad funciona igual, solo que el audio llega como archivo adjunto. Se verifica en
> el renglón 13.

### A8c. Lo que hay que decirle, antes de que lo descubra él

🔴 **El audio de sus juntas y el texto de sus documentos salen de su computadora y se
procesan en DeepInfra, un tercero.** No es información que se quede en su máquina.
Conviene decirlo en la sesión de entrega, junto con lo de A5c, antes de que suba la
grabación de una junta con terceros delicados.

**Son opcionales.** Sin la cuenta, las dos capacidades quedan dormidas y todo lo demás
(el lanzador, la bitácora, los documentos de oficina, los conectores) sigue funcionando
igual. La cuenta se puede crear después, la primera vez que de verdad las necesite.
