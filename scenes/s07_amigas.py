"""S07 — El mapa y las amigas: la distancia Lima–Erfurt y el café de los jueves después de natación."""
from scenes.common import *


def draw(c, t):
    if t < 4.6:
        p = prog(t, 0.6, 3.8, ease_io)
        lx, ly = U.map_xy(*U.PLACES['lima'])
        ex, ey = U.map_xy(*U.PLACES['erfurt'])
        cx = lerp(lx + 150, (lx + ex) / 2, prog(t, 0, 2.6)) if t < 2.6 else lerp((lx + ex) / 2, ex - 100, prog(t, 2.6, 4.6))
        cy = lerp(ly - 60, (ly + ey) / 2 - 150, prog(t, 0, 2.6)) if t < 2.6 else lerp((ly + ey) / 2 - 150, ey + 40,
                                                                                         prog(t, 2.6, 4.6))
        z = kf(t, [(0, 1.0), (2.3, 0.62), (4.6, 1.1)])
        with U.cam(c, cx, cy, z):
            U.world_map(c, t)
            U.map_route(c, t, 'lima', 'erfurt', p)
        return
    tl = t - 4.6
    with U.cam(c, kf(tl, [(0, 960), (6.4, 960)]), kf(tl, [(0, 560), (6.4, 540)]), kf(tl, [(0, 1.0), (6.4, 1.08)])):
        L.cafe_bg(c, t)
        L.swim_bag(c, 200, 1010, 1.05, '#4a8ac8')
        L.swim_bag(c, 1730, 1010, 1.0, '#e86a8a')
        # Gloria (izquierda): entusiasmo
        clap = abs(math.sin(tl * 9)) if 1.3 < tl < 3.2 else 0.0
        g_expr = 'joy' if 1.2 < tl < 4.5 else 'happy'
        GLORIA.draw(c, 560, 1150, 1.05, view='front', t=tl, expr=g_expr, bust=True, turn=0.35, look=(0.6, 0),
                    hand_L=(40 + clap * 50, -560) if 1.3 < tl < 3.2 else (150, -300),
                    hand_R=(-40 - clap * 50, -560) if 1.3 < tl < 3.2 else (-150, -300),
                    handshape_L='open', handshape_R='open', bend_L=1, bend_R=-1)
        # Inés (derecha): horrorizada, golpea la mesa con el índice
        tap = abs(math.sin(tl * 8)) * 30 if 2.6 < tl < 5.2 else 0
        i_expr = 'disgust' if tl < 2.6 else 'stern'
        INES.draw(c, 1370, 1150, 1.05, view='front', t=tl, expr=i_expr, bust=True, turn=-0.35, look=(-0.6, 0),
                  hand_R=(-60, -310 - tap) if tl > 2.6 else (-140, -300), handshape_R='point' if tl > 2.6 else 'fist',
                  hand_L=(140, -300), handshape_L='fist', talk=talk(tl, 3.0, 5.4, 10, 0.4))
        # Emilia (centro): cuenta con entusiasmo; después se ofende con Inés
        if tl < 2.6:
            e = dict(expr='proud', talk=talk(tl, 0.2, 2.4, 11, 0.5), turn=0.0, look=(0, 0),
                     hand_L=(110, -560 + math.sin(tl * 4) * 30), hand_R=(-110, -560 - math.sin(tl * 4) * 30),
                     handshape_L='open', handshape_R='open')
        elif tl < 5.0:
            e = dict(expr='happy', turn=-0.3, look=(-0.6, 0), hand_L=(150, -300), hand_R=(-150, -300))
        else:
            e = dict(expr='frown', turn=0.35, look=(0.7, 0.1), hand_L=(150, -300), hand_R=(-150, -300))
        EMI.draw(c, 960, 1130, 1.05, view='front', t=tl, bust=True, **e)
        L.cafe_table(c, tl)
