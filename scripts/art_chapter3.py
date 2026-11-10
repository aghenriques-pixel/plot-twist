"""Draw the level 3 illustrations (specs/level-3.md) as SVG files in assets/scenes/.

Run from the project folder, then colour them and draw the events on top:
    uv run python scripts/art_chapter3.py
    uv run python scripts/art_colour.py
    uv run python scripts/art_events.py

Same comic as chapter 2: people come from assets/character.svg, recoloured. Every picture is 800x400,
and the clickable spots in logic.py match the coordinates used here.
"""

from art_chapter2 import INK, METAL, OUT, PAPER, RED, TOMAS, WARM, bricks, person, svg, text

CLARA = ("#8c3b5e", "#5e2640")
POLICE = ("#2b4c7e", "#1b3358")

# Animations only these pictures use (art_colour.py adds the shared ones later)
STYLE = """<style>
@keyframes c3-search { 0%, 100% { transform: rotate(-18deg); } 50% { transform: rotate(18deg); } }
@keyframes c3-led { 0%, 100% { opacity: 1; } 50% { opacity: 0.2; } }
@keyframes c3-alarm { 0%, 100% { opacity: 0.2; } 50% { opacity: 1; } }
.c3-search { transform-box: view-box; transform-origin: 90px 62px; animation: c3-search 8s ease-in-out infinite; }
.c3-led { animation: c3-led 1s steps(1) infinite; }
.c3-alarm { animation: c3-alarm 1.4s ease-in-out infinite; }
</style>"""


def night_sky():
    return '<rect width="800" height="400" fill="#0b0f1c"/>'


def searchlight():
    return (
        f'<rect x="72" y="62" width="36" height="270" fill="{METAL}"/><rect x="62" y="48" width="56" height="18" rx="4" fill="#343a44"/>'
        '<g class="c3-search"><polygon points="90,62 250,340 380,340" fill="#fff4c0" fill-opacity="0.13"/></g>'
        '<circle cx="90" cy="58" r="10" fill="#fff4c0"/>'
    )


def yard(uniform=True):
    hanging = (
        '<path d="M500 214 h30 l10 14 -8 6 v50 h-34 v-50 l-8 -6 Z" fill="#9c9483"/>'
        '<path d="M512 214 l3 10 3 -10" fill="none" stroke="#565c66" stroke-width="2"/>'
        if uniform
        else ""
    )
    return svg(
        STYLE
        + night_sky()
        # the Ministry of Love: a wall with no windows at all
        + '<rect x="130" y="30" width="670" height="300" fill="#2a2e35"/>'
        + '<rect x="130" y="30" width="670" height="22" fill="#343a44"/>'
        + text(470, 46, "MINISTRY OF LOVE", 13, PAPER, weight="bold")
        + '<rect y="330" width="800" height="70" fill="#1a1e28"/>'
        + searchlight()
        # notice by the door
        + f'<rect x="595" y="115" width="70" height="55" fill="{PAPER}"/>'
        + text(630, 133, "WING B", 9, INK, weight="bold")
        + text(630, 150, "GUARD CHANGE", 6, INK)
        + text(630, 162, "03:15", 10, RED, weight="bold")
        # the laundry van, back doors open
        + '<rect x="300" y="230" width="44" height="105" rx="8" fill="#a8956c"/><rect x="306" y="240" width="30" height="30" fill="#8fb3cc"/>'
        + '<rect x="330" y="195" width="230" height="140" rx="10" fill="#d8d0bb"/>'
        + text(410, 230, "LAUNDRY", 16, RED, weight="bold")
        + '<rect x="478" y="203" width="78" height="100" fill="#1b1b1f"/>' + hanging
        + '<rect x="556" y="200" width="12" height="108" fill="#a8956c"/>'
        + f'<rect x="355" y="248" width="56" height="38" fill="{PAPER}"/>'
        + "".join(f'<line x1="360" y1="{258 + i * 7}" x2="405" y2="{258 + i * 7}" stroke="{INK}" stroke-width="1"/>' for i in range(4))
        + f'<circle cx="372" cy="337" r="22" fill="{INK}"/><circle cx="520" cy="337" r="22" fill="{INK}"/>'
        + '<circle cx="372" cy="337" r="8" fill="#8a8f98"/><circle cx="520" cy="337" r="8" fill="#8a8f98"/>'
        # service door with a keypad
        + '<rect x="690" y="160" width="80" height="172" fill="#3b4048"/><rect x="698" y="168" width="64" height="156" fill="#454b55"/>'
        + '<rect x="742" y="238" width="16" height="22" rx="2" fill="#1b1b1f"/><circle class="c3-led" cx="750" cy="244" r="3" fill="#2ecc71"/>'
        + f'<rect x="700" y="146" width="60" height="8" fill="{WARM}"/>'
        + person(220, 380, 1.0, coat=TOMAS)
    )


