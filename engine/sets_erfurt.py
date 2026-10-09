"""Escenarios de Erfurt (paleta fría: menta, celeste, lila, con acentos fucsia de Eva)."""
import math
import skia
from .core import W, H, shade, noise1, rnd, lerp, clamp, cmix
from .draw import (INK, LW, paint, smooth_path, ellipse, blob, shape, line, at, rrect, poly, glow, clip,
                   lin_grad, rad_grad, vgrad_rect, layer)
from . import props as PR
from .sets_lima import draw_cached

E_WALL = '#bcd9d2'
E_WALL2 = '#a9cbc4'
E_FLOOR = '#c6a27a'
E_CAB = '#8fc1b5'
SOFA = '#9a8ac0'
HORIZON = 760          # línea del piso en la vista baja del kentuki


# ---------------------------------------------------------------- vista baja del kentuki (panorama)
# Secciones (x): cocina 0-1350 | mesa 1350-2350 | living 2350-3600 | pasillo/baño 3600-4400 | entrada 4400-5200
POV_W = 5200


def pov_bg(c, t=0.0, mess=1.0, light=1.0, night=0.0, bag=True, calendar=True, fridge_photo=None):
    def base(cc):
        vgrad_rect(cc, -600, -400, POV_W + 1200, HORIZON + 400, E_WALL, E_WALL2)
        for i in range(-6, 64):
            x = i * 100
            cc.drawRect(skia.Rect(x, -400, x + 50, HORIZON), paint('#cde6df', 0.35))
        cc.drawRect(skia.Rect(-600, HORIZON - 40, POV_W + 600, HORIZON), paint('#f2efe6', 1))
        cc.drawRect(skia.Rect(-600, HORIZON - 40, POV_W + 600, HORIZON), paint(INK, 0.6, stroke=2))
        # piso con perspectiva baja: tablas que se separan hacia abajo
        vgrad_rect(cc, -600, HORIZON, POV_W + 1200, 600, shade(E_FLOOR, 0.1), shade(E_FLOOR, -0.15))
        y = HORIZON
        k = 0
        while y < H + 300:
            cc.drawLine(-600, y, POV_W + 600, y, paint(shade(E_FLOOR, -0.3), 0.45, stroke=2))
            y += 10 + k * k * 1.6
            k += 1
        for i in range(-10, 70):
            x = i * 160
            cc.drawLine(x, HORIZON, x + (x - 2600) * 0.9, H + 300, paint(shade(E_FLOOR, -0.3), 0.25, stroke=2))
        # ---- cocina
        PR.box(cc, 0, 300, 900, HORIZON - 300, E_CAB, depth=0, seed=2001)
        for k in range(4):
            cc.drawRect(skia.Rect(20 + k * 220, 330, 220 + k * 220, HORIZON - 30), paint(INK, 0.35, stroke=2.5))
            line(cc, [(190 + k * 220, 360), (190 + k * 220, 440)], '#e8e4da', 8)
        cc.drawRect(skia.Rect(-20, 270, 920, 300), paint('#f2efe6', 1))
        cc.drawRect(skia.Rect(-20, 270, 920, 300), paint(INK, 0.7, stroke=2.5))
        # horno
        shape(cc, rrect(250, 360, 300, 300, 10, 0.5, 2002), '#e4e2dc', size=150)
        cc.drawRect(skia.Rect(280, 420, 520, 600), paint('#3a3a44', 1))
        # tacho de basura
        shape(cc, rrect(940, 520, 150, 240, 20, 0.6, 2003), '#d8d5dc', size=100)
        cc.drawRect(skia.Rect(930, 510, 1100, 535), paint('#b8b5bc', 1))
        # heladera alta (sale de cuadro)
        shape(cc, rrect(1110, -300, 260, HORIZON + 300, 20, 0.6, 2004), '#f4f2ee', size=200)
        cc.drawLine(1110, 100, 1370, 100, paint(INK, 0.6, stroke=2.5))
        line(cc, [(1140, 140), (1140, 300)], '#c8c6c0', 12)
        for k, cc_ in enumerate(('#e0408a', '#5a9ad8', '#f2c94a')):
            PR.magnet(cc, 1180 + k * 60, 40 + (k % 2) * 30, cc_, 12)
        # ---- mesa (vista desde abajo)
        cc.drawRect(skia.Rect(1450, 380, 2300, 420), paint('#a8784e', 1))
        cc.drawRect(skia.Rect(1450, 380, 2300, 420), paint(INK, 0.8, stroke=2.5))
        vgrad_rect(cc, 1460, 420, 830, 30, '#7a5436', '#a8784e')
        for lx in (1480, 2250):
            shape(cc, rrect(lx, 420, 36, HORIZON + 40 - 420, 6, 0.5, 2005 + lx), '#9a6a44', size=36)
        # sillas (patas y asiento visto desde abajo)
        for sx in (1550, 2060):
            cc.drawRect(skia.Rect(sx, 540, sx + 200, 566), paint('#7a5a8a', 1))
            cc.drawRect(skia.Rect(sx, 540, sx + 200, 566), paint(INK, 0.8, stroke=2))
            for lx in (sx + 6, sx + 176):
                cc.drawRect(skia.Rect(lx, 566, lx + 18, HORIZON + 60), paint('#5a4a6a', 1))
        # ---- living
        def view(c2, w, h):
            vgrad_rect(c2, 0, 0, w, h, '#a8c8e8', '#e8d8d0')
            for i in range(7):
                bx = i * 90
                bh = 80 + rnd(2010, i) * 140
                c2.drawRect(skia.Rect(bx, h - bh, bx + 80, h), paint('#d8a890', 1))
                c2.drawPath(poly([(bx - 6, h - bh), (bx + 40, h - bh - 50), (bx + 86, h - bh)]), paint('#b8584a', 1))
        PR.window(cc, 2520, 60, 560, 420, content=view, frame='#f4f2ee', curtain='#d8b8e0')
        # tele sobre mueble bajo
        PR.box(cc, 3150, 560, 380, HORIZON - 560, '#6a5a7a', depth=0, seed=2011)
        shape(cc, rrect(3180, 300, 330, 220, 10, 0.5, 2012), '#2a2830', size=150)
        cc.drawRect(skia.Rect(3330, 520, 3360, 560), paint('#2a2830', 1))
        # sofá (frente bajo)
        shape(cc, rrect(2400, 470, 700, 300, 40, 0.8, 2013), SOFA, size=250)
        shape(cc, rrect(2380, 420, 120, 360, 40, 0.8, 2014), shade(SOFA, -0.08), size=100)
        shape(cc, rrect(3000, 420, 120, 360, 40, 0.8, 2015), shade(SOFA, -0.08), size=100)
        for k in range(3):
            shape(cc, ellipse(2560 + k * 220, 440, 110, 70, 1.0, 2016 + k), ['#f29ab4', '#f2c94a', '#8fc1b5'][k], size=100)
        for lx in (2440, 3040):
            cc.drawRect(skia.Rect(lx, 770, lx + 30, 800), paint('#5a4a3a', 1))
        # alfombra
        cc.drawOval(skia.Rect(2300, HORIZON + 30, 3500, HORIZON + 160), paint('#e8b4c8', 0.7))
        cc.drawOval(skia.Rect(2360, HORIZON + 50, 3440, HORIZON + 140), paint('#ffffff', 0.4, stroke=5))
        # espejo de pie, apoyado contra la pared (zona baja visible)
        shape(cc, rrect(3600, 90, 240, HORIZON - 70, 20, 0.6, 2019), '#d8c49a', size=150)
        vgrad_rect(cc, 3620, 110, 200, HORIZON - 110, '#dfeef2', '#b8d0d8')
        line(cc, [(3640, 150), (3700, 260)], '#ffffff', 6, 0.6)
        # ---- pasillo y puerta del baño
        cc.drawRect(skia.Rect(3900, -400, 4380, HORIZON), paint('#9fc0ba', 1))
        PR.door(cc, 3960, 40, 340, HORIZON - 40, color='#f2efe6', open_=0.6)
        for r in range(5):
            for k in range(5):
                x = 3970 + k * 60
                y = 340 + r * 80
                if x < 4260:
                    cc.drawRect(skia.Rect(x, y, x + 56, y + 76), paint('#dfeef2', 0.8))
        # ---- entrada: perchero, zapatero
        PR.door(cc, 4500, 20, 360, HORIZON - 20, color='#c8a87a')
        for k in range(3):
            cc.drawCircle(4950 + k * 80, 160, 12, paint('#5a4a3a', 1))
        shape(cc, blob([(4940, 170), (4910, 420), (5020, 430), (4980, 170)], 1.0, 2020), '#d86a8a', size=80)
        PR.box(cc, 4920, 600, 260, HORIZON - 600, '#c8a87a', seed=2021)
        PR.shoes_row(cc, 4930, 640, 4, 0.8)
    draw_cached(c, 'pov_bg', base)
    if calendar:
        # almanaque de Erfurt en la heladera (catedral)
        shape(c, rrect(1210, -200, 130, 180, 4, 0.5, 2030), '#fbf8f1', size=60, shadow=False, lw=2)
        _dom_icon(c, 1275, -60, 0.35)
        for r in range(3):
            for k in range(5):
                c.drawRect(skia.Rect(1222 + k * 22, -40 + r * 16, 1238 + k * 22, -30 + r * 16), paint('#b8b0a0', 0.8))
    if fridge_photo:
        PR.photo(c, 1240, 210, 120, 90, 1.0, rot=4, content=fridge_photo)
    if mess > 0:
        # objetos sobre la mesa que asoman
        PR.bottle(c, 1560, 380, 0.9)
        PR.bottle(c, 1640, 380, 0.85, '#4a7a3a')
        PR.magazine(c, 1860, 378, 1.0, -2, '#e07a5a')
        PR.magazine(c, 1880, 362, 0.9, 3, '#5a9ad8')
        PR.plate(c, 2120, 376, 0.9)
        PR.bottle(c, 2240, 380, 0.8)
    if bag:
        shape(c, blob([(4600, HORIZON + 10), (4580, HORIZON - 150), (4820, HORIZON - 160), (4840, HORIZON + 10)],
                      1.0, 2031), '#3a4a6a', size=150)
        line(c, [(4620, HORIZON - 150), (4700, HORIZON - 260), (4790, HORIZON - 150)], '#2a3448', 10)
    # luz de la tele / lámpara
    glow(c, 2800, 300, 900, '#fff2d8', 0.25 * light)
    if night > 0:
        c.drawRect(skia.Rect(-600, -400, POV_W + 600, 1500), paint('#203060', 0.5 * night, blend=skia.BlendMode.kMultiply))


