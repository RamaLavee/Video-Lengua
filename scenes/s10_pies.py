"""S10 — Cuatro pies: un hombre en la casa de Eva; la persecución por el pasillo.

La desnudez del libro se sugiere sin mostrarse: pies descalzos, hombros, muebles en primer plano.
"""
from scenes.common import *

TILT = 28   # la cámara quedó acostada en la cucha


def foot(c, x, y, s, big=False, flip=False, lift=0.0):
    """Pantorrilla y pie descalzo vistos desde el piso."""
    sk = P.KLAUS['skin'] if big else P.EVA['skin']
    w = 1.3 if big else 1.0
    with at(c, x, y - lift * 40, s, flip=flip):
        calf = R_taper([(0, -520), (6, -300), (0, -70)], 120 * w, 64 * w, 128 * w)
        shape(c, calf, sk, size=100)
        if big:
            for i in range(18):
                yy = -480 + i * 22
                xx = -36 + (i * 17) % 60
                c.drawLine(xx, yy, xx + 6, yy + 12, paint('#5a4030', 0.55, stroke=2.6))
        f = blob([(-40 * w, -10), (-46 * w, -70), (0, -96), (60 * w, -60), (140 * w, -30), (150 * w, 0), (-30 * w, 4)],
                 0.5, 1003 + big)
        shape(c, f, sk, size=80)
        for k in range(5):
            c.drawCircle((140 - k * 18) * w, -8 - (k == 0) * 4, (9 - k) * w, paint(shade(sk, -0.15), 1))
        c.drawArc(skia.Rect(-20 * w, -70, 30 * w, -30), 200, 120, False, paint(INK, 0.5, stroke=2.5))


def R_taper(pts, w0, w1, wm):
    return P.taper(pts, w0, w1, wm)


def feet_feed(t):
    def feed(c):
        with U.cam(c, 900, 560, 1.0):
            E.pov_bg(c, t)
        ex = 760 + math.sin(t * 1.1) * 140
        kx = 1260 + math.sin(t * 0.8 + 1) * 160
        foot(c, ex, 1000, 0.75, False, lift=max(0, math.sin(t * 3)) * 0.5)
        foot(c, ex + 150, 1010, 0.75, False, lift=max(0, math.sin(t * 3 + 3)) * 0.5)
        foot(c, kx, 1080, 0.95, True, lift=max(0, math.sin(t * 2.5)) * 0.4)
        foot(c, kx + 230, 1095, 0.95, True, lift=max(0, math.sin(t * 2.5 + 3)) * 0.4)
    return feed


def eva_above_feed(t):
    """Eva (con toalla, pelo mojado) endereza la cámara y le tira un beso."""
    def feed(c):
        E.eva_closeup_bg(c, t)
        s = 2.4
        kiss = pulse(t, 0.7, 1.3, 0.15)
        x = 960 + prog(t, 1.4, 1.8, ease_in) * 1400
        EVA_T.draw(c, x, head_at(EVA_T, s, 470), s, view='front', t=t, expr='happy' if kiss < 0.5 else 'tender', bust=True,
                   hand_L=(lerp(200, 40, kiss), lerp(-520, -800, kiss)), hand_R=(-200, -520), handshape_L='open',
                   bend_L=1, look=(0, 0.25), face=dict(mouth=(0.55, 0.25, 0.3, 0.0)) if kiss > 0.5 else None)
    return feed


def stove_feed(t, turn=0.0):
    """El hombre fríe huevos detrás de la mesa (la mesa en primer plano lo tapa de la cintura para abajo)."""
    def feed(c):
        with U.cam(c, 1250, 470, 1.0):
            E.pov_bg(c, t, mess=0.0)
        s = 1.25
        y = head_at(KLAUS_B, s, 330)
        if turn < 0.5:
            KLAUS_B.draw(c, 900, y, s, view='back', t=t, hand_L=(150, -720), hand_R=(-150, -740),
                         head_rot=8 * math.sin(t * 2))
            PR.frying_pan(c, 1080, 640, 1.0, rot=math.sin(t * 6) * 5, t=t)
        else:
            KLAUS_B.draw(c, 920, y, s, view='front', t=t, expr='frown', look=(0.0, 0.5), turn=0.15)
        c.drawRect(skia.Rect(-200, 720, 2600, 770), paint('#a8784e', 1))
        c.drawRect(skia.Rect(-200, 720, 2600, 770), paint(INK, 0.8, stroke=3))
        vgrad_rect(c, -200, 770, 2800, 40, '#7a5436', '#a8784e')
        c.drawRect(skia.Rect(-200, 810, 2600, 1300), paint('#8a6044', 1))
        PR.eggshells(c, 1350, 722, 1.1)
        PR.bottle(c, 1650, 722, 0.9)
        PR.magazine(c, 500, 712, 1.1, -3)
    return feed


