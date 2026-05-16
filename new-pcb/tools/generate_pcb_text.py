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

BOARD_W = 93.0
BOARD_H = 93.0
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

# Test-structure row Y positions (re-spaced for BOARD_H = 95mm — fits Tresky
# die-bonder envelope (≤95×95mm)). Sections from VDP downward are compressed
# vs the original 100mm layout; the DoE grid (21–43) is unchanged so the
# scientific bond-pad geometry stays bit-identical.
ROW_TITLE_Y       = 3.0
ROW_NORTH_HEADER  = 13.5
ROW_TLM           = 50.5
ROW_VDP           = 61.5
ROW_DAISY         = 70.0
ROW_DAISY_PROBES  = 72.5      # chain probe = DAISY + 2.5
ROW_LED           = 78.0
ROW_LED_PROBES    = 81.0      # LED probe = LED + 3.0
ROW_SOUTH_HEADER  = 85.0
ROW_RULER_Y       = 89.0      # mm ruler restored (93x93 board has the headroom)

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
    # When net is None we still emit `(net 0 "")` as a placeholder so the field
    # can be patched later (e.g., by the NORTH-header net-assignment pass).
    net_str = net.sexp() if net is not None else '(net 0 "")'
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


def emit_via(x: float, y: float, net: Net, size: float = 0.6, drill: float = 0.3) -> str:
    return (
        f'(via (at {f(x)} {f(y)}) (size {f(size)}) (drill {f(drill)}) '
        f'(layers "F.Cu" "B.Cu") {net.ref()} (uuid "{uuid()}"))\n'
    )


def route_dogbone(
    src_x: float, src_y: float,
    dst_x: float, dst_y: float,
    fanout_y: float,
    net: Net,
    breakout: float = 2.0,
    width_signal: float = TRACE_W,
    width_bus: float = 0.30,
) -> list[str]:
    """Route from a top-layer pad/pin at (src_x, src_y) to another top-layer
    pad at (dst_x, dst_y) by way of a back-layer 'dogbone':

        F.Cu  : src → (src_x, src_y ± breakout)
        via   : down to B.Cu
        B.Cu  : vertical to fanout_y, then horizontal to (dst_x, fanout_y)
        via   : back to F.Cu
        F.Cu  : (dst_x, fanout_y) → dst

    Each pin uses a unique fanout_y so horizontal segments on B.Cu never
    collide with each other. The breakout distance keeps vias outside
    the header-pad keepout."""
    out = []
    direction = 1 if src_y < fanout_y else -1
    breakout_y = src_y + direction * breakout
    # F.Cu breakout
    out.append(emit_track(src_x, src_y, src_x, breakout_y, net, layer="F.Cu", width=width_signal))
    # Via to B.Cu at breakout point
    out.append(emit_via(src_x, breakout_y, net))
    # B.Cu vertical to fanout Y
    if breakout_y != fanout_y:
        out.append(emit_track(src_x, breakout_y, src_x, fanout_y, net, layer="B.Cu", width=width_bus))
    # B.Cu horizontal at fanout Y
    if src_x != dst_x:
        out.append(emit_track(src_x, fanout_y, dst_x, fanout_y, net, layer="B.Cu", width=width_bus))
    # Via back to F.Cu near dst
    out.append(emit_via(dst_x, fanout_y, net))
    # F.Cu to dst
    out.append(emit_track(dst_x, fanout_y, dst_x, dst_y, net, layer="F.Cu", width=width_signal))
    return out


def route_short(
    src_x: float, src_y: float,
    dst_x: float, dst_y: float,
    jog_y: float,
    net: Net,
    width: float = TRACE_W,
) -> list[str]:
    """All-F.Cu Manhattan route from (src_x, src_y) to (dst_x, dst_y) via an
    intermediate horizontal segment at jog_y. Used for the short south-side
    header → LED probe routes where B.Cu is unnecessary."""
    out = [
        emit_track(src_x, src_y, src_x, jog_y, net, layer="F.Cu", width=width),
        emit_track(src_x, jog_y, dst_x, jog_y, net, layer="F.Cu", width=width),
        emit_track(dst_x, jog_y, dst_x, dst_y, net, layer="F.Cu", width=width),
    ]
    return out


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


def th_header_footprint(name: str, cx: float, cy: float, drill: float = 1.0, pad_d: float = 1.7, net: Net | None = None) -> str:
    pad = emit_pad("1", "circle", 0, 0, pad_d, pad_d, pad_type="thru_hole", drill=drill, net=net)
    return emit_footprint(name, cx, cy, [pad], library_id="Header_2.54mm", is_smd=False)


def fiducial_footprint(name: str, cx: float, cy: float, copper: float = 1.0, mask: float = 2.0) -> str:
    pad = emit_pad("", "circle", 0, 0, copper, copper,
                   layers=["F.Cu", "F.Mask"],
                   solder_mask_margin=(mask - copper) / 2)
    return emit_footprint(name, cx, cy, [pad], library_id="Fiducial_1mm")


