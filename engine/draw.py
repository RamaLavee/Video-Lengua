"""Primitivas de dibujo con estética de libro ilustrado.

Todas las formas se construyen con curvas suaves (Catmull-Rom) y un leve
temblor de trazo determinista, para evitar el aspecto de gráfico corporativo.
"""
import math
import skia
from .core import col, col4, to_rgb, shade, noise1, cmix, W, H

INK = '#3e2b2a'          # tinta de contorno (sepia oscuro, nunca negro puro)
INK_SOFT = '#6b5048'
LW = 3.2                 # grosor de contorno de personajes a escala 1


# ---------------------------------------------------------------- pinturas
def paint(color='#000000', a=1.0, stroke=None, blur=0.0, blend=None,
          shader=None, cap=True, aa=True):
    p = skia.Paint(AntiAlias=aa)
    p.setColor4f(col4(color, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur and blur > 0.05:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    if shader is not None:
        p.setShader(shader)
        p.setAlphaf(a)
    return p


def lin_grad(p0, p1, colors, alphas=None, pos=None):
    alphas = alphas or [1.0] * len(colors)
    cs = [col(c, a) for c, a in zip(colors, alphas)]
    return skia.GradientShader.MakeLinear(
        [skia.Point(*p0), skia.Point(*p1)], cs, pos)


def rad_grad(center, r, colors, alphas=None, pos=None):
    alphas = alphas or [1.0] * len(colors)
    cs = [col(c, a) for c, a in zip(colors, alphas)]
    return skia.GradientShader.MakeRadial(skia.Point(*center), max(r, 0.1), cs, pos)


# ---------------------------------------------------------------- trazados
def smooth_path(pts, closed=True, k=1 / 6):
    path = skia.Path()
    n = len(pts)
    if n == 0:
        return path
    path.moveTo(*pts[0])
    if n == 1:
        return path
    if n == 2:
        path.lineTo(*pts[1])
        return path
    last = n if closed else n - 1
    for i in range(last):
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        path.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        path.close()
    return path


def wobble(pts, amp=1.2, seed=0, freq=0.9):
    if amp <= 0:
        return pts
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + noise1(i * freq, seed) * amp,
                    y + noise1(i * freq, seed + 101) * amp))
    return out


def ellipse_pts(cx, cy, rx, ry, n=20, rot=0.0, start=0.0):
    pts = []
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(n):
        a = start + 2 * math.pi * i / n
        x, y = math.cos(a) * rx, math.sin(a) * ry
        pts.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return pts


def ellipse(cx, cy, rx, ry, wob=1.0, seed=0, n=20, rot=0.0):
    return smooth_path(wobble(ellipse_pts(cx, cy, rx, ry, n, rot), wob, seed))


def rrect_pts(x, y, w, h, r, per=3):
    r = max(0.5, min(r, w / 2, h / 2))
    pts = []
    corners = [(x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0),
               (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)]
    for i, (cx, cy, a0) in enumerate(corners):
        for j in range(3):
            a = a0 + (math.pi / 2) * j / 2
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        # puntos intermedios del lado siguiente
        nx, ny, _ = corners[(i + 1) % 4]
        ex = cx + math.cos(a0 + math.pi / 2) * r
        ey = cy + math.sin(a0 + math.pi / 2) * r
        a1 = corners[(i + 1) % 4][2]
        sx = nx + math.cos(a1) * r
        sy = ny + math.sin(a1) * r
        for j in range(1, per):
            f = j / per
            pts.append((ex + (sx - ex) * f, ey + (sy - ey) * f))
    return pts


def rrect(x, y, w, h, r, wob=1.0, seed=0, per=3):
    return smooth_path(wobble(rrect_pts(x, y, w, h, r, per), wob, seed))


def poly(pts, closed=True):
    path = skia.Path()
    path.moveTo(*pts[0])
    for p in pts[1:]:
        path.lineTo(*p)
    if closed:
        path.close()
    return path


