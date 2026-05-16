#!/usr/bin/env python3
"""
Generate tud-microled-v2.kicad_pcb as raw KiCad 9 S-expression text.

This bypasses the pcbnew Python SWIG bindings, which have proven flaky
during this build (Drawings()/Tracks() iterators returning SwigPyObject,
fp.Reference() returning untyped proxies, segfaults inside SetPosition
after a wipe). The S-expression format for `.kicad_pcb` is stable and
fully documented at https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/.

Run:
    ~/tools/KiCAD-MCP-Server/.venv/bin/python new-pcb/tools/generate_pcb_text.py
or any plain Python 3 — no pcbnew needed for generation.
"""

from __future__ import annotations

import math
import os
import uuid as _uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]
BOARD_PATH = REPO / "new-pcb" / "tud-microled-v2.kicad_pcb"
PRO_PATH = REPO / "new-pcb" / "tud-microled-v2.kicad_pro"

# ---------------------------------------------------------------------------
# Geometry (all coordinates in mm)
# ---------------------------------------------------------------------------

BOARD_W = 100.0
BOARD_H = 100.0
EDGE_MARGIN = 2.5

# DoE bond-pad array
DOE_ROWS = 6
DOE_COLS = 6
DOE_PITCH = 3.5
DOE_ORIGIN_Y = 21.0                        # top row centre (was 17 on smaller board)

# Probe pad geometry
PROBE_PAD = 1.27
DOE_NORTH_PROBE_Y = [13.0, 15.0, 17.0]       # unused in v3 (DoE probed directly)
DOE_SOUTH_PROBE_Y = [42.0, 44.0, 46.0]       # unused in v3

# Test-structure row Y positions (re-spaced for BOARD_H = 100mm with frames)
ROW_TITLE_Y       = 3.0
ROW_NORTH_HEADER  = 13.5
ROW_TLM           = 51.5
ROW_VDP           = 62.0
ROW_DAISY         = 73.0
ROW_DAISY_PROBES  = 76.5
ROW_LED           = 82.5
ROW_LED_PROBES    = 85.5
ROW_SOUTH_HEADER  = 89.0
ROW_RULER_Y       = 93.5

# Bond pad geometry
BOND_PAD = 1.0
MINI_PAD = 0.5
# Mini-pad centre-to-centre offset from main pad centre. Set to ensure the
# mini overlaps the main pad by ~0.25 mm (so they're electrically connected
# without needing a separate trace). The Berthier 2015 paper's "100 µm
# outside the main edge" geometry would put MINI_PAD_OFFSET = 0.85 with a
# separate under-mask jumper — deferred to v2.1.
MINI_PAD_OFFSET = 0.5

# Daisy chain
DC_PITCH = 1.8  # mm. With 1.0 mm pads → 0.8 mm gap → safe solder mask web
                # while still < 2.0 mm so a 1×1 mm die can bridge.

# Traces
TRACE_W = 0.20

# ---------------------------------------------------------------------------
# S-expression building helpers
# ---------------------------------------------------------------------------

def uuid() -> str:
    return str(_uuid.uuid4())


def f(x: float) -> str:
    """Format float for KiCad: trim trailing zeros, keep up to 6 decimals."""
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return s if s and s != "-0" else "0"


def at(x: float, y: float, rot: float | None = None) -> str:
    if rot is None or rot == 0:
        return f"(at {f(x)} {f(y)})"
    return f"(at {f(x)} {f(y)} {f(rot)})"


@dataclass
class Net:
    code: int
    name: str

    def sexp(self) -> str:
        """Full net definition (only at top of .kicad_pcb)."""
        return f'(net {self.code} "{self.name}")'

    def ref(self) -> str:
        """Net reference (in pads, segments, vias, zones)."""
        return f'(net {self.code})'


@dataclass
class NetManager:
    _by_name: dict = field(default_factory=dict)
    _next: int = 1

    def get(self, name: str) -> Net:
        if name in self._by_name:
            return self._by_name[name]
        n = Net(self._next, name)
        self._next += 1
        self._by_name[name] = n
        return n

    def all_nets(self) -> list[Net]:
        return [Net(0, "")] + list(self._by_name.values())


# ---------------------------------------------------------------------------
# Footprint / pad builders — output S-expression strings
# ---------------------------------------------------------------------------

def emit_pad(
    number: str,
    shape: str,                # "rect" | "circle" | "roundrect"
    local_x: float,
    local_y: float,
    w: float,
    h: float,
    net: Net | None = None,
    layers: list[str] | None = None,
    rotation: float = 0,
    roundrect_ratio: float | None = None,
    pad_type: str = "smd",     # "smd" | "thru_hole"
    drill: float | None = None,
    solder_mask_margin: float | None = None,
    local_clearance: float | None = None,  # mm; overrides board rule
) -> str:
    if layers is None:
        if pad_type == "thru_hole":
            layers = ["*.Cu", "*.Mask"]
        else:
            layers = ["F.Cu", "F.Paste", "F.Mask"]
    layers_str = " ".join(f'"{L}"' for L in layers)
    extra = []
    if shape == "roundrect" and roundrect_ratio is not None:
        extra.append(f"(roundrect_rratio {f(roundrect_ratio)})")
    if drill is not None:
        extra.append(f"(drill {f(drill)})")
    if solder_mask_margin is not None:
        extra.append(f"(solder_mask_margin {f(solder_mask_margin)})")
    if local_clearance is not None:
        extra.append(f"(clearance {f(local_clearance)})")
        extra.append(f"(solder_mask_margin -{f(solder_mask_margin or 0)})")
    # Pads use the full (net N "name") form; segments use the (net N) reference form.
    net_str = net.sexp() if net is not None else ""
    return (
        f'(pad "{number}" {pad_type} {shape} {at(local_x, local_y, rotation)} '
        f'(size {f(w)} {f(h)}) (layers {layers_str}) {" ".join(extra)} '
        f'{net_str} (uuid "{uuid()}"))'
    )


