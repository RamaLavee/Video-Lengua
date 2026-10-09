"""Genera hojas de modelo (guía de estilo) de personajes, kentuki y paleta.

Uso: python3 scripts/sheets.py [personajes|kentuki|paleta|todo]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import skia  # noqa: E402
from PIL import Image  # noqa: E402
from engine.core import W, H, col  # noqa: E402
from engine import people as P  # noqa: E402
from engine.draw import paint  # noqa: E402
from engine import fx  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def save(surface, path):
    arr = surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    Image.fromarray(arr[:, :, :3]).save(path)
    print('->', path)


def label(c, txt, x, y, size=26):
    f = fx.font('Lora', size)
    c.drawString(txt, x, y, f, paint('#4a3a33', 0.9))


def characters(name, styles, out, extra=None):
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(col('#efe4d2'))
    x = 170
    for st, view, kw, lab in styles:
        p = P.Person(st)
        p.draw(c, x, 980, kw.pop('scale', 0.82), view=view, t=1.3, **kw)
        label(c, lab, x - 80, 1040, 22)
        x += kw.get('_dx', 260)
    label(c, name, 40, 60, 40)
    fx.post(c, 0)
    save(s, out)


def main(what):
    os.makedirs(os.path.join(ROOT, 'assets/characters'), exist_ok=True)
    if what in ('personajes', 'todo'):
        E = P.EMILIA
        characters('Emilia — Lima, 64 años', [
            (E, 'front', dict(expr='calm'), 'frente'),
            (E, 'front', dict(expr='happy', turn=0.4, hand_L=(120, -560), handshape_L='open'), 'alegría 3/4'),
            (E, 'front', dict(expr='worried', turn=-0.3, look=(-0.5, 0)), 'preocupación'),
            (E, 'side', dict(expr='curious'), 'perfil'),
            (E, 'back', dict(turn=0.4), 'espalda'),
            (P.EMILIA_NIGHT, 'front', dict(expr='shock', hand_L=(30, -620), hand_R=(-30, -620)), 'camisón / shock'),
            (P.EMILIA_ROBE, 'front', dict(expr='angry'), 'bata / enojo'),
        ], os.path.join(ROOT, 'assets/characters/emilia_sheet.png'))
        characters('Eva y Klaus — Erfurt', [
            (P.EVA, 'front', dict(expr='happy'), 'Eva'),
            (P.EVA, 'side', dict(expr='talk'), 'Eva perfil'),
            (P.EVA_WET, 'front', dict(expr='curious', turn=0.3), 'pelo mojado'),
            (P.EVA, 'front', dict(expr='smirk', turn=-0.2), 'sonrisa perversa'),
            (P.KLAUS, 'front', dict(expr='neutral', scale=0.78), 'Klaus'),
            (P.KLAUS, 'side', dict(expr='frown', scale=0.78), 'Klaus perfil'),
            (P.KLAUS, 'back', dict(scale=0.78), 'Klaus espalda'),
        ], os.path.join(ROOT, 'assets/characters/eva_klaus_sheet.png'))
        characters('Gloria, Inés, el hijo y la mujer de las botas', [
            (P.GLORIA, 'front', dict(expr='joy'), 'Gloria'),
            (P.GLORIA, 'side', dict(expr='happy'), 'Gloria perfil'),
            (P.INES, 'front', dict(expr='stern', hand_L=(110, -560), handshape_L='point'), 'Inés'),
            (P.INES, 'side', dict(expr='disgust'), 'Inés perfil'),
            (P.SON, 'front', dict(expr='happy', scale=0.8), 'hijo'),
            (P.BOOTS_WOMAN, 'front', dict(expr='proud'), 'mujer de las botas'),
        ], os.path.join(ROOT, 'assets/characters/secundarios_sheet.png'))


def kentuki():
    from engine import rabbit as R
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(col('#efe4d2'))
    label(c, 'La conejita kentuki (Erfurt) y la de Lima', 40, 60, 40)
    items = [
        (dict(), 'frente'), (dict(yaw=0.7), 'giro 3/4'), (dict(yaw=-0.6, tilt=-8), 'cabeza ladeada'),
        (dict(eyes=0.0), 'dormida'), (dict(back=True, light=1.0), 'espalda: luz verde'),
        (dict(clip='gold', yaw=-0.3), 'conejita de Lima'), (dict(chirp=1.0, t=0.13), 'chillido'),
    ]
    x = 150
    for kw, lab in items:
        R.draw(c, x, 700, 0.9, **kw)
        label(c, lab, x - 80, 780, 22)
        x += 265
    # escala humana
    P.Person(P.EVA).draw(c, 1500, 1040, 0.25, t=1)
    R.draw(c, 1580, 1040, 0.22)
    P.Person(P.EMILIA).draw(c, 1720, 1040, 0.25, t=1, expr='happy')
    R.draw(c, 1800, 1040, 0.22, clip='gold')
    label(c, 'escala', 1640, 1070, 20)
    fx.post(c, 0)
    save(s, os.path.join(ROOT, 'assets/props/kentuki_sheet.png'))


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'todo'
    main(what)
    if what in ('kentuki', 'todo'):
        kentuki()
