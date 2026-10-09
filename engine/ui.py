"""Interfaz y recursos de montaje: vista del kentuki con su controlador, subtítulos ilegibles del
traductor, pantallas de teléfono y computadora, mapa, pantalla dividida y secuencias de planos.

Regla del proyecto: ningún texto legible explica la historia. Los botones son íconos y los
subtítulos del traductor son trazos amarillos ilegibles.
"""
import math
import skia
from .core import W, H, shade, noise1, rnd, lerp, clamp, prog, smooth, ease_io, ease_out, col
from .draw import (INK, LW, paint, smooth_path, ellipse, blob, shape, line, at, rrect, poly, glow, clip,
                   lin_grad, rad_grad, layer, vgrad_rect)

HUD_DARK = '#1d1a22'
YELLOW = '#ffd84a'


# ---------------------------------------------------------------- escritura ilegible
def glyphs(c, x, y, w, size, seed=0, color=YELLOW, progress=1.0, a=1.0, lw=None):
    """Trazos tipo manuscrito ilegible (palabras inventadas sin letras reales)."""
    lw = lw or max(2.0, size * 0.13)
    cx = x
    i = 0
    limit = x + w * clamp(progress)
    while cx < x + w - size * 0.5 and cx < limit:
        wl = size * (1.2 + rnd(seed, i) * 2.6)
        wl = min(wl, x + w - cx)
        n = max(3, int(wl / (size * 0.32)))
        pts = []
        for j in range(n):
            px = cx + wl * j / (n - 1)
            if px > limit:
                break
            py = y + math.sin(j * 2.1 + rnd(seed, i * 7 + j) * 3) * size * 0.28 - (rnd(seed + 5, i * 3 + j) > 0.8) * size * 0.4
            pts.append((px, py))
        if len(pts) > 1:
            line(c, pts, color, lw, a)
        cx += wl + size * 0.55
        i += 1


def subtitle(c, t, t0, dur, seed=0, rect=None, lines=1, a=1.0):
    """Franja de subtítulo amarillo del traductor (ilegible). rect: zona de la vista (x,y,w,h)."""
    x0, y0, w0, h0 = rect or (0, 0, W, H)
    if t < t0 or t > t0 + dur:
        return
    k = max(min(w0 / W, h0 / H), 0.62)
    ap = prog(t, t0, t0 + 0.25, smooth) * (1 - prog(t, t0 + dur - 0.3, t0 + dur, smooth)) * a
    bw = w0 * (0.58 if w0 > 1500 else 0.8)
    bh = (54 + 46 * (lines - 1)) * k
    bx = x0 + (w0 - bw) / 2
    by = y0 + h0 - bh - 70 * k
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + bw, by + bh), 14 * k, 14 * k), paint('#141218', 0.62 * ap))
    for li in range(lines):
        gp = clamp((t - t0) / max(0.4, dur * 0.55) * lines - li)
        glyphs(c, bx + 34 * k, by + (30 + li * 46) * k, bw - 68 * k, 24 * k, seed + li * 13, YELLOW, gp, ap, 4.2 * k)


# ---------------------------------------------------------------- íconos
def icon_eye(c, x, y, r, open_=1.0, color='#ffffff', a=1.0):
    h = r * 0.62 * max(0.08, open_)
    p = smooth_path([(x - r, y), (x, y - h), (x + r, y), (x, y + h)], closed=True, k=0.22)
    c.drawPath(p, paint(color, a, stroke=r * 0.16))
    if open_ > 0.2:
        c.drawCircle(x, y, r * 0.3 * open_, paint(color, a))
    else:
        for k in (-1, 0, 1):
            c.drawLine(x + k * r * 0.45, y + r * 0.12, x + k * r * 0.6, y + r * 0.42, paint(color, a, stroke=r * 0.1))


def icon_arrow(c, x, y, r, ang, color='#ffffff', a=1.0, filled=False):
    with at(c, x, y, 1.0, rot=ang):
        p = poly([(r * 0.7, 0), (-r * 0.45, -r * 0.6), (-r * 0.45, r * 0.6)])
        if filled:
            c.drawPath(p, paint(color, a))
        else:
            c.drawPath(p, paint(color, a, stroke=r * 0.14))


