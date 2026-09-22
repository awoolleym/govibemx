#!/usr/bin/env python3
"""Regenera assets/pf/ desde los originales, con la marca de agua quemada.

Por qué quemada y no con CSS: un logo puesto encima con CSS no protege nada.
Clic derecho > guardar imagen baja el archivo limpio, y la foto se va sin
marca. La única marca que sirve es la que vive dentro del JPEG.

Los originales viven en _fotos3/, que está fuera de git porque pesa 60 MB;
la fuente real es la carpeta "Fotos Web — Stilo Salón" del Drive del salón.
El script siempre parte de ahí, nunca de assets/pf/, para que correrlo dos
veces no encime dos marcas.

    python3 marca_agua.py              # todas
    python3 marca_agua.py --muestra    # solo 4, a /tmp, para ver cómo queda
"""
import json, pathlib, sys
from PIL import Image, ImageFilter

RAIZ   = pathlib.Path(__file__).parent
FUENTE = RAIZ / "_fotos3"
DESTINO = RAIZ / "assets/pf"
LOGO   = RAIZ / "assets/logo-stilo-salon-negativo.png"
W, H   = 720, 960

# ── Los tres números que importan ────────────────────────────────────────
ANCHO   = 0.28   # ancho del logo como fracción del ancho de la foto
OPACIDAD = 0.46  # 0 = invisible, 1 = sólido
MARGEN  = 0.045  # separación de la esquina, fracción del ancho

# Casi todas las fotos de uñas llevan la tarjeta física del salón abajo:
# la marca ahí encima serían dos logos peleando. En uñas sube a la esquina
# de arriba, que en esas fotos es fondo.
ESQUINA = {"cabello": "abajo", "pestanas": "abajo", "unas": "arriba"}
# ─────────────────────────────────────────────────────────────────────────

SESGO = {"cabello": 0.35, "unas": 0.5, "pestanas": 0.5}


def recorta(im, w, h, sesgo):
    iw, ih = im.size
    obj, act = w / h, iw / ih
    if act > obj:
        nw = int(ih * obj); x = int((iw - nw) * 0.5)
        im = im.crop((x, 0, x + nw, ih))
    else:
        nh = int(iw / obj); y = int((ih - nh) * sesgo)
        im = im.crop((0, y, iw, y + nh))
    return im.resize((w, h), Image.LANCZOS)


def sello(ancho_px, luz):
    """El logo blanco a su tamaño final, con una sombra suave detrás.

    La sombra no es decoración. El logo es blanco y de trazo finísimo: sobre
    unas uñas en glitter plateado se borra por completo. Por eso la sombra
    se ajusta a lo que hay debajo — `luz` es el brillo medio de esa esquina,
    de 0 a 255 — y sobre fondo claro aparece un halo oscuro que sostiene el
    trazo, mientras que sobre fondo oscuro casi no hace falta.
    """
    lg = Image.open(LOGO).convert("RGBA")
    alto = round(ancho_px * lg.height / lg.width)
    lg = lg.resize((ancho_px, alto), Image.LANCZOS)

    # En fondo claro además subimos un poco la opacidad del blanco.
    claro = min(1.0, max(0.0, (luz - 90) / 110))          # 0 oscuro … 1 claro
    op    = OPACIDAD * (1 + 0.30 * claro)
    a = lg.split()[3].point(lambda p: min(255, int(p * op)))
    lg.putalpha(a)

    pad = max(3, ancho_px // 55)
    caja = Image.new("RGBA", (ancho_px + pad * 4, alto + pad * 4), (0, 0, 0, 0))

    fuerza = int((70 + 150 * claro) * OPACIDAD)
    sombra = Image.new("RGBA", caja.size, (0, 0, 0, 0))
    sombra.paste((0, 0, 0, fuerza), (pad * 2, pad * 2), a)
    sombra = sombra.filter(ImageFilter.GaussianBlur(pad * (1.2 + 1.1 * claro)))
    if claro > 0.45:        # dos pasadas: el halo aguanta el glitter
        caja.alpha_composite(sombra)
    caja.alpha_composite(sombra)
    caja.alpha_composite(lg, (pad * 2, pad * 2))
    return caja


def marca(im, cat):
    ancho_px = round(im.width * ANCHO)
    ins = round(im.width * MARGEN)
    alto_px = round(ancho_px * 252 / 640)          # proporción del logo
    x = im.width - ancho_px - ins
    y = ins if ESQUINA[cat] == "arriba" else im.height - alto_px - ins

    # Brillo medio justo donde va la marca, para calibrar la sombra.
    trozo = im.convert("L").crop((x, y, x + ancho_px, y + alto_px))
    luz = sum(i * c for i, c in enumerate(trozo.histogram())) / (ancho_px * alto_px)

    m = sello(ancho_px, luz)
    im = im.convert("RGBA")
    im.alpha_composite(m, (x - (m.width - ancho_px) // 2,
                           y - (m.height - alto_px) // 2))
    return im.convert("RGB")


def piezas():
    sys.path.insert(0, str(FUENTE))
    from _sel import SEL
    from _sel2 import SEL2
    return SEL + SEL2


def galerias(salida):
    """Las fotos de 'Trabajos hechos aquí' de cada página de servicio.

    Las copias limpias viven en _fotos3/_limpias/ justamente para que correr
    esto dos veces no encime dos marcas; assets/ nunca es la fuente.
    """
    limpias = FUENTE / "_limpias"
    if not limpias.exists():
        print("  (sin _fotos3/_limpias, salto las galerías)")
        return 0
    cat_de = {"cabello": "cabello", "unas": "unas", "pestanas": "pestanas"}
    n = 0
    for f in sorted(limpias.glob("trabajo-*.jpg")):
        cat = cat_de[f.stem.split("-")[1]]
        im = marca(Image.open(f).convert("RGB"), cat)
        im.save(salida / f.name, quality=84, optimize=True, progressive=True)
        n += 1
    return n


def main():
    muestra = "--muestra" in sys.argv
    idx = json.load(open(FUENTE / "_index.json"))
    sel = piezas()
    if muestra:
        # una clara, una oscura, un cabello y unas pestañas
        sel = [s for s in sel if s[0] in ("120", "126", "52", "163")]
        salida = pathlib.Path("/tmp/claude-0/marca"); salida.mkdir(parents=True, exist_ok=True)
    else:
        salida = DESTINO

    for n, cat, _ in sel:
        im = Image.open(FUENTE / idx[n]).convert("RGB")
        im = marca(recorta(im, W, H, SESGO[cat]), cat)
        f = f"{cat}-{n}"
        im.save(salida / f"{f}.jpg", quality=80, optimize=True, progressive=True)
        if not muestra:
            im.save(salida / f"{f}.webp", quality=76, method=6)
    g = 0 if muestra else galerias(RAIZ / "assets")
    print(f"{len(sel)} del portafolio + {g} de galerías -> {salida}"
          f"  (ancho {ANCHO:.0%} · opacidad {OPACIDAD:.0%})")


if __name__ == "__main__":
    main()
