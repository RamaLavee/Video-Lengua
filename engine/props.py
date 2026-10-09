"""Objetos y mobiliario ilustrados (reutilizables en todas las escenas)."""
import math
import skia
from .core import shade, noise1, rnd, lerp, clamp, cmix
from .draw import (INK, LW, paint, smooth_path, ellipse, blob, shape, line, at, rrect, poly, glow,
                   lin_grad, rad_grad, clip, vgrad_rect)


# ---------------------------------------------------------------- utilidades
def box(c, x, y, w, h, color, depth=0, top=None, side=None, r=6, seed=0, lw=LW, line_a=0.9, shadow=True):
    """Caja con cara frontal y (opcional) tapa en proyección oblicua (estilo libro ilustrado)."""
    if depth:
        d = depth
        tp = poly([(x, y), (x + d * 0.6, y - d * 0.5), (x + w + d * 0.6, y - d * 0.5), (x + w, y)])
        shape(c, tp, top or shade(color, 0.15), shadow=False, lw=lw, line_a=line_a)
        sd = poly([(x + w, y), (x + w + d * 0.6, y - d * 0.5), (x + w + d * 0.6, y + h - d * 0.5), (x + w, y + h)])
        shape(c, sd, side or shade(color, -0.2), shadow=False, lw=lw, line_a=line_a)
    shape(c, rrect(x, y, w, h, r, 0.6, seed), color, lw=lw, line_a=line_a, shadow=shadow, size=min(w, h))


def wood(c, x, y, w, h, color, seed=0, n=5, a=0.25):
    with clip(c, (x, y, x + w, y + h)):
        for i in range(n):
            yy = y + h * (i + 0.5) / n + noise1(i, seed) * 3
            pts = [(x + w * k / 6, yy + noise1(k * 0.7 + i, seed + 3) * 4) for k in range(7)]
            line(c, pts, shade(color, -0.35), 1.8, a)


def weave(c, path, color, step=16, a=0.35):
    """Trama de mimbre dentro de un trazado."""
    b = path.getBounds()
    with clip(c, path):
        y = b.top()
        k = 0
        while y < b.bottom():
            x = b.left() + (step / 2 if k % 2 else 0)
            while x < b.right():
                c.drawOval(skia.Rect(x, y, x + step * 0.9, y + step * 0.55), paint(shade(color, -0.35), a, stroke=1.6))
                x += step
            y += step * 0.55
            k += 1


# ---------------------------------------------------------------- Lima: escritorio de Emilia
MONITOR_C = '#e3d9bf'


def monitor(c, x, y, w, t=0.0, screen_fn=None, on=1.0, glow_a=0.35, power_led=True):
    """Monitor viejo de carcasa amarillenta. (x, y) = esquina superior izquierda de la pantalla 16:9.
    Devuelve el rectángulo de la pantalla."""
    h = w * 9 / 16
    b = w * 0.075
    # pie
    shape(c, rrect(x + w * 0.42, y + h + b * 0.8, w * 0.16, w * 0.1, 8, 0.5, 401), shade(MONITOR_C, -0.1))
    shape(c, ellipse(x + w * 0.5, y + h + b + w * 0.11, w * 0.2, w * 0.035, 0.5, 402), shade(MONITOR_C, -0.05))
    # costado (profundidad)
    side = poly([(x - b, y - b), (x - b - w * 0.07, y - b + w * 0.03), (x - b - w * 0.07, y + h + b - w * 0.03),
                 (x - b, y + h + b)])
    shape(c, side, shade(MONITOR_C, -0.22), shadow=False)
    shape(c, rrect(x - b, y - b, w + 2 * b, h + 2 * b * 1.3, b * 0.6, 0.6, 403), MONITOR_C, size=w * 0.6)
    # manchas de amarillento
    c.drawOval(skia.Rect(x + w * 0.6, y + h + b * 0.4, x + w * 1.05, y + h + b * 1.4), paint('#c9b17a', 0.25, blur=8))
    c.drawRect(skia.Rect(x - 3, y - 3, x + w + 3, y + h + 3), paint(INK, 0.9))
    r = skia.Rect(x, y, x + w, y + h)
    if on > 0 and screen_fn:
        c.save()
        c.clipRect(r, skia.ClipOp.kIntersect, True)
        c.translate(x, y)
        c.scale(w / 1920.0, h / 1080.0)
        screen_fn(c)
        c.restore()
        if on < 1:
            c.drawRect(r, paint('#0c0b10', 1 - on))
    else:
        c.drawRect(r, paint('#16151b', 1))
        c.drawRect(skia.Rect(x, y, x + w * 0.5, y + h * 0.4), paint('#ffffff', 0.04))
    # reflejo del vidrio
    c.drawPath(poly([(x + w * 0.55, y), (x + w * 0.75, y), (x + w * 0.45, y + h), (x + w * 0.25, y + h)]),
               paint('#ffffff', 0.05))
    if power_led:
        c.drawCircle(x + w - b * 0.2, y + h + b * 1.0, 4, paint('#7ee08a' if on > 0 else '#555555', 1))
    # botón de encendido
    c.drawCircle(x + w - b * 0.9, y + h + b * 1.0, 6, paint(shade(MONITOR_C, -0.3), 1))
    return r