def emit_footprint(
    name: str,
    x: float,
    y: float,
    pads: list[str],
    rotation: float = 0,
    layer: str = "F.Cu",
    library_id: str = "",
    fp_text_layer: str = "F.SilkS",
    is_smd: bool = True,
) -> str:
    attr = "smd" if is_smd else "through_hole"
    rot_str = f" {f(rotation)}" if rotation else ""
    pads_str = "\n    ".join(pads)
    return (
        f'(footprint "{library_id}"\n'
        f'  (layer "{layer}")\n'
        f'  (uuid "{uuid()}")\n'
        f'  (at {f(x)} {f(y)}{rot_str})\n'
        f'  (attr {attr})\n'
        f'  (property "Reference" "{name}" (at 0 -2 0) (layer "F.Fab") (hide yes) '
        f'(uuid "{uuid()}") (effects (font (size 1 1) (thickness 0.15))))\n'
        f'  (property "Value" "{name}" (at 0 2 0) (layer "F.Fab") (hide yes) '
        f'(uuid "{uuid()}") (effects (font (size 1 1) (thickness 0.15))))\n'
        f'  {pads_str}\n'
        f')\n'
    )


def emit_silk_text(
    text: str,
    x: float,
    y: float,
    size: float = 1.0,
    rotation: float = 0,
    justify: str = "left",     # "left" | "center" | "right"
    layer: str = "F.SilkS",
    bold: bool = False,
) -> str:
    """Emit silkscreen text. KiCad's gr_text uses `(justify left)` or
    `(justify right)` for left/right anchored text; CENTER is the default
    and is expressed by omitting the (justify) clause entirely.
    For B.SilkS layers, `mirror` is added so text reads correctly when
    viewing the board from the back. Double-quotes and backslashes are
    escaped because KiCad's S-expression parser does not accept them raw."""
    size = max(0.8, size)
    thickness = max(0.15, size * (0.20 if bold else 0.15))
    rot_str = f" {f(rotation)}" if rotation else ""
    is_back = layer.startswith("B.")
    if justify == "center":
        justify_tokens = "mirror" if is_back else ""
    else:
        justify_tokens = justify + (" mirror" if is_back else "")
    effects_inner = f"(font (size {f(size)} {f(size)}) (thickness {f(thickness)}))"
    if justify_tokens:
        effects_inner += f" (justify {justify_tokens})"
    # Escape backslashes first, then quotes
    text_escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return (
        f'(gr_text "{text_escaped}"\n'
        f'  (at {f(x)} {f(y)}{rot_str})\n'
        f'  (layer "{layer}")\n'
        f'  (uuid "{uuid()}")\n'
        f'  (effects {effects_inner})\n'
        f')\n'
    )


def emit_silk_line(x1: float, y1: float, x2: float, y2: float, layer: str = "F.SilkS", width: float = 0.15) -> str:
    return (
        f'(gr_line (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
        f'(stroke (width {f(width)}) (type default)) (layer "{layer}") (uuid "{uuid()}"))\n'
    )


def emit_silk_rect(x1: float, y1: float, x2: float, y2: float, layer: str = "F.SilkS", width: float = 0.15) -> str:
    """Four-line rectangle on silkscreen (open border, not filled)."""
    return (
        emit_silk_line(x1, y1, x2, y1, layer=layer, width=width) +
        emit_silk_line(x2, y1, x2, y2, layer=layer, width=width) +
        emit_silk_line(x2, y2, x1, y2, layer=layer, width=width) +
        emit_silk_line(x1, y2, x1, y1, layer=layer, width=width)
    )


def emit_silk_circle(cx: float, cy: float, radius: float, layer: str = "F.SilkS", width: float = 0.15, fill: bool = False) -> str:
    fill_str = "(fill solid)" if fill else "(fill no)"
    return (
        f'(gr_circle (center {f(cx)} {f(cy)}) (end {f(cx + radius)} {f(cy)}) '
        f'(stroke (width {f(width)}) (type default)) {fill_str} (layer "{layer}") (uuid "{uuid()}"))\n'
    )


def emit_tudelft_mark(cx: float, cy: float, scale: float = 1.0, layer: str = "F.SilkS") -> str:
    """A compact stylized 'TU' flame mark + 'TUDelft' text — the same
    convention as the v1 board's silkscreen 'TUDelft' label.
    Total bounding box: ~ 18*scale × 4*scale mm. (cx, cy) = centre."""
    out = ""
    # Stylized flame on the left: 3 ascending lines suggesting the TU Delft flame
    fx = cx - 7.5 * scale
    fy_top = cy - 1.5 * scale
    fy_bot = cy + 1.5 * scale
    for i, dx in enumerate([0, 0.6, 1.2]):
        out += emit_silk_line(
            fx + dx * scale, fy_bot,
            fx + (dx + 0.5) * scale, fy_top,
            layer=layer, width=0.25 * scale,
        )
    # Wordmark
    out += emit_silk_text(
        "TUDelft", cx + 1.5 * scale, cy,
        size=2.0 * scale, justify="center", layer=layer, bold=True,
    )
    return out


