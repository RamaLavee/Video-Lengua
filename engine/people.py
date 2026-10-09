"""Rig 2D de personajes humanos (vista frontal, perfil y espalda).

Coordenadas locales: origen en el piso entre los pies, y negativo hacia arriba.
Un mismo diseño (diccionario de estilo) se reutiliza en todas las escenas para
garantizar la continuidad visual de cada personaje.
"""
import math
import skia
from .core import shade, noise1, rnd, lerp, clamp
from .draw import (INK, LW, paint, smooth_path, ellipse, blob, shape, line, at, rrect, poly)

# ---------------------------------------------------------------- expresiones
# brow: (subir, inclinación +preocupada/-enojada); mouth: (ancho, curva, apertura, asimetría)
EXPR = {
    'neutral':  dict(brow=(0.0, 0.0), mouth=(1.0, 0.15, 0.0, 0.0), squint=0.0),
    'calm':     dict(brow=(0.05, 0.1), mouth=(0.9, 0.3, 0.0, 0.0), squint=0.1),
    'happy':    dict(brow=(0.25, 0.15), mouth=(1.25, 0.9, 0.25, 0.0), squint=0.35),
    'joy':      dict(brow=(0.45, 0.2), mouth=(1.35, 1.0, 0.7, 0.0), squint=0.6),
    'tender':   dict(brow=(0.25, 0.55), mouth=(1.0, 0.6, 0.0, 0.0), squint=0.45),
    'curious':  dict(brow=(0.55, -0.1), mouth=(0.7, 0.1, 0.12, 0.3), squint=0.0),
    'surprise': dict(brow=(0.9, 0.2), mouth=(0.6, 0.0, 0.75, 0.0), squint=-0.3),
    'shock':    dict(brow=(1.0, 0.45), mouth=(0.75, -0.2, 1.0, 0.0), squint=-0.45),
    'worried':  dict(brow=(0.35, 0.9), mouth=(0.85, -0.35, 0.05, 0.15), squint=0.0),
    'sad':      dict(brow=(0.15, 1.0), mouth=(0.8, -0.6, 0.0, 0.0), squint=0.15),
    'angry':    dict(brow=(-0.3, -1.0), mouth=(0.9, -0.55, 0.12, 0.0), squint=0.25),
    'disgust':  dict(brow=(-0.1, -0.6), mouth=(0.9, -0.4, 0.05, 0.6), squint=0.35),
    'frown':    dict(brow=(-0.15, -0.55), mouth=(0.85, -0.25, 0.0, 0.0), squint=0.15),
    'smirk':    dict(brow=(-0.1, -0.35), mouth=(1.1, 0.55, 0.0, 0.85), squint=0.35),
    'grin':     dict(brow=(0.1, -0.2), mouth=(1.4, 0.85, 0.45, 0.25), squint=0.45),
    'stern':    dict(brow=(-0.2, -0.75), mouth=(0.8, -0.3, 0.0, 0.0), squint=0.2),
    'proud':    dict(brow=(0.3, -0.1), mouth=(1.1, 0.6, 0.0, 0.2), squint=0.3),
    'scared':   dict(brow=(0.8, 1.0), mouth=(0.8, -0.5, 0.45, 0.0), squint=-0.3),
    'talk':     dict(brow=(0.15, 0.05), mouth=(0.95, 0.25, 0.45, 0.0), squint=0.1),
    'cold':     dict(brow=(-0.05, -0.2), mouth=(0.9, 0.0, 0.0, 0.0), squint=0.25),
    'blank':    dict(brow=(0.0, 0.1), mouth=(0.85, -0.05, 0.0, 0.0), squint=0.0),
    'closed':   dict(brow=(0.0, 0.2), mouth=(0.9, 0.1, 0.0, 0.0), squint=1.0),
    'laugh':    dict(brow=(0.35, 0.1), mouth=(1.4, 0.9, 0.9, 0.0), squint=0.8),
}


def expr_params(name, mix_to=None, mix=0.0, over=None):
    e = dict(EXPR.get(name, EXPR['neutral']))
    if mix_to and mix > 0:
        e2 = EXPR.get(mix_to, EXPR['neutral'])
        e = {k: lerp(e[k], e2[k], mix) for k in e}
    if over:
        e.update(over)
    return e


# ---------------------------------------------------------------- estilos
# Anchos (medio ancho) del torso: nw cuello, sw hombros, cw pecho, ww cintura, hw cadera.
EMILIA = dict(
    key='emilia', height=860, head=(92, 100), neck=14, torso=250,
    nw=26, sw=100, cw=110, ww=114, hw=122,
    skin='#c48b65', cheek='#d9786f', eye_c='#2b1d1c',
    hair='#5b5462', hair_hl='#b2adb8', hair_style='emilia', brow_c='#4a4048',
    nose='button', eye_style='dot', glasses='#a07a3a', age=1,
    outfit='cardigan', top='#d6a347', inner='#8f3d5c', bottom='#41706d', skirt=255,
    leg='#a87556', shoe='#6b4636', arm=(42, 31), legw=(54, 36), hand_r=18,
)
EMILIA_NIGHT = dict(EMILIA, outfit='nightgown', top='#b8a8d8', inner='#d7cdea',
                    bottom='#b8a8d8', shoe='#c9a2b5', robe='#8d7bb3')
EMILIA_ROBE = dict(EMILIA_NIGHT, outfit='robe')

EVA = dict(
    key='eva', height=960, head=(80, 92), neck=30, torso=270,
    nw=20, sw=88, cw=84, ww=70, hw=90,
    skin='#f1cdb9', cheek='#ec9a9a', eye_c='#3a2b2a',
    iris='#7fbfe6', hair='#e6c27c', hair_hl='#f6e2ad', hair_style='eva',
    brow_c='#b48a52', nose='small', eye_style='iris', nose_ring=True,
    outfit='top', top='#8cc6e6', inner='#8cc6e6', bottom='#5f5470',
    leg='#5f5470', shoe='#f0c4b1', arm=(33, 23), legw=(62, 31), hand_r=15, barefoot=True,
)
EVA_WET = dict(EVA, hair_style='eva_wet', hair='#c9a463', hair_hl='#dcc08a')
EVA_TOWEL = dict(EVA_WET, outfit='towel', top='#f6efe6', inner='#f6efe6',
                 leg='#f1cdb9', bottom='#f1cdb9', bare_arms=True)

KLAUS = dict(
    key='klaus', height=1060, head=(86, 96), neck=30, torso=330,
    nw=36, sw=140, cw=134, ww=116, hw=114,
    skin='#e5b79c', cheek='#d98a7c', eye_c='#2f2a2a',
    iris='#c9dde3', hair='#7a6248', hair_hl='#9c8264', hair_style='klaus',
    brow_c='#6b553e', nose='big', eye_style='pale', stubble=True,
    outfit='football', top='#c7362f', inner='#f3ece4', bottom='#3e4a66',
    leg='#3e4a66', shoe='#e5b79c', arm=(52, 37), legw=(78, 44), hand_r=22, barefoot=True,
)
KLAUS_BARE = dict(KLAUS, outfit='bare', top='#e5b79c', bare_arms=True)
KLAUS_UNDER = dict(KLAUS, bottom='#2f3a5c', leg='#e5b79c', boxers=True)

GLORIA = dict(
    key='gloria', height=870, head=(94, 98), neck=12, torso=255,
    nw=26, sw=108, cw=124, ww=130, hw=134,
    skin='#d8a37e', cheek='#e07c6c', eye_c='#2b1d1c',
    hair='#9c4a33', hair_hl='#c06a48', hair_style='gloria', brow_c='#6e3a2a',
    nose='button', eye_style='dot', earrings='#e0b64a', age=1,
    outfit='blouse', top='#e8775e', inner='#e8775e', bottom='#d9c7a6',
    leg='#d9c7a6', shoe='#7a4b3a', arm=(44, 33), legw=(66, 42), hand_r=19,
)
INES = dict(
    key='ines', height=900, head=(80, 98), neck=26, torso=260,
    nw=20, sw=88, cw=84, ww=80, hw=92,
    skin='#d6a585', cheek='#cf8a7a', eye_c='#2b1d1c',
    hair='#a9a6ad', hair_hl='#d6d3d8', hair_style='ines', brow_c='#7d7980',
    nose='pointy', eye_style='dot', pearls=True, age=1,
    outfit='cardigan_closed', top='#3d4d6e', inner='#3d4d6e', bottom='#77757d', skirt=270,
    leg='#a9887a', shoe='#3a2e2c', arm=(33, 25), legw=(46, 31), hand_r=16,
)
SON = dict(
    key='son', height=1000, head=(80, 90), neck=28, torso=290,
    nw=26, sw=104, cw=98, ww=88, hw=94,
    skin='#c99572', cheek='#d4826f', eye_c='#2b1d1c',
    hair='#2a2427', hair_hl='#4a4247', hair_style='son', brow_c='#2a2427',
    nose='small_m', eye_style='dot',
    outfit='shirt', top='#f4f1ea', inner='#2f3d5a', bottom='#2f3440',
    leg='#2f3440', shoe='#2a2427', arm=(38, 27), legw=(60, 37), hand_r=17,
)
BOOTS_WOMAN = dict(
    key='boots', height=900, head=(90, 94), neck=16, torso=270,
    nw=30, sw=118, cw=124, ww=120, hw=126,
    skin='#cfa07c', cheek='#c97a68', eye_c='#2b1d1c',
    hair='#2e2626', hair_hl='#4a3e3e', hair_style='boots', brow_c='#2e2626',
    nose='button', eye_style='dot', age=1,
    outfit='work', top='#6d7a52', inner='#6d7a52', bottom='#5a5446',
    leg='#5a5446', shoe='#2b2522', boots=True, arm=(46, 35), legw=(64, 44), hand_r=19,
)