def keyboard(c, x, y, w, pressed=None, color=MONITOR_C):
    h = w * 0.28
    shape(c, rrect(x, y, w, h, 10, 0.5, 411), color, size=h)
    kw = w / 15.5
    for row in range(4):
        for k in range(14 if row < 3 else 9):
            kx = x + kw * 0.5 + k * kw + (row * kw * 0.2)
            if row == 3 and k > 2:
                kx += kw * 0.3
            ky = y + h * 0.12 + row * h * 0.21
            pr = pressed == (row, k)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(kx, ky + (2 if pr else 0), kx + kw * 0.82, ky + h * 0.16 + (2 if pr else 0)), 3, 3),
                        paint(shade(color, -0.12 if not pr else -0.3), 1))
    # flechas
    ax, ay = x + w - kw * 3.6, y + h * 0.75
    for i, (dx, dy) in enumerate(((1, 0), (0, 1), (2, 1), (1, 1))):
        pr = pressed == ('arrow', i)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(ax + dx * kw, ay + dy * h * 0.12 - h * 0.12 + (2 if pr else 0),
                                                    ax + dx * kw + kw * 0.85, ay + dy * h * 0.12 + (2 if pr else 0)), 3, 3),
                    paint(shade(color, -0.2 if not pr else -0.45), 1))
    return (ax, ay)


def mouse_dev(c, x, y, s=1.0, color=MONITOR_C):
    with at(c, x, y, s):
        shape(c, ellipse(0, 0, 22, 32, 0.4, 421), color, size=40)
        line(c, [(0, -32), (0, -6)], INK, 2, 0.6)
        line(c, [(0, -32), (-6, -60), (10, -90)], '#7a6a5a', 3, 0.8)


def tower(c, x, y, w=120, h=260):
    box(c, x, y, w, h, MONITOR_C, depth=40, seed=431)
    for k in range(3):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + 15, y + 20 + k * 30, x + w - 15, y + 40 + k * 30), 4, 4),
                    paint(shade(MONITOR_C, -0.15), 1))
    c.drawCircle(x + w / 2, y + h - 50, 10, paint(shade(MONITOR_C, -0.25), 1))


def speaker(c, x, y, w=70, h=110):
    box(c, x, y, w, h, '#4a4246', depth=18, seed=441)
    c.drawCircle(x + w / 2, y + h * 0.62, w * 0.3, paint('#2c2629', 1))
    c.drawCircle(x + w / 2, y + h * 0.25, w * 0.13, paint('#2c2629', 1))


def wicker_chair(c, x, y, s=1.0, back_only=False, seat_only=False, creak=0.0):
    """Silla de mimbre de perfil (mira a la derecha). (x,y) = punto del piso bajo el asiento."""
    col_ = '#c8955a'
    with at(c, x + math.sin(creak * 40) * creak * 3, y, s):
        if not seat_only:
            back = blob([(-110, -420), (-70, -760), (-30, -800), (10, -770), (-20, -440)], 0.8, 451)
            shape(c, back, col_, size=120)
            weave(c, back, col_, 14)
            c.drawPath(back, paint(INK, 0.9, stroke=LW))
        if back_only:
            return
        seat = blob([(-140, -440), (150, -450), (160, -400), (-130, -390)], 0.6, 452)
        shape(c, seat, shade(col_, 0.05), size=60)
        weave(c, seat, col_, 12)
        c.drawPath(seat, paint(INK, 0.9, stroke=LW))
        for lx in (-110, 130):
            line(c, [(lx, -400), (lx + (-8 if lx < 0 else 8), 0)], shade(col_, -0.25), 14)
            line(c, [(lx, -400), (lx + (-8 if lx < 0 else 8), 0)], INK, 2, 0.6)


def wicker_chair_front(c, x, y, s=1.0):
    """Respaldo de silla de mimbre visto de frente (para planos frontales de Emilia)."""
    col_ = '#c8955a'
    with at(c, x, y, s):
        back = blob([(-170, 0), (-190, -260), (-120, -360), (0, -385), (120, -360), (190, -260), (170, 0)], 0.8, 455)
        shape(c, back, col_, size=200)
        weave(c, back, col_, 18)
        c.drawPath(back, paint(INK, 0.9, stroke=LW))


def lamp(c, x, y, on=1.0, s=1.0):
    with at(c, x, y, s):
        shape(c, ellipse(0, 0, 50, 12, 0.4, 461), '#7a5a46')
        line(c, [(0, -6), (0, -150), (40, -200)], '#7a5a46', 9)
        shade_p = blob([(10, -230), (95, -250), (110, -180), (25, -165)], 0.5, 462)
        shape(c, shade_p, '#e6b25a', size=80)
        if on:
            glow(c, 70, -175, 260, '#ffd79a', 0.45 * on)


def clock(c, x, y, r, hh, mm, color='#f3ead6', rim='#8a5a3c'):
    shape(c, ellipse(x, y, r + 10, r + 10, 0.5, 471), rim, size=r * 2)
    shape(c, ellipse(x, y, r, r, 0.5, 472), color, shadow=False, size=r * 2)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.drawLine(x + math.sin(a) * r * 0.8, y - math.cos(a) * r * 0.8, x + math.sin(a) * r * 0.92,
                   y - math.cos(a) * r * 0.92, paint(INK, 0.8, stroke=3 if i % 3 == 0 else 1.6))
    ah = (hh % 12 + mm / 60) / 12 * 2 * math.pi
    am = mm / 60 * 2 * math.pi
    c.drawLine(x, y, x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5, paint(INK, 1, stroke=6))
    c.drawLine(x, y, x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75, paint(INK, 1, stroke=4))
    c.drawCircle(x, y, 6, paint(INK, 1))


