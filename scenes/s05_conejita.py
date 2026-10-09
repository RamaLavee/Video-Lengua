"""S05 — Eres una conejita: la caja del kentuki y la revelación del cuerpo de peluche."""
from scenes.common import *
from scenes.s03_conexion import eva_close


def draw(c, t):
    if t < 4.6:
        # A: Eva muestra la caja vacía frente a la cámara
        z = kf(t, [(0, 1.0), (2.0, 1.12), (4.6, 1.16)])

        def box_hold(cc):
            pass

        def feed(cc):
            with U.cam(cc, 2700, 470, 1.0):
                E.pov_bg(cc, t)
            eva_close(cc, t, 1000, 1500, 1.35, expr='happy' if t < 2.4 else 'talk', talk_amt=talk(t, 2.4, 4.2),
                      look=(0.0, 0.2), hl=(240, -520), hr=(-240, -520), hs_l='open', hs_r='open')
            PR.kentuki_box(cc, 560, 640, 380, 470, t, s=1.0)
        U.pov(c, t, feed, zoom=z, center=(1100, 640), hud_kw=dict())
        U.subtitle(c, t, 2.5, 1.9, seed=51)
    elif t < 7.2:
        # B: Emilia se lleva las manos a la cabeza, como buscando las orejas
        tl = t - 4.6
        up = prog(tl, 0.5, 1.2, ease_out)
        hl = (lerp(165, 128, up), lerp(-455, -790, up))
        hr = (lerp(-165, -128, up), lerp(-455, -790, up))
        expr = 'surprise' if tl < 1.4 else 'happy'
        emi_front(c, tl, expr=expr, hl=hl, hr=hr, handshape_l='open', handshape_r='open', bend_L=1, bend_R=-1,
                  head_rot=kf(tl, [(1.2, 0), (2.0, -9)]), look=(0, -0.3) if tl < 1.4 else (0, 0), blush=0.4)
    else:
        # C: corte por coincidencia de gesto: la conejita inclina la cabeza en Erfurt
        tl = t - 7.2
        with layer(c, 1.0, cfilter=COOL):
            cx = kf(tl, [(0, 2330), (4.8, 2420)])
            with U.cam(c, cx, 585, kf(tl, [(0, 1.28), (4.8, 1.33)])):
                E.room_bg(c, tl)
                rx = kf(tl, [(0, 2120), (1.6, 2120), (3.6, 2330)], ease_io)
                tilt = kf(tl, [(0, -9), (1.2, -9), (1.8, 4), (2.4, 0)])
                R.draw(c, rx, 905, 0.75, tl, yaw=kf(tl, [(0, -0.2), (1.6, 0.35)]), tilt=tilt,
                       ears=math.sin(tl * 3) * 0.3, chirp=pulse(tl, 3.7, 4.1, 0.1))
                EVA_W.draw(c, 2680, 905, 0.72, view='front', t=tl, expr='joy' if tl > 3.6 else 'happy',
                           look=(-0.5, 0.6), nod=0.3, turn=-0.25, hand_L=(150, -560), hand_R=(-170, -540),
                           handshape_L='open', handshape_R='open')