def _dom_icon(c, x, y, s=1.0, color='#7a6a8a'):
    """Silueta de la catedral de Erfurt (tres agujas)."""
    with at(c, x, y, s):
        c.drawRect(skia.Rect(-120, -60, 120, 60), paint(color, 1))
        for k, (dx, h) in enumerate(((-80, 200), (0, 260), (80, 200))):
            c.drawRect(skia.Rect(dx - 24, -h + 60, dx + 24, -60), paint(color, 1))
            c.drawPath(poly([(dx - 30, -h + 60), (dx, -h - 40), (dx + 30, -h + 60)]), paint(color, 1))


# ---------------------------------------------------------------- vista objetiva del living de Eva (perfil)
ROOM_W = 3800
ROOM_FLOOR = 860


def room_bg(c, t=0.0, night=0.0, tv=0.0, sunset=0.0, morning=0.0):
    def base(cc):
        vgrad_rect(cc, -600, -300, ROOM_W + 1200, ROOM_FLOOR + 300, E_WALL, E_WALL2)
        for i in range(-6, 50):
            x = i * 100
            cc.drawRect(skia.Rect(x, -300, x + 50, ROOM_FLOOR), paint('#cde6df', 0.35))
        vgrad_rect(cc, -600, ROOM_FLOOR, ROOM_W + 1200, 500, shade(E_FLOOR, 0.05), shade(E_FLOOR, -0.2))
        for i in range(8):
            y = ROOM_FLOOR + 14 + i * 26 + i * i * 2
            cc.drawLine(-600, y, ROOM_W + 600, y, paint(shade(E_FLOOR, -0.3), 0.45, stroke=2))
        cc.drawRect(skia.Rect(-600, ROOM_FLOOR - 20, ROOM_W + 600, ROOM_FLOOR), paint('#f2efe6', 1))
        # cocina a la izquierda
        PR.box(cc, -200, 560, 900, ROOM_FLOOR - 560, E_CAB, depth=40, top='#f2efe6', seed=2101)
        for k in range(4):
            cc.drawRect(skia.Rect(-180 + k * 220, 600, 20 + k * 220, ROOM_FLOOR - 30), paint(INK, 0.35, stroke=2.5))
        PR.box(cc, -200, 100, 900, 220, E_CAB, seed=2102)
        shape(cc, rrect(740, 140, 260, ROOM_FLOOR - 140, 22, 0.6, 2103), '#f4f2ee', size=200)
        cc.drawLine(740, 430, 1000, 430, paint(INK, 0.6, stroke=2.5))
        # mesa con desorden
        PR.box(cc, 1150, 600, 620, 34, '#a8784e', depth=40, seed=2104)
        for lx in (1180, 1720):
            cc.drawRect(skia.Rect(lx, 634, lx + 30, ROOM_FLOOR), paint('#9a6a44', 1))
            cc.drawRect(skia.Rect(lx, 634, lx + 30, ROOM_FLOOR), paint(INK, 0.7, stroke=2))
        for sx in (1100, 1700):
            line(cc, [(sx, 420), (sx + 20, 700), (sx + 20, ROOM_FLOOR)], '#7a5a8a', 14)
            cc.drawRect(skia.Rect(sx - 10, 690, sx + 140 if sx < 1500 else sx + 140, 712), paint('#7a5a8a', 1))
        # ventana grande
        PR.window(cc, 1950, 120, 560, 440, content=_erfurt_window_view, frame='#f4f2ee', curtain='#d8b8e0')
        # sofá
        shape(cc, rrect(2600, 520, 820, 200, 40, 0.8, 2105), shade(SOFA, -0.05), size=200)
        shape(cc, rrect(2620, 650, 780, 170, 40, 0.8, 2106), SOFA, size=200)
        shape(cc, rrect(2560, 560, 120, 270, 40, 0.8, 2107), shade(SOFA, -0.1), size=100)
        shape(cc, rrect(3360, 560, 120, 270, 40, 0.8, 2108), shade(SOFA, -0.1), size=100)
        for k in range(3):
            shape(cc, ellipse(2760 + k * 240, 600, 100, 70, 1.0, 2109 + k), ['#f29ab4', '#f2c94a', '#8fc1b5'][k], size=100)
        # tele de espaldas en el borde derecho
        PR.box(cc, 3560, 560, 260, ROOM_FLOOR - 560, '#6a5a7a', seed=2112)
        shape(cc, rrect(3590, 330, 210, 210, 10, 0.5, 2113), '#2a2830', size=150)
        # planta y lámpara de pie
        PR.plant(cc, 2520, ROOM_FLOOR, 1.0)
        line(cc, [(3520, ROOM_FLOOR), (3520, 300)], '#5a4a3a', 8)
        shape(cc, blob([(3460, 300), (3580, 300), (3550, 220), (3490, 220)], 0.5, 2114), '#f2e2c0', size=80)
        # alfombra
        cc.drawOval(skia.Rect(2400, ROOM_FLOOR + 40, 3600, ROOM_FLOOR + 140), paint('#e8b4c8', 0.75))
    draw_cached(c, 'room_bg', base)
    if tv > 0:
        glow(c, 3690, 430, 400, '#9ad0ff', 0.35 * tv * (0.8 + 0.2 * math.sin(t * 7)))
    glow(c, 3520, 260, 380, '#ffe6b0', 0.3)
    if sunset > 0:
        c.drawRect(skia.Rect(-600, -300, ROOM_W + 600, 1400), paint('#ff8a5a', 0.18 * sunset, blend=skia.BlendMode.kMultiply))
        glow(c, 2230, 340, 700, '#ff9a6a', 0.35 * sunset)
    if morning > 0:
        glow(c, 2230, 340, 800, '#fff2c8', 0.4 * morning)
    if night > 0:
        c.drawRect(skia.Rect(-600, -300, ROOM_W + 600, 1400), paint('#203060', 0.55 * night, blend=skia.BlendMode.kMultiply))


