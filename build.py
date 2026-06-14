#!/usr/bin/env python3
"""
Build Clearwater Energy Power System HMI — Ignition Perspective.
Layout guide: flex-first, grow/shrink/basis on every flex child, component.onActionPerformed nav.
Coord kept ONLY for the SLD (overlapping fixed-geometry electrical diagram).
"""
import json, os, shutil, subprocess

SRC  = os.path.dirname(os.path.abspath(__file__))
DEST = "/usr/local/ignition/data/projects/power-hmi"

# ── Palette ───────────────────────────────────────────────────────────────────
BG     = "#060B18"
SURF   = "#0D1526"
SURF2  = "#111E34"
BORDER = "#1B2B4B"
BLUE   = "#4F8EF7"
GREEN  = "#22C55E"
YELLOW = "#EAB308"
RED    = "#EF4444"
VIOLET = "#A78BFA"
CYAN   = "#06B6D4"
TEXT   = "#E2E8F0"
MUTED  = "#64748B"
MUTED2 = "#94A3B8"

F  = "'Inter', 'Barlow', 'Helvetica Neue', Arial, sans-serif"
FM = "'JetBrains Mono', 'Courier New', monospace"

# ── Core helpers ──────────────────────────────────────────────────────────────
def _pos(grow=None, shrink=None, basis=None):
    d = {}
    if grow   is not None: d["grow"]   = grow
    if shrink is not None: d["shrink"] = shrink
    if basis  is not None:
        d["basis"] = basis
    elif grow is not None or shrink is not None:
        d["basis"] = "auto"
    return d

def flex(children, direction="column", justify="flex-start", align="stretch",
         grow=None, shrink=None, basis=None, gap=None, pad=None,
         bg=None, border=None, radius=None, wrap=None, name="flex",
         overflow=None, min_height=None, **kw_style):
    style = {}
    if gap:        style["gap"]             = gap
    if pad:        style["padding"]         = pad
    if bg:         style["backgroundColor"] = bg
    if border:     style["border"]          = border
    if radius:     style["borderRadius"]    = radius
    if overflow:   style["overflow"]        = overflow
    if min_height: style["minHeight"]       = min_height
    style.update(kw_style)
    props = {"direction": direction, "justify": justify,
             "alignItems": align, "style": style}
    if wrap: props["wrap"] = wrap
    comp = {"type": "ia.container.flex", "meta": {"name": name},
            "props": props, "children": children}
    pos = _pos(grow, shrink, basis)
    if pos: comp["position"] = pos
    return comp

def lbl(text, sz="0.875rem", col=TEXT, bold=False, track="normal", upper=False,
        align="left", font=F, grow=None, shrink=None, basis=None, name="lbl",
        **kw_style):
    style = {"color": col, "fontSize": sz, "fontFamily": font,
             "textAlign": align, "letterSpacing": track}
    if bold:  style["fontWeight"]    = "700"
    if upper: style["textTransform"] = "uppercase"
    style.update(kw_style)
    comp = {"type": "ia.display.label", "meta": {"name": name},
            "props": {"text": text, "style": style}}
    pos = _pos(grow, shrink, basis)
    if pos: comp["position"] = pos
    return comp

def btn(text, page=None, bg=SURF2, col=TEXT, border_col=None,
        sz="0.75rem", radius="8px", track="normal",
        grow=0, shrink=0, basis="auto", name="btn",
        pad="0.4375rem 1rem"):
    bc = border_col or BORDER
    style = {"backgroundColor": bg, "color": col, "fontSize": sz,
             "fontFamily": F, "letterSpacing": track,
             "border": f"1px solid {bc}", "borderRadius": radius,
             "cursor": "pointer", "padding": pad}
    comp = {"type": "ia.input.button", "meta": {"name": name},
            "props": {"text": text, "style": style},
            "position": _pos(grow, shrink, basis)}
    if page:
        comp["events"] = {"component": {"onActionPerformed": {
            "type": "script", "scope": "G",
            "config": {"script": f"system.perspective.navigate(page='{page}')"}
        }}}
    return comp

def spacer():
    return lbl("", grow=1, shrink=1, basis="0%")

def nav_embed():
    return {"type":"ia.display.view","meta":{"name":"Nav"},
            "props":{"path":"Components/Nav","style":{}},
            "position":_pos(0,0,"56px")}