def icon_battery(c, x, y, w, level, color='#ffffff', a=1.0, charging=False, t=0.0):
    h = w * 0.48
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + w, y + h), h * 0.18, h * 0.18), paint(color, a, stroke=w * 0.06))
    c.drawRect(skia.Rect(x + w, y + h * 0.3, x + w * 1.08, y + h * 0.7), paint(color, a))
    lvl = clamp(level)
    cc = '#62e07a' if lvl > 0.35 else ('#ffd24a' if lvl > 0.15 else '#ff5a5a')
    if lvl > 0:
        c.drawRect(skia.Rect(x + w * 0.08, y + h * 0.16, x + w * 0.08 + w * 0.84 * lvl, y + h * 0.84), paint(cc, a))
    if charging:
        pul = 0.6 + 0.4 * math.sin(t * 5)
        bolt = poly([(x + w * 0.55, y - h * 0.15), (x + w * 0.35, y + h * 0.55), (x + w * 0.5, y + h * 0.55),
                     (x + w * 0.42, y + h * 1.15), (x + w * 0.68, y + h * 0.4), (x + w * 0.52, y + h * 0.4)])
        c.drawPath(bolt, paint('#ffe066', a * pul))
        c.drawPath(bolt, paint(INK, a * 0.6, stroke=2))


def icon_rabbit(c, x, y, r, color='#ffffff', a=1.0):
    c.drawOval(skia.Rect(x - r * 0.55, y - r * 0.4, x + r * 0.55, y + r * 0.7), paint(color, a))
    for side in (-1, 1):
        line(c, [(x + side * r * 0.12, y - r * 0.35), (x + side * r * 0.2, y - r * 0.9), (x + side * r * 0.75, y - r * 0.5),
                 (x + side * r * 0.8, y + r * 0.1)], color, r * 0.22, a)


def icon_check(c, x, y, r, color='#62e07a', a=1.0, p=1.0):
    pts = [(x - r * 0.5, y), (x - r * 0.1, y + r * 0.4), (x + r * 0.55, y - r * 0.45)]
    if p < 1:
        k = clamp(p * 2)
        pts = pts[:1] + [(lerp(pts[0][0], pts[1][0], k), lerp(pts[0][1], pts[1][1], k))] + \
            ([(lerp(pts[1][0], pts[2][0], clamp(p * 2 - 1)), lerp(pts[1][1], pts[2][1], clamp(p * 2 - 1)))] if p > 0.5 else [])
    line(c, pts, color, r * 0.22, a, smooth=False)


def icon_cross(c, x, y, r, color='#ffffff', a=1.0):
    c.drawLine(x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45, paint(color, a, stroke=r * 0.2))
    c.drawLine(x + r * 0.45, y - r * 0.45, x - r * 0.45, y + r * 0.45, paint(color, a, stroke=r * 0.2))


def icon_link(c, x, y, r, broken=0.0, color='#ffffff', a=1.0):
    g = broken * r * 0.35
    for side in (-1, 1):
        with at(c, x + side * (r * 0.32 + g), y + side * g * 0.4, 1.0, rot=-35 + side * broken * 12):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-r * 0.45, -r * 0.22, r * 0.45, r * 0.22), r * 0.22, r * 0.22),
                        paint(color, a, stroke=r * 0.13))
    if broken > 0.3:
        for k in range(3):
            ang = -60 + k * 50
            c.drawLine(x + math.cos(math.radians(ang)) * r * 0.25, y + math.sin(math.radians(ang)) * r * 0.25,
                       x + math.cos(math.radians(ang)) * r * 0.5, y + math.sin(math.radians(ang)) * r * 0.5,
                       paint(color, a * broken, stroke=r * 0.08))


def icon_power(c, x, y, r, color='#ffffff', a=1.0):
    c.drawArc(skia.Rect(x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55), -60, 300, False,
              paint(color, a, stroke=r * 0.16))
    c.drawLine(x, y - r * 0.7, x, y - r * 0.1, paint(color, a, stroke=r * 0.16))


def icon_sound(c, x, y, r, color='#ffffff', a=1.0, t=0.0):
    for k in range(3):
        rr = r * (0.35 + k * 0.3)
        c.drawArc(skia.Rect(x - rr, y - rr, x + rr, y + rr), -40, 80, False,
                  paint(color, a * (0.5 + 0.5 * math.sin(t * 10 - k)), stroke=r * 0.12))


