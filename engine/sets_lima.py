"""Escenarios de Lima (paleta cálida: ocres, terracota, mostaza, durazno) y Hong Kong."""
import math
import skia
from .core import W, H, shade, noise1, rnd, lerp, clamp, cmix
from .draw import (INK, LW, paint, smooth_path, ellipse, blob, shape, line, at, rrect, poly, glow, clip,
                   lin_grad, rad_grad, vgrad_rect, layer)
from . import props as PR

_pics = {}


def cached(key, fn, bounds=(-3000, -3000, 9000, 6000)):
    """Graba un dibujo estático como skia.Picture y lo reutiliza en cada fotograma."""
    if key not in _pics:
        rec = skia.PictureRecorder()
        cc = rec.beginRecording(skia.Rect(*bounds))
        fn(cc)
        _pics[key] = rec.finishRecordingAsPicture()
    return _pics[key]


def draw_cached(c, key, fn):
    c.drawPicture(cached(key, fn))


WALL = '#ebc49c'
WALL2 = '#e3b68d'
WAINS = '#c58b66'
FLOOR = '#9b6a4b'
SKY_LIMA = ('#d9c9c6', '#efd2bd')


# ---------------------------------------------------------------- exterior de Lima
def lima_sky(c, t):
    vgrad_rect(c, -400, -200, 2800, 1300, '#c9bcc4', '#f2d2b8', mid='#e6c7c0')
    for i in range(6):
        x = (i * 520 + t * 12 * (1 + i % 3)) % 2900 - 500
        y = 120 + (i % 3) * 140
        cl = blob([(x, y), (x + 120, y - 50), (x + 300, y - 60), (x + 460, y - 20), (x + 420, y + 30), (x + 60, y + 34)],
                  6, 1100 + i)
        c.drawPath(cl, paint('#fbeee6', 0.55, blur=6))
    glow(c, 1500, 640, 520, '#ffd9a8', 0.35)


def lima_sea_cliffs(c, t):
    # mar
    vgrad_rect(c, -400, 860, 2800, 1600, '#a9bcc0', '#6f909a')
    for i in range(9):
        y = 900 + i * 32 + i * i * 2
        ph = t * (0.4 + i * 0.05) + i
        pts = [(x, y + math.sin(x * 0.01 + ph) * (2 + i * 0.6)) for x in range(-400, 2500, 120)]
        line(c, pts, '#e6f0ee', 2.5 + i * 0.3, 0.5)
    # playa y espuma
    beach = blob([(-400, 1225), (300, 1210), (900, 1230), (1500, 1215), (2400, 1235), (2400, 1275), (900, 1268), (-400, 1272)], 3, 1111)
    shape(c, beach, '#d8c09a', shadow=False, lw=2)
    for i in range(4):
        y = 1272 + i * 22
        pts = [(x, y + math.sin(x * 0.012 + t * 1.2 + i) * 6) for x in range(-400, 2500, 80)]
        line(c, pts, '#ffffff', 5, 0.55 - i * 0.12)
    # acantilados (Costa Verde)
    cliff = blob([(-400, 760), (100, 740), (500, 770), (900, 750), (1300, 780), (1700, 760), (2400, 790),
                  (2400, 1230), (1900, 1200), (1500, 1215), (1000, 1190), (600, 1220), (100, 1200), (-400, 1215)], 5, 1112)
    shape(c, cliff, '#b98f63', size=500, shadow_a=0.3)
    with clip(c, cliff):
        for i in range(30):
            x = rnd(1113, i) * 2800 - 400
            y = 800 + rnd(1114, i) * 380
            line(c, [(x, y), (x + 40 + rnd(1115, i) * 80, y + 120)], '#8a6a4a', 3, 0.35)
        for i in range(14):
            x = rnd(1116, i) * 2800 - 400
            y = 820 + rnd(1117, i) * 300
            c.drawOval(skia.Rect(x, y, x + 120, y + 40), paint('#7f9a5a', 0.5, blur=4))
    # costanera (carretera) al pie
    line(c, [(-400, 1180), (2400, 1175)], '#6a6066', 10, 0.8)


