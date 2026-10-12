# GoVibeMX · Pantalla trasera y control remoto

Dos páginas:

| Página | Para qué | Dirección en Cloudflare |
|---|---|---|
| `infotainment.html` | La pantalla de la tablet (pasajeros) | `/pantalla` |
| `driver.html` | El control remoto en tu celular | `/remoto` |

`index.html` es el widget de reservaciones; no se toca.

---

## 0. Probar en la tablet hoy mismo (sin Cloudflare)

Como el repositorio es público, estas direcciones sirven las páginas directo de GitHub con HTTPS (necesario para el GPS):

- **Tablet:** `https://raw.githack.com/awoolleym/govibemx/ccr-b19bbd16-2su3kq/infotainment.html`
- **Celular (remoto):** `https://raw.githack.com/awoolleym/govibemx/ccr-b19bbd16-2su3kq/driver.html`

Son solo para pruebas. Para el uso diario usa las direcciones de GitHub Pages (abajo).

---

## 1. En línea con GitHub Pages ✅ (ya está activo)

El sitio se publica desde la rama **`gh-pages`** (GitHub Pages, gratis, con HTTPS):

- **Tablet (Fully Kiosk):** `https://awoolleym.github.io/govibemx/infotainment.html`
- **Celular (remoto):** `https://awoolleym.github.io/govibemx/driver.html`
- El widget de reservaciones (`index.html`) sigue en `https://awoolleym.github.io/govibemx/`.

**Firebase:** el remoto ya funciona con GitHub Pages; no hace falta agregar el dominio en *Authorized domains* (eso solo aplica a inicios de sesión con Google). Ver la sección 5 para proteger la base de datos.

**Cómo llegan los cambios:** se suben a `main` y luego se pasan a `gh-pages`; GitHub publica en 1–2 minutos.
Si prefieres un solo paso, en GitHub → Settings → Pages cambia la rama de publicación a `main`.

---

## 1b. Alternativa: Cloudflare Pages (gratis)

1. Entra a **dash.cloudflare.com** → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Elige el repositorio **awoolleym/govibemx**.
3. Configuración:
   - **Production branch:** `main` (primero haz *merge* de la rama con los cambios a `main`).
   - **Framework preset:** None
   - **Build command:** *(vacío)*
   - **Build output directory:** `/`
4. **Save and Deploy**. Te da una dirección tipo `https://govibemx.pages.dev`.
5. (Opcional) **Custom domains** → agrega algo como `pantalla.govibemx.com`.

Cada vez que se actualice `main` en GitHub, Cloudflare publica la nueva versión sola en ~1 minuto.
Además, cada rama que no es `main` recibe su propia dirección de prueba (en Cloudflare: tu proyecto → **Deployments**), así puedes probar cambios en la tablet antes de publicarlos.
Los archivos `_redirects` y `_headers` ya están listos: crean las direcciones cortas y hacen que la tablet siempre cargue la versión más nueva.

> **Firebase:** en la consola de Firebase → Authentication → Settings → **Authorized domains**, agrega tu dominio de Cloudflare (`govibemx.pages.dev` y tu dominio propio si lo usas).

---

## 2. La tablet (Lenovo Tab M9 + Fully Kiosk)

TV, juegos, guías y páginas de GoVibeMX corren **dentro** de la pantalla. Las únicas apps que se pueden abrir son las de **Streaming** (Netflix, Prime Video, Disney+, Max, YouTube y YouTube Kids), para viajes largos. Fully Kiosk bloquea todo lo demás.

> Los bloqueos de **Kiosk Mode**, **URL Whitelist** y **Remote Admin** son de **Fully Kiosk PLUS** (licencia de pago, una vez por tablet). Sin PLUS funciona todo, pero un pasajero podría salir con los botones de Android.

