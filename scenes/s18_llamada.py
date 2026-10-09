"""S18 — La llamada: Klaus recibe una llamada extraña; Eva vuelve de yoga; las fotos; Eva llama a Emilia."""
from scenes.common import *


def klaus_feed(t, phase):
    def feed(c):
        with U.cam(c, 1250, 560, 1.0):
            E.pov_bg(c, t, mess=0.5)
        if phase == 0:
            KLAUS_U.draw(c, 760, 1010, 0.8, view='side', t=t, expr='neutral', look=(0.6, 0.2),
                         hand_L=(260, -620), hand_R=(240, -600))
            PR.frying_pan(c, 1000, 520, 0.6, t=t)
            PR.phone(c, 1350, 540, 0.45, rot=80, vibrate=1.0, t=t, screen=U.call_screen('incoming', 3, t))
        else:
            KLAUS_U.draw(c, 1150, 1010, 0.8, view='front', t=t, expr='cold', look=(0, 0.3), turn=0.1,
                         hand_R=(-108, -925), bend_R=-1, handshape_R='hold',
                         hold_R=lambda cc: PR.phone(cc, -6, -20, 0.4, rot=12))
    return feed


def eva_enter_feed(t):
    def feed(c):
        with U.cam(c, 1250, 560, 1.0):
            E.pov_bg(c, t, mess=0.5)
        show = prog(t, 1.8, 2.4)
        KLAUS_U.draw(c, 900, 1010, 0.8, view='front', t=t, expr='cold', look=(0.6, 0.2) if t < 1.6 else (0, 0.3),
                     turn=0.4 if t < 1.6 else 0.0, talk=talk(t, 0.6, 1.6, 9, 0.35),
                     hand_L=(lerp(60, 230, show), lerp(-760, -620, show)), bend_L=1, handshape_L='hold',
                     hold_L=lambda cc: PR.phone(cc, 0, 0, 0.4), hand_R=(-60, -800), bend_R=-1)
        ex = kf(t, [(0, 2300), (1.0, 1400)])
        EVA.draw(c, ex, 1000, 0.76, view='front', t=t, expr='curious' if t < 2.6 else 'surprise', turn=-0.4,
                 look=(-0.6, 0.2) if t < 1.6 else (0, 0.3), hand_L=(110, -640), bend_L=1, handshape_L='hold',
                 hold_L=lambda cc: PR.yoga_mat(cc, 0, 30, 0.6, rot=10))
    return feed


def photos_closeup(c, t):
    """El teléfono de Klaus: fotos de Emilia y de su casa llena de fotos (las mandó la conejita de Lima)."""
    with layer(c, 1.0, cfilter=COOL):
        E.eva_closeup_bg(c, t)
    sw = prog(t, 1.0, 1.4)

    def scr(cc, w, h):
        cc.drawRect(skia.Rect(0, 0, w, h), paint('#101014', 1))
        with clip(cc, (0, h * 0.12, w, h * 0.88)):
            cc.save()
            cc.translate(-w * sw, h * 0.12)
            PR.photo_emilia_phone(cc, w, h * 0.76)
            cc.translate(w, 0)
            PR.photo_fridge(cc, w, h * 0.76)
            cc.restore()
    PR.phone(c, 960, 560, 3.8, rot=-3, screen=scr)
    sk = P.KLAUS['skin']
    shape(c, blob([(1180, 1200), (1170, 900), (1235, 820), (1300, 900), (1310, 1200)], 1.0, 1801), sk, size=150)
    for k in range(3):
        shape(c, ellipse(700, 760 + k * 80, 40, 30, 0.5, 1803 + k), sk, size=40)
    if 0.8 < t < 1.6:
        shape(c, ellipse(lerp(1150, 850, prog(t, 0.9, 1.4)), 520, 40, 50, 0.5, 1802), P.KLAUS['skin'], size=60)


def smirk_feed(t):
    def feed(c):
        with U.cam(c, 1250, 560, 1.0):
            E.pov_bg(c, t, mess=0.5)
        s = kf(t, [(0, 1.6), (1.4, 2.2)])
        down = prog(t, 0.8, 1.6)
        EVA.draw(c, 960, head_at(EVA, s, lerp(330, 470, down)), s, view='front', t=t, expr='smirk', bust=True,
                 look=(0, 0.1), hand_L=(lerp(110, 100, down), lerp(-640, -760, down)), bend_L=1, handshape_L='hold',
                 hold_L=lambda cc: PR.phone(cc, -4, -20, 0.42, rot=-8) if down > 0.5 else None)
    return feed


