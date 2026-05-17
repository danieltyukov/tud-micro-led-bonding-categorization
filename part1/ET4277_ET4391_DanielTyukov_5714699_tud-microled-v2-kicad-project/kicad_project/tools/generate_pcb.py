#!/usr/bin/env python3
"""
Procedurally generate tud-microled-v2.kicad_pcb.

Run with the Würth-deps venv Python:
    ~/tools/KiCAD-MCP-Server/.venv/bin/python new-pcb/tools/generate_pcb.py

The script wipes the existing board (footprints, tracks, zones, drawings)
and rebuilds it from scratch from the constants below. Re-runnable.
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[2]
BOARD_PATH = REPO / "new-pcb" / "tud-microled-v2.kicad_pcb"
LIB_DOE = REPO / "new-pcb" / "library" / "footprints" / "BondPads_DoE.pretty"
LIB_TEST = REPO / "new-pcb" / "library" / "footprints" / "TestStructures.pretty"
LIB_WURTH = REPO / "new-pcb" / "library" / "footprints" / "LED_SMD_Wurth.pretty"

# ---------------------------------------------------------------------------
# Board geometry / design rules (mm)
# ---------------------------------------------------------------------------

BOARD_W = 100.0
BOARD_H = 80.0
EDGE_MARGIN = 2.5  # keep clear of board edge

# Probe pads (Tier 1)
PROBE_PAD_SIZE = 1.27
PROBE_PAD_PITCH = 2.54  # centre-to-centre

# Trace defaults
TRACE_W_SIG = 0.20
TRACE_W_POWER = 0.40
CLEAR = 0.15

# DoE bond-pad array — 6 × 6 (= 36 sites) for v2.0; can be enlarged for v2.1
DOE_COLS = 6
DOE_ROWS = 6
DOE_PITCH = 3.5  # mm centre-to-centre (room for routing between sites)
DOE_ORIGIN_X = 14.0
DOE_ORIGIN_Y = 16.0

# Layout regions (mm) — vertically separated, no row collides with another
ROW_TOP_LABEL = 4.0           # title + fiducials at very top
ROW_NORTH_HEADER = 6.5        # 2.54mm header row
DOE_NORTH_PROBE_Y = [9.0, 11.0, 13.0]   # R1, R2, R3 probes (top half)
ROW_DOE_ARRAY = 16.0          # DoE bond pads start here (6 rows × 3.5 = 17.5mm → ends y≈34)
DOE_SOUTH_PROBE_Y = [36.5, 38.5, 40.5]  # R4, R5, R6 probes (bottom half)
ROW_TLM = 45.0                # TLM ladders
ROW_TLM_PROBES = 49.5
ROW_VDP = 53.5
ROW_VDP_PROBES = 57.0
ROW_DAISY = 61.0
ROW_DAISY_PROBES = 65.0
ROW_LED = 69.0
ROW_LED_PROBES = 72.0
ROW_SOUTH_HEADER = 75.5
ROW_RULER = 78.0

# Bond pad reference geometry
BOND_PAD_SIZE = 1.0  # main pad
MINI_PAD_SIZE = 0.5  # corner mini-pad
MINI_PAD_OFFSET = 0.6  # centre-to-centre from main pad centre

# Daisy chains, VDP, TLM, LED row positions — see place_*() functions below.

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def vmm(x: float, y: float) -> VECTOR2I:
    """mm -> KiCad VECTOR2I in nanometres."""
    return VECTOR2I(FromMM(x), FromMM(y))


def smm(x: float, y: float):
    """mm -> wxSize-equivalent (VECTOR2I in pcbnew API ≥7)."""
    return VECTOR2I(FromMM(x), FromMM(y))


_net_cache: dict = {}


def get_or_create_net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    """Idempotent net lookup. Caches Python-side since GetNetsByName() in the
    SWIG flavour ships with KiCad 9 returns SwigPyObject in some configurations."""
    if name in _net_cache:
        return _net_cache[name]
    # Try direct lookup first
    try:
        net = board.FindNet(name)
        if net is not None and net.GetNetname() == name:
            _net_cache[name] = net
            return net
    except Exception:
        pass
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    _net_cache[name] = net
    return net


def add_smd_pad(
    fp: pcbnew.FOOTPRINT,
    number: str,
    shape,
    x: float,
    y: float,
    w: float,
    h: float,
    layers=None,
    rotation: float = 0.0,
    roundrect_ratio: float | None = None,
) -> pcbnew.PAD:
    """Add an SMD pad with LOCAL (x, y) offset from the footprint's origin (mm)."""
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(shape)
    pad.SetSize(smm(w, h))
    if layers is None:
        layers = pcbnew.LSET()
        layers.AddLayer(pcbnew.F_Cu)
        layers.AddLayer(pcbnew.F_Mask)
        layers.AddLayer(pcbnew.F_Paste)
    pad.SetLayerSet(layers)
    if rotation:
        pad.SetOrientationDegrees(rotation)
    if roundrect_ratio is not None and shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        pad.SetRoundRectRadiusRatio(roundrect_ratio)
    fp.Add(pad)
    # Set the absolute position AFTER attaching to the footprint, so that
    # KiCad back-calculates the local pos0 correctly.
    fp_pos = fp.GetPosition()
    pad.SetPosition(VECTOR2I(fp_pos.x + FromMM(x), fp_pos.y + FromMM(y)))
    return pad


