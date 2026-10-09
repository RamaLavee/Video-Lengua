"""Efectos globales: textura de papel, viñeta, tipografía y rótulos."""
import os
import math
import numpy as np
import skia
from PIL import Image
from .core import W, H, col, prog, ease_out, smooth, clamp
from .draw import paint, lin_grad, rad_grad, line

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = {
    'Lora': os.path.join(ROOT, 'assets/fonts/Lora.ttf'),
    'Caveat': os.path.join(ROOT, 'assets/fonts/Caveat.ttf'),
}
_tf = {}
_paper = None


def typeface(name):
    if name not in _tf:
        _tf[name] = skia.Typeface.MakeFromFile(FONTS[name])
    return _tf[name]


def font(name, size):
    f = skia.Font(typeface(name), size)
    f.setEdging(skia.Font.Edging.kSubpixelAntiAlias)
    f.setSubpixel(True)
    return f


# ---------------------------------------------------------------- papel
def _value_noise(shape, scale, seed):
    rng = np.random.default_rng(seed)
    gh, gw = shape[0] // scale + 2, shape[1] // scale + 2
    g = rng.random((gh, gw)).astype(np.float32)
    from scipy.ndimage import zoom
    z = zoom(g, scale, order=3)
    return z[:shape[0], :shape[1]]


def make_paper(path):
    from scipy.ndimage import gaussian_filter
    h, w = H, W
    n = np.zeros((h, w), np.float32)
    for sc, a in ((240, 0.45), (90, 0.25), (30, 0.15), (8, 0.1)):
        n += _value_noise((h, w), sc, sc) * a
    n = (n - n.min()) / (n.max() - n.min())
    rng = np.random.default_rng(7)
    grain = gaussian_filter(rng.random((h, w)).astype(np.float32), 0.7)
    grain = (grain - grain.mean()) / (grain.std() + 1e-6)
    fib = np.zeros((h, w), np.float32)
    for _ in range(900):
        x0, y0 = rng.integers(0, w), rng.integers(0, h)
        L = rng.integers(20, 90)
        a = rng.random() * math.pi
        xs = (x0 + np.cos(a) * np.arange(L)).astype(int) % w
        ys = (y0 + np.sin(a) * np.arange(L)).astype(int) % h
        fib[ys, xs] += 1
    fib = gaussian_filter(fib, 0.8)
    grain = gaussian_filter(grain, 1.2)
    v = 1.0 - 0.075 * n - 0.007 * grain - 0.05 * np.clip(fib, 0, 1)
    v = np.clip(v, 0, 1)
    rgb = np.stack([v * 1.0, v * 0.985, v * 0.955], -1)
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(img).save(path)


def paper_image():
    global _paper
    if _paper is None:
        path = os.path.join(ROOT, 'assets/textures/paper.png')
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            make_paper(path)
        arr = np.array(Image.open(path).convert('RGBA'))
        _paper = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
    return _paper


def post(c, t, vignette=0.32, paper=1.0):
    """Textura de papel y viñeta (aplicados sobre cada fotograma)."""
    if paper > 0:
        p = skia.Paint()
        p.setBlendMode(skia.BlendMode.kMultiply)
        p.setAlphaf(paper)
        c.drawImage(paper_image(), 0, 0, skia.SamplingOptions(), p)
    if vignette > 0:
        sh = rad_grad((W / 2, H / 2), W * 0.62, ['#000000', '#000000', '#2b1a22'],
                      [0.0, 0.0, vignette], [0.0, 0.62, 1.0])
        p = skia.Paint()
        p.setShader(sh)
        c.drawRect(skia.Rect(0, 0, W, H), p)


# ---------------------------------------------------------------- rótulos
def place_label(c, t, text, sub=None, t0=0.0, dur=3.6, x=110, y=930, size=64, light=True):
    """Rótulo breve de ubicación: aparece, se sostiene y se desvanece."""
    a = prog(t, t0, t0 + 0.8, smooth) * (1 - prog(t, t0 + dur - 0.8, t0 + dur, smooth))
    if a <= 0.001:
        return
    rise = (1 - prog(t, t0, t0 + 1.0, ease_out)) * 14
    f = font('Lora', size)
    tw = f.measureText(text)
    fg = '#fff8ec' if light else '#3e2b2a'
    bg = '#2a1c22' if light else '#f6ecdc'
    # sombra suave para legibilidad
    c.drawString(text, x + 2, y + 3 + rise, f, paint(bg, 0.55 * a, blur=6))
    c.drawString(text, x, y + rise, f, paint(fg, a))
    # trazo decorativo a mano
    k = prog(t, t0 + 0.3, t0 + 1.3, ease_out)
    line(c, [(x, y + 26 + rise), (x + tw * 0.5 * k, y + 22 + rise), (x + tw * k, y + 27 + rise)],
         fg, 3.0, a * 0.85)
    if sub:
        f2 = font('Lora', size * 0.45)
        c.drawString(sub, x + 2, y + 72 + rise, f2, paint(bg, 0.5 * a, blur=4))
        c.drawString(sub, x, y + 70 + rise, f2, paint(fg, a * 0.9))
