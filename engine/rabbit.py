"""La conejita kentuki: peluche rosa y negro con forma de sandía.

Según la novela: cuerpo de pelota de rugby con una punta rebanada (se apoya en
la base plana), ruedas ocultas, ojos saltones donde está la cámara, dos orejas
largas unidas por una hebilla con forma de hueso que las mantiene erguidas unos
centímetros antes de caer lánguidas a los lados. Chilla y ronronea. Tiene una
luz de conexión en la base (verde).

Coordenadas locales: origen en el centro de la base apoyada en el piso.
Altura total del cuerpo ~250 unidades.
"""
import math
import skia
from .core import shade, noise1, rnd, lerp, clamp
from .draw import INK, LW, paint, smooth_path, ellipse, blob, shape, line, at, glow

PINK = '#f29ab4'
PINK_D = '#d97695'
BLACK = '#2d2631'
INNER = '#f7c3d3'
BONE = '#f6f0e4'
GOLD = '#d8a640'

BW, BH = 104, 250   # medio ancho y alto del cuerpo


def _body_path():
    pts = [(-BW * 0.8, -4), (-BW * 1.0, -BH * 0.3), (-BW * 0.95, -BH * 0.6), (-BW * 0.66, -BH * 0.88),
           (0, -BH), (BW * 0.66, -BH * 0.88), (BW * 0.95, -BH * 0.6), (BW * 1.0, -BH * 0.3), (BW * 0.8, -4),
           (0, 2)]
    return blob(pts, 0.8, 301)


def _bone(c, x, y, w, color):
    """Hebilla con forma de hueso (horizontal)."""
    r = w * 0.17
    path = skia.Path()
    path.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - w * 0.42, y - r * 0.55, x + w * 0.42, y + r * 0.55), r * 0.4, r * 0.4))
    for sx in (-1, 1):
        for sy in (-1, 1):
            path.addCircle(x + sx * w * 0.42, y + sy * r * 0.55, r * 0.75)
    path.setFillType(skia.PathFillType.kWinding)
    c.drawPath(path, paint(color, 1))
    c.drawPath(path, paint(INK, 0.85, stroke=LW * 0.85))
    # repintar el interior para ocultar contornos internos
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - w * 0.42, y - r * 0.5, x + w * 0.42, y + r * 0.5), r * 0.3, r * 0.3),
                paint(color, 1))
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.drawCircle(x + sx * w * 0.42, y + sy * r * 0.55, r * 0.68, paint(color, 1))


def _clip(c, x, y, w, color):
    """Hebilla dorada de Emilia (para la conejita de Lima)."""
    path = blob([(x - w * 0.5, y - w * 0.1), (x + w * 0.5, y - w * 0.13), (x + w * 0.55, y + w * 0.08),
                 (x - w * 0.52, y + w * 0.12)], 0.4, 333)
    shape(c, path, color, shadow=False, lw=LW * 0.85)
    for k in range(4):
        c.drawCircle(x - w * 0.3 + k * w * 0.2, y, w * 0.045, paint(shade(color, -0.35), 0.9))


