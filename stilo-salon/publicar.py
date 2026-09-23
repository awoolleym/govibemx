#!/usr/bin/env python3
"""
Arma _dist/ con EXACTAMENTE lo que debe ver el público, y nada más.

Cloudflare Pages sube todo lo que encuentra en el directorio de salida.  Sólo
excluye por su cuenta node_modules, .git y .DS_Store; los .py no.  Si se
apunta Pages a la raíz del proyecto, quedan públicos y descargables:

    stilo-salon.com/build.py        -> la lista de precios completa y las
                                       notas internas
    stilo-salon.com/marca_agua.py   -> dónde y con qué opacidad va la marca
                                       de agua, o sea el instructivo para
                                       recortarla
    stilo-salon.com/preview-movil.html

Por eso esto es una lista blanca y no una lista negra: lo que no esté
enumerado aquí no se sube, aunque alguien lo agregue al proyecto mañana.

    python3 build.py && python3 publicar.py
    # y se sube _dist/  (wrangler pages deploy _dist  ·  o se arrastra)
"""
import shutil, sys, pathlib

SRC = pathlib.Path(__file__).parent
DIST = SRC / "_dist"

# Páginas del sitio.  Se comparan contra lo que genera build.py: si no
# coinciden, es que se agregó o quitó una página y hay que actualizar aquí.
PAGINAS = [
    "index.html", "cabello.html", "unas.html", "pestanas-y-cejas.html",
    "precios.html", "portafolio.html", "guia-color-y-alisados.html",
    "guia-unas.html", "guia-extensiones-de-pestanas.html",
    "aviso-de-privacidad.html", "404.html",
    "en/index.html", "en/hair.html", "en/nails.html", "en/lashes-and-brows.html",
    "en/pricing.html", "en/portfolio.html", "en/color-and-smoothing-guide.html",
    "en/nails-guide.html", "en/eyelash-extensions-guide.html", "en/privacy.html",
]
# Configuración que Pages lee (no se sirve como página).
CONFIG = ["_headers", "_redirects", "robots.txt", "sitemap.xml",
          "favicon.ico", "apple-touch-icon.png", "site.webmanifest"]
# Todo assets/ menos lo que no haga falta servir.
ASSETS_EXT = {".css", ".js", ".jpg", ".jpeg", ".webp", ".png", ".svg", ".ico", ".woff2"}

def main():
    faltan = [p for p in PAGINAS + CONFIG if not (SRC / p).exists()]
    if faltan:
        sys.exit("Falta generar: " + ", ".join(faltan) + "\n¿Corriste build.py?")

    # Si build.py generó una página que no está en la lista blanca, avisar en
    # vez de publicarla a ciegas o de dejarla fuera en silencio.
    en_disco = {str(p.relative_to(SRC)) for p in SRC.rglob("*.html")
                if not any(x.startswith(("_preview", "_fotos", "_dist")) for x in p.parts)
                and p.name != "preview-movil.html"}
    huerfanas = sorted(en_disco - set(PAGINAS))
    if huerfanas:
        sys.exit("Hay páginas generadas que no están en PAGINAS de publicar.py:\n  "
                 + "\n  ".join(huerfanas) + "\nAgrégalas ahí (y al sitemap) antes de publicar.")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    n = 0
    for rel in PAGINAS + CONFIG:
        dest = DIST / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC / rel, dest)
        n += 1

    a = 0
    for f in (SRC / "assets").rglob("*"):
        if f.is_file() and f.suffix.lower() in ASSETS_EXT:
            dest = DIST / f.relative_to(SRC)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
            a += 1

    # Red de seguridad: que no se haya colado nada que no deba estar.
    prohibido = [str(f.relative_to(DIST)) for f in DIST.rglob("*")
                 if f.is_file() and (f.suffix in (".py", ".md", ".sh")
                                     or f.name.startswith("preview")
                                     or "__pycache__" in f.parts)]
    if prohibido:
        sys.exit("ABORTADO, se coló algo que no debe ser público:\n  "
                 + "\n  ".join(prohibido))

    peso = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"_dist/ listo — {n} páginas y archivos de config, {a} assets, "
          f"{peso/1e6:.1f} MB")
    print("Subir con:  npx wrangler pages deploy _dist")

if __name__ == "__main__":
    main()