def emit_edge_rect(x1: float, y1: float, x2: float, y2: float) -> str:
    """Rectangle on Edge.Cuts via 4 lines."""
    lines = []
    for xa, ya, xb, yb in [
        (x1, y1, x2, y1),  # top
        (x2, y1, x2, y2),  # right
        (x2, y2, x1, y2),  # bottom
        (x1, y2, x1, y1),  # left
    ]:
        lines.append(
            f'(gr_line (start {f(xa)} {f(ya)}) (end {f(xb)} {f(yb)}) '
            f'(stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "{uuid()}"))'
        )
    return "\n".join(lines) + "\n"


def emit_track(x1: float, y1: float, x2: float, y2: float, net: Net, layer: str = "F.Cu", width: float = TRACE_W) -> str:
    return (
        f'(segment (start {f(x1)} {f(y1)}) (end {f(x2)} {f(y2)}) '
        f'(width {f(width)}) (layer "{layer}") {net.ref()} (uuid "{uuid()}"))\n'
    )


# ---------------------------------------------------------------------------
# Structure builders
# ---------------------------------------------------------------------------

def bond_pad_footprint(site_id: str, cx: float, cy: float, geometry: str, radius_um: int, mini_pads: bool, net: Net) -> str:
    pads = []
    if geometry == "plain":
        pads.append(emit_pad("1", "rect", 0, 0, BOND_PAD, BOND_PAD, net=net))
    elif geometry == "rounded":
        ratio = min(0.49, max(0.01, (radius_um / 1000.0) / BOND_PAD))
        pads.append(emit_pad("1", "roundrect", 0, 0, BOND_PAD, BOND_PAD, net=net, roundrect_ratio=ratio))
    elif geometry == "circle":
        pads.append(emit_pad("1", "circle", 0, 0, BOND_PAD, BOND_PAD, net=net))
    elif geometry == "cross":
        pads.append(emit_pad("1", "rect", 0, 0, BOND_PAD, 0.2, net=net))
        pads.append(emit_pad("1", "rect", 0, 0, 0.2, BOND_PAD, net=net))
    else:
        raise ValueError(geometry)

    if mini_pads:
        for dx, dy in [(-MINI_PAD_OFFSET, -MINI_PAD_OFFSET),
                       ( MINI_PAD_OFFSET, -MINI_PAD_OFFSET),
                       (-MINI_PAD_OFFSET,  MINI_PAD_OFFSET),
                       ( MINI_PAD_OFFSET,  MINI_PAD_OFFSET)]:
            pads.append(emit_pad("1", "rect", dx, dy, MINI_PAD, MINI_PAD, net=net))

    return emit_footprint(f"BP_{site_id}", cx, cy, pads, library_id="BondPad_DoE")


def probe_pad_footprint(name: str, cx: float, cy: float, net: Net) -> str:
    pad = emit_pad("1", "rect", 0, 0, PROBE_PAD, PROBE_PAD, net=net)
    return emit_footprint(name, cx, cy, [pad], library_id="Probe_1.27mm")


def th_header_footprint(name: str, cx: float, cy: float, drill: float = 1.0, pad_d: float = 1.7) -> str:
    pad = emit_pad("1", "circle", 0, 0, pad_d, pad_d, pad_type="thru_hole", drill=drill)
    return emit_footprint(name, cx, cy, [pad], library_id="Header_2.54mm", is_smd=False)


def fiducial_footprint(name: str, cx: float, cy: float, copper: float = 1.0, mask: float = 2.0) -> str:
    pad = emit_pad("", "circle", 0, 0, copper, copper,
                   layers=["F.Cu", "F.Mask"],
                   solder_mask_margin=(mask - copper) / 2)
    return emit_footprint(name, cx, cy, [pad], library_id="Fiducial_1mm")


def vdp_footprint(ref: str, cx: float, cy: float, arm_w: float, nm: NetManager) -> tuple[str, list[Net]]:
    arm_len = max(0.8, arm_w + 0.4)  # centre-to-centre — ensures ≥ 0.3 mm gap at corners
    pads = []
    nets = []
    contacts = [
        ("1", -arm_len, 0, 0),
        ("2",  arm_len, 0, 0),
        ("3", 0, -arm_len, 90),
        ("4", 0,  arm_len, 90),
    ]
    for num, dx, dy, rot in contacts:
        net = nm.get(f"{ref}_{num}")
        nets.append((dx, dy, net))
        pads.append(emit_pad(num, "rect", dx, dy, arm_w, arm_w, net=net, rotation=rot))
    return emit_footprint(ref, cx, cy, pads, library_id="VDP"), nets


def tlm_footprint(ref: str, cx: float, cy: float, finger_w: float, spacings_um: list[int], nm: NetManager) -> tuple[str, list[tuple[float, float, Net]]]:
    """TLM ladder. The finger spacings (5–200 µm) are intentionally smaller
    than the board-level clearance rule, so each finger pad carries a per-pad
    clearance override of 0.002 mm — DRC will not flag intra-TLM clearance."""
    finger_len = 2.5
    centres = [-finger_w / 2]
    for s_um in spacings_um:
        centres.append(centres[-1] + finger_w + s_um / 1000.0)
    width_total = centres[-1] - centres[0] + finger_w
    x0 = -width_total / 2
    pads = []
    nets = []
    for i, c in enumerate(centres, 1):
        net = nm.get(f"{ref}_F{i}")
        local_x = x0 + c
        nets.append((local_x, 0.0, net))
        # local_clearance=0.002 (2 µm) → smaller than any TLM spacing
        pads.append(emit_pad(
            str(i), "rect", local_x, 0, finger_w, finger_len, net=net,
            local_clearance=0.002,
        ))
    return emit_footprint(ref, cx, cy, pads, library_id="TLM"), nets


