"""Draw the chapter 2 illustrations as SVG files in assets/scenes/.

Run from the project folder:  uv run python scripts/art_chapter2.py
People are drawn from assets/character.svg (the protagonist), recoloured for other characters,
so everyone looks like the same comic. Every picture is 800x400.
"""

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "scenes"

INK = "#121418"
PAPER = "#e8e1cf"
RED = "#b3262b"
WARM = "#f2c14e"
COLD = "#8fb3cc"
METAL = "#4a505b"
SKIN = "#c8a88a"
COAT = "#6b5236"
JULIA = ("#3f5b4a", "#2c4034")
POLICE = ("#2f3b2f", "#1f281f")
TOMAS = ("#4d5a6b", "#36404c")

# The protagonist drawn around (0, 0) = feet, from the sprite used by the clickable scenes
SPRITE = re.search(r"<svg[^>]*>(.*)</svg>", (ROOT / "assets" / "character.svg").read_text(encoding="utf-8"), re.S).group(1)


def person(x, y, scale=1.0, flip=False, coat=None):
    """A character with feet at (x, y). `coat` = (main, dark) recolours the protagonist's coat."""
    body = SPRITE
    if coat:
        body = body.replace(COAT, coat[0]).replace("#4a3824", coat[1])
    sx = -scale if flip else scale
    return f'<g transform="translate({x} {y}) scale({sx} {scale})">{body}</g>'


def svg(body, defs=""):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">'
        f"<defs>{defs}</defs>{body}</svg>"
    )


def text(x, y, value, size=9, fill=INK, anchor="middle", weight="normal", rotate=0):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    return (
        f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}"{transform}>{value}</text>'
    )


def bricks(x0, y0, x1, y1, color="#3a2f2b"):
    rows = []
    for row, y in enumerate(range(y0, y1, 18)):
        rows.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{color}" stroke-width="1"/>')
        offset = 0 if row % 2 else 20
        for x in range(x0 + offset, x1, 40):
            rows.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{min(y + 18, y1)}" stroke="{color}" stroke-width="1"/>')
    return "".join(rows)


# --- Scenes ------------------------------------------------------------------------------


