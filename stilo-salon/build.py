#!/usr/bin/env python3
"""
Stilo Salón — generador del sitio estático.

Por qué existe: los precios y los servicios viven UNA sola vez, en este archivo.
De aquí se generan las páginas en español y en inglés, idénticas en contenido.
Cuando cambie un precio, se cambia aquí y se vuelve a correr:  python3 build.py

Salida: HTML estático plano, listo para Cloudflare Pages. Sin JavaScript para
renderizar contenido — todo el texto viaja en el HTML para que Google lo lea.
"""
import html
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
WA = ("https://wa.me/525522993258?text="
      "Hola%2C%20quiero%20agendar%20una%20cita%20en%20Stilo%20Sal%C3%B3n")

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
    ("Alaciado Express", "Express Straightening", "~280", "1 h", "a partir del hombro", "shoulder length and up"),
  ]},
"tratamientos": {
  "es": "Tratamientos y Alisados", "en": "Treatments & Smoothing",
  "items": [
    ("Nanoplastia", "Nanoplasty", "~2,500", "2 h", "alisado sin formol", "formaldehyde-free smoothing"),
    ("Brazilian Blowout", "Brazilian Blowout", "~2,500", "2 h", "a partir del hombro", "shoulder length and up"),
    ("Botox Capilar", "Hair Botox", "~1,800", "1 h", "a partir del hombro", "shoulder length and up"),
    ("Tratamiento Profundo Hidratante", "Deep Hydrating Treatment", "~520", "1 h", "a partir del hombro", "shoulder length and up"),
    ("Ampolleta Hidratante Alfa Parf", "Alfaparf Hydrating Ampoule", "220", "", "", ""),
  ]},
"mani-pedi": {
  "es": "Manicure y Pedicure", "en": "Manicure & Pedicure",
  "items": [
    ("Manicure Spa", "Spa Manicure", "220", "", "sales, exfoliación, masaje y esmalte", "salts, exfoliation, massage and polish"),
    ("Manicure Express con Gel", "Express Manicure with Gel", "250", "", "drill, limado y gel hasta 2 tonos lisos", "drill, file and gel up to 2 solid shades"),
    ("Manicure Spa + Gel", "Spa Manicure + Gel", "350", "", "spa completo con gel hasta 2 tonos", "full spa with gel up to 2 shades"),
    ("Pedicure Spa", "Spa Pedicure", "360", "", "tina con sales, limado de talón, masaje y esmalte", "salt soak, heel filing, massage and polish"),
    ("Pedicure Spa + Gel", "Spa Pedicure + Gel", "450", "", "spa completo con gel hasta 2 tonos", "full spa with gel up to 2 shades"),
    ("Paquete Mani Spa + Pedi Spa con Gel", "Spa Mani + Pedi Package with Gel", "750", "", "ambos servicios con gel hasta 2 tonos lisos", "both services with gel up to 2 solid shades"),
  ]},
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
    ("Vitamina", "Nail Vitamin", "150", "", "protege y fortalece la uña natural", "protects and strengthens the natural nail"),
  ]},
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
    ("Retiro de Acrílico", "Acrylic Removal", "100", "", "", ""),
  ]},
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
    ("Retiro + Aplicación Nueva", "Removal + New Set", "150", "", "retiro cuando pasaron más de 21 días y se aplica set nuevo", "removal past 21 days, when a new set is applied"),
  ]},
"cejas": {
  "es": "Cejas", "en": "Brows",
  "items": [
    ("Diseño de Ceja", "Brow Design", "450", "", "perfilado, diseño y laminación", "shaping, design and lamination"),
    ("Laminado de Ceja", "Brow Lamination", "450", "", "perfilado y laminación", "shaping and lamination"),
    ("Ceja con Cera", "Brow Wax", "220", "", "", ""),
  ]},
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
    ("Maquillaje", "Makeup Application", "950", "", "", ""),
  ]},
}

T = {  # cadenas de interfaz
 "es": {"price":"Precio","service":"Servicio","dur":"Duración","from":"desde",
        "hero_alt":"Balayage hecho en Stilo Salón, Roma Norte: castaño oscuro en raíz con puntas rubias","wa_aria":"Escríbenos por WhatsApp","wa_cta":"Escríbenos","book":"Reservar cita en línea","book_wa":"WhatsApp","appts":"Citas","hours":"Horario",
        "mf":"Lunes a viernes","sat":"Sábado","sun":"Domingo","closed":"cerrado",
        "branch":"Sucursal Roma Norte","services":"Servicios","skip":"Saltar al contenido",
        "menu":"Menú","directions":"Cómo llegar","rights":"Todos los derechos reservados.",
        "logo_alt":"Stilo Salón — salón de belleza en Roma Norte, CDMX","privacy":"Aviso de Privacidad","full_list":"Ver la lista completa de precios",
        "mxn":"Precios en pesos mexicanos (MXN).","other":"English"},
 "en": {"price":"Price","service":"Service","dur":"Duration","from":"from",
        "hero_alt":"Balayage done at Stilo Salón, Roma Norte: dark brown roots blending into blonde ends","wa_aria":"Message us on WhatsApp","wa_cta":"Message us","book":"Book online","book_wa":"WhatsApp","appts":"Appointments","hours":"Hours",
        "mf":"Monday to Friday","sat":"Saturday","sun":"Sunday","closed":"closed",
        "branch":"Roma Norte Location","services":"Services","skip":"Skip to content",
        "menu":"Menu","directions":"Get directions","rights":"All rights reserved.",
        "logo_alt":"Stilo Salón — beauty salon in Roma Norte, Mexico City","privacy":"Privacy Notice","full_list":"See the full price list",
        "mxn":"Prices in Mexican pesos (MXN).","other":"Español"},
}