# ---------------------------------------------------------------- controlador del kentuki
def hud(c, t, rect=None, pressed=None, eye=1.0, battery=0.8, charging=False, chirp=0.0, red_hi=0.0,
        a=1.0, lying=False):
    """Interfaz del controlador sobre la vista del kentuki (íconos a los costados, sin texto)."""
    x0, y0, w0, h0 = rect or (0, 0, W, H)
    k = max(min(w0 / W, h0 / H), 0.62)
    # marco redondeado
    fr = skia.Path()
    fr.addRect(skia.Rect(x0, y0, x0 + w0, y0 + h0))
    inner = skia.Path()
    inner.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0 + 120 * k, y0 + 26 * k, x0 + w0 - 120 * k, y0 + h0 - 26 * k),
                                         40 * k, 40 * k))
    frame = skia.Op(fr, inner, skia.PathOp.kDifference_PathOp)
    c.drawPath(frame, paint(HUD_DARK, 0.82 * a))
    c.drawPath(inner, paint('#000000', 0.25 * a, stroke=6 * k))
    # columna izquierda: flechas en cruz
    cx, cy = x0 + 60 * k, y0 + h0 * 0.5
    for name, (dx, dy, ang) in dict(up=(0, -1, -90), down=(0, 1, 90), left=(-1, 0, 180), right=(1, 0, 0)).items():
        hi = pressed == name
        bx, by = cx + dx * 34 * k, cy + dy * 40 * k
        c.drawCircle(bx, by, 22 * k, paint('#ffffff' if hi else '#3a3542', (0.9 if hi else 0.8) * a))
        icon_arrow(c, bx, by, 13 * k, ang, '#1d1a22' if hi else '#ffffff', a, filled=True)
    # ícono de conejita arriba a la izquierda
    icon_rabbit(c, x0 + 60 * k, y0 + 90 * k, 26 * k, '#f29ab4', a)
    if chirp > 0:
        icon_sound(c, x0 + 95 * k, y0 + 92 * k, 28 * k, '#ffd84a', a * chirp, t)
    # columna derecha: ojo, batería, botón rojo
    rx = x0 + w0 - 60 * k
    hi = pressed == 'eye'
    c.drawCircle(rx, y0 + h0 * 0.38, 30 * k, paint('#ffffff' if hi else '#3a3542', 0.85 * a))
    icon_eye(c, rx, y0 + h0 * 0.38, 20 * k, eye, '#1d1a22' if hi else '#ffffff', a)
    icon_battery(c, rx - 26 * k, y0 + 70 * k, 52 * k, battery, '#ffffff', a, charging, t)
    rb = 26 * k * (1 + red_hi * 0.25)
    c.drawCircle(rx, y0 + h0 - 90 * k, rb, paint('#d93a3a', a))
    if red_hi > 0:
        glow(c, rx, y0 + h0 - 90 * k, rb * 2.4, '#ff6a6a', 0.6 * red_hi * a)
    icon_power(c, rx, y0 + h0 - 90 * k, rb * 0.9, '#ffffff', a)


def pov(c, t, feed, rect=None, tilt=0.0, zoom=1.0, center=None, shake=0.0, hud_kw=None, wet=0.0, dark=0.0,
        blur_edge=True, grade=None, show_hud=True):
    """Vista de la cámara del kentuki (Erfurt) con el controlador encima.

    feed(c) dibuja en coordenadas 1920x1080. tilt: rotación de cámara (p. ej. 80 si está acostada).
    """
    x0, y0, w0, h0 = rect or (0, 0, W, H)
    k = max(w0 / W, h0 / H)          # "cover": la vista llena el rectángulo
    sx = noise1(t * 9, 901) * shake * 20
    sy = noise1(t * 9, 902) * shake * 20
    cxw, cyw = center or (W / 2, H / 2)
    c.save()
    c.clipRect(skia.Rect(x0, y0, x0 + w0, y0 + h0), skia.ClipOp.kIntersect, True)
    c.translate(x0 + (w0 - W * k) / 2, y0 + (h0 - H * k) / 2)
    c.scale(k, k)
    c.save()
    c.translate(W / 2 + sx, H / 2 + sy)
    c.rotate(tilt)
    c.scale(zoom, zoom)
    c.translate(-cxw, -cyw)
    if grade is not None:
        with layer(c, cfilter=grade):
            feed(c)
    else:
        feed(c)
    c.restore()
    # efecto de lente: viñeta fría y leve aberración
    if blur_edge:
        sh = rad_grad((W / 2, H / 2), W * 0.6, ['#0a1830', '#0a1830', '#0a1830'], [0.0, 0.0, 0.42], [0, 0.6, 1])
        c.drawRect(skia.Rect(0, 0, W, H), paint('#000000', 1, shader=sh))
    if wet > 0:
        for i in range(26):
            wx = rnd(911, i) * W
            wy = (rnd(912, i) * H + t * 260 * (0.5 + rnd(913, i))) % H
            r = 18 + rnd(914, i) * 46
            c.drawCircle(wx, wy, r, paint('#dff3ff', 0.18 * wet))
            c.drawCircle(wx, wy, r, paint('#ffffff', 0.35 * wet, stroke=3))
            c.drawCircle(wx - r * 0.3, wy - r * 0.3, r * 0.25, paint('#ffffff', 0.5 * wet))
        c.drawRect(skia.Rect(0, 0, W, H), paint('#9ad0ff', 0.12 * wet))
    if dark > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#05050a', dark))
    c.restore()
    if show_hud:
        hud(c, t, rect=(x0, y0, w0, h0), **(hud_kw or {}))


