"""S06 — La ventana: la cucha fucsia, Eva la alza y aparece Erfurt al atardecer."""
from scenes.common import *


def window_frame(c, t):
    """Marco de la ventana y cortinas por delante del panorama (vista alzada)."""
    sway = noise1(t * 0.5, 61) * 10
    c.drawRect(skia.Rect(-200, -200, W + 200, 40), paint('#f4f2ee', 1))
    c.drawRect(skia.Rect(-200, H - 60, W + 200, H + 200), paint('#f4f2ee', 1))
    c.drawRect(skia.Rect(940, -200, 980, H + 200), paint('#f4f2ee', 1))
    for x in (-200, W - 120):
        c.drawRect(skia.Rect(x, -200, x + 320, H + 200), paint('#f4f2ee', 1))
    for side, x in ((-1, 150), (1, W - 150)):
        cp = blob([(x - 160, -100), (x + 160, -100), (x + 120 + sway * side, H * 0.5), (x + 170 + sway * side, H + 100),
                   (x - 170, H + 100)], 2.0, 611 + side)
        shape(c, cp, '#d8b8e0', size=200)
    c.drawRect(skia.Rect(-200, 30, W + 200, 46), paint(INK, 0.5))


def draw(c, t):
    if t < 3.0:
        # A: la conejita despierta en su cucha y Eva la levanta
        with layer(c, 1.0, cfilter=COOL):
            with U.cam(c, kf(t, [(0, 2420), (3, 2500)]), kf(t, [(0, 690), (3, 560)]), kf(t, [(0, 1.45), (3, 1.22)])):
                E.room_bg(c, t, morning=1.0)
                PR.cucha(c, 2380, 912, front=False)
                ry = kf(t, [(0, 896), (1.1, 896), (2.2, 640), (3.0, 470)])
                rx = kf(t, [(0, 2380), (1.1, 2380), (2.2, 2575)])
                in_cucha = t < 1.15
                if in_cucha:
                    R.draw(c, rx, ry, 0.62, t, eyes=prog(t, 0.2, 0.7), yaw=0.0)
                    PR.cucha(c, 2380, 912, back=False)
                reach = prog(t, 0.7, 1.15)
                hl = (lerp(150, (rx - 2600) / 0.74 + 95, reach), lerp(-420, (ry - 80 - 905) / 0.74, reach))
                hr = (lerp(-150, (rx - 2600) / 0.74 - 95, reach), lerp(-420, (ry - 80 - 905) / 0.74, reach))
                EVA.draw(c, 2600, 905, 0.74, view='front', t=t, expr='happy', look=(-0.3, 0.5) if t < 2 else (0, 0),
                         nod=0.2, hand_L=hl, hand_R=hr, handshape_L='open', handshape_R='open', bend_L=-1, bend_R=1)
                if not in_cucha:
                    R.draw(c, rx, ry, 0.62, t, eyes=1.0, yaw=kf(t, [(1.1, 0), (2.2, -0.3)]), shadow=False,
                           ears=0.4 * prog(t, 1.1, 2.2))
                    hands_over(c, EVA, 0.74)
                    PR.cucha(c, 2380, 912, back=False)
    elif t < 8.0:
        # B: vista alzada: la ciudad al atardecer
        tl = t - 3.0
        bob = math.sin(tl * 1.6) * 10

        def feed(cc):
            with U.cam(cc, kf(tl, [(0, 900), (5, 1250)]), kf(tl, [(0, 900), (1.2, 760), (5, 720)]) + bob,
                       kf(tl, [(0, 1.0), (5, 1.08)])):
                E.erfurt_panorama(cc, t)
            with layer(cc, 1 - prog(tl, 0.0, 0.8) * 0.0):
                window_frame(cc, t)
        U.pov(c, t, feed, tilt=math.sin(tl * 1.3) * 1.5, hud_kw=dict())
        label(c, t, 'Erfurt, Alemania', 3.8, 3.8, x=180, y=900)
    elif t < 10.0:
        # C: Emilia, iluminada de rojo, maravillada
        tl = t - 8.0
        emi_front(c, tl, expr='surprise' if tl < 1.1 else 'tender', screen_col='#ff9a6a', screen_light=1.6,
                  look=(0, -0.1), lean=kf(tl, [(0, 0), (1.5, -4)]), hl=(150, -470), hr=(-150, -470),
                  handshape_l='fist', handshape_r='fist')
        c.drawRect(skia.Rect(0, 0, W, H), paint('#ff7a4a', 0.12, blend=skia.BlendMode.kMultiply))
    else:
        # D: de vuelta en el piso, Emilia mueve la conejita: ¡que la alcen otra vez!
        tl = t - 10.0
        with layer(c, 1.0, cfilter=COOL):
            with U.cam(c, 2450, 620, 1.3):
                E.room_bg(c, t, sunset=0.7)
                wig = math.sin(tl * 9) * 60 * pulse(tl, 0.2, 2.0, 0.2)
                R.draw(c, 2350 + wig, 905, 0.62, tl, yaw=math.sin(tl * 11) * 0.8, ears=math.sin(tl * 10),
                       chirp=pulse(tl, 0.9, 1.3, 0.1) * 0.6)
                ex = kf(tl, [(0, 2620), (2.0, 2420)])
                EVA.draw(c, ex - 180 * prog(tl, 0.8, 2.0), 905, 0.74, view='side', flip=True, t=tl,
                         walk=(tl * 0.9) % 1 if tl > 0.8 else None, expr='laugh', look=(0.6, 0.3))