def corridor():
    doors = ""
    for number, centre in zip((15, 16, 17, 18), (230, 360, 490, 620)):
        doors += (
            f'<rect x="{centre - 40}" y="150" width="80" height="190" fill="{METAL}"/>'
            f'<rect x="{centre - 34}" y="156" width="68" height="178" fill="#565c66"/>'
            f'<rect x="{centre - 15}" y="196" width="30" height="12" fill="{INK}"/>'
            f'<circle cx="{centre + 24}" cy="260" r="4" fill="#8a8f98"/>'
            + text(centre, 142, f"B-{number}", 12, PAPER, weight="bold")
        )
    lamps = "".join(
        f'<rect x="{x - 20}" y="12" width="40" height="8" fill="{PAPER}"/><circle cx="{x}" cy="24" r="40" fill="{WARM}" fill-opacity="0.12"/>'
        for x in (150, 420, 680)
    )
    return svg(
        '<rect width="800" height="340" fill="#2a2e3a"/><rect y="320" width="800" height="20" fill="#1f2b35"/>'
        '<rect y="340" width="800" height="60" fill="#1a1d23"/>'
        + lamps
        + doors
        # roster board
        + f'<rect x="75" y="115" width="80" height="60" fill="{PAPER}"/>'
        + text(115, 130, "ROSTER", 8, INK, weight="bold")
        + "".join(f'<line x1="82" y1="{140 + i * 8}" x2="148" y2="{140 + i * 8}" stroke="{INK}" stroke-width="1"/>' for i in range(4))
        # laundry cart by the entrance
        + '<rect x="62" y="285" width="80" height="50" rx="6" fill="#8a8f98"/>'
        + f'<path d="M66 288 q10 -16 20 0 q10 -16 20 0 q10 -16 20 0 q8 -14 14 0" fill="{PAPER}"/>'
        + f'<circle cx="74" cy="340" r="6" fill="{INK}"/><circle cx="130" cy="340" r="6" fill="{INK}"/>'
        # radio on a stool
        + '<rect x="675" y="320" width="26" height="20" fill="#5a4636"/><rect x="668" y="300" width="40" height="22" rx="3" fill="#6b4a2f"/>'
        + f'<circle cx="680" cy="311" r="5" fill="{PAPER}"/>'
        # the officer's door, ajar, at the end
        + '<rect x="715" y="150" width="70" height="190" fill="#6b5236"/><rect x="715" y="150" width="8" height="190" fill="#ffd36e" fill-opacity="0.6"/>'
        + text(750, 142, "OFFICER", 8, PAPER, weight="bold")
        # the way back to the yard
        + '<rect x="0" y="130" width="40" height="210" fill="#141821"/>'
    )