NAV = {
 "es": [("/cabello.html","Cabello"),("/unas.html","Uñas"),
        ("/pestanas-y-cejas.html","Pestañas y Cejas"),("/precios.html","Precios"),("__BOOK__","Citas")],
 "en": [("/en/hair.html","Hair"),("/en/nails.html","Nails"),
        ("/en/lashes-and-brows.html","Lashes & Brows"),("/en/pricing.html","Pricing"),("__BOOK__","Book")],
}

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

def table(keys, lang):
    t, out = T[lang], []
    for k in keys:
        grp = PRICES[k]
        out.append(f'<div class="price-block" id="{k}">')
        out.append(f'<h3>{e(grp[lang])}</h3>')
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
    def _link(h, l):
        url = BOOKING if h == "__BOOK__" else h
        rel = ' rel="noopener"' if h == "__BOOK__" else ''
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
<meta name="theme-color" content="#15191D">
<meta property="og:image" content="{SITE}/assets/og.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_ld}
</head>
<body>
<a class="skip" href="#main">{t['skip']}</a>
<a class="wa-flot" href="{WA}" rel="noopener" aria-label="{t['wa_aria']}" title="{t['wa_aria']}">
  <svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path fill="currentColor" d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.65.08-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.14-.14.3-.35.45-.53.15-.18.2-.3.3-.5.1-.2.05-.38-.02-.53-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.07-.13-.27-.2-.57-.35zM12.04 21.5h-.01a9.43 9.43 0 0 1-4.8-1.32l-.35-.2-3.57.93.96-3.48-.23-.36a9.4 9.4 0 0 1-1.44-5.02c0-5.2 4.24-9.44 9.45-9.44 2.52 0 4.9.99 6.68 2.77a9.38 9.38 0 0 1 2.77 6.68c0 5.2-4.24 9.44-9.46 9.44zM20.5 3.49A11.36 11.36 0 0 0 12.04 0C5.76 0 .65 5.1.65 11.39c0 2 .52 3.96 1.52 5.68L.55 24l7.1-1.86a11.34 11.34 0 0 0 5.43 1.38h.01c6.28 0 11.39-5.11 11.39-11.4 0-3.04-1.18-5.9-3.33-8.05z"/></svg>
  <span class="wa-txt">{t['wa_cta']}</span>