def hideout(message=True, cassette=True):
    lamp = (
        '<radialGradient id="lamp"><stop offset="0" stop-color="#f2c14e" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="#f2c14e" stop-opacity="0"/></radialGradient>'
    )
    city_map = (
        f'<rect x="90" y="70" width="160" height="120" fill="#d8cfb6" stroke="#8a7a5c" stroke-width="3"/>'
        + "".join(f'<line x1="{90 + i * 20}" y1="72" x2="{90 + i * 20}" y2="188" stroke="#a89a7c" stroke-width="1"/>' for i in range(1, 8))
        + "".join(f'<line x1="92" y1="{70 + i * 20}" x2="248" y2="{70 + i * 20}" stroke="#a89a7c" stroke-width="1"/>' for i in range(1, 6))
        + f'<path d="M 100 170 Q 160 120 240 90" stroke="{COLD}" stroke-width="3" fill="none" stroke-dasharray="6 4"/>'
        + f'<path d="M 120 150 L 132 162 M 132 150 L 120 162" stroke="{RED}" stroke-width="3"/>'
        + f'<path d="M 190 100 L 202 112 M 202 100 L 190 112" stroke="{RED}" stroke-width="3"/>'
        + f'<circle cx="236" cy="92" r="6" fill="{RED}"/>'
    )
    radio = (
        f'<rect x="320" y="170" width="110" height="7" fill="#4a3a2c"/>'
        f'<rect x="330" y="110" width="90" height="60" rx="8" fill="#6b4a2f" stroke="#3a2a1c" stroke-width="2"/>'
        + "".join(f'<circle cx="{348 + (i % 4) * 9}" cy="{128 + (i // 4) * 9}" r="2.5" fill="#3a2a1c"/>' for i in range(12))
        + f'<circle cx="398" cy="138" r="12" fill="{PAPER}" stroke="#3a2a1c" stroke-width="2"/>'
        f'<line x1="398" y1="138" x2="406" y2="131" stroke="{RED}" stroke-width="2"/>'
        f'<rect x="336" y="156" width="40" height="10" fill="{PAPER}"/>'
    )
    note = (
        f'<rect x="562" y="92" width="66" height="56" fill="{PAPER}" transform="rotate(4 595 120)"/>'
        + "".join(f'<rect x="570" y="{104 + i * 9}" width="{46 - (i % 2) * 12}" height="2" fill="{INK}" opacity="0.5" transform="rotate(4 595 120)"/>' for i in range(4))
        + f'<circle cx="595" cy="95" r="3" fill="{RED}"/>'
    )
    table = (
        '<rect x="370" y="300" width="200" height="10" fill="#5a4636"/>'
        f'<rect x="380" y="310" width="8" height="40" fill="{INK}"/><rect x="552" y="310" width="8" height="40" fill="{INK}"/>'
    )
    paper = (
        f'<rect x="402" y="284" width="56" height="16" fill="{PAPER}" transform="rotate(-4 430 292)"/>'
        + text(430, 295, "OLEHUGDGH", size=7, rotate=-4)
        if message
        else ""
    )
    tape = (
        f'<rect x="502" y="284" width="34" height="16" rx="2" fill="#1b1b1f"/>'
        f'<circle cx="512" cy="292" r="4" fill="{PAPER}"/><circle cx="526" cy="292" r="4" fill="{PAPER}"/>'
        f'<rect x="508" y="286" width="22" height="3" fill="{RED}"/>'
        if cassette
        else ""
    )
    return svg(
        f'<rect width="800" height="400" fill="#2a2321"/>{bricks(0, 0, 800, 340)}'
        f'<rect y="340" width="800" height="60" fill="#1a1615"/>'
        f'<path d="M 470 0 L 470 40" stroke="{METAL}" stroke-width="2"/><path d="M 455 40 L 485 40 L 478 50 L 462 50 Z" fill="{METAL}"/>'
        f'<circle cx="470" cy="200" r="230" fill="url(#lamp)"/>'
        f"{city_map}{radio}{note}{table}{paper}{tape}"
        f'<rect x="690" y="280" width="70" height="60" fill="#4a3a2c"/><rect x="700" y="250" width="50" height="30" fill="#5a4636"/>'
        + person(645, 345, 1.0, flip=True, coat=JULIA),
        lamp,
    )