def blob(pts, wob=1.0, seed=0, closed=True):
    return smooth_path(wobble(pts, wob, seed), closed)


def shifted(path, dx, dy):
    p = skia.Path(path)
    p.offset(dx, dy)
    return p


# ---------------------------------------------------------------- pintado
def fill(c, path, color, a=1.0, blend=None):
    c.drawPath(path, paint(color, a, blend=blend))


def stroke(c, path, color=INK, lw=LW, a=1.0, blur=0):
    c.drawPath(path, paint(color, a, stroke=lw, blur=blur))


def inner_shade(c, path, color, dx, dy, blur, a=0.45, blend=None):
    """Sombra (o luz) interna en el lado opuesto a (dx,dy)."""
    b = path.getBounds()
    pad = blur * 3 + abs(dx) + abs(dy) + 4
    bounds = skia.Rect(b.left() - pad, b.top() - pad, b.right() + pad, b.bottom() + pad)
    c.save()
    c.clipPath(path, skia.ClipOp.kIntersect, True)
    lp = None
    if blend is not None:
        lp = skia.Paint()
        lp.setBlendMode(blend)
    c.saveLayer(bounds, lp)
    c.drawPath(path, paint(color, a))
    c.drawPath(shifted(path, dx, dy), paint('#000000', 1.0, blur=blur,
                                            blend=skia.BlendMode.kDstOut))
    c.restore()
    c.restore()


def shape(c, path, color, line=INK, lw=LW, a=1.0, shadow=True, light=True,
          sdir=(1, 1), size=None, grad=True, line_a=0.92, shadow_a=0.32):
    """Forma ilustrada: relleno con degradé leve, sombra interna, luz, contorno."""
    b = path.getBounds()
    sz = size or max(4.0, min(b.width(), b.height()))
    if grad:
        sh = lin_grad((b.left(), b.top()), (b.left() + b.width() * 0.25, b.bottom()),
                      [shade(color, 0.07), color, shade(color, -0.06)], pos=[0, 0.55, 1])
        c.drawPath(path, paint(color, a, shader=sh))
    else:
        c.drawPath(path, paint(color, a))
    if shadow:
        k = sz * 0.16
        inner_shade(c, path, shade(color, -0.42), -sdir[0] * k, -sdir[1] * k,
                    sz * 0.09, shadow_a * a, blend=skia.BlendMode.kMultiply)
    if light:
        k = sz * 0.12
        inner_shade(c, path, shade(color, 0.5), sdir[0] * k, sdir[1] * k,
                    sz * 0.08, 0.22 * a)
    if line and lw > 0:
        c.drawPath(path, paint(line, line_a * a, stroke=lw))


def soft_shadow(c, cx, cy, rx, ry, a=0.28, color='#3a2530'):
    c.drawOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry),
               paint(color, a, blur=max(rx, ry) * 0.25))


def glow(c, cx, cy, r, color, a=0.5, blend=skia.BlendMode.kScreen):
    sh = rad_grad((cx, cy), r, [color, color], [a, 0.0])
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    if blend is not None:
        p.setBlendMode(blend)
    c.drawCircle(cx, cy, r, p)


def line(c, pts, color=INK, lw=LW, a=1.0, closed=False, smooth=True, wob=0.0, seed=0):
    pts = wobble(pts, wob, seed) if wob else pts
    path = smooth_path(pts, closed) if smooth else poly(pts, closed)
    c.drawPath(path, paint(color, a, stroke=lw))
    return path


def limb(c, pts, w, color, line_c=INK, lw=LW, a=1.0):
    """Extremidad gruesa redondeada con contorno (brazos, piernas)."""
    path = smooth_path(pts, closed=False)
    c.drawPath(path, paint(line_c, 0.92 * a, stroke=w + lw * 2))
    c.drawPath(path, paint(color, a, stroke=w))
    # leve sombreado a lo largo
    c.drawPath(shifted(path, w * 0.12, w * 0.12),
               paint(shade(color, -0.35), 0.18 * a, stroke=w * 0.45, blur=w * 0.12))
    return path


