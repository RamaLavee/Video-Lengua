"""S08 — La rutina: el té, la nota fucsia, los juguetes, los zapatos, la cena frente al noticiero y la escapada."""
from scenes.common import *


def tea_walk(c, t):
    """Lima: Emilia lleva su té hacia la computadora."""
    x = kf(t, [(0, 2350), (3.4, 1500)], linear)
    with layer(c, 1.0, cfilter=WARM):
        with U.cam(c, x - 120, 520, 1.35):
            L.home_bg(c, t)
            EMI.draw(c, x, 880, 0.75, view='side', flip=True, t=t, walk=(t * 0.85) % 1, expr='calm',
                     hand_L=(130, -560), handshape_L='hold', hand_R=(110, -540), handshape_R='hold',
                     hold_L=lambda cc: PR.teacup(cc, 10, 10, 0.7, t, steam=1.0))


def note_pov(c, t):
    """Erfurt: la nota pegada a la pata de la silla (vista del kentuki)."""
    z = kf(t, [(0, 1.0), (3.2, 1.55)])

    def feed(cc):
        with U.cam(cc, 1700, 560, 1.0):
            E.pov_bg(cc, t)
        PR.note(cc, 1660 - 1700 + 960, 700 - 560 + 540, 1.0, rot=-6)
    U.pov(c, t, feed, zoom=z, center=(920, 680), hud_kw=dict(pressed='up' if t < 2.4 else None))


def toys(c, t):
    """Objetivo: la conejita ignora los juguetes y prefiere mirar los zapatos de Eva."""
    with layer(c, 1.0, cfilter=COOL):
        with U.cam(c, kf(t, [(0, 3000), (3.2, 3150)]), 720, 1.6):
            E.room_bg(c, t, sunset=0.4)
            PR.box(c, 3350, 640, 360, 260, '#c8a87a', depth=40, seed=801)
            PR.shoes_row(c, 3360, 880, 5, 0.95)
            PR.yarn(c, 2840, 905, 34)
            PR.toy_mouse(c, 2990, 905, 0.8)
            rx = kf(t, [(0, 2920), (1.2, 2920), (2.6, 3200)])
            R.draw(c, rx, 905, 0.55, t, yaw=kf(t, [(0, -0.5), (1.0, 0.0), (1.4, 0.8)]), ears=math.sin(t * 2) * 0.3,
                   purr=pulse(t, 2.6, 3.2, 0.1))


def sofa(c, t):
    """Objetivo: Eva cena en el sofá frente al noticiero, con la conejita entre los almohadones."""
    with layer(c, 1.0, cfilter=grade_filter(sat=0.95, bright=0.92, tint=(0.95, 0.98, 1.08))):
        with U.cam(c, 3000, 600, 1.3):
            E.room_bg(c, t, tv=1.0, night=0.35)
            pet = pulse(t, 1.4, 2.6, 0.3)
            R.draw(c, 2830, 780, 0.5, t, yaw=0.5, eyes=1.0, purr=pet)
            EVA.draw(c, 3050, 905, 0.74, view='front', t=t, sit=1, seat_h=300, expr='happy' if pet > 0.2 else 'calm',
                     turn=-0.35, look=(-0.6, 0.3) if pet > 0.2 else (0.6, -0.1),
                     hand_L=(60, -560), handshape_L='hold', hold_L=lambda cc: PR.plate(cc, 0, 10, 0.55),
                     hand_R=(-260, -560 + math.sin(t * 6) * 14 * pet) if pet > 0.1 else (-80, -560), handshape_R='open')
            PR.bottle(c, 3260, 900, 0.7)


def escape(c, t):
    """Objetivo: Eva sale de noche y la conejita se escapa debajo de la mesa."""
    with layer(c, 1.0, cfilter=grade_filter(sat=0.9, bright=0.88, tint=(0.94, 0.97, 1.1))):
        with U.cam(c, kf(t, [(0, 2200), (3.2, 1700)]), 560, 1.18):
            E.room_bg(c, t, night=0.35)
            rx = kf(t, [(0, 2350), (1.6, 1500), (3.2, 1440)], ease_out)
            R.draw(c, rx, 905, 0.55, t, yaw=-0.9, ears=math.sin(t * 8) * 0.8, chirp=pulse(t, 0.3, 0.7, 0.1) * 0.5)
            ex = kf(t, [(0, 2750), (3.2, 1900)])
            EVA.draw(c, ex, 905, 0.74, view='side', flip=True, t=t, walk=(t * 1.1) % 1, expr='laugh',
                     look=(0.7, 0.4), hand_L=(160, -470), handshape_L='open', front_L=True)
            # mesa por delante
            PR.box(c, 1150, 600, 620, 34, '#a8784e', depth=40, seed=2104)


def draw(c, t):
    U.sequence(c, t, [
        (3.4, tea_walk, None),
        (3.3, note_pov, ('paper', 0.8)),
        (3.4, toys, ('paper', 0.8)),
        (3.5, sofa, ('fade', 0.7)),
        (3.4, escape, ('fade', 0.6)),
    ])