def lima_city(c, t):
    # edificios sobre el acantilado
    cols = ['#e8d2b8', '#d9b694', '#f0dcc4', '#cfa98a', '#e2c6a8', '#c9b0a0', '#efe2cf']
    x = -380
    i = 0
    while x < 2400:
        w = 90 + rnd(1121, i) * 150
        h = 120 + rnd(1122, i) * 260
        y = 770 - h
        cc = cols[i % len(cols)]
        shape(c, rrect(x, y, w, h + 30, 4, 0.6, 1123 + i), cc, size=w, lw=2.2, line_a=0.75)
        for r in range(int(h / 46)):
            for k in range(int(w / 40)):
                wx, wy = x + 12 + k * 38, y + 16 + r * 46
                lit = rnd(1124, i * 50 + r * 7 + k) > 0.8
                c.drawRect(skia.Rect(wx, wy, wx + 20, wy + 24), paint('#ffd994' if lit else '#9aa6b0', 0.8))
        x += w + 8 + rnd(1125, i) * 30
        i += 1
    for i in range(7):
        px = 100 + i * 330
        line(c, [(px, 770), (px + 4, 690)], '#6a5a4a', 5)
        for k in range(5):
            a = math.pi * (1.1 + k * 0.2)
            line(c, [(px + 4, 690), (px + 4 + math.cos(a) * 46, 690 + math.sin(a) * 30 + 20)], '#5f7a4a', 6)


def lima_facade(c, t, lit=1.0):
    """Edificio cercano con balcones limeños de madera; la ventana iluminada de Emilia."""
    shape(c, rrect(-300, 1250, 2900, 1800, 6, 1.0, 1131), '#e8cfae', size=900, shadow_a=0.2)
    # cornisas
    for y in (1250, 1700, 2150, 2600):
        c.drawRect(skia.Rect(-320, y - 14, 2620, y + 10), paint('#cfae8a', 1))
        c.drawRect(skia.Rect(-320, y - 14, 2620, y + 10), paint(INK, 0.6, stroke=2))
    # balcones de cajón (madera tallada)
    for bx, by in ((330, 1330), (1170, 1330), (330, 1780), (1960, 1330), (1960, 1780), (-480, 1780), (720, 2230),
                   (1580, 2230)):
        shape(c, rrect(bx, by, 420, 300, 8, 0.8, 1132 + bx), '#7a4a32', size=200)
        for k in range(5):
            c.drawRect(skia.Rect(bx + 20 + k * 80, by + 30, bx + 80 + k * 80, by + 170), paint('#a8c8d0', 0.7))
            c.drawRect(skia.Rect(bx + 20 + k * 80, by + 30, bx + 80 + k * 80, by + 170), paint(INK, 0.6, stroke=2))
        for k in range(10):
            c.drawRect(skia.Rect(bx + 20 + k * 40, by + 200, bx + 46 + k * 40, by + 280), paint('#5f3a26', 1))
        c.drawRect(skia.Rect(bx - 12, by + 290, bx + 432, by + 312), paint('#5f3a26', 1))
    # ventana de Emilia
    wx, wy = 1170, 1800
    PR.window(c, wx, wy, 420, 280, content=lambda cc, w, h: _emilia_window_inside(cc, w, h, t, lit),
              frame='#f3ede2', curtain='#d9a84a', t=t)
    # plantas en macetas
    PR.plant(c, 1660, 2120, 0.7, t=t)


def _emilia_window_inside(c, w, h, t, lit):
    vgrad_rect(c, 0, 0, w, h, cmix('#5a4a52', '#f6c77a', lit), cmix('#3a2e36', '#e09a5a', lit))
    glow(c, w * 0.3, h * 0.4, 260, '#fff0c0', 0.5 * lit)
    # silueta de Emilia en la ventana (la presentamos sin revelar aún su cara)
    c.drawOval(skia.Rect(w * 0.55, h * 0.35, w * 0.7, h * 0.58), paint('#3a2a30', 0.55 * lit))
    c.drawOval(skia.Rect(w * 0.5, h * 0.55, w * 0.75, h * 1.1), paint('#3a2a30', 0.55 * lit))


def pelicans(c, t, x0=0, y0=300, n=5, speed=90, s=1.0):
    for i in range(n):
        x = x0 + t * speed - i * 140 * s
        y = y0 + i * 26 * s + math.sin(t * 1.3 + i) * 10
        flap = math.sin(t * 5 + i * 0.8)
        with at(c, x, y, s):
            line(c, [(-60, flap * 18), (-20, -6), (0, 0), (20, -6), (60, flap * 18)], '#4a3e42', 6)
            c.drawOval(skia.Rect(-14, -6, 22, 8), paint('#4a3e42', 1))
            line(c, [(20, 0), (44, 4)], '#c9a04a', 4)


