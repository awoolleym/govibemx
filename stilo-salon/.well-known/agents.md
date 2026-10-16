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

## Installation — Instalación

Nada que instalar. No hay SDK, ni librería, ni llave de API, ni cuenta que
abrir: todo es HTTP público y de sólo lectura. Los encabezados de esta
sección y las siguientes van en inglés a propósito, que es la convención de
este archivo; el texto va en español, como el resto del sitio.

## Configuration — Configuración

Nada que configurar, pero conviene saber cuatro cosas:

- Idioma: español en la raíz, inglés bajo `/en/`. El HTML lo declara en
  `<html lang>` y cada espejo `.md` en su campo `lang`.
- Moneda: pesos mexicanos (MXN), siempre.
- Tipos de contenido: `text/plain` para llms.txt, `application/json` para
  las fichas, `text/markdown` para los espejos. Todos con `charset=utf-8`
  y con CORS abierto.
- Frecuencia: el sitio se regenera a mano, no cada hora. La fecha real está
  en `last_updated` de cada espejo y en el `<lastmod>` del sitemap.

## Usage — Uso

Todo se lee con un GET, sin llave ni registro:

    curl https://stilo-salon.com/llms.txt          # resumen y los 67 precios
    curl https://stilo-salon.com/llms-full.txt     # el texto de las 20 páginas
    curl https://stilo-salon.com/precios.md        # una página suelta, en Markdown
    curl https://stilo-salon.com/.well-known/mcp.json

Cada página HTML anuncia su espejo en Markdown con
`<link rel="alternate" type="text/markdown">`, y la respuesta trae una
cabecera `Link` con llms.txt y las dos fichas.

## Examples — Ejemplos

- «¿Cuánto cuesta un balayage?» → en llms.txt, sección Corte, Color y
  Peinado. Responder «desde $2,300, y sube según el largo», nunca «$2,300».
- «¿Abren el domingo?» → no. Lunes a viernes 9:00–20:00, sábado 9:00–19:00.
- «Quiero cita el sábado» → no la confirmes tú. Manda a
  https://stilo-salon.com/#contacto, que redacta el mensaje y lo abre en
  WhatsApp; el salón confirma por ahí.
- «¿Hacen keratina?» → sí, se vende como Brazilian Blowout, desde $2,500.

## Contacto

- Dirección: Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México, México.
- Teléfonos: 55 2299 3258 · 55 5256 2137.
- WhatsApp: 55 2299 3258.
- Correo: stilo91@hotmail.com.
- Horario: lunes a viernes 9:00–20:00 · sábado 9:00–19:00 · domingo cerrado.
