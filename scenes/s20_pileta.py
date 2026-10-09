"""S20 — La pileta: la conejita de Lima la mira «como juzgándola»; Emilia la ahoga bajo el chorro de agua
hasta que la luz verde de la base deja de titilar. (Se muestra con pudor: de espaldas, el agua, la luz.)"""
from scenes.common import *

COLD_LIMA = grade_filter(sat=0.6, bright=0.92, tint=(0.93, 0.98, 1.08))


def green_light(t, t_off):
    """Titileo de la luz verde que se va apagando."""
    if t >= t_off:
        return 0.0
    rate = lerp(3.0, 1.0, clamp(t / t_off))
    v = 0.5 + 0.5 * math.sin(t * rate * 2 * math.pi)
    return v * (1 - 0.6 * clamp(t / t_off))


def stare(c, t):
    """Vista de Emilia: la conejita en la otra punta del escritorio, mirándola fijo."""
    with layer(c, 1.0, cfilter=COLD_LIMA):
        z = kf(t, [(0, 1.8), (3.0, 3.6)], ease_in)
        with U.cam(c, 1640, kf(t, [(0, 540), (3.0, 500)]), z):
            L.hall_bg(c, clock_hm=(2, 13))
            L.desk_back(c, t, screen_fn=lambda cc: U.big_red(cc, 0, 1.0), glow_a=0.0)
            L.desk_front(c, t)
            R.draw(c, 1640, 640, 0.3, t, yaw=-0.2, look=(-0.3, -0.2), clip='gold', ears=0.0)


def face(c, t):
    with layer(c, 1.0, cfilter=COLD_LIMA):
        emi_front(c, t, expr='blank' if t < 0.8 else 'cold', emix=('cold', 'angry', prog(t, 0.8, 1.4)) and None,
                  face=dict(brow=(-0.3, -0.9), mouth=(0.8, -0.35, 0.0, 0.0), squint=0.3) if t > 0.8 else None,
                  dy=-160, screen_light=0.3, screen_col='#ff8a7a', hl=(150, -470), hr=(-150, -470),
                  handshape_l='fist', handshape_r='fist')


def carry(c, t):
    """La lleva de las orejas hacia la cocina."""
    with layer(c, 1.0, cfilter=COLD_LIMA):
        x = kf(t, [(0, 1500), (2.4, 2060)], linear)
        with U.cam(c, x + 80, 520, 1.45):
            L.home_bg(c, t, sky='#b8bcc4')
            def dangle(cc):
                sw = math.sin(t * 6) * 6
                with at(cc, 0, 0, 1.0, rot=sw):
                    R.draw(cc, 0, 108, 0.36, t, clip='gold', shadow=False, chirp=0.4 + 0.4 * math.sin(t * 3),
                           ears=-0.8, light=0.6 + 0.4 * math.sin(t * 6))
            EMI.draw(c, x, 880, 0.75, view='side', t=t, walk=(t * 1.0) % 1, expr='cold', look=(0.8, 0),
                     face=dict(brow=(-0.3, -0.9), mouth=(0.8, -0.35, 0.0, 0.0), squint=0.3),
                     hand_L=(200, -480), handshape_L='fist', hold_L=dangle)


def sink(c, t):
    """En la pileta: el chorro, las manos que empujan, la luz verde que titila y se apaga."""
    with layer(c, 1.0, cfilter=COLD_LIMA):
        with U.cam(c, 2260, 520, 2.0):
            L.home_bg(c, t, sky='#b8bcc4')
            gl = green_light(t, 3.0)
            # agua de la canilla
            flow = prog(t, 0.0, 0.3)
            for k in range(4):
                xo = 2378 + (k - 1.5) * 5 + math.sin(t * 20 + k) * 3
                line(c, [(xo, 485), (xo + math.sin(t * 13 + k) * 4, 485 + 110 * flow)], '#e8f6ff', 10, 0.55)
            # salpicaduras dentro de la pileta
            push = math.sin(t * 7) * 6 * (1 - prog(t, 2.4, 3.2))
            for k in range(10):
                a = rnd(2001, k) * math.pi
                r = ((t * 140 + k * 40) % 120) * (1 - prog(t, 2.8, 3.6))
                c.drawCircle(2350 + math.cos(a) * r, 588 - math.sin(a) * r * 0.5, 4, paint('#ffffff', 0.7))
            # puntas de las orejas que asoman y patalean
            kick = (1 - prog(t, 2.2, 3.0))
            for side in (-1, 1):
                ex = 2330 + side * 22 + math.sin(t * 9 + side) * 8 * kick
                line(c, [(ex, 586), (ex + side * 8, 568 - 10 * kick), (ex + side * 14, 560)], R.BLACK, 12)
            if gl > 0:
                glow(c, 2335, 588, 170, '#62e07a', 0.95 * gl)
                glow(c, 2335, 588, 60, '#c8ffd0', 0.9 * gl)
            # Emilia de perfil, inclinada sobre la pileta
            EMI.draw(c, 2150, 880, 0.75, view='side', t=t, lean=14, expr='angry', look=(0.6, 0.8),
                     face=dict(brow=(-0.4, -1.0), mouth=(0.8, -0.5, 0.0, 0.0), squint=0.45),
                     hand_L=((2335 - 2150) / 0.75, (590 + push - 880) / 0.75), handshape_L='fist',
                     hand_R=((2320 - 2150) / 0.75, (580 + push - 880) / 0.75), handshape_R='fist')
            # borde de la mesada por delante (tapa la pileta)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(2120, 592, 2480, 614), 8, 8), paint('#b9c2c8', 1))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(2120, 592, 2480, 614), 8, 8), paint(INK, 0.8, stroke=2.5))
    # la luz verde de la base, vista a través del agua (fuera de la gradación para que conserve el color)
    gl = green_light(t, 3.0)
    if gl > 0:
        with U.cam(c, 2260, 520, 2.0):
            glow(c, 2338, 584, 90, '#3aff6a', 0.8 * gl, blend=skia.BlendMode.kPlus)
            c.drawCircle(2338, 586, 7, paint('#8dffa8', gl))


def wide(c, t):
    """Plano final: la cocina, la canilla abierta, la heladera con la foto de Eva y su conejita."""
    with layer(c, 1.0, cfilter=COLD_LIMA):
        with U.cam(c, kf(t, [(0, 2480), (5.4, 2650)]), kf(t, [(0, 520), (5.4, 500)]), kf(t, [(0, 1.45), (5.4, 1.08)])):
            L.home_bg(c, t, sky='#a8acb6')
            L.fridge_photos(c, t, 6, PR.photo_eva_rabbit, [PR.photo_klaus, PR.photo_eva_rabbit, PR.photo_klaus,
                                                           PR.photo_eva_rabbit, PR.photo_klaus])
            for k in range(3):
                xo = 2378 + (k - 1) * 5
                line(c, [(xo, 485), (xo, 590)], '#e8f6ff', 8, 0.5)
            EMI.draw(c, 2300, 880, 0.75, view='back', t=t, hand_L=(80, -520), hand_R=(-80, -520), idle=0.2)
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(2120, 592, 2480, 614), 8, 8), paint('#b9c2c8', 1))


def draw(c, t):
    U.sequence(c, t, [
        (3.0, stare, None),
        (1.6, face, ('cut', 0)),
        (2.4, carry, ('cut', 0)),
        (4.6, sink, ('cut', 0)),
        (5.4, wide, ('fade', 1.2)),
    ])