# ---------------------------------------------------------------- pasillo y escritorio de Emilia (perfil)
DESK_TOP = 640
DESK_X0, DESK_X1 = 1000, 1800
MON = (1265, 300, 440)   # x, y, ancho de la pantalla
KEYB = (1010, 594, 280)  # x, y, ancho del teclado


def hall_bg(c, clock_hm=(5, 55), lamp_on=1.0, night=0.0):
    def base(cc):
        vgrad_rect(cc, -600, -100, 3200, 800, WALL, WALL2)
        for i in range(-6, 32):
            x = i * 90
            cc.drawRect(skia.Rect(x, -100, x + 45, 600), paint('#f3d4b0', 0.35))
        cc.drawRect(skia.Rect(-600, 600, 2600, 620), paint('#a87252', 1))
        vgrad_rect(cc, -600, 620, 3200, 270, WAINS, shade(WAINS, -0.1))
        for i in range(-6, 30):
            x = i * 110
            cc.drawRect(skia.Rect(x + 10, 650, x + 100, 860), paint(INK, 0.18, stroke=2))
        vgrad_rect(cc, -600, 880, 3200, 400, FLOOR, shade(FLOOR, -0.2))
        for i in range(8):
            y = 890 + i * 30 + i * i * 3
            cc.drawLine(-600, y, 2600, y, paint(shade(FLOOR, -0.3), 0.5, stroke=2))
        cc.drawRect(skia.Rect(-600, 870, 2600, 892), paint('#7a4a32', 1))
        PR.door(cc, 60, 180, 260, 700, open_=0.35)
        PR.frame_pic(cc, 520, 200, 230, 170, PR.mountains_pic)
        cc.drawRect(skia.Rect(1180, 205, 1640, 225), paint('#8a5a3c', 1))
        cc.drawRect(skia.Rect(1180, 205, 1640, 225), paint(INK, 0.8, stroke=2.5))
        PR.gift_box(cc, 1205, 110, 110, 95, '#6a7aa8', '#e8c35a')
        PR.gift_box(cc, 1350, 135, 90, 70, '#a85a7a', '#f3e6c8')
        PR.gift_box(cc, 1475, 100, 120, 105, '#5a8a7a', '#e8c35a')
        cc.drawOval(skia.Rect(500, 900, 1500, 1010), paint('#a8423a', 0.55))
        cc.drawOval(skia.Rect(540, 915, 1460, 995), paint('#e8c35a', 0.5, stroke=4))
    draw_cached(c, 'hall_bg2', base)
    PR.clock(c, 1800, 130, 58, *clock_hm)
    if night > 0:
        c.drawRect(skia.Rect(-600, -100, 2600, 1300), paint('#1a2040', 0.55 * night, blend=skia.BlendMode.kMultiply))


def desk_back(c, t=0.0, screen_fn=None, on=1.0, lamp_on=1.0, glow_a=1.0):
    """Parte trasera del escritorio: torre, parlantes, lámpara y monitor. Devuelve el rect de pantalla."""
    def base(cc):
        PR.tower(cc, 1610, 620, 120, 250)
        PR.speaker(cc, 1170, 500, 70, 110)
        PR.speaker(cc, 1740, 500, 70, 110)
    draw_cached(c, 'desk_back2', base)
    x, y, w = MON
    r = PR.monitor(c, x, y, w, t, screen_fn, on)
    PR.lamp(c, 1840, DESK_TOP, on=lamp_on, s=0.85)
    if on > 0 and glow_a > 0:
        glow(c, x + w / 2, y + w * 0.28, 520, '#bfdcff', 0.22 * on * glow_a)
    return r