def kpi_card(title, value, unit, col, sub=""):
    return flex([
        lbl(title, sz="0.625rem", col=MUTED2, bold=True, track="1.5px",
            upper=True, grow=0, shrink=0),
        flex([
            lbl(value, sz="1.875rem", col=col, bold=True, font=FM, grow=0, shrink=0),
            lbl(unit,  sz="0.875rem", col=MUTED2, grow=0, shrink=0),
        ], direction="row", align="baseline", gap="0.375rem", grow=0, shrink=0),
        lbl(sub, sz="0.6875rem", col=MUTED, grow=0, shrink=0),
    ], direction="column", gap="0.25rem",
       grow=1, shrink=1, basis="0%",
       bg=SURF, pad="1rem 1.25rem",
       border=f"1px solid {BORDER}", radius="12px")

def section_hdr(title, sub=""):
    return flex([
        lbl(title, sz="1.375rem", col=TEXT, bold=True, grow=0, shrink=0),
        lbl(sub,   sz="0.75rem", col=MUTED, grow=0, shrink=0) if sub else spacer(),
    ], direction="column", gap="2px", grow=0, shrink=0)

# ── resource.json + write helpers ─────────────────────────────────────────────
def resource(files):
    return {"scope": "G", "version": 1, "restricted": False, "overridable": True,
            "files": files,
            "attributes": {"lastModification": {
                "actor": "admin", "timestamp": "2026-06-14T00:00:00Z"}}}

