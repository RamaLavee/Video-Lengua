"""S13 — El kentuki del hijo: él también tiene uno; la mujer de las botas y las tortas. «Tener» o «ser»."""
from scenes.common import *

LIMA_WINTER = grade_filter(sat=0.82, bright=0.95, tint=(0.96, 0.99, 1.04))


def phone_in_hand(cc):
    PR.phone(cc, 0, -6, 0.42, rot=-10)


def emi_table(c, t, expr, phone_ear=True, look=(0, 0), sip=0.0):
    """Emilia sentada frente a la mesa de fórmica del comedor (vista frontal)."""
    with U.cam(c, 1260, 470, 1.55):
        L.home_bg(c, t, sky='#c8ccd2')
        s = 0.8
        y = 890
        pose = dict(sit=1, seat_h=300, expr=expr, look=look, eyes=eyes(t, 4), idle=1.0)
        if phone_ear:
            pose.update(hand_L=(98, -650), bend_L=1, handshape_L='hold', hold_L=phone_in_hand)
        else:
            pose.update(hand_L=(60, -470), handshape_L='hold', hold_L=phone_in_hand, nod=0.5)
        cup_y = lerp(-380, -560, sip)
        pose.update(hand_R=(-60, cup_y), handshape_R='hold',
                    hold_R=lambda cc: PR.teacup(cc, 0, 30, 0.6, t, steam=1.0))
        EMI.draw(c, 1260, y, s, view='front', t=t, **pose)
        # la mesa de fórmica por delante
        shape(c, rrect(980, 610, 560, 40, 14, 0.6, 1307), '#9fd3c4', size=40)
        c.drawRect(skia.Rect(982, 640, 1538, 652), paint('#c8ced2', 1))


def son_panel(c, t):
    L.hk_bg(c, t)
    R.generic(c, 1330, 905, 0.9, t, yaw=-0.4)
    for k in range(3):
        PR.cake_box(c, 520, 905 - k * 100, 1.0)
    SON.draw(c, 960, head_at(SON, 1.2, 520), 1.2, view='front', t=t, expr='joy', bust=True,
             talk=talk(t, 0.2, 4.4, 12, 0.55), hand_R=(-96, -745), bend_R=-1, handshape_R='hold',
             hold_R=lambda cc: PR.phone(cc, -6, -20, 0.5, rot=12), hand_L=(170, -600 + math.sin(t * 6) * 30),
             handshape_L='open', look=(0.2, 0))


def boots_photo(c, w, h):
    vgrad_rect(c, 0, 0, w, h, '#d8e2c8', '#b8c8a0')
    c.drawRect(skia.Rect(w * 0.55, h * 0.15, w * 1.1, h * 0.85), paint('#c8a07a', 1))
    c.drawRect(skia.Rect(w * 0.62, h * 0.4, w * 0.8, h * 0.85), paint('#7a4a32', 1))
    c.drawPath(poly([(w * 0.5, h * 0.18), (w * 0.82, -h * 0.05), (w * 1.15, h * 0.18)]), paint('#a85a4a', 1))
    c.drawRect(skia.Rect(0, h * 0.85, w, h), paint('#8aa06a', 1))
    BOOTS.draw(c, w * 0.32, h * 0.95, h * 0.00092, view='front', t=0, expr='proud', idle=0, shadow=False)


def draw(c, t):
    if t < 4.6:
        with layer(c, 1.0, cfilter=LIMA_WINTER):
            emi_table(c, t, 'curious' if t < 2.4 else 'worried', look=(0.4, -0.2))
        U.panel(c, (1060, 60, 800, 500), lambda cc: son_panel(cc, t), center=(960, 600), zoom=0.85, radius=26)
    elif t < 7.4:
        tl = t - 4.6
        # el teléfono en primer plano: la foto de la mujer de las botas
        with layer(c, 1.0, cfilter=LIMA_WINTER):
            with U.cam(c, 1260, 520, 3.0):
                L.home_bg(c, t, sky='#c8ccd2')
            c.drawRect(skia.Rect(0, 0, W, H), paint('#2a2028', 0.35))
        pop = prog(tl, 0.3, 0.8, ease_back)
        PR.phone(c, 960, 560 + (1 - pop) * 200, 3.6, rot=-4,
                 screen=U.photo_screen(boots_photo) if tl > 0.4 else U.chat_screen([(-1, prog(tl, 0, 0.4), 131)]))
        hand = EMI.s['skin']
        hy = 900 + (1 - pop) * 200
        shape(c, blob([(1060, hy + 300), (1050, hy - 40), (1120, hy - 120), (1190, hy - 40), (1200, hy + 300)], 1.0, 1311),
              hand, size=120)
        for k in range(3):
            shape(c, ellipse(740, hy - 120 + k * 70, 34, 26, 0.5, 1312 + k), hand, size=40)
    else:
        tl = t - 7.4
        with layer(c, 1.0, cfilter=LIMA_WINTER):
            emi_table(c, t, 'sad' if tl < 2.2 else 'frown', phone_ear=False, look=(0.0, 0.7), sip=pulse(tl, 2.0, 3.4, 0.4))
