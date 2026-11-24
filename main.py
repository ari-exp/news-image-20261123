"""Draw a black-and-white newspaper front page summing up 23 November 2026.

Python 3.13 standard library only.  All pixels are generated here; the PNG
encoder, the bitmap font and every drawing primitive are implemented locally.
"""

import os
import struct
import zlib

WIDTH = HEIGHT = 1024
WHITE = 255
BLACK = 0

# ---------------------------------------------------------------------------
# 5x7 bitmap font.  Each glyph is seven rows of five bits, MSB on the left.
# ---------------------------------------------------------------------------

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000",) * 7,
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
}

GLYPH_W = 5
GLYPH_H = 7


class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray([WHITE]) * (width * height)

    def put(self, x, y, value=BLACK):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y * self.width + x] = value

    def rect(self, x0, y0, x1, y1):
        for y in range(max(0, y0), min(self.height, y1 + 1)):
            base = y * self.width
            for x in range(max(0, x0), min(self.width, x1 + 1)):
                self.pixels[base + x] = BLACK

    def frame(self, x0, y0, x1, y1):
        self.rect(x0, y0, x1, y0)
        self.rect(x0, y1, x1, y1)
        self.rect(x0, y0, x0, y1)
        self.rect(x1, y0, x1, y1)

    def line(self, x0, y0, x1, y1, weight=1):
        """Bresenham line with an optional square pen."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - weight // 2, y0 - weight // 2,
                      x0 + weight // 2, y0 + weight // 2)
            if x0 == x1 and y0 == y1:
                break
            doubled = 2 * err
            if doubled > -dy:
                err -= dy
                x0 += sx
            if doubled < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, radius, weight=1, fill=False):
        if fill:
            for y in range(cy - radius, cy + radius + 1):
                for x in range(cx - radius, cx + radius + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius:
                        self.put(x, y)
            return
        x, y, err = radius, 0, 1 - radius
        while x >= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.rect(px - weight // 2, py - weight // 2,
                          px + weight // 2, py + weight // 2)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def text_width(self, text, scale=1):
        if not text:
            return 0
        return (len(text) * (GLYPH_W + 1) - 1) * scale

    def text(self, x, y, text, scale=1, centered=False):
        """Draw text with top-left at (x, y); one-pixel glyph spacing at 1x."""
        text = text.upper()
        width = self.text_width(text, scale)
        if centered:
            x -= width // 2
        for index, char in enumerate(text):
            glyph = FONT.get(char, FONT["?"])
            gx = x + index * (GLYPH_W + 1) * scale
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.rect(gx + col * scale, y + row * scale,
                                  gx + (col + 1) * scale - 1,
                                  y + (row + 1) * scale - 1)
        return width

    def fit_text(self, x, y, max_width, text, scale):
        """Shrink the scale until the string fits; returns the scale used."""
        while scale > 1 and self.text_width(text, scale) > max_width:
            scale -= 1
        self.text(x, y, text, scale)
        return scale


def png_bytes(canvas):
    """Encode one 8-bit grayscale PNG with zlib and struct."""
    raw = bytearray()
    stride = canvas.width
    for y in range(canvas.height):
        raw.append(0)
        raw.extend(canvas.pixels[y * stride:(y + 1) * stride])

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    header = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 0, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Line-art drawings.  Each receives a Canvas and the panel's drawing box.
# ---------------------------------------------------------------------------

def draw_globe(c, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    radius = min(w, h) // 2 - 4
    c.circle(cx, cy, radius, 5)
    c.line(cx - radius, cy, cx + radius, cy, 3)
    c.line(cx, cy - radius, cx, cy + radius, 3)
    c.line(cx - 27, cy - 52, cx - 20, cy - 56, 3)
    c.line(cx + 12, cy - 50, cx + 22, cy - 44, 3)
    c.line(cx + 36, cy - 20, cx + 43, cy - 8, 3)
    c.line(cx - 44, cy + 20, cx - 36, cy + 34, 3)
    c.line(cx - 8, cy - radius + 3, cx - 24, cy - 20, 5)
    c.line(cx - 24, cy - 20, cx + 6, cy - 2, 5)
    c.line(cx + 6, cy - 2, cx - 12, cy + 28, 5)
    c.line(cx - 12, cy + 28, cx + 6, cy + radius - 3, 5)


def draw_ship(c, x, y, w, h):
    cx = x + w // 2
    deck = y + h // 2 - 8
    c.line(x + 6, deck, cx - 6, deck, 3)
    c.line(cx - 6, deck, cx - 14, deck + 18, 3)
    c.line(cx - 14, deck + 18, x + 16, deck + 18, 3)
    c.line(x + 16, deck + 18, x + 6, deck, 3)
    c.line(cx + 8, deck, cx + 22, deck - 6, 3)
    c.line(cx + 22, deck - 6, cx + 28, deck + 10, 3)
    c.line(cx + 28, deck + 10, cx + 6, deck + 10, 3)
    c.line(cx + 14, deck - 4, cx + 14, deck - 30, 3)
    c.line(cx + 14, deck - 30, cx + 32, deck - 24, 2)
    c.line(cx + 32, deck - 24, cx + 14, deck - 18, 2)
    c.line(x + 4, deck + 26, x + 20, deck + 22, 2)
    c.line(x + 20, deck + 22, x + 38, deck + 28, 2)
    c.line(x + 38, deck + 28, x + 56, deck + 22, 2)
    c.line(x + 56, deck + 22, x + w - 4, deck + 28, 2)
    c.line(x + 4, deck + 36, x + 24, deck + 32, 2)
    c.line(x + 24, deck + 32, x + 44, deck + 38, 2)
    c.line(x + 44, deck + 38, x + w - 4, deck + 32, 2)


def draw_apartment(c, x, y, w, h):
    cx = x + w // 2
    left, right = cx - 34, cx + 34
    top, bottom = y + 2, y + h - 6
    c.frame(left, top, right, bottom)
    c.rect(left - 6, bottom, right + 6, bottom + 4)
    c.line(left, top, cx - 8, top - 12, 2)
    c.line(cx - 8, top - 12, right, top, 2)
    for row_y in (top + 10, top + 29, top + 48):
        for col_x in (left + 10, cx - 5, right - 17):
            c.frame(col_x, row_y, col_x + 12, row_y + 12)
    c.line(cx - 26, top + 6, cx - 15, top + 22, 4)
    c.line(cx - 15, top + 22, cx - 4, top + 11, 4)
    c.line(cx - 4, top + 11, cx + 10, top + 30, 4)
    c.line(cx - 30, top + 40, cx - 18, top + 52, 3)
    c.line(cx + 12, top + 44, cx + 26, top + 61, 3)
    c.circle(cx - 20, top + 30, 4, 2)
    c.circle(cx + 16, top + 18, 3, 2)


def draw_chip(c, x, y, w, h):
    cx, cy = x + w // 2 - 30, y + h // 2
    c.frame(cx - 26, cy - 22, cx + 26, cy + 22)
    c.frame(cx - 13, cy - 11, cx + 13, cy + 11)
    for offset in (-14, 0, 14):
        c.line(cx + offset, cy - 22, cx + offset, cy - 30, 2)
        c.line(cx + offset, cy + 22, cx + offset, cy + 30, 2)
        c.line(cx - 26, cy + offset, cx - 34, cy + offset, 2)
        c.line(cx + 26, cy + offset, cx + 34, cy + offset, 2)
    c.line(cx - 6, cy + 7, cx - 6, cy - 7, 3)
    c.line(cx - 6, cy - 7, cx + 2, cy - 7, 3)
    c.line(cx + 2, cy - 7, cx - 3, cy + 1, 3)
    c.line(cx - 3, cy + 1, cx + 7, cy + 1, 3)
    c.line(x + w - 52, y + h - 10, x + w - 4, y + h - 10, 2)
    c.line(x + w - 50, y + h - 14, x + w - 50, y + 8, 2)
    c.line(x + w - 47, y + h - 22, x + w - 32, y + h - 34, 3)
    c.line(x + w - 32, y + h - 34, x + w - 19, y + h - 24, 3)
    c.line(x + w - 19, y + h - 24, x + w - 7, y + 10, 3)
    c.line(x + w - 20, y + 10, x + w - 7, y + 10, 3)
    c.line(x + w - 7, y + 10, x + w - 7, y + 23, 3)


def draw_ballot(c, x, y, w, h):
    cx = x + w // 2
    c.line(cx - 40, y + 8, cx - 40, y + h - 10, 3)
    c.line(cx + 40, y + 8, cx + 40, y + h - 10, 3)
    c.line(cx - 48, y + h - 10, cx + 48, y + h - 10, 4)
    c.line(cx - 44, y + h - 4, cx + 44, y + h - 4, 3)
    box_left, box_top = cx - 24, y + 16
    c.frame(box_left, box_top, box_left + 48, box_top + 44)
    c.line(box_left + 5, box_top + 55, box_left + 43, box_top + 55, 3)
    c.line(cx - 13, box_top + 22, cx - 3, box_top + 33, 4)
    c.line(cx - 3, box_top + 33, cx + 14, box_top + 12, 4)
    c.line(cx - 38, y + 8, cx - 38, y + 2, 2)
    c.line(cx + 38, y + 8, cx + 38, y + 2, 2)


def draw_factory(c, x, y, w, h):
    left, right = x + 12, x + w - 12
    roof, floor = y + 24, y + h - 8
    c.frame(left, roof, right, floor)
    c.line(left - 6, floor, right + 6, floor, 4)
    c.line(cx := x + w // 2 - 20, roof, cx + 18, roof - 22, 3)
    c.line(cx + 18, roof - 22, cx + 36, roof, 3)
    c.line(x + w - 30, roof, x + w - 30, roof - 34, 3)
    c.line(x + w - 40, roof - 34, x + w - 20, roof - 34, 3)
    for dx in (10, 36, 62):
        c.rect(left + dx, floor - 16, left + dx + 12, floor - 4)
    flame_x = x + w // 2 + 26
    c.line(flame_x - 12, roof - 2, flame_x - 18, roof - 26, 3)
    c.line(flame_x - 18, roof - 26, flame_x - 6, roof - 46, 3)
    c.line(flame_x - 6, roof - 46, flame_x + 2, roof - 24, 3)
    c.line(flame_x + 2, roof - 24, flame_x + 14, roof - 36, 3)
    c.line(flame_x + 14, roof - 36, flame_x + 10, roof - 2, 3)
    c.circle(flame_x + 26, roof - 48, 6, 2)
    c.circle(flame_x + 46, roof - 62, 4, 2)


def draw_arrow(c, x, y, w, h):
    c.line(x + 8, y + h - 8, x + 8, y + 6, 3)
    c.line(x + 8, y + h - 8, x + w - 8, y + h - 8, 3)
    c.line(x + 14, y + h - 20, x + 38, y + h - 40, 4)
    c.line(x + 38, y + h - 40, x + 58, y + h - 28, 4)
    c.line(x + 58, y + h - 28, x + w - 12, y + 8, 5)
    c.line(x + w - 34, y + 8, x + w - 12, y + 8, 4)
    c.line(x + w - 12, y + 8, x + w - 12, y + 30, 4)
    c.line(x + 20, y + h - 14, x + 44, y + h - 14, 2)


STORY_DRAWINGS = [draw_globe, draw_ship, draw_apartment,
                  draw_chip, draw_ballot, draw_factory]

STORY_HEADLINES = [
    "COP31 COLLAPSES",
    "WARSHIP SUNK",
    "STRIKE KILLS 11",
    "HUANG IS BACK",
    "DEMOCRATS WIN\nBIG",
    "FACTORY FIRE",
]

STORY_CAPTIONS = [
    ["NO DEAL AT ANTALYA;", "LONGEST UN SUMMIT;",
     "SPLIT ON FUEL AND CASH."],
    ["UKRAINE NAVAL DRONES SINK", "MERKURY SUNK AT BENGHAZI",
     "ZELENSKYY CONFIRMS IT."],
    ["RUSSIAN STRIKE HITS FLAT", "BLOCK IN DYMER NEAR KYIV;",
     "AT LEAST 11 PEOPLE DEAD."],
    ["NVIDIA BRINGS HUANG BACK;", "SHARES JUMP ABOUT 33 PCT;",
     "S&P 500 UP 4.8 PCT."],
    ["DEMOCRATS WIN 258 OR MORE", "HOUSE SEATS; BIGGEST WIN",
     "SINCE 1992."],
    ["FIRE AT INDONESIA SWEETS", "FACTORY FIRE KILLS 24;",
     "ABOUT 30 MISSING."],
]

PANEL_W, PANEL_H = 492, 218
GUTTER = 12
LEFT = (WIDTH - 2 * PANEL_W - GUTTER) // 2
TOP = 290
ROW_GAP = 12
HEADLINE_PAD = 14
HEADLINE_WIDTH = PANEL_W - 2 * HEADLINE_PAD


def draw_panel(c, index):
    col, row = index % 2, index // 2
    x0 = LEFT + col * (PANEL_W + GUTTER)
    y0 = TOP + row * (PANEL_H + ROW_GAP)
    c.frame(x0, y0, x0 + PANEL_W, y0 + PANEL_H)

    cap_w = PANEL_W - 28
    for line in STORY_CAPTIONS[index]:
        if c.text_width(line, 3) > cap_w:
            raise ValueError(f"caption too wide: {line!r}")

    headline_lines = STORY_HEADLINES[index].split("\n")
    for line in headline_lines:
        if c.text_width(line, 5) > HEADLINE_WIDTH:
            raise ValueError(f"headline too wide: {line!r}")
    c.rect(x0, y0 + 1, x0 + HEADLINE_PAD, y0 + 6 + 35 * len(headline_lines))
    for line_number, line in enumerate(headline_lines):
        c.text(x0 + HEADLINE_PAD, y0 + 6 + 35 * line_number, line, 5)

    art_y = y0 + 50
    art_h = 78
    art = Canvas(130, art_h)
    STORY_DRAWINGS[index](art, 0, 0, 130, art_h)
    art_x = x0 + (PANEL_W - 130) // 2
    for py in range(art_h):
        for px in range(130):
            if art.pixels[py * 130 + px] == BLACK:
                c.put(art_x + px, art_y + py)

    cap_y = y0 + 138
    for line in STORY_CAPTIONS[index]:
        c.text(x0 + 14, cap_y, line, 3)
        cap_y += 26
    return x0, y0


def draw_newspaper(c):
    c.text(WIDTH // 2, 10, "THE WORLD", 18, centered=True)
    c.text(WIDTH // 2, 148, "MONDAY 23 NOVEMBER 2026", 7, centered=True)
    c.text(WIDTH // 2, 208, "ONE DAY - SIX STORIES", 5, centered=True)
    c.line(16, 272, WIDTH - 16, 272, 4)

    for index in range(6):
        draw_panel(c, index)

    footer_y = TOP + 3 * PANEL_H + 2 * ROW_GAP + 4
    c.line(16, footer_y, WIDTH - 16, footer_y, 4)
    c.text(WIDTH // 2, footer_y + 12, "THE WORLD - 23 NOVEMBER 2026",
           4, centered=True)


def main():
    canvas = Canvas(WIDTH, HEIGHT)
    draw_newspaper(canvas)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "entry.png"), "wb") as handle:
        handle.write(png_bytes(canvas))


if __name__ == "__main__":
    main()
