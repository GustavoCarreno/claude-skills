# B13 · Cuando la cuenta de Claude pide volver a entrar

> Parte de la skill `instalar-lanzador-rc-windows`. El orden de todas las secciones y la tabla que dice
> en qué archivo vive cada una están en `SKILL.md`. Cuando aquí se cite otra sección (A3, B2b…),
> búscala en esa tabla.

## Contenido de este archivo

- B13. Cuando la cuenta de Claude pide volver a entrar
  - B13a. Lo que pasa, medido
  - B13b. Lo que hace el lanzador
  - B13c. Verificar
  - B13d. Lo que hay que decirle

## B13. Cuando la cuenta de Claude pide volver a entrar

Al 27 de octubre de 2026 (lanzador `946d9af`). **Vale para toda instalación.** Viaja con B2b, sin pasos
de configuración.

> 🔴 **En Windows hoy funciona solo el aviso anticipado, el ámbar de 3 días antes.** La detección de
> la sesión atorada y la entrada desde el teléfono dependen de tmux, y su versión para Windows es una
> segunda etapa sin construir ni medir en `win11-dogfood`. Mientras tanto, cuando venza, la entrada
> se hace en la computadora: `claude auth login` en una terminal, y seguir la liga.

### B13a. Lo que pasa, medido

- **La cuenta vence 27 días después de entrar.** La fecha vive en `refreshTokenExpiresAt`, dentro de
  `~/.claude/.credentials.json`, y **queda fija aunque las sesiones renueven su llave**. Medido con
  dos cuentas distintas en la misma máquina.
- **Al vencer, cada sesión que abre el lanzador se queda detenida en «Login expired»**, esperando
  algo que solo se puede hacer en una terminal. Desde el teléfono se ve como un lanzador que dejó de
  abrir sesiones, y sin esta sección eso era la llamada mensual de «el lanzador no abre».
- 🔴 **`claude auth status` responde `loggedIn: true` con la cuenta vencida.** Sirve de cero para
  verificar una instalación. Lo que dice la verdad es la fecha del archivo de credenciales.

### B13b. Lo que hace el lanzador

| Momento | Lo que se ve en el teléfono |
|---|---|
| **3 días antes de vencer** | Un aviso en ámbar arriba de todo, con la fecha y la hora en que vence |
| **Una sesión recién lanzada muestra «Login expired»** | En Linux, el aviso rojo con «Volver a entrar». **En Windows todavía falta**: la sesión se queda atorada |

Archivos que viajan con B2b: `cuenta.py`, `templates/_cuenta.html` y `templates/_cuenta_entrar.html`.

### B13c. Verificar

```powershell
cd $HOME\rc-launcher; .venv\Scripts\python -c "import cuenta; print(cuenta.vencimiento())"
```

**Falta medirlo en `win11-dogfood`**: que el archivo de credenciales viva en `$HOME\.claude\.credentials.json`
igual que en Linux.

Debe imprimir una fecha unos 27 días después del último inicio de sesión. Si sale vacía, el archivo
de credenciales falta o cambió de forma, y el aviso nunca va a aparecer: hay que revisarlo antes de
entregar.

### B13d. Lo que hay que decirle

- Una vez al mes Claude le va a pedir volver a entrar. **El aviso ámbar le da tres días**, y en
  Windows hoy se hace en la computadora, con una terminal. Conviene dejarle escrito el comando.