def city():
    sky = (
        '<linearGradient id="night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0f1c"/>'
        '<stop offset="1" stop-color="#1d2438"/></linearGradient>'
    )
    clock_tower = (
        '<rect x="70" y="40" width="70" height="300" fill="#2a2e3a"/>'
        f'<circle cx="105" cy="85" r="28" fill="{PAPER}" stroke="{METAL}" stroke-width="4"/>'
        # 10 o'clock: hour hand towards 10, minute hand straight up
        f'<line x1="105" y1="85" x2="91" y2="77" stroke="{INK}" stroke-width="4"/>'
        f'<line x1="105" y1="85" x2="105" y2="62" stroke="{INK}" stroke-width="2.5"/>'
    )
    poster = (
        '<rect x="148" y="150" width="82" height="190" fill="#3a2f2b"/>' + bricks(148, 150, 230, 340, "#2a2321")
        + f'<rect x="160" y="170" width="60" height="70" fill="{PAPER}"/><rect x="160" y="170" width="60" height="18" fill="{RED}"/>'
        + text(190, 183, "RECOLHER", size=7, fill=PAPER, weight="bold")
        + text(190, 214, "21H", size=18, weight="bold")
    )
    alley = (
        '<rect x="240" y="90" width="55" height="250" fill="#252a36"/><rect x="345" y="110" width="55" height="230" fill="#252a36"/>'
        '<path d="M 295 340 L 345 340 L 330 170 L 310 170 Z" fill="#11141c"/>'
        + "".join(f'<path d="M {300 + i * 9} 200 l 9 0 l -4 10 Z" fill="{RED if i % 2 else PAPER}"/>' for i in range(4))
        + f'<rect x="262" y="226" width="116" height="16" fill="{PAPER}"/>' + text(320, 238, "BECO DO MERCADO", size=8, weight="bold")
    )
    factories = (
        '<rect x="420" y="170" width="150" height="170" fill="#2a2e3a"/>'
        '<rect x="440" y="90" width="18" height="80" fill="#2a2e3a"/><rect x="500" y="70" width="18" height="100" fill="#2a2e3a"/>'
        '<circle cx="449" cy="80" r="14" fill="#3a3f4b" opacity="0.6"/><circle cx="509" cy="58" r="16" fill="#3a3f4b" opacity="0.6"/>'
        + "".join(f'<rect x="{432 + i * 34}" y="200" width="18" height="24" fill="{WARM}" opacity="0.5"/>' for i in range(4))
        + f'<rect x="440" y="252" width="110" height="16" fill="{PAPER}"/>' + text(495, 264, "RUA DAS FÁBRICAS", size=8, weight="bold")
    )
    tram = (
        '<path d="M 600 340 L 760 340 L 700 150 L 690 150 Z" fill="#1a1e28"/>'
        f'<path d="M 625 340 L 692 150 M 735 340 L 698 150" stroke="{METAL}" stroke-width="3"/>'
        + "".join(f'<line x1="{640 + i * 3}" y1="{320 - i * 30}" x2="{720 - i * 5}" y2="{320 - i * 30}" stroke="#3a3f4b" stroke-width="3"/>' for i in range(6))
        + f'<path d="M 600 120 L 780 120" stroke="{METAL}" stroke-width="1.5"/>'
        f'<rect x="770" y="120" width="5" height="220" fill="{METAL}"/>'
        f'<rect x="610" y="252" width="96" height="16" fill="{PAPER}"/>' + text(658, 264, "LINHA DO ELÉTRICO", size=8, weight="bold")
    )
    return svg(
        f'<rect width="800" height="400" fill="url(#night)"/><circle cx="680" cy="60" r="18" fill="{PAPER}" opacity="0.8"/>'
        f"{clock_tower}{poster}{alley}{factories}{tram}"
        f'<rect y="340" width="800" height="60" fill="#14171f"/>'
        f'<circle cx="250" cy="330" r="60" fill="{WARM}" opacity="0.06"/>',
        sky,
    )


