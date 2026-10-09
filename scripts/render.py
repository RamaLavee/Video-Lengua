"""Renderizador maestro del cortometraje.

Uso:
  python3 scripts/render.py still <segundos> <salida.png>        # un fotograma del timeline
  python3 scripts/render.py sheet <escena> <n> <salida.png>      # hoja de contacto de una escena
  python3 scripts/render.py video [--force] [--jobs 4]          # render completo por segmentos + audio
  python3 scripts/render.py chunks <i,j,...>                    # re-renderizar segmentos puntuales

El video se arma en build/chunks (segmentos H.264 de 5 s), se concatena y se mezcla con
build/audio.wav (generado por scripts/audio.py) en output/kentukis_emilia_video_final.mp4.
"""
import os
import sys
import glob
import json
import time
import hashlib
import importlib
import subprocess
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402
import skia  # noqa: E402
from PIL import Image  # noqa: E402
from engine.core import W, H, FPS, smooth, col  # noqa: E402
from engine.draw import paint, layer  # noqa: E402
from engine import fx, ui  # noqa: E402
from scenes.meta import timeline, TOTAL  # noqa: E402

BUILD = os.path.join(ROOT, 'build')
CHUNKS = os.path.join(BUILD, 'chunks')
OUTPUT = os.path.join(ROOT, 'output', 'kentukis_emilia_video_final.mp4')
CHUNK_SEC = 5.0
TL = timeline()
_mods = {}


def scene_mod(sid):
    if sid not in _mods:
        name = [f for f in os.listdir(os.path.join(ROOT, 'scenes')) if f.startswith(sid + '_') and f.endswith('.py')]
        if not name:
            _mods[sid] = None
        else:
            _mods[sid] = importlib.import_module('scenes.' + name[0][:-3])
    return _mods[sid]


def draw_scene(c, s, tl):
    m = scene_mod(s['id'])
    if m is None:
        c.clear(col('#f3e9d8'))
        f = fx.font('Lora', 60)
        c.drawString(s['id'] + ' ' + s['titulo'], 200, 540, f, paint('#3e2b2a', 1))
        return
    c.save()
    m.draw(c, tl)
    c.restore()


def render_frame(c, T):
    """Dibuja el fotograma del tiempo global T (segundos)."""
    c.clear(col('#0b0a0e'))
    idx = 0
    for i, s in enumerate(TL):
        if T >= s['start']:
            idx = i
    s = TL[idx]
    kind, d = s['trans']
    tl = T - s['start']
    if idx > 0 and kind in ('fade', 'paper') and tl < d:
        prev = TL[idx - 1]
        ptl = T - prev['start']
        p = tl / d
        if kind == 'fade':
            draw_scene(c, prev, ptl)
            with layer(c, smooth(p)):
                draw_scene(c, s, tl)
        else:
            ui.wipe(c, p, lambda cc: draw_scene(cc, prev, ptl), lambda cc: draw_scene(cc, s, tl))
    else:
        draw_scene(c, s, tl)
    black = 0.0
    if kind == 'black' and d > 0:
        black = max(black, 1 - smooth(tl / d))
    if idx + 1 < len(TL):
        nk, nd = TL[idx + 1]['trans']
        if nk == 'black' and nd > 0:
            black = max(black, smooth((tl - (s['dur'] - nd * 0.7)) / (nd * 0.7)))
    if idx == len(TL) - 1:
        black = max(black, smooth((tl - (s['dur'] - 2.5)) / 2.5))
    if black > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#0b0a0e', black))
    fx.post(c, T, vignette=0.3, paper=1.0)


def frame_array(T, surface=None):
    surface = surface or skia.Surface(W, H)
    c = surface.getCanvas()
    render_frame(c, T)
    return surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)


# ---------------------------------------------------------------- segmentos
def n_frames():
    return int(round(TOTAL * FPS))