def ntc_footprint(name: str, cx: float, cy: float, signal_net: Net, gnd_net: Net) -> str:
    """0402 NTC thermistor (e.g. Murata NCP15XH103J03RC, 10 kΩ @ 25 °C).
    Body ~1 × 0.5 mm; two 0.5 × 0.6 mm SMD pads centred at x = ±0.5 mm."""
    pads = [
        emit_pad("1", "rect", -0.50, 0, 0.5, 0.6, net=signal_net),
        emit_pad("2", "rect",  0.50, 0, 0.5, 0.6, net=gnd_net),
    ]
    return emit_footprint(name, cx, cy, pads, library_id="NTC_0402")


def tc_pad_footprint(name: str, cx: float, cy: float) -> str:
    """1 × 1 mm gold pad for soldering a thermocouple wire during reflow."""
    pad = emit_pad("1", "rect", 0, 0, 1.0, 1.0)
    return emit_footprint(name, cx, cy, [pad], library_id="TC_Pad_1mm")


def emit_zone(
    x1: float, y1: float, x2: float, y2: float,
    net: Net, layer: str = "B.Cu",
    thermal_gap: float = 0.30, thermal_bridge: float = 0.30,
    clearance: float = 0.20, min_thickness: float = 0.20,
) -> str:
    """Poured copper zone — rectangular outline, filled at plot time."""
    return (
        f'(zone (net {net.code}) (net_name "{net.name}") (layer "{layer}") '
        f'(uuid "{uuid()}") (hatch edge 0.5)\n'
        f'  (connect_pads (clearance {f(clearance)}))\n'
        f'  (min_thickness {f(min_thickness)})\n'
        f'  (filled_areas_thickness no)\n'
        f'  (fill yes (thermal_gap {f(thermal_gap)}) (thermal_bridge_width {f(thermal_bridge)}))\n'
        f'  (polygon (pts\n'
        f'    (xy {f(x1)} {f(y1)}) (xy {f(x2)} {f(y1)}) '
        f'(xy {f(x2)} {f(y2)}) (xy {f(x1)} {f(y2)})\n'
        f'  ))\n'
        f')\n'
    )


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


# WL-SFCC LED chain pitch. With body 0.95 mm + clearance, 2.5 mm pitch
# leaves a 1.55 mm gap between bodies → comfortable inter-LED trace + reflow
# void evacuation. Tighter than the original DC_PITCH (1.8 mm) is unsafe
# because the LED body is wider than the 1 mm² dummy-die pad.
LED_CHAIN_PITCH = 2.5


def led_chain_footprints(
    ref_prefix: str,
    cx: float,
    cy: float,
    n_leds: int,
    nm: "NetManager",
    pitch: float = LED_CHAIN_PITCH,
) -> tuple[list[str], "Net", "Net", list[str], float, float]:
    """N WL-SFCC 0404 LEDs in a horizontal row centred at (cx, cy), wired
    in series via the RED diode chain only:

        IN+ → LED1.A → R-diode → LED1.K_R → [inter-LED trace] → LED2.A → ...
              ... → LED_N.K_R → OUT−

    Each LED forward-biases via its red die under chain current. The chain
    tests 2N bonds (one A bond + one K_R bond per LED). A single failed
    bond opens the chain.

    The green (K_G) and blue (K_B) cathode pads of each LED are bonded
    during reflow (they receive solder paste from the stencil) and are
    given UNIQUE per-LED nets — this keeps them out of any electrical
    short with the chain, leaves them probe-accessible directly on the
    LED pad, and is recognised as a 1-pad net by DRC (no unconnected-pad
    warning).

    Returns (footprints, in_net, out_net, segments, chain_left_x, chain_right_x).
    `chain_left_x` is the X of LED_1.A pad centre, `chain_right_x` is the X of
    LED_N.K_R pad centre — used by the caller to land IN/OUT probe traces.
    """
    in_net = nm.get(f"{ref_prefix}_IN")
    out_net = nm.get(f"{ref_prefix}_OUT")

    width = (n_leds - 1) * pitch
    x0 = cx - width / 2  # X of first LED's centre

    fps: list[str] = []
    segments: list[str] = []

    for i in range(n_leds):
        x = x0 + i * pitch
        ref = f"{ref_prefix}_L{i + 1}"
        # Anode: chain IN for first LED, junction-with-previous otherwise
        a_net = in_net if i == 0 else nm.get(f"{ref_prefix}_J{i}")
        # K_R: chain OUT for last LED, junction-with-next otherwise
        k_r_net = out_net if i == n_leds - 1 else nm.get(f"{ref_prefix}_J{i + 1}")
        # K_G and K_B: per-LED isolated nets (intentionally not on the chain;
        # accessible only via manual probing directly on the LED pad).
        k_g_net = nm.get(f"{ref_prefix}_L{i + 1}_KG")
        k_b_net = nm.get(f"{ref_prefix}_L{i + 1}_KB")
        fps.append(led_footprint(ref, x, cy, a_net, k_r_net, k_b_net, k_g_net))
        # Inter-LED trace on F.Cu: from K_R of THIS LED to A of NEXT LED.
        # Both pads are at the "top" row (y = cy − 0.4) of their respective
        # footprints, so the trace is a single horizontal segment.
        if i < n_leds - 1:
            x_kr_here = x + 0.4
            x_a_next = x + pitch - 0.4
            y_trace = cy - 0.4
            segments.append(emit_track(x_kr_here, y_trace, x_a_next, y_trace, k_r_net))

    chain_left_x = x0 - 0.4                                 # LED_1.A pad centre
    chain_right_x = x0 + (n_leds - 1) * pitch + 0.4         # LED_N.K_R pad centre
    return fps, in_net, out_net, segments, chain_left_x, chain_right_x