def daisy_chain_footprint(ref: str, cx: float, cy: float, n_dies: int, nm: NetManager) -> tuple[str, Net, Net]:
    total_pads = 2 * n_dies + 2
    width = (total_pads - 1) * DC_PITCH
    x0 = -width / 2
    pads = []
    in_net = nm.get(f"{ref}_IN")
    out_net = nm.get(f"{ref}_OUT")
    for i in range(total_pads):
        local_x = x0 + i * DC_PITCH
        if i == 0:
            net = in_net
        elif i == total_pads - 1:
            net = out_net
        else:
            net = nm.get(f"{ref}_N{i}")
        pads.append(emit_pad(str(i + 1), "rect", local_x, 0, BOND_PAD, BOND_PAD, net=net))
    return emit_footprint(ref, cx, cy, pads, library_id="DaisyChain"), in_net, out_net


def led_footprint(ref: str, cx: float, cy: float, anode: Net, k_r: Net, k_b: Net, k_g: Net) -> str:
    """Würth WL-SFCC 0404 superflat land pattern: 4 SMD pads at (±0.4, ±0.4),
    each 0.4 × 0.4 mm. Pin 1 = + (anode), 2 = -R, 3 = -B, 4 = -G."""
    pads = [
        emit_pad("1", "rect", -0.4, -0.4, 0.4, 0.4, net=anode),
        emit_pad("2", "rect",  0.4, -0.4, 0.4, 0.4, net=k_r),
        emit_pad("3", "rect",  0.4,  0.4, 0.4, 0.4, net=k_b),
        emit_pad("4", "rect", -0.4,  0.4, 0.4, 0.4, net=k_g),
    ]
    return emit_footprint(ref, cx, cy, pads, library_id="WL-SFCC_0404")


# ---------------------------------------------------------------------------
# Composition: all footprints + silkscreen for the v2 board
# ---------------------------------------------------------------------------

