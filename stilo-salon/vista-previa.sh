#!/usr/bin/env bash
# Sube una versión SIN publicarla y devuelve una dirección para verla.
#
# Por qué no basta con _preview/: esa carpeta se genera a mano y se queda
# vieja en cuanto alguien cambia algo y no la regenera —pasó con los
# precios "desde", que en el preview seguían saliendo cerrados mientras el
# sitio en vivo ya estaba bien—.  Además reescribe los enlaces a rutas
# relativas, así que no prueba lo que de verdad hace Cloudflare: las URLs
# sin .html, las redirecciones viejas, la 404 propia, los tipos de
# contenido ni las cabeceras.
#
# Esto sí: la versión la sirve el mismo Worker con la misma configuración.
# Es producción, sólo que sin promover.  Lo que se vea ahí es exactamente
# lo que va a verse en stilo-salon.com al publicarla.
#
#   CLOUDFLARE_ACCOUNT_ID=... CLOUDFLARE_API_TOKEN=... ./vista-previa.sh
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py > /dev/null
python3 publicar.py
python3 preview.py        # la copia local, para que no se quede vieja

echo
npx wrangler versions upload 2>&1 | tee /tmp/version.txt | grep -E 'Version ID|Preview URL'
echo
echo "Esa dirección NO es el sitio: stilo-salon.com sigue como estaba."
echo "Para publicarla:  ./desplegar.sh"