# ---------------------------------------------------------------- pantallas de computadora
def app_window(c, color='#2a2733'):
    vgrad_rect(c, 0, 0, W, H, '#3a3644', '#24212c')
    c.drawRect(skia.Rect(0, 0, W, 70), paint('#4a4656', 1))
    for k, cc in enumerate(('#e86a5a', '#e8c25a', '#7ac46a')):
        c.drawCircle(40 + k * 40, 35, 12, paint(cc, 1))


def serial_screen(c, t, fill=1.0, ok=0.0, eye_btn=0.0, pressed=False):
    """Pantalla de activación: casillas que se completan, tilde verde y botón con ojo (sin texto)."""
    app_window(c)
    icon_rabbit(c, W / 2, 260, 70, '#f29ab4')
    n = 12
    bw = 92
    x0 = W / 2 - n * bw / 2
    for i in range(n):
        x = x0 + i * bw
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x + 8, 430, x + bw - 8, 540), 12, 12), paint('#ffffff', 0.9))
        if fill * n > i:
            c.drawCircle(x + bw / 2, 485, 16, paint('#2a2733', 1))
    if ok > 0:
        c.drawCircle(W / 2, 700, 80 * ease_out(ok), paint('#2f6a3a', 0.9))
        icon_check(c, W / 2, 700, 110, '#9cf0a8', 1.0, ok)
    if eye_btn > 0:
        a = eye_btn
        pul = 1 + 0.06 * math.sin(t * 6)
        c.drawRect(skia.Rect(0, 0, W, H), paint('#1c1a22', 0.7 * a))
        r = 120 * pul
        c.drawCircle(W / 2, H / 2, r, paint('#ffffff' if pressed else '#f29ab4', a))
        icon_eye(c, W / 2, H / 2, 80, 1.0, '#2a2733', a)


def browser_screen(c, t, scroll=0.0, highlight=0.0, contact=0.0, faces=None):
    """Sitio del club de fútbol: escudo rojo y blanco, grilla de jugadores (sin texto legible)."""
    vgrad_rect(c, 0, 0, W, H, '#f4f0ea', '#e8e2d8')
    c.drawRect(skia.Rect(0, 0, W, 64), paint('#d8d2c8', 1))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(160, 14, 1300, 50), 18, 18), paint('#ffffff', 1))
    glyphs(c, 190, 34, 400, 14, 951, '#8a8a8a', 1.0, 1.0, 3)
    c.drawRect(skia.Rect(0, 64, W, 230), paint('#c7362f', 1))
    # escudo
    sh = blob([(140, 90), (260, 90), (260, 170), (200, 215), (140, 170)], 0.4, 952)
    shape(c, sh, '#ffffff', shadow=False)
    c.drawLine(150, 165, 250, 105, paint('#c7362f', 1, stroke=18))
    glyphs(c, 320, 160, 700, 40, 953, '#ffffff', 1.0, 1.0, 7)
    from . import people as P
    ys = 300 - scroll * 300
    for i in range(10):
        col_i, row = i % 5, i // 5
        x = 120 + col_i * 340
        y = ys + row * 380
        hi = (i == 6) * highlight
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + 300, y + 340), 16, 16),
                    paint('#ffffff', 1))
        if hi > 0:
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 8, y - 8, x + 308, y + 348), 20, 20),
                        paint('#ffd84a', hi, stroke=10))
        with clip(c, (x, y, x + 300, y + 250)):
            vgrad_rect(c, x, y, 300, 250, '#d8e2ea', '#b8c8d6')
            if i == 6:
                P.Person(P.KLAUS).draw(c, x + 150, y + 560, 0.42, t=0, expr='proud', bust=True, idle=0, shadow=False)
            else:
                st = dict(P.KLAUS)
                st.update(skin=['#e5b79c', '#c99572', '#f1cdb9', '#a8775a', '#e8c2a8'][i % 5],
                          hair=['#3a2a22', '#c9a463', '#2a2427', '#5a3a2a', '#8a6a48'][i % 5],
                          stubble=(i % 2 == 0), eye_style='dot', key='p%d' % i)
                P.Person(st).draw(c, x + 150, y + 560, 0.42, t=0, expr='calm', bust=True, idle=0, shadow=False)
        glyphs(c, x + 30, y + 290, 240, 18, 960 + i, '#4a4a4a', 1.0, 1.0, 3.5)
    if contact > 0:
        a = contact
        c.drawRect(skia.Rect(0, 0, W, H), paint('#000000', 0.35 * a))
        bx, by = W / 2 - 420, H / 2 - 230
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + 840, by + 460), 24, 24), paint('#ffffff', a))
        with clip(c, (bx + 40, by + 40, bx + 300, by + 300)):
            vgrad_rect(c, bx + 40, by + 40, 260, 260, '#d8e2ea', '#b8c8d6')
            P.Person(P.KLAUS).draw(c, bx + 170, by + 610, 0.44, t=0, expr='proud', bust=True, idle=0, shadow=False)
        for k in range(4):
            yy = by + 90 + k * 60
            glyphs(c, bx + 340, yy, 420, 20, 970 + k, '#4a4a4a', 1.0, a, 4)
        # número de teléfono resaltado: dígitos como bloques
        hy = by + 380
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx + 40, hy - 45, bx + 800, hy + 25), 12, 12),
                    paint('#ffd84a', 0.5 * a))
        for k in range(11):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx + 70 + k * 64, hy - 32, bx + 108 + k * 64, hy + 12), 6, 6),
                        paint('#2a2733', a))