def _erfurt_window_view(c, w, h):
    vgrad_rect(c, 0, 0, w, h, '#a8c8e8', '#efd8c8')
    for i in range(8):
        bx = i * 80 - 20
        bh = 100 + rnd(2120, i) * 140
        c.drawRect(skia.Rect(bx, h - bh, bx + 74, h), paint(['#e8c8a8', '#d8b098', '#f0dcc4'][i % 3], 1))
        c.drawPath(poly([(bx - 6, h - bh), (bx + 37, h - bh - 50), (bx + 80, h - bh)]), paint('#b8584a', 1))
    _dom_icon(c, w * 0.7, h * 0.45, 0.4, '#8a7a9a')


# ---------------------------------------------------------------- panorama de Erfurt al atardecer
def erfurt_panorama(c, t=0.0):
    def base(cc):
        vgrad_rect(cc, -600, -400, 3200, 1500, '#c84a4a', '#f6b86a', mid='#ec7a52')
        glow(cc, 1500, 640, 900, '#ffd08a', 0.6)
        cc.drawCircle(1500, 620, 110, paint('#ffe6a8', 1))
        # colinas lejanas
        cc.drawPath(blob([(-600, 640), (200, 560), (900, 610), (1700, 570), (2600, 620), (2600, 900), (-600, 900)], 4, 2201),
                    paint('#a8506a', 0.7))
        # techos de la ciudad (tejas rojas)
        for r in range(4):
            y0 = 650 + r * 110
            for i in range(26):
                x = -600 + i * 130 + (r % 2) * 60
                w = 110 + rnd(2202, i + r * 40) * 50
                h = 80 + rnd(2203, i + r * 40) * 70
                col_ = cmix('#c25a48', '#e8a07a', rnd(2204, i + r * 40) * 0.5)
                cc.drawRect(skia.Rect(x, y0 - h * 0.4, x + w, y0 + 120), paint(cmix('#e8c4a0', '#b88a7a', r * 0.15), 1))
                cc.drawPath(poly([(x - 10, y0 - h * 0.4), (x + w / 2, y0 - h), (x + w + 10, y0 - h * 0.4)]), paint(col_, 1))
                cc.drawPath(poly([(x - 10, y0 - h * 0.4), (x + w / 2, y0 - h), (x + w + 10, y0 - h * 0.4)]),
                            paint(INK, 0.4, stroke=1.6))
                for k in range(2):
                    if rnd(2205, i * 3 + k + r * 50) > 0.5:
                        cc.drawRect(skia.Rect(x + 20 + k * 40, y0 - 10, x + 36 + k * 40, y0 + 12), paint('#ffd994', 0.8))
            # cúpulas y agujas de iglesias
        for (x, y, s) in ((300, 600, 1.0), (1150, 560, 1.3), (2100, 610, 0.9)):
            _dom_icon(cc, x, y, s * 0.9, '#6a3a4a')
        for (x, y) in ((700, 620), (1700, 600)):
            cc.drawRect(skia.Rect(x - 40, y - 120, x + 40, y + 40), paint('#6a3a4a', 1))
            cc.drawOval(skia.Rect(x - 60, y - 200, x + 60, y - 90), paint('#5a7a6a', 1))
            line(cc, [(x, y - 200), (x, y - 250)], '#5a7a6a', 6)
        # canal con el puente de las casas
        cc.drawPath(blob([(-600, 1000), (600, 960), (1400, 990), (2600, 950), (2600, 1110), (-600, 1110)], 3, 2206),
                    paint('#e8885a', 1))
        vgrad_rect(cc, -600, 1100, 3200, 700, '#e8885a', '#b8584a')
        for i in range(12):
            x = -600 + i * 280
            cc.drawRect(skia.Rect(x, 1160, x + 240, 1800), paint('#9a4a4a', 1))
            cc.drawPath(poly([(x - 20, 1160), (x + 120, 1080), (x + 260, 1160)]), paint('#7a3a3a', 1))
            for k in range(3):
                cc.drawRect(skia.Rect(x + 30 + k * 70, 1200, x + 60 + k * 70, 1240), paint('#ffd994', 0.7))
        for i in range(8):
            y = 975 + i * 16
            line(cc, [(-600, y), (2600, y - 20)], '#ffd0a0', 3, 0.5)
        cc.drawRect(skia.Rect(700, 900, 1500, 990), paint('#a86a5a', 1))
        for k in range(6):
            cc.drawArc(skia.Rect(720 + k * 130, 950, 820 + k * 130, 1040), 180, 180, False, paint('#5a3a3a', 1, stroke=6))
            cc.drawRect(skia.Rect(720 + k * 130, 840, 820 + k * 130, 905), paint('#e8c4a0', 1))
            cc.drawPath(poly([(712 + k * 130, 845), (770 + k * 130, 800), (828 + k * 130, 845)]), paint('#c25a48', 1))
        # calle ancha
        cc.drawPath(poly([(1700, 1110), (2600, 1060), (2600, 1110)]), paint('#d89a7a', 1))
    draw_cached(c, 'erfurt_pan', base)
    # pájaros
    for i in range(6):
        x = 200 + i * 160 + t * 60
        y = 300 + math.sin(t + i) * 30 + i * 18
        f = math.sin(t * 6 + i)
        line(c, [(x - 20, y + f * 8), (x, y), (x + 20, y + f * 8)], '#5a2a3a', 4)


