"""Genera el guion técnico (docs/02_guion_tecnico.md) y el storyboard (storyboard/) a partir de
scenes/meta.py y del video renderizado, para que la documentación coincida con el montaje real.

Uso: python3 scripts/make_docs.py [guion|storyboard|todo]
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scenes.meta import timeline, TOTAL  # noqa: E402

VIDEO = os.path.join(ROOT, 'output', 'kentukis_emilia_video_final.mp4')
TR = {'black': 'fundido desde negro', 'fade': 'fundido encadenado', 'paper': 'barrido de página', 'cut': 'corte'}


def mmss(t):
    return '%d:%05.2f' % (int(t // 60), t % 60)


def guion():
    tl = timeline()
    out = ['# Guion técnico — *Emilia* (adaptación visual de *Kentukis*)', '',
           'Duración total: **%s** (%.2f s). %d escenas. Tiempos tomados de `scenes/meta.py`, la misma fuente que usa el '
           'renderizador; las transiciones encadenadas se superponen, por eso una escena puede empezar antes de que '
           'termine la anterior.' % (mmss(TOTAL), TOTAL, len(tl)), '',
           '| # | Escena | Inicio | Fin | Duración | Bloque |', '|---|---|---|---|---|---|']
    blocks = [(0, 30, '1 · Presentación'), (30, 65, '2 · Conexión'), (65, 105, '3 · Vínculo'), (105, 173, '4 · Conflictos'),
              (173, 222, '5 · Consecuencias'), (222, 999, '6 · Desenlace')]
    for i, s in enumerate(tl):
        b = [x[2] for x in blocks if x[0] <= s['start'] < x[1]][0]
        out.append('| %d | %s | %s | %s | %.1f s | %s |' % (i + 1, s['titulo'], mmss(s['start']), mmss(s['end']), s['dur'], b))
    out.append('')
    for i, s in enumerate(tl):
        kind, d = s['trans']
        out += ['## %d. %s (`%s`)' % (i + 1, s['titulo'], s['id']), '',
                '- **Tiempo:** %s – %s (%.1f s)' % (mmss(s['start']), mmss(s['end']), s['dur']),
                '- **Acontecimiento del libro:** %s' % s['libro'],
                '- **Ubicación:** %s' % s['lugar'],
                '- **Personajes:** %s' % s['personajes'],
                '- **Composición:** %s' % s['composicion'],
                '- **Acción principal:** %s' % s['accion'],
                '- **Emoción predominante:** %s' % s['emocion'],
                '- **Cámara:** %s' % s['camara'],
                '- **Movimiento de personajes y objetos:** %s' % s['movimiento'],
                '- **Iluminación y paleta:** %s' % s['luz'],
                '- **Transición de entrada:** %s%s' % (TR.get(kind, kind), (' (%.1f s)' % d) if d else ''),
                '- **Transición de salida:** %s' % s['salida'],
                '- **Sonido:** %s' % s['sonido'],
                '- **Función narrativa:** %s' % s['funcion'],
                '- **Storyboard:** ![%s](../storyboard/%s.jpg)' % (s['titulo'], s['id']), '']
    path = os.path.join(ROOT, 'docs', '02_guion_tecnico.md')
    open(path, 'w').write('\n'.join(out))
    print('->', path)


def storyboard():
    """Tres fotogramas por escena extraídos del video final + una lámina general."""
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(os.path.join(ROOT, 'storyboard'), exist_ok=True)
    tmp = os.path.join(ROOT, 'build', 'sb')
    os.makedirs(tmp, exist_ok=True)
    tl = timeline()
    font = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Lora.ttf'), 22)
    strips = []
    md = ['# Storyboard', '', 'Tres momentos de cada escena, extraídos del video final '
          '(inicio, desarrollo y cierre de la acción).', '']
    for i, s in enumerate(tl):
        frames = []
        for k, f in enumerate((0.22, 0.55, 0.85)):
            t = s['start'] + s['dur'] * f
            p = os.path.join(tmp, '%s_%d.png' % (s['id'], k))
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '%.3f' % t, '-i', VIDEO, '-frames:v', '1',
                            '-vf', 'scale=480:270', p], check=True)
            frames.append(Image.open(p).convert('RGB'))
        strip = Image.new('RGB', (480 * 3 + 40, 270 + 50), (243, 233, 216))
        d = ImageDraw.Draw(strip)
        d.text((14, 12), '%d. %s  (%s – %s)' % (i + 1, s['titulo'], mmss(s['start']), mmss(s['end'])),
               fill=(62, 43, 42), font=font)
        for k, fr in enumerate(frames):
            strip.paste(fr, (10 + k * 490, 45))
        strip.save(os.path.join(ROOT, 'storyboard', s['id'] + '.jpg'), quality=88)
        strips.append(strip)
        md += ['## %d. %s' % (i + 1, s['titulo']), '', s['funcion'], '', '![%s](%s.jpg)' % (s['titulo'], s['id']), '']
    # lámina general (dos columnas)
    w, h = strips[0].size
    cols = 2
    rows = (len(strips) + cols - 1) // cols
    sheet = Image.new('RGB', (w * cols, h * rows), (243, 233, 216))
    for i, st in enumerate(strips):
        sheet.paste(st, ((i % cols) * w, (i // cols) * h))
    sheet = sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS)
    sheet.save(os.path.join(ROOT, 'storyboard', 'storyboard_completo.jpg'), quality=85)
    open(os.path.join(ROOT, 'storyboard', 'README.md'), 'w').write('\n'.join(md))
    print('-> storyboard/')


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    if what in ('guion', 'todo'):
        guion()
    if what in ('storyboard', 'todo'):
        storyboard()
