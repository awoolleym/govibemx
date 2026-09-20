#!/usr/bin/env python3
"""
Genera una copia navegable del sitio con rutas RELATIVAS, para previsualizarlo
fuera de stilo-salon.com. El sitio real (rutas absolutas) no se toca.
"""
import re, shutil, pathlib

SRC = pathlib.Path(__file__).parent
OUT = SRC / "_preview"

def rel(from_file: pathlib.Path, target: str) -> str:
    """'/en/hair.html' visto desde 'en/index.html' -> 'hair.html'"""
    depth = len(from_file.relative_to(OUT).parts) - 1
    t = target.lstrip("/")
    if t == "" or t.endswith("/"):
        t = (t + "index.html")
    prefix = "../" * depth
    return (prefix + t) if (prefix + t) else "index.html"

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    # copiar html + assets
    for f in SRC.rglob("*"):
        if OUT in f.parents or f == OUT or "_preview" in f.parts:
            continue
        if f.suffix in (".html", ".css") and f.is_file():
            dest = OUT / f.relative_to(SRC)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)

    n = 0
    for f in OUT.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        # href/src internos que empiezan con "/" (no "//" ni protocolo)
        def fix(m):
            attr, url = m.group(1), m.group(2)
            if url.startswith("//"):
                return m.group(0)
            frag = ""
            if "#" in url:
                url, frag = url.split("#", 1)
                frag = "#" + frag
            if url == "" and frag:            # ancla pura de la misma página
                return f'{attr}="{frag}"'
            return f'{attr}="{rel(f, url)}{frag}"'
        t2 = re.sub(r'\b(href|src)="(/[^"]*)"', fix, t)
        # enlaces absolutos al dominio real (toggle de idioma, footer)
        def fix_abs(m):
            attr, url = m.group(1), m.group(2)
            path = url[len("https://stilo-salon.com"):] or "/"
            frag = ""
            if "#" in path:
                path, frag = path.split("#", 1); frag = "#" + frag
            return f'{attr}="{rel(f, path)}{frag}"'
        t2 = re.sub(r'\b(href|src)="(https://stilo-salon\.com[^"]*)"', fix_abs, t2)
        # canonical / hreflang / og:url apuntan al dominio real: se dejan,
        # pero se quitan del preview para no confundir al navegador
        t2 = re.sub(r'\s*<link rel="canonical"[^>]*>\n?', "", t2)
        t2 = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*"[^>]*>\n?', "", t2)
        if t2 != t:
            f.write_text(t2, encoding="utf-8"); n += 1
    print(f"preview listo: {n} páginas reescritas en {OUT.relative_to(SRC)}/")

if __name__ == "__main__":
    main()
