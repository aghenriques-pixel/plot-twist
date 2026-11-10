"""Make every picture colourful and alive: a richer palette and ambient animation inside each SVG.

Run from the project folder, after scripts/art_chapter2.py if that was run:
    uv run python scripts/art_colour.py

It is safe to run more than once: a file is only changed if it has no "coloured" marker yet.
The animation is CSS inside the SVG, so it plays even when the picture is shown with <img>.
Clue details are not touched: the six dark screens (#050608) stay dark, numbers and texts stay.
"""

import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets"
MARKER = "<!-- coloured -->"

# Dull colours -> richer ones (deep blues and purples instead of greys, warmer woods, brighter lights)
PALETTE = {
    "#3a2f2b": "#6b3f3a", "#121418": "#14102a", "#8a7a5c": "#d39b5a", "#b3262b": "#e63946",
    "#e8e1cf": "#fff4dc", "#4a505b": "#6c7bb5", "#f2c14e": "#ffc94d", "#241c16": "#3d2417",
    "#c8a88a": "#e0b493", "#3a2a1c": "#6b3e1f", "#9c9483": "#b8a9d9", "#a89a7c": "#d8c08a",
    "#8fb3cc": "#8fe3ff", "#2a2321": "#4a2a3f", "#1a1a1a": "#231a2e", "#5f8299": "#36c5f0",
    "#2f3b2f": "#3b6b3b", "#2f2a33": "#4b2f6b", "#25212a": "#2e1f45", "#6b5236": "#a0592c",
    "#5a4636": "#9a5b34", "#a8956c": "#e2b46b", "#3a2f26": "#7a4a2a", "#1d1a22": "#2a1d4a",
    "#141821": "#1b2350", "#3f5b4a": "#2e8b57", "#4a3824": "#6e3b1c", "#343a44": "#4a4f9a",
    "#2a2e35": "#3a3f7a", "#7a2a2a": "#c0392b", "#8a8f98": "#a7b3e0", "#4d5a6b": "#3f6fb5",
    "#454b55": "#5865a8", "#3a3f4b": "#4b55a0", "#2c4034": "#1f6a40", "#4a3a2c": "#8a5530",
    "#36404c": "#2c4f86", "#1a1d23": "#22264d", "#c9a640": "#ffcf3f", "#1f281f": "#2a4a2a",
    "#1b1b1f": "#261c36", "#2a2e3a": "#353f86", "#d8d0bb": "#fff0d0", "#d8cfb6": "#fff0d0",
    "#a08a5a": "#d9a45a", "#6b4a2f": "#a8653a", "#565c66": "#7d88c4", "#45414a": "#6a5a8a",
    "#3b4048": "#56609e", "#2a2e36": "#2d3584", "#1f2b35": "#1f3a66", "#1d1a17": "#3a2318",
    "#1a1615": "#2a1a24", "#14110f": "#24150e", "#0d1018": "#101a40", "#23262c": "#2b2f66",
    "#1c1f25": "#1f2152", "#2b2a2f": "#4a2f5e", "#1f1d21": "#2d2040", "#181c22": "#1b2550",
    "#14171c": "#141a3d", "#101114": "#12203a", "#17181c": "#1a2b4a", "#0c0d10": "#0d1630",
    "#0b0f1c": "#120c3a", "#1d2438": "#3b2a78", "#211d26": "#2e1f45", "#16131a": "#1e1430",
    "#1a0c0d": "#3a0a12", "#120809": "#24060c", "#160d0e": "#3a1020", "#12151d": "#16204a",
    "#090c16": "#0f0a33", "#1a2032": "#33286e", "#1a1e28": "#2b2d6e", "#14171f": "#1c1d4a",
    "#252a36": "#3a2f7a", "#11141c": "#1a1640",
}