def big_red(c, t, p=1.0):
    """Cartel rojo de conexión finalizada (solo ícono)."""
    c.drawRect(skia.Rect(0, 0, W, H), paint('#14121a', 1))
    s = ease_out(p)
    w, h = 1300 * s, 640 * s
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(W / 2 - w / 2, H / 2 - h / 2, W / 2 + w / 2, H / 2 + h / 2), 40, 40),
                paint('#d32f2f', 1))
    icon_link(c, W / 2, H / 2, 260 * s, 1.0, '#ffffff', 1)


def dialog(c, t, hover=0.0, pressed=0.0, a=1.0):
    """Diálogo «¿anular conexión?» con íconos: eslabón y signo de interrogación, ✓ y ✗."""
    c.drawRect(skia.Rect(0, 0, W, H), paint('#000000', 0.45 * a))
    bx, by, bw, bh = W / 2 - 520, H / 2 - 300, 1040, 600
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx, by, bx + bw, by + bh), 30, 30), paint('#f4f0ea', a))
    icon_link(c, W / 2, by + 200, 150, 0.4, '#d32f2f', a)
    c.drawArc(skia.Rect(W / 2 + 130, by + 90, W / 2 + 230, by + 190), 180, 250, False, paint('#d32f2f', a, stroke=16))
    c.drawLine(W / 2 + 180, by + 190, W / 2 + 180, by + 225, paint('#d32f2f', a, stroke=16))
    c.drawCircle(W / 2 + 180, by + 258, 10, paint('#d32f2f', a))
    for side, cc in ((-1, '#3aa45a'), (1, '#8a8a8a')):
        x = W / 2 + side * 220
        y = by + 450
        hi = hover if side < 0 else 0
        r = 85 * (1 - pressed * 0.08 if side < 0 else 1)
        c.drawCircle(x, y, r, paint(cc, a))
        if hi:
            c.drawCircle(x, y, r + 14, paint('#ffffff', hi * a, stroke=8))
        if side < 0:
            icon_check(c, x, y, 110, '#ffffff', a)
        else:
            icon_cross(c, x, y, 110, '#ffffff', a)


def cursor(c, x, y, s=1.0, a=1.0):
    p = poly([(x, y), (x, y + 44 * s), (x + 12 * s, y + 33 * s), (x + 22 * s, y + 54 * s), (x + 30 * s, y + 50 * s),
              (x + 20 * s, y + 30 * s), (x + 36 * s, y + 30 * s)])
    c.drawPath(p, paint('#ffffff', a))
    c.drawPath(p, paint('#000000', a, stroke=3 * s))


# ---------------------------------------------------------------- pantallas de teléfono
def avatar(c, x, y, r, color='#6a6a7a', a=1.0):
    c.drawCircle(x, y, r, paint(color, a))
    c.drawCircle(x, y - r * 0.2, r * 0.38, paint('#d8d8e0', a))
    c.drawOval(skia.Rect(x - r * 0.62, y + r * 0.25, x + r * 0.62, y + r * 1.1), paint('#d8d8e0', a))