def write(rel, obj):
    full = os.path.join(SRC, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def view_json(root_comp, width=1440, height=900):
    return {"custom": {}, "params": {},
            "props": {"defaultSize": {"width": width, "height": height}},
            "root": root_comp}

def write_view(name, root_comp, width=1440, height=900):
    base = f"com.inductiveautomation.perspective/views/{name}"
    write(f"{base}/view.json",     view_json(root_comp, width, height))
    write(f"{base}/resource.json", resource(["view.json"]))
    print(f"  {name}")

# ═══════════════════════════════════════════════════════════════════════════════
#  NAV COMPONENT
# ═══════════════════════════════════════════════════════════════════════════════
def build_nav():
    PAGES = [
        ("/",        "Dashboard"),
        ("/events",  "Events"),
        ("/monitor", "Monitor"),
        ("/reports", "Reports"),
        ("/sld",     "SLD"),
    ]
    nav_btns = [
        btn(label, page=page, bg="transparent", border_col="transparent",
            col=MUTED2, sz="0.8125rem", track="0.5px",
            grow=0, shrink=0, name=f"nav{label}")
        for page, label in PAGES
    ]
    root = flex([
        flex([
            lbl("CLEARWATER ENERGY", sz="0.875rem", col=BLUE, bold=True,
                track="2px", grow=0, shrink=0),
        ], direction="row", align="center", grow=0, shrink=0, basis="220px"),
        flex(nav_btns, direction="row", align="center", gap="0.25rem",
             grow=1, shrink=1, basis="0%"),
        flex([
            lbl("●", sz="0.5rem", col=GREEN, grow=0, shrink=0),
            lbl("NOMINAL", sz="0.6875rem", col=MUTED2, track="1px", grow=0, shrink=0),
        ], direction="row", align="center", gap="0.5rem", grow=0, shrink=0),
    ], direction="row", align="center", gap="0",
       bg=SURF, pad="0 1.5rem",
       borderBottom=f"1px solid {BORDER}",
       min_height="56px", name="NavRoot")
    write_view("Components/Nav", root, height=56)

# ═══════════════════════════════════════════════════════════════════════════════
#  GENERATOR CARD COMPONENT
# ═══════════════════════════════════════════════════════════════════════════════
def build_generator_card():
    """Params-driven card; static render for build."""
    def row(label, value, col=MUTED2):
        return flex([
            lbl(label, sz="0.625rem", col=MUTED, upper=True, track="1px",
                grow=1, shrink=1, basis="0%"),
            lbl(value, sz="0.75rem",  col=col, bold=True, align="right",
                grow=0, shrink=0),
        ], direction="row", align="center", grow=0, shrink=0)
    root = flex([
        flex([
            flex([
                lbl("{name}", sz="1rem", col=TEXT, bold=True, grow=0, shrink=0),
                lbl("{type}", sz="0.625rem", col=MUTED, upper=True, track="1px",
                    grow=0, shrink=0),
            ], direction="column", gap="2px", grow=1, shrink=1, basis="0%"),
            lbl("{status}", sz="0.625rem", col=BG, bold=True,
                backgroundColor=GREEN, borderRadius="20px", padding="3px 10px",
                grow=0, shrink=0),
        ], direction="row", align="center", grow=0, shrink=0),
        lbl("", grow=0, shrink=0, basis="1px",
            backgroundColor=BORDER, alignSelf="stretch"),
        row("Output",    "{output} MW"),
        row("Capacity",  "{capacity} MW"),
        row("Frequency", "{freq} Hz",    CYAN),
        row("Voltage",   "{voltage} kV", BLUE),
        row("Runtime",   "{runtime}"),
    ], direction="column", gap="0.5rem",
       bg=SURF2, pad="1rem",
       border=f"1px solid {BORDER}", radius="10px",
       grow=0, shrink=0, name="GenCard")
    write_view("Components/Generator Card", root, height=200)

# ═══════════════════════════════════════════════════════════════════════════════
#  SLD COMPONENT (coord — electrical diagram)
# ═══════════════════════════════════════════════════════════════════════════════
def build_sld_component():
    """Single Line Diagram — coord container is valid for overlapping electrical geometry."""
    def cl(text, style, x, y, w, h):
        return {"type":"ia.display.label","meta":{"name":"e"},
                "props":{"text":text,"style":style},
                "position":{"x":x,"y":y,"width":w,"height":h}}

    def bus(x, y, w, col=BORDER):
        return cl("", {"backgroundColor":col,"height":"4px"}, x, y, w, 4)

    def breaker(x, y, closed=True, tag="52"):
        col = GREEN if closed else RED
        s   = "●" if closed else "○"
        return [
            cl(tag, {"fontSize":"7px","color":MUTED,"textAlign":"center"}, x-4, y-14, 28, 12),
            cl(s, {"backgroundColor":SURF2,"border":f"2px solid {col}","color":col,
                   "fontSize":"14px","fontWeight":"700","borderRadius":"4px",
                   "textAlign":"center","lineHeight":"24px"}, x, y, 20, 24),
        ]

    def gen_sym(x, y, label, mw, col=GREEN):
        return [
            cl("G", {"fontSize":"18px","fontWeight":"700","color":col,
                     "border":f"2px solid {col}","borderRadius":"50%",
                     "textAlign":"center","lineHeight":"44px",
                     "backgroundColor":SURF2}, x, y, 44, 44),
            cl(label, {"fontSize":"8px","color":MUTED2,"textAlign":"center"}, x-8, y+46, 60, 12),
            cl(f"{mw} MW", {"fontSize":"9px","color":col,"fontWeight":"700","textAlign":"center"}, x-8, y+58, 60, 12),
        ]

    def trafo(x, y, ratio="13.8/138 kV"):
        return [
            cl("T", {"fontSize":"14px","fontWeight":"700","color":VIOLET,
                     "border":f"2px solid {VIOLET}","borderRadius":"50%",
                     "textAlign":"center","lineHeight":"34px","backgroundColor":SURF2}, x, y, 34, 34),
            cl("T", {"fontSize":"14px","fontWeight":"700","color":VIOLET,
                     "border":f"2px solid {VIOLET}","borderRadius":"50%",
                     "textAlign":"center","lineHeight":"34px","backgroundColor":SURF2}, x+8, y+14, 34, 34),
            cl(ratio, {"fontSize":"7px","color":MUTED,"textAlign":"center"}, x-12, y+50, 70, 12),
        ]

    def wire_v(x, y, h): return cl("", {"backgroundColor":BORDER,"width":"2px"}, x, y, 2, h)
    def wire_h(x, y, w): return cl("", {"backgroundColor":BORDER,"height":"2px"}, x, y, w, 2)

    kids = []
    # 138 kV bus
    kids.append(bus(20, 60, 720, BLUE))
    kids.append(cl("138 kV BUS", {"fontSize":"9px","color":MUTED2,"fontWeight":"700","letterSpacing":"1px"}, 20, 42, 120, 14))

    # Generators at bus
    GEN_DATA = [
        (60,  "G-1", 48.5),
        (220, "G-2", 55.2),
        (380, "G-3", 52.0, RED, False),
        (540, "G-4", 60.0),
        (680, "G-5", 41.3, YELLOW),
    ]
    for i, gd in enumerate(GEN_DATA):
        x = gd[0]; label = gd[1]; mw = gd[2]
        col = gd[3] if len(gd) > 3 else GREEN
        closed = gd[4] if len(gd) > 4 else True
        kids.append(wire_v(x+10, 64, 40))
        kids += breaker(x+1, 104, closed=closed, tag=f"52-{i+1}")
        kids.append(wire_v(x+10, 128, 30))
        kids += trafo(x-7, 158)
        kids.append(wire_v(x+10, 208, 30))
        kids += gen_sym(x-12, 238, label, mw, col)

    # Load feed to right
    kids.append(bus(20, 340, 480, CYAN))
    kids.append(cl("13.8 kV BUS", {"fontSize":"9px","color":CYAN,"fontWeight":"700","letterSpacing":"1px"}, 20, 322, 130, 14))
    kids.append(wire_v(350, 64, 276))
    kids += breaker(341, 150, closed=True, tag="52-T")
    for i, (lx, lname, lmw) in enumerate([(40,"LOAD-A",8.2),(160,"LOAD-B",12.5),(300,"LOAD-C",6.8),(420,"LOAD-D",9.1)]):
        kids.append(wire_v(lx+10, 344, 28))
        kids.append(cl(f"▼ {lname}", {"fontSize":"8px","color":CYAN,"textAlign":"center"}, lx-10, 372, 60, 14))
        kids.append(cl(f"{lmw} MW", {"fontSize":"8px","color":MUTED2,"textAlign":"center"}, lx-10, 386, 60, 12))

    # Legend
    for i, (lc, lt) in enumerate([(GREEN,"Online"),(RED,"Fault"),(YELLOW,"Reduced"),(BLUE,"138 kV"),(CYAN,"13.8 kV")]):
        kids.append(cl("●", {"fontSize":"10px","color":lc}, 560, 320+i*20, 14, 14))
        kids.append(cl(lt,  {"fontSize":"9px","color":MUTED2}, 576, 320+i*20, 80, 14))

    sld = {"type":"ia.container.coord","meta":{"name":"SLD"},
           "props":{"style":{"width":"760px","height":"430px","flexShrink":"0"}},
           "children": kids}
    write_view("Components/SLD", sld, width=760, height=430)

# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def build_dashboard():
    GENERATORS = [
        ("G-1", "Gas Turbine",   "ONLINE",   GREEN,  48.5,  75.0,  60.0, "138.2 kV", "847 h"),
        ("G-2", "Gas Turbine",   "ONLINE",   GREEN,  55.2,  75.0,  60.0, "138.1 kV", "612 h"),
        ("G-3", "Steam Turbine", "FAULT",    RED,     0.0,  120.0, 59.8, "---",       "0 h"),
        ("G-4", "Gas Turbine",   "ONLINE",   GREEN,  60.0,  75.0,  60.1, "138.3 kV", "1204 h"),
        ("G-5", "Gas Turbine",   "DERATED",  YELLOW, 41.3,  75.0,  59.9, "137.9 kV", "320 h"),
    ]

    def gen_row(name, gtype, status, col, out, cap, freq, volt, runtime):
        return flex([
            flex([
                lbl(name,  sz="0.875rem", col=TEXT, bold=True, grow=0, shrink=0),
                lbl(gtype, sz="0.5625rem", col=MUTED, upper=True, track="1px",
                    grow=0, shrink=0),
            ], direction="column", gap="1px", grow=0, shrink=0, basis="80px"),
            lbl(status, sz="0.5625rem", col=BG if col not in (MUTED, YELLOW) else BG,
                bold=True, align="center",
                backgroundColor=col, borderRadius="12px", padding="2px 8px",
                grow=0, shrink=0, basis="72px"),
            lbl(f"{out} MW", sz="0.875rem", col=col, bold=True, font=FM,
                grow=0, shrink=0, basis="70px"),
            lbl(f"/ {cap} MW", sz="0.75rem", col=MUTED, grow=0, shrink=0, basis="60px"),
            lbl(f"{freq} Hz", sz="0.75rem", col=CYAN, font=FM,
                grow=0, shrink=0, basis="64px"),
            lbl(volt, sz="0.75rem", col=BLUE, font=FM, grow=0, shrink=0, basis="72px"),
            lbl(runtime, sz="0.75rem", col=MUTED, grow=1, shrink=1, basis="0%"),
        ], direction="row", align="center", gap="0.75rem",
           grow=0, shrink=0, pad="0.75rem 1rem",
           borderBottom=f"1px solid {BORDER}")

    gen_hdr = flex([
        lbl(h, sz="0.5rem", col=MUTED, upper=True, track="1px",
            grow=0, shrink=0, basis=b)
        for h, b in [("Unit","80px"),("Status","72px"),("Output","70px"),
                     ("Capacity","60px"),("Freq","64px"),("Voltage","72px"),("Runtime","*")]
        if b != "*"
    ] + [lbl("Runtime", sz="0.5rem", col=MUTED, upper=True, track="1px",
              grow=1, shrink=1, basis="0%")],
        direction="row", align="center", gap="0.75rem",
        grow=0, shrink=0, pad="0.5rem 1rem",
        bg=SURF2)

    gen_panel = flex([
        lbl("GENERATION UNITS", sz="0.625rem", col=MUTED2, bold=True, track="2px",
            upper=True, grow=0, shrink=0),
        flex([gen_hdr] + [gen_row(*g) for g in GENERATORS],
             direction="column", gap="0",
             grow=1, shrink=1, basis="0%",
             border=f"1px solid {BORDER}", radius="10px", overflow="hidden"),
    ], direction="column", gap="0.75rem",
       grow=0, shrink=0, basis="auto")

    sld_panel = flex([
        flex([
            lbl("SINGLE LINE DIAGRAM", sz="0.625rem", col=MUTED2, bold=True,
                track="2px", upper=True, grow=0, shrink=0),
            spacer(),
            btn("Full View", page="/sld", bg="transparent", col=BLUE,
                border_col=BLUE, sz="0.6875rem", grow=0, shrink=0),
        ], direction="row", align="center", grow=0, shrink=0),
        {"type":"ia.display.view","meta":{"name":"SLDEmbed"},
         "props":{"path":"Components/SLD"},
         "position":_pos(0, 0, "auto")},
    ], direction="column", gap="0.75rem",
       grow=0, shrink=0, bg=SURF, pad="1rem",
       border=f"1px solid {BORDER}", radius="12px", overflow="auto")

    root = flex([
        nav_embed(),
        flex([
            flex([
                flex([
                    lbl("CLEARWATER ENERGY", sz="1.25rem", col=TEXT, bold=True,
                        track="1px", grow=0, shrink=0),
                    lbl("GENERATION OVERVIEW  ·  Jun 14, 2026  ·  00:00 UTC",
                        sz="0.75rem", col=MUTED, grow=0, shrink=0),
                ], direction="column", gap="2px", grow=1, shrink=1, basis="0%"),
                lbl("205.0 MW ONLINE", sz="0.6875rem", col=GREEN, bold=True,
                    backgroundColor="rgba(34,197,94,0.08)",
                    border="1px solid rgba(34,197,94,0.3)",
                    borderRadius="20px", padding="5px 16px",
                    grow=0, shrink=0),
            ], direction="row", align="center", grow=0, shrink=0),
            # KPI strip
            flex([
                kpi_card("TOTAL OUTPUT",   "205.0", "MW",   GREEN,  "4 units online"),
                kpi_card("CAPACITY",       "345.0", "MW",   BLUE,   "59% utilized"),
                kpi_card("GRID FREQUENCY", "60.0",  "Hz",   CYAN,   "Nominal ± 0.1"),
                kpi_card("ACTIVE ALARMS",  "3",     "",     RED,    "1 Critical · 2 High"),
            ], direction="row", gap="1rem", grow=0, shrink=0),
            gen_panel,
            sld_panel,
        ], direction="column", gap="1.25rem",
           grow=1, shrink=1, basis="0%",
           pad="1.5rem 2rem", overflow="auto"),
    ], direction="column", bg=BG, name="DashboardRoot")
    write_view("Dashboard", root)

# ═══════════════════════════════════════════════════════════════════════════════
#  EVENTS
# ═══════════════════════════════════════════════════════════════════════════════
def build_events():
    EVENTS = [
        ("00:14:02", "CRITICAL", "G-3",        "Generator G-3 (Steam) protection trip — over-current relay ANSI 51", RED),
        ("00:13:58", "HIGH",     "G-3",        "G-3 stator temperature exceeded 180°C setpoint",                     RED),
        ("00:12:44", "HIGH",     "BUS-138",    "138 kV bus voltage dip 8% below nominal (138 → 126 kV)",            YELLOW),
        ("00:12:44", "AUTO",     "SYSTEM",     "AGC increased G-4 and G-5 loading to compensate G-3 trip",          BLUE),
        ("00:10:15", "WARNING",  "G-5",        "G-5 derate active — governor limiting to 55% capacity",             YELLOW),
        ("00:08:30", "INFO",     "LOAD-D",     "Load-D demand forecast updated: +1.2 MW for peak hour",             MUTED2),
        ("00:05:00", "INFO",     "WEATHER",    "Wind advisory: 45 mph gusts — cooling tower drift expected",        MUTED2),
        ("00:02:11", "HIGH",     "G-3",        "G-3 field exciter fault confirmed — maintenance dispatched",        YELLOW),
        ("Jun 13 · 23:55:02", "INFO", "SCADA","Gateway heartbeat OK · 48 tags updated",                            MUTED2),
    ]

    def event_row(ts, level, source, msg, col):
        bg_map = {"CRITICAL": RED, "HIGH": YELLOW, "WARNING": YELLOW, "AUTO": BLUE,
                  "INFO": SURF2}
        bg = bg_map.get(level, SURF2)
        txt_col = BG if level in ("CRITICAL","HIGH") else (TEXT if level == "AUTO" else MUTED2)
        return flex([
            lbl(ts,     sz="0.6875rem", col=MUTED, font=FM, grow=0, shrink=0, basis="140px"),
            lbl(level,  sz="0.5625rem", col=txt_col, bold=True, align="center",
                backgroundColor=bg, borderRadius="4px", padding="2px 6px",
                grow=0, shrink=0, basis="72px"),
            lbl(source, sz="0.75rem",   col=TEXT, bold=True, grow=0, shrink=0, basis="80px"),
            lbl(msg,    sz="0.8125rem", col=MUTED2, grow=1, shrink=1, basis="0%"),
        ], direction="row", align="center", gap="1rem",
           grow=0, shrink=0, pad="0.625rem 1rem",
           borderBottom=f"1px solid {BORDER}")

    badges = [
        ("1 CRITICAL", RED, BG), ("2 HIGH", YELLOW, BG),
        ("1 WARNING", YELLOW+"44", YELLOW), ("2 INFO", SURF2, MUTED2),
    ]
    badge_row = flex([
        lbl(t, sz="0.6875rem", col=tc, bold=True,
            backgroundColor=bg, borderRadius="20px", padding="4px 14px",
            grow=0, shrink=0)
        for t, bg, tc in badges
    ], direction="row", gap="0.5rem", grow=0, shrink=0)

    root = flex([
        nav_embed(),
        flex([
            flex([
                flex([section_hdr("EVENTS", "System alerts and operational log"),
                      spacer(), badge_row],
                     direction="row", align="center", gap="1rem", grow=0, shrink=0),
            ], grow=0, shrink=0),
            flex([
                flex([
                    lbl(h, sz="0.5rem", col=MUTED, upper=True, track="1px",
                        grow=0, shrink=0, basis=b)
                    for h, b in [("Timestamp","140px"),("Level","72px"),
                                 ("Source","80px"),("Event","*")]
                    if b != "*"
                ] + [lbl("Event", sz="0.5rem", col=MUTED, upper=True, track="1px",
                          grow=1, shrink=1, basis="0%")],
                    direction="row", align="center", gap="1rem",
                    grow=0, shrink=0, pad="0.5rem 1rem", bg=SURF2),
                *[event_row(*e) for e in EVENTS],
            ], direction="column", gap="0",
               grow=1, shrink=1, basis="0%",
               border=f"1px solid {BORDER}", radius="10px",
               overflow="hidden", bg=SURF),
        ], direction="column", gap="1.25rem",
           grow=1, shrink=1, basis="0%",
           pad="1.5rem 2rem", overflow="auto"),
    ], direction="column", bg=BG, name="EventsRoot")
    write_view("Events", root)

# ═══════════════════════════════════════════════════════════════════════════════
#  MONITOR
# ═══════════════════════════════════════════════════════════════════════════════
def build_monitor():
    def chart_card(tag, value, unit, col, points, note=""):
        max_v = max(points) or 1
        bars = [{"type":"ia.display.label","meta":{"name":"bar"},
                 "props":{"text":"","style":{"backgroundColor":col,"opacity":"0.75",
                     "borderRadius":"2px 2px 0 0","width":"14px"}},
                 "position":{"basis":f"{int(72*v/max_v)}px","shrink":0,"alignSelf":"flex-end"}}
                for v in points]
        return flex([
            flex([
                flex([
                    lbl(tag, sz="0.625rem", col=MUTED2, bold=True, track="1.5px",
                        upper=True, grow=0, shrink=0),
                    flex([
                        lbl(str(value), sz="2rem", col=col, bold=True, font=FM,
                            grow=0, shrink=0),
                        lbl(unit, sz="0.875rem", col=MUTED2, grow=0, shrink=0),
                    ], direction="row", align="baseline", gap="0.25rem", grow=0, shrink=0),
                    lbl(note, sz="0.6875rem", col=MUTED, grow=0, shrink=0),
                ], direction="column", gap="2px", grow=1, shrink=1, basis="0%"),
                lbl("24H", sz="0.625rem", col=MUTED2,
                    backgroundColor=SURF2, border=f"1px solid {BORDER}",
                    borderRadius="6px", padding="3px 8px",
                    grow=0, shrink=0),
            ], direction="row", align="flex-start", grow=0, shrink=0),
            flex(bars, direction="row", align="flex-end", gap="3px",
                 grow=0, shrink=0, basis="76px",
                 borderTop=f"1px solid {BORDER}", paddingTop="8px"),
        ], direction="column", gap="0.75rem",
           grow=1, shrink=1, basis="0%",
           bg=SURF, pad="1.125rem 1.25rem",
           border=f"1px solid {BORDER}", radius="12px",
           min_height="160px")

    CHARTS = [
        ("G-1 OUTPUT", 48.5, "MW", GREEN,  [44,46,48,49,48,48,49,48,48,49], "Gas Turbine 1"),
        ("G-2 OUTPUT", 55.2, "MW", GREEN,  [50,52,54,55,55,56,55,55,55,55], "Gas Turbine 2"),
        ("G-4 OUTPUT", 60.0, "MW", BLUE,   [56,58,60,60,60,60,60,60,60,60], "Gas Turbine 4"),
        ("G-5 OUTPUT", 41.3, "MW", YELLOW, [60,58,55,50,44,42,41,41,41,41], "Derated"),
        ("FREQUENCY",  60.0, "Hz", CYAN,   [60.0,59.9,60.1,59.8,60.2,60.0,59.9,60.1,60.0,60.0], "Grid"),
        ("138kV BUS",  138.2,"kV", VIOLET, [138,138,138,126,130,135,137,138,138,138], "Post-trip recovery"),
    ]
    time_btns = [btn(t, bg=BLUE if t=="24H" else SURF2,
                     col=TEXT if t=="24H" else MUTED2,
                     border_col=BLUE if t=="24H" else BORDER,
                     sz="0.6875rem", grow=0, shrink=0)
                 for t in ["1H","6H","24H","7D"]]

    root = flex([
        nav_embed(),
        flex([
            flex([
                section_hdr("MONITOR", "Live trends and historical analytics"),
                spacer(),
                flex(time_btns, direction="row", gap="0.5rem", grow=0, shrink=0),
            ], direction="row", align="center", grow=0, shrink=0),
            flex([chart_card(*c) for c in CHARTS],
                 direction="row", gap="1rem", wrap="wrap", grow=0, shrink=0),
        ], direction="column", gap="1.25rem",
           grow=1, shrink=1, basis="0%",
           pad="1.5rem 2rem", overflow="auto"),
    ], direction="column", bg=BG, name="MonitorRoot")
    write_view("Monitor", root)

# ═══════════════════════════════════════════════════════════════════════════════
#  REPORTS
# ═══════════════════════════════════════════════════════════════════════════════
def build_reports():
    REPORTS = [
        ("Daily Generation Summary",     "Jun 13, 2026", "Auto-generated", "PDF",    GREEN),
        ("Fault Analysis — G-3 Trip",    "Jun 14, 2026", "System",         "PDF",    RED),
        ("Weekly KPI Report",            "Jun 8, 2026",  "Scheduled",      "XLSX",   BLUE),
        ("Frequency Deviation Log",      "Jun 14, 2026", "Auto-generated", "CSV",    CYAN),
        ("Maintenance Work Order #1084", "Jun 13, 2026", "Operations",     "PDF",    YELLOW),
        ("Load Forecast — Q3 2026",      "Jun 10, 2026", "Planning",       "XLSX",   VIOLET),
        ("Monthly Compliance Report",    "Jun 1, 2026",  "Regulatory",     "PDF",    MUTED2),
    ]

    def report_row(name, date, author, fmt, col):
        return flex([
            flex([
                lbl(name,   sz="0.875rem", col=TEXT, bold=True, grow=0, shrink=0),
                lbl(f"{author}  ·  {date}", sz="0.6875rem", col=MUTED,
                    grow=0, shrink=0),
            ], direction="column", gap="2px", grow=1, shrink=1, basis="0%"),
            lbl(fmt, sz="0.625rem", col=col, bold=True, align="center",
                border=f"1px solid {col}", borderRadius="4px", padding="2px 8px",
                grow=0, shrink=0),
            btn("Download", col=BLUE, bg="transparent", border_col=BORDER,
                sz="0.6875rem", grow=0, shrink=0),
        ], direction="row", align="center", gap="1rem",
           grow=0, shrink=0, pad="0.75rem 1rem",
           borderBottom=f"1px solid {BORDER}")

    type_btns = [btn(t, bg=BLUE if i==0 else SURF2,
                     col=TEXT if i==0 else MUTED2,
                     border_col=BLUE if i==0 else BORDER,
                     sz="0.6875rem", grow=0, shrink=0)
                 for i, t in enumerate(["All","PDF","XLSX","CSV","Auto"])]

    root = flex([
        nav_embed(),
        flex([
            flex([
                section_hdr("REPORTS", "Generated reports and downloadable logs"),
                spacer(),
                flex(type_btns, direction="row", gap="0.5rem", grow=0, shrink=0),
            ], direction="row", align="center", grow=0, shrink=0),
            flex([
                flex([
                    lbl(h, sz="0.5rem", col=MUTED, upper=True, track="1px",
                        grow=0 if b!="*" else 1, shrink=0 if b!="*" else 1,
                        basis="auto" if b!="*" else "0%")
                    for h, b in [("Report Name","*"),("Type","60px"),("","80px")]
                ], direction="row", align="center", gap="1rem",
                   grow=0, shrink=0, pad="0.5rem 1rem", bg=SURF2),
                *[report_row(*r) for r in REPORTS],
            ], direction="column", gap="0",
               grow=1, shrink=1, basis="0%",
               border=f"1px solid {BORDER}", radius="10px",
               overflow="hidden", bg=SURF),
        ], direction="column", gap="1.25rem",
           grow=1, shrink=1, basis="0%",
           pad="1.5rem 2rem", overflow="auto"),
    ], direction="column", bg=BG, name="ReportsRoot")
    write_view("Reports", root)

# ═══════════════════════════════════════════════════════════════════════════════
#  SLD PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def build_sld_page():
    root = flex([
        nav_embed(),
        flex([
            flex([
                section_hdr("SINGLE LINE DIAGRAM",
                            "138 kV / 13.8 kV Generation & Distribution"),
                spacer(),
                lbl("●", sz="0.5rem", col=GREEN, grow=0, shrink=0),
                lbl("NOMINAL", sz="0.6875rem", col=MUTED2, track="1px",
                    grow=0, shrink=0),
            ], direction="row", align="center", gap="0.75rem", grow=0, shrink=0),
            flex([
                {"type":"ia.display.view","meta":{"name":"SLDEmbed"},
                 "props":{"path":"Components/SLD"},
                 "position":_pos(0, 0, "auto")},
            ], direction="row", justify="center",
               grow=1, shrink=1, basis="0%",
               bg=SURF, pad="1.5rem",
               border=f"1px solid {BORDER}", radius="12px",
               overflow="auto"),
        ], direction="column", gap="1.25rem",
           grow=1, shrink=1, basis="0%",
           pad="1.5rem 2rem", overflow="auto"),
    ], direction="column", bg=BG, name="SLDRoot")
    write_view("SLD", root)

# ═══════════════════════════════════════════════════════════════════════════════
#  PROJECT FILES
# ═══════════════════════════════════════════════════════════════════════════════
def write_project():
    write("project.json", {
        "title": "power-hmi",
        "description": "Clearwater Energy Power System HMI",
        "parent": "", "enabled": True, "inheritable": False
    })
    pc = "com.inductiveautomation.perspective/page-config"
    write(f"{pc}/config.json", {
        "pages": {
            "/":        {"title": "Power System HMI", "viewPath": "Dashboard"},
            "/events":  {"title": "Events",           "viewPath": "Events"},
            "/monitor": {"title": "Monitor",          "viewPath": "Monitor"},
            "/reports": {"title": "Reports",          "viewPath": "Reports"},
            "/sld":     {"title": "Single Line Diagram", "viewPath": "SLD"},
        },
        "sharedDocks": {"cornerPriority":"top-bottom","bottom":[],"left":[],"right":[]}
    })
    write(f"{pc}/resource.json", resource(["config.json"]))
    print("  project.json + page-config")

# ═══════════════════════════════════════════════════════════════════════════════
#  BUILD + DEPLOY
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Building power-hmi (flex layout, component.onActionPerformed nav)...")
    write_project()
    build_nav()
    build_generator_card()
    build_sld_component()
    build_dashboard()
    build_events()
    build_monitor()
    build_reports()
    build_sld_page()

    print(f"\nDeploying → {DEST}")
    if os.path.exists(DEST):
        shutil.rmtree(DEST)
    subprocess.run([
        "rsync", "-a",
        "--exclude=.git", "--exclude=*.py",
        f"{SRC}/", f"{DEST}/"
    ], check=True)
    subprocess.run(["find", DEST, "-name", "*.json", "-exec", "touch", "{}", ";"])
    print("Done.")
