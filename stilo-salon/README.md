# Stilo Salón — sitio web

Sitio estático bilingüe (ES/EN) para **Stilo Salón**, Calle Guadalajara 70-B,
Roma Norte, Cuauhtémoc, 06700, Ciudad de México.

Reemplaza el sitio actual de GoDaddy. Está construido a partir de la auditoría
SEO y el estudio de mercado de septiembre de 2026.

## Cómo cambiar un precio

Los precios viven **en un solo lugar**: el diccionario `PRICES` dentro de
`build.py`. Se editan ahí y se regenera el sitio:

```bash
python3 build.py
```

Eso reescribe las 12 páginas en los dos idiomas, con los precios ya sincronizados.
Nunca edites los `.html` a mano — el siguiente build los sobrescribe.

## Qué resuelve del sitio anterior

| Problema detectado | Cómo se resuelve |
| --- | --- |
| 8 de 15 páginas con ~105 palabras | Todas las páginas entre 610 y 745 palabras |
| 9 títulos de una sola palabra | Títulos con servicio + Roma Norte + CDMX |
| 6 páginas sin meta description | Todas con descripción única, con precios |
| 15 de 15 páginas sin structured data | `HairSalon` + `FAQPage` en JSON-LD |
| Dirección ausente del sitio | NAP completo en el footer de cada página |
| Sin versión en inglés | ES/EN completo con `hreflang` recíproco |
| "Axila $270" y "Axilas $280" duplicados | Un solo servicio, $280 |
| Acentos y erratas del menú | Corregidos en `PRICES` |
| "Privacy Policy coming soon" | Aviso de privacidad real, en ambos idiomas |
| Descuento por reseña de Google | Eliminado (viola políticas de Google) |

## Publicar en Cloudflare Pages

1. Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**, y elige este repositorio.
2. Configuración de build:
   - **Build command:** `python3 build.py`
   - **Build output directory:** `stilo-salon`
   - **Root directory:** `stilo-salon`
3. **Custom domains** → agrega `stilo-salon.com` y `www.stilo-salon.com`.
4. Cambia los nameservers del dominio en GoDaddy a los que indique Cloudflare.

`_redirects` ya manda las URLs viejas de GoDaddy (`/cabello`, `/uñas`,
`/servicios-y-costos`, `/ols/products`…) a las nuevas con 301, para no perder
el posicionamiento que ya existe.

## Pendientes antes de publicar

- [ ] Sustituir los dos marcadores `[ Sustituir por foto... ]` por fotos reales
      (portada 1200×1500, contacto 4:3) y escribirles `alt`.
- [ ] Agregar `assets/og.jpg` (1200×630) para cuando se comparta el enlace.
- [ ] Confirmar los años en el mercado: el texto dice "más de diez años".
- [ ] Decidir si se suben los precios de corte y color antes de publicar
      (ver el estudio de mercado) — si sí, se edita `PRICES` y se regenera.