STYLE = """<style>
.pulse { animation: pulse 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
.flicker { animation: flicker 4s steps(1) infinite; }
.twinkle { animation: twinkle 3s ease-in-out infinite; }
.lid { animation: lid 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; transform: scaleY(0); }
.rain { animation: rain 0.9s linear infinite; }
.drift { animation: drift 12s ease-in-out infinite alternate; }
.rise { animation: rise 7s linear infinite; }
.fall { animation: fall 2.6s ease-in infinite; }
.blink { animation: blink 1.2s steps(1) infinite; }
.sweep { animation: sweep 9s ease-in-out infinite alternate; transform-origin: 360px 20px; }
.wave { animation: wave 3s ease-out infinite; transform-box: fill-box; transform-origin: center; }
.bounce { animation: bounce 0.6s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: bottom; }
@keyframes pulse { 0%, 100% { opacity: 0.35; transform: scale(1); } 50% { opacity: 0.9; transform: scale(1.12); } }
@keyframes flicker { 0%, 100% { opacity: 1; } 31% { opacity: 0.55; } 33% { opacity: 1; } 67% { opacity: 0.7; } 69% { opacity: 1; } }
@keyframes twinkle { 0%, 100% { opacity: 0.25; } 50% { opacity: 1; } }
@keyframes lid { 0%, 90%, 100% { transform: scaleY(0); } 94%, 96% { transform: scaleY(1); } }
@keyframes rain { from { transform: translate(0, -60px); } to { transform: translate(-18px, 420px); } }
@keyframes drift { from { transform: translateX(-30px); } to { transform: translateX(30px); } }
@keyframes rise { 0% { transform: translateY(0); opacity: 0; } 20% { opacity: 0.8; } 100% { transform: translateY(-160px); opacity: 0; } }
@keyframes fall { 0% { transform: translateY(0); opacity: 0; } 10% { opacity: 1; } 100% { transform: translateY(240px); opacity: 0; } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.15; } }
@keyframes sweep { from { transform: rotate(-25deg); } to { transform: rotate(25deg); } }
@keyframes wave { 0% { transform: scale(0.6); opacity: 0.8; } 100% { transform: scale(1.6); opacity: 0; } }
@keyframes bounce { from { transform: scaleY(0.3); } to { transform: scaleY(1); } }
</style>"""


def rng(name):
    return random.Random(name)  # same picture, same raindrops every run


def glow(cx, cy, r, color, cls="pulse", delay=0.0):
    return f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="0.5" style="animation-delay:{delay}s"/>'


def eye_lid(cx, cy, rx, ry, delay=0.0):
    return f'<ellipse class="lid" cx="{cx}" cy="{cy}" rx="{rx + 1}" ry="{ry + 1}" fill="#14102a" style="animation-delay:{delay}s"/>'


def rain_lines(name, count=60, area=(0, 0, 800, 400), color="#9fd8ff"):
    r = rng(name)
    x0, y0, x1, y1 = area
    out = []
    for _ in range(count):
        x, y = r.uniform(x0, x1 + 40), r.uniform(y0, y1)
        out.append(
            f'<line class="rain" x1="{x:.0f}" y1="{y:.0f}" x2="{x - 5:.0f}" y2="{y + 16:.0f}" stroke="{color}" '
            f'stroke-width="1.3" opacity="0.4" style="animation-delay:-{r.uniform(0, 1):.2f}s;'
            f'animation-duration:{r.uniform(0.6, 1.1):.2f}s"/>'
        )
    return "".join(out)


def dust(name, count, area, color="#fff1b8"):
    r = rng(name)
    x0, y0, x1, y1 = area
    return "".join(
        f'<circle class="rise" cx="{r.uniform(x0, x1):.0f}" cy="{r.uniform(y0, y1):.0f}" r="{r.uniform(1, 2.2):.1f}" '
        f'fill="{color}" style="animation-delay:-{r.uniform(0, 7):.1f}s"/>'
        for _ in range(count)
    )