def desk_front(c, t=0.0, pressed=None, mouse=True):
    """Tapa, cajón y patas del escritorio (tapan las rodillas de Emilia) y el teclado."""
    def base(cc):
        PR.box(cc, DESK_X0, DESK_TOP, DESK_X1 - DESK_X0, 34, '#8b5a3c', depth=60, seed=1201)
        for lx in (DESK_X0 + 20, DESK_X1 - 54):
            cc.drawRect(skia.Rect(lx, DESK_TOP + 34, lx + 34, 880), paint('#7a4a32', 1))
            cc.drawRect(skia.Rect(lx, DESK_TOP + 34, lx + 34, 880), paint(INK, 0.8, stroke=2.5))
        PR.box(cc, DESK_X0 + 70, DESK_TOP + 34, 300, 74, '#9a6646', seed=1202)
        cc.drawCircle(DESK_X0 + 220, DESK_TOP + 72, 7, paint('#e0c060', 1))
    draw_cached(c, 'desk_front2', base)
    x, y, w = KEYB
    PR.keyboard(c, x, y, w, pressed=pressed)
    if mouse:
        PR.mouse_dev(c, 1345, DESK_TOP - 16, 0.8)


def desk(c, t=0.0, screen_fn=None, on=1.0, pressed=None, lamp_on=1.0, items=True, glow_a=1.0):
    r = desk_back(c, t, screen_fn, on, lamp_on, glow_a)
    desk_front(c, t, pressed)
    return r


def screen_cam_bg(c, night=0.0, lamp=1.0):
    """Contraplano: la pared del pasillo vista desde el monitor, detrás de Emilia."""
    def base(cc):
        vgrad_rect(cc, -400, -200, 2800, 900, WALL, WALL2)
        for i in range(-5, 28):
            x = i * 90
            cc.drawRect(skia.Rect(x, -200, x + 45, 700), paint('#f3d4b0', 0.35))
        cc.drawRect(skia.Rect(-400, 690, 2400, 712), paint('#a87252', 1))
        vgrad_rect(cc, -400, 712, 2800, 500, WAINS, shade(WAINS, -0.12))
        PR.door(cc, 1300, 120, 300, 760, open_=0.0)
        PR.frame_pic(cc, 360, 170, 260, 190, PR.mountains_pic)
        PR.frame_pic(cc, 700, 230, 150, 120, lambda c2, w, h: (vgrad_rect(c2, 0, 0, w, h, '#c9d8e0', '#e8dcc8'),
                                                               c2.drawCircle(w / 2, h * 0.55, h * 0.28, paint('#c48b65', 1))))
    draw_cached(c, 'screen_cam_bg', base)
    glow(c, 200, 300, 600, '#ffd79a', 0.35 * lamp)
    if night > 0:
        c.drawRect(skia.Rect(-400, -200, 2400, 1300), paint('#1a2040', 0.5 * night, blend=skia.BlendMode.kMultiply))


def desk_edge_cam(c, t, typing=0.0, pressed=None):
    """Borde del escritorio en primer plano (contraplano desde la pantalla)."""
    def base(cc):
        PR.box(cc, -100, 900, 2120, 60, '#8b5a3c', seed=1211)
        vgrad_rect(cc, -100, 958, 2120, 200, '#7a4a32', '#5a3422')
    draw_cached(c, 'desk_front', base)
    # teclado visto desde atrás (borde)
    shape(c, rrect(620, 860, 680, 56, 12, 0.5, 1212), PR.MONITOR_C, size=50)
    for k in range(14):
        kx = 650 + k * 46
        dy = 4 if typing and math.sin(t * 22 + k * 1.7) > 0.7 else 0
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(kx, 862 + dy, kx + 38, 880 + dy), 4, 4), paint(shade(PR.MONITOR_C, -0.15), 1))


# ---------------------------------------------------------------- casa de Emilia: entrada, comedor, cocina, heladera
HOME_W = 3600