def cell(clara=True):
    marks = ""
    for group in range(6):
        x = 252 + group * 18
        for row in range(3):
            y = 150 + row * 26
            marks += "".join(
                f'<line x1="{x + i * 3}" y1="{y}" x2="{x + i * 3}" y2="{y + 14}" stroke="{PAPER}" stroke-width="1.2" stroke-opacity="0.6"/>'
                for i in range(4)
            ) + f'<line x1="{x - 2}" y1="{y + 12}" x2="{x + 12}" y2="{y + 2}" stroke="{PAPER}" stroke-width="1.2" stroke-opacity="0.6"/>'
    return svg(
        '<rect width="800" height="340" fill="#2f2a33"/><rect y="340" width="800" height="60" fill="#1d1a22"/>'
        + bricks(0, 0, 800, 340, "#25212a")
        # barred window and moonlight
        + '<rect x="610" y="60" width="80" height="60" fill="#0b0f1c"/>'
        + "".join(f'<rect x="{616 + i * 16}" y="60" width="4" height="60" fill="{METAL}"/>' for i in range(5))
        + '<polygon points="610,120 690,120 600,340 470,340" fill="#8fb3cc" fill-opacity="0.12"/>'
        + marks
        # bed and bucket
        + '<rect x="590" y="300" width="180" height="16" fill="#5a4636"/><rect x="596" y="288" width="168" height="14" fill="#9c9483"/>'
        + '<rect x="598" y="316" width="8" height="26" fill="#3a2f26"/><rect x="754" y="316" width="8" height="26" fill="#3a2f26"/>'
        + '<path d="M140 320 h30 l-4 26 h-22 Z" fill="#8a8f98"/>'
        # the open door to the corridor
        + '<rect x="0" y="120" width="44" height="220" fill="#ffd36e" fill-opacity="0.25"/>'
        + (person(520, 380, 0.95, flip=True, coat=CLARA) if clara else "")
    )


def office(open_safe=False):
    safe = (
        '<rect x="620" y="240" width="85" height="105" fill="#1b1b1f"/>'
        '<rect x="700" y="236" width="18" height="112" fill="#3f5b4a"/>'
        if open_safe
        else '<rect x="620" y="240" width="85" height="105" rx="4" fill="#3f5b4a"/>'
        f'<circle cx="662" cy="285" r="16" fill="#8a8f98"/><circle cx="662" cy="285" r="4" fill="{INK}"/>'
        '<rect x="690" y="300" width="8" height="24" fill="#8a8f98"/>'
    )
    return svg(
        '<rect width="800" height="340" fill="#3a2f26"/><rect y="340" width="800" height="60" fill="#241c16"/>'
        + "".join(f'<rect x="{x}" y="0" width="4" height="340" fill="#2a2321"/>' for x in range(60, 800, 90))
        # portrait of the Leader
        + f'<rect x="362" y="52" width="86" height="112" fill="{WARM}"/><rect x="370" y="60" width="70" height="96" fill="#2f3b2f"/>'
        + f'<circle cx="405" cy="96" r="16" fill="#c8a88a"/><rect x="389" y="114" width="32" height="34" fill="{INK}"/>'
        + '<rect x="395" y="99" width="20" height="4" fill="#1a1a1a"/>'
        # desk, lamp, note and photograph
        + '<rect x="290" y="276" width="250" height="16" fill="#5a4636"/><rect x="300" y="292" width="20" height="50" fill="#4a3a2c"/>'
        + '<rect x="510" y="292" width="20" height="50" fill="#4a3a2c"/>'
        + f'<rect x="476" y="226" width="6" height="50" fill="{METAL}"/><path d="M458 226 h42 l-10 -22 h-22 Z" fill="#7a2a2a"/>'
        + f'<circle cx="479" cy="236" r="70" fill="{WARM}" fill-opacity="0.12"/>'
        + f'<rect x="452" y="245" width="42" height="26" fill="{WARM}"/>'
        + "".join(f'<line x1="456" y1="{252 + i * 6}" x2="490" y2="{252 + i * 6}" stroke="{INK}" stroke-width="1"/>' for i in range(3))
        + '<rect x="320" y="238" width="40" height="38" fill="#8a8f98"/><rect x="325" y="243" width="30" height="28" fill="#d8cfb6"/>'
        + f'<circle cx="340" cy="252" r="5" fill="#c8a88a"/><path d="M332 270 l8 -12 8 12 Z" fill="{RED}"/>'
        + safe
        # door back to the corridor
        + '<rect x="0" y="130" width="40" height="210" fill="#1a1615"/>'
    )


