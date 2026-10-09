"""S03 — La conexión: el ojo «despertar», la entrada en la pantalla y la chica de pelo mojado."""
from scenes.common import *

# Eva (pelo mojado) en primer plano frente a la cámara del kentuki
def eva_close(c, t, x=1180, y=1700, s=1.55, expr='curious', talk_amt=0.0, look=(0.0, 0.0), turn=0.0, hl=None, hr=None,
              hs_l='open', hs_r='open', who=None, hold_l=None, hold_r=None, head_rot=0.0, nod=0.0, **kw):
    who = who or EVA_W
    pose = dict(expr=expr, talk=talk_amt, look=look, turn=turn, bust=True, eyes=eyes(t, 9), head_rot=head_rot,
                handshape_L=hs_l, handshape_R=hs_r, hold_L=hold_l, hold_R=hold_r, nod=nod)
    pose.update(kw)
    if hl:
        pose['hand_L'] = hl
    if hr:
        pose['hand_R'] = hr
    who.draw(c, x, y, s, view='front', t=t, **pose)


def erfurt_kitchen(t, extra=None, cx=1500):
    def feed(c):
        with U.cam(c, cx, 470, 1.0):
            E.pov_bg(c, t, calendar=True)
        if extra:
            extra(c)
    return feed


def draw(c, t):
    if t < 4.6:
        # A: la pantalla de la computadora y la entrada en ella
        eye_btn = prog(t, 0.3, 1.0, ease_out)
        pressed = 2.1 < t < 2.5
        to_feed = prog(t, 2.6, 3.4, smooth)

        def scr(cc):
            U.serial_screen(cc, t, 1.0, 1.0, eye_btn, pressed)
            if t < 2.5:
                U.cursor(cc, lerp(1300, 990, prog(t, 1.0, 2.0)), lerp(800, 560, prog(t, 1.0, 2.0)), 1.6)
            if to_feed > 0:
                with layer(cc, to_feed):
                    feed = erfurt_kitchen(t)
                    U.pov(cc, t, feed, hud_kw=dict(eye=1.0))
        x, y, w = L.MON
        h = w * 9 / 16
        z0 = 1.35
        z1 = 1920.0 / w
        q = ease_in(clamp((t - 2.7) / 1.9)) if t > 2.7 else 0
        zoom = lerp(z0, z1, q)
        cx = lerp(1380, x + w / 2, ease_io(clamp((t - 2.3) / 2.3)))
        cy = lerp(450, y + h / 2, ease_io(clamp((t - 2.3) / 2.3)))
        with U.cam(c, cx, cy, zoom):
            emi_desk(c, t, expr='curious' if t < 2.0 else 'surprise', hl='key', hr='mouse', look=(0.7, -0.1),
                     screen=scr, handshape_r='hold')
    elif t < 9.6:
        # B: vista del kentuki: cocina ajena, llega Eva con el pelo mojado
        tl = t - 4.6
        ex = kf(tl, [(0, 2300), (1.2, 1100), (5, 1060)])
        ey = kf(tl, [(0, 2100), (1.2, 2150), (5, 2250)])
        es = kf(tl, [(0, 1.8), (1.2, 2.2), (5, 2.45)])

        def extra(cc):
            eva_close(cc, tl, ex, ey, es, expr='curious' if tl < 3.6 else 'talk', talk_amt=talk(tl, 1.4, 3.4),
                      look=(0.0, 0.1), turn=kf(tl, [(0, -0.4), (1.5, 0.0)]), head_rot=kf(tl, [(2.5, 0), (3.5, -8)]))
        feed = erfurt_kitchen(t, extra, cx=kf(tl, [(0, 1600), (5, 1650)]))
        U.pov(c, t, feed, hud_kw=dict(eye=1.0))
        U.subtitle(c, tl, 1.5, 2.4, seed=31)
    else:
        # C: contraplano: Emilia contesta «yes» (no se oye)
        tl = t - 9.6
        expr = 'curious' if tl < 1.0 else ('talk' if tl < 1.6 else 'happy')
        emi_front(c, tl, expr=expr, talk_amt=talk(tl, 1.0, 1.5, 14, 0.5), lean=kf(tl, [(0, 0), (1.0, -3)]),
                  look=(0.0, -0.05), nod=kf(tl, [(0, 0), (1.0, 0.15)]), hl=(165, -455), hr=(-165, -455),
                  handshape_l='fist', handshape_r='fist')