def home_bg(c, t=0.0, sky='#cfd2d6', photos=0, window_light=1.0):
    def base(cc):
        # paredes
        vgrad_rect(cc, -400, -200, 1900, 1100, WALL, WALL2)
        vgrad_rect(cc, 1500, -200, 2500, 1100, '#e9d8bc', '#dcc6a4')
        for i in range(-4, 18):
            x = i * 90
            cc.drawRect(skia.Rect(x, -200, x + 45, 640), paint('#f3d4b0', 0.3))
        cc.drawRect(skia.Rect(-400, 620, 1500, 640), paint('#a87252', 1))
        vgrad_rect(cc, -400, 640, 1900, 250, WAINS, shade(WAINS, -0.1))
        # azulejos de cocina
        for r in range(6):
            for k in range(24):
                x = 1520 + k * 80
                y = 360 + r * 80
                cc.drawRect(skia.Rect(x, y, x + 78, y + 78), paint('#f2ece0' if (r + k) % 2 else '#dfe8e4', 1))
                cc.drawRect(skia.Rect(x, y, x + 78, y + 78), paint('#b8b0a0', 0.6, stroke=1.5))
        # pisos: madera en comedor, baldosas en cocina
        vgrad_rect(cc, -400, 880, 1900, 500, FLOOR, shade(FLOOR, -0.2))
        for i in range(8):
            y = 890 + i * 30 + i * i * 3
            cc.drawLine(-400, y, 1500, y, paint(shade(FLOOR, -0.3), 0.5, stroke=2))
        for r in range(6):
            for k in range(30):
                x = 1500 + k * 90 - r * 10
                y = 880 + r * 40 + r * r * 4
                cc.drawRect(skia.Rect(x, y, x + 88, y + 40 + r * 8), paint('#c9b48e' if (r + k) % 2 else '#e6d6b4', 1))
        cc.drawRect(skia.Rect(-400, 870, 4000, 890), paint('#7a4a32', 1))
        # puerta de entrada
        PR.door(cc, 120, 200, 300, 680, color='#7a4a32')
        # enchufe junto a la puerta del living
        cc.drawRRect(skia.RRect.MakeRectXY(skia.Rect(480, 800, 520, 850), 4, 4), paint('#f3ede2', 1))
        cc.drawRRect(skia.RRect.MakeRectXY(skia.Rect(480, 800, 520, 850), 4, 4), paint(INK, 0.7, stroke=2))
        # aparador y ventana del comedor
        PR.box(cc, 640, 560, 380, 320, '#8b5a3c', depth=50, seed=1301)
        for k in range(3):
            cc.drawRect(skia.Rect(660 + k * 120, 600, 760 + k * 120, 850), paint(INK, 0.35, stroke=2))
        PR.frame_pic(cc, 700, 280, 220, 160, PR.mountains_pic)
        # mesada y bajo mesada
        PR.box(cc, 1560, 600, 1260, 280, '#d8c49a', depth=40, top='#efe6d4', seed=1302)
        for k in range(6):
            cc.drawRect(skia.Rect(1580 + k * 205, 640, 1765 + k * 205, 860), paint(INK, 0.35, stroke=2))
            cc.drawCircle(1740 + k * 205, 680, 6, paint('#8a7a6a', 1))
        # alacenas
        PR.box(cc, 1560, 40, 600, 220, '#d8c49a', seed=1303)
        PR.box(cc, 2500, 40, 330, 220, '#d8c49a', seed=1304)
        # cocina a gas
        cc.drawRect(skia.Rect(1600, 590, 1900, 604), paint('#3a3236', 1))
        for k in range(2):
            cc.drawOval(skia.Rect(1630 + k * 140, 575, 1730 + k * 140, 598), paint('#2a2427', 1))
        # pileta y canilla
        cc.drawRRect(skia.RRect.MakeRectXY(skia.Rect(2130, 585, 2470, 612), 10, 10), paint('#b9c2c8', 1))
        cc.drawRRect(skia.RRect.MakeRectXY(skia.Rect(2130, 585, 2470, 612), 10, 10), paint(INK, 0.8, stroke=2.5))
        line(cc, [(2300, 590), (2300, 470), (2360, 455), (2380, 480)], '#a9b4bc', 16)
        line(cc, [(2300, 590), (2300, 470), (2360, 455), (2380, 480)], INK, 2, 0.7)
        cc.drawCircle(2265, 560, 12, paint('#a9b4bc', 1))
        cc.drawCircle(2335, 560, 12, paint('#a9b4bc', 1))
        # heladera retro
        shape(cc, rrect(2900, 120, 380, 760, 40, 0.8, 1305), '#efe7d2', size=300)
        cc.drawLine(2900, 380, 3280, 380, paint(INK, 0.7, stroke=3))
        line(cc, [(2930, 200), (2930, 340)], '#b8b0a0', 12)
        line(cc, [(2930, 420), (2930, 600)], '#b8b0a0', 12)
        for k, cc_ in enumerate(('#e86a5a', '#5a9ad8', '#f2c94a', '#7ac46a', '#c46ad8')):
            PR.magnet(cc, 3000 + k * 55, 170 + (k % 2) * 30, cc_)
        for k in range(2):
            shape(cc, rrect(3020 + k * 120, 430, 90, 120, 3, 0.4, 1306 + k), '#fbf8f1', size=40, shadow=False, lw=2)
            cc.drawRect(skia.Rect(3030 + k * 120, 445, 3100 + k * 120, 470), paint(['#e86a5a', '#3a9a5a'][k], 0.9))
        # mesa de fórmica (comedor)
        shape(cc, rrect(980, 610, 560, 40, 14, 0.6, 1307), '#9fd3c4', size=40)
        cc.drawRect(skia.Rect(982, 640, 1538, 652), paint('#c8ced2', 1))
        for lx in (1010, 1500):
            cc.drawRect(skia.Rect(lx, 652, lx + 16, 880), paint('#c8ced2', 1))
            cc.drawRect(skia.Rect(lx, 652, lx + 16, 880), paint(INK, 0.7, stroke=2))
    draw_cached(c, 'home_bg', base)
    # ventana sobre la pileta (cielo gris de Lima)
    def view(cc, w, h):
        vgrad_rect(cc, 0, 0, w, h, sky, shade(sky, 0.2))
        for i in range(6):
            bx = i * 70
            bh = 60 + rnd(1310, i) * 120
            cc.drawRect(skia.Rect(bx, h - bh, bx + 60, h), paint('#b8aea6', 0.9))
    PR.window(c, 2150, 140, 300, 230, content=view, frame='#f3ede2', t=t)


