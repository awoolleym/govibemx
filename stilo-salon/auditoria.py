#!/usr/bin/env python3
"""Auditoría SEO de las 21 páginas, español e inglés.

Sólo reporta lo que puede comprobar en el HTML generado. Nada de estimaciones.
"""
import html as _html, json, pathlib, re, sys, urllib.parse
from collections import defaultdict

RAIZ = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
SITE = "https://stilo-salon.com"

def paginas():
    # Las exclusiones se miden RELATIVAS a la raíz que se audita: si no, al
    # apuntar a _dist el script se excluye a sí mismo y audita cero páginas.
    return sorted(p for p in RAIZ.rglob("*.html")
                  if not any(x.startswith(("_preview", "_fotos", "_dist"))
                             for x in p.relative_to(RAIZ).parts)
                  and p.name not in ("preview-movil.html",))

def resuelve(u):
    u = u.lstrip("/")
    for c in ([u + "index.html"] if (u == "" or u.endswith("/")) else
              [u, u + ".html", u + "/index.html"]):
        if (RAIZ / c).exists():
            return True
    return False

def sin_scripts(t):
    return re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', t, flags=re.S)

fallos, avisos = [], []
def mal(p, msg):  fallos.append(f"{p}: {msg}")
def ojo(p, msg):  avisos.append(f"{p}: {msg}")

datos = {}
for p in paginas():
    rel = str(p.relative_to(RAIZ))
    t = p.read_text(encoding="utf-8")
    c = sin_scripts(t)
    main = re.search(r'<main.*?</main>', c, re.S)
    main = main.group(0) if main else c

    # La 404 es un caso aparte y a propósito: una página de error no lleva
    # canonical, ni hreflang, ni og:url, ni entra al sitemap. Google no debe
    # indexarla —por eso lleva noindex— así que exigirle esas etiquetas sería
    # marcar como fallo justo lo correcto.
    es404 = rel == "404.html"

    d = {}
    # Hay que descodificar las entidades antes de medir: en el HTML crudo
    # "&amp;" ocupa cinco caracteres, pero Google ve uno.
    m = re.search(r'<title>(.*?)</title>', t, re.S)
    d["title"] = _html.unescape(m.group(1).strip()) if m else ""
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    d["desc"] = _html.unescape(m.group(1)) if m else ""
    m = re.search(r'<html lang="([^"]+)"', t);                   d["lang"] = m.group(1) if m else ""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', t);   d["canon"] = m.group(1) if m else ""
    d["alt"] = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', t))
    d["h1"] = re.findall(r'<h1[^>]*>(.*?)</h1>', c, re.S)
    d["og"] = dict(re.findall(r'<meta property="og:([a-z:]+)" content="([^"]*)"', t))
    d["ld"] = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: d["ld"].append(json.loads(m.group(1)))
        except Exception as e: mal(rel, f"JSON-LD inválido ({e})")
    d["encabezados"] = [(int(n), re.sub(r'<[^>]+>', '', txt).strip())
                        for n, txt in re.findall(r'<h([1-6])[^>]*>(.*?)</h\1>', main, re.S)]
    d["imgs"] = re.findall(r'<img [^>]*>', c)
    d["texto"] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', main)).strip()
    datos[rel] = d

    # ── título y descripción
    if not d["title"]: mal(rel, "sin <title>")
    elif not 30 <= len(d["title"]) <= 60: ojo(rel, f"título de {len(d['title'])} car. (ideal 30-60)")
    if not d["desc"]: mal(rel, "sin meta description")
    elif not 70 <= len(d["desc"]) <= 160: ojo(rel, f"descripción de {len(d['desc'])} car. (ideal 70-160)")

    # ── h1 y jerarquía
    if len(d["h1"]) != 1: mal(rel, f"{len(d['h1'])} etiquetas h1 (debe haber 1)")
    niveles = [n for n, _ in d["encabezados"]]
    for a, b in zip(niveles, niveles[1:]):
        if b > a + 1: mal(rel, f"salto de encabezado h{a} -> h{b}")

    # ── canonical
    if not d["canon"]:
        (ojo if es404 else mal)(rel, "sin canonical" + (" (correcto en una 404)" if es404 else ""))
    elif not d["canon"].startswith(SITE): mal(rel, f"canonical no absoluto: {d['canon']}")
    elif not resuelve(d["canon"][len(SITE):]): mal(rel, f"canonical no corresponde a ninguna página: {d['canon']}")

    # ── idioma
    esperado = "en" if rel.startswith("en/") else "es-MX"
    if d["lang"] != esperado: mal(rel, f'lang="{d["lang"]}" y debería ser "{esperado}"')

    # ── hreflang
    if not es404:
        for k in ("es-mx", "en", "x-default"):
            if k not in d["alt"]: mal(rel, f"falta hreflang {k}")

    # ── Open Graph
    for k in ("title", "description", "url", "image", "type", "locale"):
        if k == "url" and es404: continue
        if k not in d["og"]: mal(rel, f"falta og:{k}")
    if d["og"].get("url") and d["og"]["url"] != d["canon"]:
        mal(rel, "og:url no coincide con el canonical")
    loc_esp = "en_US" if rel.startswith("en/") else "es_MX"
    if d["og"].get("locale") and d["og"]["locale"] != loc_esp:
        mal(rel, f'og:locale="{d["og"]["locale"]}" y debería ser "{loc_esp}"')

    # ── imágenes
    for tag in d["imgs"]:
        if "alt=" not in tag: mal(rel, f"imagen sin alt: {tag[:70]}")
        if not ("width=" in tag and "height=" in tag):
            ojo(rel, f"imagen sin width/height (provoca saltos de maquetación): {tag[:70]}")

    # ── enlaces internos
    for attr, url in re.findall(r'\b(href|src)="([^"]+)"', c):
        if url.startswith(("http", "mailto:", "tel:", "//", "data:")): continue
        u = urllib.parse.unquote(url).split("#")[0]
        if u and not resuelve(u): mal(rel, f"enlace roto: {url}")

    # ── contenido delgado
    n = len(d["texto"].split())
    if n < 300 and not es404: ojo(rel, f"sólo {n} palabras de contenido")