def chunk_ranges():
    nf = n_frames()
    per = int(CHUNK_SEC * FPS)
    return [(i, i * per, min(nf, (i + 1) * per)) for i in range((nf + per - 1) // per)]


def _src_hash(files):
    h = hashlib.md5()
    for f in sorted(files):
        h.update(open(f, 'rb').read())
    return h.hexdigest()


def chunk_hash(f0, f1):
    t0, t1 = f0 / FPS, f1 / FPS
    ids = [s['id'] for s in TL if s['end'] > t0 - 0.01 and s['start'] < t1 + 0.01]
    files = glob.glob(os.path.join(ROOT, 'engine', '*.py')) + [os.path.join(ROOT, 'scenes', 'meta.py'),
                                                                os.path.join(ROOT, 'scenes', 'common.py'),
                                                                os.path.abspath(__file__)]
    for sid in ids:
        files += glob.glob(os.path.join(ROOT, 'scenes', sid + '_*.py'))
    files = [f for f in files if os.path.exists(f)]
    return _src_hash(files) + ':%d-%d' % (f0, f1)


def render_chunk(args):
    i, f0, f1, force = args
    os.makedirs(CHUNKS, exist_ok=True)
    out = os.path.join(CHUNKS, 'chunk_%03d.mp4' % i)
    hfile = out + '.hash'
    hv = chunk_hash(f0, f1)
    if not force and os.path.exists(out) and os.path.exists(hfile) and open(hfile).read() == hv:
        return i, 'cache', 0.0
    t_start = time.time()
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '%dx%d' % (W, H),
           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-tune', 'animation',
           '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1', '-g', str(FPS * 2),
           '-x264-params', 'keyint=%d:min-keyint=%d:scenecut=0:open-gop=0' % (FPS * 2, FPS),
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
           '-r', str(FPS), out + '.tmp.mp4']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surface = skia.Surface(W, H)
    for f in range(f0, f1):
        arr = frame_array(f / FPS, surface)
        proc.stdin.write(arr.tobytes())
    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError('ffmpeg falló en el segmento %d' % i)
    os.replace(out + '.tmp.mp4', out)
    open(hfile, 'w').write(hv)
    return i, 'render', time.time() - t_start


def render_video(force=False, jobs=4, only=None):
    rngs = chunk_ranges()
    if only is not None:
        rngs = [r for r in rngs if r[0] in only]
        force = True
    t0 = time.time()
    with Pool(jobs) as pool:
        for i, how, dt in pool.imap_unordered(render_chunk, [(i, a, b, force) for i, a, b in rngs]):
            print('segmento %03d %s %.1fs' % (i, how, dt), flush=True)
    print('render: %.1fs' % (time.time() - t0))
    assemble()


def assemble():
    rngs = chunk_ranges()
    lst = os.path.join(BUILD, 'chunks.txt')
    with open(lst, 'w') as f:
        for i, _, _ in rngs:
            f.write("file '%s'\n" % os.path.join(CHUNKS, 'chunk_%03d.mp4' % i))
    silent = os.path.join(BUILD, 'video_sin_audio.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    '-movflags', '+faststart', silent], check=True)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    audio = os.path.join(BUILD, 'audio.wav')
    if os.path.exists(audio):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-i', audio, '-map', '0:v', '-map', '1:a',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
                        '-movflags', '+faststart', OUTPUT], check=True)
    else:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', silent, '-c', 'copy', '-movflags', '+faststart',
                        OUTPUT], check=True)
    print('->', OUTPUT)


# ---------------------------------------------------------------- utilidades de revisión
def still(T, path):
    arr = frame_array(T)
    Image.fromarray(arr[:, :, :3]).save(path)
    print('->', path)


def sheet(sid, n, path, cols=4, t_from=None, t_to=None):
    s = [x for x in TL if x['id'] == sid][0]
    a = s['start'] + 0.05 if t_from is None else s['start'] + t_from
    b = s['end'] - 0.05 if t_to is None else s['start'] + t_to
    rows = (n + cols - 1) // cols
    tw, th = 480, 270
    im = Image.new('RGB', (tw * cols, th * rows), (20, 20, 20))
    surface = skia.Surface(W, H)
    from PIL import ImageDraw
    for k in range(n):
        T = a + (b - a) * k / max(1, n - 1)
        arr = frame_array(T, surface)
        fr = Image.fromarray(arr[:, :, :3]).resize((tw, th), Image.LANCZOS)
        d = ImageDraw.Draw(fr)
        d.text((6, 4), '%.2f (%.2f)' % (T, T - s['start']), fill=(255, 255, 0))
        im.paste(fr, ((k % cols) * tw, (k // cols) * th))
    im.save(path)
    print('->', path)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'video'
    if cmd == 'still':
        still(float(sys.argv[2]), sys.argv[3])
    elif cmd == 'sheet':
        extra = [float(x) for x in sys.argv[5:7]] if len(sys.argv) > 6 else (None, None)
        sheet(sys.argv[2], int(sys.argv[3]), sys.argv[4], 4, *extra)
    elif cmd == 'video':
        jobs = 4
        if '--jobs' in sys.argv:
            jobs = int(sys.argv[sys.argv.index('--jobs') + 1])
        render_video('--force' in sys.argv, jobs)
    elif cmd == 'chunks':
        render_video(True, 4, only=set(int(x) for x in sys.argv[2].split(',')))
    elif cmd == 'assemble':
        assemble()