def draw(c, x, y, scale=1.0, t=0.0, yaw=0.0, tilt=0.0, eyes=1.0, ears=0.0, chirp=0.0, purr=0.0,
         light=None, wet=0.0, clip='bone', look=(0.0, 0.0), squash=0.0, back=False, shadow=True,
         lens_glint=0.0, dirty=0.0):
    """Dibuja la conejita.

    yaw: -1..1 giro de la cara; tilt: inclinación (grados); eyes: 0 dormida..1 abiertos;
    chirp: 0..1 sacudida de chillido; purr: 0..1 vibración de ronroneo; light: None/0..1 brillo de la luz
    verde; clip: 'bone' (Erfurt) o 'gold' (Lima); back: vista trasera.
    """
    shake_x = 0.0
    shake_r = 0.0
    if chirp > 0:
        shake_x = math.sin(t * 60) * 5 * chirp
        shake_r = math.sin(t * 47) * 4 * chirp
    if purr > 0:
        shake_x += math.sin(t * 110) * 1.4 * purr
    sq = 1.0 + squash
    with at(c, x + shake_x * scale, y, scale, rot=tilt + shake_r, sy=scale / sq):
        if shadow:
            c.drawOval(skia.Rect(-BW * 1.05, -14, BW * 1.05, 16), paint('#2a1820', 0.28, blur=9))
        if light is not None and light > 0:
            glow(c, 0, 4, 70, '#7dff9a', 0.55 * light)
        sway = noise1(t * 0.8, 11) * 4 + ears * 10
        u = clamp(yaw, -1, 1)
        top = -BH
        # orejas: suben juntas, hebilla, y caen a los lados
        ear_base_x = u * BW * 0.25
        tip_y = -BH * 0.42 + abs(sway) * 0.5
        for side in (-1, 1):
            if back:
                pass
            fall = side * (BW * 1.02 + sway * side * 0.3)
            pts = [(ear_base_x + side * 9, top + 14), (ear_base_x + side * 11, top - 46), (ear_base_x + side * 24, top - 80),
                   (ear_base_x + fall * 0.62, top - 74), (ear_base_x + fall * 0.98, top - 22),
                   (ear_base_x + fall * 1.08 + side * 4, tip_y)]
            ear_w = 44
            from .people import taper
            ep = taper(pts, ear_w * 0.62, ear_w * 0.7, ear_w * 1.25)
            shape(c, ep, BLACK, line_a=0.95, shadow_a=0.4)
            if not back:
                ip = taper(pts[2:], ear_w * 0.22, ear_w * 0.34, ear_w * 0.6)
                c.save()
                c.translate(side * 2, 3)
                c.drawPath(ip, paint(INNER, 0.85))
                c.restore()
        # cuerpo
        body = _body_path()
        shape(c, body, PINK, sdir=(-0.6 + u * 0.3, -1), size=BW * 1.6, shadow_a=0.36)
        c.save()
        c.clipPath(body, skia.ClipOp.kIntersect, True)
        # base negra (punta rebanada)
        c.drawOval(skia.Rect(-BW * 1.2, -BH * 0.14, BW * 1.2, BH * 0.18), paint(BLACK, 1))
        c.drawOval(skia.Rect(-BW * 1.2, -BH * 0.14, BW * 1.2, BH * 0.18), paint('#000000', 0.0))
        line(c, [(-BW, -BH * 0.1), (0, -BH * 0.135), (BW, -BH * 0.1)], shade(PINK, 0.4), 3, 0.35)
        # semillas de sandía
        for i in range(13):
            ang = rnd(311, i) * math.pi * 2
            rr = 0.25 + rnd(312, i) * 0.6
            sx_ = math.cos(ang) * BW * 0.85 * rr - u * BW * 0.35 * (1 - rr * 0.5)
            sy_ = -BH * 0.5 + math.sin(ang) * BH * 0.32 * rr
            if not back and abs(sx_ + u * BW * 0.3) < BW * 0.55 and sy_ < -BH * 0.42:
                continue   # despejar la cara
            seed = blob([(sx_, sy_ - 9), (sx_ + 5, sy_ + 4), (sx_, sy_ + 8), (sx_ - 5, sy_ + 4)], 0.3, 320 + i)
            c.drawPath(seed, paint(BLACK, 0.92))
            c.drawCircle(sx_ - 1.5, sy_ - 3, 1.6, paint('#ffffff', 0.5))
        if dirty > 0:
            for i in range(6):
                c.drawCircle((rnd(341, i) - 0.5) * BW * 1.4, -BH * (0.2 + rnd(342, i) * 0.6), 14 + rnd(343, i) * 10,
                             paint('#7a6a5a', 0.12 * dirty, blur=8))
        c.restore()
        c.drawPath(body, paint(INK, 0.92, stroke=LW))
        # hebilla entre las orejas
        if clip == 'gold':
            _clip(c, ear_base_x, top - 30, 60, GOLD)
        elif clip == 'bone':
            _bone(c, ear_base_x, top - 32, 62, BONE)
        if back:
            # luz de conexión entre las ruedas traseras
            if light is not None:
                lc = '#62e07a' if light > 0.05 else '#4a4a4a'
                c.drawCircle(0, -10, 7, paint(lc, 1))
                c.drawCircle(0, -10, 7, paint(INK, 0.8, stroke=2))
                if light > 0.05:
                    glow(c, 0, -10, 30, '#9dffb0', 0.7 * light)
            return
        # cara
        fx = u * BW * 0.42
        fy = -BH * 0.58
        er = 36
        for side in (-1, 1):
            far = 1 - max(0, -side * u) * 0.35
            ex = fx + side * BW * 0.36 * (1 - 0.25 * abs(u))
            ey = fy
            rx_, ry_ = er * far, er * 1.04
            # ojo saltón: base y lente
            c.drawOval(skia.Rect(ex - rx_ - 3, ey - ry_ + 4, ex + rx_ + 3, ey + ry_ + 8), paint('#3a1f2a', 0.35, blur=5))
            ep = ellipse(ex, ey, rx_, ry_, 0.4, 350 + side, 18)
            c.drawPath(ep, paint('#191418', 1))
            if eyes > 0.08:
                c.save()
                c.clipPath(ep, skia.ClipOp.kIntersect, True)
                lx, ly = look
                c.drawCircle(ex + lx * 6, ey + ly * 6, er * 0.62 * far, paint('#2d3a4a', 1))
                c.drawCircle(ex + lx * 6, ey + ly * 6, er * 0.62 * far, paint('#5a7690', 0.9, stroke=3))
                c.drawCircle(ex + lx * 6, ey + ly * 6, er * 0.3 * far, paint('#0d0b0e', 1))
                c.drawCircle(ex + lx * 6 + er * 0.28, ey + ly * 6 - er * 0.32, er * 0.2, paint('#ffffff', 0.92))
                c.drawCircle(ex + lx * 6 - er * 0.25, ey + ly * 6 + er * 0.3, er * 0.08, paint('#ffffff', 0.6))
                if lens_glint > 0:
                    glow(c, ex + lx * 6, ey + ly * 6, er * 0.9, '#bfe6ff', 0.6 * lens_glint)
                # párpado
                if eyes < 1.0:
                    lid = (1 - eyes)
                    c.drawRect(skia.Rect(ex - rx_ - 4, ey - ry_ - 4, ex + rx_ + 4, ey - ry_ + 2 * ry_ * lid),
                               paint(PINK, 1))
                    c.drawLine(ex - rx_, ey - ry_ + 2 * ry_ * lid, ex + rx_, ey - ry_ + 2 * ry_ * lid,
                               paint(INK, 0.9, stroke=LW))
                c.restore()
            else:
                c.drawPath(ep, paint(PINK, 1))
                line(c, [(ex - rx_ * 0.75, ey + 2), (ex, ey + 9), (ex + rx_ * 0.75, ey + 2)], INK, LW * 1.1)
            c.drawPath(ep, paint(INK, 0.95, stroke=LW * 1.05))
        # nariz y boca
        nx, ny = fx * 1.05, fy + er * 1.15
        nose = blob([(nx - 11, ny - 5), (nx + 11, ny - 5), (nx, ny + 8)], 0.2, 360)
        c.drawPath(nose, paint(BLACK, 1))
        line(c, [(nx - 12, ny + 18), (nx - 5, ny + 21), (nx, ny + 12), (nx + 5, ny + 21), (nx + 12, ny + 18)],
             INK, LW * 0.85, 0.85)
        if chirp > 0.2:
            c.drawOval(skia.Rect(nx - 7, ny + 14, nx + 7, ny + 28), paint('#5a2a2e', 1))
        # mejillas
        for side in (-1, 1):
            c.drawOval(skia.Rect(fx + side * BW * 0.6 - 18, fy + er * 0.8, fx + side * BW * 0.6 + 18, fy + er * 1.25),
                       paint('#ff7aa0', 0.35, blur=6))
        if wet > 0:
            for i in range(12):
                wx = (rnd(371, i) - 0.5) * BW * 1.7
                wy = -BH * (0.15 + rnd(372, i) * 0.8)
                L = 10 + rnd(373, i) * 16
                line(c, [(wx, wy), (wx + 1, wy + L)], '#dff3ff', 4, 0.75 * wet)
                c.drawCircle(wx + 1, wy + L + 3, 4.5, paint('#dff3ff', 0.85 * wet))
        if light is not None and light > 0.05:
            c.drawOval(skia.Rect(-10, -5, 10, 3), paint('#7dff9a', min(1.0, light)))


def box_art(c, x, y, scale=1.0, t=0.0, view='front'):
    """Ilustración de la conejita para los costados de la caja."""
    if view == 'front':
        draw(c, x, y, scale, t, shadow=False)
    elif view == 'side':
        draw(c, x, y, scale, t, yaw=0.95, shadow=False)
    else:
        draw(c, x, y, scale, t, back=True, shadow=False)


def generic(c, x, y, scale=1.0, t=0.0, yaw=0.0, color='#d8c8a8'):
    """Kentuki del hijo: el libro no dice qué animal es, así que se dibuja sin rasgos de especie."""
    with at(c, x, y, scale):
        c.drawOval(skia.Rect(-BW * 1.0, -12, BW * 1.0, 14), paint('#2a1820', 0.25, blur=8))
        shape(c, _body_path(), color, size=BW * 1.6)
        fx = yaw * BW * 0.4
        for side in (-1, 1):
            ex = fx + side * BW * 0.34
            c.drawCircle(ex, -BH * 0.58, 30, paint('#191418', 1))
            c.drawCircle(ex + 9, -BH * 0.58 - 10, 8, paint('#ffffff', 0.9))
            c.drawCircle(ex, -BH * 0.58, 30, paint(INK, 0.9, stroke=LW))