# ---------------------------------------------------------------- geometría
def ik2(sx, sy, tx, ty, l1, l2, bend=1):
    dx, dy = tx - sx, ty - sy
    d = math.hypot(dx, dy)
    d = clamp(d, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    a = math.atan2(dy, dx)
    ca = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    al = math.acos(ca) * bend
    ex, ey = sx + l1 * math.cos(a + al), sy + l1 * math.sin(a + al)
    hx, hy = sx + d * math.cos(a), sy + d * math.sin(a)
    return (ex, ey), (hx, hy)


def arm_from_angles(sx, sy, a1, a2, l1, l2, side):
    """a1: grados desde la vertical (+ hacia afuera); a2: flexión de codo (+ hacia adentro)."""
    r1 = math.radians(a1)
    ex = sx + side * math.sin(r1) * l1
    ey = sy + math.cos(r1) * l1
    r2 = math.radians(a1 - a2)
    hx = ex + side * math.sin(r2) * l2
    hy = ey + math.cos(r2) * l2
    return (ex, ey), (hx, hy)


def _catmull(pts, per=6):
    """Muestrea una curva Catmull-Rom abierta que pasa por pts."""
    if len(pts) < 3:
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        return [(lerp(x0, x1, i / per), lerp(y0, y1, i / per)) for i in range(per + 1)]
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def taper(pts, w0, w1, wmid=None):
    """Contorno cerrado de una extremidad que se afina de w0 a w1 (diámetros)."""
    c = _catmull(pts, 5)
    L = [0.0]
    for (x0, y0), (x1, y1) in zip(c, c[1:]):
        L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
    tot = L[-1] or 1.0
    left, right = [], []
    for i, (x, y) in enumerate(c):
        if i == 0:
            dx, dy = c[1][0] - x, c[1][1] - y
        elif i == len(c) - 1:
            dx, dy = x - c[i - 1][0], y - c[i - 1][1]
        else:
            dx, dy = c[i + 1][0] - c[i - 1][0], c[i + 1][1] - c[i - 1][1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        f = L[i] / tot
        if wmid is not None:
            w = lerp(w0, wmid, f / 0.5) if f < 0.5 else lerp(wmid, w1, (f - 0.5) / 0.5)
        else:
            w = lerp(w0, w1, f)
        w *= 0.5
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    # tapas redondeadas
    (xe, ye) = c[-1]
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    d = math.hypot(dx, dy) or 1.0
    cap_end = (xe + dx / d * w1 * 0.35, ye + dy / d * w1 * 0.35)
    (xs, ys) = c[0]
    dx, dy = c[1][0] - c[0][0], c[1][1] - c[0][1]
    d = math.hypot(dx, dy) or 1.0
    cap_start = (xs - dx / d * w0 * 0.35, ys - dy / d * w0 * 0.35)
    ring = left + [cap_end] + right[::-1] + [cap_start]
    return smooth_path(ring, closed=True)


# ---------------------------------------------------------------- persona
class Person:
    def __init__(self, style):
        self.s = style
        self.hands = {}
        self.hands_world = {}

    def _sz(self):
        s = self.s
        hrx, hry = s['head']
        H = s['height']
        head_cy = -H + hry
        sh_y = head_cy + hry + s['neck']
        hip_y = sh_y + s['torso']
        neck_top = head_cy + hry * 0.7
        return hrx, hry, H, head_cy, neck_top, sh_y, hip_y

    # ------------------------------------------------------------ API
    def draw(self, c, x=0, y=0, scale=1.0, view='front', flip=False, t=0.0, **pose):
        self.hands = {}
        with at(c, x, y, scale, flip=flip):
            if pose.get('shadow', True) and not pose.get('sit') and not pose.get('bust'):
                c.drawOval(skia.Rect(-self.s['hw'] * 1.25, -18, self.s['hw'] * 1.25, 18),
                           paint('#3a2530', 0.22, blur=10))
            if view == 'front':
                self._front(c, t, pose)
            elif view == 'side':
                self._side(c, t, pose)
            else:
                self._back(c, t, pose)
        out = {}
        for k, (hx, hy) in self.hands.items():
            out[k] = (x + (-hx if flip else hx) * scale, y + hy * scale)
        self.hands_world = out
        return out

    # ------------------------------------------------------------ torso
    def _torso_pts(self, sh_y, hem, scale_w=1.0, flare=1.0):
        s = self.s
        T = s['torso']
        nw, sw, cw, ww, hw = (s['nw'], s['sw'] * scale_w, s['cw'] * scale_w, s['ww'] * scale_w, s['hw'] * scale_w)
        half = [(nw + 4, sh_y - 8), (sw * 0.8, sh_y - 1), (sw, sh_y + T * 0.13), (cw, sh_y + T * 0.4),
                (ww, sh_y + T * 0.7), (hw, sh_y + T), (hw * flare, hem)]
        left = [(-x, y) for x, y in half]
        right = [(x, y) for x, y in half[::-1]]
        return left + [(0, hem + 5)] + right + [(0, sh_y - 12)]

    def _front(self, c, t, p):
        s = self.s
        hrx, hry, H, head_cy, neck_top, sh_y, hip_y = self._sz()
        breath = math.sin(t * 2 * math.pi * 0.22 + len(s['key'])) * 0.01
        lean = p.get('lean', 0.0)
        sit = p.get('sit')
        seat_y = -p.get('seat_h', -hip_y * 0.55)
        dy = (seat_y - hip_y) if sit else 0.0
        if not p.get('bust'):
            self._legs_front(c, t, p, hip_y, seat_y)
        for k in ('hand_L', 'hand_R'):
            if p.get(k) is not None and dy:
                p[k] = (p[k][0], p[k][1] - dy)
        c.save()
        c.translate(0, dy)
        with at(c, 0, hip_y, 1.0, rot=lean):
            c.translate(0, -hip_y)
            c.save()
            c.translate(0, hip_y)
            c.scale(1.0, 1.0 + breath)
            c.translate(0, -hip_y)
            arms = self._arm_geo(p, sh_y)
            for k, g in arms.items():
                if not g['front']:
                    self._draw_arm(c, g, k)
            self._hair_back(c, t, p, head_cy, hrx, hry)
            self._body_front(c, t, p, sh_y, hip_y)
            if sit and not p.get('bust'):
                self._lap_front(c, hip_y)
            c.restore()
            hr = p.get('head_rot', 0.0) + noise1(t * 0.35, len(s['key']) * 7) * p.get('idle', 1.5)
            pivot = sh_y - 4
            with at(c, 0, pivot, 1.0, rot=hr):
                c.translate(0, -pivot)
                nk = rrect(-s['nw'] * 0.95, neck_top, s['nw'] * 1.9, sh_y - neck_top + 10, s['nw'] * 0.6, 0.5, 3)
                shape(c, nk, s['skin'], shadow=False, light=False, lw=LW * 0.9)
                c.drawOval(skia.Rect(-s['nw'], neck_top + 4, s['nw'], neck_top + 30),
                           paint(shade(s['skin'], -0.35), 0.35, blur=5))
                self._head_front(c, t, p, p.get('head_dx', 0.0), head_cy + p.get('head_dy', 0.0), hrx, hry)
            c.save()
            c.translate(0, hip_y)
            c.scale(1.0, 1.0 + breath)
            c.translate(0, -hip_y)
            for k, g in arms.items():
                if g['front']:
                    self._draw_arm(c, g, k)
            c.restore()
        c.restore()
        self._lean_hands(lean, hip_y)
        if dy:
            for k, (hx, hy) in list(self.hands.items()):
                self.hands[k] = (hx, hy + dy)

    def _lap_front(self, c, hip_y):
        s = self.s
        w0 = s['legw'][0]
        col_ = s['bottom'] if s['outfit'] in ('cardigan', 'cardigan_closed') else s['leg']
        if s['outfit'] in ('nightgown', 'robe'):
            col_ = s['top']
        if s['outfit'] == 'towel':
            col_ = s['skin']
        for side in (-1, 1):
            kx = side * s['hw'] * 0.48
            shape(c, ellipse(kx, hip_y + 34, w0 * 0.78, w0 * 0.62, 0.5, 18 + side), col_)

    def _lean_hands(self, lean, hip_y):
        if not lean:
            return
        r = math.radians(lean)
        for k, (hx, hy) in list(self.hands.items()):
            dx, dy = hx, hy - hip_y
            self.hands[k] = (dx * math.cos(r) - dy * math.sin(r), hip_y + dx * math.sin(r) + dy * math.cos(r))

    def _legs_front(self, c, t, p, hip_y, seat_y=None):
        s = self.s
        w0, w1 = s['legw']
        hw = s['hw']
        if p.get('sit'):
            for side in (-1, 1):
                kx = side * hw * 0.42
                path = taper([(kx, seat_y + 30), (kx + side * 3, -w1 * 0.4)], w0 * 0.85, w1)
                shape(c, path, s['leg'], shadow=False)
                self._shoe(c, kx + side * 4, 0, side)
            for side in (-1, 1):
                kx = side * hw * 0.45
                col_ = s['bottom'] if s['outfit'] not in ('nightgown', 'robe') else s['top']
                if s['outfit'] in ('top', 'football', 'bare', 'towel', 'shirt', 'work', 'blouse'):
                    col_ = s['leg'] if s['outfit'] != 'towel' else s['skin']
                shape(c, ellipse(kx, seat_y + 10, w0 * 0.75, w0 * 0.55, 0.5, 17 + side), col_)
            return
        walk = p.get('walk')
        for side in (-1, 1):
            lift = 0
            if walk is not None:
                ph = walk * 2 * math.pi + (0 if side < 0 else math.pi)
                lift = max(0, math.sin(ph)) * 20
            hx = side * hw * 0.45
            fx = side * hw * 0.38 + side * p.get('stance', 0)
            path = taper([(hx, hip_y - 20), (lerp(hx, fx, 0.5), hip_y * 0.48 - lift * 0.5), (fx, -w1 * 0.3 - lift)],
                         w0, w1, lerp(w0, w1, 0.55))
            shape(c, path, s['leg'], shadow=False, light=False)
            if s.get('boxers'):
                bx = taper([(hx, hip_y - 30), (lerp(hx, fx, 0.25), hip_y * 0.8)], w0 * 1.25, w0 * 1.15)
                shape(c, bx, s['bottom'])
            self._shoe(c, fx, -lift, side)

    def _shoe(self, c, x, y, side):
        s = self.s
        if s.get('barefoot'):
            path = ellipse(x + side * 5, y - 10, s['legw'][1] * 0.82, 12, 0.5, 11 + side)
            shape(c, path, s['skin'], shadow=False, lw=LW * 0.85)
            for k in range(3):
                c.drawCircle(x + side * 5 + (k - 1) * 7, y - 3, 1.6, paint(INK, 0.5))
            return
        if s.get('boots'):
            path = rrect(x - 26, y - 78, 52, 80, 14, 0.5, 13 + side)
            shape(c, path, s['shoe'], lw=LW * 0.9)
            return
        path = ellipse(x + side * 7, y - 12, s['legw'][1] * 0.95 + 6, 15, 0.5, 14 + side)
        shape(c, path, s['shoe'], lw=LW * 0.9)

    def _arm_geo(self, p, sh_y):
        s = self.s
        L1 = s['height'] * 0.155
        L2 = s['height'] * 0.15
        T = s['torso']
        geo = {}
        for side, key in ((-1, 'R'), (1, 'L')):
            sx = side * (s['sw'] - s['arm'][0] * 0.42)
            sy = sh_y + T * 0.1
            tgt = p.get('hand_' + key)
            if tgt is not None:
                bend = p.get('bend_' + key, -side)
                (ex, ey), (hx, hy) = ik2(sx, sy, tgt[0], tgt[1], L1, L2, bend)
            else:
                a1, a2 = p.get('arm_' + key, (13, 8))
                (ex, ey), (hx, hy) = arm_from_angles(sx, sy, a1, a2, L1, L2, side)
            front = p.get('front_' + key, True)
            geo[key] = dict(s=(sx, sy), e=(ex, ey), h=(hx, hy), front=front, side=side,
                            hand=p.get('handshape_' + key, 'open'), hold=p.get('hold_' + key),
                            dark=p.get('dark_' + key, 0.0))
        return geo

    def _draw_arm(self, c, g, key):
        s = self.s
        (sx, sy), (ex, ey), (hx, hy) = g['s'], g['e'], g['h']
        o = s['outfit']
        w0, w1 = s['arm']
        dk = -g.get('dark', 0.0)
        dx, dy = hx - ex, hy - ey
        d = math.hypot(dx, dy) or 1
        wx, wy = hx - dx / d * s['hand_r'] * 0.55, hy - dy / d * s['hand_r'] * 0.55
        short = o in ('top', 'football') and not s.get('bare_arms')
        bare = s.get('bare_arms') or o == 'bare'
        if bare or short:
            path = taper([(sx, sy), (ex, ey), (wx, wy)], w0 * 0.9, w1 * 0.95)
            shape(c, path, shade(s['skin'], dk), shadow=True, light=False, shadow_a=0.2)
            if short:
                mx, my = lerp(sx, ex, 0.62), lerp(sy, ey, 0.62)
                sl = taper([(sx, sy - 4), (mx, my)], w0 * 1.28, w0 * 1.18)
                shape(c, sl, shade(s['top'], dk))
        else:
            path = taper([(sx, sy), (ex, ey), (wx, wy)], w0, w1 * 1.05)
            shape(c, path, shade(s['top'], dk), shadow=True, light=False, shadow_a=0.25)
            # puño de la manga
            cx_, cy_ = lerp(ex, wx, 0.93), lerp(ey, wy, 0.93)
            ang = math.degrees(math.atan2(dy, dx))
            with at(c, cx_, cy_, 1.0, rot=ang):
                c.drawLine(0, -w1 * 0.5, 0, w1 * 0.5, paint(INK, 0.55, stroke=2.2))
        self._hand(c, hx, hy, math.atan2(dy, dx), g['hand'], g['side'], dk)
        self.hands[key] = (hx, hy)
        if g.get('hold'):
            with at(c, hx, hy, 1.0):
                g['hold'](c)

    def _hand(self, c, x, y, ang, kind, side, dk=0.0):
        s = self.s
        r = s['hand_r']
        sk = shade(s['skin'], dk)
        if kind == 'none':
            return
        with at(c, x, y, 1.0, rot=math.degrees(ang) - 90):
            if kind in ('fist', 'hold'):
                shape(c, ellipse(0, 0, r, r * 1.05, 0.4, 21), sk, shadow=False, lw=LW * 0.85)
                c.drawArc(skia.Rect(-r * 0.6, -r * 0.2, r * 0.6, r * 0.8), 20, 140, False, paint(INK, 0.45, stroke=2))
            elif kind == 'point':
                fp = smooth_path([(0, r * 0.3), (0, r * 1.95)], closed=False)
                c.drawPath(fp, paint(INK, 0.9, stroke=r * 0.55 + LW * 1.6))
                c.drawPath(fp, paint(sk, 1, stroke=r * 0.55))
                shape(c, ellipse(0, 0, r, r * 1.05, 0.4, 21), sk, shadow=False, lw=LW * 0.85)
            else:
                path = blob([(-r, -r * 0.3), (-r * 0.95, r * 0.9), (-r * 0.3, r * 1.45), (r * 0.4, r * 1.4),
                             (r * 0.95, r * 0.9), (r, -r * 0.3), (0, -r * 0.85)], 0.4, 22)
                th = taper([(-side * r * 0.7, -r * 0.05), (-side * r * 1.3, r * 0.5)], r * 0.55, r * 0.45)
                shape(c, th, sk, shadow=False, light=False, lw=LW * 0.85)
                shape(c, path, sk, shadow=False, lw=LW * 0.85)
                for k in (-1, 0, 1):
                    c.drawLine(k * r * 0.32, r * 1.0, k * r * 0.3, r * 1.35, paint(INK, 0.4, stroke=1.8))

    def _skirt(self, c, sh_y, hip_y, length, side_view=False, kx=None):
        s = self.s
        T = s['torso']
        top = sh_y + T * 0.68
        hem = top + length
        ww, hw = s['ww'], s['hw']
        pts = [(-ww * 0.85, top), (-hw * 0.96, hip_y), (-hw * 1.24, hem - 6), (-hw * 0.7, hem + 4), (0, hem + 6),
               (hw * 0.7, hem + 4), (hw * 1.24, hem - 6), (hw * 0.96, hip_y), (ww * 0.85, top)]
        shape(c, blob(pts, 0.7, 31), s['bottom'])
        for k in (-1, 1):
            line(c, [(k * hw * 0.45, hip_y + 20), (k * hw * 0.62, hem - 8)], shade(s['bottom'], -0.3), 2.4, 0.5)
        line(c, [(0, hip_y + 30), (0, hem - 4)], shade(s['bottom'], -0.3), 2.4, 0.4)

    def _body_front(self, c, t, p, sh_y, hip_y):
        s = self.s
        o = s['outfit']
        T = s['torso']
        nw, sw, hw = s['nw'], s['sw'], s['hw']
        if o in ('cardigan', 'cardigan_closed'):
            self._skirt(c, sh_y, hip_y, s.get('skirt', 250))
        if o in ('nightgown', 'robe'):
            hem = sh_y + T + s['height'] * 0.3
            gown = blob(self._torso_pts(sh_y, hem, 1.0, 1.35), 0.7, 32)
            shape(c, gown, s['top'])
            for k in (-1, 1):
                line(c, [(k * hw * 0.5, hip_y), (k * hw * 0.75, hem - 10)], shade(s['top'], -0.25), 2.4, 0.5)
            line(c, [(-nw * 1.6, sh_y - 4), (0, sh_y + 46), (nw * 1.6, sh_y - 4)], shade(s['top'], 0.6), 6, 0.9)
            if o == 'robe':
                robe = blob(self._torso_pts(sh_y, hem - 10, 1.04, 1.32), 0.7, 33)
                shape(c, robe, s['robe'])
                inner = blob([(-nw * 1.4, sh_y - 6), (-16, sh_y + T * 0.7), (-22, hem - 18), (22, hem - 18),
                              (16, sh_y + T * 0.7), (nw * 1.4, sh_y - 6), (0, sh_y - 10)], 0.4, 34)
                shape(c, inner, s['top'], shadow=False, lw=LW * 0.9)
                belt = rrect(-s['ww'] * 1.05, sh_y + T * 0.66, s['ww'] * 2.1, 24, 10, 0.6, 35)
                shape(c, belt, shade(s['robe'], -0.15), lw=LW * 0.85)
                line(c, [(10, sh_y + T * 0.7), (30, sh_y + T * 0.95)], shade(s['robe'], -0.15), 12, 1)
            return
        if o == 'towel':
            sk = blob(self._torso_pts(sh_y, sh_y + T * 0.4), 0.6, 36)
            shape(c, sk, s['skin'], shadow=False)
            tw = blob([(-s['cw'] * 1.06, sh_y + T * 0.3), (-s['hw'] * 1.1, sh_y + T * 1.0),
                       (-s['hw'] * 1.05, sh_y + T * 1.45), (s['hw'] * 1.05, sh_y + T * 1.45),
                       (s['hw'] * 1.1, sh_y + T * 1.0), (s['cw'] * 1.06, sh_y + T * 0.3)], 0.7, 37)
            shape(c, tw, s['top'])
            for k in range(3):
                yy = sh_y + T * (0.55 + k * 0.3)
                line(c, [(-hw * 0.9, yy), (hw * 0.9, yy + 5)], shade(s['top'], -0.15), 3, 0.55)
            line(c, [(-s['cw'] * 1.05, sh_y + T * 0.3), (s['cw'] * 1.05, sh_y + T * 0.3)], shade(s['top'], -0.3), 5, 0.8)
            return
        hem = sh_y + T + (40 if o in ('cardigan', 'blouse', 'cardigan_closed', 'shirt', 'work') else 14)
        torso = blob(self._torso_pts(sh_y, hem, 1.0, 1.03 if o != 'cardigan' else 1.08), 0.7, 38)
        shape(c, torso, s['skin'] if o == 'bare' else s['top'], size=s['sw'] * 1.4)
        if o == 'bare':
            for i in range(16):
                hx = noise1(i * 1.7, 5) * sw * 0.28
                hy = sh_y + 70 + rnd(9, i) * (T * 0.8)
                line(c, [(hx, hy), (hx + 4, hy + 8)], shade(s['skin'], -0.4), 2.2, 0.45)
            for k in (-1, 1):
                line(c, [(k * sw * 0.55, sh_y + T * 0.32), (k * 8, sh_y + T * 0.36)], shade(s['skin'], -0.3), 2.5, 0.5)
            return
        if o == 'cardigan':
            v = blob([(-nw * 1.7, sh_y - 6), (-6, sh_y + T * 0.55), (6, sh_y + T * 0.55), (nw * 1.7, sh_y - 6),
                      (0, sh_y - 10)], 0.4, 39)
            shape(c, v, s['inner'], lw=LW * 0.9)
            for k in (-1, 1):
                line(c, [(k * nw * 1.7, sh_y - 6), (k * 10, sh_y + T * 0.55), (k * 16, hem)], INK, LW * 0.95, 0.85)
            for k in range(3):
                by = sh_y + T * (0.64 + k * 0.13)
                c.drawCircle(-20, by, 6.5, paint(shade(s['top'], -0.38), 1))
                c.drawCircle(-20, by, 6.5, paint(INK, 0.75, stroke=2))
            for k in (-1, 1):
                pk = rrect(k * hw * 0.62 - 28, sh_y + T * 0.78, 56, 42, 10, 0.5, 40 + k)
                c.drawPath(pk, paint(INK, 0.5, stroke=2.4))
            line(c, [(-hw * 1.02, hem - 14), (hw * 1.02, hem - 14)], shade(s['top'], -0.25), 3, 0.5)
        elif o == 'cardigan_closed':
            line(c, [(0, sh_y + 24), (0, hem)], INK, 2.4, 0.7)
            for k in range(5):
                c.drawCircle(0, sh_y + 52 + k * 46, 5, paint('#e8e2d6', 1))
            line(c, [(-nw * 1.6, sh_y - 4), (0, sh_y + 26), (nw * 1.6, sh_y - 4)], INK, LW, 0.8)
        elif o == 'blouse':
            line(c, [(-nw * 1.5, sh_y - 4), (0, sh_y + 52), (nw * 1.5, sh_y - 4)], INK, LW, 0.8)
            nk = blob([(-nw * 1.5, sh_y - 4), (0, sh_y + 52), (nw * 1.5, sh_y - 4), (0, sh_y - 9)], 0.3, 42)
            shape(c, nk, s['skin'], shadow=False, lw=LW * 0.8)
            for i in range(18):
                dx = (rnd(41, i) - 0.5) * s['cw'] * 1.6
                dy = sh_y + 60 + rnd(42, i) * (T - 40)
                c.drawCircle(dx, dy, 5, paint('#fbe9dc', 0.85))
        elif o == 'top':
            nk = blob([(-nw * 2.2, sh_y - 6), (0, sh_y + 58), (nw * 2.2, sh_y - 6), (0, sh_y - 9)], 0.4, 43)
            shape(c, nk, s['skin'], shadow=False, lw=LW * 0.85)
            for k in (-1, 1):
                line(c, [(k * s['ww'] * 0.6, sh_y + T * 0.75), (k * s['ww'] * 0.3, sh_y + T * 0.95)],
                     shade(s['top'], -0.3), 2.2, 0.5)
        elif o == 'football':
            col_ = blob([(-nw * 1.5, sh_y - 6), (0, sh_y + 44), (nw * 1.5, sh_y - 6), (0, sh_y - 12)], 0.4, 44)
            shape(c, col_, s['inner'], lw=LW * 0.9, shadow=False)
            nk = blob([(-nw * 1.15, sh_y - 4), (0, sh_y + 30), (nw * 1.15, sh_y - 4), (0, sh_y - 9)], 0.4, 45)
            shape(c, nk, s['skin'], shadow=False, lw=LW * 0.7)
            for k in (-1, 1):
                line(c, [(k * sw * 0.97, sh_y + T * 0.2), (k * s['ww'] * 1.02, sh_y + T * 0.72),
                         (k * hw * 1.0, hem - 8)], s['inner'], 9, 0.95)
            self._number(c, sw * 0.42, sh_y + T * 0.3, 32, s['inner'])
            cr = blob([(-sw * 0.5, sh_y + T * 0.2), (-sw * 0.3, sh_y + T * 0.2), (-sw * 0.3, sh_y + T * 0.32),
                       (-sw * 0.4, sh_y + T * 0.4), (-sw * 0.5, sh_y + T * 0.32)], 0.2, 46)
            shape(c, cr, s['inner'], shadow=False, light=False, lw=2)
            c.drawLine(-sw * 0.47, sh_y + T * 0.25, -sw * 0.33, sh_y + T * 0.31, paint(s['top'], 1, stroke=4))
        elif o == 'shirt':
            line(c, [(0, sh_y + 10), (0, hem)], shade(s['top'], -0.3), 2.5, 0.8)
            tie = blob([(-10, sh_y + 6), (10, sh_y + 6), (16, sh_y + T * 0.55), (0, sh_y + T * 0.62),
                        (-16, sh_y + T * 0.55)], 0.4, 47)
            shape(c, tie, s['inner'], lw=LW * 0.8, shadow=False)
            for k in (-1, 1):
                cl = blob([(0, sh_y + 4), (k * nw * 1.6, sh_y - 10), (k * nw * 1.2, sh_y + 28)], 0.3, 48 + k)
                shape(c, cl, s['top'], lw=LW * 0.8, shadow=False)
        elif o == 'work':
            line(c, [(-nw * 1.5, sh_y - 4), (0, sh_y + 48), (nw * 1.5, sh_y - 4)], INK, LW, 0.8)
            for k in (-1, 1):
                pk = rrect(k * sw * 0.45 - 26, sh_y + T * 0.25, 52, 44, 6, 0.5, 49 + k)
                c.drawPath(pk, paint(INK, 0.6, stroke=2.4))
        if s.get('pearls'):
            for i in range(11):
                a = math.pi * (0.15 + 0.7 * i / 10)
                px, py = math.cos(a) * nw * 1.9, sh_y + math.sin(a) * 32 - 6
                c.drawCircle(px, py, 6, paint('#f4efe6', 1))
                c.drawCircle(px, py, 6, paint(INK, 0.5, stroke=1.5))

    def _number(self, c, x, y, h, color):
        pts = [(x + h * 0.25, y + h * 0.5), (x + h * 0.25, y - h * 0.5), (x - h * 0.3, y + h * 0.18),
               (x + h * 0.4, y + h * 0.18)]
        c.drawPath(poly(pts, False), paint(color, 0.95, stroke=h * 0.22))

    # ------------------------------------------------------------ cabeza frontal
    def _head_front(self, c, t, p, cx, cy, rx, ry):
        s = self.s
        u = clamp(p.get('turn', 0.0), -1, 1)
        v = p.get('nod', 0.0)
        for side in (-1, 1):
            vis = 1 - max(0, side * u) * 1.2
            if vis > 0.1:
                ex = cx + side * rx * (0.96 - 0.1 * abs(u)) - u * rx * 0.12
                ear = ellipse(ex, cy + ry * 0.12 + v * 6, rx * 0.17 * vis, ry * 0.2, 0.4, 51 + side)
                shape(c, ear, s['skin'], shadow=False, lw=LW * 0.85)
                if s.get('earrings'):
                    c.drawCircle(ex, cy + ry * 0.38, 9, paint(s['earrings'], 1))
                    c.drawCircle(ex, cy + ry * 0.38, 9, paint(INK, 0.7, stroke=2))
        jaw = 1.0 if s.get('age') else 0.9
        hp = blob([(cx, cy - ry), (cx + rx * 0.78, cy - ry * 0.72), (cx + rx, cy - ry * 0.05),
                   (cx + rx * 0.9 * jaw, cy + ry * 0.55), (cx + rx * 0.45, cy + ry * 0.95),
                   (cx, cy + ry * 1.02), (cx - rx * 0.45, cy + ry * 0.95), (cx - rx * 0.9 * jaw, cy + ry * 0.55),
                   (cx - rx, cy - ry * 0.05), (cx - rx * 0.78, cy - ry * 0.72)], 0.7, 52)
        shape(c, hp, s['skin'], sdir=(-0.6 + u * 0.4, -1), size=rx * 1.7)
        if s.get('stubble'):
            c.save()
            c.clipPath(hp, skia.ClipOp.kIntersect, True)
            c.drawOval(skia.Rect(cx - rx * 0.95 - u * rx * 0.2, cy + ry * 0.25, cx + rx * 0.95 - u * rx * 0.2,
                                 cy + ry * 1.4), paint('#6a5446', 0.2, blur=10))
            for i in range(110):
                a = rnd(61, i) * math.pi
                rr_ = 0.55 + rnd(62, i) * 0.45
                dx = math.cos(a) * rx * rr_ * 0.95
                dy = math.sin(a) * ry * rr_ * 0.95
                if dy > ry * 0.25:
                    c.drawCircle(cx + dx - u * rx * 0.15, cy + dy, 1.5, paint('#4a3a32', 0.4))
            c.restore()
        fx = cx - u * rx * 0.3
        fy = cy + v * ry * 0.16
        e = expr_params(p.get('expr', 'neutral'), p.get('expr2'), p.get('emix', 0.0), p.get('face'))
        talk = p.get('talk', 0.0)
        ck = p.get('blush', 0.0) * 0.35 + 0.22
        for side in (-1, 1):
            c.drawOval(skia.Rect(fx + side * rx * 0.55 - rx * 0.2, fy + ry * 0.28 - ry * 0.12,
                                 fx + side * rx * 0.55 + rx * 0.2, fy + ry * 0.28 + ry * 0.12),
                       paint(s['cheek'], ck, blur=rx * 0.09))
        op = p.get('eyes', 1.0) * (1 - max(0, e['squint']) * 0.45) * (1 + max(0, -e['squint']) * 0.25)
        look = p.get('look', (0.0, 0.0))
        eye_dx = rx * 0.36
        for side in (-1, 1):
            far = 1 - max(0, -side * u) * 0.25
            ex = fx + side * eye_dx * (1 - 0.18 * abs(u))
            self._eye(c, ex, fy - ry * 0.02, rx, op, look, e, far, side)
        br, bt = e['brow']
        for side in (-1, 1):
            ex = fx + side * eye_dx * (1 - 0.18 * abs(u))
            by = fy - ry * 0.27 - br * ry * 0.1
            inner_y = by - bt * ry * 0.07
            outer_y = by + bt * ry * 0.04
            pts = [(ex - side * rx * 0.17, inner_y), (ex, by - ry * 0.025), (ex + side * rx * 0.17, outer_y)]
            line(c, pts, s['brow_c'], rx * 0.075 * (1.25 if s['key'] == 'klaus' else 1), 0.95)
        self._nose(c, fx - u * rx * 0.12, fy + ry * 0.24, rx, u)
        if s.get('nose_ring'):
            nx = fx - u * rx * 0.12 + rx * 0.1
            c.drawArc(skia.Rect(nx - 6, fy + ry * 0.3 - 4, nx + 6, fy + ry * 0.3 + 8), 200, 300, False,
                      paint('#c9cdd6', 1, stroke=2.6))
        w, cv, opn, asym = e['mouth']
        opn = max(opn, talk)
        self._mouth(c, fx - u * rx * 0.08, fy + ry * 0.55, rx * 0.32 * w, cv, opn, asym, rx)
        if s.get('age'):
            for side in (-1, 1):
                mx = fx - u * rx * 0.08 + side * rx * 0.45
                line(c, [(mx, fy + ry * 0.38), (mx + side * rx * 0.05, fy + ry * 0.58)],
                     shade(s['skin'], -0.35), 2.2, 0.45)
        self._hair_front(c, t, p, cx, cy, rx, ry, u)
        if s.get('glasses'):
            self._glasses(c, fx, fy - ry * 0.02, rx, ry, u, eye_dx)

    def _eye(self, c, ex, ey, rx, op, look, e, far, side):
        s = self.s
        st = s['eye_style']
        lx, ly = look
        if op < 0.12:
            line(c, [(ex - rx * 0.11, ey + 1), (ex, ey + rx * 0.04), (ex + rx * 0.11, ey + 1)], INK, LW * 0.9, 0.95)
            return
        if e['squint'] > 0.5 and st == 'dot':
            line(c, [(ex - rx * 0.12, ey + rx * 0.04), (ex, ey - rx * 0.06), (ex + rx * 0.12, ey + rx * 0.04)],
                 INK, LW * 1.1, 0.95)
            return
        if st == 'dot':
            erx, ery = rx * 0.085 * far, rx * 0.115 * op
            ox, oy = ex + lx * rx * 0.05, ey + ly * rx * 0.04
            c.drawOval(skia.Rect(ox - erx, oy - ery, ox + erx, oy + ery), paint(s['eye_c'], 1))
            c.drawCircle(ox + erx * 0.35, oy - ery * 0.4, rx * 0.028, paint('#ffffff', 0.9))
            return
        big = 1.35 if st == 'pale' else 1.0
        wrx, wry = rx * 0.15 * far * big, rx * 0.105 * op * big
        wp = ellipse(ex, ey, wrx, wry, 0.3, 71 + side, 16)
        c.drawPath(wp, paint('#fbf7f1', 1))
        c.save()
        c.clipPath(wp, skia.ClipOp.kIntersect, True)
        ir = rx * (0.085 if st == 'pale' else 0.088)
        ix, iy = ex + lx * wrx * 0.45, ey + ly * wry * 0.35
        c.drawCircle(ix, iy, ir, paint(s['iris'], 1))
        c.drawCircle(ix, iy, ir, paint(shade(s['iris'], -0.4), 0.8, stroke=2))
        c.drawCircle(ix, iy, ir * (0.3 if st == 'pale' else 0.5), paint('#1f1a1d', 1))
        c.drawCircle(ix + ir * 0.35, iy - ir * 0.35, ir * 0.25, paint('#ffffff', 0.95))
        c.drawOval(skia.Rect(ex - wrx, ey - wry * 1.2, ex + wrx, ey - wry * 0.55),
                   paint(shade(s['skin'], -0.3), 0.3, blur=3))
        c.restore()
        c.drawPath(wp, paint(INK, 0.95, stroke=LW * 0.9))
        line(c, [(ex - wrx * 1.05, ey - wry * 0.1), (ex, ey - wry * 1.08), (ex + wrx * 1.05, ey - wry * 0.1)],
             INK, LW * 1.25, 0.95)

    def _nose(self, c, x, y, rx, u):
        s = self.s
        n = s['nose']
        sk = s['skin']
        if n == 'button':
            c.drawOval(skia.Rect(x - rx * 0.13, y - rx * 0.09, x + rx * 0.13, y + rx * 0.09),
                       paint(shade(sk, -0.12), 1))
            line(c, [(x - rx * 0.12, y + rx * 0.02), (x, y + rx * 0.1), (x + rx * 0.12, y + rx * 0.02)],
                 INK, LW * 0.8, 0.75)
            c.drawCircle(x - rx * 0.04, y - rx * 0.03, rx * 0.035, paint('#ffffff', 0.35))
        elif n in ('small', 'small_m'):
            line(c, [(x + rx * 0.02, y - rx * 0.16), (x - rx * 0.05 + u * 4, y + rx * 0.04),
                     (x + rx * 0.06, y + rx * 0.07)], INK, LW * 0.8, 0.7)
        elif n == 'big':
            path = blob([(x - rx * 0.05, y - rx * 0.28), (x + rx * 0.09, y - rx * 0.02), (x + rx * 0.18, y + rx * 0.1),
                         (x, y + rx * 0.16), (x - rx * 0.18, y + rx * 0.1)], 0.3, 81)
            shape(c, path, shade(sk, -0.06), shadow=False, light=False, lw=LW * 0.8, line_a=0.7)
        elif n == 'pointy':
            line(c, [(x, y - rx * 0.22), (x + rx * 0.12, y + rx * 0.08), (x - rx * 0.03, y + rx * 0.1)],
                 INK, LW * 0.8, 0.8)

    def _mouth(self, c, x, y, w, cv, opn, asym, rx):
        h = rx * 0.32 * opn
        lift_l = cv * rx * 0.12 + asym * rx * 0.07
        lift_r = cv * rx * 0.12 - asym * rx * 0.03
        if opn < 0.06:
            line(c, [(x - w, y - lift_l), (x, y + cv * rx * 0.06), (x + w, y - lift_r)], INK, LW * 1.0, 0.95)
            return
        top = [(x - w, y - lift_l), (x - w * 0.4, y - h * 0.15 + cv * 2), (x + w * 0.4, y - h * 0.15 + cv * 2),
               (x + w, y - lift_r)]
        bot = [(x + w * 0.55, y + h * 0.75), (x, y + h * (1.0 + max(0, cv) * 0.2)), (x - w * 0.55, y + h * 0.75)]
        path = blob(top + bot, 0.2, 91)
        c.drawPath(path, paint('#5a2a2e', 1))
        c.save()
        c.clipPath(path, skia.ClipOp.kIntersect, True)
        c.drawOval(skia.Rect(x - w * 0.5, y + h * 0.45, x + w * 0.5, y + h * 1.6), paint('#d9737a', 0.9))
        c.restore()
        c.drawPath(path, paint(INK, 0.95, stroke=LW * 0.9))

    def _glasses(self, c, fx, fy, rx, ry, u, eye_dx):
        gc = self.s['glasses']
        r = rx * 0.25
        pos = []
        for side in (-1, 1):
            ex = fx + side * eye_dx * (1 - 0.18 * abs(u))
            pos.append(ex)
            rr = r * (1 - max(0, -side * u) * 0.22)
            c.drawOval(skia.Rect(ex - rr, fy - r * 0.92, ex + rr, fy + r * 0.92), paint('#ffffff', 0.12))
            c.drawOval(skia.Rect(ex - rr, fy - r * 0.92, ex + rr, fy + r * 0.92), paint(gc, 1, stroke=3.4))
            c.drawArc(skia.Rect(ex - rr * 0.7, fy - r * 0.7, ex + rr * 0.7, fy + r * 0.7), 200, 50, False,
                      paint('#ffffff', 0.6, stroke=2.5))
        line(c, [(pos[0] + r * 0.95, fy - 2), ((pos[0] + pos[1]) / 2, fy - 6), (pos[1] - r * 0.95, fy - 2)], gc, 3.2)
        for side, ex in zip((-1, 1), pos):
            if side * u < 0.3:
                line(c, [(ex + side * r, fy - 3), (fx + side * rx * 0.98 + u * rx * 0.25, fy - 1)], gc, 3, 0.9)

    # ------------------------------------------------------------ pelo
    def _hair_back(self, c, t, p, cy, rx, ry):
        s = self.s
        hs = s['hair_style']
        cx = p.get('head_dx', 0.0)
        cy = cy + p.get('head_dy', 0.0)
        hc = s['hair']
        sway = noise1(t * 0.6, 3) * 3
        if hs == 'emilia':
            path = blob([(cx - rx * 1.12, cy - ry * 0.1), (cx - rx * 1.06, cy + ry * 0.66), (cx - rx * 0.6, cy + ry * 0.84),
                         (cx + rx * 0.6, cy + ry * 0.84), (cx + rx * 1.06, cy + ry * 0.66), (cx + rx * 1.12, cy - ry * 0.1),
                         (cx, cy - ry * 1.1)], 1.0, 101)
            shape(c, path, shade(hc, -0.15))
        elif hs in ('eva', 'eva_wet'):
            L = ry * (1.6 if hs == 'eva' else 1.7)
            w = 1.25 if hs == 'eva' else 1.08
            path = blob([(cx - rx * w, cy - ry * 0.2), (cx - rx * (w + 0.05) + sway, cy + L * 0.75),
                         (cx - rx * 0.8 + sway, cy + L), (cx + rx * 0.8 + sway, cy + L),
                         (cx + rx * (w + 0.05) + sway, cy + L * 0.75), (cx + rx * w, cy - ry * 0.2),
                         (cx, cy - ry * 1.12)], 1.0, 102)
            shape(c, path, shade(hc, -0.12))
        elif hs == 'gloria':
            for i in range(14):
                a = math.pi * (0.95 + 1.1 * i / 13)
                bx = cx + math.cos(a) * rx * 1.05
                by = cy + math.sin(a) * ry * 0.95 + ry * 0.15
                shape(c, ellipse(bx, by, rx * 0.34, ry * 0.32, 0.6, 103 + i), shade(hc, -0.12),
                      shadow=False, light=False, lw=LW * 0.8)
        elif hs == 'boots':
            path = blob([(cx - rx * 1.1, cy - ry * 0.2), (cx - rx * 1.1, cy + ry * 1.1), (cx + rx * 1.1, cy + ry * 1.1),
                         (cx + rx * 1.1, cy - ry * 0.2), (cx, cy - ry * 1.1)], 1.0, 104)
            shape(c, path, shade(hc, -0.12))

    def _hair_front(self, c, t, p, cx, cy, rx, ry, u):
        s = self.s
        hs = s['hair_style']
        hc = s['hair']
        hl = s['hair_hl']
        ox = -u * rx * 0.12
        if hs == 'emilia':
            pts = []
            n = 9
            for i in range(n + 1):
                a = math.pi * (1.02 + 0.96 * i / n)
                r_ = 1.08 + 0.07 * math.sin(i * 2.3)
                pts.append((cx + ox * 0.5 + math.cos(a) * rx * r_, cy - ry * 0.08 + math.sin(a) * ry * r_ * 1.02))
            pts += [(cx + rx * 1.08, cy + ry * 0.42), (cx + rx * 0.82, cy + ry * 0.3), (cx + rx * 0.8, cy - ry * 0.18),
                    (cx + rx * 0.3 + ox, cy - ry * 0.46), (cx - rx * 0.25 + ox, cy - ry * 0.38),
                    (cx - rx * 0.62 + ox, cy - ry * 0.5), (cx - rx * 0.86, cy - ry * 0.2), (cx - rx * 0.86, cy + ry * 0.3),
                    (cx - rx * 1.1, cy + ry * 0.45)]
            path = blob(pts, 0.8, 111)
            shape(c, path, hc, sdir=(-0.5, -1), size=rx * 1.4)
            line(c, [(cx - rx * 0.6, cy - ry * 0.8), (cx - rx * 0.1 + ox, cy - ry * 0.62), (cx + rx * 0.5, cy - ry * 0.72)],
                 hl, 5, 0.85)
            line(c, [(cx + rx * 0.85, cy - ry * 0.45), (cx + rx * 0.98, cy + ry * 0.15)], hl, 4, 0.7)
            line(c, [(cx - rx * 0.95, cy - ry * 0.35), (cx - rx * 1.0, cy + ry * 0.2)], hl, 4, 0.6)
            for side in (-1, 1):
                line(c, [(cx + side * rx * 0.2 + ox, cy - ry * 0.95), (cx + side * rx * 0.55 + ox, cy - ry * 0.55)],
                     shade(hc, -0.35), 2.5, 0.6)
        elif hs in ('eva', 'eva_wet'):
            wet = hs == 'eva_wet'
            part = cx + ox + rx * 0.12
            pts_l = [(part, cy - ry * 1.04), (cx - rx * 0.7, cy - ry * 0.85), (cx - rx * 1.04, cy - ry * 0.2),
                     (cx - rx * (1.06 if not wet else 0.98), cy + ry * 0.9), (cx - rx * 0.86, cy + ry * 0.75),
                     (cx - rx * 0.84, cy - ry * 0.05), (cx - rx * 0.45 + ox, cy - ry * 0.55), (part - 4, cy - ry * 0.72)]
            pts_r = [(part, cy - ry * 1.04), (cx + rx * 0.72, cy - ry * 0.85), (cx + rx * 1.04, cy - ry * 0.2),
                     (cx + rx * (1.06 if not wet else 0.98), cy + ry * 0.9), (cx + rx * 0.86, cy + ry * 0.75),
                     (cx + rx * 0.84, cy - ry * 0.05), (cx + rx * 0.5 + ox, cy - ry * 0.5), (part + 4, cy - ry * 0.72)]
            paths = [blob(pts_l, 0.6, 112), blob(pts_r, 0.6, 113)]
            for hp in paths:
                shape(c, hp, hc, sdir=(-0.5, -1), size=rx)
            for k, hp in enumerate(paths):
                c.save()
                c.clipPath(hp, skia.ClipOp.kIntersect, True)
                side = -1 if k == 0 else 1
                for i in range(5 if wet else 3):
                    sx_ = part + side * rx * (0.2 + i * 0.18)
                    line(c, [(sx_, cy - ry * 0.95), (sx_ + side * rx * 0.25, cy - ry * 0.3),
                             (sx_ + side * rx * 0.32, cy + ry * 0.6)],
                         hl if not wet else shade(hc, -0.25), 2.4, 0.6)
                c.restore()
            if wet:
                for i in range(4):
                    side = -1 if i % 2 == 0 else 1
                    c.drawCircle(cx + side * rx * (0.92 + rnd(122, i) * 0.1), cy + ry * (0.3 + rnd(123, i) * 0.5),
                                 3.2, paint('#e6f4ff', 0.85))
        elif hs == 'klaus':
            path = blob([(cx - rx * 0.98, cy - ry * 0.05), (cx - rx * 0.95, cy - ry * 0.7), (cx - rx * 0.4, cy - ry * 1.06),
                         (cx + rx * 0.4, cy - ry * 1.08), (cx + rx * 0.95, cy - ry * 0.7), (cx + rx * 0.98, cy - ry * 0.05),
                         (cx + rx * 0.82, cy - ry * 0.45), (cx + ox, cy - ry * 0.62), (cx - rx * 0.82, cy - ry * 0.45)],
                        0.6, 131)
            shape(c, path, hc, size=rx)
            c.save()
            c.clipPath(path, skia.ClipOp.kIntersect, True)
            for i in range(10):
                hx = cx - rx * 0.7 + i * rx * 0.15
                line(c, [(hx, cy - ry * 0.95), (hx + 6, cy - ry * 0.7)], hl, 2.2, 0.5)
            c.restore()
        elif hs == 'gloria':
            for i in range(11):
                a = math.pi * (1.0 + 1.0 * i / 10)
                bx = cx + ox + math.cos(a) * rx * 0.92
                by = cy - ry * 0.12 + math.sin(a) * ry * 0.95
                shape(c, ellipse(bx, by, rx * 0.3, ry * 0.27, 0.6, 141 + i), hc, shadow=False, lw=LW * 0.8, size=rx * 0.5)
            for i in range(5):
                bx = cx + ox + (i - 2) * rx * 0.33
                shape(c, ellipse(bx, cy - ry * 0.62, rx * 0.26, ry * 0.22, 0.6, 151 + i), hc, shadow=False,
                      lw=LW * 0.8, size=rx * 0.5)
        elif hs == 'ines':
            path = blob([(cx - rx * 1.0, cy + ry * 0.05), (cx - rx * 0.96, cy - ry * 0.65), (cx, cy - ry * 1.07),
                         (cx + rx * 0.96, cy - ry * 0.65), (cx + rx * 1.0, cy + ry * 0.05), (cx + rx * 0.84, cy - ry * 0.45),
                         (cx + ox, cy - ry * 0.72), (cx - rx * 0.84, cy - ry * 0.45)], 0.5, 161)
            shape(c, path, hc, size=rx)
            bun = ellipse(cx + ox * 0.3, cy - ry * 1.18, rx * 0.42, ry * 0.3, 0.6, 162)
            shape(c, bun, hc, size=rx * 0.6)
            c.save()
            c.clipPath(path, skia.ClipOp.kIntersect, True)
            for i in range(5):
                line(c, [(cx - rx * 0.6 + i * rx * 0.3, cy - ry * 0.95), (cx + ox, cy - ry * 0.7)], hl, 2, 0.5)
            c.restore()
        elif hs == 'son':
            path = blob([(cx - rx * 1.0, cy - ry * 0.0), (cx - rx * 0.98, cy - ry * 0.75), (cx - rx * 0.3, cy - ry * 1.12),
                         (cx + rx * 0.6, cy - ry * 1.08), (cx + rx * 1.0, cy - ry * 0.65), (cx + rx * 1.0, cy - ry * 0.05),
                         (cx + rx * 0.85, cy - ry * 0.5), (cx + rx * 0.2 + ox, cy - ry * 0.55), (cx - rx * 0.6 + ox, cy - ry * 0.7),
                         (cx - rx * 0.85, cy - ry * 0.45)], 0.5, 171)
            shape(c, path, hc, size=rx)
            line(c, [(cx - rx * 0.4, cy - ry * 0.95), (cx + rx * 0.5, cy - ry * 0.8)], hl, 3, 0.6)
        elif hs == 'boots':
            path = blob([(cx - rx * 1.05, cy + ry * 0.3), (cx - rx * 1.0, cy - ry * 0.7), (cx, cy - ry * 1.1),
                         (cx + rx * 1.0, cy - ry * 0.7), (cx + rx * 1.05, cy + ry * 0.3), (cx + rx * 0.82, cy - ry * 0.3),
                         (cx + ox, cy - ry * 0.6), (cx - rx * 0.82, cy - ry * 0.3)], 0.6, 181)
            shape(c, path, hc, size=rx)

    # ------------------------------------------------------------ perfil (mira a +x)
    def _side(self, c, t, p):
        s = self.s
        hrx, hry, H, head_cy, neck_top, sh_y, hip_y = self._sz()
        breath = math.sin(t * 2 * math.pi * 0.22) * 0.01
        lean = p.get('lean', 0.0)
        sit = p.get('sit', 0)
        walk = p.get('walk')
        bw = (s['cw'] + s['hw']) * 0.33
        L1 = s['height'] * 0.155
        L2 = s['height'] * 0.15
        legL = -hip_y
        w0, w1 = s['legw']

        seat_y = -p.get('seat_h', -hip_y * 0.55)
        dy = (seat_y - hip_y) if sit else 0.0

        def leg(far):
            lc = shade(s['leg'], -0.2) if far else s['leg']
            if sit:
                kx = p.get('knee_x', bw * 2.4)
                ky = seat_y - 6 + (6 if far else 0)
                fx = kx + p.get('foot_dx', 6) + (14 if far else 0)
                path = taper([(-bw * 0.2, seat_y - 10), (kx, ky), (fx, -w1 * 0.35)], w0, w1, lerp(w0, w1, 0.4))
                shape(c, path, lc, shadow=False, light=False)
                self._shoe_side(c, fx - 6, 0, far)
                return
            if walk is not None:
                ph = (walk + (0.5 if far else 0.0)) * 2 * math.pi
                fx = math.sin(ph) * legL * 0.3
                lift = max(0, math.cos(ph)) * 24
                (kx, ky), (ax, ay) = ik2(0, hip_y, fx, -w1 * 0.3 - lift, legL * 0.5, legL * 0.5, -1)
                path = taper([(0, hip_y - 10), (kx, ky), (ax, ay)], w0, w1, lerp(w0, w1, 0.5))
                foot = (ax, ay + w1 * 0.3)
            else:
                fx = (12 if far else -8) + p.get('stance', 0) * (1 if far else -1)
                path = taper([(0, hip_y - 10), (fx * 0.6, hip_y * 0.5), (fx, -w1 * 0.3)], w0, w1, lerp(w0, w1, 0.5))
                foot = (fx, 0)
            shape(c, path, lc, shadow=False, light=False)
            if s.get('boxers') and not far:
                bx = taper([(0, hip_y - 20), (lerp(0, path.getBounds().centerX(), 0.3), hip_y * 0.82)], w0 * 1.3, w0 * 1.2)
                shape(c, bx, s['bottom'])
            self._shoe_side(c, foot[0], foot[1], far)

        if p.get('chair_back'):
            p['chair_back'](c)
        leg(True)
        if not sit:
            leg(False)
        c.save()
        c.translate(0, dy)
        with at(c, 0, hip_y, 1.0, rot=lean):
            c.translate(0, -hip_y)
            sx, sy = bw * 0.05, sh_y + s['torso'] * 0.12
            tgt = p.get('hand_R')
            if tgt is not None:
                tgt = (tgt[0], tgt[1] - dy)
                (ex, ey), (hx, hy) = ik2(sx, sy, tgt[0], tgt[1], L1, L2, p.get('bend_R', 1))
            else:
                a = math.radians(p.get('swing_R', 6 if walk is None else math.sin(walk * 2 * math.pi) * 22))
                ex, ey = sx + math.sin(a) * L1, sy + math.cos(a) * L1
                b = a + math.radians(p.get('elbow_R', 14))
                hx, hy = ex + math.sin(b) * L2, ey + math.cos(b) * L2
            self._arm_side(c, (sx, sy), (ex, ey), (hx, hy), True, 'R', p)
            self._hair_back_side(c, t, p, head_cy, hrx, hry)
            c.save()
            c.translate(0, hip_y)
            c.scale(1.0, 1.0 + breath)
            c.translate(0, -hip_y)
            self._torso_side(c, p, sh_y, hip_y, bw)
            c.restore()
            if sit:
                c.save()
                c.translate(0, -dy)
                leg(False)
                c.restore()
                if s['outfit'] in ('cardigan', 'cardigan_closed', 'nightgown', 'robe'):
                    self._lap_side(c, p, sh_y, hip_y, bw)
            hr = p.get('head_rot', 0.0) + noise1(t * 0.35, len(s['key']) * 5) * p.get('idle', 1.2)
            pv = sh_y - 2
            with at(c, bw * 0.3, pv, 1.0, rot=hr):
                c.translate(-bw * 0.3, -pv)
                nk = rrect(bw * 0.05, neck_top, s['nw'] * 1.9, sh_y - neck_top + 14, s['nw'] * 0.6, 0.5, 191)
                shape(c, nk, s['skin'], shadow=False, light=False, lw=LW * 0.9)
                self._head_side(c, t, p, bw * 0.3 + p.get('head_dx', 0.0), head_cy + p.get('head_dy', 0.0), hrx, hry)
            sx, sy = bw * 0.3, sh_y + s['torso'] * 0.14
            tgt = p.get('hand_L')
            if tgt is not None:
                tgt = (tgt[0], tgt[1] - dy)
                (ex, ey), (hx, hy) = ik2(sx, sy, tgt[0], tgt[1], L1, L2, p.get('bend_L', 1))
            else:
                a = math.radians(p.get('swing_L', 4 if walk is None else -math.sin(walk * 2 * math.pi) * 22))
                ex, ey = sx + math.sin(a) * L1, sy + math.cos(a) * L1
                b = a + math.radians(p.get('elbow_L', 12))
                hx, hy = ex + math.sin(b) * L2, ey + math.cos(b) * L2
            self._arm_side(c, (sx, sy), (ex, ey), (hx, hy), False, 'L', p)
        c.restore()
        self._lean_hands(lean, hip_y)
        if dy:
            for k, (hx, hy) in list(self.hands.items()):
                self.hands[k] = (hx, hy + dy)

    def _lap_side(self, c, p, sh_y, hip_y, bw):
        s = self.s
        kx = p.get('knee_x', bw * 2.4)
        col_ = s['bottom'] if s['outfit'].startswith('cardigan') else s['top']
        L = 70 if s['outfit'].startswith('cardigan') else 150
        lap = blob([(-bw * 0.9, hip_y - 46), (kx + 10, hip_y - 44), (kx + 38, hip_y - 20), (kx + 30, hip_y + L * 0.6),
                    (kx - 10, hip_y + L), (kx - 40, hip_y + L * 0.5), (-bw * 0.9, hip_y + 20)], 0.7, 228)
        shape(c, lap, col_)
        if s['outfit'] == 'robe':
            shape(c, blob([(-bw * 0.9, hip_y - 46), (kx * 0.6, hip_y - 44), (kx * 0.5, hip_y + 10),
                           (-bw * 0.9, hip_y + 20)], 0.6, 229), s['robe'])

    def _shoe_side(self, c, x, y, far):
        s = self.s
        dk = -0.18 if far else 0.0
        if s.get('barefoot'):
            path = blob([(x - 18, y - 2), (x - 14, y - 22), (x + 10, y - 18), (x + 36, y - 8), (x + 36, y),
                         (x - 12, y + 1)], 0.4, 201)
            shape(c, path, shade(s['skin'], dk), shadow=False, lw=LW * 0.85)
            return
        if s.get('boots'):
            path = blob([(x - 22, y), (x - 20, y - 74), (x + 18, y - 74), (x + 20, y - 26), (x + 44, y - 16),
                         (x + 44, y)], 0.4, 202)
        else:
            path = blob([(x - 20, y), (x - 18, y - 24), (x + 12, y - 24), (x + 42, y - 10), (x + 42, y)], 0.4, 203)
        shape(c, path, shade(s['shoe'], dk), lw=LW * 0.9)

    def _arm_side(self, c, sp, ep, hp, far, key, p):
        s = self.s
        o = s['outfit']
        dk = -0.2 if far else 0.0
        w0, w1 = s['arm']
        hx, hy = hp
        ex, ey = ep
        dx, dy = hx - ex, hy - ey
        d = math.hypot(dx, dy) or 1
        wx, wy = hx - dx / d * s['hand_r'] * 0.55, hy - dy / d * s['hand_r'] * 0.55
        short = o in ('top', 'football') and not s.get('bare_arms')
        bare = s.get('bare_arms') or o == 'bare'
        if bare or short:
            shape(c, taper([sp, ep, (wx, wy)], w0 * 0.9, w1 * 0.95), shade(s['skin'], dk), light=False, shadow_a=0.2)
            if short:
                mx, my = lerp(sp[0], ep[0], 0.62), lerp(sp[1], ep[1], 0.62)
                shape(c, taper([(sp[0], sp[1] - 4), (mx, my)], w0 * 1.28, w0 * 1.18), shade(s['top'], dk))
        else:
            col_ = s['robe'] if o == 'robe' else s['top']
            shape(c, taper([sp, ep, (wx, wy)], w0, w1 * 1.05), shade(col_, dk), light=False, shadow_a=0.25)
        kind = p.get('handshape_' + key, 'fist')
        with at(c, hx, hy, 1.0, rot=math.degrees(math.atan2(dy, dx)) - 90):
            r = s['hand_r']
            sk = shade(s['skin'], dk)
            if kind == 'point':
                fp = smooth_path([(0, r * 0.3), (0, r * 1.9)], closed=False)
                c.drawPath(fp, paint(INK, 0.9, stroke=r * 0.55 + LW * 1.6))
                c.drawPath(fp, paint(sk, 1, stroke=r * 0.55))
            if kind != 'none':
                shape(c, ellipse(0, 0, r, r * 1.08, 0.4, 211), sk, shadow=False, lw=LW * 0.85)
        self.hands[key] = (hx, hy)
        hold = p.get('hold_' + key)
        if hold:
            with at(c, hx, hy, 1.0):
                hold(c)

    def _torso_side(self, c, p, sh_y, hip_y, bw):
        s = self.s
        o = s['outfit']
        T = s['torso']
        sit = p.get('sit')
        belly = (s['ww'] - s['sw'] * 0.8) / 60.0
        if o in ('nightgown', 'robe'):
            if sit:
                hem = hip_y + 30
            else:
                hem = sh_y + T + s['height'] * 0.3
            pts = [(-bw * 0.75, sh_y + 4), (bw * 0.7, sh_y - 2), (bw * (1.0 + belly * 0.3), sh_y + T * 0.45),
                   (bw * 1.0, hip_y), (bw * (1.35 if not sit else 1.0), hem), (-bw * (1.2 if not sit else 1.0), hem),
                   (-bw * 1.05, hip_y - 20), (-bw * 0.95, sh_y + T * 0.3)]
            shape(c, blob(pts, 0.7, 221), s['robe'] if o == 'robe' else s['top'])
            if o == 'robe':
                shape(c, blob([(bw * 0.2, sh_y + 2), (bw * 0.72, sh_y + 2), (bw * 0.6, sh_y + T * 0.55),
                               (bw * 0.3, sh_y + T * 0.5)], 0.3, 222), s['top'], shadow=False, lw=LW * 0.8)
            return
        hem = hip_y + (34 if o in ('cardigan', 'blouse', 'cardigan_closed', 'shirt', 'work') else 10)
        if o in ('cardigan', 'cardigan_closed') and not sit:
            Lk = s.get('skirt', 250)
            top = sh_y + T * 0.68
            sk = blob([(-bw * 1.08, top), (bw * 1.0, top), (bw * 1.25, hip_y), (bw * 1.45, top + Lk),
                       (-bw * 1.35, top + Lk), (-bw * 1.2, hip_y)], 0.7, 224)
            shape(c, sk, s['bottom'])
        pts = [(-bw * 0.72, sh_y + 4), (bw * 0.62, sh_y - 2), (bw * (0.98 + belly * 0.35), sh_y + T * 0.42),
               (bw * (0.95 + belly * 0.2), hip_y - 10), (bw * 0.92, hem), (-bw * 1.05, hem), (-bw * 1.08, hip_y - 30),
               (-bw * 0.95, sh_y + T * 0.32)]
        shape(c, blob(pts, 0.7, 226), s['skin'] if o == 'bare' else s['top'])
        if o == 'cardigan':
            v = blob([(bw * 0.15, sh_y), (bw * 0.66, sh_y), (bw * 0.82, sh_y + T * 0.5)], 0.3, 227)
            shape(c, v, s['inner'], shadow=False, lw=LW * 0.8)
            line(c, [(bw * 0.62, sh_y + 2), (bw * 0.86, sh_y + T * 0.55), (bw * 0.8, hem - 4)], INK, LW * 0.9, 0.7)
        elif o == 'football':
            self._number(c, -bw * 0.62, sh_y + T * 0.35, 30, s['inner'])
            line(c, [(-bw * 1.0, sh_y + T * 0.3), (-bw * 1.04, hem - 6)], s['inner'], 8, 0.9)
        elif o == 'top':
            line(c, [(bw * 0.1, sh_y), (bw * 0.6, sh_y + 34)], shade(s['top'], -0.3), LW * 0.8, 0.8)

    def _hair_back_side(self, c, t, p, cy, rx, ry):
        s = self.s
        hs = s['hair_style']
        cx = p.get('head_dx', 0.0)
        cy += p.get('head_dy', 0.0)
        if hs in ('eva', 'eva_wet'):
            L = ry * 1.6
            path = blob([(cx - rx * 0.1, cy - ry * 1.0), (cx - rx * 1.0, cy - ry * 0.4), (cx - rx * 1.05, cy + L * 0.8),
                         (cx - rx * 0.2, cy + L), (cx + rx * 0.35, cy + ry * 0.4)], 0.8, 231)
            shape(c, path, shade(s['hair'], -0.12))

    def _head_side(self, c, t, p, cx, cy, rx, ry):
        s = self.s
        e = expr_params(p.get('expr', 'neutral'), p.get('expr2'), p.get('emix', 0.0), p.get('face'))
        nod = p.get('nod', 0.0)
        hp = blob([(cx - rx * 0.1, cy - ry), (cx + rx * 0.62, cy - ry * 0.8), (cx + rx * 0.92, cy - ry * 0.25),
                   (cx + rx * 1.0, cy + ry * 0.12), (cx + rx * 1.12, cy + ry * 0.24), (cx + rx * 0.98, cy + ry * 0.4),
                   (cx + rx * 0.9, cy + ry * 0.62), (cx + rx * 0.82, cy + ry * 0.75), (cx + rx * 0.5, cy + ry * 1.0),
                   (cx - rx * 0.2, cy + ry * 0.9), (cx - rx * 0.78, cy + ry * 0.35), (cx - rx * 0.85, cy - ry * 0.35)],
                  0.6, 241)
        shape(c, hp, s['skin'], sdir=(0.7, -1), size=rx * 1.6)
        if s.get('stubble'):
            c.save()
            c.clipPath(hp, skia.ClipOp.kIntersect, True)
            c.drawOval(skia.Rect(cx - rx * 0.2, cy + ry * 0.3, cx + rx * 1.2, cy + ry * 1.3), paint('#6a5446', 0.22, blur=10))
            c.restore()
        shape(c, ellipse(cx - rx * 0.12, cy + ry * 0.12, rx * 0.16, ry * 0.22, 0.4, 242), s['skin'], shadow=False,
              lw=LW * 0.85)
        ck = p.get('blush', 0.0) * 0.35 + 0.22
        c.drawOval(skia.Rect(cx + rx * 0.35, cy + ry * 0.2, cx + rx * 0.8, cy + ry * 0.48),
                   paint(s['cheek'], ck, blur=rx * 0.09))
        ex, ey = cx + rx * 0.62, cy - ry * 0.02 + nod * ry * 0.08
        op = p.get('eyes', 1.0) * (1 - max(0, e['squint']) * 0.45) * (1 + max(0, -e['squint']) * 0.25)
        look = p.get('look', (0.6, 0.0))
        if s['eye_style'] in ('iris', 'pale'):
            big = 1.3 if s['eye_style'] == 'pale' else 1.0
            if op < 0.12:
                line(c, [(ex - rx * 0.08, ey), (ex + rx * 0.08, ey + 2)], INK, LW * 0.9)
            else:
                wp = ellipse(ex + 4, ey, rx * 0.09 * big, rx * 0.1 * op * big, 0.3, 243, 12)
                c.drawPath(wp, paint('#fbf7f1', 1))
                c.save()
                c.clipPath(wp, skia.ClipOp.kIntersect, True)
                c.drawCircle(ex + 4 + rx * 0.04, ey + look[1] * 3, rx * 0.075, paint(s['iris'], 1))
                c.drawCircle(ex + 4 + rx * 0.05, ey + look[1] * 3, rx * 0.03, paint('#1f1a1d', 1))
                c.restore()
                c.drawPath(wp, paint(INK, 0.95, stroke=LW * 0.85))
                line(c, [(ex - rx * 0.07, ey - rx * 0.06 * op), (ex + rx * 0.12, ey - rx * 0.11 * op)], INK, LW * 1.2)
        else:
            if op < 0.12:
                line(c, [(ex - rx * 0.07, ey), (ex + rx * 0.07, ey + 3)], INK, LW * 0.9)
            elif e['squint'] > 0.5:
                line(c, [(ex - rx * 0.08, ey + 4), (ex, ey - 4), (ex + rx * 0.08, ey + 4)], INK, LW * 1.1)
            else:
                c.drawOval(skia.Rect(ex - rx * 0.06 + look[0] * 3, ey - rx * 0.1 * op, ex + rx * 0.06 + look[0] * 3,
                                     ey + rx * 0.1 * op), paint(s['eye_c'], 1))
                c.drawCircle(ex + rx * 0.02 + look[0] * 3, ey - rx * 0.04 * op, rx * 0.025, paint('#ffffff', 0.9))
        br, bt = e['brow']
        by = ey - ry * 0.26 - br * ry * 0.1
        line(c, [(ex - rx * 0.14, by + bt * 2), (ex + rx * 0.12, by - rx * 0.03 - bt * 6)], s['brow_c'], rx * 0.075)
        if s.get('nose_ring'):
            c.drawArc(skia.Rect(cx + rx * 0.95, cy + ry * 0.3, cx + rx * 1.1, cy + ry * 0.45), 0, 300, False,
                      paint('#c9cdd6', 1, stroke=2.6))
        w, cv, opn, asym = e['mouth']
        opn = max(opn, p.get('talk', 0.0))
        mx, my = cx + rx * 0.82, cy + ry * 0.62
        if opn > 0.08:
            mp = ellipse(mx + 2, my + opn * 5, rx * 0.09, rx * 0.06 + opn * rx * 0.12, 0.2, 244, 12)
            c.drawPath(mp, paint('#5a2a2e', 1))
            c.drawPath(mp, paint(INK, 0.9, stroke=LW * 0.85))
        else:
            line(c, [(mx - rx * 0.12, my + 2 - cv * 7), (mx + rx * 0.08, my + 2)], INK, LW * 0.95)
        if s.get('age'):
            line(c, [(mx - rx * 0.16, my - rx * 0.16), (mx - rx * 0.2, my + rx * 0.02)], shade(s['skin'], -0.35), 2.2, 0.45)
        self._hair_side(c, t, p, cx, cy, rx, ry)
        if s.get('glasses'):
            gc = s['glasses']
            r = rx * 0.22
            c.drawOval(skia.Rect(ex - r * 0.55, ey - r * 0.95, ex + r * 0.55, ey + r * 0.95), paint('#ffffff', 0.12))
            c.drawOval(skia.Rect(ex - r * 0.55, ey - r * 0.95, ex + r * 0.55, ey + r * 0.95), paint(gc, 1, stroke=3.4))
            line(c, [(ex - r * 0.55, ey - 3), (cx - rx * 0.05, cy + ry * 0.02)], gc, 3, 0.95)

    def _hair_side(self, c, t, p, cx, cy, rx, ry):
        s = self.s
        hs = s['hair_style']
        hc, hl = s['hair'], s['hair_hl']
        if hs == 'emilia':
            pts = [(cx + rx * 0.72, cy - ry * 0.45), (cx + rx * 0.66, cy - ry * 0.86), (cx + rx * 0.1, cy - ry * 1.14),
                   (cx - rx * 0.7, cy - ry * 0.95), (cx - rx * 1.08, cy - ry * 0.25), (cx - rx * 1.05, cy + ry * 0.45),
                   (cx - rx * 0.62, cy + ry * 0.68), (cx - rx * 0.4, cy + ry * 0.4), (cx - rx * 0.1, cy + ry * 0.38),
                   (cx + rx * 0.05, cy - ry * 0.1), (cx + rx * 0.3, cy - ry * 0.46)]
            shape(c, blob(pts, 0.8, 251), hc, size=rx * 1.4)
            line(c, [(cx + rx * 0.5, cy - ry * 0.8), (cx - rx * 0.2, cy - ry * 0.95), (cx - rx * 0.85, cy - ry * 0.5)],
                 hl, 5, 0.85)
            line(c, [(cx - rx * 0.9, cy - ry * 0.1), (cx - rx * 0.85, cy + ry * 0.4)], hl, 4, 0.6)
        elif hs in ('eva', 'eva_wet'):
            pts = [(cx + rx * 0.8, cy - ry * 0.5), (cx + rx * 0.5, cy - ry * 1.02), (cx - rx * 0.4, cy - ry * 1.1),
                   (cx - rx * 1.0, cy - ry * 0.55), (cx - rx * 1.05, cy + ry * 0.4), (cx - rx * 0.55, cy + ry * 0.3),
                   (cx - rx * 0.15, cy - ry * 0.25), (cx + rx * 0.4, cy - ry * 0.55)]
            hp = blob(pts, 0.6, 252)
            shape(c, hp, hc, size=rx)
            c.save()
            c.clipPath(hp, skia.ClipOp.kIntersect, True)
            for i in range(4):
                line(c, [(cx + rx * (0.4 - i * 0.3), cy - ry * 0.95), (cx - rx * (0.3 + i * 0.2), cy - ry * 0.3)],
                     hl if hs == 'eva' else shade(hc, -0.25), 2.4, 0.55)
            c.restore()
        elif hs == 'klaus':
            pts = [(cx + rx * 0.75, cy - ry * 0.55), (cx + rx * 0.55, cy - ry * 1.02), (cx - rx * 0.3, cy - ry * 1.1),
                   (cx - rx * 0.88, cy - ry * 0.6), (cx - rx * 0.86, cy - ry * 0.05), (cx - rx * 0.35, cy - ry * 0.25),
                   (cx + rx * 0.2, cy - ry * 0.62)]
            shape(c, blob(pts, 0.5, 253), hc, size=rx)
        elif hs == 'gloria':
            for i in range(10):
                a = math.pi * (0.55 + 1.05 * i / 9)
                bx = cx - rx * 0.32 + math.cos(a) * rx * 0.78
                by = cy - ry * 0.2 + math.sin(a) * ry * 0.92
                shape(c, ellipse(bx, by, rx * 0.32, ry * 0.3, 0.6, 254 + i), hc, shadow=False, lw=LW * 0.8, size=rx * 0.5)
        else:
            pts = [(cx + rx * 0.75, cy - ry * 0.55), (cx + rx * 0.5, cy - ry * 1.05), (cx - rx * 0.4, cy - ry * 1.1),
                   (cx - rx * 0.92, cy - ry * 0.5), (cx - rx * 0.9, cy + ry * 0.1), (cx - rx * 0.35, cy - ry * 0.3),
                   (cx + rx * 0.2, cy - ry * 0.6)]
            shape(c, blob(pts, 0.5, 255), hc, size=rx)
            if hs == 'ines':
                shape(c, ellipse(cx - rx * 0.5, cy - ry * 1.05, rx * 0.4, ry * 0.3, 0.6, 256), hc, size=rx * 0.6)

    # ------------------------------------------------------------ espalda
    def _back(self, c, t, p):
        s = self.s
        hrx, hry, H, head_cy, neck_top, sh_y, hip_y = self._sz()
        lean = p.get('lean', 0.0)
        T = s['torso']
        if not p.get('bust') and not p.get('sit'):
            self._legs_front(c, t, p, hip_y)
        with at(c, 0, hip_y, 1.0, rot=lean):
            c.translate(0, -hip_y)
            arms = self._arm_geo(p, sh_y)
            for k, g in arms.items():
                g['hand'] = g['hand'] if p.get('show_hands') else 'none'
                if not g['front']:
                    self._draw_arm(c, g, k)
            o = s['outfit']
            if o in ('nightgown', 'robe'):
                hem = sh_y + T + s['height'] * 0.3
                shape(c, blob(self._torso_pts(sh_y, hem, 1.02, 1.35), 0.7, 261), s['robe'] if o == 'robe' else s['top'])
            else:
                if o in ('cardigan', 'cardigan_closed'):
                    self._skirt(c, sh_y, hip_y, s.get('skirt', 250))
                hem = sh_y + T + (40 if o in ('cardigan', 'cardigan_closed', 'blouse', 'shirt') else 14)
                shape(c, blob(self._torso_pts(sh_y, hem, 1.0, 1.05), 0.7, 263), s['skin'] if o == 'bare' else s['top'],
                      size=s['sw'] * 1.4)
                if o == 'football':
                    self._number(c, 0, sh_y + T * 0.45, 80, s['inner'])
            hr = p.get('head_rot', 0.0)
            with at(c, 0, sh_y - 4, 1.0, rot=hr):
                c.translate(0, -(sh_y - 4))
                cx, cy = 0, head_cy
                nk = rrect(-s['nw'] * 0.95, neck_top, s['nw'] * 1.9, sh_y - neck_top + 10, s['nw'] * 0.6, 0.5, 265)
                shape(c, nk, s['skin'], shadow=False, light=False, lw=LW * 0.9)
                for side in (-1, 1):
                    shape(c, ellipse(side * hrx * 0.96, cy + hry * 0.12, hrx * 0.16, hry * 0.2, 0.4, 264 + side),
                          s['skin'], shadow=False, lw=LW * 0.85)
                shape(c, ellipse(cx, cy, hrx, hry, 0.6, 266, 18), s['skin'])
                hs = s['hair_style']
                hc = s['hair']
                if hs == 'emilia':
                    pts = []
                    for i in range(14):
                        a = math.pi * (0.85 + 1.3 * i / 13)
                        r_ = 1.1 + 0.06 * math.sin(i * 2.1)
                        pts.append((math.cos(a) * hrx * r_, cy - hry * 0.05 + math.sin(a) * hry * r_))
                    pts += [(hrx * 0.95, cy + hry * 0.75), (0, cy + hry * 0.9), (-hrx * 0.95, cy + hry * 0.75)]
                    hp = blob(pts, 0.8, 267)
                    shape(c, hp, hc, size=hrx * 1.4)
                    c.save()
                    c.clipPath(hp, skia.ClipOp.kIntersect, True)
                    for k in range(5):
                        x0 = -hrx * 0.8 + k * hrx * 0.4
                        line(c, [(x0, cy - hry * 0.9), (x0 * 1.1 + 6, cy), (x0 * 1.05, cy + hry * 0.8)],
                             s['hair_hl'], 3.5, 0.5)
                    c.restore()
                elif hs in ('eva', 'eva_wet'):
                    shape(c, blob([(-hrx * 1.1, cy - hry * 0.3), (-hrx * 1.15, cy + hry * 1.6), (hrx * 1.15, cy + hry * 1.6),
                                   (hrx * 1.1, cy - hry * 0.3), (0, cy - hry * 1.12)], 0.8, 268), hc, size=hrx)
                elif hs == 'gloria':
                    for i in range(16):
                        a = math.pi * 2 * i / 16
                        shape(c, ellipse(math.cos(a) * hrx * 0.75, cy + math.sin(a) * hry * 0.8, hrx * 0.38, hry * 0.34,
                                         0.6, 269 + i), hc, shadow=False, lw=LW * 0.8, size=hrx * 0.5)
                else:
                    shape(c, ellipse(cx, cy - hry * 0.1, hrx * 1.04, hry * 0.98, 0.6, 290), hc, size=hrx)
                    if hs == 'ines':
                        shape(c, ellipse(0, cy - hry * 1.15, hrx * 0.42, hry * 0.3, 0.6, 291), hc)
                u = p.get('turn', 0.0)
                if s.get('glasses') and abs(u) > 0.2:
                    side = 1 if u > 0 else -1
                    line(c, [(side * hrx * 0.95, cy + 2), (side * hrx * 1.12, cy - 4)], s['glasses'], 3.2)
            for k, g in arms.items():
                if g['front']:
                    self._draw_arm(c, g, k)