def circle(c, x, y, r, color, a=1.0, line_c=None, lw=LW):
    c.drawCircle(x, y, r, paint(color, a))
    if line_c:
        c.drawCircle(x, y, r, paint(line_c, a, stroke=lw))


def rect(c, x, y, w, h, color, a=1.0):
    c.drawRect(skia.Rect(x, y, x + w, y + h), paint(color, a))


def vgrad_rect(c, x, y, w, h, top, bottom, a=1.0, mid=None):
    if mid:
        sh = lin_grad((0, y), (0, y + h), [top, mid, bottom])
    else:
        sh = lin_grad((0, y), (0, y + h), [top, bottom])
    c.drawRect(skia.Rect(x, y, x + w, y + h), paint('#000000', a, shader=sh))


# ---------------------------------------------------------------- utilidades de canvas
class at:
    """Contexto de transformación: with at(c, x, y, s, rot): ..."""

    def __init__(self, c, x=0.0, y=0.0, s=1.0, rot=0.0, sy=None, flip=False):
        self.c, self.x, self.y, self.s, self.rot = c, x, y, s, rot
        self.sy = s if sy is None else sy
        self.flip = flip

    def __enter__(self):
        self.c.save()
        self.c.translate(self.x, self.y)
        if self.rot:
            self.c.rotate(self.rot)
        self.c.scale(-self.s if self.flip else self.s, self.sy)
        return self.c

    def __exit__(self, *a):
        self.c.restore()


class layer:
    """Capa con opacidad (y filtro de color opcional)."""

    def __init__(self, c, alpha=1.0, bounds=None, cfilter=None, blend=None):
        self.c, self.alpha, self.bounds = c, alpha, bounds
        self.cfilter, self.blend = cfilter, blend

    def __enter__(self):
        p = skia.Paint()
        p.setAlphaf(max(0.0, min(1.0, self.alpha)))
        if self.cfilter is not None:
            p.setColorFilter(self.cfilter)
        if self.blend is not None:
            p.setBlendMode(self.blend)
        self.c.saveLayer(self.bounds, p)
        return self.c

    def __exit__(self, *a):
        self.c.restore()


class clip:
    def __init__(self, c, path_or_rect):
        self.c, self.p = c, path_or_rect

    def __enter__(self):
        self.c.save()
        if isinstance(self.p, skia.Path):
            self.c.clipPath(self.p, skia.ClipOp.kIntersect, True)
        else:
            self.c.clipRect(skia.Rect(*self.p), skia.ClipOp.kIntersect, True)
        return self.c

    def __exit__(self, *a):
        self.c.restore()


def tint_filter(color, amount):
    """Filtro de color que mezcla la imagen hacia un tono (para gradación)."""
    r, g, b = to_rgb(color)
    k = 1 - amount
    m = [k, 0, 0, 0, r * amount,
         0, k, 0, 0, g * amount,
         0, 0, k, 0, b * amount,
         0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(m)


def grade_filter(sat=1.0, bright=1.0, tint=(1.0, 1.0, 1.0), lift=(0, 0, 0)):
    """Saturación, brillo y balance de color (multiplicativo)."""
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    s = sat
    m = [
        (lr * (1 - s) + s), lg * (1 - s), lb * (1 - s),
        lr * (1 - s), (lg * (1 - s) + s), lb * (1 - s),
        lr * (1 - s), lg * (1 - s), (lb * (1 - s) + s),
    ]
    out = []
    for row in range(3):
        k = bright * tint[row]
        out += [m[row * 3] * k, m[row * 3 + 1] * k, m[row * 3 + 2] * k, 0, lift[row]]
    out += [0, 0, 0, 1, 0]
    return skia.ColorFilters.Matrix(out)