def teacup(c, x, y, s=1.0, t=0.0, steam=1.0, tilt=0.0, spill=0.0, color='#f3eadb'):
    with at(c, x, y, s, rot=tilt):
        shape(c, ellipse(0, 4, 60, 12, 0.4, 481), shade(color, -0.05), size=40)
        body = blob([(-42, -60), (42, -60), (34, -8), (0, 2), (-34, -8)], 0.5, 482)
        shape(c, body, color, size=60)
        c.drawOval(skia.Rect(-42, -68, 42, -52), paint('#9a5a2a', 1))
        c.drawOval(skia.Rect(-42, -68, 42, -52), paint(INK, 0.9, stroke=2.5))
        line(c, [(40, -48), (64, -42), (60, -20), (34, -18)], INK, 9)
        line(c, [(40, -48), (64, -42), (60, -20), (34, -18)], color, 4.5)
        line(c, [(-30, -32), (30, -32)], '#c46a5a', 4, 0.7)
    if steam > 0:
        for k in range(3):
            ph = (t * 0.5 + k / 3) % 1
            sx = x + (k - 1) * 14 * s
            pts = [(sx + math.sin(ph * 6 + j) * 8 * s, y - (70 + ph * 80 + j * 22) * s) for j in range(4)]
            line(c, pts, '#ffffff', 5 * s, steam * 0.45 * math.sin(ph * math.pi))
    if spill > 0:
        c.drawOval(skia.Rect(x - 40 * s, y - 6 * s, x + (40 + 160 * spill) * s, y + 14 * s), paint('#9a5a2a', 0.85))


def phone(c, x, y, s=1.0, rot=0.0, screen=None, t=0.0, face_down=False, vibrate=0.0, color='#2b2a33'):
    """Teléfono celular. screen: función(c, w, h) que dibuja la pantalla en coordenadas locales."""
    w, h = 120, 230
    vx = math.sin(t * 90) * 3 * vibrate
    with at(c, x + vx, y, s, rot=rot):
        if face_down:
            shape(c, rrect(-w / 2, -h / 2, w, h, 18, 0.4, 491), '#4a4a58', size=w)
            c.drawCircle(-w * 0.25, -h * 0.35, 10, paint('#1f1f25', 1))
            return
        shape(c, rrect(-w / 2, -h / 2, w, h, 18, 0.4, 492), color, size=w, light=False)
        r = skia.Rect(-w / 2 + 9, -h / 2 + 16, w / 2 - 9, h / 2 - 16)
        c.drawRect(r, paint('#1b2230', 1))
        if screen:
            c.save()
            c.clipRect(r, skia.ClipOp.kIntersect, True)
            c.translate(r.left(), r.top())
            screen(c, r.width(), r.height())
            c.restore()
        if vibrate > 0:
            for k in (-1, 1):
                line(c, [(k * (w / 2 + 14), -30), (k * (w / 2 + 22), 0), (k * (w / 2 + 14), 30)], INK, 3, vibrate)


def gift_box(c, x, y, w, h, color='#b85a4a', ribbon='#e8c35a', t=0.0, open_=0.0, cello=1.0, stamps=False, s=1.0):
    """Caja de regalo envuelta en celofán (regalos del hijo desde Hong Kong)."""
    with at(c, x, y, s):
        box(c, 0, 0, w, h, color, depth=w * 0.25, seed=501)
        line(c, [(w / 2, 0), (w / 2, h)], ribbon, 12)
        line(c, [(0, h / 2), (w, h / 2)], ribbon, 12)
        if stamps:
            for k in range(3):
                sx = w * 0.12 + k * w * 0.13
                shape(c, rrect(sx, h * 0.62, w * 0.11, h * 0.2, 2, 0.3, 502 + k), ['#e9d9b0', '#d7e3c8', '#e3c6c6'][k],
                      shadow=False, lw=1.6)
                # pequeño skyline de Hong Kong en la estampilla
                for j in range(4):
                    bh = h * (0.05 + rnd(503, j + k * 4) * 0.08)
                    c.drawRect(skia.Rect(sx + 4 + j * w * 0.022, h * 0.78 - bh, sx + 4 + j * w * 0.022 + w * 0.016, h * 0.78),
                               paint('#5a6a8a', 0.8))
        if cello > 0:
            cp = blob([(-12, h + 6), (-18, -20), (w * 0.3, -w * 0.18 - 10), (w + w * 0.25, -w * 0.2),
                       (w + w * 0.3, h * 0.4), (w + 14, h + 8)], 2.5, 504)
            c.drawPath(cp, paint('#dff0ff', 0.18 * cello))
            c.drawPath(cp, paint('#ffffff', 0.55 * cello, stroke=2))
            for k in range(5):
                gx = w * (0.1 + 0.2 * k) + math.sin(t * 3 + k) * 4
                line(c, [(gx, -10), (gx + 16, h * 0.3)], '#ffffff', 3, 0.5 * cello)


