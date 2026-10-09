"""S11 — El robo y el agua: el hombre saca dinero de la billetera de Eva y mete la conejita bajo la canilla."""
from scenes.common import *


def table_feed(t):
    """La conejita sobre la mesa: el hombre (con el torso desnudo) revisa la cartera de Eva."""
    def feed(c):
        E.eva_closeup_bg(c, t)
        s = 1.6
        take = prog(t, 1.3, 2.3)
        hl = (lerp(120, 60, take), lerp(-560, -700, take))
        KLAUS_B.draw(c, 980, head_at(KLAUS_B, s, 300), s, view='front', t=t, expr='frown', look=(0.2, 0.7), nod=0.5,
                     bust=True, hand_L=hl, hand_R=(-130, -540), handshape_L='hold',
                     hold_L=(lambda cc: PR.bills(cc, 0, -10, 0.6, rot=-20)) if take > 0.2 else None)
        c.drawRect(skia.Rect(-100, 860, W + 100, H + 100), paint('#a8784e', 1))
        c.drawRect(skia.Rect(-100, 860, W + 100, 880), paint(shade('#a8784e', 0.2), 1))
        PR.purse(c, 760, 930, 1.3, open_=1.0)
        PR.wallet(c, 1130, 900, 1.2, open_=1.0, bills=1 - take, rot=-6)
    return feed


def spin_feed(t):
    def feed(c):
        E.eva_closeup_bg(c, t)
        x = 960 + math.sin(t * 5) * 500
        s = 2.4
        KLAUS_B.draw(c, x, head_at(KLAUS_B, s, 420), s, view='front', t=t, expr='angry', look=(0, 0.3), bust=True,
                     hand_L=(60, -700), hand_R=(-60, -690), bend_L=1, bend_R=-1, handshape_L='open', handshape_R='open')
    return feed


def sink_feed(t):
    """Bajo la canilla de la cocina de Eva: el chorro cae sobre la lente."""
    def feed(c):
        vgrad_rect(c, -200, -200, W + 400, H + 400, '#cfe2dc', '#a9cbc4')
        for r in range(6):
            for k in range(12):
                c.drawRect(skia.Rect(k * 170 - 60, r * 170 - 120, k * 170 + 104, r * 170 + 44), paint('#e4f0ec', 0.6))
        # pileta de acero
        sink = blob([(-200, 640), (2120, 600), (2120, 1300), (-200, 1300)], 2, 1101)
        shape(c, sink, '#b9c2c8', size=600)
        c.drawOval(skia.Rect(700, 900, 1220, 1060), paint('#8a949c', 1))
        # canilla
        line(c, [(1300, -200), (1300, 120), (1080, 160), (1020, 260)], '#a9b4bc', 60)
        line(c, [(1300, -200), (1300, 120), (1080, 160), (1020, 260)], INK, 3, 0.7)
        flow = prog(t, 0.2, 0.6)
        if flow > 0:
            for k in range(5):
                xo = 1010 + math.sin(t * 20 + k) * 8 + (k - 2) * 14
                line(c, [(xo, 270), (xo + math.sin(t * 14 + k) * 10, 270 + 900 * flow)], '#e8f6ff', 26, 0.55)
            for k in range(14):
                a = rnd(1102, k) * math.pi
                r = (t * 300 + k * 60) % 300
                c.drawCircle(1000 + math.cos(a) * r, 860 - math.sin(a) * r * 0.6, 10, paint('#ffffff', 0.6))
        PR.eggshells(c, 300, 640, 1.2)
    return feed


def draw(c, t):
    if t < 3.4:
        U.pov(c, t, table_feed(t), hud_kw=dict(chirp=pulse(t, 2.4, 3.3, 0.1)))
    elif t < 4.8:
        tl = t - 3.4
        with U.cam(c, 1120, 480, 1.6):
            emi_desk(c, tl, who=EMI_N, expr='angry', hl=hand_preset('key', tl), hr='mouse', look=(0.8, 0.0), night=1.0,
                     lean=4, talk_amt=0.25 + 0.2 * math.sin(tl * 20),
                     screen=lambda cc: U.pov(cc, tl, table_feed(2.6 + tl), hud_kw=dict(chirp=1.0)), clock_hm=(9, 42))
    elif t < 6.6:
        tl = t - 4.8
        U.pov(c, t, spin_feed(tl), tilt=math.sin(tl * 6) * 25, shake=0.8, zoom=1.0 + 0.2 * tl,
              hud_kw=dict(chirp=1.0, pressed=['left', 'right'][int(tl * 4) % 2]))
    elif t < 9.4:
        tl = t - 6.6
        U.pov(c, t, sink_feed(tl), tilt=kf(tl, [(0, -20), (0.5, -8)]) + math.sin(tl * 9) * 3, shake=0.4,
              wet=prog(tl, 0.5, 1.5), hud_kw=dict(chirp=pulse(tl, 0.6, 2.6, 0.2)))
    else:
        tl = t - 9.4
        with U.cam(c, 1120, 480, 1.6):
            emi_desk(c, tl, who=EMI_N, expr='scared', hl='face', hr='face', look=(0.8, 0.0), lean=-6, night=1.0,
                     handshape_l='open', handshape_r='open',
                     screen=lambda cc: U.pov(cc, tl, sink_feed(2.8 + tl), wet=1.0, hud_kw=dict()), clock_hm=(9, 43))
