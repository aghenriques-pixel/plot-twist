"""Draw the event pictures (specs/story-events-notebook.md) on top of the scenes they happen in.

Run from the project folder, after art_chapter2.py and art_colour.py:
    uv run python scripts/art_events.py

Each event starts from an already coloured scene picture (so it keeps its colours and ambient
animation) and adds people, light and danger on top. Animated shapes use fill-opacity, never an
opacity attribute (see tests/test_art.py::test_animated_lights_never_turn_solid).
"""

from pathlib import Path

from art_chapter2 import bricks, person

ROOT = Path(__file__).resolve().parent.parent
SCENES = ROOT / "assets" / "scenes"

POLICE = ("#2b4c7e", "#1b3358")
SELLER = ("#7a4f8c", "#553563")

# Animations for the events only; class names start with "ev-" so they never clash
STYLE = """<style>
@keyframes ev-sweep { 0%, 100% { transform: rotate(-7deg); } 50% { transform: rotate(7deg); } }
@keyframes ev-alarm { 0%, 100% { opacity: 0.2; } 50% { opacity: 1; } }
@keyframes ev-flame { 0%, 100% { transform: scale(1, 1); } 50% { transform: scale(0.85, 1.15); } }
@keyframes ev-steam { from { transform: translateY(0); opacity: 0.8; } to { transform: translateY(-40px); opacity: 0; } }
.ev-sweep { transform-box: view-box; animation: ev-sweep 3.2s ease-in-out infinite; }
.ev-alarm { animation: ev-alarm 1.4s ease-in-out infinite; }
.ev-flame { transform-box: fill-box; transform-origin: center bottom; animation: ev-flame 0.5s ease-in-out infinite; }
.ev-steam { animation: ev-steam 2.6s linear infinite; }
</style>"""


def beam(x, y, left, right, colour="#fff4c0", strength=0.24):
    """A torch beam from (x, y) down to the floor between `left` and `right`, slowly sweeping."""
    return (
        f'<g class="ev-sweep" style="transform-origin:{x}px {y}px">'
        f'<polygon points="{x},{y} {left},400 {right},400" fill="{colour}" fill-opacity="{strength}"/>'
        f'<circle cx="{x}" cy="{y}" r="7" fill="{colour}" fill-opacity="0.9"/></g>'
    )


def danger_tint():
    return '<rect class="ev-alarm" width="800" height="400" fill="#ff2a4f" fill-opacity="0.12"/>'


def steam(x, y):
    return "".join(
        f'<circle class="ev-steam" cx="{x + dx}" cy="{y}" r="4" fill="#ffffff" fill-opacity="0.5" style="animation-delay:-{delay}s"/>'
        for dx, delay in ((-4, 0), (3, 0.9), (0, 1.8))
    )


def flame(x, y, size=1.0):
    return (
        f'<circle cx="{x}" cy="{y - 6 * size}" r="{26 * size}" fill="#ffb347" fill-opacity="0.18"/>'
        f'<ellipse class="ev-flame" cx="{x}" cy="{y - 6 * size}" rx="{4 * size}" ry="{8 * size}" fill="#ffd36e"/>'
    )


def archive_footsteps():
    return (
        # light from the corridor through the door left ajar, and the guard in the doorway
        '<polygon points="0,110 46,120 300,400 0,400" fill="#ffe7a3" fill-opacity="0.16"/>'
        + person(28, 368, 1.0, coat=POLICE)
        + beam(46, 250, 260, 520)
        + danger_tint()
    )


def tunnel_patrol():
    return (
        person(420, 340, 0.62, flip=True, coat=POLICE)
        + person(470, 342, 0.66, flip=True, coat=POLICE)
        + beam(452, 268, 140, 360, strength=0.28)
        + danger_tint()
    )


def tunnel_dead_end():
    wall = bricks(215, 90, 625, 360, "#4a3a33")
    return (
        '<rect width="800" height="400" fill="#05030f" fill-opacity="0.45"/>'
        f'<rect x="215" y="90" width="410" height="270" fill="#2e2420"/>{wall}'
        # candle stub and the tin box in a crack of the wall
        '<rect x="325" y="338" width="10" height="18" fill="#efe3c2"/>'
        + flame(330, 338, 0.9)
        + '<rect x="488" y="270" width="54" height="34" rx="3" fill="#8a4b2a"/>'
        '<rect x="488" y="270" width="54" height="8" rx="3" fill="#a8623a"/>'
        '<circle cx="515" cy="287" r="30" fill="#ffd36e" fill-opacity="0.08"/>'
    )


def factory_patrol():
    return (
        person(610, 385, 0.92, flip=True, coat=POLICE)
        + person(668, 385, 0.92, flip=True, coat=POLICE)
        + person(722, 385, 0.92, flip=True, coat=POLICE)
        + beam(596, 300, 120, 380, strength=0.26)
        + danger_tint()
    )


def market_alley():
    stripes = "".join(
        f'<polygon points="{440 + i * 20},178 {460 + i * 20},178 {464 + i * 20},206 {444 + i * 20},206" '
        f'fill="{"#e85d75" if i % 2 else "#f7e8c4"}"/>'
        for i in range(8)
    )
    return (
        # the guards far away at their brazier
        person(690, 352, 0.6, coat=POLICE)
        + person(745, 352, 0.6, flip=True, coat=POLICE)
        + '<rect x="708" y="330" width="24" height="22" fill="#3a3030"/>'
        + flame(720, 330, 1.6)
        # the coffee stall, much closer
        + f'<rect x="446" y="206" width="6" height="150" fill="#3b2f2a"/><rect x="594" y="206" width="6" height="150" fill="#3b2f2a"/>{stripes}'
        + '<rect x="452" y="300" width="142" height="14" fill="#6b4a32"/><rect x="460" y="314" width="126" height="50" fill="#4e3626"/>'
        + person(522, 385, 0.95, flip=True, coat=SELLER)
        + '<rect x="560" y="282" width="16" height="18" rx="3" fill="#c0c7d2"/>'
        + steam(568, 278)
    )


def night_round():
    return (
        # the cleaning cupboard between cells 15 and 16, and the guard coming out of 15
        '<rect x="272" y="180" width="46" height="160" fill="#4a3a2c"/><rect x="276" y="184" width="38" height="152" fill="#6b4a2f"/>'
        '<circle cx="306" cy="262" r="3" fill="#ffd36e"/>'
        + person(230, 382, 1.0, coat=POLICE)
        + beam(252, 250, 360, 640)
        + danger_tint()
    )


EVENTS = {
    "arquivo_passos.svg": ("arquivo.svg", archive_footsteps),
    "tunel_patrulha.svg": ("tunel.svg", tunnel_patrol),
    "tunel_beco.svg": ("tunel.svg", tunnel_dead_end),
    "c2_patrulha.svg": ("c2_cidade.svg", factory_patrol),
    "c2_mercado.svg": ("c2_cidade.svg", market_alley),
    "c3_ronda.svg": ("c3_corredor.svg", night_round),
}


def draw(base, overlay):
    text = (SCENES / base).read_text(encoding="utf-8")
    # The new shapes go before the scene's own style and ambient light, so the vignette stays on top
    at = text.index("<style")
    return text[:at] + STYLE + overlay() + text[at:]


if __name__ == "__main__":
    for name, (base, overlay) in EVENTS.items():
        (SCENES / name).write_text(draw(base, overlay), encoding="utf-8")
        print("wrote", name)