### 2.1 Preparar la tablet (Ajustes de Android)
1. **Batería → Modo de protección** (Lenovo): actívalo. Carga hasta ~80% y cuida la batería porque la tablet vive conectada.
2. **Pantalla → Tiempo de espera:** el máximo. **Rotación automática:** apagada, en horizontal.
3. **No molestar:** activado, para que no salgan notificaciones encima de la pantalla.
4. **Ubicación:** activada, en alta precisión.
5. **Texto a voz:** *Google* con español (México), para el 🔊 de Español básico.
6. Quita la cuenta de Google personal o desactiva la Play Store, y quita apps que no uses.
7. **Opciones de desarrollador → Permanecer activo** (pantalla encendida mientras carga). Opcional.

### 2.2 Ajustes de Fully Kiosk
Los nombres pueden variar un poco según la versión.

| Sección | Ajuste | Valor |
|---|---|---|
| Web Content Settings | **Start URL** | `https://awoolleym.github.io/govibemx/infotainment.html` |
| | Enable Geolocation Access | ✅ (y permiso de ubicación para Fully) |
| | Autoplay Videos | ✅ |
| | Enable Fullscreen Videos | ✅ |
| | **Enable Popups** | ❌ (nada abre ventanas nuevas) |
| | **Enable JavaScript Interface** | ✅ (lo usa el botón Streaming para abrir las apps) |
| Web Zoom and Scaling | Enable Zoom | ❌ |
| | Initial Scale | 0 / automático (la pantalla se adapta sola) |
| Web Browsing Settings | Enable Pull to Refresh | ❌ |
| | Enable Back Button | ❌ |
| | Open URLs in other apps / Intent URLs | ❌ |
| Web Auto Reload | **Auto Reload on Idle** | **Apagado** (0). La pantalla ya se reconecta sola; si Fully recarga, quitaría lo que esté viendo el pasajero |
| | Reload on Internet Reconnect | ✅ |
| Toolbars & Appearance | Show Status Bar / Navigation Bar / Action Bar / Address Bar | ❌ todas |
| | Fullscreen / Immersive mode | ✅ |
| Device Management | **Keep Screen On** | ✅ |
| | Screen Orientation | Landscape |
| | **Launch on Boot** | ✅ |
| | Unlock Screen | ✅ |
| Kiosk Mode (PLUS) | **Enable Kiosk Mode** | ✅ |
| | **Kiosk Mode PIN** | un PIN tuyo (distinto al del remoto) |
| | Kiosk Exit Gesture | Swipe from left edge (o 7 toques rápidos) |
| | Disable Status Bar | ✅ |
| | Disable Other Apps | ✅ |
| | **App Whitelist** | las apps de streaming (lista abajo) |
| | Disable Volume Buttons | como prefieras (el volumen de TV lo manejas tú) |
| | Disable Power Button | ✅ (pide permiso de administrador del dispositivo) |
| | Lock Safe Mode | ✅ |
| Web Filter (PLUS) | **URL Whitelist** | la lista de abajo |
| Remote Administration (PLUS) | Enable Remote Administration | ✅ con contraseña; o usa **Fully Cloud** para manejar varias tablets |

**URL Whitelist** (una por línea; si algo deja de cargar, agrega su dominio):

```
*awoolleym.github.io*
*govibemx.com*
*youtube-nocookie.com*
*youtube.com*
*ytimg.com*
*googlevideo.com*
*gstatic.com*
*googleapis.com*
*firebaseio.com*
*cloudflare.com*
*arcgisonline.com*
*project-osrm.org*
*open-meteo.com*
*qrserver.com*
*wsimg.com*
*famobi.com*
```

**App Whitelist** (las únicas apps que se pueden abrir desde la pantalla; instálalas e inicia sesión antes):

```
com.netflix.mediaclient
com.amazon.avod.thirdpartyclient
com.disney.disneyplus
com.wbd.stream
com.google.android.youtube
com.google.android.apps.youtube.kids
```

Si no usas alguna app, no la instales: el botón simplemente no abre nada.

**Cómo regresan de Netflix y otras apps:** con Fully como app de inicio (abajo), el botón ◯ Inicio de Android siempre vuelve a GoVibeMX. La pantalla de Streaming se lo dice al pasajero. Con **Remote Administration / Fully Cloud** también puedes usar *Bring to Foreground* desde tu celular para traer la pantalla de vuelta. Prueba en tu tablet que la barra de navegación aparezca dentro de las apps; si no aparece, revisa en Kiosk Mode las opciones que ocultan la barra de navegación.

