#!/usr/bin/env python3
"""build.py: writes assets/profile.svg, the profile card (terminal glass over a blurred backdrop).
Edit the FETCH list or assets/goddess.txt and run:  python3 scripts/build.py"""
import html
import os

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = open(os.path.join(AQUI, "assets", "goddess.txt")).read().rstrip("\n").split("\n")

PASTEL = {"rosa": "#e894a0", "azul": "#a6c7ee", "pessego": "#f2b58f", "verde": "#bad6a1",
          "lilas": "#c9a6eb", "amarelo": "#f0d499"}
TEXTO, APAGADO, LINHA = "#ececec", "#9a9aa2", "rgba(255,255,255,0.16)"
MONO = "'JetBrains Mono','Adwaita Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

FETCH = [
    ("user", "Sapyst", "rosa"),
    ("os", "Arch Aero OS", "azul"),
    ("wm", "Hyprland", "pessego"),
    ("shell", "bash", "verde"),
    ("term", "kitty", "lilas"),
    ("font", "Adwaita Mono", "amarelo"),
    ("theme", "terminal glass", "rosa"),
    ("muses", "Athena . Artemis . Selene", "azul"),
    ("now", "ascii-walls", "verde"),
]

W, H = 960, 560
FS, LH, CW = 11.5, 15.2, 6.92          # art font size, line height, char width (approx.)


def esc(s):
    return html.escape(s, quote=False)


def cor_arte(ch):
    if ch in "o*,":
        return PASTEL["verde"]                 # laurel
    if ch == "@":
        return PASTEL["amarelo"]               # gold pins
    if ch == "~":
        return "#b9b2c9"                       # hair
    if ch == "(" or ch == "=" or ch == "<":
        return PASTEL["pessego"]
    return TEXTO


def linha_arte(s, x, y):
    """One art line as tspans grouped by color (keeps xml:space so columns line up)."""
    partes, atual, buf = [], None, ""
    for ch in s:
        c = cor_arte(ch) if ch != " " else atual
        if c != atual and buf:
            partes.append((atual, buf)); buf = ""
        atual = c; buf += ch
    if buf:
        partes.append((atual, buf))
    spans = "".join(f'<tspan fill="{c or TEXTO}">{esc(t)}</tspan>' for c, t in partes)
    return f'<text x="{x}" y="{y:.1f}" xml:space="preserve">{spans}</text>'


def quadro(x, y, w, h, titulo, cor):
    """TUI frame: straight inner lines, title in a gap of the top border."""
    tw = len(titulo) * 7.4 + 14
    return (f'<path d="M{x + 14 + tw} {y} H{x + w} V{y + h} H{x} V{y} H{x + 14}" fill="none" '
            f'stroke="{LINHA}" stroke-width="1"/>'
            f'<text x="{x + 21}" y="{y + 4.5}" font-size="12" fill="{cor}" font-weight="600">{esc(titulo)}</text>')