def card(c, x, y, s=1.0, rot=0.0):
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-80, -50, 160, 100, 10, 0.4, 511), '#f2efe6', size=60)
        c.drawRect(skia.Rect(-80, -30, 80, -14), paint('#3a3a46', 1))
        for k in range(8):
            c.drawRect(skia.Rect(-62 + k * 15, 10, -52 + k * 15, 26), paint('#6a6a78', 0.8))
        shape(c, ellipse(55, 20, 16, 16, 0.3, 512), '#f29ab4', shadow=False, lw=2)


def kentuki_box(c, x, y, w, h, t=0.0, s=1.0, logo=True, dirty=0.0, open_lid=1.0, empty=True):
    """Caja del producto: frente casi todo de celofán (se ve vacía) y fotos de la conejita
    de frente, de perfil y de espaldas en el costado."""
    from . import rabbit as R
    d = w * 0.75
    with at(c, x, y, s):
        # costado ancho con las tres fotos
        side = poly([(w, 0), (w + d * 0.62, -d * 0.42), (w + d * 0.62, h - d * 0.42), (w, h)])
        shape(c, side, '#f2dde8', shadow=False)
        top = poly([(0, 0), (d * 0.62, -d * 0.42), (w + d * 0.62, -d * 0.42), (w, 0)])
        shape(c, top, '#ead8e2', shadow=False)
        c.save()
        m = skia.Matrix()
        m.setAll(d * 0.62 / 300.0, 0, w, -d * 0.42 / 300.0, 1, 0, 0, 0, 1)
        c.concat(m)
        for k, kw in enumerate((dict(), dict(yaw=0.95), dict(back=True))):
            fy = h * (0.12 + k * 0.29)
            c.drawRect(skia.Rect(40, fy, 260, fy + h * 0.25), paint('#ffffff', 1))
            c.drawRect(skia.Rect(40, fy, 260, fy + h * 0.25), paint(INK, 0.5, stroke=2))
            R.draw(c, 150, fy + h * 0.23, h * 0.00072, 0, shadow=False, **kw)
        c.restore()
        shape(c, rrect(0, 0, w, h, 6, 0.6, 521), '#f6eef2', size=min(w, h))
        # frente de celofán: se ve el interior vacío
        win = rrect(w * 0.08, h * 0.08, w * 0.84, h * 0.72, 10, 0.4, 522)
        c.drawPath(win, paint('#e8dcc8', 1))
        c.drawPath(shifted_path(win, 0, 0), paint('#c9b8a0', 0.5, stroke=26, blur=12))
        c.drawOval(skia.Rect(w * 0.25, h * 0.62, w * 0.75, h * 0.76), paint('#b8a690', 0.5, blur=6))
        c.drawPath(win, paint('#ffffff', 0.28))
        c.drawPath(win, paint(INK, 0.8, stroke=2.5))
        line(c, [(w * 0.18, h * 0.16), (w * 0.34, h * 0.6)], '#ffffff', 6, 0.7)
        line(c, [(w * 0.3, h * 0.14), (w * 0.4, h * 0.4)], '#ffffff', 4, 0.5)
        c.drawRect(skia.Rect(w * 0.02, h * 0.84, w * 0.98, h * 0.97), paint('#f29ab4', 1))
        if logo:
            from .fx import font
            f = font('Lora', h * 0.09)
            tw = f.measureText('kentuki')
            c.drawString('kentuki', w * 0.5 - tw / 2, h * 0.94, f, paint('#ffffff', 1))
        if dirty > 0:
            for i in range(7):
                c.drawCircle(rnd(531, i) * w, rnd(532, i) * h, 18 + rnd(533, i) * 20, paint('#8a7660', 0.12 * dirty, blur=10))


def shifted_path(path, dx, dy):
    p = skia.Path(path)
    p.offset(dx, dy)
    return p


def cucha(c, x, y, w=330, h=120, back=True, front=True):
    """Cucha de felpa fucsia con pintitas blancas."""
    col_ = '#e0408a'
    if back:
        rim = ellipse(x, y - h * 0.45, w * 0.5, h * 0.5, 1.0, 541)
        shape(c, rim, col_, size=w * 0.4)
        c.drawOval(skia.Rect(x - w * 0.38, y - h * 0.62, x + w * 0.38, y - h * 0.2), paint(shade(col_, -0.3), 1))
    if front:
        fr = blob([(x - w * 0.52, y - h * 0.5), (x - w * 0.45, y + 4), (x + w * 0.45, y + 4), (x + w * 0.52, y - h * 0.5),
                   (x + w * 0.3, y - h * 0.25), (x - w * 0.3, y - h * 0.25)], 1.0, 542)
        shape(c, fr, col_, size=w * 0.3)
        for i in range(16):
            px = x + (rnd(543, i) - 0.5) * w * 0.9
            py = y - h * (0.05 + rnd(544, i) * 0.4)
            if fr.contains(px, py):
                c.drawCircle(px, py, 6, paint('#ffffff', 0.9))


def charger(c, x, y, w=150, state=None, t=0.0):
    """Base de carga. state: None (sin luz), 'red', 'yellow', 'green'."""
    shape(c, ellipse(x, y - 6, w * 0.5, w * 0.12, 0.5, 551), '#d8d5dc', size=40)
    c.drawOval(skia.Rect(x - w * 0.5, y - 6, x + w * 0.5, y + 10), paint('#a9a5ae', 1))
    c.drawOval(skia.Rect(x - w * 0.5, y - 6, x + w * 0.5, y + 10), paint(INK, 0.8, stroke=2.5))
    if state:
        cc = {'red': '#ff5a5a', 'yellow': '#ffd24a', 'green': '#62e07a'}[state]
        pul = 0.6 + 0.4 * math.sin(t * 4)
        c.drawCircle(x + w * 0.38, y + 2, 6, paint(cc, 1))
        glow(c, x + w * 0.38, y + 2, 26, cc, 0.6 * pul)


