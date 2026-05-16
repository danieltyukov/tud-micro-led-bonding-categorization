#!/usr/bin/env bash
# Preview-and-iterate loop. Run this WITHOUT generating fab outputs.
#
# Usage:  bash new-pcb/tools/preview.sh
#
# Output:
#   new-pcb/fab/preview/board_top.png      — top 3D render
#   new-pcb/fab/preview/board_bottom.png   — bottom 3D render
#   new-pcb/fab/preview/silk_top.svg       — top silk + edge cuts as SVG
#   new-pcb/fab/preview/silk_bottom.svg    — bottom silk + edge cuts as SVG
#   stdout: DRC summary

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_DIR"

PCB="new-pcb/tud-microled-v2.kicad_pcb"
PREVIEW_DIR="new-pcb/fab/preview"
mkdir -p "$PREVIEW_DIR"

# Pass --no-regen to skip the generator (keeps freerouted traces)
if [ "${1:-}" != "--no-regen" ]; then
    echo "[1/4] Regenerating PCB from generate_pcb_text.py …"
    python3 new-pcb/tools/generate_pcb_text.py | tail -5
    echo "[1b]  Refilling zones (B.Cu GND pour)…"
    ~/tools/KiCAD-MCP-Server/.venv/bin/python -c "
import pcbnew
b = pcbnew.LoadBoard('$PCB')
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard('$PCB', b)
print('zones refilled')
" 2>&1 | grep -v "memory leak\|destructor"
else
    echo "[1/4] Skipping regeneration (--no-regen)"
fi

echo ""
echo "[2/4] Running DRC …"
DRC_TXT="$(mktemp)"
kicad-cli pcb drc -o "$DRC_TXT" --format report "$PCB" 2>&1 | tail -2

# Extract counts
VIOL=$(grep -oP "Found \K[0-9]+(?= DRC)" "$DRC_TXT" || echo "?")
UNCONN=$(grep -oP "Found \K[0-9]+(?= unconnected)" "$DRC_TXT" || echo "?")
echo "  → $VIOL DRC violations, $UNCONN unconnected pads"

echo ""
echo "[3/4] Rendering 3D previews (top + bottom) …"
kicad-cli pcb render --width 1600 --height 1280 --side top    --quality high --background opaque -o "$PREVIEW_DIR/board_top.png"    "$PCB" 2>&1 | tail -1
kicad-cli pcb render --width 1600 --height 1280 --side bottom --quality high --background opaque -o "$PREVIEW_DIR/board_bottom.png" "$PCB" 2>&1 | tail -1

echo ""
echo "[4/4] Plotting silkscreen + edge cuts SVG …"
TMP_SVG_DIR="$(mktemp -d)"
kicad-cli pcb export svg --layers "F.SilkS,Edge.Cuts" --mode-multi --black-and-white -o "$TMP_SVG_DIR" "$PCB" 2>&1 | tail -1
kicad-cli pcb export svg --layers "B.SilkS,Edge.Cuts" --mode-multi --black-and-white -o "$TMP_SVG_DIR" "$PCB" 2>&1 | tail -1
cp "$TMP_SVG_DIR"/*F_Silkscreen* "$PREVIEW_DIR/silk_top.svg" 2>/dev/null || true
cp "$TMP_SVG_DIR"/*B_Silkscreen* "$PREVIEW_DIR/silk_bottom.svg" 2>/dev/null || true

echo ""
echo "Preview ready in $PREVIEW_DIR/"
ls -la "$PREVIEW_DIR/"
