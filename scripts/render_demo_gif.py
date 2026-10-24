"""Render docs/demo.gif from real CLI runs: each question is typed, then its captured output appears.

Needs Pillow and a monospace TTF (this script's only dependencies) and a ledger set up by
scripts/setup_ledger.py:

    python scripts/render_demo_gif.py [--font /path/to/Mono.ttf] [--out docs/demo.gif]
"""
import argparse
from pathlib import Path
import shlex
import subprocess
import sys
import textwrap

from PIL import Image, ImageColor, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[1]
SCENES = [('bitcoin holdings on 2026-10-18', 0, 7000), ('what is the mNAV', 2, 4500)]
COLS, ROWS, WIDTH, PAD, SIZE = 100, 28, 900, 24, 14
BG, INK, YELLOW = '#111214', '#F5F5EF', '#FFE500'
FONTS = ['/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf',
         '/usr/share/fonts/TTF/DejaVuSansMono.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
         '/System/Library/Fonts/Menlo.ttc']


def run(question, expected_exit):
    proc = subprocess.run([sys.executable, '-m', 'ask_filings', question], cwd=PROJECT,
                          capture_output=True, text=True)
    if proc.returncode != expected_exit:
        raise SystemExit(f'{question!r} exited {proc.returncode}, expected {expected_exit}:\n{proc.stderr}')
    return proc.stdout.rstrip('\n').split('\n')


def wrap(lines):
    rows = []
    for line in lines:
        indent = ' ' * (len(line) - len(line.lstrip()) + 2)
        rows += textwrap.wrap(line, COLS, subsequent_indent=indent, break_on_hyphens=False) or ['']
    return rows


def frames():
    """Yield (rows, answer-line row indexes, duration ms) for each screen state."""
    for question, expected_exit, hold in SCENES:
        command = 'python -m ask_filings ' + shlex.quote(question)
        lines = run(question, expected_exit)
        output, first = wrap(lines), len(wrap(lines[:1]))
        if len(output) + 1 > ROWS:
            raise SystemExit(f'{question!r} needs {len(output) + 1} rows; raise ROWS')
        yield ['$ █'], set(), 600
        for end in range(2, len(command) + 1, 2):
            yield ['$ ' + command[:end] + '█'], set(), 45
        yield ['$ ' + command], set(), 500
        yield ['$ ' + command] + output, set(range(1, first + 1)), hold


def palette():
    """One fixed palette for every frame: 16 antialiasing steps from the background to each ink."""
    rgb = [ImageColor.getrgb(c) for c in (BG, INK, YELLOW)]
    ramps = [tuple(round(b + (c - b) * t / 15) for b, c in zip(rgb[0], ink)) for ink in rgb[1:] for t in range(16)]
    image = Image.new('P', (1, 1))
    image.putpalette([v for colour in ramps for v in colour])
    return image


def render(rows, emphasis, font, line_height):
    image = Image.new('RGB', (WIDTH, PAD * 2 + ROWS * line_height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((PAD, PAD), '$', font=font, fill=YELLOW)
    draw.text((PAD + font.getlength('$ '), PAD), rows[0][2:], font=font, fill=INK)
    for i, row in enumerate(rows[1:], 1):
        draw.text((PAD, PAD + i * line_height), row, font=font, fill=YELLOW if i in emphasis else INK)
    return image


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--font', default=next((f for f in FONTS if Path(f).is_file()), None))
    p.add_argument('--out', default=str(PROJECT / 'docs/demo.gif'))
    a = p.parse_args()
    if not a.font:
        raise SystemExit('no monospace font found; pass --font')
    font = ImageFont.truetype(a.font, SIZE)
    if font.getlength('M' * COLS) > WIDTH - 2 * PAD:
        raise SystemExit(f'{COLS} columns of {a.font} at {SIZE}px do not fit {WIDTH}px')
    line_height = round(SIZE * 1.45)
    images, durations, fixed = [], [], palette()
    for rows, emphasis, ms in frames():
        images.append(render(rows, emphasis, font, line_height).quantize(palette=fixed, dither=Image.Dither.NONE))
        durations.append(ms)
    images[0].save(a.out, save_all=True, append_images=images[1:], duration=durations, loop=0, optimize=True)
    print(f'{a.out}: {len(images)} frames, {sum(durations) / 1000:.1f} s, '
          f'{Path(a.out).stat().st_size / 1e6:.2f} MB, font {Path(a.font).name}')


if __name__ == '__main__':
    main()