def eva_floor_feed(t):
    def feed(c):
        with U.cam(c, 1250, 560, 1.0):
            E.pov_bg(c, t, mess=0.5)
        s = 2.2
        EVA.draw(c, 960, head_at(EVA, s, 470), s, view='front', t=t, expr='smirk' if (t % 3) < 1.6 else 'talk',
                 talk=talk(t, 0.0, 99, 9, 0.35), bust=True, look=(0, 0.1), hand_L=(100, -760), bend_L=1,
                 handshape_L='hold', hold_L=lambda cc: PR.phone(cc, -4, -20, 0.42, rot=-8))
    return feed


def draw(c, t):
    if t < 1.6:
        U.pov(c, t, klaus_feed(t, 0), hud_kw=dict())
    elif t < 3.6:
        tl = t - 1.6
        U.pov(c, t, klaus_feed(tl, 1), zoom=kf(tl, [(0, 1.0), (2.0, 1.15)]), center=(1150, 450), hud_kw=dict())
    elif t < 6.4:
        tl = t - 3.6
        U.pov(c, t, eva_enter_feed(tl), hud_kw=dict())
    elif t < 8.0:
        photos_closeup(c, t - 6.4)
    elif t < 9.6:
        tl = t - 8.0
        U.pov(c, t, smirk_feed(tl), hud_kw=dict())
    elif t < 11.6:
        tl = t - 9.6
        nudge = prog(tl, 0.2, 1.0)
        px = lerp(1560, 1430, nudge)
        answered = tl > 1.2

        def items(cc):
            R.draw(cc, px + 120, 640, 0.3, tl, yaw=-0.8, clip='gold', look=(-0.6, 0.6))
            if not answered:
                PR.phone(cc, px, 628, 0.45, rot=90, vibrate=1.0, t=tl, screen=U.call_screen('incoming', 3, tl))
        with U.cam(c, 1250, 500, 1.55):
            emi_desk(c, tl, expr='curious' if not answered else 'neutral', hl=(px, 600) if not answered else 'ear',
                     hr='key', look=(0.6, 0.4) if not answered else (0.8, 0),
                     handshape_l='hold', hold_l=(lambda cc: PR.phone(cc, 0, -6, 0.42, rot=-10)) if answered else None,
                     screen=lambda cc: U.pov(cc, tl, eva_floor_feed(tl), hud_kw=dict()), extra_desk=items,
                     clock_hm=(2, 9))
    elif t < 14.6:
        tl = t - 11.6
        expr = 'curious' if tl < 0.8 else ('worried' if tl < 1.9 else 'shock')
        spill = prog(tl, 2.2, 2.9)

        def scr(cc):
            U.pov(cc, tl, eva_floor_feed(tl), hud_kw=dict())
            U.subtitle(cc, tl, 0.2, 2.6, seed=181, lines=2)

        def rabbit_desk(cc):
            R.draw(cc, 1610, 640, 0.3, tl, yaw=-0.75, clip='gold', look=(-0.7, -0.2))
        with U.cam(c, 1250, 490, 1.5):
            emi_desk(c, tl, expr=expr, hl='ear', hr='key' if tl < 2.1 else 'chest', look=(0.8, -0.1),
                     lean=kf(tl, [(0, 3), (2.1, 3), (2.6, -12)]), handshape_l='hold',
                     hold_l=lambda cc: PR.phone(cc, 0, -6, 0.42, rot=-10), screen=scr, cup_spill=spill,
                     extra_desk=rabbit_desk, clock_hm=(2, 10), creak=pulse(tl, 2.1, 2.6, 0.1))
    else:
        tl = t - 14.6
        rise = prog(tl, 0.0, 0.5, ease_out)
        emi_front(c, tl, expr='shock' if tl < 0.6 else 'talk', talk_amt=talk(tl, 0.6, 1.2, 9, 0.25),
                  dy=-160 * rise, hl=(98, -650) if tl < 1.2 else (150, -470), bend_L=1, handshape_l='hold',
                  hold_l=lambda cc: PR.phone(cc, 0, -6, 0.42, rot=-10), hr=(-150, -470), handshape_r='fist',
                  desk=True, face=dict(brow=(0.7, 0.9)))
