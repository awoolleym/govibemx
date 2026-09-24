#!/usr/bin/env bash
# Sube _dist/ al Worker y comprueba que de verdad quedó arriba.
#
# El panel de Cloudflare puede dejar el despliegue anterior en pie sin decir
# nada si la carga se corta.  Esto no: wrangler falla con error, y además
# después se piden seis archivos al dominio real.  Si alguno no está, el
# script sale con error en vez de dar por bueno el despliegue.
#
#   CLOUDFLARE_ACCOUNT_ID=... CLOUDFLARE_API_TOKEN=... ./desplegar.sh
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py > /dev/null
python3 publicar.py
npx wrangler deploy

echo
echo "Comprobando el sitio en vivo…"
fallos=0
for ruta in / /precios /AGENTS.md /precios.md /llms-full.txt /sitemap.md /.well-known/agents.json; do
  codigo=$(curl -s -o /dev/null -w '%{http_code}' "https://stilo-salon.com${ruta}")
  [ "$codigo" = "200" ] || { echo "  ✗ ${ruta} -> ${codigo}"; fallos=$((fallos+1)); continue; }
  echo "  ✓ ${ruta}"
done
# Una marca que sólo existe en la versión nueva: si falta, lo que se sirve
# es un despliegue viejo aunque todo respondiera 200.
curl -s https://stilo-salon.com/ | grep -q 'assets/app\.' \
  || { echo "  ✗ la portada no enlaza assets/app.<hash>.js: está sirviendo una versión vieja"; fallos=$((fallos+1)); }

[ "$fallos" = "0" ] && echo "Listo: el sitio en vivo es esta versión." \
                    || { echo "$fallos comprobaciones fallaron."; exit 1; }
