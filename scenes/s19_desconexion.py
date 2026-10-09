"""S19 — Conexión finalizada: Emilia apaga la pantalla, busca el botón rojo y anula la conexión."""
from scenes.common import *


def pull_feed(t):
    """Klaus se ríe y levanta a Eva del piso (se corta antes de cualquier desnudez)."""
    def feed(c):
        with U.cam(c, 1250, 560, 1.0):
            E.pov_bg(c, t, mess=0.5)
        up = prog(t, 0.3, 1.0)
        EVA.draw(c, 1000, 1000 + 300 * (1 - up), 0.76, view='front', t=t, expr='laugh', turn=0.4, look=(0.6, -0.2),
                 hand_L=(220, -760), bend_L=1, handshape_L='open')
        KLAUS_U.draw(c, 1300, 1010, 0.8, view='front', t=t, expr='laugh', turn=-0.4, look=(-0.6, 0.2),
                     hand_R=(-260, -640 + 120 * (1 - up)), handshape_R='hold')
    return feed


def arm(c, x, y, ang=-10, color=None):
    """Antebrazo y mano de Emilia que entra por la izquierda del encuadre."""
    color = color or P.EMILIA['top']
    path = P.taper([(x - 900, y + 260), (x - 400, y + 120), (x - 40, y + 10)], 150, 110, 130)
    shape(c, path, color, size=150)
    shape(c, ellipse(x, y, 60, 64, 0.5, 1901), P.EMILIA['skin'], size=100)


def monitor_close(c, t, screen, on=1.0, hand=None, red_glow=0.0):
    x, y, w = L.MON
    with U.cam(c, x + w / 2, y + w * 0.3, 3.3):
        L.hall_bg(c, clock_hm=(2, 11))
        L.desk_back(c, t, screen_fn=screen, on=on, glow_a=0.6)
        L.desk_front(c, t)
        if red_glow > 0:
            glow(c, x + w / 2, y + w * 0.28, 600, '#ff4a4a', 0.35 * red_glow)
    if hand:
        arm(c, *hand)


def draw(c, t):
    if t < 1.4:
        U.pov(c, t, pull_feed(t), hud_kw=dict())
    elif t < 2.8:
        tl = t - 1.4
        off = prog(tl, 0.35, 0.45)
        monitor_close(c, tl, lambda cc: U.pov(cc, 1.4 + tl, pull_feed(1.4 + tl), hud_kw=dict()), on=1 - off,
                      hand=(lerp(400, 1500, prog(tl, 0, 0.35)), lerp(1300, 1010, prog(tl, 0, 0.35))) if tl < 1.0 else None)
    elif t < 6.6:
        tl = t - 2.8
        on = prog(tl, 0.35, 0.45)
        cur = (kf(tl, [(0.6, 900), (1.5, 1800), (2.6, 1800), (3.2, 740)]), kf(tl, [(0.6, 700), (1.5, 1000), (2.6, 1000),
                                                                                  (3.2, 820)]))

        def scr(cc):
            dlg = prog(tl, 1.75, 2.0)
            red = prog(tl, 3.35, 3.6)
            if red > 0:
                U.big_red(cc, tl, red)
                return
            with layer(cc, 1.0, cfilter=grade_filter(sat=0.4, bright=0.6)):
                U.pov(cc, tl, lambda c2: (c2.clear(col('#3a3440')), glow(c2, 900, 600, 500, '#c8a0a0', 0.5)),
                      hud_kw=dict(red_hi=pulse(tl, 1.2, 1.9, 0.15)))
            if dlg > 0:
                U.dialog(cc, tl, hover=prog(tl, 3.0, 3.2), pressed=pulse(tl, 3.2, 3.35, 0.05), a=dlg)
            U.cursor(cc, cur[0], cur[1], 2.2)
        monitor_close(c, tl, scr, on=on, hand=(400, 1010) if tl < 0.5 else None, red_glow=prog(tl, 3.35, 3.6))
    elif t < 8.4:
        tl = t - 6.6
        emi_front(c, tl, expr='blank', red=1.0, screen_light=0.6, screen_col='#ff5a4a', look=(0, 0), idle=0.2,
                  face=dict(brow=(0.6, 0.6), squint=-0.2), hl=(150, -470), hr=(-150, -470), handshape_l='fist',
                  handshape_r='fist', eyes_closed=0.0)
    else:
        tl = t - 8.4
        creak = pulse(tl, 0.2, 1.4, 0.2)
        with U.cam(c, 1180, 520, 1.6):
            L.hall_bg(c, clock_hm=(2, 12))
            L.desk_back(c, tl, screen_fn=lambda cc: U.big_red(cc, 0, 1.0), glow_a=0.0)
            glow(c, 1485, 420, 700, '#ff4a4a', 0.35)
            PR.wicker_chair(c, CHAIR_X, 880, CHAIR_S, back_only=True, creak=creak)
            PR.wicker_chair(c, CHAIR_X, 880, CHAIR_S, seat_only=True, creak=creak)
            EMI.draw(c, 860, 880, 0.7, view='side', t=tl, expr='blank', look=(0.8, -0.2), lean=8,
                     hand_L=loc_local(985 - 20 + math.sin(tl * 40) * 2 * creak, 650), hand_R=loc_local(985 - 30, 680),
                     handshape_L='fist', handshape_R='fist', face=dict(brow=(0.5, 0.7)))
            L.desk_front(c, tl)
            PR.teacup(c, 1440, 632, 0.72, tl, steam=0.0, spill=1.0)


def loc_local(xw, yw):
    return ((xw - 860) / 0.7, (yw - 880) / 0.7)
