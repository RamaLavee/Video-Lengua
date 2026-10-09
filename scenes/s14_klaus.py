"""S14 — Klaus Berger: la camiseta n.º 4, la búsqueda, el mensaje, la llamada, el espejo y la bañera."""
from scenes.common import *


def cucha_feed(t, klaus=True, mirror=False, eva=None, bag=True):
    """Vista horizontal desde la cucha (la cámara a ras del piso)."""
    def feed(c):
        cx = 3280 if mirror else 2780
        with U.cam(c, cx, 560, 1.0):
            E.pov_bg(c, t, bag=bag)
            if klaus:
                KLAUS.draw(c, 2640, 790, 0.7, view='side', t=t, sit=1, seat_h=440, knee_x=210, expr='neutral',
                           look=(0.8, 0), hand_L=(160, -470), handshape_L='hold',
                           hold_L=lambda cc: PR.bottle(cc, 0, 20, 0.6))
                E.SOFA  # el sofá ya está en el fondo
                glow(c, 3340, 410, 300, '#9ad0ff', 0.3 * (0.8 + 0.2 * math.sin(t * 7)))
            if mirror:
                # garabato rojo agresivo escrito con lápiz labial a la altura de un kentuki (ilegible)
                pts = []
                for i in range(22):
                    x = 3640 + i * 8.5
                    y = 660 + math.sin(i * 1.7) * 30 + (i % 4 == 0) * -40
                    pts.append((x, y))
                line(c, pts, '#d1242f', 9, 0.95, smooth=False)
                line(c, [(3650, 700), (3700, 610), (3740, 700), (3790, 600)], '#d1242f', 9, 0.95, smooth=False)
                PR.lipstick(c, 3560, 900, 1.2, rot=-75, broken=True)
            if eva is not None:
                eva(c)
    return feed


def browser(t, contact=0.0):
    def fn(c):
        U.browser_screen(c, t, scroll=0.0, highlight=prog(t, 0.6, 1.0), contact=contact)
    return fn


def phone_closeup(c, t, screen, face_down=False, vib=0.0, under=None):
    with layer(c, 1.0, cfilter=WARM):
        with U.cam(c, 1200, 600, 2.6):
            L.hall_bg(c)
            L.desk_back(c, t, screen_fn=browser(t, 1.0))
            L.desk_front(c, t)
    c.drawRect(skia.Rect(0, 0, W, H), paint('#2a2028', 0.3))
    PR.phone(c, 960 + t * 10, 560 - t * 6, 3.6 * (1 + t * 0.05), rot=-4 - t * 0.7, screen=screen, face_down=face_down,
             vibrate=vib, t=t)


def bath_feed(t):
    def feed(c):
        E.bathtub_pov(c, t)
        s = 2.2
        wag = math.sin(t * 9) * 40 * pulse(t, 0.3, 1.3, 0.1)
        EVA.draw(c, 960, head_at(EVA, s, 230), s, view='front', t=t, expr='angry', bust=True, look=(0, 0.6), nod=0.5,
                 talk=talk(t, 0.3, 1.3), hand_L=(180 + wag, -760), handshape_L='point', bend_L=1)
    return feed


def eva_angry_feed(t):
    def feed(c):
        with U.cam(c, 3280, 560, 1.0):
            E.pov_bg(c, t, bag=False)
        s = 1.5
        EVA.draw(c, 1250 - 200 * prog(t, 0, 1.2), head_at(EVA, s, 330), s, view='front', t=t,
                 expr='surprise' if t < 0.8 else 'angry', look=(-0.6, 0.6) if t < 0.8 else (0, 0.7), nod=0.4,
                 hand_L=(150, -560), handshape_L='hold', hold_L=lambda cc: PR.lipstick(cc, 0, 0, 0.8, rot=30, broken=True))
    return feed


def draw(c, t):
    if t < 2.4:
        U.pov(c, t, cucha_feed(t), zoom=kf(t, [(0, 1.0), (2.4, 1.12)]), center=(980, 470), hud_kw=dict())
    elif t < 4.6:
        tl = t - 2.4
        with U.cam(c, kf(tl, [(0, 1200), (2.2, 1350)]), 470, kf(tl, [(0, 1.4), (2.2, 1.6)])):
            emi_desk(c, tl, expr='curious' if tl < 1.4 else 'frown', hl='type', hr='mouse', look=(0.8, -0.1), lean=7,
                     screen=browser(tl), handshape_l='point', clock_hm=(4, 20))
    elif t < 6.4:
        tl = t - 4.6
        x, y, w = L.MON
        with U.cam(c, x + w / 2, y + w * 9 / 32, 1920.0 / w * 0.98):
            emi_desk(c, tl, expr='frown', screen=browser(1.0 + tl, prog(tl, 0.1, 0.5)), clock_hm=(4, 21))
    elif t < 8.6:
        tl = t - 6.4
        phone_closeup(c, tl, U.chat_screen([(1, prog(tl, 0.2, 1.4), 141)]))
    elif t < 9.6:
        tl = t - 8.6
        emi_front(c, tl, expr='shock', hl=(30, -720), hr=(-160, -470), bend_L=1, handshape_l='open', handshape_r='fist')
    elif t < 11.4:
        tl = t - 9.6
        if tl < 0.9:
            phone_closeup(c, tl, U.chat_screen([(1, 1.0, 141), (-1, prog(tl, 0.0, 0.4), 143)]))
        else:
            phone_closeup(c, tl, U.call_screen('incoming', 7, tl), vib=1.0 if tl < 1.5 else 0.0, face_down=tl > 1.5)
    elif t < 13.6:
        tl = t - 11.4
        U.pov(c, t, cucha_feed(t, klaus=False, mirror=True, bag=False), zoom=kf(tl, [(0, 1.0), (2.2, 1.35)]),
              center=(1100, 640), hud_kw=dict())
    elif t < 16.4:
        tl = t - 13.6
        if tl < 1.4:
            U.pov(c, t, eva_angry_feed(tl), hud_kw=dict())
        else:
            U.pov(c, t, bath_feed(tl - 1.4), tilt=kf(tl, [(1.4, -12), (1.9, 0)]), hud_kw=dict())
    else:
        tl = t - 16.4
        off = prog(tl, 0.5, 0.6)
        U.pov(c, t, bath_feed(1.4 + tl), dark=off, hud_kw=dict(eye=1.0))
