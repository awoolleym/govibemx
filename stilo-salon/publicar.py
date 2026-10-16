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
import shutil, sys, pathlib, zipfile

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
CONFIG = ["_headers", "_redirects", "robots.txt", "sitemap.xml", "llms.txt",
          "llms-full.txt", "sitemap.md", "AGENTS.md",
          "favicon.ico", "apple-touch-icon.png", "site.webmanifest",
          ".well-known/agents.json", ".well-known/mcp.json",
          ".well-known/agents.md",
          "agents.json", "mcp.json",
          # Verificación de propiedad de Google Search Console.  Es un .html
          # pero no es una página: no lleva nada dentro salvo su propio
          # nombre, no entra al sitemap y nadie lo enlaza.  Por eso va aquí
          # y no en PAGINAS, y por eso se excluye de la comprobación de
          # páginas huérfanas de abajo.
          "googlecd804256c478278c.html"]
# El espejo en Markdown de cada página: mismo nombre, otra extensión. Se
# deriva de PAGINAS para que no se pueda agregar una página y olvidar el suyo.
ESPEJOS = [p[:-5] + ".md" for p in PAGINAS if p != "404.html"]
# .well-known empieza con punto: al comprimir hay que excluir sólo los
# archivos ocultos sueltos, no esa carpeta.  Con "zip -x '.*'" se perdía
# entera y nadie se enteraba hasta ver el 404.
# Todo assets/ menos lo que no haga falta servir.
ASSETS_EXT = {".css", ".js", ".jpg", ".jpeg", ".webp", ".png", ".svg", ".ico", ".woff2"}

def main():
    faltan = [p for p in PAGINAS + CONFIG + ESPEJOS if not (SRC / p).exists()]
    if faltan:
        sys.exit("Falta generar: " + ", ".join(faltan) + "\n¿Corriste build.py?")

    # Si build.py generó una página que no está en la lista blanca, avisar en
    # vez de publicarla a ciegas o de dejarla fuera en silencio.
    en_disco = {str(p.relative_to(SRC)) for p in SRC.rglob("*.html")
                if not any(x.startswith(("_preview", "_fotos", "_dist")) for x in p.parts)
                and p.name not in ("preview-movil.html",
                                   "googlecd804256c478278c.html")}
    huerfanas = sorted(en_disco - set(PAGINAS))
    if huerfanas:
        sys.exit("Hay páginas generadas que no están en PAGINAS de publicar.py:\n  "
                 + "\n  ".join(huerfanas) + "\nAgrégalas ahí (y al sitemap) antes de publicar.")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    n = 0
    for rel in PAGINAS + CONFIG + ESPEJOS:
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
                 if f.is_file() and (f.suffix in (".py", ".sh")
                                     or f.name.startswith("preview")
                                     or "__pycache__" in f.parts)]
    if prohibido:
        sys.exit("ABORTADO, se coló algo que no debe ser público:\n  "
                 + "\n  ".join(prohibido))

    huella = sellar(DIST)

    peso = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    # El zip se arma aquí y no a mano: escrito a mano se cuela
    # "zip -x '.*'", que excluye todo lo que empieza con punto y se lleva la
    # carpeta .well-known entera sin decir nada.  Aquí se listan los archivos
    # explícitamente, así que lo que está en _dist es lo que va en el zip.
    zipf = SRC / "_dist.zip"
    if zipf.exists():
        zipf.unlink()
    archivos = sorted(f for f in DIST.rglob("*") if f.is_file())
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in archivos:
            z.write(f, f.relative_to(DIST))
    # Comprobación: lo que se comprimió tiene que ser exactamente lo que hay.
    with zipfile.ZipFile(zipf) as z:
        dentro = {i.filename for i in z.infolist() if not i.is_dir()}
    esperado = {str(f.relative_to(DIST)) for f in archivos}
    if dentro != esperado:
        sys.exit(f"El zip no coincide con _dist. Falta: {sorted(esperado-dentro)[:5]}")

    print(f"_dist/ listo — {n} páginas y archivos de config, {a} assets, "
          f"{peso/1e6:.1f} MB")
    print(f"  {huella} assets renombrados con su huella (caché de un año sin riesgo)")
    print(f"_dist.zip — {len(dentro)} archivos, {zipf.stat().st_size/1e6:.1f} MB")
    print("Subir el zip al Worker, o:  npx wrangler pages deploy _dist")


