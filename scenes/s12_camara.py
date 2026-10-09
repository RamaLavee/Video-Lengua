"""S12 — La cámara: Eva le limpia los ojos («ahí está la cámara»); el hombre deja de sonreír y la mira."""
from scenes.common import *


def eva_lift_feed(t):
    def feed(c):
        E.eva_closeup_bg(c, t)
        s = 2.3
        dry = math.sin(t * 7) * 30
        EVA_T.draw(c, 960, head_at(EVA_T, s, 480), s, view='front', t=t, expr='talk' if t < 1.6 else 'happy', bust=True,
                   talk=talk(t, 0.5, 1.5), look=(0.6, 0.0) if t < 1.6 else (0, 0.2), turn=0.3 if t < 1.6 else 0,
                   hand_L=(120, -900 + dry), bend_L=1, handshape_L='open',
                   hold_L=lambda cc: PR.towel_corner(cc, 30, -30, 0.5, rot=20), hand_R=(-200, -520))
    return feed


def wipe_feed(t):
    def feed(c):
        E.eva_closeup_bg(c, t)
        s = 2.6
        point = prog(t, 1.2, 1.5)
        EVA_T.draw(c, 960, head_at(EVA_T, s, 430), s, view='front', t=t, expr='tender' if t < 1.2 else 'talk', bust=True,
                   talk=talk(t, 1.3, 2.3), look=(0, 0.1),
                   hand_L=(lerp(180, 105, point), lerp(-520, -700, point)), handshape_L='point' if point > 0.3 else 'open',
                   bend_L=-1, hand_R=(-200, -520))
        # la toalla pasa por delante de la lente
        sw = prog(t, 0.0, 1.0, ease_io)
        if 0 < sw < 1:
            PR.towel_corner(c, lerp(-400, 2300, sw), 640, 3.0, rot=-20)
    return feed


def sofa_feed(t, stare):
    """Desde el sofá, junto a Eva: el hombre trae la comida, pregunta, y se queda mirando la cámara."""
    def feed(c):
        with U.cam(c, 600, 380, 1.0):
            E.room_bg(c, t, night=0.2)
        s = 1.5
        smile = 1 - stare
        KLAUS_B.draw(c, 1150, head_at(KLAUS_B, s, 360), s, view='front', t=t,
                     expr='happy' if smile > 0.5 else 'blank', emix=None, bust=True, look=(-0.3, 0.1) if stare < 0.5 else (0, 0),
                     turn=-0.2 * smile, talk=talk(t, 0.6, 1.6) * smile,
                     hand_L=(130, -650), handshape_L='hold', hold_L=lambda cc: PR.plate(cc, 0, 0, 0.8),
                     hand_R=(-160, -560), face=dict(squint=-0.2) if stare > 0.5 else None)
        # Eva a la izquierda: hombro, toalla y el dedo que señala a la conejita
        nod = math.sin(t * 6) * 0.15 * pulse(t, 1.8, 2.8, 0.2)
        EVA_T.draw(c, 300, head_at(EVA_T, 2.0, 560), 2.0, view='front', t=t, expr='talk' if 1.8 < t < 3.0 else 'happy',
                   talk=talk(t, 1.8, 2.8), turn=0.55, look=(0.8, 0.0), nod=nod, bust=True,
                   hand_L=(200, -700) if 1.8 < t < 3.0 else (150, -420), handshape_L='point', bend_L=-1)
    return feed


def draw(c, t):
    if t < 3.6:
        U.pov(c, t, eva_lift_feed(t), wet=1 - prog(t, 2.4, 3.6), tilt=kf(t, [(0, -8), (1.0, 0)]),
              hud_kw=dict())
        U.subtitle(c, t, 0.5, 1.2, seed=121)
    elif t < 6.0:
        tl = t - 3.6
        U.pov(c, t, wipe_feed(tl), wet=0.4 * (1 - prog(tl, 0.0, 1.0)), hud_kw=dict())
        U.subtitle(c, tl, 1.3, 1.2, seed=123)
    elif t < 8.4:
        tl = t - 6.0
        emi_front(c, tl, who=EMI_N, expr='tender' if tl < 1.4 else 'happy', blush=0.6, night=1.0,
                  hl=(25, -575), hr=(-150, -470), handshape_l='open', handshape_r='fist', bend_L=-1,
                  face=dict(brow=(0.4, 0.8)) if tl < 1.4 else None)
    else:
        tl = t - 8.4
        stare = prog(tl, 2.2, 2.7)
        z = 1.0 + 0.9 * prog(tl, 2.5, 4.3, ease_io)
        with layer(c, 1.0, cfilter=TENSE if stare > 0 else None):
            U.pov(c, t, sofa_feed(tl, stare), zoom=z, center=(1150, 380), hud_kw=dict())
        U.subtitle(c, tl, 1.8, 1.0, seed=125)
