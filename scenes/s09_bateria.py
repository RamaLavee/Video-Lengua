"""S09 — La batería: el hijo explica la «caducidad programada»; Eva la carga cada noche."""
from scenes.common import *


def phone_in_hand(cc):
    PR.phone(cc, 0, -6, 0.42, rot=-10)


def son_panel(c, t, expr='worried'):
    L.hk_bg(c, t)
    SON.draw(c, 960, 1640, 1.25, view='front', t=t, expr=expr, bust=True, talk=talk(t, 0.2, 4.4, 12, 0.5),
             hand_R=(-96, -745), handshape_R='hold', hold_R=lambda cc: PR.phone(cc, -6, -20, 0.5, rot=12), bend_R=-1,
             hand_L=(140, -560 + math.sin(t * 5) * 30), handshape_L='open', look=(0.2, 0))


def battery_icon(c, t, x, y, p):
    """Ícono grande de batería que se vacía (sin texto)."""
    with at(c, x, y, 1.0):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-120, -60, 120, 60), 18, 18), paint('#fbf8f1', 0.95))
        U.icon_battery(c, -90, -40, 170, 1 - p, '#3e2b2a', 1.0)
        if p > 0.8:
            a = 0.5 + 0.5 * math.sin(t * 10)
            c.drawCircle(105, -50, 16, paint('#d32f2f', a))


def market(c, t, phase):
    with layer(c, 1.0, cfilter=WARM):
        with U.cam(c, 1060, 560, 1.18):
            L.super_bg(c, t)
            PR.cart(c, 700, 950, 1.0)
            if phase == 0:
                EMI.draw(c, 1000, 940, 0.78, view='front', t=t, expr='worried' if t > 1.2 else 'curious',
                         hand_L=(98, -650), handshape_L='hold', hold_L=phone_in_hand, bend_L=1, hand_R=(-200, -440),
                         look=(0.3, -0.1), talk=talk(t, 2.6, 3.4, 12, 0.4))
                L.peaches_and_cans(c, t, 0.0)
            else:
                sw = prog(t, 1.0, 2.2)
                EMI.draw(c, 1000, 940, 0.78, view='front', t=t, expr='tender', turn=0.35, look=(0.6, 0.5),
                         hand_L=(lerp(200, 450, sw), lerp(-420, -260, sw)), handshape_L='hold',
                         hand_R=(-200, -440), blush=0.4)
                L.peaches_and_cans(c, t, sw)


def call(c, t):
    market(c, t, 0)
    # recuadro de Hong Kong
    rect = (1120, 60, 740, 470)
    U.panel(c, rect, lambda cc: son_panel(cc, t), center=(960, 560), zoom=0.9, radius=26)
    label(c, t, 'Hong Kong', 0.6, 3.6, x=1150, y=500, size=40)
    battery_icon(c, t, 560, 200, prog(t, 1.2, 4.2))


def night(c, t):
    def left(cc):
        with layer(cc, 1.0, cfilter=NIGHT):
            with U.cam(cc, 700, 600, 1.15):
                L.bedroom_bg(cc, t, night=1.0)
                sleeping(cc, EMI_N, 860, 640, 0.62, t)
                shape(cc, rrect(240, 690, 900, 130, 30, 1.0, 1405), '#9a7ab8', size=120)
                for k in range(5):
                    line(cc, [(320 + k * 160, 710), (300 + k * 160, 810)], shade('#9a7ab8', -0.2), 3, 0.5)
    st = 'red' if t < 1.0 else ('yellow' if t < 2.4 else 'green')

    def right(cc):
        with layer(cc, 1.0, cfilter=NIGHT):
            with U.cam(cc, 2440, 600, 1.25):
                E.room_bg(cc, t, night=1.0)
                PR.charger(cc, 2350, 912, 170, state=st, t=t)
                ry = kf(t, [(0, 640), (0.8, 900)])
                R.draw(cc, 2350, ry, 0.6, t, eyes=0.0, shadow=t > 0.8)
                EVA.draw(cc, 2560, 905, 0.74, view='front', t=t, expr='tender', look=(-0.5, 0.6), nod=0.3,
                         hand_L=((2350 - 2560) / 0.74 + 85, (ry - 80 - 905) / 0.74),
                         hand_R=((2350 - 2560) / 0.74 - 85, (ry - 80 - 905) / 0.74), bend_L=-1, bend_R=1)
    U.split(c, left, right)


def smile(c, t):
    market(c, t, 1)


def draw(c, t):
    U.sequence(c, t, [
        (4.9, call, None),
        (3.4, night, ('fade', 0.6)),
        (3.9, smile, ('fade', 0.6)),
    ])