def build_board() -> tuple[list[str], list[str], list[str], NetManager]:
    """Return (footprints, drawings, segments, nets)."""
    nm = NetManager()
    fps = []
    drawings = []
    segments = []

    # --- Board outline -------------------------------------------------
    drawings.append(emit_edge_rect(0, 0, BOARD_W, BOARD_H))
    # Decorative silkscreen frame just inside the edge cuts
    drawings.append(emit_silk_rect(1.5, 1.5, BOARD_W - 1.5, BOARD_H - 1.5, width=0.15))

    # --- Fiducials -----------------------------------------------------
    for i, (x, y) in enumerate([(4.0, 4.0), (BOARD_W - 4.0, 4.0),
                                 (4.0, BOARD_H - 4.0), (BOARD_W - 4.0, BOARD_H - 4.0)], 1):
        fps.append(fiducial_footprint(f"FID{i}", x, y))
    # Asymmetric orientation indicator — small triangle ▲ on top-left
    # outside the title frame (well clear of the NW fiducial copper).
    drawings.append(emit_silk_line(3.0, 12.5, 4.5, 12.5, width=0.3))
    drawings.append(emit_silk_line(4.5, 12.5, 3.75, 11.0, width=0.3))
    drawings.append(emit_silk_line(3.75, 11.0, 3.0, 12.5, width=0.3))

    # =====================================================================
    # TITLE BLOCK (y=3..11) — 3 zones (TUDelft mark | project | author)
    # divided by vertical silkscreen lines. Frame keeps clear of fiducials
    # at the corners (fiducial copper at x = 4 ± 0.5, y = 4 ± 0.5).
    # =====================================================================
    title_box_y0 = 3.0
    title_box_y1 = 11.0
    title_cy = (title_box_y0 + title_box_y1) / 2
    drawings.append(emit_silk_rect(6.0, title_box_y0, BOARD_W - 6.0, title_box_y1, width=0.25))
    # Zone dividers
    zone_l = 23.0   # left of project zone
    zone_r = 75.0   # right of project zone
    drawings.append(emit_silk_line(zone_l, title_box_y0, zone_l, title_box_y1, width=0.2))
    drawings.append(emit_silk_line(zone_r, title_box_y0, zone_r, title_box_y1, width=0.2))
    # Zone 1: TUDelft mark (centered in its zone)
    drawings.append(emit_tudelft_mark((6.0 + zone_l) / 2, title_cy, scale=1.0))
    # Zone 2: project name + sub
    proj_cx = (zone_l + zone_r) / 2
    drawings.append(emit_silk_text("MICRO-LED BOND CHARACTERIZATION", proj_cx, title_cy - 1.5,
                                   size=1.4, justify="center", bold=True))
    drawings.append(emit_silk_text("PCB v2.0   /   ECTM + ITEC   /   2026", proj_cx, title_cy + 0.8,
                                   size=0.95, justify="center"))
    drawings.append(emit_silk_text("100 x 100 mm  -  2-layer FR-4  -  ENIG", proj_cx, title_cy + 2.5,
                                   size=0.8, justify="center"))
    # Zone 3: author info
    info_cx = (zone_r + BOARD_W - 6.0) / 2
    drawings.append(emit_silk_text("Daniel Tyukov", info_cx, title_cy - 1.8,
                                   size=1.1, justify="center", bold=True))
    drawings.append(emit_silk_text("student no.  5714699", info_cx, title_cy + 0.2,
                                   size=0.9, justify="center"))
    drawings.append(emit_silk_text("ET4277  +  ET4391", info_cx, title_cy + 2.0,
                                   size=0.9, justify="center"))

    # =====================================================================
    # 2.54 mm pin-header rows (Tier-2) — physical pins
    # =====================================================================
    n_pins = 30
    total_w = (n_pins - 1) * 2.54
    x0 = (BOARD_W - total_w) / 2
    for i in range(n_pins):
        xh = x0 + i * 2.54
        fps.append(th_header_footprint(f"H_N_{i+1}", xh, ROW_NORTH_HEADER))
        fps.append(th_header_footprint(f"H_S_{i+1}", xh, ROW_SOUTH_HEADER))
    # Section labels
    drawings.append(emit_silk_text("TIER-2 NORTH  -  30 pins  -  2.54 mm pitch",
                                   BOARD_W/2, ROW_NORTH_HEADER + 2.5,
                                   size=0.9, justify="center"))

    # =====================================================================
    # DoE BOND-PAD ARRAY (6×6) — concise framed section.
    # Array centered. R1..R6 + C1..C6 tags on the sides. Compact LEGEND
    # box on the right with short bullets.
    # =====================================================================
    doe_box_y0 = 17.0
    doe_box_y1 = 43.5
    drawings.append(emit_silk_rect(3.5, doe_box_y0, BOARD_W - 3.5, doe_box_y1, width=0.15))
    drawings.append(emit_silk_text("BOND-PAD DoE  (6 x 6 @ 3.5 mm pitch)",
                                   BOARD_W/2, doe_box_y0 + 1.2,
                                   size=1.1, justify="center", bold=True))

    array_total_w = (DOE_COLS - 1) * DOE_PITCH
    array_x0 = 14.0
    array_x1 = array_x0 + array_total_w
    doe_meta = []
    for r in range(DOE_ROWS):
        for c in range(DOE_COLS):
            cx = array_x0 + c * DOE_PITCH
            cy = DOE_ORIGIN_Y + r * DOE_PITCH
            site_id = f"R{r+1}C{c+1}"
            if r < 2:
                geom, R, minis = "plain", 0, False
            elif r < 4:
                geom, R, minis = "plain", 0, True
            else:
                geom, R, minis = "rounded", [50, 100, 200, 50, 100, 200][c], True
            net = nm.get(f"BP_{site_id}_P1")
            fps.append(bond_pad_footprint(site_id, cx, cy, geom, R, minis, net))
            doe_meta.append((r, c, cx, cy, site_id, net))

    # Row tags on the LEFT of the array (right-anchored for tight alignment)
    for r in range(DOE_ROWS):
        cy = DOE_ORIGIN_Y + r * DOE_PITCH
        drawings.append(emit_silk_text(f"R{r+1}", array_x0 - 1.8, cy + 0.3,
                                       size=0.9, justify="right", bold=True))
    # Column tags BELOW the array (so they don't collide with the section header)
    for c in range(DOE_COLS):
        cx = array_x0 + c * DOE_PITCH
        drawings.append(emit_silk_text(f"C{c+1}", cx,
                                       DOE_ORIGIN_Y + 5 * DOE_PITCH + 2.0,
                                       size=0.85, justify="center"))

    # Compact LEGEND on the right
    leg_x0 = array_x1 + 5.0
    leg_x1 = BOARD_W - 5.5
    leg_y0 = DOE_ORIGIN_Y - 1.5
    leg_y1 = DOE_ORIGIN_Y + 5 * DOE_PITCH + 1.5
    leg_cx = (leg_x0 + leg_x1) / 2
    drawings.append(emit_silk_rect(leg_x0, leg_y0, leg_x1, leg_y1, width=0.15))
    drawings.append(emit_silk_text("LEGEND", leg_cx, leg_y0 + 1.5,
                                   size=0.95, justify="center", bold=True))
    legend_lines = [
        "R1, R2  :  plain",
        "R3, R4  :  + 4 minis",
        "R5, R6  :  rounded + minis",
        "",
        "C1, C4  :  R = 50 um",
        "C2, C5  :  R = 100 um",
        "C3, C6  :  R = 200 um",
    ]
    for i, ln in enumerate(legend_lines):
        if not ln:
            continue
        drawings.append(emit_silk_text(ln, leg_cx, leg_y0 + 3.5 + i * 2.2,
                                       size=0.8, justify="center"))

    # --- DoE probe pads ------------------------------------------------
    # IMPORTANT: each DoE bond pad is 1×1 mm, large enough to probe DIRECTLY
    # with a tungsten/BeCu needle. We don't add separate probe pads here in
    # v2.0 — straight column-wise routing collides with intervening bond
    # pads and proper 2-layer fan-out is deferred to v2.1.
    # Row IDs are silkscreened next to the array so sites are addressable.

    # =====================================================================
    # TLM LADDERS — contact resistivity, sub-µm spacings
    # =====================================================================
    tlm_box_y0 = 45.0
    tlm_box_y1 = 58.0
    drawings.append(emit_silk_rect(3.5, tlm_box_y0, BOARD_W - 3.5, tlm_box_y1, width=0.15))
    drawings.append(emit_silk_text("TLM LADDERS",
                                   BOARD_W/2, tlm_box_y0 + 1.6,
                                   size=1.2, justify="center", bold=True))
    drawings.append(emit_silk_text("spacings:  5  /  10  /  20  /  50  /  100  /  200 um",
                                   BOARD_W/2, tlm_box_y0 + 3.3,
                                   size=0.8, justify="center"))
    spacings = [5, 10, 20, 50, 100, 200]   # µm
    widths = [0.25, 0.5, 1.0]              # mm
    tlm_x_centres = [22.0, 50.0, 78.0]
    for x_c, w in zip(tlm_x_centres, widths):
        fp_str, nets = tlm_footprint(f"TLM_W{w}", x_c, ROW_TLM, w, spacings, nm)
        fps.append(fp_str)
        drawings.append(emit_silk_text(f"TLM  W = {w} mm", x_c, ROW_TLM + 2.5,
                                       size=1.0, justify="center", bold=True))

    # =====================================================================
    # VDP CLOVERLEAVES — sheet resistance
    # =====================================================================
    vdp_box_y0 = 59.0
    vdp_box_y1 = 67.0
    drawings.append(emit_silk_rect(3.5, vdp_box_y0, BOARD_W - 3.5, vdp_box_y1, width=0.15))
    drawings.append(emit_silk_text("VAN DER PAUW",
                                   BOARD_W/2, vdp_box_y0 + 1.5,
                                   size=1.2, justify="center", bold=True))
    vdp_widths = [1.0, 0.5, 0.25, 0.1]
    vdp_x_centres = [15.0, 38.0, 62.0, 85.0]
    for x_c, w in zip(vdp_x_centres, vdp_widths):
        fp_str, nets = vdp_footprint(f"VDP_W{w}", x_c, ROW_VDP, w, nm)
        fps.append(fp_str)
        drawings.append(emit_silk_text(f"VDP  W = {w} mm", x_c, ROW_VDP + 2.5,
                                       size=0.9, justify="center", bold=True))

    # =====================================================================
    # DAISY CHAINS — n bond joints in series
    # =====================================================================
    dc_box_y0 = 68.0
    dc_box_y1 = 79.0
    drawings.append(emit_silk_rect(3.5, dc_box_y0, BOARD_W - 3.5, dc_box_y1, width=0.15))
    drawings.append(emit_silk_text("DAISY CHAINS",
                                   BOARD_W/2, dc_box_y0 + 1.5,
                                   size=1.2, justify="center", bold=True))
    dc_layouts = [
        ( 6, 22.0, ROW_DAISY),
        (12, 70.0, ROW_DAISY),
    ]
    for n, x_c, y_c in dc_layouts:
        fp_str, in_net, out_net = daisy_chain_footprint(f"DC_N{n}", x_c, y_c, n, nm)
        fps.append(fp_str)
        drawings.append(emit_silk_text(f"DC  N = {n}  dies", x_c, y_c - 2.0,
                                       size=1.0, justify="center", bold=True))
        chain_w = (2 * n + 1) * DC_PITCH
        chain_in_x = x_c - chain_w/2
        chain_out_x = x_c + chain_w/2
        in_x = max(EDGE_MARGIN + PROBE_PAD/2 + 0.5, chain_in_x - 2.0)
        out_x = min(BOARD_W - EDGE_MARGIN - PROBE_PAD/2 - 0.5, chain_out_x + 2.0)
        probe_y = y_c + 3.5
        fps.append(probe_pad_footprint(f"PP_DC{n}_IN", in_x, probe_y, in_net))
        fps.append(probe_pad_footprint(f"PP_DC{n}_OUT", out_x, probe_y, out_net))
        drawings.append(emit_silk_text("IN", in_x, probe_y + 1.2, size=0.7, justify="center"))
        drawings.append(emit_silk_text("OUT", out_x, probe_y + 1.2, size=0.7, justify="center"))
        segments.append(emit_track(in_x, probe_y, in_x, y_c, in_net))
        segments.append(emit_track(in_x, y_c, chain_in_x, y_c, in_net))
        segments.append(emit_track(out_x, probe_y, out_x, y_c, out_net))
        segments.append(emit_track(out_x, y_c, chain_out_x, y_c, out_net))

    # =====================================================================
    # LED ROW — 8 × Würth WL-SFCC 0404 super-flat RGB LEDs
    # Vertical packing (mm): header 80.5 | LED 82.5 | D-tag 84.0 | probes 85.5
    # =====================================================================
    led_box_y0 = 79.5
    led_box_y1 = 86.7
    drawings.append(emit_silk_rect(3.5, led_box_y0, BOARD_W - 3.5, led_box_y1, width=0.15))
    drawings.append(emit_silk_text("WL-SFCC 0404 RGB LEDs",
                                   BOARD_W/2, led_box_y0 + 1.2,
                                   size=1.1, justify="center", bold=True))

    led_pitch = 10.0
    led_x0 = (BOARD_W - 7 * led_pitch) / 2
    common_anode = nm.get("LED_VCC")
    led_pad_offsets = {
        "A":  (-0.4, -0.4),
        "KR": ( 0.4, -0.4),
        "KB": ( 0.4,  0.4),
        "KG": (-0.4,  0.4),
    }
    a_probe_xs = []
    for i in range(8):
        x = led_x0 + i * led_pitch
        net_r = nm.get(f"LED{i+1}_KR")
        net_b = nm.get(f"LED{i+1}_KB")
        net_g = nm.get(f"LED{i+1}_KG")
        fps.append(led_footprint(f"D{i+1}", x, ROW_LED, common_anode, net_r, net_b, net_g))
        # D-tag goes BELOW the LED footprint (between LED and probe row).
        drawings.append(emit_silk_text(f"D{i+1}", x, ROW_LED + 1.8,
                                       size=0.85, justify="center", bold=True))
        probe_layout = [
            (-3.0, "A",  common_anode),
            (-1.0, "KG", net_g),
            ( 1.0, "KB", net_b),
            ( 3.0, "KR", net_r),
        ]
        for dx, label, net in probe_layout:
            px = x + dx
            py = ROW_LED_PROBES
            fps.append(probe_pad_footprint(f"PP_D{i+1}_{label}", px, py, net))
            pad_dx, pad_dy = led_pad_offsets[label]
            target_x = x + pad_dx
            target_y = ROW_LED + pad_dy
            meet_y = ROW_LED + 1.0
            segments.append(emit_track(px, py, px, meet_y, net))
            segments.append(emit_track(px, meet_y, target_x, target_y, net))
            if label == "A":
                a_probe_xs.append(px)

    # Common-anode bus on B.Cu — vias at each A probe + horizontal trace.
    # Sits below the LED row in the inverted-Y plane (B.Cu has no other
    # routing so it's a clean ground plane / bus area).
    if a_probe_xs:
        for px in a_probe_xs:
            # Via from F.Cu A-probe through to B.Cu
            segments.append(
                f'(via (at {f(px)} {f(ROW_LED_PROBES)}) (size 0.6) (drill 0.3) '
                f'(layers "F.Cu" "B.Cu") {common_anode.ref()} (uuid "{uuid()}"))\n'
            )
        bus_y = ROW_LED_PROBES
        for i in range(len(a_probe_xs) - 1):
            segments.append(emit_track(
                a_probe_xs[i], bus_y, a_probe_xs[i + 1], bus_y,
                common_anode, layer="B.Cu", width=0.4,
            ))

    # =====================================================================
    # SOUTH-HEADER LABEL + mm RULER
    # =====================================================================
    drawings.append(emit_silk_text("TIER-2 SOUTH  -  30 pins  -  2.54 mm pitch",
                                   BOARD_W/2, ROW_SOUTH_HEADER + 2.5,
                                   size=0.9, justify="center"))

    # mm ruler: horizontal line with tick marks every 5mm and labels every 10mm
    ruler_x0 = (BOARD_W - 80) / 2
    ruler_x1 = ruler_x0 + 80
    ruler_y = ROW_RULER_Y
    drawings.append(emit_silk_line(ruler_x0, ruler_y, ruler_x1, ruler_y, width=0.18))
    for mm_val in range(0, 81, 5):
        x = ruler_x0 + mm_val
        tick = 1.0 if mm_val % 10 == 0 else 0.6
        drawings.append(emit_silk_line(x, ruler_y, x, ruler_y + tick, width=0.18))
        if mm_val % 10 == 0:
            drawings.append(emit_silk_text(str(mm_val), x, ruler_y + 1.8,
                                           size=0.85, justify="center"))

    # =====================================================================
    # BACK-SIDE silkscreen — title, fab notes, pinout table, course info
    # =====================================================================
    _emit_back_side_silk(drawings)

    return fps, drawings, segments, nm


