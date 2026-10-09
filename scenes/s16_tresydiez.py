"""S16 — Las tres y diez: Eva la perdonó; la foto de la heladera; Emilia fotografía la pantalla."""
from scenes.common import *


def morning_feed(t):
    """Desde la mesa de la cocina de Eva, a la mañana, sobre el cargador: la heladera con la foto."""
    def feed(c):
        with U.cam(c, kf(t, [(0, 980), (3, 880)]), kf(t, [(0, 470), (3, 420)]), kf(t, [(0, 1.25), (3, 1.9)])):
            E.room_bg(c, t, morning=1.0)
            # almanaque y foto de Eva con su conejita en el centro de la heladera
            shape(c, rrect(800, 200, 140, 170, 4, 0.5, 1601), '#fbf8f1', size=60, shadow=False, lw=2)
            E._dom_icon(c, 870, 320, 0.3)
            PR.photo(c, 870, 520, 170, 128, 1.0, rot=-3, content=PR.photo_eva_rabbit)
            PR.magnet(c, 780, 640, '#e0408a', 12)
            PR.magnet(c, 960, 680, '#5a9ad8', 12)
            PR.bottle(c, 1250, 600, 0.8)
            PR.plate(c, 1500, 598, 0.9)
        glow(c, W * 0.8, 0, 900, '#fff2c8', 0.35)
    return feed


def draw(c, t):
    if t < 3.0:
        with layer(c, 1.0, cfilter=NIGHT):
            if t < 2.1:
                with U.cam(c, 640, 560, 1.3):
                    lamp = prog(t, 1.3, 1.5)
                    L.bedroom_bg(c, t, night=1.0, lamp=lamp)
                    up = prog(t, 0.5, 0.8, ease_out)
                    if up < 0.5:
                        sleeping(c, EMI_N, 860, 640, 0.62, t)
                    else:
                        with clip(c, (-2000, -2000, 4000, 760)):
                            EMI_N.draw(c, 420, 980, 0.62, view='front', t=t, expr='scared', sit=1, seat_h=420, bust=True,
                                       look=(0.3, 0), turn=0.2, hand_L=(150, -330), hand_R=(-150, -330), idle=1.5,
                                       head_rot=math.sin(t * 9) * 2 * (1 - prog(t, 0.8, 1.6)))
                    shape(c, rrect(240, 700, 900, 120, 30, 1.0, 1405), '#9a7ab8', size=120)
                    for k in range(5):
                        line(c, [(320 + k * 160, 720), (300 + k * 160, 810)], shade('#9a7ab8', -0.2), 3, 0.5)
            else:
                with U.cam(c, 140, 610, 6.0):
                    L.bedroom_bg(c, t, night=1.0, lamp=1.0)
    elif t < 5.0:
        tl = t - 3.0
        with layer(c, 1.0, cfilter=NIGHT):
            with U.cam(c, 700, 560, 1.32):
                L.home_bg(c, t)
                PR.charger(c, 560, 885, 150, state='green', t=tl)
                R.draw(c, 560, 872, 0.4, tl, eyes=0.0, clip=None)
                EMI_N.draw(c, kf(tl, [(0, 1100), (2.0, 820)]), 880, 0.75, view='side', flip=True, t=tl,
                           walk=(tl * 0.8) % 1, expr='worried', look=(-0.2, 0.6) if 0.6 < tl < 1.6 else (0.6, 0))
    elif t < 7.2:
        tl = t - 5.0
        with U.cam(c, 1250, 480, 1.45):
            emi_desk(c, tl, who=EMI_N, expr='curious', hl='key', hr='mouse', look=(0.8, -0.1), lean=5, night=1.0,
                     screen=lambda cc: U.pov(cc, tl, morning_feed(0), hud_kw=dict(charging=True, battery=0.6)),
                     clock_hm=(3, 11))
    elif t < 10.2:
        tl = t - 7.2
        U.pov(c, t, morning_feed(tl), hud_kw=dict(charging=True, battery=0.6 + tl * 0.05))
    else:
        tl = t - 10.2
        flash = pulse(tl, 1.15, 1.35, 0.08)
        emi_front(c, tl, who=EMI_N, expr='tender', blush=0.5, night=1.0, screen_col='#fff0c8',
                  hl=(70, -700), hr=(-70, -700), bend_L=1, bend_R=-1, handshape_l='hold', handshape_r='hold',
                  hold_l=lambda cc: PR.phone(cc, -60, -10, 0.6, rot=90, face_down=True))
        if flash > 0:
            c.drawRect(skia.Rect(0, 0, W, H), paint('#ffffff', 0.8 * flash))