Para el bloqueo más fuerte, ve a **Android → Ajustes → Apps → Apps predeterminadas → App de inicio → Fully Kiosk**. Así el botón de Inicio siempre regresa a la pantalla.

### 2.3 Qué ven los pasajeros
- **Bienvenida (se abre a mano desde el remoto con *Welcome screen*):** se queda en pantalla hasta que alguien la toca o tú la cambias desde el remoto; ya no se va sola. Primero sale el saludo grande con el nombre del pasajero. Al tocar sale la segunda página: **"¡Hola! Soy Alan, tu anfitrión y conductor"**, abróchate el cinturón, Wi-Fi con contraseña, agua y A/C.
- **"Tu anfitrión · Alan"** siempre está arriba en la pantalla; al tocarlo vuelve a salir la info de Wi-Fi, agua y cinturón.
  - Para cambiar el nombre (otro conductor u otra camioneta), agrega `?host=Nombre` al final del Start URL. Ejemplo: `…/infotainment.html?host=Luis`.
  - El nombre y contraseña del Wi-Fi están en `infotainment.html` (busca `var WIFI`).
- **Despedida 👋:** se abre desde el celular (**Goodbye**) o desde el menú del conductor. Muestra:
  - "¡Gracias, {nombre}!" y "¿Llevas todo?".
  - El QR de reseña de Google, en todos los viajes. En Live Map/Uber también sale "califica en la app".
  - El QR de govibemx.com para reservar otra vez.
  - Se cierra al tocarla o con New ride.
- **Streaming:** Netflix, Prime Video, Disney+, Max, YouTube y YouTube Kids (abren como apps).
- **GoVibe TV:** videos de México elegidos que se reproducen dentro. No pueden abrir YouTube ni buscar otros.
- **Juegos:**
  - **🕹️ Arcade:** 20 juegos tipo Poki (Moto X3M, Penalty Shooters, billar, burbujas, 2048, sudoku…) de **Famobi**. Están hechos para mostrarse dentro de otra página, y se juegan dentro de la pantalla.
    - Poki no se deja mostrar dentro de otra página, por eso no está.
    - La primera vez cada juego tarda unos segundos en cargar; después se guarda en la tablet y abre más rápido.
    - Si un juego deja de cargar algún día, Famobi lo actualizó: dímelo y cambio el enlace.
  - **⚡ Rápidos:** Memorama, Trivia CDMX y ¡Encuéntralo!. Abren al instante, incluso sin internet.
- **🔆 Brillo:** botón arriba en la pantalla.
  - Opciones: 100%, 70%, 40%, 15% o **Apagar la pantalla**. Apagada queda en negro y se enciende con un toque.
  - Desde el remoto: tarjeta **Screen** (brillo, ⏻ Off, 💡 On).
  - Para que el brillo cambie la luz real de la pantalla:
    - En Fully, **Enable JavaScript Interface** debe estar activado.
    - En Android: **Ajustes → Apps → Fully Kiosk → Modificar ajustes del sistema → Permitir**.
    - Apaga el **Brillo adaptable / automático** de Android (Ajustes → Pantalla); si no, Android lo vuelve a subir solo.
    - En Fully → **Device Management**, deja vacío el ajuste **Screen Brightness**; si tiene un valor, Fully impone ese brillo.
    - Sin esos permisos el botón igual funciona: la pantalla detecta que la luz no cambió y la oscurece con una capa negra (ahorra menos batería).
- **GoVibeMX (excursiones, servicios):** tu sitio abre dentro, con botón ⬅ Inicio.
- Tras 3 minutos sin tocar, la pantalla vuelve sola al mapa o al inicio. Si hay un video, espera a que termine.
- Para probar sin manejar: abre el menú del conductor (mantén presionado el reloj 1.5 s) → **▶ Demo**.

### Medidas y fechas
- Todo sale en los dos sistemas:
  - Distancias en km y millas.
  - Alturas en metros y pies.
  - Temperatura en °C y °F.
  - Velocidad en km/h y mph.
