#!/usr/bin/env python3
"""goddess.py: an original goddess bust (greek profile, laurel crown, chiton) drawn with cairo
as separate regions, then written as line ASCII: the outline uses / \\ | _ - by edge direction,
and each region gets its own texture. No external art is used."""
import math
import cairo

W, H = 320, 400


def regions():
    """name -> path function, in drawing priority (later wins)."""
    def drapery(c):
        c.move_to(20, 400); c.curve_to(34, 330, 92, 300, 128, 292)
        c.line_to(188, 292); c.curve_to(236, 300, 290, 330, 304, 400); c.close_path()

    def neck(c):
        c.move_to(124, 302); c.curve_to(120, 272, 118, 246, 122, 226)
        c.line_to(186, 238); c.curve_to(182, 262, 184, 284, 190, 302); c.close_path()

    def face(c):
        c.move_to(150, 58)
        c.curve_to(180, 60, 200, 80, 206, 100)
        c.line_to(238, 164); c.line_to(220, 172)
        c.curve_to(225, 178, 224, 184, 217, 190)
        c.curve_to(223, 194, 222, 200, 214, 206)
        c.curve_to(208, 210, 212, 218, 214, 226)
        c.curve_to(208, 242, 188, 246, 172, 242)
        c.line_to(120, 230); c.line_to(110, 118); c.close_path()

    def hair(c):
        c.move_to(208, 106)
        c.curve_to(200, 66, 172, 40, 132, 42)
        c.curve_to(90, 44, 64, 78, 68, 122)
        c.curve_to(70, 172, 96, 212, 126, 234)
        c.curve_to(142, 214, 148, 190, 152, 170)
        c.curve_to(160, 140, 178, 112, 208, 106); c.close_path()
        c.new_sub_path(); c.arc(62, 152, 34, 0, 2 * math.pi)

    def laurel(c):
        for i in range(12):
            t = math.radians(-24 - i * 14)
            x, y = 140 + 76 * math.cos(t), 130 + 82 * math.sin(t)
            c.save(); c.translate(x, y); c.rotate(t + math.pi / 2 + (0.6 if i % 2 else -0.6))
            c.scale(1, 0.45); c.new_sub_path(); c.arc(0, 0, 12, 0, 2 * math.pi); c.restore()

    def ear(c):
        c.save(); c.translate(152, 160); c.scale(1, 1.6); c.new_sub_path(); c.arc(0, 0, 8, 0, 2 * math.pi); c.restore()

    def eye(c):
        c.move_to(188, 126); c.curve_to(194, 120, 203, 122, 207, 129); c.curve_to(200, 131, 193, 131, 188, 126)

    def brooch(c):
        c.new_sub_path(); c.arc(208, 314, 8, 0, 2 * math.pi)

    return [("drapery", drapery), ("neck", neck), ("face", face), ("hair", hair),
            ("laurel", laurel), ("ear", ear), ("eye", eye), ("brooch", brooch)]


def coverage(path, cols, rows):
    s = cairo.ImageSurface(cairo.FORMAT_A8, W, H)
    c = cairo.Context(s)
    path(c); c.set_source_rgba(0, 0, 0, 1); c.fill()
    s.flush()
    d, st = s.get_data(), s.get_stride()
    cw, ch = W / cols, H / rows
    g = []
    for r in range(rows):
        row = []
        for k in range(cols):
            tot = n = 0
            for y in range(int(r * ch), int((r + 1) * ch), 2):
                for x in range(int(k * cw), int((k + 1) * cw), 2):
                    tot += d[y * st + x]; n += 1
            row.append(tot / n / 255)
        g.append(row)
    return g


TEXTURE = {
    "hair": lambda r, k: "~" if (r + k // 3) % 2 else "-",
    "laurel": lambda r, k: "o" if (r + k) % 2 else "*",
    "face": lambda r, k: " ",
    "neck": lambda r, k: " ",
    "ear": lambda r, k: "(",
    "eye": lambda r, k: "<",
    "brooch": lambda r, k: "@",
    "drapery": lambda r, k: "|" if k % 5 == r % 2 else ("'" if (r + k) % 7 == 0 else " "),
}


def ascii_art(cols=58, rows=34):
    regs = regions()
    cov = {n: coverage(p, cols, rows) for n, p in regs}
    label = [[None] * cols for _ in range(rows)]
    for n, _ in regs:
        for r in range(rows):
            for k in range(cols):
                if cov[n][r][k] > (0.25 if n in ("eye", "brooch", "ear") else 0.45):
                    label[r][k] = n
    fig = [[1.0 if label[r][k] else 0.0 for k in range(cols)] for r in range(rows)]

    def at(g, r, k):
        return g[min(rows - 1, max(0, r))][min(cols - 1, max(0, k))]

    out = []
    for r in range(rows):
        line = ""
        for k in range(cols):
            lb = label[r][k]
            if lb is None:
                line += " "; continue
            # silhouette outline: cell inside the figure next to the outside
            gx = at(fig, r, k + 1) - at(fig, r, k - 1)
            gy = at(fig, r + 1, k) - at(fig, r - 1, k)
            edge = abs(gx) + abs(gy) > 0 and min(at(fig, r, k - 1), at(fig, r, k + 1),
                                                   at(fig, r - 1, k), at(fig, r + 1, k)) == 0
            if not edge and lb in ("face", "neck"):
                # inner outline between the skin and the hair/drapery
                nb = {at_label for at_label in (label[max(0, r - 1)][k], label[min(rows - 1, r + 1)][k],
                                                label[r][max(0, k - 1)], label[r][min(cols - 1, k + 1)])}
                if nb - {"face", "neck", "ear", "eye"}:
                    line += "."; continue
            if edge:
                a = math.degrees(math.atan2(gy, gx)) % 180   # gradient direction
                if a < 22.5 or a >= 157.5:
                    ch = "|"
                elif a < 67.5:
                    ch = "\\" if gy * gx > 0 else "/"
                elif a < 112.5:
                    ch = "_" if gy < 0 else "-"
                else:
                    ch = "/" if gy * gx < 0 else "\\"
                if lb == "laurel":
                    ch = "o"
                line += ch
            else:
                line += TEXTURE[lb](r, k)
        out.append(line.rstrip())
    while out and not out[0].strip():
        out.pop(0)
    return out


if __name__ == "__main__":
    print("\n".join(ascii_art()))