def yarn(c, x, y, r=40, color='#7fb0d8'):
    shape(c, ellipse(x, y - r, r, r, 0.8, 561), color, size=r * 2)
    for k in range(5):
        a = k * 0.6
        c.drawArc(skia.Rect(x - r * 0.8, y - r * 1.8, x + r * 0.8, y - r * 0.2), a * 60, 140, False,
                  paint(shade(color, -0.3), 0.7, stroke=2.4))
    line(c, [(x + r, y - r * 0.4), (x + r * 1.8, y - 4), (x + r * 2.6, y - 2)], color, 4)


def toy_mouse(c, x, y, s=1.0):
    with at(c, x, y, s):
        shape(c, blob([(-40, 0), (-30, -26), (10, -30), (40, -6), (30, 2)], 0.5, 571), '#a8988a', size=40)
        shape(c, ellipse(20, -30, 10, 10, 0.4, 572), '#a8988a', shadow=False)
        line(c, [(-40, -4), (-70, -18), (-90, -6)], '#6a5a4a', 3)
        c.drawCircle(32, -14, 3, paint(INK, 1))


def note(c, x, y, s=1.0, rot=0.0):
    """Nota de Eva con tinta fucsia (escritura ilegible)."""
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-70, -55, 140, 110, 4, 0.8, 581), '#fff4e8', size=60, shadow=False)
        c.drawRect(skia.Rect(-25, -64, 25, -48), paint('#f4e6a8', 0.85))
        for k in range(4):
            yy = -30 + k * 20
            pts = []
            for j in range(12):
                pts.append((-55 + j * 9 + k * 2, yy + math.sin(j * 1.9 + k) * 4 - j * 0.6))
            line(c, pts, '#e0408a', 2.6, 0.95, smooth=True)
        c.drawPath(blob([(40, 28), (48, 20), (56, 28), (48, 40)], 0.2, 582), paint('#e0408a', 1))


def shoes_row(c, x, y, n=7, s=1.0):
    cols = ['#c0395a', '#2d2631', '#e8b04a', '#6a8fc0', '#f2efe6', '#8a4a6a', '#3a7a6a']
    with at(c, x, y, s):
        for i in range(n):
            sx = i * 70
            shape(c, blob([(sx, 0), (sx, -22), (sx + 20, -26), (sx + 55, -12), (sx + 58, 0)], 0.4, 591 + i),
                  cols[i % len(cols)], size=30)
            if i % 3 == 0:
                line(c, [(sx + 50, -2), (sx + 52, 18)], INK, 4)


def purse(c, x, y, s=1.0, open_=0.0):
    with at(c, x, y, s):
        line(c, [(-60, -80), (-30, -170), (30, -170), (60, -80)], '#5a3a3a', 8)
        shape(c, blob([(-110, 0), (-95, -90), (95, -90), (110, 0)], 0.6, 601), '#b8606a', size=90)
        if open_ > 0:
            c.drawOval(skia.Rect(-90, -100 - 20 * open_, 90, -80), paint('#3a2228', 1))


def wallet(c, x, y, s=1.0, open_=1.0, bills=1.0, rot=0.0):
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-90, -10, 180, 70, 10, 0.5, 611), '#6a4a3a', size=60)
        if open_ > 0:
            for k in range(int(4 * bills)):
                shape(c, rrect(-80 + k * 4, -30 - k * 6, 150, 50, 4, 0.5, 612 + k), '#9cc49a', shadow=False, lw=2)
            shape(c, rrect(-70, 0, 70, 44, 6, 0.5, 616), '#e8d47a', shadow=False, lw=2)


def bills(c, x, y, s=1.0, rot=0.0, n=3):
    with at(c, x, y, s, rot=rot):
        for k in range(n):
            shape(c, rrect(-75 + k * 5, -25 - k * 7, 150, 50, 4, 0.5, 621 + k), '#9cc49a', shadow=False, lw=2)
            c.drawCircle(-75 + k * 5 + 75, -k * 7, 12, paint('#6a9a6a', 0.7, stroke=2))


def frying_pan(c, x, y, s=1.0, rot=0.0, eggs=2, t=0.0):
    with at(c, x, y, s, rot=rot):
        line(c, [(110, -10), (260, -40)], '#3a3236', 22)
        shape(c, ellipse(0, 0, 130, 34, 0.5, 631), '#3a3236', size=60)
        c.drawOval(skia.Rect(-112, -26, 112, 22), paint('#2a2427', 1))
        for k in range(eggs):
            ex = -50 + k * 80
            shape(c, ellipse(ex, -2, 40, 15, 1.2, 632 + k), '#fbf6ea', shadow=False, lw=2)
            c.drawCircle(ex + 4, -5, 11, paint('#f2b23a', 1))
        for k in range(3):
            ph = (t * 0.7 + k * 0.33) % 1
            line(c, [(-40 + k * 40, -30 - ph * 80), (-30 + k * 40, -60 - ph * 80)], '#ffffff', 4, 0.4 * math.sin(ph * math.pi))


