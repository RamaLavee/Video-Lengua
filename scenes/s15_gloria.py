"""S15 — El regalo de Gloria: una conejita usada, idéntica a la que Emilia es en Erfurt."""
from scenes.common import *


def draw(c, t):
    if t < 1.0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#0b0a0e', 1))
        return
    tl = t - 1.0
    with layer(c, 1.0, cfilter=WARM):
        if tl < 3.4:
            # Gloria entra con la caja envuelta
            with U.cam(c, 700, 500, 1.35):
                L.home_bg(c, t)
                door_open = prog(tl, 0.0, 0.6)
                gx = kf(tl, [(0, 300), (2.4, 700)])
                GLORIA.draw(c, gx, 880, 0.78, view='side', t=tl, walk=(tl * 0.9) % 1 if tl < 2.4 else None,
                            expr='joy', hand_L=(200, -520), hand_R=(170, -540), handshape_L='hold', handshape_R='hold',
                            hold_L=lambda cc: PR.wrapped_box(cc, -10, -150, 150, 120, 1.0, dirty=0.6))
                PR.door(c, 120, 200, 300, 680, color='#7a4a32', open_=door_open * (1 - prog(tl, 2.6, 3.2)))
                EMI.draw(c, 1000, 880, 0.75, view='front', t=tl, expr='surprise' if tl < 1.4 else 'curious',
                         turn=-0.5, look=(-0.7, 0), hand_L=(150, -420), hand_R=(-150, -420))
        elif tl < 6.4:
            # en la mesa de fórmica: la conejita envuelta en un repasador, con los ojos cerrados
            t2 = tl - 3.4
            with U.cam(c, 1260, 520, 1.6):
                L.home_bg(c, t)
                unwrap = prog(t2, 0.3, 1.4)
                GLORIA.draw(c, 1080, 880, 0.78, view='front', t=t2, expr='joy' if t2 > 1.6 else 'happy', turn=0.4,
                            look=(0.6, 0.4), hand_L=(180, -500) if t2 < 1.6 else (60 + abs(math.sin(t2 * 9)) * 40, -560),
                            hand_R=(-60, -500) if t2 < 1.6 else (-60 - abs(math.sin(t2 * 9)) * 40, -560),
                            handshape_L='open', handshape_R='open', bend_L=1 if t2 > 1.6 else -1,
                            bend_R=-1 if t2 > 1.6 else 1)
                EMI.draw(c, 1460, 880, 0.75, view='front', t=t2, expr='worried' if t2 < 1.8 else 'tender',
                         turn=-0.45, look=(-0.6, 0.5), nod=0.3, hand_L=(150, -420), hand_R=(-150, -420),
                         blush=0.4 if t2 > 1.8 else 0)
                shape(c, rrect(980, 610, 560, 40, 14, 0.6, 1307), '#9fd3c4', size=40)
                c.drawRect(skia.Rect(982, 640, 1538, 652), paint('#c8ced2', 1))
                PR.dish_towel(c, 1260, 612, 0.5, open_=unwrap)
                R.draw(c, 1260, 600, 0.48 * (0.6 + 0.4 * unwrap), t2, eyes=0.0, clip=None, shadow=False)
                if unwrap < 0.9:
                    with layer(c, 1 - unwrap):
                        PR.dish_towel(c, 1260, 580, 0.5, open_=0.0)
        else:
            # Gloria enchufa el cargador junto a la puerta; la conejita duerme ahí
            t3 = tl - 6.4
            with U.cam(c, 640 - t3 * 15, 560 + t3 * 12, 1.32 + t3 * 0.08):
                L.home_bg(c, t)
                PR.charger(c, 560, 885, 150, state='green' if t3 > 1.0 else None, t=t3)
                R.draw(c, 560, 872, 0.4, t3, eyes=0.0, clip=None)
                gx = kf(t3, [(0, 760), (1.2, 760), (2.4, 860)])
                GLORIA.draw(c, gx, 880, 0.78, view='side', flip=True, t=t3, expr='happy', look=(0.6, 0.6),
                            lean=kf(t3, [(0, -10), (1.2, -10), (1.8, 0)]),
                            hand_L=(180, -300) if t3 < 1.2 else (120, -420), handshape_L='hold')
                if t3 > 1.6:
                    EMI.draw(c, kf(t3, [(1.6, 1250), (2.6, 1080)]), 880, 0.75, view='side', flip=True, t=t3,
                             walk=(t3 * 0.8) % 1, expr='tender', look=(0.6, 0.5))