def make_footprint(board: pcbnew.BOARD, name: str, x: float, y: float, layer=None) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(name)
    fp.SetValue(name)
    fp.SetPosition(vmm(x, y))
    if layer is not None:
        fp.SetLayer(layer)
    # Hide silkscreen text — research convention: clean optical-metrology surface.
    # Reference()/Value() in pcbnew 9 returns PCB_FIELD; in some SWIG flavours
    # it surfaces as opaque SwigPyObject. Guard defensively.
    try:
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
    except AttributeError:
        for fld in fp.GetFields():
            try:
                fld.SetVisible(False)
            except Exception:
                pass
    board.Add(fp)
    return fp


def add_silkscreen_text(board: pcbnew.BOARD, text: str, x: float, y: float, size: float = 1.0, layer=None) -> None:
    if layer is None:
        layer = pcbnew.F_SilkS
    # Enforce KiCad/Eurocircuits silkscreen minima: 0.8 mm height, 0.15 mm thickness
    size = max(0.8, size)
    thickness = max(0.15, size * 0.15)
    txt = pcbnew.PCB_TEXT(board)
    txt.SetText(text)
    txt.SetPosition(vmm(x, y))
    txt.SetLayer(layer)
    txt.SetTextSize(smm(size, size))
    txt.SetTextThickness(FromMM(thickness))
    board.Add(txt)


def add_track(board: pcbnew.BOARD, x1: float, y1: float, x2: float, y2: float, net, width: float = TRACE_W_SIG, layer=None) -> None:
    if layer is None:
        layer = pcbnew.F_Cu
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(vmm(x1, y1))
    t.SetEnd(vmm(x2, y2))
    t.SetWidth(FromMM(width))
    t.SetLayer(layer)
    if net is not None:
        t.SetNet(net)
    board.Add(t)