def eggshells(c, x, y, s=1.0):
    with at(c, x, y, s):
        for k, (dx, r) in enumerate(((0, 0), (60, 30), (120, -20))):
            shape(c, blob([(dx - 22, 0), (dx - 18, -18), (dx - 6, -10), (dx + 4, -22), (dx + 14, -10), (dx + 22, 0)], 0.5,
                          641 + k), '#f3e6cf', shadow=False, lw=2)


def bottle(c, x, y, s=1.0, color='#7a5a2a'):
    with at(c, x, y, s):
        shape(c, blob([(-22, 0), (-24, -110), (-10, -140), (-9, -180), (9, -180), (10, -140), (24, -110), (22, 0)],
                      0.4, 651), color, size=40)
        c.drawRect(skia.Rect(-22, -90, 22, -50), paint('#f0e2b0', 0.95))
        c.drawRect(skia.Rect(-12, -100, -4, -10), paint('#ffffff', 0.25))


def plate(c, x, y, s=1.0, food=True):
    with at(c, x, y, s):
        shape(c, ellipse(0, 0, 90, 22, 0.4, 661), '#f3f0e8', size=40)
        c.drawOval(skia.Rect(-60, -14, 60, 12), paint('#e2ddd2', 1))
        if food:
            c.drawOval(skia.Rect(-40, -12, 30, 6), paint('#d9a54a', 1))
            c.drawOval(skia.Rect(-5, -16, 40, 2), paint('#c0503a', 1))


def magazine(c, x, y, s=1.0, rot=0.0, color='#e07a5a'):
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-90, -14, 180, 28, 3, 0.5, 671), color, size=20, shadow=False)
        c.drawRect(skia.Rect(-80, -8, 20, 0), paint('#ffffff', 0.6))


def towel_corner(c, x, y, s=1.0, rot=0.0, color='#f6efe6'):
    with at(c, x, y, s, rot=rot):
        shape(c, blob([(-200, -60), (40, -90), (180, 40), (-60, 120)], 3.0, 681), color, size=120)
        for k in range(4):
            line(c, [(-150 + k * 60, -40), (-80 + k * 60, 90)], shade(color, -0.12), 3, 0.6)


def lipstick(c, x, y, s=1.0, rot=0.0, open_=True, broken=False):
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-12, -40, 24, 50, 4, 0.3, 691), '#c9a24a', size=20, shadow=False)
        if open_:
            tip = blob([(-9, -40), (-9, -70), (0, -82), (9, -66), (9, -40)], 0.3, 692)
            if broken:
                tip = blob([(-9, -40), (-9, -52), (9, -58), (9, -40)], 0.3, 693)
            shape(c, tip, '#d1242f', size=16, shadow=False)


def yoga_mat(c, x, y, s=1.0, rot=0.0):
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-30, -150, 60, 300, 28, 0.5, 701), '#8a6ab8', size=60)
        c.drawOval(skia.Rect(-30, -165, 30, -135), paint(shade('#8a6ab8', -0.25), 1))
        c.drawOval(skia.Rect(-30, -165, 30, -135), paint(INK, 0.8, stroke=2))
        line(c, [(-30, -60), (30, -60)], '#3a3236', 5)


def cake_box(c, x, y, s=1.0):
    with at(c, x, y, s):
        box(c, -70, -90, 140, 90, '#f3e6d6', depth=40, seed=711)
        line(c, [(0, -90), (0, 0)], '#7a3a2a', 6)
        c.drawOval(skia.Rect(-30, -112, 30, -96), paint('#7a3a2a', 0.9, stroke=5))


def cart(c, x, y, s=1.0):
    with at(c, x, y, s):
        p = poly([(-150, -300), (150, -300), (120, -120), (-130, -120)])
        c.drawPath(p, paint('#c9d2d8', 0.35))
        for k in range(8):
            xx = -150 + k * 40
            c.drawLine(xx, -300, xx * 0.86 + 2, -120, paint('#8a969e', 0.9, stroke=3))
        for k in range(5):
            yy = -300 + k * 45
            c.drawLine(-150 + k * 4, yy, 150 - k * 6, yy, paint('#8a969e', 0.9, stroke=3))
        c.drawPath(p, paint(INK, 0.8, stroke=3))
        line(c, [(150, -300), (190, -360), (260, -360)], '#8a969e', 8)
        line(c, [(-130, -120), (-120, -40), (120, -40), (120, -120)], '#8a969e', 6)
        for wx in (-110, 110):
            shape(c, ellipse(wx, -16, 16, 16, 0.4, 721), '#3a3236')


def can(c, x, y, s=1.0, color='#4a8a5a', label='#f3e6c8'):
    with at(c, x, y, s):
        shape(c, rrect(-30, -80, 60, 80, 8, 0.4, 731), color, size=40)
        c.drawRect(skia.Rect(-30, -60, 30, -24), paint(label, 0.95))
        c.drawOval(skia.Rect(-30, -86, 30, -74), paint(shade(color, 0.2), 1))
        c.drawOval(skia.Rect(-30, -86, 30, -74), paint(INK, 0.7, stroke=2))