def fridge_photos(c, t, n=1, main_content=None, others=None):
    """Fotos impresas pegadas en la heladera de Emilia."""
    if n >= 1 and main_content:
        PR.photo(c, 3090, 290, 150, 110, 1.0, rot=-3, content=main_content)
    if n >= 2 and others:
        spots = [(2980, 640, 4), (3190, 650, -6), (3080, 760, 2), (3200, 180, 5), (2990, 470, -4)]
        for i, (x, y, r) in enumerate(spots[:n - 1]):
            PR.photo(c, x, y, 100, 76, 1.0, rot=r, content=others[i % len(others)], border=10)


# ---------------------------------------------------------------- dormitorio
def bedroom_bg(c, t=0.0, night=1.0, lamp=0.0):
    def base(cc):
        vgrad_rect(cc, -400, -200, 2800, 1100, '#c9b6c8', '#b8a2b8')
        for i in range(-4, 28):
            x = i * 100
            cc.drawRect(skia.Rect(x, -200, x + 50, 900), paint('#d8c6d6', 0.3))
        vgrad_rect(cc, -400, 880, 2800, 400, '#7a5a4a', '#5a3e32')
        # ventana con la noche de Lima
        def view(c2, w, h):
            vgrad_rect(c2, 0, 0, w, h, '#2a2c4a', '#4a4466')
            for i in range(8):
                bx = i * 60
                bh = 70 + rnd(1401, i) * 120
                c2.drawRect(skia.Rect(bx, h - bh, bx + 52, h), paint('#3a3650', 1))
                for k in range(4):
                    if rnd(1402, i * 9 + k) > 0.55:
                        c2.drawRect(skia.Rect(bx + 10, h - bh + 14 + k * 26, bx + 24, h - bh + 28 + k * 26),
                                    paint('#ffd994', 0.8))
        PR.window(cc, 1250, 160, 420, 330, content=view, frame='#efe6da', curtain='#8a6a9a')
        # cama
        PR.box(cc, 200, 520, 60, 380, '#7a4a32', seed=1403)
        shape(cc, rrect(240, 650, 900, 150, 20, 0.8, 1404), '#efe6f2', size=120)
        shape(cc, rrect(240, 700, 900, 120, 30, 1.0, 1405), '#9a7ab8', size=120)
        for k in range(5):
            line(cc, [(320 + k * 160, 720), (300 + k * 160, 810)], shade('#9a7ab8', -0.2), 3, 0.5)
        shape(cc, ellipse(330, 650, 100, 40, 1.0, 1406), '#fbf6ee', size=80)
        cc.drawRect(skia.Rect(240, 800, 1140, 840), paint('#7a4a32', 1))
        cc.drawRect(skia.Rect(1110, 820, 1140, 900), paint('#7a4a32', 1))
        # mesita de luz con cajón
        PR.box(cc, 20, 640, 160, 240, '#8b5a3c', depth=30, seed=1407)
        cc.drawRect(skia.Rect(35, 680, 165, 740), paint(INK, 0.5, stroke=2))
        cc.drawCircle(100, 710, 6, paint('#e0c060', 1))
    draw_cached(c, 'bedroom_bg', base)
    # velador
    with at(c, 70, 640, 1.0):
        shape(c, rrect(-12, -90, 24, 90, 4, 0.3, 1408), '#c9a24a', size=20)
        shape(c, blob([(-60, -90), (60, -90), (40, -170), (-40, -170)], 0.5, 1409), '#f3e2c0', size=60)
        if lamp > 0:
            glow(c, 0, -120, 500, '#ffd79a', 0.6 * lamp)
    # despertador analógico (3:10)
    PR.clock(c, 140, 610, 26, 3, 10, color='#fbf6ee', rim='#c46a5a')
    if night > 0:
        c.drawRect(skia.Rect(-400, -200, 2400, 1300), paint('#1a2550', 0.45 * night * (1 - lamp * 0.5),
                                                          blend=skia.BlendMode.kMultiply))