def _emit_back_side_silk(drawings: list) -> None:
    """B.SilkS — minimal, all text centered, no overflow."""
    L = "B.SilkS"
    cx = BOARD_W / 2

    # Outer decorative frame matching the front
    drawings.append(emit_silk_rect(1.5, 1.5, BOARD_W - 1.5, BOARD_H - 1.5, layer=L, width=0.15))

    # ── TITLE BLOCK ────────────────────────────────────────────────────
    drawings.append(emit_silk_rect(3.5, 3.0, BOARD_W - 3.5, 12.0, layer=L, width=0.25))
    drawings.append(emit_tudelft_mark(cx, 6.5, scale=1.4, layer=L))
    drawings.append(emit_silk_text("BOTTOM  -  tud-microled-v2  -  2026",
                                   cx, 10.5, size=0.95, justify="center", layer=L))

    # ── FABRICATION (single column, compact) ───────────────────────────
    fab_y0 = 16.0
    fab_y1 = 36.0
    drawings.append(emit_silk_rect(3.5, fab_y0, BOARD_W - 3.5, fab_y1, layer=L, width=0.15))
    drawings.append(emit_silk_text("FABRICATION", cx, fab_y0 + 2.0,
                                   size=1.2, justify="center", bold=True, layer=L))
    fab_lines = [
        "2-layer FR-4   1.6 mm   1 oz Cu",
        "Finish:  ENIG   (Ni 4 um / Au 0.075 um)",
        "Mask:  matte green   /   silk:  white",
        "Min clearance 0.15 mm   /   min trace 0.20 mm",
        "Min via / drill   0.45 / 0.20 mm",
    ]
    for i, ln in enumerate(fab_lines):
        drawings.append(emit_silk_text(ln, cx, fab_y0 + 5.0 + i * 2.8,
                                       size=0.85, justify="center", layer=L))

    # ── ASSEMBLY (single column, compact) ──────────────────────────────
    asm_y0 = 38.0
    asm_y1 = 58.0
    drawings.append(emit_silk_rect(3.5, asm_y0, BOARD_W - 3.5, asm_y1, layer=L, width=0.15))
    drawings.append(emit_silk_text("ASSEMBLY", cx, asm_y0 + 2.0,
                                   size=1.2, justify="center", bold=True, layer=L))
    asm_lines = [
        "Paste:   TS391LT  Sn42 Bi57.6 Ag0.4",
        "Stencil:  100 um SS  (eC-stencil-mate)",
        "Bonder:  Tresky T-3000-PRO",
        "Reflow:  hot-plate, peak 165 C",
        "Metrology:  Keyence VK-X250 + X-ray + shear",
    ]
    for i, ln in enumerate(asm_lines):
        drawings.append(emit_silk_text(ln, cx, asm_y0 + 5.0 + i * 2.8,
                                       size=0.85, justify="center", layer=L))

    # ── DESIGNER ───────────────────────────────────────────────────────
    aut_y0 = 59.0
    aut_y1 = 72.0
    drawings.append(emit_silk_rect(3.5, aut_y0, BOARD_W - 3.5, aut_y1, layer=L, width=0.15))
    drawings.append(emit_silk_text("DESIGNER", cx, aut_y0 + 2.0,
                                   size=1.2, justify="center", bold=True, layer=L))
    drawings.append(emit_silk_text("Daniel Tyukov  -  student no. 5714699",
                                   cx, aut_y0 + 5.0, size=0.95, justify="center", layer=L))
    drawings.append(emit_silk_text("ET4277  +  ET4391  -  TU Delft  MSc EE",
                                   cx, aut_y0 + 7.5, size=0.9, justify="center", layer=L))
    drawings.append(emit_silk_text("based on  Abdelwahab et al.  ECTC 2025",
                                   cx, aut_y0 + 10.0, size=0.85, justify="center", layer=L))

    # ── SECTION KEY ────────────────────────────────────────────────────
    # South-header through-holes are at y=89 (pad dia 1.7 → 88.15-89.85).
    # Box and ALL text must clear y < 87.5 with margin.
    key_y0 = 73.5
    key_y1 = 86.0
    drawings.append(emit_silk_rect(3.5, key_y0, BOARD_W - 3.5, key_y1, layer=L, width=0.15))
    drawings.append(emit_silk_text("SECTION KEY", cx, key_y0 + 1.7,
                                   size=1.1, justify="center", bold=True, layer=L))
    # Combine LEDs and probes into one line so we have 5, not 6
    key_lines = [
        "DoE  -  6 x 6 isolated bond pads",
        "TLM  -  contact-resistivity ladder",
        "VDP  -  Van der Pauw cloverleaf",
        "DC   -  daisy chain (N joints)",
        "D1..D8  +  PP-*  -  LEDs and probes",
    ]
    for i, ln in enumerate(key_lines):
        drawings.append(emit_silk_text(ln, cx, key_y0 + 3.8 + i * 1.55,
                                       size=0.8, justify="center", layer=L))