</a>
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="{home}"><img src="/assets/logo-stilo-salon.png" width="640" height="252" alt="{t['logo_alt']}"></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="nav">{t['menu']}</button>
    <nav class="nav" id="nav" aria-label="{'Principal' if lang=='es' else 'Main'}">
      {nav}
      <div class="lang">
        <a href="{es_href}" hreflang="es-mx"{' aria-current="true"' if lang=='es' else ''}>ES</a>
        <a href="{en_href}" hreflang="en"{' aria-current="true"' if lang=='en' else ''}>EN</a>
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
        <p><a href="https://www.instagram.com/stilosalon91/" rel="noopener">Instagram</a><br>
        <a href="{GMB}" rel="noopener">Google</a><br>
        <a href="https://www.fresha.com/lvp/stilo-salon-guadalajara-ciudad-de-mexico-zn6WVb" rel="noopener">Fresha</a></p>
        <p style="margin-top:1rem"><a class="foot-resena" href="{RESENA}" rel="noopener">{'★ Escribe tu reseña' if lang=='es' else '★ Write your review'}</a></p>
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
      <span><a href="{'/aviso-de-privacidad.html' if lang=='es' else '/en/privacy.html'}">{t['privacy']}</a> · <a href="{en_href if lang=='es' else es_href}">{t['other']}</a></span>
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

  // ── Visor de galería ────────────────────────────────────────────────
  var figs = document.querySelectorAll('.galeria figure');
  if (figs.length) {{
    var visor = document.createElement('div');
    visor.className = 'visor';
    visor.setAttribute('role', 'dialog');
    visor.setAttribute('aria-modal', 'true');
    visor.innerHTML = '<button class="visor-cerrar" aria-label="Cerrar">&times;</button>' +
                      '<img alt=""><figcaption></figcaption>';
    document.body.appendChild(visor);
    var vImg = visor.querySelector('img');
    var vCap = visor.querySelector('figcaption');
    var abridor = null;

    function abrir(fig) {{
      var im = fig.querySelector('img');
      var cap = fig.querySelector('figcaption');
      vImg.src = im.currentSrc || im.src;
      vImg.alt = im.alt || '';
      vCap.textContent = cap ? cap.textContent : '';
      visor.classList.add('abierto');
      document.body.style.overflow = 'hidden';
      abridor = fig;
      visor.querySelector('.visor-cerrar').focus();
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
    document.addEventListener('keydown', function (ev) {{
      if (ev.key === 'Escape' && visor.classList.contains('abierto')) cerrar();
    }});
  }}

  // Encabezado compacto al bajar
  var head = document.querySelector('.site-head'), ticking = false;
  window.addEventListener('scroll', function () {{
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {{
      head.classList.toggle('scrolled', window.scrollY > 40);
      ticking = false;
    }});
  }}, {{ passive: true }});
}})();
</script>
</body>
</html>
"""

def write(path, content):
    p = OUT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"  {path}  ({len(content):,} bytes)"

# ─────────────────────────────────────────────────────────────────────────────
# CONTENIDO DE LAS PÁGINAS
# ─────────────────────────────────────────────────────────────────────────────
C = {
"es": {
 "home_h1": "¡Bonita la que lo lea!",
 "home_lede": "Bienvenida a Stilo Salón. Nos encanta consentirte y hacerte sentir como en casa: somos el lugar para relajarte, dejarte consentir y ser tú misma. Porque sabemos que la belleza no lo es todo… pero conocemos el gran poder que tiene para impulsarnos a ser la mejor versión de nosotras mismas.",
 "home_lede2": "Precios completos, con su duración, a la vista.",
 "home_why_h2": "Nos estamos actualizando, sin perder lo que ya funcionaba",
 "why": [
   ("Precios publicados", "La lista completa está en el sitio, no en un mensaje privado. Si un servicio requiere ajuste por largo o densidad de cabello, te lo decimos antes de empezar — nunca al momento de cobrar."),
   ("Técnica al día", "Nanoplastia, botox capilar y Brazilian Blowout con producto profesional. Extensiones de pestañas en cinco técnicas distintas, desde el 1x1 clásico hasta el volumen ruso."),
   ("Tiempos reales", "Cada servicio de la lista incluye su duración. Un balayage son tres horas y lo decimos de frente, para que organices tu día sin sorpresas."),
 ],
 "svc_cards": [
   ("Cabello", "Corte, tinte, balayage, babylights, matiz y peinado.", "desde $330", "/cabello.html", "Ver cabello y color"),
   ("Tratamientos", "Nanoplastia, Brazilian Blowout, botox capilar e hidratación profunda.", "desde $520", "/cabello.html#tratamientos", "Ver tratamientos y alisados"),
   ("Uñas", "Manicure y pedicure spa, gel, acrílico, esculturales y vitaminas.", "desde $150", "/unas.html", "Ver uñas, manicure y pedicure"),
   ("Pestañas y Cejas", "Extensiones 1x1 a volumen ruso, lifting, laminado y diseño de ceja.", "desde $450", "/pestanas-y-cejas.html", "Ver pestañas y cejas"),
 ],
 "faq": [
   ("¿Cuál es su horario de atención?", "Lunes a viernes de 9:00 a 20:00 y sábados de 9:00 a 19:00. Domingos cerrado."),
   ("¿Dónde están ubicados?", "En Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México. Estamos a unas cuadras del Metro Insurgentes."),
   ("¿Necesito cita o aceptan walk-in?", "Recomendamos cita, sobre todo para color y tratamientos que toman varias horas. Puedes reservar en línea a cualquier hora, escribirnos por WhatsApp o llamarnos. Recibimos walk-in según la disponibilidad del día."),
   ("¿Qué formas de pago aceptan?", "Efectivo y tarjetas de débito y crédito."),
   ("¿Los precios publicados son finales?", "Los precios marcados “desde” aplican a cabello a partir del hombro. Si tu cabello es más largo o más denso, el ajuste se te comunica antes de empezar el servicio, nunca al final."),
   ("¿Sus servicios tienen garantía?", "Sí. Si algo no quedó como lo acordamos, regresa dentro de los 7 días siguientes y lo corregimos sin costo."),
 ],
 "visit_h2": "Estamos en el corazón de la Roma Norte",
},
"en": {
 "home_h1": "Beautiful, whoever's reading this.",
 "home_lede": "Welcome to Stilo Salón. We love spoiling you and making you feel at home: this is the place to relax, be looked after, and be yourself. Because beauty isn't everything — but we know the power it has to push us toward the best version of ourselves.",
 "home_lede2": "Full prices, with real durations, in plain sight.",
 "home_why_h2": "We are modernizing, without losing what already worked",
 "why": [
   ("Published prices", "The full list is on the site, not in a private message. If a service needs an adjustment for hair length or density, we tell you before we start — never at the register."),
   ("Current technique", "Nanoplasty, hair botox and Brazilian Blowout with professional product. Eyelash extensions in five distinct techniques, from classic 1x1 to Russian volume."),
   ("Honest timing", "Every service on the list shows its duration. A balayage takes three hours and we say so up front, so you can plan your day."),
 ],
 "svc_cards": [
   ("Hair", "Cuts, color, balayage, babylights, toner and styling.", "from $330", "/en/hair.html", "See hair and color"),
   ("Treatments", "Nanoplasty, Brazilian Blowout, hair botox and deep hydration.", "from $520", "/en/hair.html#tratamientos", "See treatments and smoothing"),
   ("Nails", "Spa manicure and pedicure, gel, acrylic, sculpted nails and vitamins.", "from $150", "/en/nails.html", "See nails, manicure and pedicure"),
   ("Lashes & Brows", "Extensions from 1x1 to Russian volume, lifts, lamination and brow design.", "from $450", "/en/lashes-and-brows.html", "See lashes and brows"),
 ],
 "faq": [
   ("What are your hours?", "Monday to Friday, 9:00 to 20:00, and Saturday, 9:00 to 19:00. Closed Sundays."),
   ("Where are you located?", "Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Mexico City — a few blocks from Metro Insurgentes."),
   ("Do I need an appointment, or do you take walk-ins?", "We recommend an appointment, especially for color and treatments that take several hours. You can book online any time, message us on WhatsApp, or call. We do take walk-ins based on the day's availability."),
   ("What payment methods do you accept?", "Cash, and debit and credit cards."),
   ("Are the published prices final?", "Prices marked “from” apply to hair at shoulder length and above. If your hair is longer or denser, we tell you the adjustment before starting the service, never at the end."),
   ("Do your services come with a guarantee?", "Yes. If something did not turn out the way we agreed, come back within 7 days and we will correct it at no cost."),
 ],
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
      "openingHoursSpecification":[
        {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"09:00","closes":"20:00"},
        {"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"19:00"}],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)


FEATURED = [
  ("cabello", 1), ("cabello", 2), ("cabello", 8),
  ("tratamientos", 0), ("pestanas", 0), ("mani-pedi", 2),
]

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
    cards = "".join(
      f'<article class="card"><h3>{e(n)}</h3><p>{e(d)}</p>'
      f'<p class="from">{e(p)}</p><a class="more" href="{h}">{e(cta)}</a></article>'
      for n, d, p, h, cta in c["svc_cards"])
    why = "".join(f'<div><h3>{e(h)}</h3><p>{e(b)}</p></div>' for h, b in c["why"])
    faqs = "".join(
      f'<details class="faq"{" open" if i==0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>'
      for i, (q, a) in enumerate(c["faq"]))
    hi = "Roma Norte · Ciudad de México" if lang=="es" else "Roma Norte · Mexico City"
    return f"""
