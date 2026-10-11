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

Son solo para pruebas: pueden tardar unos minutos en mostrar cambios nuevos. Para el uso diario, usa Cloudflare (abajo).

---

## 1. Publicar en Cloudflare Pages (gratis)

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

## 2. La tablet (Fully Kiosk)

1. **Start URL:** `https://TU-DOMINIO/pantalla`
2. **Web Content Settings → Enable Geolocation Access:** activado (y permiso de ubicación para Fully en Android).
3. Para probar sin manejar: abre el menú del conductor (mantén presionado el reloj 1.5 s) → **▶ Demo**.

---

## 3. El control remoto en tu celular

1. En el celular abre `https://TU-DOMINIO/remoto`.
2. La primera vez te pide **crear un PIN** (4–6 dígitos, dos veces). Todos tus celulares usan el mismo PIN.
3. En el menú del navegador elige **"Agregar a pantalla de inicio"**: queda un ícono **GoVibe Remote** como si fuera app.
4. Úsalo así:
   - Toca el viaje: **Live Map** (Uber), **City Tour**, **Globo**, **Pirámides**, **Regreso** o **City ride** (sin mapa).
   - **🆕 New ride**: limpia la pantalla y saluda al siguiente pasajero.
   - Arriba ves si la tablet está **en línea**, los km que faltan y el GPS.

Sin internet en el celular puedes cambiar el viaje desde la misma tablet: mantén presionado el reloj 1.5 s.

---

## 4. Revisión rápida después de publicar

- [ ] La tablet abre `/pantalla` y muestra el mapa con GPS.
- [ ] El celular abre `/remoto`, creas el PIN y al tocar un viaje la tablet cambia.
- [ ] **New ride** desde el celular limpia la pantalla.
- [ ] El botón 🔊 de Español básico suena (si no: Ajustes de Android → texto a voz de Google con español de México).