# ---------------------------------------------------------------------------
# .kicad_pcb file emission
# ---------------------------------------------------------------------------

PCB_HEADER = """(kicad_pcb
\t(version 20241229)
\t(generator "tud-microled-v2-generator")
\t(generator_version "1.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "TUD micro-LED bond characterization v2")
\t\t(date "2026-05-16")
\t\t(rev "v2.0")
\t\t(comment 1 "Generator: new-pcb/tools/generate_pcb_text.py")
\t\t(comment 2 "Authors: ECTM TU Delft + ITEC")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(17 "Dwgs.User" user "User.Drawings")
\t\t(19 "Cmts.User" user "User.Comments")
\t\t(21 "Eco1.User" user "User.Eco1")
\t\t(23 "Eco2.User" user "User.Eco2")
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t\t(39 "User.1" user)
\t\t(41 "User.2" user)
\t\t(43 "User.3" user)
\t\t(45 "User.4" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(tenting front back)
\t\t(pcbplotparams
\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)
\t\t\t(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)
\t\t\t(disableapertmacros no)
\t\t\t(usegerberextensions no)
\t\t\t(usegerberattributes yes)
\t\t\t(usegerberadvancedattributes yes)
\t\t\t(creategerberjobfile yes)
\t\t\t(dashed_line_dash_ratio 12.000000)
\t\t\t(dashed_line_gap_ratio 3.000000)
\t\t\t(svgprecision 4)
\t\t\t(plotframeref no)
\t\t\t(mode 1)
\t\t\t(useauxorigin no)
\t\t\t(hpglpennumber 1)
\t\t\t(hpglpenspeed 20)
\t\t\t(hpglpendiameter 15.000000)
\t\t\t(pdf_front_fp_property_popups yes)
\t\t\t(pdf_back_fp_property_popups yes)
\t\t\t(pdf_metadata yes)
\t\t\t(pdf_single_document no)
\t\t\t(dxfpolygonmode yes)
\t\t\t(dxfimperialunits yes)
\t\t\t(dxfusepcbnewfont yes)
\t\t\t(psnegative no)
\t\t\t(psa4output no)
\t\t\t(plot_black_and_white yes)
\t\t\t(sketchpadsonfab no)
\t\t\t(plotpadnumbers no)
\t\t\t(hidednponfab no)
\t\t\t(sketchdnponfab yes)
\t\t\t(crossoutdnponfab yes)
\t\t\t(subtractmaskfromsilk no)
\t\t\t(outputformat 1)
\t\t\t(mirror no)
\t\t\t(drillshape 1)
\t\t\t(scaleselection 1)
\t\t\t(outputdirectory "")
\t\t)
\t)
"""

PCB_FOOTER = ")\n"


def main() -> int:
    print("Building board structure...")
    fps, drawings, segments, nm = build_board()
    print(f"  Footprints:  {len(fps)}")
    print(f"  Drawings:    {len(drawings)}")
    print(f"  Segments:    {len(segments)}")
    print(f"  Nets:        {len(nm.all_nets())}")

    print(f"Writing: {BOARD_PATH}")
    with open(BOARD_PATH, "w") as fh:
        fh.write(PCB_HEADER)
        for net in nm.all_nets():
            fh.write(f"\t{net.sexp()}\n")
        for d in drawings:
            fh.write(d)
        for fp in fps:
            fh.write(fp)
        for s in segments:
            fh.write(s)
        fh.write(PCB_FOOTER)

    print("Done. Now run kicad-cli pcb drc / open in KiCad.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