def tower():
    sky = (
        '<linearGradient id="night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#090c16"/>'
        '<stop offset="1" stop-color="#1a2032"/></linearGradient>'
    )
    lattice = (
        f'<path d="M 360 20 L 300 340 M 360 20 L 420 340" stroke="{METAL}" stroke-width="5"/>'
        + "".join(
            f'<line x1="{360 - (y - 20) * 60 / 320}" y1="{y}" x2="{360 + (y - 20) * 60 / 320}" y2="{y}" stroke="{METAL}" stroke-width="2"/>'
            for y in range(60, 340, 35)
        )
        + "".join(
            f'<line x1="{360 - (y - 20) * 60 / 320}" y1="{y}" x2="{360 + (y + 35 - 20) * 60 / 320}" y2="{y + 35}" stroke="{METAL}" stroke-width="1.5"/>'
            for y in range(60, 300, 35)
        )
        + f'<circle cx="360" cy="18" r="6" fill="{RED}"/><circle cx="360" cy="18" r="16" fill="{RED}" opacity="0.25"/>'
    )
    building = (
        '<rect x="480" y="140" width="320" height="200" fill="#2a2e3a"/>'
        + text(640, 165, "RÁDIO DO PARTIDO", size=13, fill=PAPER, weight="bold")
        + f'<rect x="560" y="170" width="80" height="170" fill="{INK}"/><rect x="566" y="176" width="68" height="164" fill="#23262c"/>'
        + f'<rect x="650" y="228" width="22" height="36" rx="2" fill="{INK}" stroke="{METAL}" stroke-width="1"/>'
        + "".join(text(655 + (i % 3) * 6, 238 + (i // 3) * 8, chr(65 + i), size=5, fill=COLD) for i in range(9))
    )
    booth = (
        '<rect x="120" y="232" width="100" height="108" fill="#3a3f4b"/><rect x="134" y="250" width="72" height="40" fill="#0d1018"/>'
        f'<rect x="110" y="224" width="120" height="10" fill="{METAL}"/>'
    )
    return svg(
        f'<rect width="800" height="400" fill="url(#night)"/>'
        + "".join(f'<circle cx="{(i * 97) % 800}" cy="{(i * 53) % 120}" r="1" fill="{PAPER}" opacity="0.6"/>' for i in range(30))
        + f"{lattice}{building}{booth}"
        + f'<rect y="340" width="800" height="60" fill="#12151d"/>',
        sky,
    )


def studio():
    panels = "".join(
        f'<rect x="{180 + col * 46}" y="{40 + row * 46}" width="40" height="40" fill="#2f2a33" stroke="#25212a" stroke-width="2"/>'
        for row in range(3)
        for col in range(8)
    )
    on_air = f'<rect x="380" y="10" width="90" height="24" rx="4" fill="#3a1416"/>' + text(425, 27, "NO AR", size=13, fill="#ff6b6b", weight="bold")
    window = (
        '<rect x="40" y="60" width="110" height="120" fill="#0d1018" stroke="#3a3f4b" stroke-width="6"/>'
        + "".join(f'<rect x="{50 + (i * 23) % 90}" y="{120 + (i * 17) % 50}" width="4" height="5" fill="{WARM}" opacity="0.7"/>' for i in range(14))
    )
    console = (
        '<rect x="180" y="300" width="170" height="12" fill="#3a3f4b"/><rect x="190" y="312" width="10" height="40" fill="#1a1d23"/>'
        '<rect x="330" y="312" width="10" height="40" fill="#1a1d23"/>'
        '<rect x="195" y="226" width="140" height="74" rx="6" fill="#2a2e36" stroke="#4a505b" stroke-width="2"/>'
        f'<circle cx="250" cy="262" r="28" fill="{PAPER}" stroke="{METAL}" stroke-width="3"/>'
        + "".join(
            f'<line x1="{250 + 22 * math.cos(a / 10)}" y1="{262 + 22 * math.sin(a / 10)}" '
            f'x2="{250 + 27 * math.cos(a / 10)}" y2="{262 + 27 * math.sin(a / 10)}" stroke="{INK}" stroke-width="1.5"/>'
            for a in range(0, 63, 6)
        )
        + f'<line x1="250" y1="262" x2="268" y2="248" stroke="{RED}" stroke-width="3"/>'
        + "".join(f'<circle cx="{300 + (i % 2) * 18}" cy="{246 + (i // 2) * 20}" r="6" fill="#1a1d23" stroke="{METAL}"/>' for i in range(4))
    )
    mic = (
        f'<rect x="447" y="200" width="6" height="120" fill="{METAL}"/><path d="M 425 320 L 475 320 L 465 330 L 435 330 Z" fill="{METAL}"/>'
        f'<rect x="436" y="170" width="28" height="42" rx="14" fill="#1b1b1f" stroke="{METAL}" stroke-width="2"/>'
        + "".join(f'<line x1="440" y1="{180 + i * 7}" x2="460" y2="{180 + i * 7}" stroke="{METAL}" stroke-width="1"/>' for i in range(4))
    )
    desk = (
        '<rect x="540" y="305" width="150" height="10" fill="#5a4636"/><rect x="550" y="315" width="8" height="40" fill="#1a1d23"/>'
        '<rect x="672" y="315" width="8" height="40" fill="#1a1d23"/>'
        '<rect x="555" y="248" width="110" height="56" rx="4" fill="#2a2e36" stroke="#4a505b" stroke-width="2"/>'
        f'<circle cx="585" cy="270" r="12" fill="#1b1b1f" stroke="{PAPER}" stroke-width="2"/><circle cx="635" cy="270" r="12" fill="#1b1b1f" stroke="{PAPER}" stroke-width="2"/>'
        + "".join(f'<rect x="{570 + i * 22}" y="290" width="14" height="8" fill="{METAL}"/>' for i in range(4))
    )
    poster = (
        f'<rect x="600" y="70" width="120" height="80" fill="{RED}"/>'
        + text(660, 96, "RÁDIO DO PARTIDO", size=10, fill=PAPER, weight="bold")
        + text(660, 128, "101.4 FM", size=20, fill=PAPER, weight="bold")
    )
    return svg(
        f'<rect width="800" height="400" fill="#211d26"/>{panels}{on_air}{window}{poster}'
        f'<rect y="340" width="800" height="60" fill="#16131a"/>{console}{mic}{desk}'
    )


def ending_voice():
    sky = (
        '<linearGradient id="dawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a2240"/>'
        '<stop offset="0.7" stop-color="#5a4a6a"/><stop offset="1" stop-color="#c98a5b"/></linearGradient>'
    )
    roofs = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{400 - y}" fill="#1d1a22"/>'
        + "".join(f'<rect x="{x + 8 + j * 16}" y="{y + 14}" width="7" height="9" fill="{WARM}" opacity="0.8"/>' for j in range(max(1, w // 16 - 1)))
        for x, y, w in [(0, 240, 90), (80, 210, 70), (150, 255, 100), (250, 225, 80), (330, 270, 120), (450, 235, 90), (540, 255, 110)]
    )
    tower = f'<path d="M 700 60 L 670 340 M 700 60 L 730 340" stroke="{METAL}" stroke-width="4"/><circle cx="700" cy="58" r="6" fill="{RED}"/>'
    waves = "".join(
        f'<path d="M {700 - r} {58 + r * 0.2} A {r} {r} 0 0 1 {700 + r} {58 + r * 0.2}" fill="none" stroke="{PAPER}" stroke-width="2" opacity="{0.7 - r / 400}"/>'
        for r in range(40, 280, 40)
    )
    return svg(
        f'<rect width="800" height="400" fill="url(#dawn)"/>{waves}{tower}{roofs}'
        f'<rect y="340" width="800" height="60" fill="#141218"/>'
        + person(360, 345, 0.95)
        + person(430, 345, 0.95, flip=True, coat=JULIA),
        sky,
    )


def ending_recognised():
    return svg(
        f'<rect width="800" height="400" fill="#1d0e10"/>'
        f'<rect x="380" y="10" width="90" height="24" rx="4" fill="#5a1416"/>' + text(425, 27, "NO AR", size=13, fill="#ff8080", weight="bold")
        + f'<rect x="600" y="60" width="150" height="280" fill="{WARM}" opacity="0.8"/><path d="M 600 60 L 570 75 L 570 355 L 600 340 Z" fill="#3a2a1c"/>'
        + person(640, 345, 1.0, flip=True, coat=POLICE)
        + person(705, 345, 1.0, flip=True, coat=POLICE)
        + f'<rect x="347" y="200" width="6" height="120" fill="{METAL}"/><rect x="336" y="170" width="28" height="42" rx="14" fill="#1b1b1f"/>'
        + person(300, 370, 1.05)
        + f'<rect y="340" width="800" height="60" fill="#120809" opacity="0.6"/><rect width="800" height="400" fill="{RED}" opacity="0.08"/>'
    )


FILES = {
    "c2_esconderijo.svg": hideout(message=True, cassette=True),
    "c2_esconderijo_sem_mensagem.svg": hideout(message=False, cassette=True),
    "c2_esconderijo_sem_cassete.svg": hideout(message=True, cassette=False),
    "c2_esconderijo_vazio.svg": hideout(message=False, cassette=False),
    "c2_cidade.svg": city(),
    "c2_torre.svg": tower(),
    "c2_estudio.svg": studio(),
    "final_c2_voz.svg": ending_voice(),
    "final_c2_reconhecido.svg": ending_recognised(),
}

if __name__ == "__main__":
    for name, content in FILES.items():
        (OUT / name).write_text(content + "\n", encoding="utf-8")
        print("wrote", name)
