#!/usr/bin/env python3
"""
Stilo Salón — generador del sitio estático.

Por qué existe: los precios y los servicios viven UNA sola vez, en este archivo.
De aquí se generan las páginas en español y en inglés, idénticas en contenido.
Cuando cambie un precio, se cambia aquí y se vuelve a correr:  python3 build.py

Salida: HTML estático plano, listo para Cloudflare Pages. Sin JavaScript para
renderizar contenido — todo el texto viaja en el HTML para que Google lo lea.
"""
import re, html
from datetime import date
import pathlib

OUT = pathlib.Path(__file__).parent
SITE = "https://stilo-salon.com"

NAP = {
    "street": "Calle Guadalajara 70-B",
    "locality": "Roma Norte, Cuauhtémoc",
    "postal": "06700",
    "city": "Ciudad de México",
    "tel1": "+525522993258", "tel1_display": "55 2299 3258",
    "tel2": "+525552562137", "tel2_display": "55 5256 2137",
}
BOOKING = "https://stilo-salon.versum.com/?trade=598440"
# Ficha de Google. GMB_CORTO es el enlace que comparte el propio salón;
# GMB_CID es el canónico armado con el CID de la ficha. Ambos abren el mismo
# lugar, y los dos van al schema para que Google los asocie.
GMB_CORTO = "https://maps.app.goo.gl/SRXsyACEtcT2T9cd7"
GMB_CID   = "https://maps.google.com/?cid=4574699337846800212"
GMB       = GMB_CORTO
# Enlace directo al formulario de reseña. El token lleva embebido el CID de
# la ficha (verificado: 4574699337846800212), así que abre la caja de reseña
# del negocio correcto, sin pasar por el perfil.
RESENA = "https://g.page/r/CVS_klrPmHw_EBM/review"
OPINIONES = 91   # ← actualizar cuando crezca
PERFILES = ["https://www.instagram.com/stilosalon91/",
            "https://www.fresha.com/lvp/stilo-salon-guadalajara-ciudad-de-mexico-zn6WVb",
            "https://stilo-salon.versum.com/",
            GMB_CID, GMB_CORTO]
# FB y TIKTOK se suman abajo, una vez definidos (ver la sección de redes).
WA = ("https://wa.me/525522993258?text="
      "Hola%2C%20quiero%20agendar%20una%20cita%20en%20Stilo%20Sal%C3%B3n")
# La valoración entra por WhatsApp con su propio mensaje: así sabemos de
# dónde viene la clienta y ella no tiene que explicar qué quiere.
WA_VALORA = ("https://wa.me/525522993258?text="
             "Hola%2C%20quiero%20una%20cita%20de%20valoraci%C3%B3n."
             "%20Les%20mando%20una%20foto%20y%20me%20dicen%20qu%C3%A9%20me%20conviene")


# El trazo de WhatsApp vive aquí una sola vez: lo usan el botón flotante,
# los iconos del pie y el de la portada.
WA_PATH = ("M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.65.08-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.14-.14.3-.35.45-.53.15-.18.2-.3.3-.5.1-.2.05-.38-.02-.53-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.07-.13-.27-.2-.57-.35zM12.04 21.5h-.01a9.43 9.43 0 0 1-4.8-1.32l-.35-.2-3.57.93.96-3.48-.23-.36a9.4 9.4 0 0 1-1.44-5.02c0-5.2 4.24-9.44 9.45-9.44 2.52 0 4.9.99 6.68 2.77a9.38 9.38 0 0 1 2.77 6.68c0 5.2-4.24 9.44-9.46 9.44zM20.5 3.49A11.36 11.36 0 0 0 12.04 0C5.76 0 .65 5.1.65 11.39c0 2 .52 3.96 1.52 5.68L.55 24l7.1-1.86a11.34 11.34 0 0 0 5.43 1.38h.01c6.28 0 11.39-5.11 11.39-11.4 0-3.04-1.18-5.9-3.33-8.05z")

# ── Redes ─────────────────────────────────────────────────────────────
# Solo entra lo que existe de verdad. Si mañana abren Facebook o TikTok,
# se agrega una línea aquí y aparece en el pie de las 18 páginas.
IG = "https://www.instagram.com/stilosalon91/"
# PENDIENTE: pegar aquí las URLs reales de Facebook y TikTok. En cuanto
# dejen de estar vacías aparecen solas en el pie de las 18 páginas y en el
# sameAs del JSON-LD.  Una URL equivocada es peor que ninguna: el sameAs es
# lo que Google usa para saber que esos perfiles son el mismo negocio.
FB     = ""
TIKTOK = ""
PERFILES += [u for u in (FB, TIKTOK) if u]

_RED_SVG = {
 "ig": ('<rect x="3" y="3" width="18" height="18" rx="5.2"/>'
        '<circle cx="12" cy="12" r="4.1"/>'
        '<circle cx="17.3" cy="6.7" r="1.15" fill="currentColor" stroke="none"/>'),
 "wa": ('<path fill="currentColor" stroke="none" d="%s"/>' % WA_PATH),
 "gmb": ('<path d="M12 21.6s7-6.2 7-11.1a7 7 0 1 0-14 0c0 4.9 7 11.1 7 11.1z"/>'
         '<circle cx="12" cy="10.4" r="2.6"/>'),
 "fb": ('<path d="M14.1 21.4v-8.3h2.8l.42-3.25h-3.22V7.77c0-.94.26-1.58 1.61-1.58h1.72V3.28'
        'A23 23 0 0 0 15 3.15c-2.48 0-4.18 1.51-4.18 4.29v2.39H8v3.25h2.82v8.32z"/>'),
 "tk": ('<path d="M16.4 3.2h-2.9v12.1a2.6 2.6 0 1 1-2.2-2.57V9.8a5.65 5.65 0 1 0 5.1 5.62V9.5'
        'a6.4 6.4 0 0 0 3.7 1.18V7.77A3.66 3.66 0 0 1 16.4 3.2z"/>'),
}

def redes(lang):
    """Fila de iconos de redes para el pie."""
    items = [(k, u, n) for k, u, n in
             [("ig", IG, "Instagram"), ("fb", FB, "Facebook"), ("tk", TIKTOK, "TikTok"),
              ("wa", WA, "WhatsApp"), ("gmb", GMB, "Google Maps")] if u]
    ic = "".join(
      f'<a href="{u}" rel="noopener" aria-label="{n}" title="{n}">'
      f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
      f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_RED_SVG[k]}</svg></a>'
      for k, u, n in items)
    return f'<div class="redes">{ic}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# PRECIOS — fuente única de verdad.  (nombre_es, nombre_en, precio, duración,
# nota_es, nota_en).  "desde" se marca con el prefijo ~ en el precio.
# ─────────────────────────────────────────────────────────────────────────────
PRICES = {
"cabello": {
  "es": "Corte, Color y Peinado", "en": "Cut, Color & Styling",
  "items": [
    ("Corte Dama", "Women's Haircut", "330", "30 min", "con moldeado", "with blow-dry shaping"),
    ("Corte Dama", "Women's Haircut", "420", "30 min", "con lavado y peinado", "with wash and style"),
    ("Corte Caballero", "Men's Haircut", "230", "30 min", "", ""),
    ("Corte Niño / Niña", "Children's Haircut", "190", "30 min", "", ""),
    ("Tinte", "Full Color", "~800", "1 h 15", "a partir del hombro", "shoulder length and up"),
    ("Retoque de Raíz", "Root Touch-Up", "900", "1 h 15", "", ""),
    ("Matiz", "Toner", "~900", "1 h 15", "a partir del hombro", "shoulder length and up"),
    ("Baño de Color", "Color Gloss", "~900", "1 h 15", "a partir del hombro", "shoulder length and up"),
    ("Balayage", "Balayage", "~2,300", "3 h", "a partir del hombro", "shoulder length and up"),
    ("Babylights", "Babylights", "~2,300", "3 h", "a partir del hombro", "shoulder length and up"),
    ("Base", "Base Color", "~1,200", "2 h", "a partir del hombro", "shoulder length and up"),
    ("Split Ender", "Split Ender", "~600", "1 h", "elimina puntas abiertas", "removes split ends"),
    ("Alto Peinado", "Updo", "~600", "30 min", "", ""),
    ("Alaciado o Moldeado con Secadora", "Blow-Dry Styling", "~280", "1 h", "a partir del hombro", "shoulder length and up"),
    ("Alaciado Express", "Express Straightening", "~280", "1 h", "a partir del hombro", "shoulder length and up")]},
"tratamientos": {
  "es": "Tratamientos y Alisados", "en": "Treatments & Smoothing",
  "items": [
    ("Nanoplastia", "Nanoplasty", "~2,500", "2 h", "alisado sin formol", "formaldehyde-free smoothing"),
    ("Brazilian Blowout", "Brazilian Blowout", "~2,500", "2 h",
     "el tratamiento de keratina · a partir del hombro",
     "the keratin treatment · shoulder length and up"),
    ("Botox Capilar", "Hair Botox", "~1,800", "1 h", "a partir del hombro", "shoulder length and up"),
    ("Tratamiento Profundo Hidratante", "Deep Hydrating Treatment", "~520", "1 h", "a partir del hombro", "shoulder length and up"),
    ("Ampolleta Hidratante Alfa Parf", "Alfaparf Hydrating Ampoule", "220", "", "", "")]},
"mani-pedi": {
  "es": "Manicure y Pedicure", "en": "Manicure & Pedicure",
  "items": [
    ("Manicure Spa", "Spa Manicure", "220", "", "sales, exfoliación, masaje y esmalte", "salts, exfoliation, massage and polish"),
    ("Manicure Express con Gel", "Express Manicure with Gel", "250", "", "drill, limado y gel hasta 2 tonos lisos", "drill, file and gel up to 2 solid shades"),
    ("Manicure Spa + Gel", "Spa Manicure + Gel", "350", "", "spa completo con gel hasta 2 tonos", "full spa with gel up to 2 shades"),
    ("Pedicure Spa", "Spa Pedicure", "360", "", "tina con sales, limado de talón, masaje y esmalte", "salt soak, heel filing, massage and polish"),
    ("Pedicure Spa + Gel", "Spa Pedicure + Gel", "450", "", "spa completo con gel hasta 2 tonos", "full spa with gel up to 2 shades"),
    ("Paquete Mani Spa + Pedi Spa con Gel", "Spa Mani + Pedi Package with Gel", "750", "", "ambos servicios con gel hasta 2 tonos lisos", "both services with gel up to 2 solid shades")]},
"gel-esmalte": {
  "es": "Gel, Esmalte y Vitaminas", "en": "Gel, Polish & Nail Vitamins",
  "items": [
    ("Gel Manos", "Gel — Hands", "180", "", "hasta 2 tonos lisos · tono adicional $20", "up to 2 solid shades · extra shade $20"),
    ("Gel Pies", "Gel — Feet", "220", "", "hasta 2 tonos lisos · tono adicional $20", "up to 2 solid shades · extra shade $20"),
    ("Esmalte", "Regular Polish", "150", "", "hasta 2 tonos lisos · tono adicional $10", "up to 2 solid shades · extra shade $10"),
    ("Retiro de Gel", "Gel Removal", "100", "", "", ""),
    ("Calcio", "Calcium", "150", "", "fortalece la uña natural", "strengthens the natural nail"),
    ("Calcio + Gel", "Calcium + Gel", "280", "", "hasta 2 tonos lisos", "up to 2 solid shades"),
    ("Rubber", "Rubber Base", "150", "", "cubre imperfecciones y da volumen a uñas débiles", "covers imperfections, adds body to weak nails"),
    ("Vitamina", "Nail Vitamin", "150", "", "protege y fortalece la uña natural", "protects and strengthens the natural nail")]},
"unas": {
  "es": "Acrílico y Esculturales", "en": "Acrylic & Sculpted Nails",
  "items": [
    ("Acrílico sobre uña natural", "Acrylic over Natural Nail", "400", "", "", ""),
    ("Retoque de Acrílico", "Acrylic Fill", "350", "", "", ""),
    ("Uña Escultural con Gel", "Sculpted Gel Nail", "~500", "", "hasta el #2, hasta 2 tonos lisos", "up to length #2, up to 2 solid shades"),
    ("Retoque Escultural con Gel", "Sculpted Gel Fill", "~400", "", "hasta el #2, hasta 2 tonos lisos", "up to length #2, up to 2 solid shades"),
    ("Uña Tip con Gel", "Gel Tip Nail", "~450", "", "hasta el #2, hasta 2 tonos lisos", "up to length #2, up to 2 solid shades"),
    ("Retoque de Uña Tip con Gel", "Gel Tip Fill", "~350", "", "hasta el #3, hasta 2 tonos lisos", "up to length #3, up to 2 solid shades"),
    ("Acripie", "Acrylic — Toes", "380", "", "", ""),
    ("Retiro de Acrílico", "Acrylic Removal", "100", "", "", "")]},
"pestanas": {
  "es": "Extensiones de Pestañas", "en": "Eyelash Extensions",
  "items": [
    ("Extensiones 1x1", "Classic 1x1 Set", "750", "1 h 30", "técnica clásica, una extensión por pestaña", "classic technique, one extension per lash"),
    ("Extensiones Flat", "Flat Set", "800", "1 h 30", "más ligeras, mayor superficie de adhesión", "lighter, larger bonding surface"),
    ("Extensiones YY", "YY Set", "1,000", "1 h 30", "efecto de mayor densidad", "denser look"),
    ("Extensiones Híbridas", "Hybrid Set", "1,100", "2 h", "mezcla de clásico y volumen", "mix of classic and volume"),
    ("Extensiones Volumen Ruso", "Russian Volume Set", "1,200", "2 h", "máxima densidad", "maximum density"),
    ("Retoque 1x1", "Classic 1x1 Fill", "450", "", "mínimo 50% de pestaña, antes de 21 días", "at least 50% retention, within 21 days"),
    ("Retoque Flat", "Flat Fill", "500", "", "mínimo 50% de pestaña, antes de 21 días", "at least 50% retention, within 21 days"),
    ("Retoque YY", "YY Fill", "550", "", "mínimo 50% de pestaña, antes de 21 días", "at least 50% retention, within 21 days"),
    ("Retoque Híbridas", "Hybrid Fill", "550", "", "de 50% a 30% de pestaña, antes de 21 días", "50%–30% retention, within 21 days"),
    ("Retoque Volumen Ruso", "Russian Volume Fill", "650", "", "mínimo 50% de pestaña, antes de 21 días", "at least 50% retention, within 21 days"),
    ("Retoque de Trabajo Externo", "Fill on Outside Work", "~500", "", "según la técnica que traigas", "depending on the technique applied elsewhere"),
    ("Lifting de Pestañas", "Lash Lift", "450", "", "incluye tinte y keratina", "includes tint and keratin"),
    ("Retiro de Pestañas", "Lash Removal", "200", "", "sin nueva aplicación", "without a new application"),
    ("Retiro + Aplicación Nueva", "Removal + New Set", "150", "", "retiro cuando pasaron más de 21 días y se aplica set nuevo", "removal past 21 days, when a new set is applied")]},
"cejas": {
  "es": "Cejas", "en": "Brows",
  "items": [
    ("Diseño de Ceja", "Brow Design", "450", "", "perfilado, diseño y laminación", "shaping, design and lamination"),
    ("Laminado de Ceja", "Brow Lamination", "450", "", "perfilado y laminación", "shaping and lamination"),
    ("Ceja con Cera", "Brow Wax", "220", "", "", "")]},
"depilacion": {
  "es": "Depilación con Cera y Maquillaje", "en": "Waxing & Makeup",
  "items": [
    ("Cara Completa", "Full Face", "480", "", "", ""),
    ("Axilas", "Underarms", "280", "", "", ""),
    ("Bigote", "Upper Lip", "180", "", "", ""),
    ("Bozo", "Peach Fuzz", "180", "", "", ""),
    ("Mentón", "Chin", "150", "", "", ""),
    ("Patilla", "Sideburns", "120", "", "", ""),
    ("Nariz", "Nose", "120", "", "", ""),
    ("Maquillaje", "Makeup Application", "950", "", "", "")]},
}

T = {  # cadenas de interfaz
 "es": {"price":"Precio","service":"Servicio","dur":"Duración","from":"desde",
        "hero_alt":"Clienta con balayage largo en Stilo Salón, Roma Norte, con el salón al fondo","unas_alt":"Uñas largas en gel dorado espejo hechas en Stilo Salón, Roma Norte","pest_alt":"Extensiones de pestañas de volumen ruso aplicadas en Stilo Salón, Roma Norte","wa_aria":"Escríbenos por WhatsApp","wa_cta":"Escríbenos","book":"Reservar cita en línea","book_wa":"WhatsApp","appts":"Citas","hours":"Horario",
        "mf":"Lunes a viernes","sat":"Sábado","sun":"Domingo","closed":"cerrado",
        "branch":"Sucursal Roma Norte","services":"Servicios","skip":"Saltar al contenido",
        "menu":"Menú","directions":"Cómo llegar","rights":"Todos los derechos reservados.",
        "logo_alt":"Stilo Salón — salón de belleza en Roma Norte, CDMX","privacy":"Aviso de Privacidad","full_list":"Ver la lista completa de precios",
        "mxn":"Precios en pesos mexicanos (MXN).","other":"English"},
 "en": {"price":"Price","service":"Service","dur":"Duration","from":"from",
        "hero_alt":"Client with long balayage at Stilo Salón, Roma Norte, with the salon behind her","unas_alt":"Long mirror-gold gel nails done at Stilo Salón, Roma Norte","pest_alt":"Russian volume eyelash extensions applied at Stilo Salón, Roma Norte","wa_aria":"Message us on WhatsApp","wa_cta":"Message us","book":"Book online","book_wa":"WhatsApp","appts":"Appointments","hours":"Hours",
        "mf":"Monday to Friday","sat":"Saturday","sun":"Sunday","closed":"closed",
        "branch":"Roma Norte Location","services":"Services","skip":"Skip to content",
        "menu":"Menu","directions":"Get directions","rights":"All rights reserved.",
        "logo_alt":"Stilo Salón — beauty salon in Roma Norte, Mexico City","privacy":"Privacy Notice","full_list":"See the full price list",
        "mxn":"Prices in Mexican pesos (MXN).","other":"Español"},
}

NAV = {
 "es": [("/cabello.html","Cabello"),("/unas.html","Uñas"),
        ("/pestanas-y-cejas.html","Pestañas y Cejas"),("/portafolio.html","Portafolio"),
        ("/precios.html","Precios"),("__BOOK__","Citas")],
 "en": [("/en/hair.html","Hair"),("/en/nails.html","Nails"),
        ("/en/lashes-and-brows.html","Lashes & Brows"),("/en/portfolio.html","Portfolio"),
        ("/en/pricing.html","Pricing"),("__BOOK__","Book")],
}

# ─────────────────────────────────────────────────────────────────────────────
# ICONOS — trazo fino, dibujados a mano, con los motivos del propio logo:
# la tijera y la pestaña. Van embebidos en el HTML: cero peticiones extra.
# ─────────────────────────────────────────────────────────────────────────────
ICONOS = {
"cabello": """<svg class="ico" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
<path d="M14.5 7.5 L30.5 34.5"/><path d="M33.5 7.5 L17.5 34.5"/>
<circle cx="32.5" cy="37.5" r="4.4"/><circle cx="15.5" cy="37.5" r="4.4"/>
<circle cx="24" cy="24.7" r="1.7"/></svg>""",
"tratamientos": """<svg class="ico" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
<path d="M24 6c0 0-9 11-9 18a9 9 0 0 0 18 0c0-7-9-18-9-18z"/>
<path d="M20 26a4 4 0 0 0 4 4"/><path d="M12 40c4 2 8 3 12 3s8-1 12-3"/></svg>""",
"unas": """<svg class="ico" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
<rect x="18.4" y="4" width="11.2" height="12.5" rx="2.8"/>
<path d="M21.6 16.5h4.8v4.2h-4.8z"/>
<rect x="13.2" y="20.7" width="21.6" height="22.3" rx="5.4"/>
<path d="M18 27.4h8.4"/></svg>""",
"pestanas": """<svg class="ico" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
<path d="M6 28c6-8 12-12 18-12s12 4 18 12"/><circle cx="24" cy="26" r="5"/>
<path d="M10 33l-3 5M17 36l-2 5M24 38v6M31 36l2 5M38 33l3 5"/></svg>""",
}

def icono(clave):
    return ICONOS.get(clave, "")

def e(s): return html.escape(str(s), quote=False)