# ---------------------------------------------------------------- supermercado
def super_bg(c, t=0.0):
    def base(cc):
        vgrad_rect(cc, -400, -200, 2800, 1100, '#e8e6dc', '#d8d6cc')
        for k in range(5):
            x = 100 + k * 420
            cc.drawRect(skia.Rect(x, -10, x + 260, 14), paint('#ffffff', 1))
            glow(cc, x + 130, 20, 300, '#ffffff', 0.4)
        # góndolas
        for r in range(4):
            y = 160 + r * 170
            cc.drawRect(skia.Rect(-400, y + 140, 2400, y + 160), paint('#c8ced2', 1))
            cc.drawRect(skia.Rect(-400, y + 140, 2400, y + 160), paint(INK, 0.6, stroke=2))
            for k in range(40):
                x = -380 + k * 72
                col_ = ['#e86a5a', '#4a8a5a', '#f2c94a', '#5a7ac8', '#c46ad8', '#e8a05a'][(k + r * 3) % 6]
                if r == 2 and 18 <= k <= 22:
                    continue   # estante vacío (las galletitas)
                PR.can(cc, x + 30, y + 140, 0.9 if r % 2 else 1.0, col_)
        vgrad_rect(cc, -400, 880, 2800, 400, '#d8d2c4', '#c4bcae')
        for k in range(30):
            cc.drawLine(-400 + k * 120, 880, -600 + k * 140, 1300, paint('#b8b0a2', 0.6, stroke=2))
    draw_cached(c, 'super_bg', base)


def peaches_and_cans(c, t, swap=0.0):
    """Cajón con latas de arvejas y duraznos; swap 0..1 pasa los duraznos arriba."""
    PR.box(c, 1240, 760, 420, 130, '#b88a5a', depth=40, seed=1501)
    for k in range(4):
        PR.can(c, 1300 + k * 95, 780 - swap * 0, 0.9, '#5a9a4a', '#f3f0d8')
    for k in range(3):
        y = lerp(800, 690, swap)
        x = 1330 + k * 110
        PR.peach(c, x, y + (0 if swap > 0.5 else 30), 1.0)


# ---------------------------------------------------------------- café
def cafe_bg(c, t=0.0):
    def base(cc):
        vgrad_rect(cc, -400, -200, 2800, 1100, '#e6d2b6', '#d8c0a0')
        PR.window(cc, 160, 120, 640, 420, content=_cafe_street, frame='#6a4a3a', mull=True)
        PR.window(cc, 1120, 120, 640, 420, content=_cafe_street, frame='#6a4a3a', mull=True)
        for k in range(3):
            x = 400 + k * 560
            line(cc, [(x, -200), (x, 60)], INK, 3, 0.8)
            shape(cc, blob([(x - 70, 60), (x + 70, 60), (x + 40, 0), (x - 40, 0)], 0.4, 1601 + k), '#c46a4a', size=60)
        vgrad_rect(cc, -400, 840, 2800, 400, '#8a6a52', '#6a4e3a')
        PR.plant(cc, 960, 840, 1.1)
    draw_cached(c, 'cafe_bg', base)


