#!/usr/bin/env python3
"""Prepara las fotos del salón —el local, no los trabajos— para el sitio.

Son otra cosa que las del portafolio y por eso no pasan por marca_agua.py:
nadie se roba la foto de una fachada, y una marca encima del toldo sólo
estorbaría.  Aquí sólo se recortan al tamaño que se sirve y se guardan en
los dos formatos que pide img() en build.py: WebP primero, JPEG de respaldo.

Las cuatro vienen de la cámara a 4000x3000 y entre 0.8 y 8.4 MB.  Servirlas
así tardaría más que toda la portada junta, y nadie las ve a ese tamaño: el
hueco más grande del sitio mide 1200 px de ancho.

Los originales viven en _fotos-salon/, fuera de git como el resto de los
_fotos*.  El script siempre parte de ahí y nunca de assets/, para que
correrlo dos veces no vuelva a comprimir lo ya comprimido.

    python3 fotos_salon.py
"""
import pathlib
from PIL import Image, ImageOps

RAIZ    = pathlib.Path(__file__).parent
FUENTE  = RAIZ / "_fotos-salon"
DESTINO = RAIZ / "assets"

# Las cuatro vienen 4:3 de la cámara, pero el sitio las muestra en 3:2:
# acompañan al texto y no lo interrumpen, y lo que sobra en las cuatro es
# techo y piso.  Se recortan aquí en vez de dejar que el navegador recorte
# con object-fit, para no mandar píxeles que nadie va a ver.  1200 de ancho
# es el doble del hueco más grande (560), que es lo que piden las pantallas
# de alta densidad.
ANCHO, ALTO = 1200, 800

# El prefijo "local-" las separa de las fotos de trabajos en assets/.
#
# El segundo número es de dónde sale el recorte vertical: 0 conserva el
# borde de arriba, 1 el de abajo, 0.5 reparte.  Casi todas se reparten,
# pero en las estaciones de corte lo bueno está arriba —los espejos de
# arco— y lo que sobra abajo es piso y el carrito de brochas, así que ahí
# el recorte se corre hacia arriba.
FOTOS = {
    "fachada":         0.5,
    "estaciones":      0.15,
    "cabina-pestanas": 0.5,
    "pedicure":        0.5,
}


def main():
    if not FUENTE.exists():
        raise SystemExit(f"No está {FUENTE.name}/. Los originales no entran a "
                         "git: cópialos ahí antes de correr esto.")
    for nombre, centro_y in FOTOS.items():
        origen = FUENTE / f"{nombre}.jpg"
        if not origen.exists():
            raise SystemExit(f"Falta {origen}")
        im = Image.open(origen)
        # exif_transpose respeta la rotación que grabó el teléfono; sin esto
        # una foto tomada de lado sale acostada y nadie entiende por qué.
        im = ImageOps.exif_transpose(im).convert("RGB")
        # ImageOps.fit recorta centrado a la proporción pedida en vez de
        # deformar.  Como las cuatro ya son 4:3, no recorta nada.
        im = ImageOps.fit(im, (ANCHO, ALTO), Image.LANCZOS,
                          centering=(0.5, centro_y))
        base = DESTINO / f"local-{nombre}"
        im.save(base.with_suffix(".jpg"), quality=82, optimize=True, progressive=True)
        im.save(base.with_suffix(".webp"), quality=80, method=6)
        kb = lambda p: p.stat().st_size / 1024
        print(f"  local-{nombre:16s} {ANCHO}x{ALTO}  "
              f"jpg {kb(base.with_suffix('.jpg')):5.0f} KB  "
              f"webp {kb(base.with_suffix('.webp')):5.0f} KB  "
              f"(original {kb(origen)/1024:.1f} MB)")


if __name__ == "__main__":
    main()
