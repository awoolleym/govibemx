#!/usr/bin/env python3
"""Genera el favicon y los iconos de la app desde cero.

Por qué no se usa el logo tal cual: la palabra "Stilo" está escrita de un
solo trazo continuo —no hay una sola columna de píxeles vacía entre la S y
la t, está comprobado—, así que la inicial no se puede recortar.  Las
tijeras del logo sí se aíslan por color, pero miden 59x42 px y estiradas a
512 quedan borrosas.  Por eso la S es tipográfica (Cormorant Garamond, la
de los títulos del sitio) y las tijeras van dibujadas en vector aquí.

Por qué hay dos dibujos y no uno: la S con las tijeras se lee bien hasta 48
px, y de ahí para abajo las dos cosas juntas se convierten en una mancha.
La pestaña del navegador usa 16 o 32.  Así que el .ico lleva arte distinto
en cada tamaño —para eso existe el formato—: la marca completa en 48, y la
S sola en 32 y 16, donde es lo único que se distingue.  Los iconos grandes
(pantalla de inicio, PWA) llevan siempre la marca completa.

    python3 iconos.py
"""
import json, math, pathlib, urllib.request
from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).parent
FUENTE_CACHE = RAIZ / "_fotos3" / "cormorant-garamond.ttf"
# La misma familia que carga el sitio para los títulos.
FUENTE_URL = ("https://fonts.gstatic.com/s/cormorantgaramond/v21/"
              "co3umX5slCNuHLi8bLeY9MK7whWMhyjypVO7abI26QOD_v86GnM.ttf")

ROSA   = (192, 97, 132, 255)   # --accent
BLANCO = (255, 255, 255, 255)
LETRA  = "S"
OCUPA  = 0.66                  # alto de la letra como fracción del lado


def fuente_ttf() -> pathlib.Path:
    if not FUENTE_CACHE.exists():
        FUENTE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(FUENTE_URL, timeout=30) as r:
            FUENTE_CACHE.write_bytes(r.read())
    return FUENTE_CACHE


def tijeras(lado: int, color) -> Image.Image:
    """Tijeras de peluquería, dibujadas al tamaño que se pidan.

    Se trazan a cuatro veces el tamaño final y se bajan con LANCZOS: así el
    filo queda limpio sin depender del antialias del dibujante.  Las hojas
    son triángulos que nacen anchos en el tornillo y mueren en punta, que es
    lo que las hace legibles en chico; con grosor constante se leen como dos
    palos.
    """
    S = lado * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    px, py = S * 0.46, S * 0.50                      # el tornillo
    pt = lambda a, r: (px + r * math.cos(math.radians(a)),
                       py + r * math.sin(math.radians(a)))
    for ang in (-160, -128):                          # las dos hojas
        d.polygon([pt(ang + 90, S * 0.052), pt(ang, S * 0.46),
                   pt(ang - 90, S * 0.052)], fill=color)
    raro, g = S * 0.105, max(2, int(S * 0.038))
    for ang in (26, 66):                              # brazos y aros
        c = pt(ang, S * 0.315)
        d.line([(px, py), c], fill=color, width=g)
        d.ellipse([c[0] - raro, c[1] - raro, c[0] + raro, c[1] + raro],
                  outline=color, width=g)
    d.ellipse([px - S * 0.035, py - S * 0.035,
               px + S * 0.035, py + S * 0.035], fill=color)
    return im.resize((lado, lado), Image.LANCZOS)


def _ese(im: Image.Image, ocupa: float, dx=0.0, dy=0.0) -> Image.Image:
    """La S centrada por su caja real, no por la métrica de la fuente.

    La métrica reserva sitio para acentos y descendentes que la S no usa, así
    que centrar por ella deja la letra flotando alta.
    """
    d = ImageDraw.Draw(im)
    L, ruta, pt_ = im.width, str(fuente_ttf()), im.width
    while pt_ > 4:
        f = ImageFont.truetype(ruta, pt_)
        x0, y0, x1, y1 = d.textbbox((0, 0), LETRA, font=f)
        if (y1 - y0) <= L * ocupa:
            break
        pt_ -= 1
    f = ImageFont.truetype(ruta, pt_)
    x0, y0, x1, y1 = d.textbbox((0, 0), LETRA, font=f)
    d.text(((L - (x1 - x0)) / 2 - x0 + L * dx,
            (L - (y1 - y0)) / 2 - y0 + L * dy), LETRA, font=f, fill=BLANCO)
    return im


def marca(lado: int) -> Image.Image:
    """La marca completa: la S con las tijeras colgando de su cola.

    Es la misma idea del logo, donde el rasgo final termina en las tijeras.
    """
    im = _ese(Image.new("RGBA", (lado, lado), ROSA), 0.60, -0.09, -0.06)
    t = tijeras(int(lado * 0.46), BLANCO)
    im.paste(t, (int(lado * 0.52), int(lado * 0.50)), t)
    return im


def inicial(lado: int) -> Image.Image:
    """Solo la S, para los tamaños donde las tijeras ya no se distinguen."""
    return _ese(Image.new("RGBA", (lado, lado), ROSA), 0.66)


def main():
    assets = RAIZ / "assets"
    # 48 lleva la marca completa; 32 y 16 solo la inicial, porque ahí las
    # tijeras ya no se ven y solo ensucian la letra.
    caras = [inicial(16), inicial(32), marca(48)]
    caras[2].save(RAIZ / "favicon.ico", format="ICO",
                  sizes=[(16, 16), (32, 32), (48, 48)],
                  append_images=caras[:2])

    # iOS no admite transparencia; el fondo sólido evita el cuadro negro.
    marca(180).convert("RGB").save(RAIZ / "apple-touch-icon.png")
    for n in (192, 512):
        marca(n).convert("RGB").save(assets / f"icon-{n}.png")

    (RAIZ / "site.webmanifest").write_text(json.dumps({
        "name": "Stilo Salón",
        "short_name": "Stilo",
        "icons": [
            {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": "#c06184",
        "background_color": "#fdfbfc",
        "display": "standalone",
        "start_url": "/",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("iconos listos: favicon.ico (S sola en 16 y 32, marca completa en 48) · "
          "apple-touch-icon.png · assets/icon-192.png · assets/icon-512.png · "
          "site.webmanifest")


if __name__ == "__main__":
    main()