def twinkles(name, points, color="#ffd36e", size=(3, 4)):
    r = rng(name)
    return "".join(
        f'<rect class="twinkle" x="{x}" y="{y}" width="{size[0]}" height="{size[1]}" fill="{color}" '
        f'style="animation-delay:-{r.uniform(0, 3):.1f}s;animation-duration:{r.uniform(2, 4):.1f}s"/>'
        for x, y in points
    )


def light(cx, cy, r, color, opacity=0.35):
    """A soft coloured light: makes the scene less flat."""
    gid = f"l{cx}{cy}{r}".replace(".", "")
    return (
        f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>'
    )


VIGNETTE = (
    '<radialGradient id="vignette" cx="0.5" cy="0.45" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
    '<stop offset="1" stop-color="#05021a" stop-opacity="0.55"/></radialGradient>'
    '<rect width="800" height="400" fill="url(#vignette)"/>'
)


def screens_flicker():
    """The working screens in the surveillance station flicker; the six broken ones stay dark (clue)."""
    offline = {(0, 2), (0, 6), (1, 0), (1, 4), (2, 1), (2, 5)}
    r = rng("screens")
    out = []
    for row in range(3):
        for col in range(7):
            if (row, col) in offline:
                continue
            x, y = 44 + col * 105, 34 + row * 70
            out.append(
                f'<rect class="flicker" x="{x}" y="{y}" width="87" height="52" fill="#7fe8ff" opacity="0.18" '
                f'style="animation-delay:-{r.uniform(0, 4):.1f}s;animation-duration:{r.uniform(2.5, 5):.1f}s"/>'
            )
    return "".join(out)