<section class="hero">
  <img class="marca-agua" src="/assets/logo-stilo-salon.png" alt="" aria-hidden="true">
  <div class="wrap hero-grid"><div>
  <p class="eyebrow">{hi}</p>
  <h1>{e(c['home_h1'])}</h1>
  <p class="lede">{e(c['home_lede'])}</p>
  <p class="lede-fino">{e(c['home_lede2'])}</p>
  <div class="btn-row">
    <a class="btn btn-primary" href="{BOOKING}" rel="noopener">{t['book']}</a>
    <a class="btn btn-wa" href="{WA}" rel="noopener">{t['book_wa']}</a>
    <a class="btn btn-ghost" href="tel:{NAP['tel1']}">{NAP['tel1_display']}</a>
  </div>
  <div class="trust">
    <div><strong>+10</strong>{'años en Roma Norte' if lang=='es' else 'years in Roma Norte'}</div>
    <div><a href="{GMB}" rel="noopener" style="text-decoration:none;color:inherit"><strong>{OPINIONES}</strong>{'opiniones en Google' if lang=='es' else 'Google reviews'}</a></div>
    <div><strong>60+</strong>{'servicios con precio publicado' if lang=='es' else 'services with published prices'}</div>
    <div><strong>7 {'días' if lang=='es' else 'days'}</strong>{'de garantía en cada servicio' if lang=='es' else 'guarantee on every service'}</div>
  </div>
</div>
<figure class="hero-figure">{img("hero", 900, 1125, t["hero_alt"], ALTA)}<span class="sello"><img src="/assets/logo-stilo-salon.png" width="640" height="252" alt="" aria-hidden="true"></span></figure>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-head"><p class="eyebrow">{'Nuestros servicios' if lang=='es' else 'Our services'}</p>
  <h2>{'Todo lo que hacemos, con su precio' if lang=='es' else 'Everything we do, with its price'}</h2></div>
  <div class="grid g4 js-reveal">{cards}</div>
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
  <h2>{'Búscanos, léenos, reserva' if lang=='es' else 'Look us up, read us, book'}</h2>
  <p class="lede">{f'Ya somos {OPINIONES} opiniones en Google. Si ya viniste, la tuya nos ayuda muchísimo a que más clientas nos encuentren.' if lang=='es' else f'We are at {OPINIONES} Google reviews. If you have been here, yours helps more clients find us.'}</p></div>
  <div class="perfiles">
    <a class="perfil" href="{GMB}" rel="noopener">
      <strong>Google</strong><span>{f'{OPINIONES} opiniones · cómo llegar' if lang=='es' else f'{OPINIONES} reviews · directions'}</span></a>
    <a class="perfil" href="https://www.instagram.com/stilosalon91/" rel="noopener">
      <strong>Instagram</strong><span>@stilosalon91</span></a>
    <a class="perfil" href="https://www.fresha.com/lvp/stilo-salon-guadalajara-ciudad-de-mexico-zn6WVb" rel="noopener">
      <strong>Fresha</strong><span>{'Reserva y reseñas' if lang=='es' else 'Booking and reviews'}</span></a>
    <a class="perfil destacado" href="{RESENA}" rel="noopener">
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
    <div class="btn-row"><a class="btn btn-primary" href="{BOOKING}" rel="noopener">{t['book']}</a>
    <a class="btn btn-wa" href="{WA}" rel="noopener">WhatsApp</a>
    <a class="btn btn-ghost" href="https://maps.google.com/?q=Guadalajara+70-B,+Roma+Norte,+CDMX" rel="noopener">{t['directions']}</a></div>
  </div>
  <figure class="hero-figure" style="aspect-ratio:4/3"><img src="/assets/contacto.jpg" width="1200" height="900" alt="" loading="lazy"></figure>
  </div>
</div></section>
"""

def svc_body(lang, eyebrow, h1, intro, paras, keys, note="", extra="", banner=""):
    t = T[lang]
    body = "".join(f"<p>{p}</p>" for p in paras)
    return f"""
<section style="padding-bottom:1.5rem"><div class="wrap">
  <p class="eyebrow">{e(eyebrow)}</p>
  <h1>{e(h1)}</h1>
  <p class="lede">{e(intro)}</p>