def call_screen(kind='incoming', seed=0, t=0.0, a=1.0, avatar_fn=None):
    def fn(c, w, h):
        vgrad_rect(c, 0, 0, w, h, '#2a3550', '#141a2a')
        if avatar_fn:
            with clip(c, skia.Path().addCircle(w / 2, h * 0.3, w * 0.28) if False else (w * 0.22, h * 0.16, w * 0.78, h * 0.44)):
                avatar_fn(c, w, h)
        else:
            avatar(c, w / 2, h * 0.3, w * 0.25)
        for k in range(11):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(w * 0.08 + k * w * 0.077, h * 0.52, w * 0.08 + k * w * 0.077 + w * 0.05,
                                                        h * 0.57), 2, 2), paint('#ffffff', 0.85))
        if kind == 'incoming':
            pul = 1 + 0.12 * math.sin(t * 8)
            c.drawCircle(w * 0.27, h * 0.82, w * 0.12 * pul, paint('#3aa45a', 1))
            c.drawCircle(w * 0.73, h * 0.82, w * 0.12, paint('#d32f2f', 1))
        else:
            c.drawCircle(w * 0.5, h * 0.82, w * 0.12, paint('#d32f2f', 1))
            for k in range(5):
                hh = (math.sin(t * 9 + k * 1.3) * 0.5 + 0.5) * h * 0.06 + 4
                c.drawRect(skia.Rect(w * 0.32 + k * w * 0.08, h * 0.66 - hh, w * 0.36 + k * w * 0.08, h * 0.66 + hh),
                           paint('#9ad0ff', 0.8))
    return fn


def chat_screen(bubbles, t=0.0):
    """bubbles: lista de (lado: 1 propio/-1 ajeno, progreso 0..1, semilla)."""
    def fn(c, w, h):
        vgrad_rect(c, 0, 0, w, h, '#f0ece4', '#e4ded2')
        y = h * 0.18
        for side, p, seed in bubbles:
            if p <= 0:
                continue
            bw = w * 0.72
            bx = w - bw - 8 if side > 0 else 8
            bh = 46
            col_ = '#bfe8b8' if side > 0 else '#ffffff'
            s = ease_out(min(1.0, p * 2))
            c.save()
            c.translate(bx + (bw if side > 0 else 0), y)
            c.scale(s, s)
            c.translate(-(bx + (bw if side > 0 else 0)), -y)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx, y, bx + bw, y + bh), 12, 12), paint(col_, 1))
            glyphs(c, bx + 10, y + 16, bw - 20, 9, seed, '#3a3a3a', 1.0, 1.0, 2.2)
            glyphs(c, bx + 10, y + 32, bw * 0.6, 9, seed + 3, '#3a3a3a', 1.0, 1.0, 2.2)
            c.restore()
            y += bh + 14
    return fn


def photo_screen(content):
    def fn(c, w, h):
        c.drawRect(skia.Rect(0, 0, w, h), paint('#101014', 1))
        with clip(c, (0, h * 0.12, w, h * 0.88)):
            c.save()
            c.translate(0, h * 0.12)
            content(c, w, h * 0.76)
            c.restore()
    return fn


# ---------------------------------------------------------------- mapa
_CONT = {
    'sa': [(-80, 9), (-75, 11), (-62, 11), (-52, 5), (-35, -5), (-39, -14), (-41, -22), (-48, -26), (-53, -34), (-58, -38),
           (-65, -41), (-67, -46), (-68, -52), (-72, -54), (-75, -50), (-73, -40), (-71, -30), (-70, -18), (-76, -14),
           (-81, -6), (-80, 0), (-78, 3), (-77, 7)],
    'na': [(-168, 65), (-140, 70), (-110, 72), (-85, 70), (-75, 62), (-62, 58), (-55, 50), (-66, 44), (-70, 41), (-76, 35),
           (-81, 30), (-80, 25), (-83, 29), (-90, 29), (-97, 26), (-97, 20), (-90, 16), (-84, 10), (-80, 8), (-83, 9),
           (-87, 13), (-95, 16), (-105, 20), (-110, 23), (-117, 32), (-124, 40), (-125, 48), (-135, 58), (-150, 60),
           (-165, 60)],
    'eu': [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 54), (8, 57), (5, 62), (12, 66), (20, 70), (30, 70),
           (40, 67), (45, 60), (40, 50), (35, 46), (28, 41), (26, 38), (22, 37), (20, 40), (16, 38), (12, 44), (8, 44),
           (3, 42), (-1, 37)],
    'af': [(-17, 21), (-16, 14), (-12, 8), (-7, 4), (2, 5), (9, 4), (10, -1), (13, -8), (12, -17), (15, -27), (18, -34),
           (25, -34), (32, -28), (35, -20), (40, -15), (40, -5), (43, 0), (51, 12), (43, 12), (38, 18), (33, 28), (32, 31),
           (20, 32), (10, 37), (0, 36), (-6, 35), (-10, 30), (-13, 27)],
    'as': [(28, 41), (36, 36), (35, 32), (43, 13), (52, 17), (57, 25), (66, 25), (72, 20), (77, 8), (80, 15), (88, 22),
           (92, 22), (98, 16), (100, 4), (104, 1), (106, 10), (109, 20), (117, 23), (122, 30), (122, 40), (130, 42), (135, 35),
           (142, 46), (143, 52), (160, 60), (179, 66), (179, 72), (140, 73), (110, 77), (80, 73), (60, 70), (45, 68), (40, 67),
           (45, 60), (40, 50), (35, 46)],
    'au': [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -26), (151, -34), (145, -38),
           (138, -35), (131, -31), (122, -34), (115, -34)],
    'gl': [(-50, 60), (-42, 60), (-20, 70), (-20, 80), (-40, 83), (-60, 78), (-72, 77), (-55, 70)],
    'uk': [(-5, 50), (1, 51), (2, 53), (-2, 56), (-5, 58), (-6, 55), (-3, 54), (-5, 52)],
    'jp': [(130, 31), (135, 34), (140, 36), (142, 40), (141, 43), (145, 44), (141, 45), (139, 40), (136, 36), (131, 34)],
}
PLACES = {'lima': (-77.03, -12.05), 'erfurt': (11.03, 50.98), 'hongkong': (114.17, 22.3)}