def peach(c, x, y, s=1.0):
    with at(c, x, y, s):
        shape(c, ellipse(0, -30, 32, 30, 0.6, 741), '#f2a26a', size=50)
        c.drawOval(skia.Rect(-10, -56, 22, -24), paint('#f06a5a', 0.45, blur=6))
        line(c, [(0, -60), (2, -40)], INK, 2, 0.5)
        shape(c, blob([(2, -60), (20, -74), (30, -64), (14, -58)], 0.3, 742), '#7aa05a', shadow=False, lw=2)


def photo(c, x, y, w, h, s=1.0, rot=0.0, content=None, frame='#fbf8f1', tape=True, border=14):
    """Foto impresa (con borde blanco) que muestra content(c, w, h)."""
    with at(c, x, y, s, rot=rot):
        shape(c, rrect(-w / 2 - border, -h / 2 - border, w + 2 * border, h + 2 * border, 3, 0.4, 751), frame,
              size=50, shadow=False, lw=2.4)
        r = skia.Rect(-w / 2, -h / 2, w / 2, h / 2)
        c.drawRect(r, paint('#cfd8dc', 1))
        if content:
            c.save()
            c.clipRect(r, skia.ClipOp.kIntersect, True)
            c.translate(-w / 2, -h / 2)
            content(c, w, h)
            c.restore()
        c.drawRect(r, paint(INK, 0.6, stroke=1.6))
        if tape:
            c.save()
            c.rotate(-8)
            c.drawRect(skia.Rect(-28, -h / 2 - border - 10, 28, -h / 2 - border + 12), paint('#f6e9b0', 0.8))
            c.restore()


def magnet(c, x, y, color, r=14):
    shape(c, ellipse(x, y, r, r, 0.3, 761), color, shadow=False, lw=2)


def plant(c, x, y, s=1.0, pot='#c86a4a', leaf='#6a9a5a', t=0.0):
    with at(c, x, y, s):
        for k in range(7):
            a = -math.pi / 2 + (k - 3) * 0.32 + noise1(t * 0.4 + k, 771) * 0.04
            L = 120 + (k % 3) * 30
            tip = (math.cos(a) * L, -60 + math.sin(a) * L)
            mid = (math.cos(a) * L * 0.5 - 10, -60 + math.sin(a) * L * 0.5)
            lp = blob([(0, -60), (mid[0] - 16, mid[1]), tip, (mid[0] + 16, mid[1])], 0.5, 772 + k)
            shape(c, lp, shade(leaf, (k % 3) * 0.06 - 0.06), size=40)
        shape(c, blob([(-55, -70), (55, -70), (42, 0), (-42, 0)], 0.5, 779), pot, size=60)


def frame_pic(c, x, y, w, h, content=None, color='#8a5a3c'):
    shape(c, rrect(x - 12, y - 12, w + 24, h + 24, 4, 0.5, 781), color, size=40)
    r = skia.Rect(x, y, x + w, y + h)
    c.drawRect(r, paint('#efe2c4', 1))
    if content:
        with clip(c, (x, y, x + w, y + h)):
            c.save()
            c.translate(x, y)
            content(c, w, h)
            c.restore()
    c.drawRect(r, paint(INK, 0.7, stroke=2))


def mountains_pic(c, w, h):
    vgrad_rect(c, 0, 0, w, h, '#f2c9a0', '#f7e4c6')
    p = poly([(0, h), (0, h * 0.6), (w * 0.3, h * 0.25), (w * 0.5, h * 0.5), (w * 0.72, h * 0.18), (w, h * 0.55), (w, h)])
    c.drawPath(p, paint('#8a7aa8', 1))
    p2 = poly([(w * 0.62, h * 0.32), (w * 0.72, h * 0.18), (w * 0.8, h * 0.3)])
    c.drawPath(p2, paint('#ffffff', 0.9))
    c.drawRect(skia.Rect(0, h * 0.8, w, h), paint('#7a9a5a', 1))


def door(c, x, y, w, h, color='#a0684a', open_=0.0, frame=True):
    if frame:
        shape(c, rrect(x - 16, y - 16, w + 32, h + 16, 4, 0.5, 791), shade(color, 0.15), size=40)
    if open_ > 0:
        c.drawRect(skia.Rect(x, y, x + w, y + h), paint('#3a2a2a', 1))
    dw = w * (1 - open_ * 0.85)
    shape(c, rrect(x, y, dw, h, 3, 0.5, 792), color, size=w)
    if dw > w * 0.4:
        for k in range(2):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + dw * 0.15, y + h * (0.08 + k * 0.48), x + dw * 0.85,
                                                        y + h * (0.44 + k * 0.48)), 6, 6), paint(INK, 0.4, stroke=2.4))
        c.drawCircle(x + dw * 0.86, y + h * 0.52, 9, paint('#e0c060', 1))
        c.drawCircle(x + dw * 0.86, y + h * 0.52, 9, paint(INK, 0.8, stroke=2))


