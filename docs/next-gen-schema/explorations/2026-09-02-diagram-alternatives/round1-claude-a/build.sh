#!/bin/sh
# Regenerate the mockups from the graph files and rasterize them for inspection.
set -e
D=$(cd "$(dirname "$0")" && pwd)
python3 "$D/render_nested.py" "$D/views/pleural-effusion.json" > "$D/alt1-pleural-effusion.svg"
python3 "$D/render_nested.py" "$D/views/pyelonephritis.json"    > "$D/alt1-pyelonephritis.svg"
python3 "$D/render_matrix.py" "$D/views/pleural-effusion.json" > "$D/alt2-pleural-effusion.svg"
python3 "$D/render_matrix.py" "$D/views/pyelonephritis.json"    > "$D/alt2-pyelonephritis.svg"
for f in "$D"/alt*.svg; do python3 -c "import xml.dom.minidom,sys; xml.dom.minidom.parse(sys.argv[1])" "$f"; done
if [ -n "$PNG" ]; then
  for f in "$D"/alt*.svg; do uv run --quiet --with cairosvg python -c "import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=1800)" "$f" "$PNG/$(basename "$f" .svg).png"; done
fi