</div></section>
{f'<div class="wrap"><figure class="banner">{img(banner[:-4], 1400, 787, "", TARDE)}</figure></div>' if banner else ''}
<section class="alt" style="padding-top:0"><div class="wrap" style="max-width:74ch">{body}{extra}</div></section>
<section><div class="wrap">
  <p class="muted" style="font-size:.9rem">{t['mxn']} {e(note)}</p>
  {table(keys, lang)}
  <div class="btn-row"><a class="btn btn-primary" href="{BOOKING}" rel="noopener">{t['book']}</a>
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
      "En <strong id='tratamientos'>tratamientos y alisados</strong> trabajamos tres técnicas distintas, y la diferencia importa. La <strong>nanoplastia</strong> (desde $2,500) es un alisado sin formol que reestructura la fibra capilar y deja el cabello liso y con brillo por varios meses. El <strong>Brazilian Blowout</strong> (desde $2,500) sella la cutícula y reduce el frizz manteniendo movimiento — no deja el cabello completamente lacio. El <strong>botox capilar</strong> (desde $1,800, una hora) no alisa: rellena y repara cabello poroso o maltratado por decoloración.",
      "Si no sabes cuál te conviene, escríbenos por WhatsApp con una foto de tu cabello y te decimos con honestidad cuál sí y cuál no. A veces la respuesta es un <strong>tratamiento profundo hidratante</strong> de $520 y no un alisado de $2,500.",
      "Todos nuestros servicios tienen <strong>7 días de garantía</strong>: si algo no quedó como lo acordamos, regresas y lo corregimos sin costo.",
     ]),
   en=dict(eyebrow="Hair & color · Roma Norte",
     title="Haircuts, Color & Balayage in Roma Norte, Mexico City | Stilo Salón",
     desc="Women's cut from $330, color from $800, balayage from $2,300, nanoplasty from $2,500 MXN. Published prices and durations. Guadalajara 70-B, Roma Norte, Mexico City.",
     h1="Haircuts, color and hair treatments in Roma Norte",
     intro="All the hair work we do, with its real price and duration. No quotes by private message, and no last-minute adjustments.",
     paras=[
      "At Stilo Salón we work hair on three fronts: <strong>cutting</strong>, <strong>color</strong> and <strong>treatment</strong>. Each has its own logic of time and product, which is why we publish durations alongside prices. A women's cut with wash and style is thirty minutes. A balayage is three hours. Knowing that in advance lets you book without losing your day.",
      "For <strong>cuts</strong> we serve women, men and children. The difference between the cut with blow-dry shaping ($330) and the cut with wash and style ($420) is exactly that — the wash and the finished style. If you are in a hurry or arrive with clean hair, the first works; if you want to walk out ready, take the second.",
      "In <strong>color</strong> we cover everything from the simplest to the most technical. A <strong>root touch-up</strong> ($900) is monthly maintenance on color you already have. <strong>Full color</strong> (from $800) covers the whole head. <strong>Toner</strong> and <strong>color gloss</strong> (from $900) correct or refresh the tone without lifting the base. And <strong>balayage</strong> and <strong>babylights</strong> (from $2,300, three hours) are freehand lightening techniques that build natural dimension with a soft grow-out — no hard root line at six weeks.",
      "Color prices marked “from” apply at shoulder length and above. Longer or denser hair takes more product and more time, and we tell you that adjustment <strong>before</strong> we begin, with the mirror in front of you. Never at the register.",
      "In <strong id='tratamientos'>treatments and smoothing</strong> we work three distinct techniques, and the difference matters. <strong>Nanoplasty</strong> (from $2,500) is a formaldehyde-free smoothing service that restructures the hair fiber, leaving it straight and glossy for several months. <strong>Brazilian Blowout</strong> (from $2,500) seals the cuticle and cuts frizz while keeping movement — it does not leave hair perfectly flat. <strong>Hair botox</strong> (from $1,800, one hour) does not straighten: it fills and repairs porous hair damaged by bleaching.",
      "If you are not sure which one suits you, message us on WhatsApp with a photo of your hair and we will tell you honestly which will work and which will not. Sometimes the answer is a $520 deep hydrating treatment rather than a $2,500 smoothing service.",
      "Every service carries a <strong>7-day guarantee</strong>: if something did not turn out the way we agreed, come back and we will correct it at no cost.",
     ])),
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
     ]),
   en=dict(eyebrow="Nails · Roma Norte",
     title="Nails, Manicure & Pedicure in Roma Norte, Mexico City | Stilo Salón",
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
     ])),
 dict(key="lashes", es_slug="/pestanas-y-cejas.html", en_slug="/en/lashes-and-brows.html",
   keys=["pestanas", "cejas", "depilacion"],
   es=dict(eyebrow="Pestañas y cejas · Roma Norte",
     title="Extensiones de Pestañas y Diseño de Cejas en Roma Norte, CDMX | Stilo Salón",
     desc="Extensiones de pestañas desde $750: 1x1, flat, YY, híbridas y volumen ruso. Lifting $450, laminado de ceja $450. Roma Norte, CDMX. Citas: 55 2299 3258.",
     h1="Extensiones de pestañas y diseño de cejas en Roma Norte",
     intro="¿Quieres saber cuánto cuestan? ¿Qué técnicas existen? ¿Cuál es apta para ti? ¿Cuánto duran? Aquí está toda la información detallada de esta maravillosa forma de lucir unos ojos y unas cejas de impacto.",
     paras=[]),
   en=dict(eyebrow="Lashes & brows · Roma Norte",
     title="Eyelash Extensions & Brow Design in Roma Norte, Mexico City | Stilo Salón",
     desc="Eyelash extensions from $750 MXN: classic 1x1, flat, YY, hybrid and Russian volume. Lash lift $450, brow lamination $450. Roma Norte, Mexico City.",
     h1="Eyelash extensions and brow design in Roma Norte",
     intro="Want to know what they cost? Which techniques exist? Which one suits you? How long they last? Here is everything you need to know about this wonderful way to get eyes and brows with real impact.",
     paras=[])),
]

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
     p="We do not recommend it if you have not worn hybrid or classic first — the natural lash needs to be prepared for the weight.")),
]

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
    o.append(f'<h2>{"Los tres alisados, comparados" if es else "The three smoothing services, compared"}</h2>')
    o.append('<p>' + ("No son lo mismo y elegir mal es caro. Esta es la diferencia:"
      if es else "They are not the same, and choosing wrong is expensive. Here is the difference:") + '</p>')
    rows = ([("Nanoplastia", "$2,500", "2 h", "Alisa de verdad, sin formol. Reestructura la fibra.",
              "Quieres el cabello liso y con brillo varios meses."),
             ("Brazilian Blowout", "$2,500", "2 h", "Sella la cutícula y baja el frizz, conservando movimiento.",
              "Quierescontrolar el frizz pero no perder tu onda natural."),
             ("Botox capilar", "$1,800", "1 h", "No alisa: rellena y repara.",
              "Tu cabello está poroso o maltratado por decoloración.")]
            if es else
            [("Nanoplasty", "$2,500", "2 h", "Genuinely straightens, formaldehyde-free. Restructures the fiber.",
              "You want straight, glossy hair for several months."),
             ("Brazilian Blowout", "$2,500", "2 h", "Seals the cuticle and cuts frizz while keeping movement.",
              "You want frizz control without losing your natural wave."),
             ("Hair botox", "$1,800", "1 h", "Does not straighten: it fills and repairs.",
              "Your hair is porous or damaged from bleaching.")])
    th = ("Servicio","Precio","Tiempo","Qué hace","Te conviene si") if es else ("Service","Price","Time","What it does","Choose it if")
    o.append('<table class="price"><thead><tr>' + "".join(f'<th>{x}</th>' for x in th) + '</tr></thead><tbody>' +
      "".join(f'<tr><td class="svc">{a}</td><td class="amt">{b}</td><td class="dur">{c}</td>'
              f'<td>{d}</td><td>{ee}</td></tr>' for a,b,c,d,ee in rows) + '</tbody></table>')
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
      "acrylic itself. Waiting two months does not save money, it costs nail. A fill is always cheaper than a full set.") + '</p>')
    o.append('<p>' + ("El <strong>retiro</strong> ($100) lo hacemos siempre con técnica y producto. Arrancarte el acrílico en casa "
      "se lleva capas de tu uña natural, y recuperarlas toma meses."
      if es else
      "<strong>Removal</strong> ($100) is always done with proper technique and product. Prying acrylic off at home takes layers of "
      "your natural nail with it, and those take months to grow back.") + '</p>')
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
    return "\n".join(o)