ALTA  = ' fetchpriority="high"'
TARDE = ' loading="lazy"'

def img(base, w, h, alt, extra=""):
    """<picture>: WebP primero, JPEG de respaldo. Si no hay WebP, solo <img>."""
    jpg = f'<img src="/assets/{base}.jpg" width="{w}" height="{h}" alt="{alt}"{extra}>'
    if not (OUT / "assets" / f"{base}.webp").exists():
        return jpg
    return f'<picture><source srcset="/assets/{base}.webp" type="image/webp">{jpg}</picture>' 

def money(p):
    """'~2,300' -> ('desde', '$2,300')"""
    return (True, "$" + p[1:]) if p.startswith("~") else (False, "$" + p)

def table(keys, lang, nivel=3):
    t, out = T[lang], []
    for k in keys:
        grp = PRICES[k]
        out.append(f'<div class="price-block" id="{k}">')
        out.append(f'<h{nivel}>{e(grp[lang])}</h{nivel}>')
        out.append('<table class="price">')
        out.append(f'<thead><tr><th>{t["service"]}</th>'
                   f'<th style="text-align:right">{t["price"]}</th>'
                   f'<th style="text-align:right">{t["dur"]}</th></tr></thead><tbody>')
        for it in grp["items"]:
            name = it[0] if lang == "es" else it[1]
            note = it[4] if lang == "es" else it[5]
            dur  = it[3]
            pre, amt = money(it[2])
            label = f'{t["from"]} {amt}' if pre else amt
            small = f'<small>{e(note)}</small>' if note else ""
            out.append(f'<tr><td class="svc">{e(name)}{small}</td>'
                       f'<td class="amt">{e(label)}</td>'
                       f'<td class="dur">{e(dur) if dur else "—"}</td></tr>')
        out.append('</tbody></table></div>')
    return "\n".join(out)

def page(lang, slug, title, desc, body, alt_href, extra_ld=""):
    t = T[lang]
    home = "/" if lang == "es" else "/en/"
    canon = f"{SITE}{home}" if slug in ("", "index") else f"{SITE}{slug}"
    es_href = canon if lang == "es" else alt_href
    en_href = alt_href if lang == "es" else canon
    # Los <link rel="alternate"> del head van absolutos porque Google lo
    # exige.  Los enlaces que el visitante pica, no: si el botón EN apunta
    # a https://stilo-salon.com/en/, te saca del servidor donde estás
    # —una preview, una prueba, un dominio nuevo todavía sin conectar— y
    # te manda al dominio real, que puede estar sirviendo otra cosa.
    # En ruta relativa funciona en cualquier servidor, el de verdad incluido.
    _ruta = lambda u: u[len(SITE):] or "/"
    es_ruta, en_ruta = _ruta(es_href), _ruta(en_href)
    def _link(h, l):
        url = BOOKING if h == "__BOOK__" else h
        rel = ' target="_blank" rel="noopener"' if h == "__BOOK__" else ''
        return '<a href="%s"%s>%s</a>' % (url, rel, e(l))
    nav = "\n      ".join(_link(h, l) for h, l in NAV[lang])
    return f"""<!DOCTYPE html>
<html lang="{'es-MX' if lang=='es' else 'en'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="es-mx" href="{es_href}">
<link rel="alternate" hreflang="en" href="{en_href}">
<link rel="alternate" hreflang="x-default" href="{es_href}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{'es_MX' if lang=='es' else 'en_US'}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:url" content="{canon}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#15191D">
<meta property="og:image" content="{SITE}/assets/og.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="preload" href="/assets/parisienne.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
{extra_ld}
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
<a class="wa-flot" href="{WA}" rel="noopener" aria-label="{t['wa_aria']}" title="{t['wa_aria']}">
  <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path fill="currentColor" d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.65.08-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.14-.14.3-.35.45-.53.15-.18.2-.3.3-.5.1-.2.05-.38-.02-.53-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.07-.13-.27-.2-.57-.35zM12.04 21.5h-.01a9.43 9.43 0 0 1-4.8-1.32l-.35-.2-3.57.93.96-3.48-.23-.36a9.4 9.4 0 0 1-1.44-5.02c0-5.2 4.24-9.44 9.45-9.44 2.52 0 4.9.99 6.68 2.77a9.38 9.38 0 0 1 2.77 6.68c0 5.2-4.24 9.44-9.46 9.44zM20.5 3.49A11.36 11.36 0 0 0 12.04 0C5.76 0 .65 5.1.65 11.39c0 2 .52 3.96 1.52 5.68L.55 24l7.1-1.86a11.34 11.34 0 0 0 5.43 1.38h.01c6.28 0 11.39-5.11 11.39-11.4 0-3.04-1.18-5.9-3.33-8.05z"/></svg>
  <span class="wa-txt">{t['wa_cta']}</span>
</a>
{promo(lang)}
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="{home}"><img src="/assets/logo-stilo-salon.png" width="640" height="252" alt="{t['logo_alt']}"></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="nav">{t['menu']}</button>
    <nav class="nav" id="nav" aria-label="{'Principal' if lang=='es' else 'Main'}">
      {nav}
      <div class="lang">
        <a href="{es_ruta}" hreflang="es-mx"{' aria-current="true"' if lang=='es' else ''}>ES</a>
        <a href="{en_ruta}" hreflang="en"{' aria-current="true"' if lang=='en' else ''}>EN</a>
      </div>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <p class="foot-brand"><img src="/assets/logo-stilo-salon-negativo.png" width="640" height="252" alt="{t['logo_alt']}" loading="lazy"></p>
        <p>{'Salón de belleza en Roma Norte, Ciudad de México. Cabello, uñas, pestañas y cejas.' if lang=='es' else 'Beauty salon in Roma Norte, Mexico City. Hair, nails, lashes and brows.'}</p>
      </div>
      <div>
        <h4>{t['services']}</h4>
        <p>{'<br>'.join(_link(h, l) for h, l in NAV[lang])}</p>
      </div>
      <div>
        <h4>{'Síguenos' if lang=='es' else 'Follow us'}</h4>
        {redes(lang)}
        <p><a href="{IG}" rel="noopener">@stilosalon91</a></p>
        <p style="margin-top:1rem"><a class="foot-resena" href="{RESENA}" target="_blank" rel="noopener">{'★ Escribe tu reseña' if lang=='es' else '★ Write your review'}</a></p>
        <h4 style="margin-top:1.6rem">{t['hours']}</h4>
        <p>{t['mf']} · 9:00 – 20:00<br>{t['sat']} · 9:00 – 19:00<br>{t['sun']} · {t['closed']}</p>
      </div>
      <div>
        <h4>{t['branch']}</h4>
        <address>
          {NAP['street']}<br>
          {NAP['locality']}<br>
          {NAP['postal']}, {NAP['city']}<br>
          <a href="tel:{NAP['tel1']}">{NAP['tel1_display']}</a>
        </address>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 Stilo Salón. {t['rights']}</span>
      <span><a href="{'/aviso-de-privacidad.html' if lang=='es' else '/en/privacy.html'}">{t['privacy']}</a> · <a href="{en_ruta if lang=='es' else es_ruta}">{t['other']}</a></span>
    </div>
  </div>
</footer>
<script>
(function(){{
  'use strict';
  var menos = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Menú móvil
  var b = document.getElementById('menuBtn'), n = document.getElementById('nav');
  if (b && n) b.addEventListener('click', function () {{
    var o = n.classList.toggle('open');
    b.setAttribute('aria-expanded', o ? 'true' : 'false');
  }});

  // La promo se retira sola al vencer.
  // El sitio es estático: si nadie lo regenera, la franja se queda
  // puesta con una oferta muerta. Esto la quita en cuanto pasa su
  // fecha, sin depender de que alguien se acuerde.
  var pr = document.querySelector('.promo[data-hasta]');
  if (pr) {{
    var hoy = new Date();
    var h = hoy.getFullYear() + '-' +
            String(hoy.getMonth() + 1).padStart(2, '0') + '-' +
            String(hoy.getDate()).padStart(2, '0');
    if (h > pr.getAttribute('data-hasta')) pr.remove();
  }}

  // Inclinación 3D de las tarjetas de servicio.
  // Antes había translateZ pero sin perspectiva en el contenedor, así
  // que no se movía nada. Ahora la rejilla tiene perspectiva y cada
  // tarjeta gira siguiendo al cursor, con 7 grados de tope.
  var tarjetas = document.querySelectorAll('.grid.g4 .card');
  if (tarjetas.length && window.matchMedia('(hover: hover)').matches
      && window.matchMedia('(min-width: 700px)').matches) {{
    for (var ti = 0; ti < tarjetas.length; ti++) (function (c) {{
      var pend = false;
      c.addEventListener('mousemove', function (ev) {{
        if (pend) return;
        pend = true;
        requestAnimationFrame(function () {{
          var r = c.getBoundingClientRect();
          var px = (ev.clientX - r.left) / r.width  - .5;
          var py = (ev.clientY - r.top)  / r.height - .5;
          c.style.setProperty('--ry', (px * 17).toFixed(2) + 'deg');
          c.style.setProperty('--rx', (-py * 17).toFixed(2) + 'deg');
          c.style.setProperty('--mx', (px * 100 + 50).toFixed(1) + '%');
          c.style.setProperty('--my', (py * 100 + 50).toFixed(1) + '%');
          pend = false;
        }});
      }});
      c.addEventListener('mouseleave', function () {{
        c.style.setProperty('--ry', '0deg');
        c.style.setProperty('--rx', '0deg');
      }});
    }})(tarjetas[ti]);
  }}

  // Entrar por un enlace debe dejarte arriba.
  // El navegador —y el visor de vista previa— recuerdan dónde te quedaste
  // en una página que ya habías abierto, y al volver a entrar por un
  // enlace te dejan a media altura o hasta abajo. Si la navegación es
  // nueva y no trae ancla, empezamos arriba. El botón "atrás" conserva su
  // posición, que ahí sí es lo que uno espera.
  window.addEventListener('pageshow', function (ev) {{
    if (ev.persisted) return;
    var e = (window.performance && performance.getEntriesByType)
              ? performance.getEntriesByType('navigation')[0] : null;
    if (e && e.type === 'back_forward') return;
    if (location.hash) return;
    window.scrollTo({{ top: 0, left: 0, behavior: 'auto' }});
  }});

  if (menos) return;   // quien pidió menos movimiento, no recibe ninguno

  // A partir de aquí el JS se hace responsable de revelar. Marcamos <html>
  // para que el CSS pueda ocultar: si este script nunca corre, nada se oculta.
  document.documentElement.classList.add('anim');

  // Respaldo: pase lo que pase, a los 2.5 s todo queda visible. Más vale
  // perder la animación que perder el contenido.
  setTimeout(function () {{
    var faltan = document.querySelectorAll('.reveal:not(.seen)');
    for (var i = 0; i < faltan.length; i++) faltan[i].classList.add('seen');
  }}, 2500);

  // Aparición al entrar en pantalla
  var grupos = document.querySelectorAll('.js-reveal');
  for (var g = 0; g < grupos.length; g++) {{
    var hijos = grupos[g].children;
    for (var i = 0; i < hijos.length; i++) {{
      hijos[i].classList.add('reveal');
      if (i % 4) hijos[i].classList.add('d' + (i % 4));
    }}
  }}
  var secciones = document.querySelectorAll('.sec-head, .price-block, details.faq');
  for (var k = 0; k < secciones.length; k++) secciones[k].classList.add('reveal');

  if ('IntersectionObserver' in window) {{
    var io = new IntersectionObserver(function (ents) {{
      ents.forEach(function (en) {{
        if (en.isIntersecting) {{ en.target.classList.add('seen'); io.unobserve(en.target); }}
      }});
    }}, {{ rootMargin: '0px 0px -8% 0px', threshold: 0.01 }});
    document.querySelectorAll('.reveal').forEach(function (el) {{ io.observe(el); }});
  }} else {{
    document.querySelectorAll('.reveal').forEach(function (el) {{ el.classList.add('seen'); }});
  }}

  // Inclinación 3D de las tarjetas (solo con mouse: en táctil estorba)
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {{
    document.querySelectorAll('.card').forEach(function (c) {{
      c.addEventListener('mousemove', function (ev) {{
        var r = c.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width - 0.5;
        var py = (ev.clientY - r.top) / r.height - 0.5;
        c.style.transform = 'perspective(850px) rotateX(' + (-py * 7).toFixed(2) +
                            'deg) rotateY(' + (px * 9).toFixed(2) + 'deg) translateY(-6px)';
        c.style.setProperty('--mx', ((ev.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        c.style.setProperty('--my', ((ev.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      }});
      c.addEventListener('mouseleave', function () {{ c.style.transform = ''; }});
    }});
  }}

  // Los números de la barra de confianza cuentan hacia arriba
  var barra = document.querySelector('.trust');
  if (barra && 'IntersectionObserver' in window) {{
    new IntersectionObserver(function (ents, ob) {{
      if (!ents[0].isIntersecting) return;
      ob.disconnect();
      barra.querySelectorAll('strong').forEach(function (el) {{
        var txt = el.textContent, m = txt.match(/\d+/);
        if (!m) return;
        var fin = parseInt(m[0], 10), ini = performance.now();
        (function paso(t) {{
          var p = Math.min((t - ini) / 900, 1);
          var val = Math.round(fin * (1 - Math.pow(1 - p, 3)));
          el.textContent = txt.replace(/\d+/, val);
          if (p < 1) requestAnimationFrame(paso);
        }})(ini);
      }});
    }}, {{ threshold: 0.4 }}).observe(barra);
  }}


  // ── Parallax de la foto de portada ──────────────────────────────────
  // Se mueve una fracción de lo que se mueve la página: da profundidad sin
  // marear. Se calcula dentro de requestAnimationFrame para no trabar scroll.
  var foto = document.querySelector('.hero-figure img');
  if (foto && window.innerWidth > 900) {{
    var pend = false;
    window.addEventListener('scroll', function () {{
      if (pend) return;
      pend = true;
      requestAnimationFrame(function () {{
        var y = window.scrollY;
        if (y < 900) foto.style.transform = 'translateY(' + (y * 0.07).toFixed(1) + 'px)';
        pend = false;
      }});
    }}, {{ passive: true }});
  }}

  // ── Portafolio: categoría + técnica ──────────────────────────────────
  var pf = document.querySelector('.pf');
  if (pf) {{
    var rejilla  = pf.querySelector('.pf-rejilla');
    var piezas   = rejilla.querySelectorAll('figure');
    var pestanas = pf.querySelectorAll('.pf-tab');
    var chips    = pf.querySelectorAll('.pf-f');
    var cajasF   = pf.querySelectorAll('.pf-filtros');
    var vacio    = pf.querySelector('.pf-vacio');
    var cat = 'cabello', tec = '';

    function pinta() {{
      var n = 0;
      for (var i = 0; i < piezas.length; i++) {{
        var f = piezas[i];
        var ok = f.getAttribute('data-cat') === cat &&
                 (tec === '' || f.getAttribute('data-tec') === tec);
        f.hidden = !ok;
        // las piezas ocultas nunca cruzaron el observador, así que
        // entrarían en opacidad 0 y se quedarían invisibles.
        if (ok) {{ f.classList.add('seen'); n++; }}
      }}
      // Cada categoría tiene su propio juego de chips; Pestañas no tiene.
      for (var c = 0; c < cajasF.length; c++) {{
        cajasF[c].hidden = (cajasF[c].getAttribute('data-cat') !== cat);
      }}
      vacio.hidden = (n > 0);
    }}

    // Devuelve el chip "Todo" de la categoría activa, o null si no hay chips.
    function chipTodo(c) {{
      var caja = pf.querySelector('.pf-filtros[data-cat="' + c + '"]');
      return caja ? caja.querySelector('.pf-f[data-tec=""]') : null;
    }}

    function transicion() {{
      rejilla.classList.add('cambiando');
      setTimeout(function () {{
        pinta();
        rejilla.classList.remove('cambiando');
      }}, 220);
    }}

    for (var a = 0; a < pestanas.length; a++) {{
      (function (b) {{
        b.addEventListener('click', function () {{
          if (b.classList.contains('activo')) return;
          for (var j = 0; j < pestanas.length; j++) {{
            pestanas[j].classList.remove('activo');
            pestanas[j].setAttribute('aria-pressed', 'false');
          }}
          b.classList.add('activo'); b.setAttribute('aria-pressed', 'true');
          cat = b.getAttribute('data-cat'); tec = '';
          for (var k = 0; k < chips.length; k++) {{
            var on = chips[k].getAttribute('data-tec') === '';
            chips[k].classList.toggle('activo', on);
            chips[k].setAttribute('aria-pressed', on ? 'true' : 'false');
          }}
          transicion();
        }});
      }})(pestanas[a]);
    }}

    for (var c = 0; c < chips.length; c++) {{
      (function (ch) {{
        ch.addEventListener('click', function () {{
          if (ch.classList.contains('activo')) return;
          var hermanos = ch.parentNode.querySelectorAll('.pf-f');
          for (var j = 0; j < hermanos.length; j++) {{
            hermanos[j].classList.remove('activo');
            hermanos[j].setAttribute('aria-pressed', 'false');
          }}
          ch.classList.add('activo'); ch.setAttribute('aria-pressed', 'true');
          tec = ch.getAttribute('data-tec');
          transicion();
        }});
      }})(chips[c]);
    }}

    // #cabello / #unas / #pestanas, y también las técnicas: #balayage etc.
    // Así las páginas de servicio pueden enlazar directo a su sección.
    function desdeHash() {{
      var h = (location.hash || '').replace('#', '');
      if (!h) return;
      var tb = pf.querySelector('.pf-tab[data-cat="' + h + '"]');
      if (tb) {{ tb.click(); return; }}
      var ch = pf.querySelector('.pf-f[data-tec="' + h + '"]');
      if (ch) {{
        // Cada técnica vive dentro de una categoría: hay que activar la suya
        // primero o el filtro dejaría la rejilla en blanco.
        var dueno = ch.parentNode.getAttribute('data-cat');
        var tb2 = pf.querySelector('.pf-tab[data-cat="' + dueno + '"]');
        if (tb2) tb2.click();
        ch.click();
      }}
    }}

    pinta();
    desdeHash();
    window.addEventListener('hashchange', desdeHash);
  }}

  // ── Visor de galería ────────────────────────────────────────────────
  var figs = document.querySelectorAll('.galeria figure, .pf-rejilla figure');
  if (figs.length) {{
    var visor = document.createElement('div');
    visor.className = 'visor';
    visor.setAttribute('role', 'dialog');
    visor.setAttribute('aria-modal', 'true');
    visor.innerHTML = '<button class="visor-cerrar" aria-label="Cerrar">&times;</button>' +
                      '<button class="visor-nav visor-prev" aria-label="Anterior">&#8249;</button>' +
                      '<button class="visor-nav visor-next" aria-label="Siguiente">&#8250;</button>' +
                      '<img alt=""><figcaption></figcaption>';
    document.body.appendChild(visor);
    var vImg = visor.querySelector('img');
    var vCap = visor.querySelector('figcaption');
    var abridor = null;

    var vPrev = visor.querySelector('.visor-prev');
    var vNext = visor.querySelector('.visor-next');

    // Los hermanos visibles de la misma galería: en el portafolio eso
    // depende del filtro activo, así que se recalcula al abrir.
    function vecinos(fig) {{
      var caja = fig.parentNode, out = [];
      var todos = caja.querySelectorAll(':scope > figure');
      for (var i = 0; i < todos.length; i++) {{
        if (!todos[i].hidden) out.push(todos[i]);
      }}
      return out;
    }}

    function abrir(fig) {{
      var im = fig.querySelector('img');
      var cap = fig.querySelector('figcaption');
      vImg.src = im.currentSrc || im.src;
      vImg.alt = im.alt || '';
      // El pie del portafolio son dos nodos (<b> y <span>); textContent los
      // pega sin espacio. Si vienen separados, los unimos con un punto medio.
      if (cap && cap.children.length > 1) {{
        var trozos = [];
        for (var q = 0; q < cap.children.length; q++) {{
          var tx = cap.children[q].textContent.trim();
          if (tx) trozos.push(tx);
        }}
        vCap.textContent = trozos.join(' · ');
      }} else {{
        vCap.textContent = cap ? cap.textContent : '';
      }}
      visor.classList.add('abierto');
      document.body.style.overflow = 'hidden';
      abridor = fig;
      var g = vecinos(fig);
      var solo = g.length < 2;
      vPrev.hidden = solo; vNext.hidden = solo;
      visor.querySelector('.visor-cerrar').focus();
    }}

    function mover(paso) {{
      if (!abridor) return;
      var g = vecinos(abridor);
      var i = g.indexOf(abridor);
      if (i < 0) return;
      abrir(g[(i + paso + g.length) % g.length]);
    }}
    function cerrar() {{
      visor.classList.remove('abierto');
      document.body.style.overflow = '';
      if (abridor) {{ abridor.focus(); abridor = null; }}
    }}
    for (var i = 0; i < figs.length; i++) {{
      (function (fig) {{
        fig.setAttribute('tabindex', '0');
        fig.setAttribute('role', 'button');
        fig.addEventListener('click', function () {{ abrir(fig); }});
        fig.addEventListener('keydown', function (ev) {{
          if (ev.key === 'Enter' || ev.key === ' ') {{ ev.preventDefault(); abrir(fig); }}
        }});
      }})(figs[i]);
    }}
    visor.addEventListener('click', function (ev) {{
      if (ev.target === visor || ev.target.classList.contains('visor-cerrar')) cerrar();
    }});
    vPrev.addEventListener('click', function (ev) {{ ev.stopPropagation(); mover(-1); }});
    vNext.addEventListener('click', function (ev) {{ ev.stopPropagation(); mover(1); }});
    document.addEventListener('keydown', function (ev) {{
      if (!visor.classList.contains('abierto')) return;
      if (ev.key === 'Escape') cerrar();
      else if (ev.key === 'ArrowLeft') mover(-1);
      else if (ev.key === 'ArrowRight') mover(1);
    }});
    // Deslizar en celular
    var x0 = null;
    visor.addEventListener('touchstart', function (ev) {{
      x0 = ev.changedTouches[0].clientX;
    }}, {{ passive: true }});
    visor.addEventListener('touchend', function (ev) {{
      if (x0 === null) return;
      var d = ev.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(d) > 45) mover(d < 0 ? 1 : -1);
    }}, {{ passive: true }});
  }}

  // Encabezado compacto al bajar.
  // Banda muerta a propósito: entra a 88 y no sale hasta 32. Con un solo
  // umbral, el temblor normal del scroll en celular cruzaba el límite una
  // y otra vez y la clase se encendía y apagaba sin parar — medido: 7
  // cambios con 10 micro-scrolls. Eso era el parpadeo.
  var head = document.querySelector('.site-head'), ticking = false, fijo = false;
  window.addEventListener('scroll', function () {{
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {{
      var y = window.scrollY || window.pageYOffset;
      if (!fijo && y > 88) {{ fijo = true; head.classList.add('scrolled'); }}
      else if (fijo && y < 32) {{ fijo = false; head.classList.remove('scrolled'); }}
      ticking = false;
    }});
  }}, {{ passive: true }});
}})();
</script>
</body>
</html>
"""

