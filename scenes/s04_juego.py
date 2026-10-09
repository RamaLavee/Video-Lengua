"""S04 — Cerrar los ojos: el juego de dormir/despertar y el dedo que toca la nariz (pantalla dividida)."""
from scenes.common import *
from scenes.s03_conexion import eva_close, erfurt_kitchen


def manual(c):
    shape(c, rrect(-60, -80, 120, 150, 6, 0.4, 3001), '#f6f2e8', size=60)
    c.drawRect(skia.Rect(-60, -80, 60, -40), paint('#f29ab4', 1))
    for k in range(4):
        line(c, [(-40, -20 + k * 22), (40, -20 + k * 22)], '#9a9a9a', 3)


def finger(c, t, p):  # noqa: E302
    """Dedo índice de Eva acercándose a la lente."""
    if p <= 0:
        return
    x = lerp(2100, 1050, ease_out(p))
    y = lerp(1300, 620, ease_out(p))
    s = lerp(1.0, 2.6, p)
    with at(c, x, y, s, rot=-35):
        sk = P.EVA['skin']
        shape(c, rrect(-34, -20, 68, 300, 34, 0.6, 3002), sk, size=60)
        shape(c, ellipse(0, -10, 34, 40, 0.6, 3003), sk, size=60)
        c.drawOval(skia.Rect(-20, -40, 20, 0), paint('#f6d8c8', 1))
        c.drawOval(skia.Rect(-20, -40, 20, 0), paint(INK, 0.6, stroke=2))


def draw(c, t):
    dark = prog(t, 5.15, 5.4, smooth) * (1 - prog(t, 6.6, 6.9, smooth))
    eye_state = 1 - dark
    pressed = 'eye' if (5.0 < t < 5.35 or 6.45 < t < 6.75) else ('up' if 8.5 < t < 9.2 else ('down' if 9.5 < t < 10.1 else None))
    zoom = 1.0 + 0.16 * prog(t, 8.6, 9.2) - 0.2 * prog(t, 9.6, 10.2)
    fp = prog(t, 7.6, 8.8, ease_out) * (1 - prog(t, 9.6, 10.2))
    # --- Lima (izquierda)
    if t < 3.4:
        e_expr, closed = 'curious', None
    elif t < 5.0:
        e_expr, closed = 'calm', prog(t, 3.5, 3.8)
    elif t < 7.5:
        e_expr, closed = 'curious', None
    elif t < 10.2:
        e_expr, closed = 'happy', None
    else:
        e_expr, closed = 'joy', None
    hl = (165, -455)
    hr = (-165, -455)
    if 4.9 < t < 5.5 or 6.3 < t < 6.9:
        hr = (-110, -470)
    if 8.3 < t < 10.3:
        hl = (205, -468 + (6 if pressed in ('up', 'down') else 0))

    def left(cc):
        emi_front(cc, t, expr=e_expr, eyes_closed=closed, hl=hl, hr=hr, handshape_l='fist', handshape_r='fist',
                  look=(0.25, 0.0), turn=0.15, blush=0.3 if t > 10 else 0.0)

    # --- Erfurt (derecha)
    if t < 2.6:
        ev = dict(expr='curious', hl=(60, -700), hr=(-40, -700), hold_l=manual, hs_l='hold', hs_r='hold', look=(0.2, 0.6),
                  nod=0.4)
    elif t < 4.2:
        cover = prog(t, 3.3, 3.7)
        ev = dict(expr='talk' if t < 3.6 else 'closed', talk_amt=talk(t, 2.6, 3.5),
                  hl=(lerp(130, 48, cover), lerp(-640, -870, cover)), hr=(lerp(-130, -48, cover), lerp(-640, -870, cover)),
                  hs_l='open', hs_r='open', look=(0, 0), bend_L=1, bend_R=-1)
    elif t < 6.6:
        ev = dict(expr='curious', look=(0, 0))
    elif t < 7.6:
        clap = abs(math.sin((t - 6.6) * 9))
        ev = dict(expr='joy', hl=(30 + clap * 60, -560), hr=(-30 - clap * 60, -560), hs_l='open', hs_r='open')
    else:
        ev = dict(expr='laugh' if t > 9.2 else 'happy', talk_amt=talk(t, 8.0, 9.0) * 0.6)

    def feed(cc):
        with U.cam(cc, 1650, 470, 1.0):
            E.pov_bg(cc, t)
        eva_close(cc, t, 1060, 2250, 2.45, **ev)
        finger(cc, t, fp)

    c.drawRect(skia.Rect(0, 0, W, H), paint('#f3e9d8', 1))
    g = 18
    lr = (g, g, W * 0.5 - g * 1.5, H - 2 * g)
    rr = (W * 0.5 + g * 0.5, g, W * 0.5 - g * 1.5, H - 2 * g)
    U.panel(c, lr, left, center=(960, 560), zoom=1.0)
    k = rr[2] / W
    rh = H * k
    rect = (rr[0], (H - rh) / 2, rr[2], rh)
    c.drawRect(skia.Rect(rr[0], rr[1], rr[0] + rr[2], rr[1] + rr[3]), paint('#1d1a22', 1))
    U.pov(c, t, feed, rect=rect, zoom=zoom, dark=dark, hud_kw=dict(pressed=pressed, eye=eye_state))
    U.subtitle(c, t, 2.7, 1.5, seed=41, rect=rect)
    U.subtitle(c, t, 8.0, 1.6, seed=43, rect=rect)
    c.drawRect(skia.Rect(rr[0], rr[1], rr[0] + rr[2], rr[1] + rr[3]), paint(INK, 0.85, stroke=5))
    # pequeños rótulos visuales de lugar: punto cálido / frío en las esquinas
    c.drawCircle(lr[0] + 34, lr[1] + 34, 10, paint('#e8a04a', 0.9))
    c.drawCircle(rr[0] + rr[2] - 34, rr[1] + 34, 10, paint('#7ab8e0', 0.9))