def add_via(board: pcbnew.BOARD, x: float, y: float, net, diameter: float = 0.6, drill: float = 0.3) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(vmm(x, y))
    via.SetWidth(FromMM(diameter))
    via.SetDrill(FromMM(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    if net is not None:
        via.SetNet(net)
    board.Add(via)


# ---------------------------------------------------------------------------
# Footprint generators (placed directly on the board, no .kicad_mod file
# because everything here is one-off / parametric and the .pretty library
# would just be a snapshot of the script's output)
# ---------------------------------------------------------------------------

def bond_pad_site(
    board: pcbnew.BOARD,
    site_id: str,
    cx: float,
    cy: float,
    geometry: str,        # "plain", "rounded", "circle", "cross"
    radius_um: int = 0,   # corner radius for "rounded"
    mini_pads: bool = False,
    net_p1=None,          # main-pad net (Force-High)
    net_p2=None,          # cathode-side net (Force-Low)
) -> pcbnew.FOOTPRINT:
    """Place a bond pad site + its 2 outboard 1.27mm probe pads (FH/FL)."""
    fp = make_footprint(board, f"BP_{site_id}", cx, cy)

    if geometry == "plain":
        add_smd_pad(fp, "1", pcbnew.PAD_SHAPE_RECT, 0, 0, BOND_PAD_SIZE, BOND_PAD_SIZE)
    elif geometry == "rounded":
        ratio = (radius_um / 1000.0) / BOND_PAD_SIZE  # ratio of radius to pad size
        ratio = min(0.49, max(0.01, ratio))
        add_smd_pad(
            fp, "1", pcbnew.PAD_SHAPE_ROUNDRECT, 0, 0,
            BOND_PAD_SIZE, BOND_PAD_SIZE,
            roundrect_ratio=ratio,
        )
    elif geometry == "circle":
        add_smd_pad(fp, "1", pcbnew.PAD_SHAPE_CIRCLE, 0, 0, BOND_PAD_SIZE, BOND_PAD_SIZE)
    elif geometry == "cross":
        # 1×1 mm envelope, 0.2mm arm width
        add_smd_pad(fp, "1", pcbnew.PAD_SHAPE_RECT, 0, 0, 1.0, 0.2)
        add_smd_pad(fp, "1", pcbnew.PAD_SHAPE_RECT, 0, 0, 0.2, 1.0)
    else:
        raise ValueError(geometry)

    if mini_pads:
        for dx, dy in [(-MINI_PAD_OFFSET, -MINI_PAD_OFFSET),
                       ( MINI_PAD_OFFSET, -MINI_PAD_OFFSET),
                       (-MINI_PAD_OFFSET,  MINI_PAD_OFFSET),
                       ( MINI_PAD_OFFSET,  MINI_PAD_OFFSET)]:
            add_smd_pad(fp, "1", pcbnew.PAD_SHAPE_RECT, dx, dy, MINI_PAD_SIZE, MINI_PAD_SIZE)

    # Connect the bond pad to net P1
    if net_p1 is not None:
        for pad in fp.Pads():
            if pad.GetNumber() == "1":
                pad.SetNet(net_p1)

    return fp


def add_probe_pad(
    board: pcbnew.BOARD,
    name: str,
    x: float,
    y: float,
    net=None,
    silkscreen_label: str | None = None,
) -> pcbnew.FOOTPRINT:
    fp = make_footprint(board, name, x, y)
    pad = add_smd_pad(fp, "1", pcbnew.PAD_SHAPE_RECT, 0, 0, PROBE_PAD_SIZE, PROBE_PAD_SIZE)
    if net is not None:
        pad.SetNet(net)
    if silkscreen_label:
        add_silkscreen_text(board, silkscreen_label, x, y - PROBE_PAD_SIZE/2 - 0.5, size=0.7)
    return fp


def add_th_header_pin(
    board: pcbnew.BOARD,
    name: str,
    x: float,
    y: float,
    net=None,
    drill: float = 1.0,
    pad_diameter: float = 1.7,
) -> pcbnew.FOOTPRINT:
    fp = make_footprint(board, name, x, y)
    pad = pcbnew.PAD(fp)
    pad.SetNumber("1")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(smm(pad_diameter, pad_diameter))
    pad.SetDrillSize(smm(drill, drill))
    layers = pcbnew.LSET()
    for L in [pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.F_Mask, pcbnew.B_Mask]:
        layers.AddLayer(L)
    pad.SetLayerSet(layers)
    if net is not None:
        pad.SetNet(net)
    fp.Add(pad)
    fp_pos = fp.GetPosition()
    pad.SetPosition(fp_pos)  # pad sits at footprint origin
    return fp


def add_fiducial(board: pcbnew.BOARD, name: str, x: float, y: float, copper: float = 1.0, mask: float = 2.0) -> pcbnew.FOOTPRINT:
    fp = make_footprint(board, name, x, y)
    pad = pcbnew.PAD(fp)
    pad.SetNumber("")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(smm(copper, copper))
    layers = pcbnew.LSET()
    layers.AddLayer(pcbnew.F_Cu)
    layers.AddLayer(pcbnew.F_Mask)
    pad.SetLayerSet(layers)
    pad.SetLocalSolderMaskMargin(FromMM((mask - copper) / 2))
    fp.Add(pad)
    fp_pos = fp.GetPosition()
    pad.SetPosition(fp_pos)
    return fp


def add_vdp(board: pcbnew.BOARD, ref: str, cx: float, cy: float, arm_w: float, arm_len: float | None = None) -> tuple:
    """Place a 4-contact Van der Pauw cloverleaf and return the 4 pad-centre nets.
    arm_len is the centre-to-centre offset; auto-scales to leave > 0.3 mm gap."""
    if arm_len is None:
        arm_len = max(0.8, arm_w + 0.4)  # ensure ~0.3 mm corner-to-corner gap
    fp = make_footprint(board, ref, cx, cy)
    nets = []
    contacts = [
        (-arm_len, 0, 0),
        ( arm_len, 0, 0),
        (0, -arm_len, 90),
        (0,  arm_len, 90),
    ]
    for i, (dx, dy, rot) in enumerate(contacts, 1):
        net = get_or_create_net(board, f"{ref}_{i}")
        nets.append((dx, dy, net))
        pad = add_smd_pad(fp, str(i), pcbnew.PAD_SHAPE_RECT, dx, dy, arm_w, arm_w, rotation=rot)
        pad.SetNet(net)
    return tuple(nets)


def add_tlm_bank(
    board: pcbnew.BOARD,
    ref: str,
    cx: float,
    cy: float,
    finger_w: float,
    spacings_um: list[int],
    finger_len: float = 4.0,
) -> list:
    """Place a TLM ladder with `len(spacings)+1` fingers and return the per-finger nets."""
    finger_centres = [-finger_w / 2]
    for s_um in spacings_um:
        finger_centres.append(finger_centres[-1] + finger_w + s_um / 1000.0)
    width_total = finger_centres[-1] - finger_centres[0] + finger_w
    x0 = cx - width_total / 2
    fp = make_footprint(board, ref, cx, cy)
    nets = []
    for i, fc in enumerate(finger_centres, 1):
        net = get_or_create_net(board, f"{ref}_F{i}")
        nets.append((x0 + fc - cx, 0, net))
        pad = add_smd_pad(
            fp, str(i), pcbnew.PAD_SHAPE_RECT,
            x0 + fc - cx, 0, finger_w, finger_len,
        )
        pad.SetNet(net)
    return nets


def add_daisy_chain(
    board: pcbnew.BOARD,
    ref: str,
    cx: float,
    cy: float,
    n_dies: int,
    pitch: float = 1.4,
) -> tuple:
    """A linear row of `2*n_dies` 1×1 mm bond pads. Adjacent pads alternate
    between 'this die's top' and 'next die's bottom' — the dies bridge them.

    Returns (input_net, output_net) for chain measurement.
    """
    fp = make_footprint(board, ref, cx, cy)
    total_pads = 2 * n_dies + 2  # +2 for end caps that pad-out to probe pads
    width = (total_pads - 1) * pitch
    x0 = -width / 2
    in_net = get_or_create_net(board, f"{ref}_IN")
    out_net = get_or_create_net(board, f"{ref}_OUT")
    # Pad 0 (input), pads 1..2n connected in pairs by dies, pad 2n+1 (output)
    for i in range(total_pads):
        pad = add_smd_pad(
            fp, str(i + 1), pcbnew.PAD_SHAPE_RECT,
            x0 + i * pitch, 0, BOND_PAD_SIZE, BOND_PAD_SIZE,
        )
        if i == 0:
            pad.SetNet(in_net)
        elif i == total_pads - 1:
            pad.SetNet(out_net)
        else:
            # Each interior pad belongs to a unique node along the chain.
            net = get_or_create_net(board, f"{ref}_N{i}")
            pad.SetNet(net)
    return in_net, out_net


# ---------------------------------------------------------------------------
# Würth LED placement
# ---------------------------------------------------------------------------

def load_wurth_footprint() -> pcbnew.FOOTPRINT | None:
    """Read our vendored Würth WL-SFCC 0404 superflat footprint."""
    libpath = str(LIB_WURTH)
    try:
        return pcbnew.FootprintLoad(libpath, "D_Wurth_WL-SFCC-0404superflat")
    except Exception as e:
        print(f"WARN: could not load Würth footprint: {e}", file=sys.stderr)
        return None


def place_led(board: pcbnew.BOARD, ref: str, x: float, y: float, anode_net, k_r_net, k_b_net, k_g_net) -> pcbnew.FOOTPRINT:
    src = load_wurth_footprint()
    if src is None:
        # Fallback: 4 generic pads matching the recommended land
        fp = make_footprint(board, ref, x, y)
        pad_positions = [
            ("1", -0.4, -0.4, anode_net),  # + (common anode)
            ("2",  0.4, -0.4, k_r_net),     # -R
            ("3",  0.4,  0.4, k_b_net),     # -B
            ("4", -0.4,  0.4, k_g_net),     # -G
        ]
        for n, dx, dy, net in pad_positions:
            pad = add_smd_pad(fp, n, pcbnew.PAD_SHAPE_RECT, dx, dy, 0.4, 0.4)
            pad.SetNet(net)
        return fp

    fp = pcbnew.FOOTPRINT(src)
    fp.SetReference(ref)
    fp.SetValue("WL-SFCC")
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    fp.SetPosition(vmm(x, y))
    board.Add(fp)
    nets_by_pin = {"1": anode_net, "2": k_r_net, "3": k_b_net, "4": k_g_net}
    for pad in fp.Pads():
        n = pad.GetNumber()
        if n in nets_by_pin and nets_by_pin[n] is not None:
            pad.SetNet(nets_by_pin[n])
    return fp


# ---------------------------------------------------------------------------
# Board placement
# ---------------------------------------------------------------------------

def wipe_board(board: pcbnew.BOARD) -> None:
    """Remove everything the generator owns (footprints, tracks, zones, drawings)
    so the script is idempotent."""
    for fp in list(board.GetFootprints()):
        board.Remove(fp)
    try:
        for t in [t for t in board.Tracks()]:
            board.Remove(t)
    except TypeError:
        pass
    for zone in list(board.Zones()):
        board.Remove(zone)
    try:
        drawings = [d for d in board.Drawings()]
    except TypeError:
        drawings = []
    for d in drawings:
        if d.GetLayer() != pcbnew.Edge_Cuts:
            board.Remove(d)


def place_doe_array(board: pcbnew.BOARD) -> dict[str, tuple]:
    """36-site DoE bond-pad array (6×6).

    Geometry varies by row band:
       row 0-1: plain square, no minis (control)
       row 2-3: plain square + 4 corner minis
       row 4-5: rounded variants (R=50/100/200) + minis
    """
    out = {}
    array_total_w = (DOE_COLS - 1) * DOE_PITCH
    centre_offset_x = (BOARD_W - array_total_w) / 2 - DOE_ORIGIN_X + 1
    for r in range(DOE_ROWS):
        for c in range(DOE_COLS):
            cx = DOE_ORIGIN_X + c * DOE_PITCH + centre_offset_x
            cy = DOE_ORIGIN_Y + r * DOE_PITCH
            site_id = f"R{r+1}C{c+1}"
            if r < 2:
                geom, R, minis = "plain", 0, False
            elif r < 4:
                geom, R, minis = "plain", 0, True
            else:
                radii = [50, 100, 200, 50, 100, 200]
                geom, R, minis = "rounded", radii[c], True
            net = get_or_create_net(board, f"BP_{site_id}_P1")
            fp = bond_pad_site(board, site_id, cx, cy, geom, R, minis, net_p1=net)
            out[site_id] = (fp, net, geom, R, minis, cx, cy)
    return out


def place_doe_probe_pads(board: pcbnew.BOARD, doe_sites: dict) -> None:
    """One 1.27 mm probe pad per DoE site, with vertical stagger so the 3 rows
    in each half-strip get unique Y coordinates."""
    for site_id, (fp, net, geom, R, minis, cx, cy) in sorted(doe_sites.items()):
        r = int(site_id.split("R")[1].split("C")[0])
        if r <= 3:
            y = DOE_NORTH_PROBE_Y[r - 1]
        else:
            y = DOE_SOUTH_PROBE_Y[r - 4]
        add_probe_pad(board, f"PP_{site_id}", cx, y, net=net)


def place_tlm_ladders(board: pcbnew.BOARD) -> list:
    """3 TLM ladders centered at y=ROW_TLM."""
    spacings = [5, 10, 20, 50, 100, 200]  # µm
    widths = [0.25, 0.5, 1.0]              # mm
    y = ROW_TLM
    x_centres = [22.0, 50.0, 78.0]
    out = []
    for x_c, w in zip(x_centres, widths):
        nets = add_tlm_bank(board, f"TLM_W{w}", x_c, y, w, spacings, finger_len=2.5)
        add_silkscreen_text(board, f"TLM W={w}mm", x_c - 6, y - 2.2, size=1.0)
        # End-finger probe pads
        for idx, side in [(0, "A"), (-1, "B")]:
            dx, dy, net = nets[idx]
            add_probe_pad(board, f"PP_TLM_W{w}_{side}",
                          x_c + dx, ROW_TLM_PROBES, net=net)
        out.append((w, nets))
    return out


def place_vdps(board: pcbnew.BOARD) -> list:
    """4 Van der Pauw cloverleaves at y=ROW_VDP."""
    widths = [1.0, 0.5, 0.25, 0.1]
    x_centres = [15.0, 38.0, 62.0, 85.0]
    y = ROW_VDP
    out = []
    for x_c, w in zip(x_centres, widths):
        nets = add_vdp(board, f"VDP_W{w}", x_c, y, arm_w=w, arm_len=1.0)
        add_silkscreen_text(board, f"VDP W={w}", x_c - 4, y - 2.2, size=1.0)
        for i, (dx, dy, net) in enumerate(nets, 1):
            add_probe_pad(board, f"PP_VDP_W{w}_{i}",
                          x_c + dx * 2.5, ROW_VDP_PROBES + dy * 1.0, net=net)
        out.append((w, nets))
    return out


def place_daisy_chains(board: pcbnew.BOARD) -> list:
    """3 daisy chains at y=ROW_DAISY. Pitch 1.8 mm → 0.8 mm gap → safe mask web,
    but still under the 2.0 mm pitch limit where a 1×1 mm die can no longer bridge."""
    sizes = [6, 12, 24]
    pitch = 1.8
    out = []
    y = ROW_DAISY
    x_centres = [15.0, 40.0, 75.0]
    for x_c, n in zip(x_centres, sizes):
        in_net, out_net = add_daisy_chain(board, f"DC_N{n}", x_c, y, n_dies=n, pitch=pitch)
        add_silkscreen_text(board, f"DC N={n}", x_c - 3, y - 2.2, size=1.0)
        chain_w = (2 * n + 1) * pitch
        add_probe_pad(board, f"PP_DC{n}_IN", x_c - chain_w/2 - 2.5, ROW_DAISY_PROBES, net=in_net)
        add_probe_pad(board, f"PP_DC{n}_OUT", x_c + chain_w/2 + 2.5, ROW_DAISY_PROBES, net=out_net)
        out.append((n, in_net, out_net))
    return out


def place_leds(board: pcbnew.BOARD) -> list:
    """8 Würth WL-SFCC RGB LEDs at y=ROW_LED."""
    y = ROW_LED
    pitch = 10.0
    x0 = (BOARD_W - 7 * pitch) / 2
    out = []
    common_anode = get_or_create_net(board, "LED_VCC")
    for i in range(8):
        x = x0 + i * pitch
        net_r = get_or_create_net(board, f"LED{i+1}_KR")
        net_b = get_or_create_net(board, f"LED{i+1}_KB")
        net_g = get_or_create_net(board, f"LED{i+1}_KG")
        place_led(board, f"D{i+1}", x, y, common_anode, net_r, net_b, net_g)
        add_silkscreen_text(board, f"D{i+1}", x - 1.0, y - 2.0, size=1.0)
        # Each LED gets its own probe-pad cluster on the row below it
        add_probe_pad(board, f"PP_D{i+1}_A", x - 3, ROW_LED_PROBES, net=common_anode)
        add_probe_pad(board, f"PP_D{i+1}_KR", x - 1, ROW_LED_PROBES, net=net_r)
        add_probe_pad(board, f"PP_D{i+1}_KB", x + 1, ROW_LED_PROBES, net=net_b)
        add_probe_pad(board, f"PP_D{i+1}_KG", x + 3, ROW_LED_PROBES, net=net_g)
        out.append((i+1, common_anode, net_r, net_b, net_g))
    return out


def place_headers(board: pcbnew.BOARD) -> None:
    """Two 30-pin 2.54 mm headers along N and S edges (Tier-2 access)."""
    n_pins = 30
    pitch = 2.54
    total_w = (n_pins - 1) * pitch
    x0 = (BOARD_W - total_w) / 2
    for i in range(n_pins):
        x = x0 + i * pitch
        add_th_header_pin(board, f"H_N_{i+1}", x, ROW_NORTH_HEADER)
        add_th_header_pin(board, f"H_S_{i+1}", x, ROW_SOUTH_HEADER)


def place_fiducials(board: pcbnew.BOARD) -> None:
    add_fiducial(board, "FID1", 4.0, 4.0)              # NW
    add_fiducial(board, "FID2", BOARD_W - 4.0, 4.0)    # NE
    add_fiducial(board, "FID3", 4.0, BOARD_H - 4.0)    # SW
    add_fiducial(board, "FID4", BOARD_W - 4.0, BOARD_H - 4.0)  # SE
    # Asymmetric "L" mark at NW so orientation is unambiguous
    add_silkscreen_text(board, "L", 7.0, 4.0, size=1.5)


def place_silkscreen_metadata(board: pcbnew.BOARD) -> None:
    add_silkscreen_text(board, "TUD micro-LED v2", BOARD_W/2 - 15, ROW_TOP_LABEL, size=1.5)
    add_silkscreen_text(board, "ECTM + ITEC", BOARD_W/2 - 9, ROW_TOP_LABEL + 1.8, size=1.0)
    add_silkscreen_text(board, "DoE bond-pads (6x6)",
                        BOARD_W/2 - 13, ROW_DOE_ARRAY - 2, size=1.0)
    # mm ruler along south edge (every 10 mm label + every 5 mm tick)
    ruler_x0 = (BOARD_W - 80) / 2
    for mm_val in range(0, 81, 10):
        x = ruler_x0 + mm_val
        add_silkscreen_text(board, str(mm_val), x - 1.5, ROW_RULER, size=0.8)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print(f"Loading board: {BOARD_PATH}")
    board = pcbnew.LoadBoard(str(BOARD_PATH))

    print("Wiping existing footprints / tracks / zones (idempotent run)")
    wipe_board(board)

    print("Placing fiducials + silkscreen metadata")
    place_fiducials(board)
    place_silkscreen_metadata(board)

    print("Placing 2.54 mm pin-header rows (Tier-2 access)")
    place_headers(board)

    print(f"Placing DoE bond-pad array ({DOE_ROWS}×{DOE_COLS} = {DOE_ROWS*DOE_COLS} sites)")
    doe = place_doe_array(board)
    place_doe_probe_pads(board, doe)

    print("Placing TLM ladders")
    place_tlm_ladders(board)

    print("Placing VDP cloverleaves")
    place_vdps(board)

    print("Placing daisy chains N=6/12/24")
    place_daisy_chains(board)

    print("Placing 8 × Würth WL-SFCC RGB LEDs")
    place_leds(board)

    print("Saving board")
    pcbnew.Refresh()
    pcbnew.SaveBoard(str(BOARD_PATH), board)

    print(f"Footprints placed: {len(board.GetFootprints())}")
    print(f"Nets defined:      {board.GetNetCount()}")
    print(f"Board file:        {BOARD_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