def chase_feed(t, p):
    """Huida por el piso hacia el pasillo; la sombra del hombre crece por detrás."""
    def feed(c):
        cx = lerp(1500, 3950, ease_in(clamp(p)))
        with U.cam(c, cx, 600, 1.0 + 0.12 * p):
            E.pov_bg(c, t)
        sh = ease_out(clamp(p * 1.2))
        c.drawOval(skia.Rect(960 - 1500 * sh, 1250 - 900 * sh, 960 + 1500 * sh, 1250 + 500 * sh),
                   paint('#140f1a', 0.78 * sh, blur=70))
    return feed


def face_feed(t):
    def feed(c):
        E.eva_closeup_bg(c, t)
        s = 3.5
        KLAUS_B.draw(c, 960, head_at(KLAUS_B, s, 560), s, view='front', t=t, expr='blank', bust=True, look=(0, 0),
                     idle=0.5, face=dict(squint=-0.25))
    return feed


def draw(c, t):
    if t < 2.4:
        sc = lambda cc: U.pov(cc, t, feet_feed(t), tilt=TILT, hud_kw=dict())  # noqa: E731
        with U.cam(c, 1250, 520, 1.3):
            emi_desk(c, t, who=EMI_N, expr='curious', hl='key', hr='mouse', look=(0.7, 0.0), screen=sc, night=1.0,
                     clock_hm=(9, 40))
    elif t < 5.0:
        U.pov(c, t, feet_feed(t), tilt=TILT, zoom=1.12, hud_kw=dict())
    elif t < 6.6:
        tl = t - 5.0
        emi_front(c, tl, who=EMI_N, expr='frown' if tl < 0.9 else 'worried', night=1.0,
                  look=(-0.6, 0.1) if tl < 0.9 else (0, 0), turn=-0.3 if tl < 0.9 else 0, hl=(150, -470),
                  hr=(-150, -470), handshape_l='fist', handshape_r='fist')
    elif t < 8.4:
        tl = t - 6.6
        U.pov(c, t, eva_above_feed(tl), tilt=kf(tl, [(0, TILT), (0.5, 0)]), hud_kw=dict(chirp=pulse(tl, 0, 0.5, 0.1)))
    elif t < 10.0:
        tl = t - 8.4
        U.pov(c, t, stove_feed(tl, turn=prog(tl, 1.0, 1.2)), hud_kw=dict())
    elif t < 11.2:
        tl = t - 10.0
        with U.cam(c, 1120, 480, 1.6):
            emi_desk(c, tl, who=EMI_N, expr='shock', hl='collar', hr='collar', look=(0.8, 0.0), lean=-6, night=1.0,
                     screen=lambda cc: U.pov(cc, tl, stove_feed(tl, 1.0), hud_kw=dict()), handshape_l='fist',
                     handshape_r='fist', clock_hm=(9, 41))
    elif t < 14.0:
        tl = t - 11.2
        U.pov(c, t, chase_feed(t, tl / 2.8), shake=0.5 + tl * 0.2, tilt=math.sin(tl * 7) * 2,
              hud_kw=dict(pressed='up', chirp=pulse(tl, 1.6, 2.2, 0.1)))
    elif t < 15.3:
        tl = t - 14.0
        U.pov(c, t, face_feed(tl), zoom=kf(tl, [(0, 0.8), (0.4, 1.0), (1.3, 1.08)]), shake=0.25,
              tilt=kf(tl, [(0, 14), (0.4, 0)]), hud_kw=dict(chirp=pulse(tl, 0, 0.6, 0.1)))
    else:
        tl = t - 15.3
        with U.cam(c, 1150, 470, 1.6):
            emi_desk(c, tl, who=EMI_N, expr='scared', hl='collar', hr='collar', look=(0.8, -0.1), lean=-10,
                     night=1.0, screen=lambda cc: U.pov(cc, tl, face_feed(tl), hud_kw=dict()), handshape_l='fist',
                     handshape_r='fist', clock_hm=(9, 42))