def _cafe_street(c, w, h):
    vgrad_rect(c, 0, 0, w, h, '#d6dde0', '#eae4d8')
    for i in range(5):
        bx = i * 140
        bh = 140 + rnd(1611, i) * 160
        c.drawRect(skia.Rect(bx, h - bh, bx + 120, h), paint(['#e8d2b8', '#cfa98a', '#efe2cf'][i % 3], 1))
    c.drawRect(skia.Rect(0, h - 40, w, h), paint('#9a9a9a', 1))


def cafe_table(c, t=0.0):
    shape(c, ellipse(960, 830, 620, 80, 0.8, 1621), '#f3ede2', size=120)
    c.drawRect(skia.Rect(940, 880, 980, 1180), paint('#5a4a42', 1))
    for k, x in enumerate((640, 960, 1280)):
        PR.teacup(c, x, 830, 0.9, t + k, steam=0.8, color=['#f3eadb', '#e8f0f4', '#f6e2e2'][k])


def swim_bag(c, x, y, s=1.0, color='#4a8ac8'):
    with at(c, x, y, s):
        shape(c, blob([(-90, 0), (-100, -130), (100, -130), (90, 0)], 0.6, 1631), color, size=100)
        line(c, [(-60, -130), (-40, -200), (40, -200), (60, -130)], shade(color, -0.3), 8)
        # antiparras colgando
        for k in (-1, 1):
            c.drawOval(skia.Rect(-30 + k * 26 - 16, -60, -30 + k * 26 + 16, -36), paint('#2a2a3a', 1))
            c.drawOval(skia.Rect(-30 + k * 26 - 10, -55, -30 + k * 26 + 10, -41), paint('#9ad0ff', 1))
        line(c, [(-72, -48), (-90, -90), (40, -90), (14, -48)], '#2a2a3a', 3)


# ---------------------------------------------------------------- Hong Kong
def hk_bg(c, t=0.0, balcony=True):
    def base(cc):
        vgrad_rect(cc, -400, -200, 2800, 1300, '#1c1840', '#4a2a5a', mid='#2a2050')
        for i in range(26):
            x = -300 + i * 100 + rnd(1701, i) * 40
            bh = 300 + rnd(1702, i) * 600
            w = 70 + rnd(1703, i) * 60
            col_ = ['#2a2a4a', '#30304e', '#26263e'][i % 3]
            cc.drawRect(skia.Rect(x, 900 - bh, x + w, 1000), paint(col_, 1))
            for r in range(int(bh / 30)):
                for k in range(int(w / 22)):
                    if rnd(1704, i * 400 + r * 10 + k) > 0.55:
                        cc.drawRect(skia.Rect(x + 6 + k * 22, 900 - bh + 12 + r * 30, x + 16 + k * 22, 900 - bh + 24 + r * 30),
                                    paint(['#ffd994', '#9ad8ff', '#ff9ac8'][(r + k) % 3], 0.75))
        vgrad_rect(cc, -400, 900, 2800, 400, '#1a1a38', '#0e0e22')
        for i in range(20):
            y = 920 + i * 14
            line(cc, [(-400, y), (2400, y + 3)], '#5a4a8a', 2, 0.4)
    draw_cached(c, 'hk_bg', base)
    for i, (x, y, cc_) in enumerate(((300, 420, '#ff5ab0'), (1400, 380, '#5ad8ff'), (900, 560, '#ffd04a'))):
        glow(c, x, y, 220, cc_, 0.25 + 0.08 * math.sin(t * 2 + i))
    # cartel rojo del restaurante de enfrente (farol, sin texto)
    with at(c, 1650, 560, 1.0):
        shape(c, rrect(-60, -120, 120, 240, 20, 0.6, 1705), '#c8302e', size=100)
        glow(c, 0, 0, 200, '#ff6a4a', 0.35)
        for k in range(3):
            c.drawRect(skia.Rect(-30, -80 + k * 60, 30, -50 + k * 60), paint('#f6d26a', 0.9))
    if balcony:
        c.drawRect(skia.Rect(-400, 880, 2400, 905), paint('#8a8aa0', 1))
        for k in range(40):
            c.drawRect(skia.Rect(-400 + k * 70, 905, -392 + k * 70, 1100), paint('#8a8aa0', 1))