# El archivo en disco se llama precios.html, pero la URL pública es
# /precios.  Cloudflare sirve el .html sin que se note, y quitarlo aquí
# —en un solo lugar, al escribir— evita tener que acordarse en las 95
# rutas que hay repartidas por este archivo.  El canonical, el hreflang,
# el og:url, los enlaces internos, el sitemap y los _redirects salen
# todos de aquí, así que no se pueden desalinear entre sí.
#
# Sin esto, el servidor redirige /precios.html a /precios con un 307
# mientras el canonical sigue diciendo /precios.html: se le pide a Google
# que indexe una dirección que se mueve.
#
# 404.html queda intacto a propósito: Cloudflare lo busca por ese nombre.
RUTA_PUBLICA = re.compile(
    r'((?:https://stilo-salon\.com)?/(?:[a-z0-9-]+/)*[a-z0-9-]+)\.html(?=["#<])')

def sin_extension(texto):
    return RUTA_PUBLICA.sub(
        lambda m: m.group(0) if m.group(1).endswith("/404") else m.group(1), texto)

def write(path, content):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    if path.endswith((".html", ".xml")):
        content = sin_extension(content)
    p.write_text(content, encoding="utf-8")
    return f"  {path}  ({len(content):,} bytes)"

# ─────────────────────────────────────────────────────────────────────────────
# CONTENIDO DE LAS PÁGINAS
# ─────────────────────────────────────────────────────────────────────────────
C = {
"es": {
 "home_h1": ["¡Bonita", "la que lo lea!"],
 "home_lede": "Bienvenida a Stilo Salón. Nos encanta consentirte y hacerte sentir como en casa: somos el lugar para relajarte, dejarte consentir y ser tú misma. Porque sabemos que la belleza no lo es todo… pero conocemos el gran poder que tiene para impulsarnos a ser la mejor versión de nosotras mismas.",
 "home_why_h2": "Nos estamos actualizando, sin perder lo que ya funcionaba",
 "why": [
   ("Nunca un ajuste al cobrar", "La lista completa está en el sitio, no en un mensaje privado. Si un servicio requiere ajuste por largo o densidad de cabello, te lo decimos antes de empezar — nunca al momento de cobrar."),
   ("Técnica al día", "Nanoplastia, botox capilar y Brazilian Blowout con producto profesional. Extensiones de pestañas en cinco técnicas distintas, desde el 1x1 clásico hasta el volumen ruso."),
   ("Tiempos reales", "Cada servicio de la lista incluye su duración. Un balayage son tres horas y lo decimos de frente, para que organices tu día sin sorpresas.")],
 "svc_cards": [
   ("cabello", "Cabello", "Corte, tinte, balayage, babylights, matiz y peinado.", "desde $330", "/cabello.html", "Ver cabello y color"),
   ("tratamientos", "Tratamientos", "Nanoplastia, Brazilian Blowout, botox capilar e hidratación profunda.", "desde $520", "/guia-color-y-alisados.html#alisados", "Ver tratamientos y alisados"),
   ("unas", "Uñas", "Manicure y pedicure spa, gel, acrílico, esculturales y vitaminas.", "desde $150", "/unas.html", "Ver uñas, manicure y pedicure"),
   ("pestanas", "Pestañas y Cejas", "Extensiones 1x1 a volumen ruso, lifting, laminado y diseño de ceja.", "desde $450", "/pestanas-y-cejas.html", "Ver pestañas y cejas")],
 "faq": [
   ("¿Cuál es su horario de atención?", "Lunes a viernes de 9:00 a 20:00 y sábados de 9:00 a 19:00. Domingos cerrado."),
   ("¿Dónde están ubicados?", "En Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México. Estamos a unas cuadras del Metro Insurgentes."),
   ("¿Necesito cita o aceptan walk-in?", "Recomendamos cita, sobre todo para color y tratamientos que toman varias horas. Puedes reservar en línea a cualquier hora, escribirnos por WhatsApp o llamarnos. Recibimos walk-in según la disponibilidad del día."),
   ("¿Puedo llevar a mi perro?", "Sí, somos pet friendly. Puedes venir con tu mascota siempre que sea tranquila con otras personas y la traigas con correa o en transportadora."),
   ("¿Tienen WiFi?", "Sí, WiFi gratis para las clientas. Los servicios de color y tratamiento toman varias horas, así que puedes trabajar o ver algo mientras tanto. También te ofrecemos una bebida de cortesía."),
   ("¿Qué formas de pago aceptan?", "Efectivo y tarjetas de débito y crédito."),
   ("¿Aceptan meses sin intereses?", "Sí. Manejamos 3 meses sin intereses con todas las tarjetas de crédito en compras a partir de $2,000."),
   ("¿Los precios publicados son finales?", "Los precios marcados “desde” aplican a cabello a partir del hombro. Si tu cabello es más largo o más denso, el ajuste se te comunica antes de empezar el servicio, nunca al final."),
   ("¿Sus servicios tienen garantía?", "Sí. Todos nuestros servicios tienen 72 horas de garantía, y las uñas en gel 5 días. Si algo no quedó como lo acordamos, regresa dentro de ese plazo y lo corregimos sin costo.")],
 "visit_h2": "Estamos en el corazón de la Roma Norte",
},
"en": {
 "home_h1": ["Beautiful", "— yes, you."],
 "home_lede": "Welcome to Stilo Salón. We love spoiling you and making you feel at home: this is the place to relax, be looked after, and be yourself. Because beauty isn't everything — but we know the power it has to push us toward the best version of ourselves.",
 "home_why_h2": "We are modernizing, without losing what already worked",
 "why": [
   ("No adjustments at the register", "The full list is on the site, not in a private message. If a service needs an adjustment for hair length or density, we tell you before we start — never at the register."),
   ("Current technique", "Nanoplasty, hair botox and Brazilian Blowout with professional product. Eyelash extensions in five distinct techniques, from classic 1x1 to Russian volume."),
   ("Honest timing", "Every service on the list shows its duration. A balayage takes three hours and we say so up front, so you can plan your day.")],
 "svc_cards": [
   ("cabello", "Hair", "Cuts, color, balayage, babylights, toner and styling.", "from $330", "/en/hair.html", "See hair and color"),
   ("tratamientos", "Treatments", "Nanoplasty, Brazilian Blowout, hair botox and deep hydration.", "from $520", "/en/color-and-smoothing-guide.html#alisados", "See treatments and smoothing"),
   ("unas", "Nails", "Spa manicure and pedicure, gel, acrylic, sculpted nails and vitamins.", "from $150", "/en/nails.html", "See nails, manicure and pedicure"),
   ("pestanas", "Lashes & Brows", "Extensions from 1x1 to Russian volume, lifts, lamination and brow design.", "from $450", "/en/lashes-and-brows.html", "See lashes and brows")],
 "faq": [
   ("What are your hours?", "Monday to Friday, 9:00 to 20:00, and Saturday, 9:00 to 19:00. Closed Sundays."),
   ("Where are you located?", "Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Mexico City — a few blocks from Metro Insurgentes."),
   ("Do I need an appointment, or do you take walk-ins?", "We recommend an appointment, especially for color and treatments that take several hours. You can book online any time, message us on WhatsApp, or call. We do take walk-ins based on the day's availability."),
   ("Can I bring my dog?", "Yes, we are pet friendly. You are welcome to come with your pet as long as it is calm around people and comes on a leash or in a carrier."),
   ("Do you have WiFi?", "Yes, free WiFi for clients. Color and treatment services take several hours, so you can work or watch something while you wait. We also offer you a complimentary drink."),
   ("What payment methods do you accept?", "Cash, and debit and credit cards."),
   ("Do you offer interest-free monthly payments?", "Yes. We offer 3 interest-free monthly payments with any credit card on purchases from $2,000 MXN."),
   ("Are the published prices final?", "Prices marked “from” apply to hair at shoulder length and above. If your hair is longer or denser, we tell you the adjustment before starting the service, never at the end."),
   ("Do your services come with a guarantee?", "Yes. Every service carries a 72-hour guarantee, and gel nails 5 days. If something did not turn out the way we agreed, come back within that window and we will correct it at no cost.")],
 "visit_h2": "In the heart of Roma Norte",
},
}

def faq_ld(lang):
    qs = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (_j(q), _j(a)) for q, a in C[lang]["faq"])
    return ('<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}</script>' % qs)

def _j(s):
    import json
    return json.dumps(s, ensure_ascii=False)