# ---------------------------------------------------------------------------
# Composition: all footprints + silkscreen for the v2 board
# ---------------------------------------------------------------------------

def south_pin_net(pin_idx: int, nm: NetManager) -> "Net | None":
    """Map a SOUTH-header pin index (1..32) to its assigned LED net.

    All 8 LEDs × 4 signals = 32 nets headerized into a 32-pin row.
    Pin 1  → D1 A  (LED_VCC)
    Pin 2  → D1 KG
    ...
    Pin 32 → D8 KR"""
    if pin_idx < 1 or pin_idx > 32:
        return None
    idx0 = pin_idx - 1
    led = idx0 // 4 + 1
    role = idx0 % 4
    if led > 8:
        return None
    if role == 0:
        return nm.get("LED_VCC")
    role_name = {1: "KG", 2: "KB", 3: "KR"}[role]
    return nm.get(f"LED{led}_{role_name}")


def south_pin_target_xy(pin_idx: int, board_w: float, row_led_probes: float) -> tuple[float, float]:
    """The (target_x, target_y) for the south header pin → LED probe pad.
    LED i has probes at x = led_x ± {-3, -1, +1, +3} for {A, KG, KB, KR}."""
    led_pitch = 10.0
    led_x0 = (board_w - 7 * led_pitch) / 2
    idx0 = pin_idx - 1
    led = idx0 // 4 + 1
    role = idx0 % 4
    led_x = led_x0 + (led - 1) * led_pitch
    role_dx = {0: -3.0, 1: -1.0, 2: 1.0, 3: 3.0}[role]
    return (led_x + role_dx, row_led_probes)


