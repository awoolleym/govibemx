#!/usr/bin/env python3
"""Genera el favicon y los iconos de la app desde cero.

Por qué una "S" tipográfica y no el logo: el logo es una escritura de trazo
finísimo, y a 16 px —el tamaño real de una pestaña— desaparece.  Peor: la
palabra "Stilo" está escrita de un solo trazo continuo, sin un solo píxel
vacío entre la S y la t, así que ni siquiera se puede recortar la inicial.
Las tijeras sí se pueden aislar por color, pero miden 59x42 px en el
original y estiradas a 512 quedan borrosas.

La salida es la inicial en Cormorant Garamond, que es la tipografía de los
títulos del sitio, blanca sobre el rosa de la marca.  Se lee a 16 px y en
una barra de pestañas llena se distingue de un vistazo, que es lo único
que le pedimos a un favicon.

    python3 iconos.py
"""
import json, pathlib, urllib.request
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


def marca(lado: int) -> Image.Image:
    """La S centrada ópticamente por su caja real, no por la métrica.

    El centrado por métrica deja la letra flotando alta, porque la caja de
    la fuente reserva sitio para acentos y descendentes que la S no usa.
    """
    im = Image.new("RGBA", (lado, lado), ROSA)
    d = ImageDraw.Draw(im)
    ruta = str(fuente_ttf())
    pt = lado
    while pt > 4:
        f = ImageFont.truetype(ruta, pt)
        x0, y0, x1, y1 = d.textbbox((0, 0), LETRA, font=f)
        if (y1 - y0) <= lado * OCUPA:
            break
        pt -= 1
    f = ImageFont.truetype(ruta, pt)
    x0, y0, x1, y1 = d.textbbox((0, 0), LETRA, font=f)
    d.text(((lado - (x1 - x0)) / 2 - x0, (lado - (y1 - y0)) / 2 - y0),
           LETRA, font=f, fill=BLANCO)
    return im


def main():
    assets = RAIZ / "assets"
    # El .ico lleva los tres tamaños dentro: el navegador escoge. Cada uno se
    # dibuja a su tamaño en vez de reescalar el grande, así el trazo no se
    # adelgaza hasta desaparecer en el de 16.
    caras = [marca(n) for n in (16, 32, 48)]
    caras[2].save(RAIZ / "favicon.ico", format="ICO",
                  sizes=[(16, 16), (32, 32), (48, 48)])

    # iOS no admite transparencia ni redondea por su cuenta en todas las
    # versiones; el fondo sólido evita el cuadro negro.
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

    print("iconos listos: favicon.ico · apple-touch-icon.png · "
          "assets/icon-192.png · assets/icon-512.png · site.webmanifest")


if __name__ == "__main__":
    main()