def window(c, x, y, w, h, content=None, frame='#f3ede2', curtain=None, t=0.0, mull=True):
    shape(c, rrect(x - 18, y - 18, w + 36, h + 36, 6, 0.5, 801), frame, size=50)
    with clip(c, (x, y, x + w, y + h)):
        if content:
            c.save()
            c.translate(x, y)
            content(c, w, h)
            c.restore()
    c.drawRect(skia.Rect(x, y, x + w, y + h), paint(INK, 0.8, stroke=2.5))
    if mull:
        c.drawLine(x + w / 2, y, x + w / 2, y + h, paint(frame, 1, stroke=12))
        c.drawLine(x, y + h * 0.45, x + w, y + h * 0.45, paint(frame, 1, stroke=10))
    c.drawRect(skia.Rect(x - 30, y + h + 6, x + w + 30, y + h + 26), paint(shade(frame, -0.1), 1))
    if curtain:
        for side in (-1, 1):
            cx_ = x + (0 if side < 0 else w)
            sway = noise1(t * 0.4, 811 + side) * 8
            cp = blob([(cx_ - side * 10, y - 40), (cx_ + side * 110 + sway, y - 40), (cx_ + side * 80 + sway * 1.5, y + h * 0.5),
                       (cx_ + side * 120 + sway * 2, y + h + 40), (cx_ - side * 20, y + h + 40)], 1.0, 812 + side)
            shape(c, cp, curtain, size=100)
            for k in range(3):
                line(c, [(cx_ + side * (20 + k * 28), y - 30), (cx_ + side * (16 + k * 30) + sway, y + h + 30)],
                     shade(curtain, -0.2), 2.5, 0.5)


def dish_towel(c, x, y, s=1.0, open_=0.0, color='#e8e0d0', stripe='#c8403a'):
    """Repasador en el que viene envuelta la conejita usada."""
    with at(c, x, y, s):
        w = lerp(160, 320, open_)
        p = blob([(-w, -40), (-w * 0.6, -150 + open_ * 60), (w * 0.6, -160 + open_ * 60), (w, -40), (w * 0.8, 20),
                  (-w * 0.8, 20)], 4.0, 1801)
        shape(c, p, color, size=150)
        for k in range(3):
            line(c, [(-w * 0.85, -30 - k * 22), (w * 0.85, -34 - k * 22)], stripe, 5, 0.85)


def wrapped_box(c, x, y, w, h, s=1.0, paper='#e9b44a', open_=0.0, dirty=0.0):
    with at(c, x, y, s):
        box(c, 0, 0, w, h, paper, depth=w * 0.3, seed=1811)
        for k in range(14):
            c.drawCircle(rnd(1812, k) * w, rnd(1813, k) * h, 9, paint('#ffffff', 0.55))
        if open_ < 0.5:
            line(c, [(w / 2, 0), (w / 2, h)], '#c8403a', 10)
            line(c, [(0, h / 2), (w, h / 2)], '#c8403a', 10)
        if dirty > 0:
            for i in range(6):
                c.drawCircle(rnd(1814, i) * w, rnd(1815, i) * h, 16, paint('#7a6a5a', 0.12 * dirty, blur=8))


def photo_eva_rabbit(c, w, h):
    """Foto de la heladera de Eva: Eva en el sofá con su conejita dormida, tirándole un beso."""
    from . import people as P, rabbit as R
    vgrad_rect(c, 0, 0, w, h, '#b8a8d0', '#9a8ac0')
    c.save()
    c.scale(w / 400.0, h / 300.0)
    P.Person(P.EVA).draw(c, 200, 110 + 868 * 0.42, 0.42, view='front', t=0, expr='tender', bust=True, idle=0,
                         face=dict(mouth=(0.55, 0.25, 0.3, 0.0)), hand_L=(120, -500), hand_R=(-120, -500))
    R.draw(c, 205, 300, 0.42, 0, eyes=0.0, shadow=False)
    c.restore()


def photo_klaus(c, w, h):
    from . import people as P
    vgrad_rect(c, 0, 0, w, h, '#bcd9d2', '#a9cbc4')
    c.save()
    c.scale(w / 400.0, h / 300.0)
    P.Person(P.KLAUS_UNDER).draw(c, 200, 120 + 964 * 0.42, 0.42, view='front', t=0, expr='neutral', bust=True, idle=0)
    c.restore()


def photo_emilia_phone(c, w, h):
    """Foto tomada por la conejita de Lima: Emilia hablando por teléfono (desde abajo)."""
    from . import people as P
    vgrad_rect(c, 0, 0, w, h, '#ebc49c', '#e3b68d')
    c.save()
    c.scale(w / 400.0, h / 300.0)
    P.Person(P.EMILIA_ROBE).draw(c, 200, 130 + 760 * 0.5, 0.5, view='front', t=0, expr='closed', bust=True, idle=0,
                                 hand_L=(95, -650), bend_L=1, handshape_L='hold',
                                 hold_L=lambda cc: phone(cc, 0, -6, 0.45, rot=-10))
    c.restore()


def photo_fridge(c, w, h):
    """Foto de la heladera de Emilia cubierta de fotos."""
    vgrad_rect(c, 0, 0, w, h, '#e9d8bc', '#dcc6a4')
    c.save()
    c.scale(w / 400.0, h / 300.0)
    shape(c, rrect(110, 20, 180, 300, 20, 0.6, 1821), '#efe7d2', size=100)
    for k in range(9):
        x = 130 + (k % 3) * 52
        y = 50 + (k // 3) * 70
        c.drawRect(skia.Rect(x, y, x + 40, y + 50), paint('#fbf8f1', 1))
        c.drawRect(skia.Rect(x + 4, y + 4, x + 36, y + 40), paint(['#9a8ac0', '#bcd9d2', '#f29ab4'][k % 3], 1))
    c.restore()