def map_xy(lon, lat):
    """Proyección equirectangular sobre un mapa de 3600x1800 (centrado en 0,0)."""
    return (lon * 10.0, -lat * 10.0)


def world_map(c, t):
    """Dibuja el mapa en coordenadas de mundo (usar con cámara)."""
    c.drawRect(skia.Rect(-4000, -3000, 4000, 3000), paint('#cfe0e0', 1))
    for i in range(14):
        y = -900 + i * 140
        line(c, [(-1900, y), (1900, y + 6)], '#b8d0d2', 2, 0.6)
    for k, pts in _CONT.items():
        pp = [map_xy(*p) for p in pts]
        path = blob(pp, 2.0, 1001 + len(k))
        shape(c, path, '#e8d6b0', size=200, shadow_a=0.25, lw=3.0)
    # rosa de los vientos
    with at(c, -1450, 600, 1.0):
        for a in range(4):
            with at(c, 0, 0, 1.0, rot=a * 90):
                c.drawPath(poly([(0, -90), (16, 0), (-16, 0)]), paint('#a07a5a', 0.8))
        c.drawCircle(0, 0, 50, paint('#a07a5a', 0.8, stroke=3))


def map_route(c, t, a_name, b_name, p, color='#d24a6a', icon=True, a=1.0):
    ax, ay = map_xy(*PLACES[a_name])
    bx, by = map_xy(*PLACES[b_name])
    mx, my = (ax + bx) / 2, (ay + by) / 2 - math.hypot(bx - ax, by - ay) * 0.28
    n = 60
    pts = []
    for i in range(int(n * clamp(p)) + 1):
        u = i / n
        x = (1 - u) ** 2 * ax + 2 * (1 - u) * u * mx + u * u * bx
        y = (1 - u) ** 2 * ay + 2 * (1 - u) * u * my + u * u * by
        pts.append((x, y))
    for i in range(0, len(pts) - 1, 2):
        c.drawLine(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], paint(color, a, stroke=7))
    for name, (x, y) in ((a_name, (ax, ay)), (b_name, (bx, by))):
        if name == b_name and p < 0.98:
            continue
        c.drawCircle(x, y, 16, paint(color, a))
        c.drawCircle(x, y, 16, paint(INK, a, stroke=3))
        glow(c, x, y, 50, color, 0.4 * a)
    if icon and 0 < p < 1 and pts:
        from . import rabbit as R
        R.draw(c, pts[-1][0], pts[-1][1] + 20, 0.22, t, shadow=False)


# ---------------------------------------------------------------- montaje
def panel(c, rect, fn, center=(W / 2, H / 2), zoom=1.0, border=True, radius=0):
    """Dibuja fn (en coordenadas 1920x1080) dentro de rect, centrando 'center' y con zoom."""
    x0, y0, w0, h0 = rect
    c.save()
    if radius:
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x0 + w0, y0 + h0), radius, radius))
        c.clipPath(p, skia.ClipOp.kIntersect, True)
    else:
        c.clipRect(skia.Rect(x0, y0, x0 + w0, y0 + h0), skia.ClipOp.kIntersect, True)
    c.translate(x0 + w0 / 2, y0 + h0 / 2)
    c.scale(zoom, zoom)
    c.translate(-center[0], -center[1])
    fn(c)
    c.restore()
    if border:
        if radius:
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x0 + w0, y0 + h0), radius, radius),
                        paint(INK, 0.85, stroke=5))
        else:
            c.drawRect(skia.Rect(x0, y0, x0 + w0, y0 + h0), paint(INK, 0.85, stroke=5))