HAIR_FAQ = {
 "es": [("¿Cuál es la diferencia entre balayage y babylights?",
         "El balayage se pinta a mano alzada de medios a puntas y deja una transición suave que crece sin línea marcada. Los babylights son mechones muy finos tomados desde la raíz que imitan el aclarado natural del sol: se ven más parejos y menos contrastados. Ambos cuestan desde $2,300 y toman tres horas."),
        ("¿Cada cuándo debo retocar la raíz?",
         "Con tinte global o base, entre cuatro y seis semanas. Con balayage o babylights puedes estirarlo a tres o cuatro meses porque el crecimiento es suave por diseño."),
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
         "Cada tres o cuatro semanas. El retoque siempre cuesta menos que el juego completo, y esperar más tiempo termina costando uña."),
        ("¿Puedo retirarme el gel o el acrílico en casa?",
         "No te lo recomendamos. Arrancarlo se lleva capas de tu uña natural y recuperarlas toma meses. El retiro con técnica cuesta $100."),
        ("Tengo la uña débil después de mucho acrílico, ¿qué hago?",
         "Empieza por las vitaminas ($150): el calcio fortalece, el rubber cubre imperfecciones y da cuerpo a uñas delgadas, y la vitamina protege mientras la uña se recupera. Se pueden combinar con gel para que no dejes de traerlas arregladas."),
        ("¿Qué incluye el manicure spa?",
         "Tina con sales, exfoliación, masaje y esmalte, por $220. Con gel en lugar de esmalte son $350. El pedicure spa ($360) añade limado de talón y masaje de pies.")],
 "en": [("Acrylic or gel?",
         "If your natural nail is healthy, gel looks just as good and treats it better. Acrylic makes sense when you want structure and length. Gel lasts two to three weeks; acrylic holds longer but needs a fill every three to four weeks."),
        ("Does acrylic damage the natural nail?",
         "The damage does not come from the acrylic, it comes from letting it grow out too long: as the nail grows, product lifts at the base and moisture gets in. With fills every three to four weeks and proper removal, the natural nail stays healthy."),
        ("How often do I need a fill?",
         "Every three to four weeks. A fill always costs less than a full set, and waiting longer ends up costing nail."),
        ("Can I remove gel or acrylic at home?",
         "We do not recommend it. Prying it off takes layers of your natural nail with it, and those take months to grow back. Professional removal is $100."),
        ("My nails are weak after a long run of acrylic — what now?",
         "Start with nail vitamins ($150): calcium strengthens, rubber base covers imperfections and adds body to thin nails, and nail vitamin protects while the nail recovers. They combine with gel so you do not have to go bare."),
        ("What does the spa manicure include?",
         "A salt soak, exfoliation, massage and polish, for $220. With gel instead of polish it is $350. The spa pedicure ($360) adds heel filing and a foot massage.")],
}