- Los mapas tienen escala en km y millas.
- Las fechas antiguas usan **antes / después de Cristo**: **BC / AD** en inglés y **a.C. / d.C.** en español. Ejemplos: *~100 a.C.*, *200 d.C.*, *1325 AD*.

### 2.4 Tamaño de pantalla
La Tab M9 (1340×800) muestra la página como ~1005×600. Todo se ajusta a la altura: la pantalla de inicio cabe completa sin desplazarse en 1340×800, 1072×640, 1005×600 y 893×533, y también funciona en vertical. Si quieres todo más grande o más chico, cambia **Initial Scale** (p. ej. 90 o 110).

---

## 3. El control remoto en tu celular

1. En el celular abre `https://awoolleym.github.io/govibemx/driver.html`.
2. La primera vez te pide **crear un PIN** (4–6 dígitos, dos veces). Todos tus celulares usan el mismo PIN.
3. En el menú del navegador elige **"Agregar a pantalla de inicio"**: queda un ícono **GoVibe Remote** como si fuera app.
4. Úsalo así:
   - Toca el viaje: **Live Map** (Uber), **City Tour**, **Globo**, **Pirámides**, **Regreso** o **City ride** (sin mapa).
   - **✈️ Aeropuerto**: elige uno de los tres botones chiquitos: **AICM T1**, **AICM T2** o **AIFA**.
     - La ruta se calcula **desde donde está la camioneta en el momento en que activas el viaje**. Sale la hora de llegada y tips de vuelo.
     - Si la tablet todavía no tiene GPS, muestra "Esperando GPS" y traza la ruta en cuanto lo tiene.
   - **🏁 Regreso a CDMX**: no va a una dirección exacta.
     - Traza la ruta desde donde estés hasta la entrada a la Ciudad de México.
     - Al entrar a la ciudad sale "¡Bienvenidos de vuelta!" y el mapa cambia a colonias y lugares cercanos, como en el City Tour.
     - Sirve igual desde Teotihuacán, desde el aeropuerto o desde cualquier lado.
   - Abajo siempre tienes **🏠 Home**, **EN/ES**, **🎉 Welcome** y **👋 Goodbye**, al alcance del pulgar.
   - **🆕 New ride**: limpia la pantalla para el siguiente pasajero y guarda su nombre. **No** abre la bienvenida sola: ábrela tú con **Welcome screen** cuando quieras.
   - **On the tablet**: Inicio, idioma, abrir una sección (guías, TV, juegos…).
   - **👋 Goodbye**: pantalla de despedida al final del viaje.
   - **〰️ Traveled path on the map** (tarjeta *Screen*): prende o apaga la línea del camino ya recorrido. Apagada, el mapa solo muestra la camioneta y la ruta, ideal para viajes de Uber. El camino se sigue guardando, así que al prenderla vuelve a salir.
   - **Show a page or video**: pega cualquier dirección y la tablet la abre dentro de la pantalla. Un enlace de YouTube se reproduce en GoVibe TV. Algunos sitios (Google, Netflix, etc.) no se dejan mostrar dentro de otra página.
   - Arriba ves si la tablet está **en línea**, los km que faltan y el GPS.

Sin internet en el celular puedes cambiar el viaje desde la misma tablet: mantén presionado el reloj 1.5 s.

### Samsung Galaxy S26 Ultra y Z Flip5
- **Instalar como app:** abre la página en Chrome o Samsung Internet → menú → **Agregar a pantalla de inicio** / **Instalar app**. Abre sin barra de direcciones.
- **📱 Keep screen on** (abajo de todo): la pantalla del celular no se apaga mientras el remoto está abierto. Útil con el celular en el soporte.
- Cada botón vibra un poquito al tocarlo, para que sepas que se envió sin mirar.
- **Z Flip5 abierto:** se ve igual que en el S26 Ultra.
- **Z Flip5 cerrado (pantalla Flex Window):** el remoto muestra solo lo esencial, con botones grandes. Para abrirlo ahí:
  - Ajustes → Funciones avanzadas → **Labs** → *Apps permitidas en la pantalla externa*.
  - O instala **Good Lock** → **MultiStar** → *Launcher Widget* y agrega el remoto.
  - Samsung cambia estos menús seguido; si no los ves, busca "pantalla externa" en Ajustes.


