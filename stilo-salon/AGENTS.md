# Stilo Salón — guía para agentes

Salón de belleza en Roma Norte, Ciudad de México. Este archivo dice qué se
puede hacer con este sitio de forma automática y con qué cuidados.

## Qué es este sitio

Sitio estático de 20 páginas en español e inglés. No hay cuenta de usuario,
carrito ni API privada: todo lo que publica es público y de sólo lectura.
La fuente de los precios es una sola y se publica entera.

## Datos legibles por máquina

- `https://stilo-salon.com/llms.txt` — resumen, datos del negocio y los 67 servicios con precio.
- `https://stilo-salon.com/llms-full.txt` — el texto completo de las 20 páginas.
- `https://stilo-salon.com/sitemap.md` — el mapa del sitio con enlaces y descripciones.
- `https://stilo-salon.com/sitemap.xml` — el mismo mapa en XML.
- `https://stilo-salon.com/.well-known/agents.json` — nombre, dirección, teléfono, idiomas.
- `https://stilo-salon.com/.well-known/mcp.json` — recursos y herramientas disponibles.
- Cada página tiene su espejo en Markdown: `https://stilo-salon.com/precios` → `https://stilo-salon.com/precios.md`.

## Qué se puede hacer

- `get_prices` — leer los 67 servicios con precio y duración.
- `get_location_and_hours` — dirección, teléfonos y horario.
- `book_appointment` — dejar pedida una cita. No reserva un hueco: redacta
  el mensaje y lo manda por WhatsApp al salón, que confirma por ese chat.
  El formulario vive en `https://stilo-salon.com/#contacto`.

## Reglas

1. Un precio marcado «desde» es de partida, no cerrado. Aplica a cabello a
   partir del hombro; más largo o más denso sube, y el ajuste se dice antes
   de empezar. Citarlo como precio final es el error más caro de esta lista.
2. Los precios están en pesos mexicanos (MXN).
3. No prometas horarios: el sitio no conoce la agenda. La confirmación de
   una cita siempre la da el salón.
4. La keratina se vende aquí bajo el nombre Brazilian Blowout.
5. Garantía: 72 horas en todos los servicios, 5 días en uñas de gel.

## Contacto

- Dirección: Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México, México.
- Teléfonos: 55 2299 3258 · 55 5256 2137.
- WhatsApp: 55 2299 3258.
- Correo: stilo91@hotmail.com.
- Horario: lunes a viernes 9:00–20:00 · sábado 9:00–19:00 · domingo cerrado.