def build_board() -> tuple[list[str], list[str], list[str], NetManager]:
    """Return (footprints, drawings, segments, nets)."""
    nm = NetManager()
    fps = []
    drawings = []
    segments = []
    # Per-target registries — filled while placing structures, drained when
    # we route the Tier-2 header pre-wires at the end of this function.
    vdp_targets: list[tuple[str, "Net", float, float]] = []   # (label, net, x, y)
    dc_targets: list[tuple[str, "Net", float, float]] = []
    tlm_targets: list[tuple[str, "Net", float, float]] = []
    led_probe_targets: list[tuple[str, "Net", float, float]] = []

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
    # Zone dividers — shifted left for 95mm board so author zone keeps its 19mm
    # width (was zone_l=23, zone_r=75 on the 100mm board).
    zone_l = 18.0   # left of project zone
    zone_r = 70.0   # right of project zone
    drawings.append(emit_silk_line(zone_l, title_box_y0, zone_l, title_box_y1, width=0.2))
    drawings.append(emit_silk_line(zone_r, title_box_y0, zone_r, title_box_y1, width=0.2))
    # Zone 1: TUDelft mark (centered in its zone). Scaled down vs the 100mm
    # layout because the zone shrank from 17mm to 12mm wide.
    drawings.append(emit_tudelft_mark((6.0 + zone_l) / 2, title_cy, scale=0.85))
    # Zone 2: project name + sub
    proj_cx = (zone_l + zone_r) / 2
    drawings.append(emit_silk_text("MICRO-LED BOND CHARACTERIZATION", proj_cx, title_cy - 1.5,
                                   size=1.4, justify="center", bold=True))
    drawings.append(emit_silk_text("PCB v2.0   /   ECTM + ITEC   /   2026", proj_cx, title_cy + 0.8,
                                   size=0.95, justify="center"))
    drawings.append(emit_silk_text("93 x 93 mm  -  2-layer FR-4  -  ENIG (all pads gold)", proj_cx, title_cy + 2.5,
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
    # 2.54 mm pin-header rows (Tier-2) — physical pins.
    # NORTH: 30 pins, ALL pre-wired to VDP / DC / TLM via B.Cu dogbone.
    # SOUTH: 32 pins, ALL pre-wired to D1..D8 × 4 LED signals on F.Cu.
    # =====================================================================
    # NORTH and SOUTH headers both have 32 pins at the SAME X positions so a
    # 32-pin breadboard / IDC connector can mate both rows without distortion.
    n_pins_north = 32
    n_pins_south = 32
    north_total_w = (n_pins_north - 1) * 2.54
    south_total_w = (n_pins_south - 1) * 2.54
    north_x0 = (BOARD_W - north_total_w) / 2
    south_x0 = (BOARD_W - south_total_w) / 2

    # ───── NORTH header pre-routing: 4 pins → LED-chain probe endpoints ─────
    # Pre-create the chain nets here (before the chain footprints, which call
    # nm.get() with the same names — NetManager dedupes by name) so we can
    # assign them to specific north pins at pad creation. Pin selection chosen
    # so that each pin's vertical path is collision-free below (DoE / TLM /
    # VDP / chain LEDs), with the closest pin x to each chain probe:
    NORTH_CHAIN_PIN_NETS = {
         3: nm.get("DCL6_IN"),
        10: nm.get("DCL6_OUT"),
        19: nm.get("DCL12_IN"),
        32: nm.get("DCL12_OUT"),
    }

    for i in range(n_pins_north):
        xh = north_x0 + i * 2.54
        pin_idx = i + 1
        # Pin 1, 10, 22, 30 are pre-wired to chain endpoints below; the other
        # 26 stay user-jumperable (pad net = none).
        pin_net = NORTH_CHAIN_PIN_NETS.get(pin_idx)
        fps.append(th_header_footprint(f"H_N_{pin_idx}", xh, ROW_NORTH_HEADER, net=pin_net))
    for i in range(n_pins_south):
        xh = south_x0 + i * 2.54
        south_net = south_pin_net(i + 1, nm)
        fps.append(th_header_footprint(f"H_S_{i+1}", xh, ROW_SOUTH_HEADER, net=south_net))
    # Section labels
    # Single-line caption — fits in the 2.4mm strip between silk circle
    # bottoms (y=14.6) and DoE frame top (y=17).
    drawings.append(emit_silk_text("NORTH 32-pin  -  O = pre-wired LED chain (others jumperable)",
                                   BOARD_W/2, ROW_NORTH_HEADER + 2.2,
                                   size=0.5, justify="center"))

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
    tlm_box_y0 = 44.5
    tlm_box_y1 = 56.5
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
        # Register the two END fingers for header-routing (F1, F7).
        # nets is a list of (local_x, local_y, net) — element 0 is F1, -1 is F7.
        for label, (lx, ly, net) in [("F1", nets[0]), ("F7", nets[-1])]:
            tlm_targets.append((f"TLM_W{w}_{label}", net, x_c + lx, ROW_TLM + ly))

    # =====================================================================
    # VDP CLOVERLEAVES — sheet resistance
    # =====================================================================
    vdp_box_y0 = 57.5
    vdp_box_y1 = 65.5
    drawings.append(emit_silk_rect(3.5, vdp_box_y0, BOARD_W - 3.5, vdp_box_y1, width=0.15))
    drawings.append(emit_silk_text("VAN DER PAUW",
                                   BOARD_W/2, vdp_box_y0 + 1.5,
                                   size=1.2, justify="center", bold=True))
    vdp_widths = [1.0, 0.5, 0.25, 0.1]
    vdp_x_centres = [15.0, 38.0, 62.0, 85.0]
    for x_c, w in zip(vdp_x_centres, vdp_widths):
        fp_str, nets = vdp_footprint(f"VDP_W{w}", x_c, ROW_VDP, w, nm)
        fps.append(fp_str)
        # W= labels removed in 93mm spin — the 4 cloverleaves are visually
        # distinguishable by size (W=0.1 is tiny, W=1.0 is the largest).
        # Back-side silkscreen documents the W values per position.
        # Register all 4 cloverleaf contacts. `nets` is (dx, dy, net) per contact.
        for i, (dx, dy, net) in enumerate(nets, 1):
            vdp_targets.append((f"VDP_W{w}_{i}", net, x_c + dx, ROW_VDP + dy))

    # =====================================================================
    # LED DAISY CHAINS — N WL-SFCC LEDs in series via RED chain (A → K_R).
    # Replaces the original dummy-die ladders (we only have LED inventory,
    # not Si dummy dies). Each chain tests 2N bonds; failure of any one
    # opens the chain. K_G / K_B pads are bonded but isolated per-LED,
    # accessible via manual probing on the LED pad.
    # =====================================================================
    dc_box_y0 = 66.5
    dc_box_y1 = 74.5
    drawings.append(emit_silk_rect(3.5, dc_box_y0, BOARD_W - 3.5, dc_box_y1, width=0.15))
    drawings.append(emit_silk_text("LED DAISY CHAINS",
                                   BOARD_W/2, dc_box_y0 + 1.5,
                                   size=1.2, justify="center", bold=True))
    dc_layouts = [
        ( 6, 22.0, ROW_DAISY),
        (12, 70.0, ROW_DAISY),
    ]
    for n, x_c, y_c in dc_layouts:
        fp_list, in_net, out_net, chain_segs, chain_left_x, chain_right_x = \
            led_chain_footprints(f"DCL{n}", x_c, y_c, n, nm)
        fps.extend(fp_list)
        segments.extend(chain_segs)
        drawings.append(emit_silk_text(f"DC-R  N = {n}  LEDs", x_c, y_c - 2.0,
                                       size=1.0, justify="center", bold=True))
        # IN/OUT probe pads. Place them just outside the chain endpoints,
        # honouring board-edge margins.
        in_x = max(EDGE_MARGIN + PROBE_PAD/2 + 0.5, chain_left_x - 2.0)
        out_x = min(BOARD_W - EDGE_MARGIN - PROBE_PAD/2 - 0.5, chain_right_x + 2.0)
        probe_y = y_c + 3.5
        fps.append(probe_pad_footprint(f"PP_DCL{n}_IN", in_x, probe_y, in_net))
        fps.append(probe_pad_footprint(f"PP_DCL{n}_OUT", out_x, probe_y, out_net))
        # IN/OUT labels above the probe pads (below would clash with DC frame)
        drawings.append(emit_silk_text("IN", in_x, probe_y - 1.1, size=0.7, justify="center"))
        drawings.append(emit_silk_text("OUT", out_x, probe_y - 1.1, size=0.7, justify="center"))
        dc_targets.append((f"DCL{n}_IN", in_net, in_x, probe_y))
        dc_targets.append((f"DCL{n}_OUT", out_net, out_x, probe_y))
        # Route IN probe → LED_1.A pad. The chain trace row is at y_c - 0.4
        # (top row of LED footprints, where both A and K_R pads sit).
        chain_lead_y = y_c - 0.4
        segments.append(emit_track(in_x, probe_y, in_x, chain_lead_y, in_net))
        segments.append(emit_track(in_x, chain_lead_y, chain_left_x, chain_lead_y, in_net))
        segments.append(emit_track(out_x, probe_y, out_x, chain_lead_y, out_net))
        segments.append(emit_track(out_x, chain_lead_y, chain_right_x, chain_lead_y, out_net))

    # =====================================================================
    # LED ROW — 8 × Würth WL-SFCC 0404 super-flat RGB LEDs
    # Vertical packing (mm):
    #   y = 78.5 section title (placed ABOVE the section frame)
    #   y = 79.5 NTC row (0402 thermistors)
    #   y = 80.5 TH labels
    #   y = 82.5 LEDs
    #   y = 84.0 D-tags
    #   y = 85.5 probes
    # =====================================================================
    led_box_y0 = 75.5
    led_box_y1 = 82.5
    drawings.append(emit_silk_rect(3.5, led_box_y0, BOARD_W - 3.5, led_box_y1, width=0.15))
    # (WL-SFCC section title removed in the 95mm spin — there is not enough
    # vertical space for a legible title in the 1mm gap between DC frame end
    # (74.5) and LED frame start (75.5). The LED row is self-evident from
    # context, and the back-side silkscreen still names the part.)

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
            # Register probe pad for south-header routing
            led_probe_targets.append((f"PP_D{i+1}_{label}", net, px, py))

    # Common-anode bus on B.Cu — vias at each A probe + WIDE 0.8 mm trace
    # (low-inductance return path for pulsed-IV measurements).
    if a_probe_xs:
        for px in a_probe_xs:
            segments.append(
                f'(via (at {f(px)} {f(ROW_LED_PROBES)}) (size 0.6) (drill 0.3) '
                f'(layers "F.Cu" "B.Cu") {common_anode.ref()} (uuid "{uuid()}"))\n'
            )
        bus_y = ROW_LED_PROBES
        for i in range(len(a_probe_xs) - 1):
            segments.append(emit_track(
                a_probe_xs[i], bus_y, a_probe_xs[i + 1], bus_y,
                common_anode, layer="B.Cu", width=0.8,   # widened from 0.4
            ))

    # =====================================================================
    # NTC THERMISTORS — 4 × 0402 NTCs between LED pairs for V_F-TSP and
    # aging temp monitoring. Signal pin → per-NTC probe pad; common pin → GND.
    # =====================================================================
    gnd = nm.get("GND")
    ntc_y = 76.5           # inside LED frame top, above LEDs at 78.0
    ntc_xs = [20.0, 40.0, 60.0, 80.0]
    for i, nx in enumerate(ntc_xs, 1):
        ntc_net = nm.get(f"NTC{i}")
        fps.append(ntc_footprint(f"TH{i}", nx, ntc_y, ntc_net, gnd))
        # Probe pad to the LEFT (signal pin)
        ppx = nx - 2.5
        fps.append(probe_pad_footprint(f"PP_NTC{i}", ppx, ntc_y, ntc_net))
        segments.append(emit_track(nx - 0.5, ntc_y, ppx, ntc_y, ntc_net))
        # Via at GND pin (RIGHT side) → B.Cu GND pour
        segments.append(emit_via(nx + 0.5, ntc_y, gnd))
        # TH labels removed in 93mm spin — the NTC-to-LED gap is too tight
        # to fit a legible label without clipping the LED top-pad mask.
        # NTCs are visually identifiable as the only 0402 SMD components on
        # the board; back-side silkscreen names them for completeness.

    # =====================================================================
    # REFLOW TC PADS — 4 × 1 mm gold pads for soldering a fine-wire
    # thermocouple. Placed in the truly empty strip between sections at the
    # board edges, clear of all section frames and other copper.
    # Labels omitted — the four small isolated gold pads at the corners are
    # self-evident; identification is in the back-side silkscreen.
    # =====================================================================
    # TC pads placed inside section frames at the LEFT/RIGHT extremities
    # (clear of TLM/VDP/DC structures which all sit between x=10 and x=90).
    # Placed OUTSIDE the TLM / VDP section frames, in the strip between the
    # section frame and the decorative outer frame. Keeps them clear of the
    # DCL12_OUT north-route trace which runs at x=86.15.
    for i, (tx, ty) in enumerate([
        (2.5, 50.5), (2.5, 64.5),                        # left of TLM / VDP
        (BOARD_W - 2.5, 50.5), (BOARD_W - 2.5, 64.5),    # right of TLM / VDP
    ], 1):
        fps.append(tc_pad_footprint(f"TC{i}", tx, ty))

    # =====================================================================
    # GND PROBE PADS at the 4 corners (1.27 mm gold) + B.Cu GND POUR.
    # The pour ties all GND points together and gives a clean low-impedance
    # return for AC impedance / EIS / pulsed-IV measurements.
    # =====================================================================
    # Top corners only — bottom strip is now taken by the mm ruler.
    # B.Cu GND pour still gives return-path access everywhere.
    # GND probe X positions chosen to clear the new 32-pin north header
    # (pin 1 at x=7.13, pin 32 at x=85.87) and the DCL12_OUT route at x=85.87.
    for i, (gx, gy) in enumerate([(4.0, 16.0), (BOARD_W - 5.0, 16.0)], 1):
        fps.append(probe_pad_footprint(f"PP_GND{i}", gx, gy, gnd))
        # Via to B.Cu GND pour
        segments.append(emit_via(gx, gy, gnd))
        # GND label to the side (not above where outer silk frame sits)
        drawings.append(emit_silk_text("GND", gx + 2.5 if gx < 50 else gx - 2.5, gy,
                                       size=0.6, justify="center"))
    # Poured GND zone on B.Cu — covers most of the back, excludes the
    # area immediately around the LED_VCC bus (KiCad's auto-clearance
    # honours the 0.2 mm pad-clearance set in `connect_pads`).
    drawings.append(emit_zone(
        x1=EDGE_MARGIN, y1=EDGE_MARGIN,
        x2=BOARD_W - EDGE_MARGIN, y2=BOARD_H - EDGE_MARGIN,
        net=gnd, layer="B.Cu",
    ))

    # =====================================================================
    # SOUTH-HEADER LABEL + mm RULER
    # =====================================================================
    drawings.append(emit_silk_text("TIER-2 SOUTH  -  pre-wired to LEDs D1..D8  -  32 pins @ 2.54 mm",
                                   BOARD_W/2, ROW_SOUTH_HEADER + 2.5,
                                   size=0.65, justify="center"))

    # mm ruler: horizontal line with tick marks every 5mm and labels every 10mm.
    # Restored in the 93×93 spin (fits in the south header → bottom GND gap).
    ruler_x0 = (BOARD_W - 70) / 2
    ruler_x1 = ruler_x0 + 70
    ruler_y = ROW_RULER_Y
    drawings.append(emit_silk_line(ruler_x0, ruler_y, ruler_x1, ruler_y, width=0.18))
    for mm_val in range(0, 71, 5):
        x = ruler_x0 + mm_val
        tick = 0.8 if mm_val % 10 == 0 else 0.5
        drawings.append(emit_silk_line(x, ruler_y, x, ruler_y + tick, width=0.18))
        if mm_val % 10 == 0:
            drawings.append(emit_silk_text(str(mm_val), x, ruler_y + 1.5,
                                           size=0.6, justify="center"))

    # =====================================================================
    # TIER-2 HEADER PRE-WIRING (the heart of the v3 routing)
    # =====================================================================
    # All structures are placed by now. Build pin-assignment lists and route.
    pin_pitch = 2.54

    def north_pin_x(idx: int) -> float:
        return north_x0 + (idx - 1) * pin_pitch

    def south_pin_x(idx: int) -> float:
        return south_x0 + (idx - 1) * pin_pitch

    # Alias for backward compatibility with old code below
    pin_x = south_pin_x
    n_pins_per_row = n_pins_south

    # ------- SOUTH pin map: derived from south_pin_net() / south_pin_target_xy()
    # The same functions place the pin's pad NET (above) and now produce the
    # routing target. Net + target are guaranteed consistent.
    south_assignments = []
    for pin_idx in range(1, n_pins_per_row + 1):
        net = south_pin_net(pin_idx, nm)
        if net is None:
            continue
        tx, ty = south_pin_target_xy(pin_idx, BOARD_W, ROW_LED_PROBES)
        # Label is just the net name for silkscreen / docs.
        south_assignments.append((pin_idx, net.name, net, tx, ty))
    # ------- NORTH pin map: nearest-neighbour assignment.
    # For each pin (in pin-X order), greedily assign the nearest unassigned
    # target. Then per-pin fanout_y in target's zone with unique offset.
    # This minimises horizontal trace lengths and avoids the crossings that
    # appeared with monotonic sort-by-X.
    all_north_targets = list(tlm_targets + vdp_targets + dc_targets)
    available = list(all_north_targets)
    north_assignments = []
    for pin_idx in range(1, n_pins_north + 1):
        if not available:
            break
        px = north_pin_x(pin_idx)
        # Pick the nearest remaining target (by absolute X distance to pin)
        nearest_i = min(range(len(available)),
                        key=lambda i: abs(available[i][2] - px))
        label, net, tx, ty = available.pop(nearest_i)
        north_assignments.append((pin_idx, label, net, tx, ty))

    # ------- Route SOUTH: 4 horizontal "lanes" by probe role (A/KG/KB/KR).
    # Probe labels alternate per LED so consecutive pins are A,KG,KB,KR,
    # A,KG,KB,KR.... Putting each role on its own jog Y means within a
    # role-lane the horizontals are at unique X bands (10 mm LED pitch),
    # and between roles the vertical drops at each pin's X / target's X
    # never cross another role's horizontal.
    # Lane Ys MUST sit between the south header pad keepout (y > 84.15) and
    # the LED probe pad top (y < 81.635). 4 lanes at 0.4 mm spacing fit in
    # the 2.5 mm gap with comfortable margin both ways.
    role_to_lane_y = {"A": 83.6, "KG": 83.2, "KB": 82.8, "KR": 82.4}
    for idx, label, net, tx, ty in south_assignments:
        px = pin_x(idx)
        py = ROW_SOUTH_HEADER
        # The pin's role is uniquely determined by (pin_idx - 1) % 4:
        # 0=A, 1=KG, 2=KB, 3=KR — matches south_pin_net()'s mapping.
        role = ["A", "KG", "KB", "KR"][(idx - 1) % 4]
        jy = role_to_lane_y[role]
        segments.extend(route_short(px, py, tx, ty, jy, net))

    # ------- NORTH: 4 of 30 pins pre-wired to LED-chain endpoints; the
    # other 26 stay user-jumperable. Routing the 4 chain pins is tractable
    # (vs the abandoned 26-target v3 attempt) because chain endpoints are
    # large 1.27mm probe pads with whole-board F.Cu headroom around them.
    #
    # Each route: vertical down from header pin to the gap above the chain
    # row (y=68 for chain pins 1/10/22; y=17→jog for pin 30 which has to
    # detour around VDP W=0.1 at x=85), horizontal jog to the chain probe X,
    # then vertical down to the probe pad. All on F.Cu.
    chain_routes = [
        # (pin_idx, pin_x, target_x, target_y, route_y, label)
        ( 3, north_x0 +  2 * pin_pitch, 13.35, ROW_DAISY_PROBES, 68.0, "DCL6_IN"),
        (10, north_x0 +  9 * pin_pitch, 30.65, ROW_DAISY_PROBES, 68.0, "DCL6_OUT"),
        (19, north_x0 + 18 * pin_pitch, 53.85, ROW_DAISY_PROBES, 68.0, "DCL12_IN"),
        # Pin 32 has to detour: a straight vertical at pin 32's X (= 85.87 on
        # 93mm board) collides with VDP_W=0.1's right contact at (85.8, 61.5).
        # Route jogs right to x=86.15 just below the north header keepout,
        # then drops straight down to the chain probe.
        (32, north_x0 + 31 * pin_pitch, 86.15, ROW_DAISY_PROBES, None, "DCL12_OUT"),
    ]
    north_assignments = []
    for pin_idx, pin_x_val, tx, ty, jog_y, label in chain_routes:
        net = NORTH_CHAIN_PIN_NETS[pin_idx]
        if jog_y is not None:
            # 3-segment Manhattan route via mid-board horizontal jog at jog_y.
            segments.append(emit_track(pin_x_val, ROW_NORTH_HEADER, pin_x_val, jog_y, net))
            segments.append(emit_track(pin_x_val, jog_y, tx, jog_y, net))
            segments.append(emit_track(tx, jog_y, tx, ty, net))
        else:
            # Pin 32: detour via y=17 to clear VDP W=0.1 at (85.8, 61.5).
            detour_y = 17.0
            segments.append(emit_track(pin_x_val, ROW_NORTH_HEADER, pin_x_val, detour_y, net))
            segments.append(emit_track(pin_x_val, detour_y, tx, detour_y, net))
            segments.append(emit_track(tx, detour_y, tx, ty, net))
        # Silk circle around the pin pad — visual cue that this pin is
        # pre-wired (vs the 28 user-jumperable neighbours). Radius 1.1mm
        # sits 0.25mm outside the 1.7mm pad mask opening.
        drawings.append(emit_silk_circle(pin_x_val, ROW_NORTH_HEADER,
                                         radius=1.1, width=0.2))
        north_assignments.append((pin_idx, label, net, tx, ty))

    # ------- Silkscreen pin numbers (every 5th pin + endpoints) ---------
    # 2.54 mm pitch is too tight for per-pin labels. Major labels only at
    # 1, 5, 10, ..., 30. No tick marks (created overlap warnings).
    # North labels go BETWEEN title block (y=11) and header pads (y > 12.65).
    # South labels go BETWEEN header pads (y < 89.85) and the section caption.
    # North labels go ABOVE the header pads (y=11.85, in the gap between
    # title block bottom at y=11 and pin pad keepout top at y=12.65).
    # South labels go just BELOW the header pads (y=86.5, between pad keepout
    # bottom at y=85.85 and the south caption at y=87.5).
    for idx in range(1, n_pins_per_row + 1):
        px = pin_x(idx)
        if idx == 1 or idx == n_pins_per_row or idx % 5 == 0:
            drawings.append(emit_silk_text(
                str(idx), px, 11.85,
                size=0.65, justify="center", layer="F.SilkS",
            ))
            drawings.append(emit_silk_text(
                str(idx), px, 86.5,
                size=0.65, justify="center", layer="F.SilkS",
            ))

    # =====================================================================
    # BACK-SIDE silkscreen — title, fab notes, PINOUT, course info
    # =====================================================================
    _emit_back_side_silk(drawings, south_assignments, north_assignments)

    return fps, drawings, segments, nm


def _emit_back_side_silk(drawings: list, south_assignments=None, north_assignments=None) -> None:
    """B.SilkS — minimal, all text centered, no overflow.

    If south_assignments and north_assignments are provided (pre-wired
    Tier-2 header maps), replaces the SECTION KEY box with a PINOUT box
    listing pin index → net for each header row."""
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

    # ── PINOUT ────────────────────────────────────────────────────────
    # Two-column table: pin index → net assignment.
    # Box bottom must clear south-header through-holes at y=85 (95×95 board).
    key_y0 = 73.5
    key_y1 = 83.0
    drawings.append(emit_silk_rect(3.5, key_y0, BOARD_W - 3.5, key_y1, layer=L, width=0.15))
    drawings.append(emit_silk_text("TIER-2 SOUTH PINOUT", cx, key_y0 + 1.3,
                                   size=1.0, justify="center", bold=True, layer=L))
    if south_assignments:
        # Just SOUTH (NORTH is currently user-jumperable / unconnected).
        # Group consecutive pins by LED group: e.g. "Pin 1..4  D1 A,KG,KB,KR".
        led_groups = []     # [(led_num, [(pin, role)])]
        for idx, label, net, _, _ in south_assignments:
            # role from net name: LED_VCC → A; LEDn_Kx → Kx
            if net.name == "LED_VCC":
                role = "A"
                led_num = (idx - 1) // 4 + 1
            else:
                # name like LED3_KG → led 3, role KG
                m = net.name.split("_")
                led_num = int(m[0][3:])
                role = m[1]
            if led_groups and led_groups[-1][0] == led_num:
                led_groups[-1][1].append((idx, role))
            else:
                led_groups.append((led_num, [(idx, role)]))
        # Compact: 4-per-line for LED rows, 2 footer lines, all big enough.
        lines = []
        compact = []
        for led_num, pins in led_groups:
            compact.append(f"{pins[0][0]:>2}-{pins[-1][0]:<2} D{led_num}")
        # Pack 4 LED-groups per silk line
        for i in range(0, len(compact), 4):
            lines.append("   ".join(compact[i:i+4]))
        lines.append("each group: A, KG, KB, KR  (A = LED_VCC)")
        lines.append("NORTH row: user-jumperable")
        for i, ln in enumerate(lines):
            y = key_y0 + 3.5 + i * 1.5
            if y > key_y1 - 1.0:
                break
            drawings.append(emit_silk_text(ln, cx, y,
                                           size=0.8, justify="center", layer=L))
    else:
        # Fallback: original section-key list
        for i, ln in enumerate([
            "DoE  -  6 x 6 isolated bond pads",
            "TLM  -  contact-resistivity ladder",
            "VDP  -  Van der Pauw cloverleaf",
            "DC-R  -  LED chain N in series (RED)",
            "D1..D8  +  PP-*  -  LEDs and probes",
        ]):
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