def topic_faq_ld(table, lang):
    body = ",".join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
                    % (_j(q), _j(a)) for q, a in table[lang])
    return ('<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}</script>' % body)

# Fotos reales de trabajos del salón. Son exportaciones de Instagram a 640x640,
# suficientes para galería pero NO para una portada a sangre completa.
GALERIA = {
 "hair": [("trabajo-cabello-01.jpg",
           "Balayage en cabello largo hecho en Stilo Salón Roma Norte, transición de castaño a rubio",
           "Balayage · 3 horas · desde $2,300",
           "Long-hair balayage done at Stilo Salón Roma Norte, brown blending into blonde",
           "Balayage · 3 hours · from $2,300"),
          ("trabajo-cabello-02.jpg",
           "Balayage con ondas hecho en Stilo Salón Roma Norte",
           "Balayage con ondas · Alto peinado desde $600",
           "Balayage with waves done at Stilo Salón Roma Norte",
           "Balayage with waves · Updo from $600")],
 "nails": [("trabajo-unas-01.jpg",
            "Manicure francés con uña larga cuadrada, hecho en Stilo Salón Roma Norte",
            "Francés con uña cuadrada · Manicure Spa + Gel",
            "French manicure, square tip, done at Stilo Salón Roma Norte",
            "Square-tip French · Spa Manicure + Gel"),
           ("trabajo-unas-02.jpg",
            "Uñas acrílicas largas en rojo y verde con diseño, hechas en Stilo Salón Roma Norte",
            "Acrílico largo con diseño · Uña escultural con gel",
            "Long acrylic nails in red and green with art, done at Stilo Salón Roma Norte",
            "Long acrylic with nail art · Sculpted gel")],
}

def galeria_html(key, lang):
    items = GALERIA.get(key)
    if not items: return ""
    es = lang == "es"
    figs = "".join(
      f'<figure><img src="/assets/{f}" width="640" height="640" loading="lazy" '
      f'alt="{e(alt_es if es else alt_en)}"><figcaption>{e(cap_es if es else cap_en)}</figcaption></figure>'
      for f, alt_es, cap_es, alt_en, cap_en in items)
    titulo = "Trabajos hechos aquí" if es else "Work done here"
    return f'<h2>{titulo}</h2><div class="galeria js-reveal">{figs}</div>'