def salon_ld(lang):
    import json
    d = {"@context":"https://schema.org","@type":"HairSalon","@id":f"{SITE}/#salon",
      "name":"Stilo Salón","url":f"{SITE}/" if lang=="es" else f"{SITE}/en/",
      "description":("Salón de belleza en Roma Norte, CDMX. Cabello, color, tratamientos, uñas, extensiones de pestañas y diseño de cejas."
                     if lang=="es" else
                     "Beauty salon in Roma Norte, Mexico City. Hair, color, treatments, nails, eyelash extensions and brow design."),
      "telephone":"+52-55-2299-3258","priceRange":"$$","currenciesAccepted":"MXN",
      "paymentAccepted":("Efectivo, tarjeta de débito, tarjeta de crédito, 3 meses sin intereses desde $2,000" if lang=="es" else "Cash, debit card, credit card, 3 interest-free monthly payments from $2,000"),
      "image":f"{SITE}/assets/og.png",
      "address":{"@type":"PostalAddress","streetAddress":NAP["street"],
                 "addressLocality":NAP["locality"],"addressRegion":"Ciudad de México",
                 "postalCode":NAP["postal"],"addressCountry":"MX"},
      "areaServed":["Roma Norte","Roma Sur","Condesa","Juárez","Ciudad de México"],
      "sameAs":PERFILES,
      "email":"stilo91@hotmail.com",
      "hasMap":"https://maps.google.com/?q=Guadalajara+70-B,+Roma+Norte,+CDMX",
      "potentialAction":{"@type":"ReserveAction",
        "target":{"@type":"EntryPoint","urlTemplate":BOOKING,
                  "inLanguage":"es-MX",
                  "actionPlatform":["http://schema.org/DesktopWebPlatform",
                                    "http://schema.org/MobileWebPlatform"]},
        "result":{"@type":"Reservation","name":"Cita en Stilo Salón"}},
      "amenityFeature":[
        {"@type":"LocationFeatureSpecification",
         "name":"Wi-Fi gratuito" if lang=="es" else "Free Wi-Fi","value":True},
        {"@type":"LocationFeatureSpecification",
         "name":"Se admiten mascotas" if lang=="es" else "Pet friendly","value":True},
        {"@type":"LocationFeatureSpecification",
         "name":"Bebida de cortesía" if lang=="es" else "Complimentary drink","value":True}],
      "petsAllowed":True,
      "openingHoursSpecification":[
        {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"09:00","closes":"20:00"},
        {"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"19:00"}],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)


FEATURED = [
  ("cabello", 1), ("cabello", 2), ("cabello", 8),
  ("tratamientos", 0), ("pestanas", 0), ("mani-pedi", 2)]


# ── Amenidades ────────────────────────────────────────────────────────
# Tres cosas que la clienta decide ANTES de agendar: si puede trabajar,
# si puede traer a su perro y cómo la van a tratar mientras espera.
# Van en la portada (zona de conversión) y también en el JSON-LD, que es
# de donde Google toma los "atributos" del negocio.
AMENIDAD_ICONO = {
  "wifi": ('<path d="M3 8.6a12.7 12.7 0 0 1 18 0"/>'
           '<path d="M6.3 12a8 8 0 0 1 11.4 0"/>'
           '<path d="M9.6 15.4a3.4 3.4 0 0 1 4.8 0"/>'
           '<circle cx="12" cy="18.9" r="1.15" fill="currentColor" stroke="none"/>'),
  "pet":  ('<ellipse cx="6.6" cy="10.1" rx="1.9" ry="2.5"/>'
           '<ellipse cx="10.4" cy="6.9" rx="1.9" ry="2.6"/>'
           '<ellipse cx="14.5" cy="6.9" rx="1.9" ry="2.6"/>'
           '<ellipse cx="18.3" cy="10.1" rx="1.9" ry="2.5"/>'
           '<path d="M12.4 12.6c2.5 0 4.8 2 4.8 4.3 0 1.9-1.5 3-3.1 3-.8 0-1.2-.3-1.7-.3'
           's-.9.3-1.7.3c-1.6 0-3.1-1.1-3.1-3 0-2.3 2.3-4.3 4.8-4.3z"/>'),
  "bebida": ('<path d="M4.6 8.2h11.6v6.4a4.6 4.6 0 0 1-4.6 4.6H9.2a4.6 4.6 0 0 1-4.6-4.6V8.2z"/>'
             '<path d="M16.2 9.7h1.9a2.6 2.6 0 0 1 0 5.2h-1.9"/>'
             '<path d="M8.6 2.8c-.75.9-.75 1.8 0 2.7"/>'
             '<path d="M12.7 2.8c-.75.9-.75 1.8 0 2.7"/>'),
}
AMENIDADES = [
  ("wifi",   "WiFi gratis",        "Free WiFi"),
  ("pet",    "Pet friendly",       "Pet friendly"),
  ("bebida", "Bebida de cortesía", "Complimentary drink")]

def amenidades(lang):
    """Fila de amenidades de la portada."""
    ch = "".join(
      f'<li><svg class="ico-am" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
      f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
      f'{AMENIDAD_ICONO[k]}</svg>{e(es if lang=="es" else en)}</li>'
      for k, es, en in AMENIDADES)
    return f'<ul class="amenidades">{ch}</ul>'



# ── Portada rotatoria ─────────────────────────────────────────────────
# Tres fotos en vez de una: la portada deja de hablar solo de cabello y
# enseña las tres líneas del salón antes de que nadie baje.  El H1 no
# rota — lo que Google indexa se queda fijo.
PORTADA = [
  ("tri-cabello",  803, 1125, "hero_alt",  "Cabello y color",   "Hair & color",
   "/cabello.html",         "/en/hair.html"),
  ("tri-unas",     457,  640, "unas_alt",  "Uñas",              "Nails",
   "/unas.html",            "/en/nails.html"),
  ("tri-pestanas", 457,  640, "pest_alt",  "Pestañas y cejas",  "Lashes & brows",
   "/pestanas-y-cejas.html","/en/lashes-and-brows.html")]

def portada(lang):
    """Portada de una sola foto que se sale por el borde derecho.

    El tríptico enseñaba las tres líneas, pero eso ya lo hacen las
    tarjetas de servicio con foto cuadrada que van justo debajo. Aquí
    manda una imagen sola sobre campo limpio, que es lo que le da el
    aire de la referencia.
    """
    t = T[lang]
    return ('<div class="foto-portada">'
            + img("hero", 960, 1010, t["hero_alt"], ALTA)
            + '</div>')

# ── Marcas con las que trabajan ───────────────────────────────────────
# Logos oficiales, bajados de los sitios de cada marca y servidos desde
# /assets/marcas.  Uso nominativo: decir con qué producto trabajamos.
# Van todos en gris a la misma altura óptica para que la fila se lea
# como una sola cosa y no como cuatro logos peleando.
#   alto:  ajustado a ojo, no matemáticamente — un logo de dos renglones
#          (framesi) necesita más alto que un wordmark de uno.
#   clase: "claro" para los que vienen más tenues de origen.
#   ancho: calculado del viewBox / los píxeles reales, para que el
#          navegador reserve el hueco y la franja no brinque al cargar.
MARCAS = [
  ("alfaparf.svg",          "Alfaparf Milano",   115, 22, ""),
  ("framesi.png",           "Framesi",            99, 34, ""),
  ("brazilian-blowout.svg", "Brazilian Blowout", 142, 19, ""),
  ("split-ender.png",       "Split Ender",       107, 23, " claro"),
  ("inoar.png",             "Inoar",              94, 22, "")]

def marcas(lang):
    ms = "".join(
      f'<li class="m-logo{cl}"><img src="/assets/marcas/{f}" alt="{e(n)}" '
      f'width="{w}" height="{h}" loading="lazy" style="--h:{h}px"></li>'
      for f, n, w, h, cl in MARCAS)
    tit = ("Trabajamos con producto profesional"
           if lang == "es" else "We work with professional product")
    return (f'<section class="marcas"><div class="wrap">'
            f'<p class="marcas-t">{e(tit)}</p><ul>{ms}</ul></div></section>')


# ─────────────────────────────────────────────────────────────────────────────
# PORTAFOLIO — el trabajo real del salón, por categoría
#
# 70 fotos propias, del carrete del salón, no de Instagram: las de IG venían
# a 640px y eso era el techo de calidad de todo el sitio.  Estas son 1200×1600
# de origen; aquí salen recortadas a 3:4 (720×960) porque el cabello es
# vertical y cuadrarlo corta justamente el trabajo que se quiere enseñar.
#
# La técnica de cada foto está clasificada a ojo, mirando el degradado, el
# punto donde arranca la decoloración y el tono final.  Balayage, babylights
# y mechas se parecen en foto, así que el criterio es el que le sirve a la
# clienta que busca, no el del catálogo técnico: "balayage" para el barrido
# de raíz oscura a puntas claras, "rubios" para todo lo que termina en rubio
# frío o platino, "morenas y alisados" para el oscuro y el liso, "fantasía"
# para el color vivo.  Si una queda mal puesta, se cambia esta línea y ya.
PF_TEC = ["balayage", "rubios", "morenas", "fantasia"]

PF_ETI = {
 "es": {"balayage": ("Balayage", "desde $2,300"),
        "rubios":   ("Rubios y babylights", "desde $2,300"),
        "morenas":  ("Color y alisado", "desde $800"),
        "fantasia": ("Color fantasía", "cotización en el salón"),
        "diseno":   ("Uñas con diseño", "desde $250"),
        "tono":     ("Uñas de un tono", "desde $250"),
        "unas":     ("Uñas en gel", "desde $250"),
        "pestanas": ("Extensiones de pestañas", "desde $750")},
 "en": {"balayage": ("Balayage", "from $2,300"),
        "rubios":   ("Blondes & babylights", "from $2,300"),
        "morenas":  ("Color & smoothing", "from $800"),
        "fantasia": ("Fantasy color", "quoted in the salon"),
        "diseno":   ("Nail art", "from $250"),
        "tono":     ("Single-shade nails", "from $250"),
        "unas":     ("Gel nails", "from $250"),
        "pestanas": ("Lash extensions", "from $750")},
}

PF_CAT = {
 "es": [("cabello", "Cabello"), ("unas", "Uñas"), ("pestanas", "Pestañas")],
 "en": [("cabello", "Hair"), ("unas", "Nails"), ("pestanas", "Lashes")],
}

# Un juego de filtros por categoría.  Pestañas no lleva: clásicas, híbridas
# y volumen ruso no se distinguen con seguridad en una foto, y prefiero no
# etiquetar mal un servicio que cuesta $750 a $1,200.
PF_FILTRO = {
 "es": {"cabello": [("", "Todo"), ("balayage", "Balayage"), ("rubios", "Rubios"),
                    ("morenas", "Morenas y alisados"), ("fantasia", "Color fantasía")],
        "unas":    [("", "Todo"), ("diseno", "Con diseño"), ("tono", "De un tono")]},
 "en": {"cabello": [("", "All"), ("balayage", "Balayage"), ("rubios", "Blondes"),
                    ("morenas", "Brunettes & smoothing"), ("fantasia", "Fantasy color")],
        "unas":    [("", "All"), ("diseno", "Nail art"), ("tono", "Single shade")]},
}

PORTAFOLIO = [
  ("cabello-2", "cabello", "balayage"),
  ("cabello-3", "cabello", "balayage"),
  ("cabello-8", "cabello", "balayage"),
  ("cabello-12", "cabello", "balayage"),
  ("cabello-16", "cabello", "balayage"),
  ("cabello-20", "cabello", "balayage"),
  ("cabello-23", "cabello", "balayage"),
  ("cabello-25", "cabello", "balayage"),
  ("cabello-28", "cabello", "balayage"),
  ("cabello-32", "cabello", "balayage"),
  ("cabello-33", "cabello", "balayage"),
  ("cabello-35", "cabello", "balayage"),
  ("cabello-41", "cabello", "balayage"),
  ("cabello-48", "cabello", "balayage"),
  ("cabello-52", "cabello", "balayage"),
  ("cabello-53", "cabello", "balayage"),
  ("cabello-55", "cabello", "balayage"),
  ("cabello-58", "cabello", "balayage"),
  ("cabello-60", "cabello", "balayage"),
  ("cabello-62", "cabello", "balayage"),
  ("cabello-65", "cabello", "balayage"),
  ("cabello-70", "cabello", "balayage"),
  ("cabello-75", "cabello", "balayage"),
  ("cabello-83", "cabello", "balayage"),
  ("cabello-85", "cabello", "balayage"),
  ("cabello-89", "cabello", "balayage"),
  ("cabello-93", "cabello", "balayage"),
  ("cabello-94", "cabello", "balayage"),
  ("cabello-96", "cabello", "balayage"),
  ("cabello-103", "cabello", "balayage"),
  ("cabello-104", "cabello", "balayage"),
  ("cabello-105", "cabello", "balayage"),
  ("cabello-115", "cabello", "balayage"),
  ("cabello-188", "cabello", "balayage"),
  ("cabello-27", "cabello", "rubios"),
  ("cabello-31", "cabello", "rubios"),
  ("cabello-44", "cabello", "rubios"),
  ("cabello-47", "cabello", "rubios"),
  ("cabello-51", "cabello", "rubios"),
  ("cabello-67", "cabello", "rubios"),
  ("cabello-69", "cabello", "rubios"),
  ("cabello-74", "cabello", "rubios"),
  ("cabello-79", "cabello", "rubios"),
  ("cabello-82", "cabello", "rubios"),
  ("cabello-86", "cabello", "rubios"),
  ("cabello-88", "cabello", "rubios"),
  ("cabello-100", "cabello", "rubios"),
  ("cabello-106", "cabello", "rubios"),
  ("cabello-174", "cabello", "rubios"),
  ("cabello-180", "cabello", "rubios"),
  ("cabello-13", "cabello", "morenas"),
  ("cabello-49", "cabello", "morenas"),
  ("cabello-50", "cabello", "morenas"),
  ("cabello-68", "cabello", "morenas"),
  ("cabello-72", "cabello", "morenas"),
  ("cabello-80", "cabello", "morenas"),
  ("cabello-91", "cabello", "morenas"),
  ("cabello-5", "cabello", "fantasia"),
  ("cabello-6", "cabello", "fantasia"),
  ("cabello-15", "cabello", "fantasia"),
  ("cabello-43", "cabello", "fantasia"),
  ("cabello-63", "cabello", "fantasia"),
  ("cabello-64", "cabello", "fantasia"),
  ("cabello-107", "cabello", "fantasia"),
  ("unas-21", "unas", "diseno"),
  ("unas-38", "unas", "diseno"),
  ("unas-99", "unas", "diseno"),
  ("unas-102", "unas", "diseno"),
  ("unas-108", "unas", "diseno"),
  ("unas-124", "unas", "diseno"),
  ("unas-125", "unas", "diseno"),
  ("unas-128", "unas", "diseno"),
  ("unas-134", "unas", "diseno"),
  ("unas-137", "unas", "diseno"),
  ("unas-139", "unas", "diseno"),
  ("unas-140", "unas", "diseno"),
  ("unas-141", "unas", "diseno"),
  ("unas-145", "unas", "diseno"),
  ("unas-149", "unas", "diseno"),
  ("unas-153", "unas", "diseno"),
  ("unas-157", "unas", "diseno"),
  ("unas-158", "unas", "diseno"),
  ("unas-167", "unas", "diseno"),
  ("unas-172", "unas", "diseno"),
  ("unas-176", "unas", "diseno"),
  ("unas-179", "unas", "diseno"),
  ("unas-186", "unas", "diseno"),
  ("unas-192", "unas", "diseno"),
  ("unas-201", "unas", "diseno"),
  ("unas-42", "unas", "tono"),
  ("unas-90", "unas", "tono"),
  ("unas-116", "unas", "tono"),
  ("unas-120", "unas", "tono"),
  ("unas-126", "unas", "tono"),
  ("unas-154", "unas", "tono"),
  ("unas-168", "unas", "tono"),
  ("unas-171", "unas", "tono"),
  ("unas-198", "unas", "tono"),
  ("unas-210", "unas", "tono"),
  ("unas-217", "unas", "tono"),
  ("pestanas-98", "pestanas", ""),
  ("pestanas-110", "pestanas", ""),
  ("pestanas-112", "pestanas", ""),
  ("pestanas-113", "pestanas", ""),
  ("pestanas-114", "pestanas", ""),
  ("pestanas-118", "pestanas", ""),
  ("pestanas-119", "pestanas", ""),
  ("pestanas-123", "pestanas", ""),
  ("pestanas-129", "pestanas", ""),
  ("pestanas-132", "pestanas", ""),
  ("pestanas-133", "pestanas", ""),
  ("pestanas-159", "pestanas", ""),
  ("pestanas-163", "pestanas", ""),
  ("pestanas-164", "pestanas", ""),
  ("pestanas-169", "pestanas", ""),
  ("pestanas-175", "pestanas", ""),
  ("pestanas-178", "pestanas", ""),
  ("pestanas-183", "pestanas", ""),
  ("pestanas-184", "pestanas", ""),
  ("pestanas-189", "pestanas", ""),
  ("pestanas-194", "pestanas", ""),
  ("pestanas-195", "pestanas", ""),
  ("pestanas-196", "pestanas", ""),
  ("pestanas-205", "pestanas", ""),
  ("pestanas-209", "pestanas", ""),
  ("pestanas-213", "pestanas", ""),
  ("pestanas-216", "pestanas", ""),
  ("pestanas-219", "pestanas", "")]

def _pf_alt(lang, cat, tec):
    t = PF_ETI[lang][tec or cat][0]
    return (f"{t} hecho en Stilo Salón, Roma Norte, CDMX" if lang == "es"
            else f"{t} done at Stilo Salón, Roma Norte, Mexico City")

def portafolio_html(lang):
    cuentas = {}
    for _, cat, _ in PORTAFOLIO:
        cuentas[cat] = cuentas.get(cat, 0) + 1

    tabs = "".join(
      f'<button class="pf-tab{" activo" if i == 0 else ""}" type="button" '
      f'data-cat="{c}" aria-pressed="{"true" if i == 0 else "false"}">'
      f'{e(n)} <span class="pf-n">{cuentas.get(c, 0)}</span></button>'
      for i, (c, n) in enumerate(PF_CAT[lang]))

    filtros = "".join(
      f'<div class="pf-filtros" data-cat="{cat}"{"" if i == 0 else " hidden"}>' +
      "".join(
        f'<button class="pf-f{" activo" if t == "" else ""}" type="button" '
        f'data-tec="{t}" aria-pressed="{"true" if t == "" else "false"}">{e(n)}</button>'
        for t, n in chips) +
      '</div>'
      for i, (cat, chips) in enumerate(PF_FILTRO[lang].items()))

    piezas = []
    for f, cat, tec in PORTAFOLIO:
        titulo, precio = PF_ETI[lang][tec or cat]
        piezas.append(
          f'<figure data-cat="{cat}" data-tec="{tec}"'
          f'{"" if cat == "cabello" else " hidden"}>'
          f'<picture>'
          f'<source srcset="/assets/pf/{f}.webp" type="image/webp">'
          f'<img src="/assets/pf/{f}.jpg" width="720" height="960" '
          f'alt="{e(_pf_alt(lang, cat, tec))}" loading="lazy" decoding="async">'
          f'</picture>'
          f'<figcaption><b>{e(titulo)}</b><span>{e(precio)}</span></figcaption>'
          f'</figure>')

    vacio = ("Todavía no hay fotos en esta categoría."
             if lang == "es" else "No photos in this category yet.")
    return (f'<div class="pf">'
            f'<div class="pf-tabs">{tabs}</div>'
            f'<div class="pf-filtros-caja">{filtros}</div>'
            f'<div class="pf-rejilla js-reveal">{"".join(piezas)}</div>'
            f'<p class="pf-vacio" hidden>{e(vacio)}</p>'
            f'</div>')

def portafolio_body(lang):
    t = T[lang]
    if lang == "es":
        eyebrow = "Nuestro trabajo"
        h1 = "Portafolio"
        lede = ("Todo lo que ves aquí salió de esta silla, en Guadalajara 70-B. "
                "Sin filtros de stock ni fotos compradas: son clientas reales, "
                "con el precio publicado de cada servicio.")
        cierre = "¿Viste algo que te gustó? Te lo hacemos."
    else:
        eyebrow = "Our work"
        h1 = "Portfolio"
        lede = ("Everything here came out of this chair, at Guadalajara 70-B. "
                "No stock photos, no bought images: real clients, with the "
                "published price of each service.")
        cierre = "See something you like? We'll do it for you."
    return (f'<section class="pf-cab"><div class="wrap">'
            f'<p class="eyebrow">{e(eyebrow)}</p><h1>{e(h1)}</h1>'
            f'<p class="lede">{e(lede)}</p></div></section>'
            f'<section class="pf-sec"><div class="wrap">{portafolio_html(lang)}</div></section>'
            f'<section class="alt"><div class="wrap" style="text-align:center">'
            f'<p class="pf-cierre">{e(cierre)}</p>'
            f'<div class="btn-row" style="justify-content:center">'
            f'<a class="btn btn-primary" href="{BOOKING}" target="_blank" rel="noopener">{t["book"]}</a>'
            f'<a class="btn btn-wa" href="{WA}" rel="noopener">{t["book_wa"]}</a>'
            f'</div></div></section>')


# ── Promoción vigente ────────────────────────────────────────────────
# Una sola llave controla toda la banda.
#
# Las fechas son lo importante. El sitio es estático: si nadie lo
# regenera, una promo vencida se queda puesta, y eso es peor que no
# tener promo — dice que el salón no atiende su propia página. Por eso
# la fecha de fin viaja en el HTML y un JS la esconde sola en cuanto
# pasa, aunque nadie toque nada.
#
# tema: "" deja la banda en tinta de marca. "patrio" solo le cambia el
# color de fondo, nada más. Un disfraz de temporada en todo el sitio se
# lee barato y hay que acordarse de quitarlo; una franja que se retira
# sola, no.
PROMO = dict(
  activa = True,
  # Arranca a media semana de octubre, no el día 1: las uñas y el
  # maquillaje de temporada se apartan con una o dos semanas, y una franja
  # colgada un mes entero deja de verse.  Termina el 3 de noviembre, un día
  # después de Muertos, y se retira sola.
  desde  = "2026-10-15",
  hasta  = "2026-11-03",
  tema   = "muertos",
  url    = None,          # None = WhatsApp; o una URL propia
  es = dict(etiqueta="🎃 Halloween y Muertos",
            texto="Uñas y maquillaje de temporada",
            cta="Apartar por WhatsApp"),
  en = dict(etiqueta="🎃 Halloween",
            texto="Seasonal nail art and makeup",
            cta="Book on WhatsApp"),
)

def promo(lang):
    """Franja de promoción. No se imprime fuera de su rango de fechas."""
    if not PROMO["activa"]:
        return ""
    hoy = date.today().isoformat()
    if not (PROMO["desde"] <= hoy <= PROMO["hasta"]):
        return ""
    d = PROMO[lang]
    url = PROMO["url"] or WA
    tema = (" promo-" + PROMO["tema"]) if PROMO["tema"] else ""
    return (f'<div class="promo{tema}" data-hasta="{PROMO["hasta"]}">'
            f'<div class="wrap promo-in">'
            f'<span class="promo-tag">{e(d["etiqueta"])}</span>'
            f'<span class="promo-txt">{e(d["texto"])}</span>'
            f'<a class="promo-cta" href="{url}" rel="noopener">{e(d["cta"])}</a>'
            f'</div></div>')


# ── Adornos de la portada ─────────────────────────────────────────────
# El marco de línea viene de la referencia que le gustó al salón. La
# flor ya no la dibujo yo: es la de su propio material de marca (el
# banner de 3840x2160 que tenían en Drive), recortada del mármol con
# una máscara por saturación. Su acuarela real vale más que mi trazo.
def adornos():
    return ('<div class="deco" aria-hidden="true">'
            '<span class="d-marco"></span>'
            # Dos veces la misma pieza, en esquinas opuestas: arriba a
            # la izquierda y su espejo abajo a la derecha. Recortar
            # pimpollos sueltos de la acuarela deja el canto cuadrado y
            # se ven rotos, así que se repite entera.
            '<img class="d-flor2" src="/assets/flor-marca.png" '
            'width="980" height="627" alt="" loading="lazy">'
            '<img class="d-flor3" src="/assets/flor-marca.png" '
            'width="980" height="627" alt="" loading="lazy">'
            '</div>')

def featured_table(lang):
    t = T[lang]
    rows = []
    for key, idx in FEATURED:
        it = PRICES[key]["items"][idx]
        name = it[0] if lang == "es" else it[1]
        note = it[4] if lang == "es" else it[5]
        pre, amt = money(it[2])
        label = f'{t["from"]} {amt}' if pre else amt
        small = f'<small>{e(note)}</small>' if note else ""
        rows.append(f'<tr><td class="svc">{e(name)}{small}</td>'
                    f'<td class="amt">{e(label)}</td>'
                    f'<td class="dur">{e(it[3]) if it[3] else "—"}</td></tr>')
    return (f'<table class="price"><thead><tr><th>{t["service"]}</th>'
            f'<th style="text-align:right">{t["price"]}</th>'
            f'<th style="text-align:right">{t["dur"]}</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')

def home_body(lang):
    t, c = T[lang], C[lang]
    # Foto cuadrada arriba de cada tarjeta: es trabajo real y a 560 px se
    # sirve casi a tamaño nativo, así que se ve nítida. El icono se queda,
    # montado sobre la esquina de la foto.
    cards = "".join(
      f'<article class="card">'
      f'<a class="card-foto" href="{h}" tabindex="-1" aria-hidden="true">'
      f'<img src="/assets/card-{k}.jpg" width="560" height="560" alt="" loading="lazy">'
      f'</a>'
      # El icono sale del marco de la foto y se monta a caballo sobre el
      # canto: dentro de la imagen se perdía contra el trabajo.
      f'<div class="card-cuerpo"><span class="card-ico">{icono(k)}</span>'
      f'<h3>{e(n)}</h3><p>{e(d)}</p>'
      f'<p class="from">{e(p)}</p><a class="more" href="{h}">{e(cta)}</a></div></article>'
      for k, n, d, p, h, cta in c["svc_cards"])
    why = "".join(f'<div><h3>{e(h)}</h3><p>{e(b)}</p></div>' for h, b in c["why"])
    faqs = "".join(
      f'<details class="faq"{" open" if i==0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>'
      for i, (q, a) in enumerate(c["faq"]))
    hi = "Roma Norte · Ciudad de México" if lang=="es" else "Roma Norte · Mexico City"
    return f"""
<section class="hero">
  <img class="marca-agua" src="/assets/logo-stilo-salon.png" width="640" height="252" alt="" aria-hidden="true" loading="lazy">
  {adornos()}
  {portada(lang)}
  <div class="wrap hero-grid"><div>
  <p class="eyebrow">{hi}</p>
  <h1 class="h1-firma"><em>{e(c["home_h1"][0])}</em><br>{e(c["home_h1"][1])}</h1>
  <p class="lede">{e(c['home_lede'])}</p>
  <div class="btn-row btn-row-hero">
    <a class="btn btn-primary" href="{BOOKING}" target="_blank" rel="noopener">{t['book']}</a>
  </div>
  <div class="hero-alt">
    <span>{'o escríbenos' if lang=='es' else 'or reach us'}</span>
    <a class="ic-red ic-wa" href="{WA}" rel="noopener"
       aria-label="{t['wa_aria']}" title="{t['wa_aria']}">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="{WA_PATH}"/></svg></a>
    <a class="ic-red ic-tel" href="tel:{NAP['tel1']}"
       aria-label="{'Llámanos al' if lang=='es' else 'Call us at'} {NAP['tel1_display']}"
       title="{NAP['tel1_display']}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
           stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
        <path d="M6.3 3.5h3l1.5 3.7-1.9 1.4a12.5 12.5 0 0 0 5.5 5.5l1.4-1.9 3.7 1.5v3a1.8 1.8 0 0 1-2 1.8A15.6 15.6 0 0 1 4.5 5.5a1.8 1.8 0 0 1 1.8-2z"/>
      </svg></a>
    <a class="hero-tel" href="tel:{NAP['tel1']}">{NAP['tel1_display']}</a>
  </div>
</div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Nuestros servicios' if lang=='es' else 'Our services'}</p>
  <h2>{'Todo lo que hacemos, con su precio' if lang=='es' else 'Everything we do, with its price'}</h2></div>
  <div class="grid g4 js-reveal">{cards}</div>
</div></section>

<section class="cifras"><div class="wrap">
  <div class="trust">
    <div><strong>+10</strong>{'años en Roma Norte' if lang=='es' else 'years in Roma Norte'}</div>
    <div><a href="{GMB}" rel="noopener" style="text-decoration:none;color:inherit"><strong>{OPINIONES}</strong>{'opiniones en Google' if lang=='es' else 'Google reviews'}</a></div>
    <div><strong>72 h</strong>{'de garantía en cada servicio' if lang=='es' else 'guarantee on every service'}</div>
    <div><strong>3 {'meses' if lang=='es' else 'months'}</strong>{'sin intereses desde $2,000' if lang=='es' else 'interest-free from $2,000'}</div>
  </div>
</div></section>

{marcas(lang)}


<section class="valora"><div class="wrap">
  <div class="valora-in">
    <div>
      <p class="eyebrow">{'Antes de agendar' if lang=='es' else 'Before you book'}</p>
      <h2>{'¿No sabes qué servicio necesitas?' if lang=='es' else 'Not sure which service you need?'}</h2>
      <p class="lede">{'Pide una cita de valoración: mándanos una foto de tu cabello, tus uñas o tus pestañas por WhatsApp y te decimos qué te conviene, cuánto cuesta y cuánto tarda — antes de que reserves nada. Si la respuesta honesta es un tratamiento de $520 y no un alisado de $2,500, te lo vamos a decir.' if lang=='es' else 'Ask for a valuation: send us a photo of your hair, nails or lashes on WhatsApp and we will tell you what suits you, what it costs and how long it takes — before you book anything. If the honest answer is a $520 treatment rather than a $2,500 smoothing service, we will say so.'}</p>
    </div>
    <div class="btn-row">
      <a class="btn btn-wa" href="{WA_VALORA}" rel="noopener">{'Pedir mi valoración' if lang=='es' else 'Ask for my valuation'}</a>
      <a class="btn btn-ghost" href="{'/precios.html' if lang=='es' else '/en/pricing.html'}">{'Ver la lista de precios' if lang=='es' else 'See the price list'}</a>
    </div>
  </div>
</div></section>

<section class="ink-sec"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Por qué Stilo' if lang=='es' else 'Why Stilo'}</p>
  <h2>{e(c['home_why_h2'])}</h2></div>
  <div class="grid g3 js-reveal">{why}</div>
</div></section>

<section><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Los más pedidos' if lang=='es' else 'Most requested'}</p>
  <h2>{'Lo que más nos piden en Roma Norte' if lang=='es' else 'What Roma Norte asks us for most'}</h2>
  <p class="lede">{t['mxn']}</p></div>
  {featured_table(lang)}
  <div class="btn-row"><a class="btn btn-primary" href="{'/precios.html' if lang=='es' else '/en/pricing.html'}">{t['full_list']}</a></div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Preguntas frecuentes' if lang=='es' else 'Frequently asked'}</p>
  <h2>{'Lo que nos preguntan antes de agendar' if lang=='es' else 'What people ask before booking'}</h2></div>
  {faqs}
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Dónde encontrarnos' if lang=='es' else 'Find us'}</p>
  <h2>{'Búscanos y léenos' if lang=='es' else 'Look us up and read us'}</h2>
  <p class="lede">{f'Ya somos {OPINIONES} opiniones en Google. Si ya viniste, la tuya nos ayuda muchísimo a que más clientas nos encuentren.' if lang=='es' else f'We are at {OPINIONES} Google reviews. If you have been here, yours helps more clients find us.'}</p></div>
  <div class="perfiles">
    <a class="perfil" href="{GMB}" rel="noopener">
      <strong>Google</strong><span>{f'{OPINIONES} opiniones · cómo llegar' if lang=='es' else f'{OPINIONES} reviews · directions'}</span></a>
    <a class="perfil" href="https://www.instagram.com/stilosalon91/" rel="noopener">
      <strong>Instagram</strong><span>@stilosalon91</span></a>
    <a class="perfil destacado" href="{RESENA}" target="_blank" rel="noopener">
      <strong>{'Escribe tu reseña' if lang=='es' else 'Write your review'}</strong><span>{'Se abre directo en Google · toma menos de un minuto' if lang=='es' else 'Opens straight in Google · under a minute'}</span></a>
  </div>
</div></section>

<section id="contacto"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Visítanos' if lang=='es' else 'Visit us'}</p><h2>{e(c['visit_h2'])}</h2></div>
  <div class="grid g2"><div>
    <h3>{t['branch']}</h3>
    <address><strong>{NAP['street']}</strong><br>{NAP['locality']}<br>{NAP['postal']}, {NAP['city']}<br><br>
    {t['appts']}: <a href="tel:{NAP['tel1']}">{NAP['tel1_display']}</a><br>
    <a href="tel:{NAP['tel2']}">{NAP['tel2_display']}</a></address>
    <p style="margin-top:1.4rem"><strong>{t['mf']}</strong> 9:00 – 20:00<br><strong>{t['sat']}</strong> 9:00 – 19:00<br><strong>{t['sun']}</strong> {t['closed']}</p>
    {amenidades(lang)}
    <div class="btn-row"><a class="btn btn-primary" href="{BOOKING}" target="_blank" rel="noopener">{t['book']}</a>
    <a class="btn btn-wa" href="{WA}" rel="noopener">WhatsApp</a>
    <a class="btn btn-ghost" href="https://maps.google.com/?q=Guadalajara+70-B,+Roma+Norte,+CDMX" rel="noopener">{t['directions']}</a></div>
  </div>
  <div>
    <a class="mapa" href="{GMB}" target="_blank" rel="noopener"
       aria-label="{'Ver la ubicación de Stilo Salón en Google Maps' if lang=='es' else 'See Stilo Salón on Google Maps'}">
      <img src="/assets/mapa-roma-norte.jpg" width="1200" height="900" loading="lazy"
           alt="{'Mapa de Roma Norte con la ubicación de Stilo Salón en Calle Guadalajara 70-B, entre Durango y Colima' if lang=='es' else 'Map of Roma Norte showing Stilo Salón at Calle Guadalajara 70-B, between Durango and Colima'}">
      <span class="mapa-pie">{'Abrir en Google Maps' if lang=='es' else 'Open in Google Maps'}</span>
    </a>
    <p class="mapa-cred">{'Mapa © colaboradores de' if lang=='es' else 'Map © '}
      <a href="https://www.openstreetmap.org/copyright" rel="noopener nofollow">OpenStreetMap</a></p>
  </div>
  </div>
</div></section>
"""

def svc_body(lang, eyebrow, h1, intro, paras, keys, note="", extra="", banner="", alt_foto="", nivel=3):
    t = T[lang]
    body = "".join(f"<p>{p}</p>" for p in paras)
    # La foto va al lado del texto, no en una tira horizontal arriba del
    # contenido.  Antes era una imagen 16:9 aplastada por CSS a 240px de
    # alto sobre 1080 de ancho — un recorte de 4.5:1 que decapitaba a la
    # clienta y dejaba una franja de cabello sin contexto.
    foto = (f'<figure class="svc-foto">'
            f'{img(banner[:-4], 900, 1200, alt_foto, TARDE)}</figure>') if banner else ''
    return f"""
<section class="svc-cab"><div class="wrap svc-cab-in">
  <div class="svc-cab-txt">
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1>{e(h1)}</h1>
    <p class="lede">{e(intro)}</p>
  </div>
  {foto}
</div></section>
<section class="alt" style="padding-top:0"><div class="wrap" style="max-width:74ch">{body}{extra}</div></section>
<section><div class="wrap">
  <p class="muted" style="font-size:.9rem">{t['mxn']} {e(note)}</p>
  {table(keys, lang, nivel)}
  <div class="btn-row"><a class="btn btn-primary" href="{BOOKING}" target="_blank" rel="noopener">{t['book']}</a>
  <a class="btn btn-wa" href="{WA}" rel="noopener">{t['book_wa']}</a>
  <a class="btn btn-ghost" href="tel:{NAP['tel1']}">{NAP['tel1_display']}</a></div>
</div></section>
"""

# ─────────────────────────────────────────────────────────────────────────────
# PÁGINAS DE SERVICIO — el texto largo vive aquí.  Google necesita leer esto:
# las páginas de 100 palabras no compiten.
# ─────────────────────────────────────────────────────────────────────────────
SERVICE_PAGES = [
 dict(key="hair", es_slug="/cabello.html", en_slug="/en/hair.html",
   keys=["cabello", "tratamientos"],
   es=dict(eyebrow="Cabello y color · Roma Norte",
     title="Corte, Color y Balayage en Roma Norte, CDMX | Stilo Salón",
     desc="Corte dama desde $330, tinte desde $800, balayage desde $2,300, nanoplastia desde $2,500. Precios y duraciones publicados. Guadalajara 70-B, Roma Norte, CDMX.",
     h1="Corte, color y tratamientos de cabello en Roma Norte",
     intro="Todo el trabajo de cabello que hacemos, con su precio y su duración real. Sin cotizaciones por mensaje privado y sin ajustes de último momento.",
     paras=[
      "En Stilo Salón trabajamos el cabello en tres frentes: <strong>corte</strong>, <strong>color</strong> y <strong>tratamiento</strong>. Cada uno tiene su propia lógica de tiempo y de producto, y por eso publicamos las duraciones junto a los precios. Un corte de dama con lavado y peinado son treinta minutos. Un balayage son tres horas. Saber eso de antemano te permite agendar sin que el día se te desacomode.",
      "En <strong>corte</strong> manejamos dama, caballero y niños. La diferencia entre el corte con moldeado ($330) y el corte con lavado y peinado ($420) es justamente el lavado y el peinado terminado: si vienes con prisa o ya con el cabello lavado, el primero te sirve; si quieres salir lista, el segundo.",
      "En <strong>color</strong> cubrimos desde lo más sencillo hasta lo más técnico. El <strong>retoque de raíz</strong> ($900) es el mantenimiento mensual de un color que ya traes. El <strong>tinte</strong> (desde $800) es color completo. El <strong>matiz</strong> y el <strong>baño de color</strong> (desde $900) corrigen o refrescan el tono sin levantar el color base. Y el <strong>balayage</strong> y los <strong>babylights</strong> (desde $2,300, tres horas) son técnicas de iluminación a mano alzada que crean dimensión natural, con crecimiento suave: no te dejan una línea de raíz marcada a las seis semanas.",
      "Los precios de color marcados “desde” aplican de hombro hacia arriba. El cabello más largo o más denso lleva más producto y más tiempo, y el ajuste te lo decimos <strong>antes</strong> de empezar, con el espejo enfrente. Nunca al momento de cobrar.",
      "En <strong id='tratamientos'>tratamientos y alisados</strong> trabajamos tres técnicas distintas, y la diferencia importa. La <strong>nanoplastia</strong> (desde $2,500) es un alisado sin formol que reestructura la fibra capilar y deja el cabello liso y con brillo por varios meses. El <strong>Brazilian Blowout</strong> (desde $2,500) es el que mucha gente pide como <strong>keratina</strong>: sella la cutícula y reduce el frizz manteniendo movimiento — no deja el cabello completamente lacio. El <strong>botox capilar</strong> (desde $1,800, una hora) no alisa: rellena y repara cabello poroso o maltratado por decoloración.",
      "Si no sabes cuál te conviene, escríbenos por WhatsApp con una foto de tu cabello y te decimos con honestidad cuál sí y cuál no. A veces la respuesta es un <strong>tratamiento profundo hidratante</strong> de $520 y no un alisado de $2,500.",
      "Todos nuestros servicios tienen <strong>72 horas de garantía</strong>: si algo no quedó como lo acordamos, regresas y lo corregimos sin costo. Y en compras desde $2,000 manejamos <strong>3 meses sin intereses</strong> con todas las tarjetas de crédito."]),
   en=dict(eyebrow="Hair & color · Roma Norte",
     title="Haircuts, Color & Balayage in Roma Norte | Stilo Salón",
     desc="Women's cut from $330, color from $800, balayage from $2,300, nanoplasty from $2,500 MXN. Published prices and durations. Roma Norte, Mexico City.",
     h1="Haircuts, color and hair treatments in Roma Norte",
     intro="All the hair work we do, with its real price and duration. No quotes by private message, and no last-minute adjustments.",
     paras=[
      "At Stilo Salón we work hair on three fronts: <strong>cutting</strong>, <strong>color</strong> and <strong>treatment</strong>. Each has its own logic of time and product, which is why we publish durations alongside prices. A women's cut with wash and style is thirty minutes. A balayage is three hours. Knowing that in advance lets you book without losing your day.",
      "For <strong>cuts</strong> we serve women, men and children. The difference between the cut with blow-dry shaping ($330) and the cut with wash and style ($420) is exactly that — the wash and the finished style. If you are in a hurry or arrive with clean hair, the first works; if you want to walk out ready, take the second.",
      "In <strong>color</strong> we cover everything from the simplest to the most technical. A <strong>root touch-up</strong> ($900) is monthly maintenance on color you already have. <strong>Full color</strong> (from $800) covers the whole head. <strong>Toner</strong> and <strong>color gloss</strong> (from $900) correct or refresh the tone without lifting the base. And <strong>balayage</strong> and <strong>babylights</strong> (from $2,300, three hours) are freehand lightening techniques that build natural dimension with a soft grow-out — no hard root line at six weeks.",
      "Color prices marked “from” apply at shoulder length and above. Longer or denser hair takes more product and more time, and we tell you that adjustment <strong>before</strong> we begin, with the mirror in front of you. Never at the register.",
      "In <strong id='tratamientos'>treatments and smoothing</strong> we work three distinct techniques, and the difference matters. <strong>Nanoplasty</strong> (from $2,500) is a formaldehyde-free smoothing service that restructures the hair fiber, leaving it straight and glossy for several months. <strong>Brazilian Blowout</strong> (from $2,500) is the one most people ask for as a <strong>keratin treatment</strong>: it seals the cuticle and cuts frizz while keeping movement — it does not leave hair perfectly flat. <strong>Hair botox</strong> (from $1,800, one hour) does not straighten: it fills and repairs porous hair damaged by bleaching.",
      "If you are not sure which one suits you, message us on WhatsApp with a photo of your hair and we will tell you honestly which will work and which will not. Sometimes the answer is a $520 deep hydrating treatment rather than a $2,500 smoothing service.",
      "Every service carries a <strong>72-hour guarantee</strong>: if something did not turn out the way we agreed, come back and we will correct it at no cost. On purchases from $2,000 we offer <strong>3 interest-free monthly payments</strong> with any credit card."])),
 dict(key="nails", es_slug="/unas.html", en_slug="/en/nails.html",
   keys=["mani-pedi", "gel-esmalte", "unas"],
   es=dict(eyebrow="Uñas · Roma Norte",
     title="Uñas, Manicure y Pedicure en Roma Norte, CDMX | Stilo Salón",
     desc="Manicure spa desde $220, gel desde $180, acrílico desde $400, esculturales desde $500. Paquete mani + pedi con gel $750. Roma Norte, CDMX.",
     h1="Uñas, manicure y pedicure en Roma Norte",
     intro="Desde un esmalte sencillo hasta esculturales con gel. Toda la lista con precio, para que elijas sin preguntar.",
     paras=[
      "Nuestro servicio de uñas se divide en tres bloques: <strong>manicure y pedicure</strong>, <strong>gel y esmalte</strong>, y <strong>acrílico y esculturales</strong>. La diferencia entre ellos es sobre todo de duración del resultado y de cuidado de la uña natural.",
      "El <strong>manicure spa</strong> ($220) incluye tina con sales, exfoliación, masaje y esmalte — es el servicio completo de cuidado, no solo el color. Si quieres que dure más, el <strong>manicure spa + gel</strong> ($350) cambia el esmalte por gel, que aguanta entre dos y tres semanas sin despostillarse. El <strong>pedicure spa</strong> ($360) añade limado de talón y masaje de pies.",
      "Si vas a hacer manos y pies el mismo día, el <strong>paquete de mani spa + pedi spa con gel</strong> ($750) es la opción conveniente: los dos servicios completos con gel en ambos.",
      "En <strong>gel y esmalte</strong> cobramos por separado cuando solo quieres el color: <strong>gel en manos</strong> ($180), <strong>gel en pies</strong> ($220) o <strong>esmalte tradicional</strong> ($150). Todos incluyen hasta dos tonos lisos; los tonos adicionales o los diseños tienen un costo extra pequeño que te decimos antes.",
      "Las <strong>vitaminas</strong> ($150) son tratamientos para la uña natural, no color. El <strong>calcio</strong> fortalece, el <strong>rubber</strong> cubre imperfecciones y da cuerpo a uñas delgadas o débiles, y la <strong>vitamina</strong> protege mientras la uña se recupera. Si traes las uñas maltratadas después de mucho acrílico, empieza por aquí.",
      "En <strong>acrílico y esculturales</strong> manejamos acrílico sobre uña natural ($400), uña escultural con gel (desde $500) y uña tip con gel (desde $450). Los retoques son más económicos que el juego completo y te recomendamos hacerlos cada tres o cuatro semanas: esperar más tiempo daña la uña natural. El <strong>retiro</strong> ($100) lo hacemos siempre con técnica, nunca arrancando.",
      "Una nota honesta: no todas las manos necesitan acrílico. Si tu uña natural está en buen estado, un gel bien puesto se ve igual de bien y cuida más. Te lo vamos a decir.",
      "Las <strong>uñas en gel tienen 5 días de garantía</strong> — el resto de nuestros servicios, 72 horas. Si se te despostilla algo dentro de ese plazo, regresas y lo corregimos sin costo."]),
   en=dict(eyebrow="Nails · Roma Norte",
     title="Nails, Manicure & Pedicure in Roma Norte | Stilo Salón",
     desc="Spa manicure from $220, gel from $180, acrylic from $400, sculpted nails from $500 MXN. Mani + pedi gel package $750. Roma Norte, Mexico City.",
     h1="Nails, manicure and pedicure in Roma Norte",
     intro="From a simple polish to sculpted gel nails. The whole list with prices, so you can choose without asking.",
     paras=[
      "Our nail work splits into three blocks: <strong>manicure and pedicure</strong>, <strong>gel and polish</strong>, and <strong>acrylic and sculpted nails</strong>. The difference between them is mostly how long the result lasts and how it treats your natural nail.",
      "The <strong>spa manicure</strong> ($220) includes a salt soak, exfoliation, massage and polish — it is the full care service, not just color. If you want it to last longer, the <strong>spa manicure + gel</strong> ($350) swaps polish for gel, which holds two to three weeks without chipping. The <strong>spa pedicure</strong> ($360) adds heel filing and a foot massage.",
      "If you are doing hands and feet the same day, the <strong>spa mani + spa pedi package with gel</strong> ($750) is the convenient option: both full services with gel on each.",
      "In <strong>gel and polish</strong> we charge separately when you only want color: <strong>gel on hands</strong> ($180), <strong>gel on feet</strong> ($220) or <strong>regular polish</strong> ($150). All include up to two solid shades; additional shades or designs carry a small extra cost that we tell you beforehand.",
      "<strong>Nail vitamins</strong> ($150) are treatments for the natural nail, not color. <strong>Calcium</strong> strengthens, <strong>rubber base</strong> covers imperfections and adds body to thin or weak nails, and <strong>nail vitamin</strong> protects while the nail recovers. If your nails are worn down after a long stretch of acrylic, start here.",
      "In <strong>acrylic and sculpted nails</strong> we offer acrylic over the natural nail ($400), sculpted gel nails (from $500) and gel tips (from $450). Fills cost less than a full set, and we recommend them every three or four weeks — waiting longer damages the natural nail. <strong>Removal</strong> ($100) is always done properly, never by prying.",
      "One honest note: not every hand needs acrylic. If your natural nail is in good shape, a well-applied gel looks just as good and treats it better. We will tell you so.",
      "<strong>Gel nails carry a 5-day guarantee</strong> — every other service, 72 hours. If anything chips within that window, come back and we will fix it at no cost."])),
 dict(key="lashes", es_slug="/pestanas-y-cejas.html", en_slug="/en/lashes-and-brows.html",
   keys=["pestanas", "cejas", "depilacion"],
   es=dict(eyebrow="Pestañas y cejas · Roma Norte",
     title="Extensiones de Pestañas y Cejas en Roma Norte | Stilo Salón",
     desc="Extensiones de pestañas desde $750: 1x1, flat, YY, híbridas y volumen ruso. Lifting $450, laminado de ceja $450. Roma Norte, CDMX. Citas: 55 2299 3258.",
     h1="Extensiones de pestañas y diseño de cejas en Roma Norte",
     intro="¿Quieres saber cuánto cuestan? ¿Qué técnicas existen? ¿Cuál es apta para ti? ¿Cuánto duran? Aquí está toda la información detallada de esta maravillosa forma de lucir unos ojos y unas cejas de impacto.",
     paras=[]),
   en=dict(eyebrow="Lashes & brows · Roma Norte",
     title="Eyelash Extensions & Brows in Roma Norte | Stilo Salón",
     desc="Eyelash extensions from $750 MXN: classic 1x1, flat, YY, hybrid and Russian volume. Lash lift $450, brow lamination $450. Roma Norte, Mexico City.",
     h1="Eyelash extensions and brow design in Roma Norte",
     intro="Want to know what they cost? Which techniques exist? Which one suits you? How long they last? Here is everything you need to know about this wonderful way to get eyes and brows with real impact.",
     paras=[]))]

# ─────────────────────────────────────────────────────────────────────────────
# GUÍA DE PESTAÑAS — contenido propio del salón. Es el mejor activo editorial
# que tienen: responde las búsquedas informativas ("cuánto duran", "cómo se
# cuidan") que hoy no capturan.
# ─────────────────────────────────────────────────────────────────────────────
TECNICAS = [
 dict(id="tecnica-1x1", precio="$750", dur="1 hora 30 minutos", retoque="$450",
   es=dict(n="Técnica 1x1 o clásica",
     q="Se coloca una extensión por cada una de tus pestañas naturales. Es set completo, así que lo tupido depende de la cantidad de pestaña que tengas.",
     p="Es la técnica de entrada y la más natural. Si nunca has usado extensiones, empieza aquí."),
   en=dict(n="Classic 1x1",
     q="One extension on each of your natural lashes. It is a full set, so how dense it looks depends on how much natural lash you have.",
     p="This is the entry technique and the most natural. If you have never worn extensions, start here.")),
 dict(id="tecnica-flat", precio="$800", dur="1 hora 30 minutos", retoque="$500",
   es=dict(n="Técnica flat",
     q="Usa una fibra de base plana que abraza tu pestaña natural en lugar de apoyarse en un punto.",
     p="Pesa menos y se adhiere mejor, por eso funciona bien si tienes la pestaña delgada o quebradiza."),
   en=dict(n="Flat",
     q="Uses a flat-based fiber that wraps your natural lash instead of resting on a single point.",
     p="It weighs less and bonds better, so it works well if your lashes are fine or brittle.")),
 dict(id="tecnica-yy", precio="$1,000", dur="1 hora 30 minutos", retoque="$550",
   es=dict(n="Técnica YY",
     q="Fibras entrelazadas en forma de Y: cada extensión cubre el doble sin pesar el doble.",
     p="Da sensación de mayor densidad sin cargar la pestaña natural. Buen punto medio entre el 1x1 y el volumen."),
   en=dict(n="YY",
     q="Y-shaped interlaced fibers: each extension covers twice the area without twice the weight.",
     p="It creates a denser look without loading the natural lash. A good middle ground between classic and volume.")),
 dict(id="tecnica-hibrida", precio="$1,100", dur="2 horas", retoque="$550",
   es=dict(n="Técnica híbrida",
     q="Combina 1x1 y volumen: se coloca una extensión clásica y un grupo de volumen, alternando.",
     p="Se ven más tupidas aunque no tengas mucha pestaña natural. Es el punto medio, y la que más nos piden."),
   en=dict(n="Hybrid",
     q="Combines 1x1 and volume: one classic extension and one volume fan, alternating.",
     p="Looks fuller even without much natural lash. It is the middle ground, and the set we are asked for most.")),
 dict(id="tecnica-volumen", precio="$1,200", dur="2 horas", retoque="$650",
   es=dict(n="Técnica volumen ruso",
     q="Se colocan tres extensiones por cada pestaña tuya, en abanico.",
     p="No la recomendamos si antes no usaste híbridas o clásicas: hay que ir preparando tu pestaña para el peso."),
   en=dict(n="Russian volume",
     q="Three extensions in a fan on each of your natural lashes.",
     p="We do not recommend it if you have not worn hybrid or classic first — the natural lash needs to be prepared for the weight."))]

CUIDADOS = {
 "es": ["No mojar las pestañas durante las primeras 24 horas.",
        "No usar productos grasos para desmaquillarte; de preferencia agua micelar.",
        "No usar vapor ni sauna.",
        "Cepillar y lavar a diario — que el agua caiga en tus pestañas al menos una vez al día.",
        "No utilizar rímel.",
        "No frotar tus ojos bruscamente.",
        "Hacer un retoque cada dos o tres semanas."],
 "en": ["Keep lashes dry for the first 24 hours.",
        "Do not use oil-based removers; micellar water is best.",
        "No steam and no sauna.",
        "Brush and wash daily — let water run over your lashes at least once a day.",
        "Do not use mascara.",
        "Do not rub your eyes hard.",
        "Book a fill every two to three weeks."],
}

CUIDADOS_LIFT = {
 "es": ["No mojar durante las primeras 24 horas.",
        "No usar vapor ni sauna.",
        "No usar aceite de bebé; solo aceite de almendras o agua micelar.",
        "Puedes usar rímel después de 24 horas.",
        "Evitar agua muy caliente los primeros tres días."],
 "en": ["Keep dry for the first 24 hours.",
        "No steam and no sauna.",
        "No baby oil — almond oil or micellar water only.",
        "You can wear mascara after 24 hours.",
        "Avoid very hot water for the first three days."],
}

def lash_guide(lang):
    es = lang == "es"
    out = [f'<h2>{"La biblia de las extensiones de pestañas y cejas" if es else "The eyelash and brow bible"}</h2>']
    out.append('<p>' + ("Todo lo que nos preguntan en la silla, escrito. Empecemos por lo primero: cuál es cuál."
        if es else "Everything people ask us in the chair, written down. First things first: which one is which.") + '</p>')
    out.append(f'<h3>{"Las cinco técnicas" if es else "The five techniques"}</h3>')
    for t in TECNICAS:
        d = t[lang]
        out.append(f'<h4 id="{t["id"]}">{e(d["n"])} — {t["precio"]}</h4>')
        out.append(f'<p>{e(d["q"])} {e(d["p"])}</p>')
        out.append(f'<p class="muted">{"Aplicación" if es else "Application"}: {t["dur"]} · '
                   f'{"Retoque" if es else "Fill"}: {t["retoque"]}</p>')
    out.append(f'<h2>{"Por qué los retoques son necesarios" if es else "Why fills are necessary"}</h2>')
    out.append('<p>' + ("Tus pestañas cumplen un ciclo de vida: se caen alrededor de <strong>cuatro o cinco al día</strong>, "
        "y con cada una se va su extensión. Por eso el retoque no es un extra, es parte del servicio. "
        "Las extensiones <strong>no maltratan ni tiran</strong> tu pestaña natural — lo que ves caer es el ciclo normal."
        if es else
        "Your lashes follow a growth cycle: you shed roughly <strong>four or five a day</strong>, and each one takes its "
        "extension with it. That is why a fill is not an extra, it is part of the service. Extensions "
        "<strong>do not damage or pull out</strong> your natural lashes — what you see falling is the normal cycle.") + '</p>')
    out.append('<p>' + ("El retoque se cobra <strong>a evaluación de la lashista</strong>, según tus cuidados, tu crecimiento y "
        "cuánta pestaña conserves: necesitas al menos el <strong>50%</strong> puesta. "
        "Pasados los <strong>21 días</strong> ya no es retoque — la mayor parte de las extensiones se habrá caído, "
        "así que se cobra retiro ($150) más aplicación nueva."
        if es else
        "The fill is priced <strong>at the lash artist's assessment</strong>, based on your aftercare, your growth and how much "
        "lash you still have: you need at least <strong>50%</strong> retention. Past <strong>21 days</strong> it is no longer a "
        "fill — most extensions will have shed — so it is charged as removal ($150) plus a new set.") + '</p>')
    out.append(f'<h2>{"Cuidados de tus extensiones" if es else "Caring for your extensions"}</h2>')
    out.append("<ul>" + "".join(f"<li>{e(c)}</li>" for c in CUIDADOS[lang]) + "</ul>")
    out.append('<p>' + ("La duración de tus extensiones depende directamente del cuidado que les des. "
        "Bien cuidadas y con retoque puntual, duran el tiempo que tú quieras."
        if es else
        "How long your extensions last depends directly on how you care for them. Well cared for and filled on "
        "schedule, they last as long as you want them to.") + '</p>')
    out.append(f'<h2>{"Lifting de pestañas — $450" if es else "Lash lift — $450"}</h2>')
    out.append('<p>' + ("El lifting eleva tu <strong>pestaña natural desde la raíz</strong> para dar un efecto natural. "
        "No se usa pelo sintético: el proceso va con pigmento y keratina, así que no daña la pestaña. "
        "Incluye tinte negro y dura entre <strong>mes y medio y dos meses</strong>, según la persona y sus cuidados. "
        "La aplicación toma una hora y puedes repetirlo cuantas veces quieras."
        if es else
        "A lash lift raises your <strong>natural lash from the root</strong> for a natural effect. No synthetic hair is used: "
        "the process uses pigment and keratin, so it does not damage the lash. It includes black tint and lasts "
        "<strong>six to eight weeks</strong>, depending on the person and their aftercare. Application takes an hour and you "
        "can repeat it as often as you like.") + '</p>')
    out.append("<ul>" + "".join(f"<li>{e(c)}</li>" for c in CUIDADOS_LIFT[lang]) + "</ul>")
    out.append(f'<h2>{"Cejas: diseño y laminado" if es else "Brows: design and lamination"}</h2>')
    out.append('<p>' + ("El <strong>diseño de ceja</strong> ($450) combina trazado, depilación y planchado, mapeado a tu rostro. "
        "El <strong>laminado de ceja</strong> ($450) sigue el mismo proceso, pero el planchado va <strong>hacia arriba</strong>, "
        "que es lo que da el efecto de ceja más poblada y peinada."
        if es else
        "<strong>Brow design</strong> ($450) combines mapping, waxing and pressing, shaped to your face. "
        "<strong>Brow lamination</strong> ($450) follows the same process, but the hair is pressed <strong>upward</strong>, "
        "which is what creates the fuller, brushed-up look.") + '</p>')
    out.append('<p class="muted">' + ("También hacemos depilación con cera de rostro y axilas, y maquillaje ($950) para eventos. "
        "La lista completa está abajo."
        if es else "We also offer facial and underarm waxing, and makeup application ($950) for events. "
        "The full list is below.") + '</p>')
    return "\n".join(out)

def lash_faq_ld(lang):
    es = lang == "es"
    qa = ([("¿Cuánto duran las extensiones de pestañas?",
            "Duran el tiempo que quieras, siempre que las retoques cada dos o tres semanas y las cuides. Tus pestañas naturales se caen entre cuatro y cinco al día y con ellas se va la extensión, por eso el retoque es parte del servicio."),
           ("¿Las extensiones maltratan mis pestañas naturales?",
            "No. Las extensiones no maltratan ni tiran la pestaña natural. Lo que ves caer es el ciclo de vida normal de tu pestaña."),
           ("¿Cada cuándo tengo que retocar?",
            "Cada dos o tres semanas. Necesitas conservar al menos el 50% de la pestaña puesta. Pasados 21 días ya no aplica retoque: se cobra retiro más aplicación nueva."),
           ("¿Qué técnica me conviene si es mi primera vez?",
            "La técnica 1x1 o clásica, de $750. El volumen ruso no se recomienda si antes no usaste híbridas o clásicas, porque hay que preparar tu pestaña para el peso."),
           ("¿Puedo usar rímel con extensiones?",
            "No. Con extensiones no se usa rímel. Con lifting de pestañas sí, después de las primeras 24 horas."),
           ("¿Cuánto dura el lifting de pestañas?",
            "Entre mes y medio y dos meses, según la persona y sus cuidados. Incluye tinte negro y keratina, y no usa pelo sintético.")]
          if es else
          [("How long do eyelash extensions last?",
            "They last as long as you want, provided you get a fill every two to three weeks and care for them. Your natural lashes shed four to five a day and the extension goes with them, which is why fills are part of the service."),
           ("Do extensions damage my natural lashes?",
            "No. Extensions do not damage or pull out the natural lash. What you see shedding is your lashes' normal growth cycle."),
           ("How often do I need a fill?",
            "Every two to three weeks. You need to keep at least 50% retention. Past 21 days a fill no longer applies: it is charged as removal plus a new set."),
           ("Which technique should I choose for my first time?",
            "Classic 1x1, at $750. Russian volume is not recommended unless you have worn hybrid or classic first, because the natural lash needs to be prepared for the weight."),
           ("Can I wear mascara with extensions?",
            "No. Mascara is not used with extensions. With a lash lift you can, after the first 24 hours."),
           ("How long does a lash lift last?",
            "Six to eight weeks, depending on the person and their aftercare. It includes black tint and keratin, and uses no synthetic hair.")])
    body = ",".join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
                    % (_j(q), _j(a)) for q, a in qa)
    return ('<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}</script>' % body)

# ─────────────────────────────────────────────────────────────────────────────
# GUÍAS DE CABELLO Y UÑAS
# Escritas para responder búsquedas informativas reales ("diferencia entre
# balayage y babylights", "acrílico o gel", "cada cuándo retocar raíz").
# REVISAR: el salón debe confirmar que todo coincide con su práctica.
# ─────────────────────────────────────────────────────────────────────────────
def hair_guide(lang):
    es = lang == "es"
    o = []
    o.append(f'<h2>{"Balayage, babylights y matiz: cuál es cuál" if es else "Balayage, babylights and toner: which is which"}</h2>')
    o.append('<p>' + ("Son las tres cosas que más nos preguntan, y se confunden seguido. "
      "El <strong>balayage</strong> se pinta a mano alzada, barriendo el color de medios a puntas: deja una transición suave "
      "y crece sin línea marcada, por eso aguanta meses sin retoque. Los <strong>babylights</strong> son mechones muy finos "
      "tomados desde la raíz, que imitan el aclarado natural del sol en el cabello de un niño — se ven más parejos y "
      "menos contrastados que el balayage. Ambos toman tres horas y arrancan en $2,300."
      if es else
      "These are the three we get asked about most, and they get confused constantly. "
      "<strong>Balayage</strong> is painted freehand, sweeping color from mid-length to ends: it leaves a soft transition and grows "
      "out without a hard line, which is why it holds for months between appointments. <strong>Babylights</strong> are very fine "
      "sections taken from the root, imitating the way sun naturally lightens a child's hair — more even and less contrasted "
      "than balayage. Both take three hours and start at $2,300.") + '</p>')
    o.append('<p>' + ("El <strong>matiz</strong> no aclara: neutraliza. Es lo que quita el amarillo o el naranja que aparece semanas "
      "después de un aclarado, y por eso suele ir después de un balayage, no en lugar de él. El <strong>baño de color</strong> "
      "deposita tono y brillo sin levantar la base. Los dos arrancan en $900 y toman hora y cuarto."
      if es else
      "<strong>Toner</strong> does not lighten — it neutralizes. It is what removes the yellow or orange that appears weeks after "
      "lightening, which is why it usually follows a balayage rather than replacing it. A <strong>color gloss</strong> deposits tone "
      "and shine without lifting the base. Both start at $900 and take an hour and fifteen.") + '</p>')
    o.append(f'<h2>{"Cada cuándo retocar la raíz" if es else "How often to touch up your roots"}</h2>')
    o.append('<p>' + ("El cabello crece alrededor de un centímetro al mes. Con un <strong>tinte global</strong> o una <strong>base</strong>, "
      "la raíz se nota a las cuatro o seis semanas y ahí va el <strong>retoque de raíz</strong> ($900). Con balayage o babylights "
      "el crecimiento es suave por diseño: puedes estirarlo a tres o cuatro meses, y muchas clientas solo entran a matiz "
      "en medio. Esa es la ventaja real de las técnicas a mano alzada, y la razón por la que a la larga salen más baratas."
      if es else
      "Hair grows about a centimeter a month. With <strong>full color</strong> or a <strong>base</strong>, the root shows at four to six "
      "weeks, and that is when a <strong>root touch-up</strong> ($900) goes in. With balayage or babylights the grow-out is soft by "
      "design: you can stretch it to three or four months, and many clients only come in for a toner in between. That is the "
      "real advantage of freehand technique, and why it costs less over time.") + '</p>')
    o.append(f'<h2 id="alisados">{"Los tres alisados, comparados" if es else "The three smoothing services, compared"}</h2>')
    o.append('<p>' + ("No son lo mismo y elegir mal es caro. Esta es la diferencia:"
      if es else "They are not the same, and choosing wrong is expensive. Here is the difference:") + '</p>')
    rows = ([("Nanoplastia", "$2,500", "2 h", "Alisa de verdad, sin formol. Reestructura la fibra.",
              "Quieres el cabello liso y con brillo varios meses."),
             ("Brazilian Blowout", "$2,500", "2 h", "Es el tratamiento de keratina. Sella la cutícula y baja el frizz, conservando movimiento.",
              "Quieres controlar el frizz pero no perder tu onda natural."),
             ("Botox capilar", "$1,800", "1 h", "No alisa: rellena y repara.",
              "Tu cabello está poroso o maltratado por decoloración.")]
            if es else
            [("Nanoplasty", "$2,500", "2 h", "Genuinely straightens, formaldehyde-free. Restructures the fiber.",
              "You want straight, glossy hair for several months."),
             ("Brazilian Blowout", "$2,500", "2 h", "This is the keratin treatment. Seals the cuticle and cuts frizz while keeping movement.",
              "You want frizz control without losing your natural wave."),
             ("Hair botox", "$1,800", "1 h", "Does not straighten: it fills and repairs.",
              "Your hair is porous or damaged from bleaching.")])
    th = ("Servicio","Precio","Tiempo","Qué hace","Te conviene si") if es else ("Service","Price","Time","What it does","Choose it if")
    # Cinco columnas no caben en un celular. Envuelta, la que se desliza es
    # la tabla y no la página entera — que es lo que pasaba antes.
    o.append('<div class="tabla-ancha">'
      '<table class="price"><thead><tr>' + "".join(f'<th>{x}</th>' for x in th) + '</tr></thead><tbody>' +
      "".join(f'<tr><td class="svc">{a}</td><td class="amt">{b}</td><td class="dur">{c}</td>'
              f'<td>{d}</td><td>{ee}</td></tr>' for a,b,c,d,ee in rows) + '</tbody></table></div>')
    o.append('<p>' + ("Si no sabes cuál te toca, mándanos una foto por WhatsApp. A veces la respuesta honesta es un "
      "<strong>tratamiento profundo hidratante</strong> de $520 y no un alisado de $2,500 — y preferimos decírtelo antes que cobrarte de más."
      if es else
      "If you are not sure which one applies, send us a photo on WhatsApp. Sometimes the honest answer is a $520 "
      "<strong>deep hydrating treatment</strong> rather than a $2,500 smoothing service — and we would rather tell you that than overcharge you.") + '</p>')
    o.append(f'<h2>{"Split Ender: cortar solo la punta abierta" if es else "Split Ender: cutting only the split end"}</h2>')
    o.append('<p>' + ("El <strong>Split Ender</strong> (desde $600, una hora) es una herramienta que recorta únicamente las puntas "
      "abiertas, milímetros, sin quitarte largo. Sirve cuando quieres dejarte crecer el cabello pero las puntas ya están "
      "quebradas y el corte normal te costaría varios centímetros. No sustituye al corte: lo espacia."
      if es else
      "The <strong>Split Ender</strong> (from $600, one hour) is a tool that trims only the split ends — millimeters — without "
      "taking length. It is for when you are growing your hair out but the ends are breaking and a regular cut would cost you "
      "several centimeters. It does not replace a haircut: it spaces them out.") + '</p>')
    o.append(f'<h2>{"Garantía y formas de pago" if es else "Guarantee and payment"}</h2>')
    o.append('<p>' + ("Todos nuestros servicios tienen <strong>72 horas de garantía</strong>: si algo no quedó "
      "como lo acordamos, regresas dentro de ese plazo y lo corregimos sin costo. "
      "Aceptamos efectivo y tarjetas de débito y crédito, y a partir de <strong>$2,000</strong> puedes pagar "
      "a <strong>3 meses sin intereses</strong> con cualquier tarjeta de crédito — que es justo el rango en el "
      "que caen el balayage, la nanoplastia y el Brazilian Blowout."
      if es else
      "Every service carries a <strong>72-hour guarantee</strong>: if something did not turn out the way we "
      "agreed, come back within that window and we will correct it at no cost. "
      "We take cash and debit and credit cards, and from <strong>$2,000</strong> you can split the payment into "
      "<strong>3 interest-free monthly instalments</strong> with any credit card — which is exactly the range "
      "balayage, nanoplasty and Brazilian Blowout fall into.") + '</p>')
    return "\n".join(o)

def nails_guide(lang):
    es = lang == "es"
    o = []
    o.append(f'<h2>{"Acrílico, gel y escultural: qué te conviene" if es else "Acrylic, gel and sculpted: what suits you"}</h2>')
    o.append('<p>' + ("La diferencia no es de precio, es de para qué. El <strong>gel</strong> (desde $180) va sobre tu uña natural "
      "y le da color y resistencia: dura de dos a tres semanas y es lo más noble con la uña. El <strong>acrílico</strong> ($400) "
      "construye estructura encima: aguanta más y permite largo, pero pide retoque puntual. La <strong>uña escultural con gel</strong> "
      "(desde $500) construye largo con gel en lugar de acrílico — queda más ligera y flexible, y suele sentirse más natural."
      if es else
      "The difference is not price, it is purpose. <strong>Gel</strong> (from $180) goes over your natural nail for color and "
      "resistance: it lasts two to three weeks and is the gentlest option. <strong>Acrylic</strong> ($400) builds structure on top: "
      "it holds up longer and allows length, but needs fills on schedule. <strong>Sculpted gel nails</strong> (from $500) build length "
      "with gel instead of acrylic — lighter and more flexible, and they usually feel more natural.") + '</p>')
    o.append(f'<h2>{"Por qué el retoque se hace a tiempo" if es else "Why fills matter on schedule"}</h2>')
    o.append('<p>' + ("El retoque va cada <strong>tres o cuatro semanas</strong>. No es por vender más: conforme la uña crece, el "
      "material se despega de la raíz y queda una cámara de aire donde entra humedad. Ahí es donde se daña la uña natural — "
      "no en el acrílico en sí. Esperar dos meses no ahorra dinero, cuesta uña. El retoque siempre sale más barato que el "
      "juego completo."
      if es else
      "Fills go every <strong>three to four weeks</strong>. This is not about selling more: as the nail grows, the product lifts at "
      "the base and leaves an air pocket where moisture gets in. That is where the natural nail gets damaged — not from the "
      "acrylic itself. Waiting two months does not save money, it costs nail. A fill is cheaper than a full set, though "
      "not half the price — we explain why below.") + '</p>')
    o.append('<p>' + ("El <strong>retiro</strong> ($100) lo hacemos siempre con técnica y producto. Arrancarte el acrílico en casa "
      "se lleva capas de tu uña natural, y recuperarlas toma meses."
      if es else
      "<strong>Removal</strong> ($100) is always done with proper technique and product. Prying acrylic off at home takes layers of "
      "your natural nail with it, and those take months to grow back.") + '</p>')
    # ── Por qué el retoque cuesta casi lo mismo ─────────────────────────
    # Es la pregunta que más llega al salón. A propósito sin cifras: los
    # precios ya están en la tabla de la página de uñas, y repetirlos aquí
    # sólo subraya lo chica que es la rebaja. Lo que convence es entender
    # el trabajo, no volver a leer el número.
    o.append(f'<h2 id="retoque">'
             f'{"Por qué el retoque cuesta casi lo mismo que uno nuevo" if es else "Why a fill costs almost the same as a new set"}</h2>')
    o.append('<p>' + ("Es la pregunta que más nos hacen, y es justa. La respuesta honesta es que "
      "<strong>un retoque no es rellenar el hueco de la raíz</strong>. Cuando tu uña crece no aparece nada más un espacio: "
      "toda la estructura se recorrió. El <strong>apex</strong> —el punto más grueso, el que sostiene la fuerza de la uña— "
      "quedó fuera de lugar, y con él la uña perdió el balance. Si sólo se rellena la raíz y se pinta encima, en cuatro o "
      "cinco días truena justo por ahí."
      if es else
      "It is the question we get most, and it is a fair one. The honest answer is that <strong>a fill is not topping up the "
      "gap at the base</strong>. When your nail grows, it is not just a gap that appears: the whole structure has moved. The "
      "<strong>apex</strong> — the thickest point, the one that carries the nail's strength — is now in the wrong place, and the "
      "nail has lost its balance. Fill only the base and paint over it, and in four or five days it snaps right there.") + '</p>')
    o.append('<p>' + ("Lo que de verdad lleva un retoque bien hecho: desbastar casi todo el producto viejo y no sólo la raíz, "
      "reparar los levantamientos y las grietas que casi siempre hay, reconstruir el apex en su lugar nuevo, rebalancear las "
      "diez uñas para que queden parejas, y volver a hacer toda la superficie y todo el color. El tiempo en la silla es "
      "prácticamente el mismo que el de un juego nuevo —a veces más, porque desbastar producto viejo tarda más que trabajar "
      "sobre una uña limpia."
      if es else
      "What a proper fill actually takes: filing down almost all the old product, not just the base; repairing the lifting and "
      "cracks there almost always are; rebuilding the apex in its new position; rebalancing all ten nails so they match; and "
      "redoing the entire surface and the entire color. Chair time is practically the same as a new set — sometimes more, "
      "because filing down old product takes longer than working on a clean nail.") + '</p>')
    o.append('<p>' + ("Lo que sí te ahorras es el material de la extensión y el esculpido del largo, que ya están hechos. Por eso "
      "el retoque cuesta menos, pero no la mitad: un retoque que costara la mitad sería una uña que dura la mitad, y eso no te "
      "lo vamos a vender."
      if es else
      "What you do save is the extension product and the sculpting of the length, which are already done. That is why a fill "
      "costs less, but not half: a fill at half the price would be a nail that lasts half as long, and that is not something we "
      "will sell you.") + '</p>')
    o.append('<p>' + ("¿Cuándo conviene empezar de cero en lugar de retocar? Cuando ya llevas varios retoques encima y la uña se "
      "siente pesada, o cuando hay levantamiento en varias uñas a la vez. Te lo decimos nosotras antes de empezar, no a la hora "
      "de cobrar."
      if es else
      "When is it better to start fresh instead of filling? Once you have several fills stacked up and the nail starts to feel "
      "heavy, or when there is lifting on several nails at once. We tell you before we start, not when it is time to pay.") + '</p>')

    o.append(f'<h2>{"Si traes la uña débil: empieza por aquí" if es else "If your nails are weak: start here"}</h2>')
    o.append('<p>' + ("Después de mucho tiempo con acrílico es normal que la uña quede delgada. Para eso están las "
      "<strong>vitaminas</strong> ($150 cada una), que no son color sino tratamiento: el <strong>calcio</strong> fortalece, el "
      "<strong>rubber</strong> cubre imperfecciones y da cuerpo a uñas delgadas, y la <strong>vitamina</strong> protege mientras la uña "
      "se recupera. Se pueden combinar con gel ($280 calcio + gel) para que no dejes de traerlas arregladas mientras sanan."
      if es else
      "After a long run of acrylic it is normal for the nail to end up thin. That is what <strong>nail vitamins</strong> ($150 each) "
      "are for — treatment, not color: <strong>calcium</strong> strengthens, <strong>rubber base</strong> covers imperfections and adds body "
      "to thin nails, and <strong>nail vitamin</strong> protects while the nail recovers. They combine with gel ($280 calcium + gel) so "
      "you do not have to go bare while they heal.") + '</p>')
    o.append('<p>' + ("Y una recomendación honesta: si tu uña natural está sana, un gel bien puesto se ve igual de bien que el "
      "acrílico y la cuida más. Te lo vamos a decir aunque el acrílico cueste más."
      if es else
      "And an honest recommendation: if your natural nail is healthy, a well-applied gel looks just as good as acrylic and "
      "treats it better. We will tell you so, even though acrylic costs more.") + '</p>')
    o.append(f'<h2>{"Garantía" if es else "Guarantee"}</h2>')
    o.append('<p>' + ("Las <strong>uñas en gel tienen 5 días de garantía</strong> y el resto de nuestros "
      "servicios, <strong>72 horas</strong>. Si algo se despostilla o no quedó como lo acordamos dentro de ese "
      "plazo, regresas y lo corregimos sin costo."
      if es else
      "<strong>Gel nails carry a 5-day guarantee</strong>, and every other service <strong>72 hours</strong>. "
      "If anything chips or did not turn out the way we agreed within that window, come back and we will fix "
      "it at no cost.") + '</p>')
    return "\n".join(o)

HAIR_FAQ = {
 "es": [("¿Cuál es la diferencia entre balayage y babylights?",
         "El balayage se pinta a mano alzada de medios a puntas y deja una transición suave que crece sin línea marcada. Los babylights son mechones muy finos tomados desde la raíz que imitan el aclarado natural del sol: se ven más parejos y menos contrastados. Ambos cuestan desde $2,300 y toman tres horas."),
        ("¿Cada cuándo debo retocar la raíz?",
         "Con tinte global o base, entre cuatro y seis semanas. Con balayage o babylights puedes estirarlo a tres o cuatro meses porque el crecimiento es suave por diseño."),
        ("¿Hacen keratina?",
         "Sí. En el salón le decimos Brazilian Blowout, que es su nombre comercial, pero es el tratamiento de keratina: cuesta $2,500, toma dos horas y sella la cutícula para bajar el frizz sin dejarte el cabello completamente lacio. Si lo que quieres es liso de verdad, entonces es nanoplastia."),
        ("¿Qué alisado me conviene?",
         "La nanoplastia alisa de verdad y sin formol. El Brazilian Blowout baja el frizz conservando movimiento. El botox capilar no alisa: rellena y repara cabello poroso o decolorado. Si no sabes cuál, mándanos una foto por WhatsApp."),
        ("¿Cuál es la diferencia entre matiz y baño de color?",
         "El matiz neutraliza el amarillo o naranja que aparece después de aclarar; no cambia el tono base. El baño de color deposita tono y brillo sin levantar la base. Ambos desde $900."),
        ("¿Qué es el Split Ender?",
         "Una herramienta que recorta únicamente las puntas abiertas, milímetros, sin quitarte largo. Sirve para dejarte crecer el cabello sin cargar puntas quebradas. Desde $600."),
        ("¿Los precios de color son finales?",
         "Los precios marcados “desde” aplican a cabello a partir del hombro. Si tu cabello es más largo o más denso lleva más producto y más tiempo, y el ajuste te lo decimos antes de empezar, nunca al cobrar.")],
 "en": [("What is the difference between balayage and babylights?",
         "Balayage is painted freehand from mid-length to ends and leaves a soft transition that grows out without a hard line. Babylights are very fine sections taken from the root that imitate natural sun-lightening: more even, less contrasted. Both start at $2,300 and take three hours."),
        ("How often should I touch up my roots?",
         "With full color or a base, every four to six weeks. With balayage or babylights you can stretch it to three or four months, because the grow-out is soft by design."),
        ("Do you do keratin treatments?",
         "Yes. We call it Brazilian Blowout, its commercial name, but it is the keratin treatment: $2,500, two hours, and it seals the cuticle to cut frizz without leaving your hair perfectly flat. If you want genuinely straight hair, that is nanoplasty."),
        ("Which smoothing service should I choose?",
         "Nanoplasty genuinely straightens, formaldehyde-free. Brazilian Blowout reduces frizz while keeping movement. Hair botox does not straighten: it fills and repairs porous or bleached hair. If you are unsure, send us a photo on WhatsApp."),
        ("What is the difference between toner and color gloss?",
         "Toner neutralizes the yellow or orange that appears after lightening; it does not change the base. A color gloss deposits tone and shine without lifting the base. Both from $900."),
        ("What is the Split Ender?",
         "A tool that trims only split ends — millimeters — without taking length. It lets you grow your hair out without carrying broken ends. From $600."),
        ("Are the color prices final?",
         "Prices marked “from” apply at shoulder length and above. Longer or denser hair takes more product and time, and we tell you that adjustment before we start, never at the register.")],
}

NAILS_FAQ = {
 "es": [("¿Acrílico o gel?",
         "Si tu uña natural está sana, el gel se ve igual de bien y la cuida más. El acrílico conviene cuando quieres estructura y largo. El gel dura de dos a tres semanas; el acrílico aguanta más pero pide retoque cada tres o cuatro semanas."),
        ("¿El acrílico daña la uña natural?",
         "El daño no viene del acrílico, viene de dejarlo crecer demasiado: al crecer la uña, el material se despega en la raíz y entra humedad. Con retoque cada tres o cuatro semanas y retiro con técnica, la uña natural se mantiene bien."),
        ("¿Cada cuándo tengo que retocar?",
         "Cada tres o cuatro semanas. El retoque cuesta menos que el juego completo y esperar más tiempo termina costando uña."),
        ("¿Por qué el retoque de uña escultural cuesta casi lo mismo que una nueva?",
         "Porque un retoque no es rellenar el hueco de la raíz. Al crecer la uña toda la estructura se recorre y el apex, el punto que sostiene la fuerza, queda fuera de lugar. Hay que desbastar casi todo el producto viejo, reparar levantamientos, reconstruir el apex, rebalancear las diez uñas y rehacer superficie y color: el tiempo en la silla es casi el mismo que el de un juego nuevo. Lo que te ahorras es el material de la extensión y el esculpido del largo, y por eso cuesta menos, pero no la mitad."),
        ("¿Puedo retirarme el gel o el acrílico en casa?",
         "No te lo recomendamos. Arrancarlo se lleva capas de tu uña natural y recuperarlas toma meses. El retiro con técnica cuesta $100."),
        ("Tengo la uña débil después de mucho acrílico, ¿qué hago?",
         "Empieza por las vitaminas ($150): el calcio fortalece, el rubber cubre imperfecciones y da cuerpo a uñas delgadas, y la vitamina protege mientras la uña se recupera. Se pueden combinar con gel para que no dejes de traerlas arregladas."),
        ("¿Qué incluye el manicure spa?",
         "Tina con sales, exfoliación, masaje y esmalte, por $220. Con gel en lugar de esmalte son $350. El pedicure spa ($360) añade limado de talón y masaje de pies."),
        ("¿Las uñas en gel tienen garantía?",
         "Sí, 5 días. El resto de nuestros servicios tienen 72 horas de garantía. Si algo se despostilla dentro de ese plazo, regresas y lo corregimos sin costo.")],
 "en": [("Acrylic or gel?",
         "If your natural nail is healthy, gel looks just as good and treats it better. Acrylic makes sense when you want structure and length. Gel lasts two to three weeks; acrylic holds longer but needs a fill every three to four weeks."),
        ("Does acrylic damage the natural nail?",
         "The damage does not come from the acrylic, it comes from letting it grow out too long: as the nail grows, product lifts at the base and moisture gets in. With fills every three to four weeks and proper removal, the natural nail stays healthy."),
        ("How often do I need a fill?",
         "Every three to four weeks. A fill costs less than a full set, and waiting longer ends up costing nail."),
        ("Why does a sculpted nail fill cost almost the same as a new set?",
         "Because a fill is not topping up the gap at the base. As the nail grows the whole structure moves and the apex, the point that carries the strength, ends up in the wrong place. We have to file down almost all the old product, repair lifting, rebuild the apex, rebalance all ten nails and redo surface and color: chair time is almost the same as a new set. What you save is the extension product and the sculpting of the length, and that is why it costs less, but not half."),
        ("Can I remove gel or acrylic at home?",
         "We do not recommend it. Prying it off takes layers of your natural nail with it, and those take months to grow back. Professional removal is $100."),
        ("My nails are weak after a long run of acrylic — what now?",
         "Start with nail vitamins ($150): calcium strengthens, rubber base covers imperfections and adds body to thin nails, and nail vitamin protects while the nail recovers. They combine with gel so you do not have to go bare."),
        ("What does the spa manicure include?",
         "A salt soak, exfoliation, massage and polish, for $220. With gel instead of polish it is $350. The spa pedicure ($360) adds heel filing and a foot massage."),
        ("Do gel nails come with a guarantee?",
         "Yes, 5 days. Every other service carries a 72-hour guarantee. If anything chips within that window, come back and we will fix it at no cost.")],
}

def topic_faq_ld(table, lang):
    body = ",".join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
                    % (_j(q), _j(a)) for q, a in table[lang])
    return ('<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}</script>' % body)

# Fotos reales de trabajos del salón. Son exportaciones de Instagram a 640x640,
# suficientes para galería pero NO para una portada a sangre completa.
# Tres fotos por galería, ni una más: es un adelanto, no el catálogo.  Quien
# quiera ver más pica "Ver todo el portafolio", que es justo el enlace que va
# debajo.  Seis en una página y tres en otra se lee a descuido.
GALERIA = {
 # Estas salen de assets/pf/, o sea del portafolio: ya vienen curadas,
 # recortadas a 3:4 y con la marca de agua puesta donde toca.  No se
 # recortan a cuadro porque la marca va abajo y un recorte cuadrado se la
 # comería; por eso esta galería es la única que va en vertical.
 "hair": [("pf/cabello-3.jpg",
           "Balayage rubio con ondas hecho en Stilo Salón Roma Norte",
           "Balayage · 3 horas · desde $2,300",
           "Blonde balayage with waves at Stilo Salón Roma Norte",
           "Balayage · 3 hours · from $2,300"),
          ("pf/cabello-25.jpg",
           "Balayage en cabello largo con barrido suave, Stilo Salón Roma Norte",
           "Balayage en cabello largo · desde $2,300",
           "Long-hair balayage with a soft sweep, Stilo Salón Roma Norte",
           "Long-hair balayage · from $2,300"),
          ("pf/cabello-32.jpg",
           "Balayage de raíz oscura a puntas rubias con ondas, Stilo Salón Roma Norte",
           "Raíz oscura a puntas claras · desde $2,300",
           "Dark roots to blonde ends with waves, Stilo Salón Roma Norte",
           "Dark roots to light ends · from $2,300")],
 # Tres encuadres distintos a propósito: el macro enseña densidad, el
 # perfil enseña largo y curvatura, y el frontal enseña cómo queda la cara
 # completa.  Ninguna lleva cubrebocas: las que lo traen fechan el trabajo
 # en 2021.
 #
 # El pie de foto describe el EFECTO, no la técnica.  Clásicas, híbridas y
 # volumen ruso no se distinguen con seguridad en una foto —es la misma
 # razón por la que el portafolio no filtra pestañas por técnica—, así que
 # ponerle nombre sería inventar. Va el precio de entrada, que sí es cierto
 # para las cinco técnicas.
 # Las tres las eligió el salón. Las dos primeras ya vivían en el
 # portafolio (118 y 209); la tercera la subieron nueva y se procesó por el
 # mismo camino que las demás: recorte 3:4 y marca de agua quemada.
 #
 # El pie describe el EFECTO, no la técnica: clásicas, híbridas y volumen
 # ruso no se distinguen con seguridad en una foto, así que nombrarlas
 # sería inventar. El precio de entrada sí es cierto para las cinco.
 "lashes": [("pf/pestanas-118.jpg",
             "Extensiones de pestañas largas y abiertas, Stilo Salón Roma Norte",
             "Efecto abierto · Extensiones desde $750",
             "Long, open eyelash extensions, Stilo Salón Roma Norte",
             "Open effect · Extensions from $750"),
            ("pf/pestanas-209.jpg",
             "Extensiones de pestañas definidas en ambos ojos, Stilo Salón Roma Norte",
             "Efecto definido · Extensiones desde $750",
             "Defined eyelash extensions on both eyes, Stilo Salón Roma Norte",
             "Defined effect · Extensions from $750"),
            ("pf/pestanas-219.jpg",
             "Extensiones de pestañas con efecto natural, Stilo Salón Roma Norte",
             "Efecto natural · Extensiones desde $750",
             "Natural-effect eyelash extensions, Stilo Salón Roma Norte",
             "Natural effect · Extensions from $750")],
 "nails": [("trabajo-unas-01.jpg",
            "Uñas con diseño de leopardo en blanco y dorado, Stilo Salón Roma Norte",
            "Diseño de leopardo · Uña escultural con gel",
            "Leopard-print nails in white and gold, Stilo Salón Roma Norte",
            "Leopard print · Sculpted gel"),
           ("trabajo-unas-07.jpg",
            "Uñas almendra en nude con punta francesa, Stilo Salón Roma Norte",
            "Almendra con francés · Uña escultural con gel",
            "Almond nude nails with French tip, Stilo Salón Roma Norte",
            "Almond with French tip · Sculpted gel"),
           ("trabajo-unas-02.jpg",
            "Uñas largas coffin en dorado metálico y nude, Stilo Salón Roma Norte",
            "Coffin en dorado metálico · Uña tip con gel",
            "Long coffin nails in metallic gold and nude, Stilo Salón Roma Norte",
            "Coffin in metallic gold · Gel tip")],
}

def galeria_html(key, lang):
    items = GALERIA.get(key)
    if not items: return ""
    es = lang == "es"
    figs = "".join(
      # El span es el marco que recorta: sin él, el acercamiento al pasar
      # el cursor se derrama sobre el pie de foto.
      f'<figure><span class="g-foto"><img src="/assets/{f}" '
      f'width="{720 if f.startswith("pf/") else 560}" '
      f'height="{960 if f.startswith("pf/") else 560}" '
      f'loading="lazy" alt="{e(alt_es if es else alt_en)}"></span>'
      f'<figcaption>{e(cap_es if es else cap_en)}</figcaption></figure>'
      for f, alt_es, cap_es, alt_en, cap_en in items)
    titulo = "Trabajos hechos aquí" if es else "Work done here"
    ancla = {"hair": "cabello", "nails": "unas", "lashes": "pestanas"}[key]
    destino = ("/portafolio.html#" if es else "/en/portfolio.html#") + ancla
    masq = ("Ver todo el portafolio" if es else "See the full portfolio")
    alta = ' g-alta' if any(i[0].startswith("pf/") for i in items) else ''
    return (f'<h2>{titulo}</h2><div class="galeria{alta} js-reveal">{figs}</div>'
            f'<p class="g-mas"><a href="{destino}">{e(masq)} &rarr;</a></p>')

GUIA_META = {
 "lashes": dict(
   es_slug="/guia-extensiones-de-pestanas.html", en_slug="/en/eyelash-extensions-guide.html",
   es=dict(title="Extensiones de Pestañas y Cejas: la Biblia | Stilo Salón",
     desc="¿Cuánto duran las extensiones de pestañas? ¿Qué técnica te conviene? ¿Cada cuándo retocar? La guía completa de Stilo Salón, Roma Norte, CDMX.",
     h1="La biblia de las extensiones de pestañas y cejas",
     lede="¿Quieres saber cuánto cuestan? ¿Qué técnicas existen? ¿Cuál es apta para ti? ¿Cuánto duran? Aquí está todo, escrito por quienes las aplican.",
     eyebrow="Guía completa · Roma Norte"),
   en=dict(title="The Eyelash Extension & Brow Bible | Stilo Salón",
     desc="How long do eyelash extensions last? Which technique suits you? How often to get a fill? The complete guide from Stilo Salón, Roma Norte, Mexico City.",
     h1="The eyelash extension and brow bible",
     lede="Want to know what they cost? Which techniques exist? Which suits you? How long they last? It is all here, written by the people who apply them.",
     eyebrow="Complete guide · Roma Norte")),
 "hair": dict(
   es_slug="/guia-color-y-alisados.html", en_slug="/en/color-and-smoothing-guide.html",
   es=dict(title="Balayage, Babylights y Alisados: la Guía | Stilo Salón",
     desc="Balayage o babylights, cada cuándo retocar raíz y qué alisado te conviene: keratina (Brazilian Blowout), nanoplastia o botox capilar. Roma Norte, CDMX.",
     h1="Color y alisados: la guía completa",
     lede="Lo que más nos preguntan en la silla, escrito: qué técnica de color es cuál, cada cuándo volver, y cuál alisado te toca.",
     eyebrow="Guía completa · Roma Norte"),
   en=dict(title="Balayage, Babylights & Smoothing: the Guide | Stilo Salón",
     desc="Balayage or babylights, how often to touch up roots, and which smoothing suits you: keratin (Brazilian Blowout), nanoplasty or hair botox. Roma Norte, CDMX.",
     h1="Color and smoothing: the complete guide",
     lede="What people ask us most in the chair, written down: which color technique is which, how often to come back, and which smoothing service is yours.",
     eyebrow="Complete guide · Roma Norte")),
 "nails": dict(
   es_slug="/guia-unas.html", en_slug="/en/nails-guide.html",
   es=dict(title="Acrílico, Gel o Escultural: la Guía de Uñas | Stilo Salón",
     desc="Qué conviene entre acrílico, gel y escultural, cada cuándo retocar sin dañar la uña natural, y qué hacer si traes la uña débil. Roma Norte, CDMX.",
     h1="Uñas: la guía completa",
     lede="Qué técnica te conviene, por qué el retoque a tiempo protege tu uña natural, y qué hacer si la traes débil.",
     eyebrow="Guía completa · Roma Norte"),
   en=dict(title="Acrylic, Gel or Sculpted: the Nail Guide | Stilo Salón",
     desc="What suits you between acrylic, gel and sculpted nails, how often to fill without damaging the natural nail, and what to do if your nails are weak.",
     h1="Nails: the complete guide",
     lede="Which technique suits you, why fills on schedule protect your natural nail, and what to do if yours are weak.",
     eyebrow="Complete guide · Roma Norte")),
}

RESUMEN = {
 "lashes": {"es": "Cinco técnicas, de la clásica 1x1 al volumen ruso. Todas son set completo, se retocan cada dos o tres semanas y no maltratan tu pestaña natural. Abajo están los precios de todas.",
            "en": "Five techniques, from classic 1x1 to Russian volume. All are full sets, filled every two to three weeks, and none damage your natural lashes. All prices below."},
 "hair":   {"es": "Corte, color y tratamiento. Los precios marcados “desde” aplican de hombro hacia arriba; si tu cabello es más largo, el ajuste te lo decimos antes de empezar, nunca al cobrar.",
            "en": "Cutting, color and treatment. Prices marked “from” apply at shoulder length and above; if your hair is longer, we tell you the adjustment before we start, never at the register."},
 "nails":  {"es": "Manicure y pedicure spa, gel, acrílico y esculturales, más vitaminas para uña débil. Todo con su precio abajo.",
            "en": "Spa manicure and pedicure, gel, acrylic and sculpted nails, plus treatments for weak nails. Every price below."},
}

def enlace_guia(key, lang):
    g = GUIA_META[key]; d = g[lang]
    slug = g["es_slug"] if lang == "es" else g["en_slug"]
    txt = "Leer la guía completa" if lang == "es" else "Read the complete guide"
    sub = ("Todo el detalle: técnicas, duración, cuidados y cada cuándo volver."
           if lang == "es" else
           "The full detail: techniques, how long they last, aftercare and when to come back.")
    return (f'<a class="a-guia" href="{slug}"><span class="a-guia-t">{e(d["h1"])}</span>'
            f'<span class="a-guia-s">{e(sub)}</span><span class="a-guia-c">{txt} &rarr;</span></a>')

def main():
    log = []
    # Home (ES + EN)
    for lang in ("es", "en"):
        home, alt = ("/", f"{SITE}/en/") if lang == "es" else ("/en/", f"{SITE}/")
        title = ("Stilo Salón | Salón de Belleza en Roma Norte, CDMX"
                 if lang == "es" else
                 "Stilo Salón | Beauty Salon in Roma Norte, Mexico City")
        desc = ("Salón de belleza en Roma Norte, CDMX. Corte desde $330, balayage desde $2,300, "
                "pestañas desde $750. Precios publicados, sin sorpresas. Reserva en línea."
                if lang == "es" else
                "Beauty salon in Roma Norte, Mexico City. Cuts from $330, balayage from $2,300, "
                "lashes from $750 MXN. Published prices, no surprises. Book online.")
        out = "index.html" if lang == "es" else "en/index.html"
        log.append(write(out, page(lang, "", title, desc, home_body(lang), alt,
                                   salon_ld(lang) + faq_ld(lang))))
    # Service pages
    for sp in SERVICE_PAGES:
        for lang in ("es", "en"):
            d = sp[lang]
            slug = sp["es_slug"] if lang == "es" else sp["en_slug"]
            alt  = SITE + (sp["en_slug"] if lang == "es" else sp["es_slug"])
            extra = galeria_html(sp["key"], lang) + enlace_guia(sp["key"], lang)
            bnr = {"hair":"h-cabello.jpg","nails":"h-unas.jpg","lashes":"h-pestanas.jpg"}[sp["key"]]
            alt_f = {"hair":  ("Balayage rubio ceniza hecho en Stilo Salón, Roma Norte, CDMX",
                               "Ash blonde balayage done at Stilo Salón, Roma Norte, Mexico City"),
                     "nails": ("Uñas largas en gel con francés blanco hechas en Stilo Salón, Roma Norte",
                               "Long gel nails with a white French tip done at Stilo Salón, Roma Norte"),
                     "lashes":("Extensiones de pestañas de volumen aplicadas en Stilo Salón, Roma Norte",
                               "Volume lash extensions applied at Stilo Salón, Roma Norte")}[sp["key"]]
            alt_f = alt_f[0] if lang == "es" else alt_f[1]
            resumen = [RESUMEN[sp["key"]][lang]]
            body = svc_body(lang, d["eyebrow"], d["h1"], d["intro"], resumen, sp["keys"], extra=extra, banner=bnr, alt_foto=alt_f)
            ld = salon_ld(lang)   # el FAQPage vive en la guía, que es donde están las respuestas
            log.append(write(slug.lstrip("/"), page(lang, slug, d["title"], d["desc"], body, alt, ld)))
    # Páginas de guía: una por servicio, en los dos idiomas
    CUERPO = {"lashes": lash_guide, "hair": hair_guide, "nails": nails_guide}
    FAQ_G  = {"lashes": lambda l: lash_faq_ld(l),
              "hair":   lambda l: topic_faq_ld(HAIR_FAQ, l),
              "nails":  lambda l: topic_faq_ld(NAILS_FAQ, l)}
    VUELTA = {"lashes": ("/pestanas-y-cejas.html", "/en/lashes-and-brows.html",
                         "Ver precios de pestañas y cejas", "See lash and brow prices"),
              "hair":   ("/cabello.html", "/en/hair.html",
                         "Ver precios de cabello y color", "See hair and color prices"),
              "nails":  ("/unas.html", "/en/nails.html",
                         "Ver precios de uñas", "See nail prices")}
    for key, g in GUIA_META.items():
        for lang in ("es", "en"):
            d = g[lang]
            slug = g["es_slug"] if lang == "es" else g["en_slug"]
            alt  = SITE + (g["en_slug"] if lang == "es" else g["es_slug"])
            volver_es, volver_en, txt_es, txt_en = VUELTA[key]
            destino = volver_es if lang == "es" else volver_en
            txt = txt_es if lang == "es" else txt_en
            cuerpo = (f'<section><div class="wrap">'
                      f'<p class="eyebrow">{e(d["eyebrow"])}</p><h1>{e(d["h1"])}</h1>'
                      f'<p class="lede">{e(d["lede"])}</p></div></section>'
                      f'<section class="alt" style="padding-top:0"><div class="wrap" style="max-width:74ch">'
                      f'{CUERPO[key](lang)}'
                      f'<a class="a-guia" href="{destino}"><span class="a-guia-t">{txt}</span>'
                      f'<span class="a-guia-c">{"Ver precios" if lang=="es" else "See prices"} &rarr;</span></a>'
                      f'</div></section>'
                      f'<section><div class="wrap"><div class="btn-row">'
                      f'<a class="btn btn-primary" href="{BOOKING}" target="_blank" rel="noopener">{T[lang]["book"]}</a>'
                      f'<a class="btn btn-wa" href="{WA}" rel="noopener">{T[lang]["book_wa"]}</a>'
                      f'</div></div></section>')
            log.append(write(slug.lstrip("/"), page(lang, slug, d["title"], d["desc"],
                                                    cuerpo, alt, salon_ld(lang) + FAQ_G[key](lang))))

    # Portafolio
    for lang in ("es", "en"):
        slug = "/portafolio.html" if lang == "es" else "/en/portfolio.html"
        alt  = SITE + ("/en/portfolio.html" if lang == "es" else "/portafolio.html")
        if lang == "es":
            title = "Portafolio de Trabajos | Stilo Salón Roma Norte, CDMX"
            desc = ("Trabajos reales de Stilo Salón en Roma Norte: balayage, rubios, alisados, "
                    "uñas en gel y extensiones de pestañas, cada foto con su precio publicado.")
        else:
            title = "Portfolio | Stilo Salón Roma Norte, Mexico City"
            desc = ("Real work from Stilo Salón in Roma Norte: balayage, blondes, smoothing, "
                    "gel nails and lash extensions, every photo with its published price.")
        log.append(write(slug.lstrip("/"), page(lang, slug, title, desc,
                                                portafolio_body(lang), alt, salon_ld(lang))))

    # Full price list
    allk = list(PRICES.keys())
    for lang in ("es", "en"):
        slug = "/precios.html" if lang == "es" else "/en/pricing.html"
        alt  = SITE + ("/en/pricing.html" if lang == "es" else "/precios.html")
        title = ("Lista de Precios Completa | Stilo Salón Roma Norte, CDMX" if lang == "es"
                 else "Full Price List | Stilo Salón Roma Norte, Mexico City")
        desc = ("Precios de Stilo Salón: cabello, keratina, uñas, pestañas, cejas y "
                "depilación. Más de 60 servicios con precio y duración. Roma Norte, CDMX."
                if lang == "es" else
                "Full price list for Stilo Salón: hair, treatments, nails, lashes, brows and waxing. "
                "Over 60 services with price and duration. Roma Norte, Mexico City.")
        h1 = "Lista de precios completa" if lang == "es" else "Full price list"
        intro = ("Todos nuestros servicios con su precio y su duración. Los precios marcados “desde” "
                 "aplican a cabello a partir del hombro; cualquier ajuste te lo decimos antes de empezar. "
                 "A partir de $2,000 puedes pagar a 3 meses sin intereses con cualquier "
                 "tarjeta de crédito."
                 if lang == "es" else
                 "Every service with its price and duration. Prices marked “from” apply at shoulder "
                 "length and above; any adjustment is discussed before we begin. From $2,000 you can "
                 "split the payment into 3 interest-free monthly instalments with any credit card.")
        body = svc_body(lang, "Roma Norte · CDMX" if lang=="es" else "Roma Norte · Mexico City",
                        h1, intro, [], allk, nivel=2)
        log.append(write(slug.lstrip("/"), page(lang, slug, title, desc, body, alt, salon_ld(lang))))
    # Privacy
    for lang in ("es", "en"):
        slug = "/aviso-de-privacidad.html" if lang == "es" else "/en/privacy.html"
        alt  = SITE + ("/en/privacy.html" if lang == "es" else "/aviso-de-privacidad.html")
        if lang == "es":
            title, h1 = "Aviso de Privacidad | Stilo Salón", "Aviso de Privacidad"
            desc = ("Aviso de privacidad de Stilo Salón, Roma Norte, CDMX. Qué datos recabamos para tu cita, para qué los usamos y cómo ejercer tus derechos ARCO.")
            ps = ["<strong>Stilo Salón</strong>, con domicilio en Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México, es responsable del tratamiento de tus datos personales.",
                  "<strong>Qué datos recabamos.</strong> Únicamente los necesarios para agendar y dar seguimiento a tu cita: nombre, teléfono y, cuando aplica, el historial de servicios realizados en el salón.",
                  "<strong>Para qué los usamos.</strong> Para confirmar y recordarte tus citas, llevar el registro de los servicios que te hemos hecho, y contactarte si necesitamos reprogramar. No vendemos ni compartimos tus datos con terceros.",
                  "<strong>Tus derechos.</strong> Puedes solicitar el acceso, la rectificación, la cancelación o la oposición al tratamiento de tus datos (derechos ARCO) llamando al 55 2299 3258 o directamente en el salón.",
                  "<strong>Cambios.</strong> Cualquier modificación a este aviso se publicará en esta misma página.",
                  "Última actualización: septiembre de 2026."]
        else:
            title, h1 = "Privacy Notice | Stilo Salón, Roma Norte CDMX", "Privacy Notice"
            desc = ("Privacy notice for Stilo Salón, Roma Norte, Mexico City. What data we collect for your appointment, how we use it, and how to exercise your rights.")
            ps = ["<strong>Stilo Salón</strong>, located at Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Mexico City, is responsible for the handling of your personal data.",
                  "<strong>What we collect.</strong> Only what is needed to book and follow up on your appointment: name, phone number and, where applicable, the history of services performed at the salon.",
                  "<strong>How we use it.</strong> To confirm and remind you of appointments, keep a record of the services we have performed, and contact you if we need to reschedule. We do not sell or share your data with third parties.",
                  "<strong>Your rights.</strong> You may request access, rectification, cancellation or object to the handling of your data (ARCO rights) by calling 55 2299 3258 or in person at the salon.",
                  "<strong>Changes.</strong> Any change to this notice will be published on this page.",
                  "Last updated: September 2026."]
        body = (f'<section><div class="wrap" style="max-width:74ch"><h1>{h1}</h1>'
                + "".join(f"<p>{p}</p>" for p in ps) + '</div></section>')
        log.append(write(slug.lstrip("/"), page(lang, slug, title, desc, body, alt)))

    # 404: Cloudflare Pages la sirve para cualquier ruta que no exista.
    # Es una sola página para los dos árboles (/ y /en/), así que lleva los
    # dos idiomas.  No lleva canonical ni hreflang ni entra al sitemap:
    # una página de error no se indexa.
    body404 = """
<section class="svc-cab"><div class="wrap svc-cab-in">
  <div class="svc-cab-txt">
    <p class="eyebrow">Error 404</p>
    <h1>Esta página no existe</h1>
    <p class="lede">Puede que el enlace est&eacute; viejo o que la direcci&oacute;n
    tenga un error. Lo que buscas seguro est&aacute; aqu&iacute; abajo.</p>
    <div class="btn-row" style="margin-top:1.6rem">
      <a class="btn btn-primary" href="/">Ir al inicio</a>
      <a class="btn btn-ghost" href="/precios.html">Ver precios</a>
      <a class="btn btn-wa" href="%s">WhatsApp</a>
    </div>
    <p style="margin-top:2.2rem; font-size:.9rem; color:#7b6f74">
      <strong>This page doesn&rsquo;t exist.</strong>
      <a href="/en/">Go to the English home page</a> &middot;
      <a href="/en/pricing.html">See prices</a>
    </p>
  </div>
</div></section>""" % WA
    h404 = page("es", "/404.html", "P\u00e1gina no encontrada | Stilo Sal\u00f3n",
                "La p\u00e1gina que buscas no existe. Vuelve al inicio o consulta la lista de precios.",
                body404, f"{SITE}/en/")
    h404 = re.sub(r'\s*<link rel="canonical"[^>]*>', "", h404)
    h404 = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*"[^>]*>', "", h404)
    h404 = re.sub(r'\s*<meta property="og:url"[^>]*>', "", h404)
    h404 = h404.replace("<title>", '<meta name="robots" content="noindex,follow">\n<title>', 1)
    log.append(write("404.html", h404))

    # sitemap / robots / Cloudflare
    urls = ["/", "/cabello.html", "/unas.html", "/pestanas-y-cejas.html", "/precios.html",
            "/guia-extensiones-de-pestanas.html", "/guia-color-y-alisados.html", "/guia-unas.html",
            "/portafolio.html", "/en/portfolio.html",
            "/aviso-de-privacidad.html", "/en/", "/en/hair.html", "/en/nails.html",
            "/en/lashes-and-brows.html", "/en/pricing.html", "/en/eyelash-extensions-guide.html",
            "/en/color-and-smoothing-guide.html", "/en/nails-guide.html", "/en/privacy.html"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{SITE}{u}</loc><changefreq>monthly</changefreq>"
                  f"<priority>{'1.0' if u in ('/', '/en/') else '0.8'}</priority></url>")
    sm.append("</urlset>")
    log.append(write("sitemap.xml", "\n".join(sm) + "\n"))
    log.append(write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"))
    log.append(write("_headers",
        "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: SAMEORIGIN\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: geolocation=(), microphone=(), camera=()\n\n"
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n\n"
        # Cloudflare no sabe qué tipo es un .ico y lo sirve con
        # "content-type: null", que no es un tipo válido.  Medido en el sitio
        # en vivo: el resto de las extensiones las acierta todas, sólo ésta
        # no.  Se declara a mano.
        "/favicon.ico\n  Content-Type: image/vnd.microsoft.icon\n"
        "  Cache-Control: public, max-age=604800\n"))
    # Rutas viejas del sitio de GoDaddy -> nuevas.  Evita perder el poco
    # posicionamiento que ya existe.
    # Ojo con estas: ahora que las URLs públicas no llevan .html, las reglas
    # viejas /cabello -> /cabello.html y /unas -> /unas.html apuntarían a su
    # propio destino y harían un bucle de redirecciones.  Se eliminan: esas
    # dos direcciones ya SON la página, no hay nada que redirigir.  Las demás
    # siguen sirviendo porque vienen de rutas que ya no existen.
    log.append(write("_redirects",
        "/u%C3%B1as          /unas                    301\n"
        "/extensiones        /pestanas-y-cejas        301\n"
        "/lifting            /pestanas-y-cejas        301\n"
        "/microblading       /pestanas-y-cejas        301\n"
        "/dise%C3%B1o-de-ceja /pestanas-y-cejas       301\n"
        "/servicios-y-costos /precios                 301\n"
        "/colores-y-dise%C3%B1os-lv-1 /unas           301\n"
        "/comun%C3%ADcate-con-nosotros /#contacto     301\n"
        "/informacion        /pestanas-y-cejas        301\n"
        "/citas              /#contacto               301\n"
        "/galeria            /                        301\n"
        "/ols/products       /precios                 301\n"))
    print("Stilo Salón — sitio generado:\n" + "\n".join(log))
    print(f"\n{len(urls)} páginas · fuente única de precios: PRICES en build.py")

if __name__ == "__main__":
    main()