def ambient(name):
    """What moves in each picture."""
    base = name.replace(".svg", "")
    if base.startswith("ministerio"):
        return (
            light(400, 0, 380, "#7b8cff", 0.28)
            + glow(210, 130, 16, "#ff4d6d") + glow(480, 130, 16, "#ff4d6d", delay=1.5)
            + eye_lid(210, 130, 30, 13) + eye_lid(480, 130, 30, 13, delay=2.5)
            + glow(572, 262, 26, "#ffd36e")
            + dust(name, 18, (60, 60, 760, 290))
        )
    if base.startswith("arquivo"):
        return (
            '<path class="flicker" d="M 388 80 L 412 80 L 520 340 L 280 340 Z" fill="#ffd36e" opacity="0.18"/>'
            + light(400, 300, 260, "#ff9a3c", 0.25)
            + dust(name, 24, (300, 100, 500, 330))
        )
    if base.startswith("apartamento"):
        return (
            light(710, 220, 220, "#ffb347", 0.35)
            + rain_lines(name, 30, (85, 75, 270, 240), "#bfe6ff")
            + twinkles(name, [(94 + i * 22, 190 + (i * 13) % 40) for i in range(8)])
            + glow(380, 115, 12, "#ff4d6d") + eye_lid(380, 115, 25, 12)
            + '<rect class="flicker" x="660" y="110" width="100" height="220" fill="#fff1b8" opacity="0.15"/>'
        )
    if base.startswith("vigilancia"):
        return (
            light(400, 120, 360, "#36c5f0", 0.22)
            + screens_flicker()
            + '<circle class="blink" cx="770" cy="250" r="5" fill="#ff3b30"/>'
            + glow(682, 358, 18, "#ffcf3f")
        )
    if base == "tunel":
        drops = "".join(
            f'<circle class="fall" cx="{x}" cy="{y}" r="1.8" fill="#9fd8ff" style="animation-delay:-{d}s"/>'
            for x, y, d in [(260, 160, 0.3), (420, 140, 1.4), (610, 160, 0.9), (330, 120, 2.1), (520, 130, 1.8)]
        )
        return (
            light(610, 330, 150, "#36c5f0", 0.35)
            + '<circle class="drift" cx="430" cy="250" r="30" fill="#fff4dc" opacity="0.35"/>'
            + light(430, 250, 120, "#fff4dc", 0.2)
            + drops
        )
    if base == "esconderijo":
        return light(430, 300, 200, "#ffc94d", 0.45) + glow(430, 300, 40, "#ffc94d") + dust(name, 14, (330, 200, 530, 360))
    if base == "final_resistencia":
        return light(400, 215, 300, "#ffb347", 0.45) + glow(400, 215, 70, "#ffd36e") + dust(name, 20, (60, 60, 760, 340), "#fff4dc")
    if base in ("final_descoberto", "final_traido"):
        return (
            '<rect class="blink" width="800" height="400" fill="#ff1f3d" opacity="0.12"/>'
            + glow(80, 150, 50, "#ff3b30") + glow(720, 150, 50, "#ff3b30", delay=0.6)
            + light(400, 200, 300, "#ff4d6d", 0.25)
        )
    if base.startswith("c2_esconderijo"):
        return (
            '<circle class="flicker" cx="470" cy="200" r="230" fill="#ffc94d" opacity="0.10"/>'
            + light(470, 60, 300, "#ffb347", 0.3)
            + dust(name, 20, (300, 80, 640, 330))
            + glow(236, 92, 9, "#ff4d6d")
        )
    if base == "c2_cidade":
        return (
            light(680, 60, 160, "#cfe3ff", 0.45)
            + twinkles(name, [(432 + i * 34, 200) for i in range(4)], "#ffd36e", (18, 24))
            + light(250, 330, 160, "#ffc94d", 0.3)
            + '<rect class="drift" x="0" y="250" width="800" height="70" fill="#b8a9ff" opacity="0.12"/>'
            + rain_lines(name, 80)
        )
    if base == "c2_torre":
        stars = twinkles(name, [((i * 97) % 800, (i * 53) % 120) for i in range(30)], "#ffffff", (2, 2))
        return (
            stars
            + '<path class="sweep" d="M 360 20 L 250 400 L 470 400 Z" fill="#fff4dc" opacity="0.10"/>'
            + '<circle class="blink" cx="360" cy="18" r="10" fill="#ff3b30"/>'
            + light(360, 18, 90, "#ff3b30", 0.4)
            + light(600, 250, 220, "#7b8cff", 0.25)
        )
    if base == "c2_estudio":
        bars = "".join(
            f'<rect class="bounce" x="{300 + i * 7}" y="236" width="5" height="22" fill="{c}" '
            f'style="animation-delay:-{i * 0.13:.2f}s"/>'
            for i, c in enumerate(["#2ecc71", "#2ecc71", "#a3e635", "#ffcf3f", "#ff7b54", "#e63946"])
        )
        return (
            '<rect class="blink" x="380" y="10" width="90" height="24" rx="4" fill="#ff1f3d" opacity="0.45"/>'
            + light(425, 20, 120, "#ff3b30", 0.35)
            + light(450, 220, 260, "#9b5de5", 0.25)
            + bars
        )
    if base == "final_c2_voz":
        waves = "".join(
            f'<circle class="wave" cx="700" cy="58" r="60" fill="none" stroke="#fff4dc" stroke-width="2" style="animation-delay:{d}s"/>'
            for d in (0, 1, 2)
        )
        return waves + light(400, 400, 360, "#ffb347", 0.35)
    if base == "final_c2_reconhecido":
        return (
            '<rect class="blink" width="800" height="400" fill="#ff1f3d" opacity="0.12"/>'
            + light(675, 200, 220, "#ffc94d", 0.35)
        )
    return ""


def colour(path):
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    text = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: PALETTE.get(m.group(0).lower(), m.group(0)), text)
    if path.parent.name == "scenes":
        extra = ambient(path.name)
        text = text.replace("</svg>", f"{STYLE}{extra}{VIGNETTE}{MARKER}</svg>", 1)
    else:
        text = text.replace("</svg>", f"{MARKER}</svg>", 1)
    path.write_text(text, encoding="utf-8")
    return True


if __name__ == "__main__":
    changed = [p.name for p in sorted(ART.rglob("*.svg")) if colour(p)]
    print(f"coloured {len(changed)} pictures")