def split(c, left, right, ratio=0.5, gutter=18, lzoom=1.0, rzoom=1.0, lcenter=None, rcenter=None, bg='#f3e9d8'):
    c.drawRect(skia.Rect(0, 0, W, H), paint(bg, 1))
    lw = W * ratio - gutter * 1.5
    rw = W * (1 - ratio) - gutter * 1.5
    lr = (gutter, gutter, lw, H - 2 * gutter)
    rr = (W * ratio + gutter * 0.5, gutter, rw, H - 2 * gutter)
    panel(c, lr, left, lcenter or (W / 2, H / 2), lzoom)
    panel(c, rr, right, rcenter or (W / 2, H / 2), rzoom)
    return lr, rr


class cam:
    """Cámara: with cam(c, cx, cy, zoom, rot): el punto (cx,cy) del mundo queda en el centro."""

    def __init__(self, c, cx=W / 2, cy=H / 2, zoom=1.0, rot=0.0):
        self.c, self.cx, self.cy, self.z, self.r = c, cx, cy, zoom, rot

    def __enter__(self):
        c = self.c
        c.save()
        c.translate(W / 2, H / 2)
        if self.r:
            c.rotate(self.r)
        c.scale(self.z, self.z)
        c.translate(-self.cx, -self.cy)
        return c

    def __exit__(self, *a):
        self.c.restore()


def wipe(c, p, draw_a, draw_b, angle=12, color='#f3e9d8'):
    """Barrido de página: B entra desde la derecha con un borde de papel y sombra."""
    draw_a(c)
    if p <= 0:
        return
    x = lerp(W + 300, -300, ease_io(p))
    sk = math.tan(math.radians(angle)) * H
    region = poly([(x + sk / 2, 0), (W + 400, 0), (W + 400, H), (x - sk / 2, H)])
    c.save()
    c.clipPath(region, skia.ClipOp.kIntersect, True)
    draw_b(c)
    c.restore()
    edge = [(x + sk / 2, -10), (x - sk / 2, H + 10)]
    c.drawPath(smooth_path(edge, closed=False), paint('#000000', 0.35, stroke=40, blur=18))
    c.drawPath(smooth_path(edge, closed=False), paint(color, 1, stroke=8))


def iris(c, p, draw_a, draw_b, cx=W / 2, cy=H / 2):
    draw_a(c)
    if p <= 0:
        return
    r = ease_io(p) * math.hypot(W, H) * 0.6
    path = skia.Path()
    path.addCircle(cx, cy, max(r, 0.1))
    c.save()
    c.clipPath(path, skia.ClipOp.kIntersect, True)
    draw_b(c)
    c.restore()


def sequence(c, t, shots):
    """Encadena planos dentro de una escena.

    shots: lista de (duración, función(c, tl), (transición, dur)). Transiciones: cut, fade, paper, black, iris.
    """
    starts = []
    acc = 0.0
    for d, fn, tr in shots:
        kind, td = tr if tr else ('cut', 0)
        if starts and kind in ('fade', 'paper', 'iris'):
            acc -= td
        starts.append(acc)
        acc += d
    idx = 0
    for i, s0 in enumerate(starts):
        if t >= s0:
            idx = i
    d, fn, tr = shots[idx]
    kind, td = tr if tr else ('cut', 0)
    tl = t - starts[idx]
    if idx > 0 and kind in ('fade', 'paper', 'iris') and tl < td:
        pfn = shots[idx - 1][1]
        ptl = t - starts[idx - 1]
        p = tl / td
        if kind == 'fade':
            pfn(c, ptl)
            with layer(c, smooth(p)):
                fn(c, tl)
        elif kind == 'paper':
            wipe(c, p, lambda cc: pfn(cc, ptl), lambda cc: fn(cc, tl))
        else:
            iris(c, p, lambda cc: pfn(cc, ptl), lambda cc: fn(cc, tl))
    else:
        fn(c, tl)
    # fundidos a negro
    black = 0.0
    if kind == 'black' and td > 0:
        black = max(black, 1 - smooth(tl / td))
    if idx + 1 < len(shots):
        nk, nd = shots[idx + 1][2] if shots[idx + 1][2] else ('cut', 0)
        if nk == 'black' and nd > 0:
            black = max(black, smooth((tl - (d - nd * 0.6)) / (nd * 0.6)))
    if black > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#0b0a0e', black))
    return idx, tl
