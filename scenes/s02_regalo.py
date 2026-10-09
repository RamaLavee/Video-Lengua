"""S02 — El regalo del hijo: Emilia abre el paquete de Hong Kong e ingresa el código de la tarjeta."""
from scenes.common import *


def screen(t):
    fill = prog(t, 7.0, 10.6, linear_fill)
    ok = prog(t, 10.8, 11.6, ease_out)
    return lambda c: U.serial_screen(c, t, fill, ok)


def linear_fill(x):
    # el código se ingresa dígito por dígito
    return math.floor(clamp(x) * 12) / 12.0


def draw(c, t):
    zoom = kf(t, [(0, 1.22), (6.5, 1.28), (13, 1.45)])
    cx = kf(t, [(0, 1180), (6.5, 1220), (13, 1330)])
    cy = kf(t, [(0, 500), (13, 470)])
    open_ = prog(t, 0.6, 3.2, smooth)
    with U.cam(c, cx, cy, zoom):
        # tiempos de la acción
        if t < 3.3:
            hl, hr = (1215 + math.sin(t * 6) * 16, 585), (1170 - math.sin(t * 5) * 12, 575)
            expr, look = 'frown', (0.7, 0.4)
            hs_l = hs_r = 'fist'
        elif t < 5.0:
            hl, hr = 'card', 'lap'
            expr, look = 'curious', (0.7, -0.1)
            hs_l, hs_r = 'hold', 'fist'
        elif t < 6.6:
            hl, hr = ('glasses' if t < 5.6 else 'card'), 'back'
            expr, look = ('worried' if t > 5.6 else 'calm'), (0.6, 0.0)
            hs_l, hs_r = 'hold', 'open'
        elif t < 11.2:
            hl, hr = 'type', (1110, 500)
            expr, look = 'frown', (0.7, 0.2)
            hs_l, hs_r = 'point', 'hold'
        else:
            hl, hr = 'lap', 'lap'
            expr, look = 'neutral', (-0.4, -0.7) if t < 12.2 else (0.6, 0.0)
            hs_l = hs_r = 'fist'
        lean = kf(t, [(5.0, 0), (5.6, -5), (6.4, 0)])
        head_rot = -10 if 11.2 < t < 12.2 else 0

        def card_in_hand(cc):
            PR.card(cc, 0, -10, 0.55, rot=-20)

        def desk_items(cc):
            # paquete con sellos de Hong Kong y celofán
            bx = kf(t, [(0, 1120), (3.2, 1120), (4.2, 1530)])
            by = kf(t, [(0, 500), (3.2, 500), (4.2, 548)])
            sc = kf(t, [(0, 1.0), (3.2, 1.0), (4.2, 0.6)])
            PR.gift_box(cc, bx, by, 160, 100, '#c85a4a', '#e8c35a', t=t, cello=1 - open_, stamps=True, s=sc)
        hold_l = card_in_hand if (3.3 <= t < 11.2 and hl != 'glasses') or (t >= 6.6 and t < 11.2) else None
        hold_r = card_in_hand if 6.6 <= t < 11.2 else None
        if 6.6 <= t < 11.2:
            hold_l = None
        emi_desk(c, t, expr=expr, hl=hl, hr=hr, look=look, head_rot=head_rot, lean=lean, screen=screen(t),
                 hold_l=hold_l, hold_r=hold_r, handshape_l=hs_l, handshape_r=hs_r, extra_desk=desk_items,
                 clock_hm=(5, 56))