---

## 4. Revisión rápida después de publicar

- [ ] La tablet abre `/pantalla` y muestra el mapa con GPS.
- [ ] El celular abre `/remoto`, creas el PIN y al tocar un viaje la tablet cambia.
- [ ] **New ride** desde el celular limpia la pantalla.
- [ ] El botón 🔊 de Español básico suena (si no: Ajustes de Android → texto a voz de Google con español de México).

---

## 5. Proteger la base de datos (Firebase)

Hoy la base de datos `govibebooking` se puede leer **sin iniciar sesión**:
- Lo del remoto (`rearScreen`: viaje, comandos y el PIN cifrado).
- También `inquiries` y `config` del widget de reservaciones.

La pantalla y el remoto ya inician sesión de forma anónima, así que puedes cerrar `rearScreen` sin romper nada:

1. Entra a **console.firebase.google.com** → proyecto **govibebooking** → **Realtime Database** → pestaña **Rules**.
2. **Antes de cambiar nada, copia las reglas actuales** y guárdalas.
3. Dentro de `"rules"`, agrega este bloque:

```json
"rearScreen": {
  "$van": {
    ".read": "auth != null",
    ".write": "auth != null"
  }
}
```

4. Ojo: si arriba de todo hay `".read": true` o `".write": true`, esas reglas abren **toda** la base y el bloque de arriba no sirve. En ese caso cámbialas por reglas por sección. Por ejemplo, esto deja el widget de reservaciones **igual que hoy** y protege el remoto:

```json
{
  "rules": {
    "bookings":  { ".read": true, ".write": true },
    "inquiries": { ".read": true, ".write": true },
    "config":    { ".read": true, ".write": true },
    "rearScreen": {
      "$van": { ".read": "auth != null", ".write": "auth != null" }
    }
  }
}
```

5. **Publish**. Después prueba en el celular: tocar un viaje debe cambiar la tablet.

`bookings` e `inquiries` guardan datos de tus clientes. Conviene protegerlos también, pero depende de cómo inicia sesión el widget de reservaciones. Revísalo antes de cerrarlos para no romper las reservaciones.

---

## 6. Cuando se cae la señal (Starlink)

- **La tablet se reconecta sola:**
  - Si pierde la conexión con el remoto por más de ~20 s, la fuerza de nuevo sin recargar la página (el video y el juego siguen).
  - Arriba, junto al reloj, sale **📡 Reconectando…** o **📡 Sin señal** y desaparece cuando vuelve.
- **Último recurso:**
  - Si en 3 minutos no logra reconectar, recarga la página, solo cuando nadie la está usando (sin video, sin bienvenida ni despedida en pantalla, y nadie la ha tocado en el último minuto).
  - Lo hace como máximo una vez cada 10 minutos.
- **Siempre abre:** la tablet y el remoto guardan una copia (`sw.js`). Si se recarga sin internet, abre igual, en vez de la página de error. El mapa también guarda las zonas que ya vio.
- **Remoto:**
  - Si tu celular pierde señal, sale **📡 Phone reconnecting…**.
  - Con el botón **🔄 Reconnect** (abajo) reconectas tu celular y le pides a la tablet que se reporte.
- **Comandos viejos no se ejecutan:** si mandas algo mientras la tablet no tenía señal, al reconectar solo se ejecuta si tiene menos de 2 minutos. Un *New ride* vale hasta 10 minutos.
- **Recomendado en Fully:** Web Auto Reload → **Reload on Internet Reconnect** activado y **Auto Reload on Idle apagado**. Si algo recarga la página, la bienvenida o la despedida vuelven a aparecer solas.
- **Respaldo de internet:** guarda en la tablet la red de Starlink **y** el hotspot de tu celular. Android cambia solo a la que tenga señal.