# ── unicidad de títulos y descripciones
for campo, nombre in (("title", "título"), ("desc", "descripción")):
    vistos = defaultdict(list)
    for rel, d in datos.items(): vistos[d[campo]].append(rel)
    for v, ps in vistos.items():
        if len(ps) > 1: mal(", ".join(ps), f"{nombre} duplicado: “{v[:50]}…”")

# ── hreflang recíproco (de verdad: el conjunto debe ser idéntico en ambas)
for rel, d in datos.items():
    for k, destino in d["alt"].items():
        if k == "x-default": continue
        ruta = destino[len(SITE):].lstrip("/")
        for cand in ([ruta + "index.html"] if (ruta == "" or ruta.endswith("/")) else
                     [ruta, ruta + ".html", ruta + "/index.html"]):
            if cand in datos:
                otra = datos[cand]
                if otra["alt"] != d["alt"]:
                    mal(rel, f"hreflang no recíproco con {cand}: {d['alt']} vs {otra['alt']}")
                break
        else:
            mal(rel, f"hreflang {k} apunta a una página que no existe: {destino}")

# ── paridad español / inglés
# La 404 es una sola para los dos idiomas, así que no cuenta en la paridad.
es = {r for r in datos if not r.startswith("en/") and r != "404.html"}
en = {r for r in datos if r.startswith("en/")}
if len(es) != len(en): mal("global", f"{len(es)} páginas en español y {len(en)} en inglés")

# ── idioma real del texto (fuga de un idioma al otro)
MARCA_ES = re.compile(r'\b(pesta[ñn]as|u[ñn]as|cabello|precio|desde|reserva|cita|nuestros?|salón)\b', re.I)
MARCA_EN = re.compile(r'\b(the|and|your|from|book|price|hair|nails|lashes|our)\b', re.I)
for rel, d in datos.items():
    txt = d["texto"]
    if not txt: continue
    ces, cen = len(MARCA_ES.findall(txt)), len(MARCA_EN.findall(txt))
    if rel == "404.html": continue   # lleva los dos idiomas a propósito
    if rel.startswith("en/") and ces > cen * 0.25:
        mal(rel, f"texto en español dentro de la versión inglesa ({ces} marcas ES vs {cen} EN)")
    if not rel.startswith("en/") and cen > ces * 0.25:
        mal(rel, f"texto en inglés dentro de la versión española ({cen} marcas EN vs {ces} ES)")

# ── sitemap y robots
sm = (RAIZ / "sitemap.xml")
if not sm.exists(): mal("global", "no hay sitemap.xml")
else:
    urls = set(re.findall(r'<loc>([^<]+)</loc>', sm.read_text(encoding="utf-8")))
    canons = {d["canon"] for d in datos.values() if d["canon"]}
    for u in sorted(urls - canons): mal("sitemap", f"lista una URL que ninguna página declara como canónica: {u}")
    for u in sorted(canons - urls):
        if u.endswith("/404"): continue
        mal("sitemap", f"falta la URL canónica {u}")
rb = (RAIZ / "robots.txt")
if not rb.exists(): mal("global", "no hay robots.txt")
else:
    r = rb.read_text(encoding="utf-8")
    if "Sitemap:" not in r: mal("robots.txt", "no apunta al sitemap")
    if re.search(r'^Disallow:\s*/\s*$', r, re.M): mal("robots.txt", "bloquea todo el sitio")

# ── datos estructurados
tipos = defaultdict(int)
for rel, d in datos.items():
    for b in d["ld"]:
        for obj in (b if isinstance(b, list) else [b]):
            tipos[obj.get("@type", "?")] += 1
for req in ("HairSalon", "FAQPage"):
    if not tipos.get(req): mal("global", f"ningún bloque JSON-LD de tipo {req}")

print(f"páginas auditadas: {len(datos)}  ({len(es)} ES · {len(en)} EN)")
print(f"tipos de datos estructurados: {dict(tipos)}")
print(f"\nFALLOS: {len(fallos)}")
for f in fallos: print("  ✗", f)
print(f"\nAVISOS: {len(avisos)}")
for a in avisos: print("  ·", a)
