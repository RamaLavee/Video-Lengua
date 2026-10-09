"""S17 — Ama y ser: la convivencia con su propia conejita, las fotos impresas, los llamados de Klaus."""
from scenes.common import *


def photo_eva(c, w, h):
    """Foto de la pantalla: Eva sola, sonriendo (las fotos de Klaus están en la mesita de luz, no aquí)."""
    vgrad_rect(c, 0, 0, w, h, '#bcd9d2', '#a9cbc4')
    c.save()
    c.scale(w / 400.0, h / 300.0)
    EVA.draw(c, 200, 120 + 868 * 0.42, 0.42, view='front', t=0, expr='happy', bust=True, idle=0)
    c.restore()


def photo_erfurt(c, w, h):
    """Foto de la pantalla: Erfurt al atardecer desde la ventana de Eva."""
    vgrad_rect(c, 0, 0, w, h, '#ec7a52', '#f6b86a')
    c.save()
    c.scale(w / 400.0, h / 300.0)
    for i in range(6):
        x = i * 70
        c.drawRect(skia.Rect(x, 190, x + 60, 300), paint('#e8c4a0', 1))
        c.drawPath(poly([(x - 6, 190), (x + 30, 150), (x + 66, 190)]), paint('#c25a48', 1))
    E._dom_icon(c, 280, 150, 0.35, '#6a3a4a')
    c.restore()


FRIDGE_OTHERS = [photo_eva, photo_erfurt, PR.photo_eva_rabbit, photo_eva, photo_erfurt]


def fridge(c, t, n=6):
    L.fridge_photos(c, t, n, PR.photo_eva_rabbit, FRIDGE_OTHERS)


def kitchen(c, t):
    with layer(c, 1.0, cfilter=WARM):
        with U.cam(c, kf(t, [(0, 3090), (2.6, 2650)]), kf(t, [(0, 380), (2.6, 520)]), kf(t, [(0, 2.4), (2.6, 1.35)])):
            L.home_bg(c, t)
            fridge(c, t)
            ex = kf(t, [(0, 3500), (2.8, 2450)])
            EMI_R.draw(c, ex, 880, 0.75, view='side', flip=True, t=t, walk=(t * 0.8) % 1, expr='calm', look=(0.6, 0.3))
            rx = kf(t, [(0, 3750), (2.9, 2700)])
            R.draw(c, rx, 885, 0.34, t, yaw=-0.6, clip='gold', ears=math.sin(t * 4) * 0.3)


def tea(c, t):
    with layer(c, 1.0, cfilter=WARM):
        with U.cam(c, 1900, 560, 1.5):
            L.home_bg(c, t)
            PR.teacup(c, 1700, 600, 0.9, t, steam=1.0)
            line(c, [(1750, 560), (1760, 480)], '#ffffff', 6, 0.0)
            EMI_R.draw(c, 1850, 880, 0.75, view='front', t=t, expr='tender', look=(0.4, 0.8), nod=0.5, turn=0.3,
                       hand_L=(150, -420), hand_R=(-150, -420), blush=0.3)
            R.draw(c, 2020, 885, 0.36, t, yaw=-0.5, look=(-0.3, -0.6), clip='gold', purr=pulse(t, 0.6, 2.2, 0.3))


def ring(c, t):
    """El teléfono vibra en la mesada: la conejita mira fijo el número iluminado."""
    with layer(c, 1.0, cfilter=grade_filter(sat=0.9, tint=(0.98, 1.0, 1.03))):
        with U.cam(c, kf(t, [(0, 1980), (1.6, 2010)]), kf(t, [(0, 640), (1.6, 700)]), kf(t, [(0, 2.4), (1.6, 3.4)])):
            L.home_bg(c, t)
            PR.phone(c, 2050, 590, 0.6, rot=0, screen=U.call_screen('incoming', 9, t), vibrate=1.0, t=t)
            R.draw(c, 2000, 885, 0.5, t, yaw=0.3, look=(0.4, -0.9), clip='gold', lens_glint=0.6 + 0.4 * math.sin(t * 8))
    U.icon_sound(c, 1500, 300, 60, '#ffd84a', 0.8, t)


def listen(c, t):
    with layer(c, 1.0, cfilter=WARM):
        with U.cam(c, 1900, 520, 1.6):
            L.home_bg(c, t)
            EMI_R.draw(c, 1850, 880, 0.75, view='front', t=t, expr='calm', eyes=0.0, nod=-0.2,
                       hand_L=(98, -650), bend_L=1, handshape_L='hold', hold_L=lambda cc: PR.phone(cc, 0, -6, 0.42, rot=-10),
                       hand_R=(-150, -420), talk=talk(t, 1.4, 2.0, 9, 0.3))
            R.draw(c, 2070, 885, 0.36, t, yaw=-0.4, look=(-0.4, -0.9), clip='gold')


def desk2pm(c, t):
    lift = prog(t, 0.4, 1.4)
    rx = lerp(1080, 1640, lift)
    ry = lerp(880, 640, lift) - math.sin(lift * math.pi) * 120

    def under(cc):
        if lift < 0.99:
            R.draw(cc, rx, ry, 0.3, t, yaw=-0.6, clip='gold', shadow=lift < 0.05)

    def on_desk(cc):
        if lift >= 0.99:
            R.draw(cc, 1640, 640, 0.3, t, yaw=-0.75, look=(-0.6, -0.8), clip='gold', ears=math.sin(t * 3) * 0.3,
                   purr=pulse(t, 2.4, 4.0, 0.3))

    hl = (rx, ry - 60) if lift < 0.99 else ('up' if 1.8 < t < 3.6 else 'key')
    with U.cam(c, 1300, 480, 1.4):
        scr = lambda cc: U.pov(cc, t, pov_feed(t, 2900, 560), hud_kw=dict())  # noqa: E731
        emi_desk(c, t, expr='happy' if t > 1.6 else 'calm', hl=hl, hr='mouse', look=(0.8, -0.2), talk_amt=talk(t, 2.0, 3.4, 10, 0.4),
                 handshape_l='point' if 1.8 < t < 3.6 else 'open', screen=scr, clock_hm=(2, 0), extra_desk=on_desk,
                 under_desk=under, cup=False)


def draw(c, t):
    U.sequence(c, t, [
        (3.0, kitchen, None),
        (2.3, tea, ('fade', 0.5)),
        (1.9, ring, ('cut', 0)),
        (1.5, listen, ('cut', 0)),
        (4.8, desk2pm, ('paper', 0.8)),
    ])