# Extensiones de archivos de texto donde puede haber una ruta a assets/.
TEXTO = {".html", ".css", ".xml", ".txt", ".json", ".md", ".webmanifest"}


def sellar(dist):
    """Renombra cada archivo de assets/ con la huella de su contenido.

    Por qué hace falta: _headers sirve /assets/* con
    "max-age=31536000, immutable".  Un año, e "immutable" le dice al
    navegador que ni siquiera pregunte si cambió.  Eso está bien para un
    archivo cuyo nombre cambia cuando cambia su contenido —como
    app.<hash>.js— y está MAL para todo lo demás: con nombre fijo, quien
    ya visitó el sitio se queda con el style.css y las fotos viejas hasta
    un año, y lo único que lo arregla es un Shift+F5 que nadie hace.

    Pasó de verdad: el salón reportó que los cambios se veían con
    Shift+F5 y se deshacían al recargar normal.

    Se hace aquí y no en build.py para que el preview siga teniendo
    nombres legibles y para que la huella salga del archivo tal como se
    publica.  Dos pasadas porque el CSS referencia imágenes: primero se
    sellan las imágenes y se reescriben las referencias dentro del CSS,
    y sólo entonces se sella el CSS, que ya no va a volver a cambiar.
    """
    import hashlib, re

    def hashear(rutas):
        mapa = {}
        for f in sorted(rutas):
            rel = f.relative_to(dist).as_posix()
            # app.<hash>.js ya trae su huella puesta por build.py.
            if re.search(r"\.[0-9a-f]{8}\.[a-z0-9]+$", rel):
                continue
            h = hashlib.sha1(f.read_bytes()).hexdigest()[:8]
            nuevo = f"{f.stem}.{h}{f.suffix}"
            f.rename(f.with_name(nuevo))
            mapa["/" + rel] = "/" + (f.parent / nuevo).relative_to(dist).as_posix()
        return mapa

    def reescribir(mapa):
        if not mapa:
            return
        # De la ruta más larga a la más corta: si una fuera prefijo de
        # otra, reemplazar primero la corta partiría la larga.
        pares = sorted(mapa.items(), key=lambda kv: -len(kv[0]))
        for f in dist.rglob("*"):
            if not f.is_file() or (f.suffix not in TEXTO and f.name not in ("_headers", "_redirects")):
                continue
            try:
                txt = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            orig = txt
            for viejo, nuevo in pares:
                if viejo in txt:
                    txt = txt.replace(viejo, nuevo)
            if txt != orig:
                f.write_text(txt, encoding="utf-8")

    def reescribir_css_relativo(mapa):
        """El CSS vive dentro de assets/ y se refiere a sus vecinos por el
        nombre pelado: url("flor-marca.png"), no "/assets/flor-marca.png".
        La reescritura de arriba no los ve, así que al renombrar los
        archivos esas tres referencias —la tipografía y las dos flores—
        quedaban rotas.  Pasó: la primera versión de esto las rompió y lo
        cazó la revisión."""
        vecinos = {viejo.rsplit("/", 1)[-1]: nuevo.rsplit("/", 1)[-1]
                   for viejo, nuevo in mapa.items()
                   if viejo.count("/") == 2}          # /assets/x.png
        for f in assets.rglob("*.css"):
            txt = orig = f.read_text(encoding="utf-8")
            for v, n in sorted(vecinos.items(), key=lambda kv: -len(kv[0])):
                for comilla in ('"', "'", ""):
                    txt = txt.replace(f"url({comilla}{v}{comilla})",
                                      f"url({comilla}{n}{comilla})")
            if txt != orig:
                f.write_text(txt, encoding="utf-8")

    assets = dist / "assets"
    imagenes = [f for f in assets.rglob("*") if f.is_file() and f.suffix != ".css"]
    mapa = hashear(imagenes)
    reescribir(mapa)
    reescribir_css_relativo(mapa)
    hojas = [f for f in assets.rglob("*.css") if f.is_file()]
    mapa2 = hashear(hojas)
    reescribir(mapa2)
    return len(mapa) + len(mapa2)

if __name__ == "__main__":
    main()