def svg():
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="{MONO}">')
    o.append('<defs>'
             '<filter id="desfoque" x="-50%" y="-50%" width="200%" height="200%">'
             '<feGaussianBlur stdDeviation="60"/></filter>'
             '<filter id="sombra" x="-10%" y="-10%" width="120%" height="130%">'
             '<feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000" flood-opacity="0.35"/></filter>'
             '<clipPath id="cartao"><rect width="100%" height="100%" rx="18"/></clipPath>'
             '</defs>')
    o.append('<style>'
             '.cursor{animation:pisca 1.1s steps(1) infinite}'
             '@keyframes pisca{50%{opacity:0}}'
             '.flutua{animation:flutua 14s ease-in-out infinite alternate}'
             '.flutua2{animation:flutua 18s ease-in-out infinite alternate-reverse}'
             '@keyframes flutua{from{transform:translate(0,0)}to{transform:translate(60px,-30px)}}'
             '@media (prefers-reduced-motion: reduce){.cursor,.flutua,.flutua2{animation:none}}'
             '</style>')
    # backdrop: dark wallpaper with soft pastel lights, heavily blurred
    o.append('<g clip-path="url(#cartao)">')
    o.append('<rect width="100%" height="100%" fill="#121318"/>')
    o.append('<g filter="url(#desfoque)" opacity="0.75">'
             f'<circle class="flutua" cx="170" cy="140" r="150" fill="{PASTEL["lilas"]}"/>'
             f'<circle class="flutua2" cx="820" cy="110" r="130" fill="{PASTEL["azul"]}"/>'
             f'<circle class="flutua" cx="640" cy="470" r="150" fill="{PASTEL["pessego"]}" opacity="0.7"/>'
             f'<circle class="flutua2" cx="260" cy="500" r="120" fill="{PASTEL["rosa"]}" opacity="0.7"/>'
             '</g>')
    # glass window (theme color at 62%, 1px light outline)
    o.append(f'<rect x="28" y="28" width="{W - 56}" height="{H - 56}" rx="14" fill="rgba(30,30,34,0.62)" '
             f'stroke="{LINHA}" filter="url(#sombra)"/>')
    # title bar: the system window buttons + title
    o.append(f'<g font-size="13" fill="{TEXTO}">'
             '<text x="48" y="56">✖</text><text x="68" y="56">▲</text>'
             '<text x="88" y="56">▼</text><text x="108" y="56">●</text></g>')
    o.append(f'<text x="{W / 2}" y="56" text-anchor="middle" font-size="12.5" fill="{APAGADO}">kitty — sapyst@aero</text>')
    o.append(f'<line x1="28" y1="72" x2="{W - 28}" y2="72" stroke="{LINHA}"/>')

    # left frame: the goddess
    ax, ay = 52, 96
    aw = 54 * CW + 24
    ah = len(ART) * LH + 26
    o.append(quadro(ax, ay, aw, ah, "goddess.txt", PASTEL["lilas"]))
    o.append(f'<g font-size="{FS}">')
    for i, l in enumerate(ART):
        o.append(linha_arte(l, ax + 12, ay + 24 + i * LH))
    o.append('</g>')

    # right column
    rx = ax + aw + 22
    rw = W - 52 - rx
    y = ay
    o.append(f'<text x="{rx}" y="{y + 4}" font-size="13" xml:space="preserve">'
             f'<tspan fill="{PASTEL["rosa"]}">sapyst</tspan><tspan fill="{APAGADO}">@</tspan>'
             f'<tspan fill="{PASTEL["azul"]}">aero</tspan><tspan fill="{APAGADO}"> ~ </tspan>'
             f'<tspan fill="{PASTEL["verde"]}">❯</tspan><tspan fill="{TEXTO}"> fetch --goddess</tspan></text>')
    fy = y + 26
    fh = len(FETCH) * 21 + 22
    o.append(quadro(rx, fy, rw, fh, "system", PASTEL["azul"]))
    for i, (k, v, c) in enumerate(FETCH):
        yy = fy + 28 + i * 21
        o.append(f'<text x="{rx + 16}" y="{yy}" font-size="13"><tspan fill="{PASTEL[c]}">{esc(k)}</tspan>'
                 f'<tspan x="{rx + 86}" fill="{APAGADO}">•</tspan>'
                 f'<tspan x="{rx + 104}" fill="{TEXTO}">{esc(v)}</tspan></text>')
    # palette
    py = fy + fh + 18
    o.append(quadro(rx, py, rw, 50, "palette", PASTEL["pessego"]))
    for i, c in enumerate(PASTEL.values()):
        o.append(f'<rect x="{rx + 16 + i * ((rw - 32) / 6)}" y="{py + 18}" width="{(rw - 32) / 6 - 8}" height="18" fill="{c}"/>')
    # oracle line + prompt with blinking cursor
    qy = py + 50 + 18
    o.append(quadro(rx, qy, rw, 58, "oracle", PASTEL["amarelo"]))
    o.append(f'<text x="{rx + 16}" y="{qy + 25}" font-size="12.5" fill="{TEXTO}">know thyself.</text>')
    o.append(f'<text x="{rx + 16}" y="{qy + 44}" font-size="11.5" fill="{APAGADO}">— temple of Apollo, Delphi</text>')
    cy = ay + ah
    o.append(f'<text x="{rx}" y="{cy}" font-size="13" xml:space="preserve"><tspan fill="{PASTEL["verde"]}">❯</tspan>'
             f'<tspan class="cursor" fill="{TEXTO}"> █</tspan></text>')
    o.append('</g></svg>')
    return "\n".join(o)


if __name__ == "__main__":
    with open(os.path.join(AQUI, "assets", "profile.svg"), "w") as f:
        f.write(svg())
    print("assets/profile.svg written")