def gate():
    stripes = "".join(
        f'<rect x="{640 + i * 20}" y="255" width="20" height="12" fill="{RED if i % 2 else PAPER}"/>' for i in range(8)
    )
    return svg(
        STYLE
        + night_sky()
        + '<rect x="0" y="40" width="460" height="300" fill="#2a2e35"/>'
        + '<rect y="330" width="800" height="70" fill="#1a1e28"/>'
        # the street beyond, where the van waits with its lights off
        + '<rect x="700" y="300" width="90" height="34" rx="6" fill="#a8956c"/><circle cx="716" cy="336" r="8" fill="{INK}"/>'.replace("{INK}", INK)
        # booth with a single bulb
        + '<rect x="610" y="170" width="80" height="165" fill="#3b4048"/><rect x="622" y="190" width="56" height="40" fill="#8fb3cc"/>'
        + f'<circle cx="650" cy="166" r="6" fill="{WARM}"/><circle cx="650" cy="166" r="60" fill="{WARM}" fill-opacity="0.12"/>'
        + f'<rect x="632" y="250" width="8" height="85" fill="{METAL}"/>' + stripes
        # laundry cart
        + '<rect x="235" y="285" width="110" height="52" rx="6" fill="#8a8f98"/>'
        + f'<path d="M238 288 q12 -20 24 0 q12 -20 24 0 q12 -20 24 0 q12 -18 32 0" fill="{PAPER}"/>'
        + f'<circle cx="250" cy="342" r="7" fill="{INK}"/><circle cx="330" cy="342" r="7" fill="{INK}"/>'
        + person(560, 385, 1.0, flip=True, coat=POLICE)
        + '<rect class="c3-alarm" width="800" height="400" fill="#ff2a4f" fill-opacity="0.1"/>'
    )


def dawn(defs_id):
    return (
        f'<linearGradient id="{defs_id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b2a78"/>'
        '<stop offset="0.6" stop-color="#ff8c69"/><stop offset="1" stop-color="#ffd36e"/></linearGradient>'
    )


def ending_names():
    pages = "".join(
        f'<rect x="{x}" y="{y}" width="14" height="18" fill="{PAPER}" transform="rotate({r} {x} {y})"/>'
        for x, y, r in ((180, 90, -20), (260, 60, 15), (560, 80, -10), (640, 120, 25), (720, 70, -30))
    )
    return svg(
        '<rect width="800" height="400" fill="url(#dawn9)"/>'
        + '<circle cx="400" cy="300" r="70" fill="#fff4c0" fill-opacity="0.7"/>'
        + "".join(f'<rect x="{x}" y="{260 - h}" width="60" height="{h + 80}" fill="#2a2e35"/>' for x, h in ((0, 80), (70, 40), (620, 60), (690, 100)))
        + '<rect y="330" width="800" height="70" fill="#1d1a22"/>'
        + person(330, 345, 0.9)
        + person(395, 345, 0.9, flip=True, coat=TOMAS)
        + person(455, 345, 0.85, flip=True, coat=CLARA)
        + '<rect x="318" y="268" width="26" height="18" fill="#7a2a2a"/>'
        + pages,
        dawn("dawn9"),
    )


def ending_two():
    return svg(
        '<rect width="800" height="400" fill="url(#dawn10)"/>'
        + '<circle cx="620" cy="300" r="60" fill="#fff4c0" fill-opacity="0.6"/>'
        # the Ministry behind, still dark, one lit slit
        + '<rect x="40" y="90" width="260" height="250" fill="#2a2e35"/><rect x="160" y="150" width="8" height="40" fill="#ffd36e"/>'
        + '<polygon points="300,400 380,330 440,330 800,400" fill="#3a3f4b"/>'
        + '<rect y="330" width="800" height="10" fill="#1d1a22"/>'
        + '<rect x="560" y="345" width="70" height="30" rx="6" fill="#a8956c"/>'
        + f'<circle cx="575" cy="377" r="7" fill="{INK}"/><circle cx="615" cy="377" r="7" fill="{INK}"/>',
        dawn("dawn10"),
    )


FILES = {
    "c3_patio.svg": yard(uniform=True),
    "c3_patio_sem_uniforme.svg": yard(uniform=False),
    "c3_corredor.svg": corridor(),
    "c3_cela.svg": cell(clara=True),
    "c3_cela_vazia.svg": cell(clara=False),
    "c3_gabinete.svg": office(open_safe=False),
    "c3_gabinete_aberto.svg": office(open_safe=True),
    "c3_portao.svg": gate(),
    "final_c3_nomes.svg": ending_names(),
    "final_c3_dois.svg": ending_two(),
}

if __name__ == "__main__":
    for name, content in FILES.items():
        (OUT / name).write_text(content + "\n", encoding="utf-8")
        print("wrote", name)