# ---------------------------------------------------------------- bañera (vista desde adentro)
def bathtub_pov(c, t=0.0, light=1.0):
    vgrad_rect(c, -200, -200, W + 400, H + 400, '#dfeef2', '#c8dde4')
    for r in range(8):
        for k in range(14):
            c.drawRect(skia.Rect(k * 150 - 100, r * 150 - 200, k * 150 + 46, r * 150 - 54), paint('#ffffff', 0.5))
    glow(c, W / 2, 0, 600, '#fffbe8', 0.5 * light)
    tub = blob([(-200, 420), (300, 360), (960, 340), (1620, 360), (2120, 420), (2120, 1300), (-200, 1300)], 3, 2301)
    shape(c, tub, '#f6f6f2', size=900, shadow_a=0.35)
    c.drawPath(smooth_path([(-200, 430), (960, 350), (2120, 430)], closed=False), paint('#ffffff', 0.9, stroke=30))
    c.drawPath(smooth_path([(-200, 430), (960, 350), (2120, 430)], closed=False), paint(INK, 0.6, stroke=3))
    c.drawCircle(960, 1000, 40, paint('#a9b4bc', 1))
    c.drawCircle(960, 1000, 40, paint(INK, 0.7, stroke=3))


def eva_closeup_bg(c, t=0.0, warm=0.0):
    """Fondo desenfocado para primeros planos de Eva (vista alzada)."""
    vgrad_rect(c, -400, -400, W + 800, H + 800, cmix(E_WALL, '#f3d6c0', warm), cmix(E_WALL2, '#e8c0b0', warm))
    c.drawRect(skia.Rect(1250, 120, 1750, 560), paint('#e8f2fa', 0.75, blur=24))
    c.drawRect(skia.Rect(1250, 120, 1750, 560), paint('#ffffff', 0.4, blur=24, stroke=30))
    c.drawOval(skia.Rect(150, 600, 650, 900), paint(SOFA, 0.5, blur=30))
    c.drawOval(skia.Rect(300, 150, 600, 350), paint('#f2c94a', 0.4, blur=30))