def main():
    log = []
    # Home (ES + EN)
    for lang in ("es", "en"):
        home, alt = ("/", f"{SITE}/en/") if lang == "es" else ("/en/", f"{SITE}/")
        title = ("Stilo Salón | Salón de Belleza en Roma Norte, CDMX — Cabello, Uñas y Pestañas"
                 if lang == "es" else
                 "Stilo Salón | Beauty Salon in Roma Norte, Mexico City — Hair, Nails & Lashes")
        desc = ("Salón de belleza en Roma Norte, CDMX. Corte desde $330, balayage desde $2,300, "
                "extensiones de pestañas desde $750. Precios publicados, sin sorpresas. "
                "Reserva en línea o al 55 2299 3258."
                if lang == "es" else
                "Beauty salon in Roma Norte, Mexico City. Cuts from $330, balayage from $2,300, "
                "lash extensions from $750 MXN. Published prices, no surprises. "
                "Guadalajara 70-B. Book online or call 55 2299 3258.")
        out = "index.html" if lang == "es" else "en/index.html"
        log.append(write(out, page(lang, "", title, desc, home_body(lang), alt,
                                   salon_ld(lang) + faq_ld(lang))))
    # Service pages
    for sp in SERVICE_PAGES:
        for lang in ("es", "en"):
            d = sp[lang]
            slug = sp["es_slug"] if lang == "es" else sp["en_slug"]
            alt  = SITE + (sp["en_slug"] if lang == "es" else sp["es_slug"])
            extra = {"lashes": lash_guide, "hair": hair_guide, "nails": nails_guide}[sp["key"]](lang)
            extra += galeria_html(sp["key"], lang)
            bnr = {"hair":"h-cabello.jpg","nails":"h-unas.jpg","lashes":"h-pestanas.jpg"}[sp["key"]]
            body = svc_body(lang, d["eyebrow"], d["h1"], d["intro"], d["paras"], sp["keys"], extra=extra, banner=bnr)
            faq = {"lashes": lambda l: lash_faq_ld(l),
                   "hair":   lambda l: topic_faq_ld(HAIR_FAQ, l),
                   "nails":  lambda l: topic_faq_ld(NAILS_FAQ, l)}[sp["key"]](lang)
            ld = salon_ld(lang) + faq
            log.append(write(slug.lstrip("/"), page(lang, slug, d["title"], d["desc"], body, alt, ld)))
    # Full price list
    allk = list(PRICES.keys())
    for lang in ("es", "en"):
        slug = "/precios.html" if lang == "es" else "/en/pricing.html"
        alt  = SITE + ("/en/pricing.html" if lang == "es" else "/precios.html")
        title = ("Lista de Precios Completa | Stilo Salón Roma Norte, CDMX" if lang == "es"
                 else "Full Price List | Stilo Salón Roma Norte, Mexico City")
        desc = ("Lista de precios completa de Stilo Salón: cabello, tratamientos, uñas, pestañas, "
                "cejas y depilación. Más de 60 servicios con precio y duración. Roma Norte, CDMX."
                if lang == "es" else
                "Full price list for Stilo Salón: hair, treatments, nails, lashes, brows and waxing. "
                "Over 60 services with price and duration. Roma Norte, Mexico City.")
        h1 = "Lista de precios completa" if lang == "es" else "Full price list"
        intro = ("Todos nuestros servicios con su precio y su duración. Los precios marcados “desde” "
                 "aplican a cabello a partir del hombro; cualquier ajuste te lo decimos antes de empezar."
                 if lang == "es" else
                 "Every service with its price and duration. Prices marked “from” apply at shoulder "
                 "length and above; any adjustment is discussed before we begin.")
        body = svc_body(lang, "Roma Norte · CDMX" if lang=="es" else "Roma Norte · Mexico City",
                        h1, intro, [], allk)
        log.append(write(slug.lstrip("/"), page(lang, slug, title, desc, body, alt, salon_ld(lang))))
    # Privacy
    for lang in ("es", "en"):
        slug = "/aviso-de-privacidad.html" if lang == "es" else "/en/privacy.html"
        alt  = SITE + ("/en/privacy.html" if lang == "es" else "/aviso-de-privacidad.html")
        if lang == "es":
            title, h1 = "Aviso de Privacidad | Stilo Salón", "Aviso de Privacidad"
            desc = ("Aviso de privacidad de Stilo Salón, salón de belleza en Roma Norte, CDMX. Qué datos recabamos para tu cita, para qué los usamos y cómo ejercer tus derechos ARCO.")
            ps = ["<strong>Stilo Salón</strong>, con domicilio en Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México, es responsable del tratamiento de tus datos personales.",
                  "<strong>Qué datos recabamos.</strong> Únicamente los necesarios para agendar y dar seguimiento a tu cita: nombre, teléfono y, cuando aplica, el historial de servicios realizados en el salón.",
                  "<strong>Para qué los usamos.</strong> Para confirmar y recordarte tus citas, llevar el registro de los servicios que te hemos hecho, y contactarte si necesitamos reprogramar. No vendemos ni compartimos tus datos con terceros.",
                  "<strong>Tus derechos.</strong> Puedes solicitar el acceso, la rectificación, la cancelación o la oposición al tratamiento de tus datos (derechos ARCO) llamando al 55 2299 3258 o directamente en el salón.",
                  "<strong>Cambios.</strong> Cualquier modificación a este aviso se publicará en esta misma página.",
                  "Última actualización: septiembre de 2026."]
        else:
            title, h1 = "Privacy Notice | Stilo Salón", "Privacy Notice"
            desc = ("Privacy notice for Stilo Salón, a beauty salon in Roma Norte, Mexico City. What data we collect for your appointment, how we use it, and how to exercise your rights.")
            ps = ["<strong>Stilo Salón</strong>, located at Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Mexico City, is responsible for the handling of your personal data.",
                  "<strong>What we collect.</strong> Only what is needed to book and follow up on your appointment: name, phone number and, where applicable, the history of services performed at the salon.",
                  "<strong>How we use it.</strong> To confirm and remind you of appointments, keep a record of the services we have performed, and contact you if we need to reschedule. We do not sell or share your data with third parties.",
                  "<strong>Your rights.</strong> You may request access, rectification, cancellation or object to the handling of your data (ARCO rights) by calling 55 2299 3258 or in person at the salon.",
                  "<strong>Changes.</strong> Any change to this notice will be published on this page.",
                  "Last updated: September 2026."]
        body = (f'<section><div class="wrap" style="max-width:74ch"><h1>{h1}</h1>'
                + "".join(f"<p>{p}</p>" for p in ps) + '</div></section>')
        log.append(write(slug.lstrip("/"), page(lang, slug, title, desc, body, alt)))

    # sitemap / robots / Cloudflare
    urls = ["/", "/cabello.html", "/unas.html", "/pestanas-y-cejas.html", "/precios.html",
            "/aviso-de-privacidad.html", "/en/", "/en/hair.html", "/en/nails.html",
            "/en/lashes-and-brows.html", "/en/pricing.html", "/en/privacy.html"]
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
        "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n"))
    # Rutas viejas del sitio de GoDaddy -> nuevas.  Evita perder el poco
    # posicionamiento que ya existe.
    log.append(write("_redirects",
        "/cabello            /cabello.html            301\n"
        "/u%C3%B1as          /unas.html               301\n"
        "/unas               /unas.html               301\n"
        "/extensiones        /pestanas-y-cejas.html   301\n"
        "/lifting            /pestanas-y-cejas.html   301\n"
        "/microblading       /pestanas-y-cejas.html   301\n"
        "/dise%C3%B1o-de-ceja /pestanas-y-cejas.html  301\n"
        "/servicios-y-costos /precios.html            301\n"
        "/colores-y-dise%C3%B1os-lv-1 /unas.html      301\n"
        "/comun%C3%ADcate-con-nosotros /#contacto     301\n"
        "/informacion        /pestanas-y-cejas.html   301\n"
        "/citas              /#contacto               301\n"
        "/galeria            /                        301\n"
        "/ols/products       /precios.html            301\n"))
    print("Stilo Salón — sitio generado:\n" + "\n".join(log))
    print(f"\n{len(urls)} páginas · fuente única de precios: PRICES en build.py")

if __name__ == "__main__":
    main()
