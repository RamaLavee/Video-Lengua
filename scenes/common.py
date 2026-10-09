"""Elementos compartidos por las escenas: elenco, planos recurrentes y utilidades."""
import math
import skia
from engine.core import (W, H, clamp, lerp, smooth, ease_io, ease_out, ease_in, ease_back, linear, prog, kf, pulse, bump,
                         noise1, rnd, blink, shade, cmix, col)
from engine.draw import (INK, paint, layer, clip, glow, grade_filter, tint_filter, vgrad_rect, line, shape, ellipse,
                         rrect, blob, poly, at)
from engine import people as P, rabbit as R, props as PR, ui as U, fx
from engine import sets_lima as L, sets_erfurt as E

# ---------------------------------------------------------------- elenco
EMI = P.Person(P.EMILIA)
EMI_N = P.Person(P.EMILIA_NIGHT)
EMI_R = P.Person(P.EMILIA_ROBE)
EVA = P.Person(P.EVA)
EVA_W = P.Person(P.EVA_WET)
EVA_T = P.Person(P.EVA_TOWEL)
KLAUS = P.Person(P.KLAUS)
KLAUS_B = P.Person(P.KLAUS_BARE)
KLAUS_U = P.Person(P.KLAUS_UNDER)
GLORIA = P.Person(P.GLORIA)
INES = P.Person(P.INES)
SON = P.Person(P.SON)
BOOTS = P.Person(P.BOOTS_WOMAN)

# gradaciones de color por lugar y por tensión dramática
WARM = grade_filter(sat=1.02, tint=(1.03, 1.0, 0.95))
COOL = grade_filter(sat=0.95, tint=(0.95, 1.0, 1.05))
NIGHT = grade_filter(sat=0.8, bright=0.82, tint=(0.88, 0.95, 1.12))
TENSE = grade_filter(sat=0.72, bright=0.95, tint=(0.93, 0.98, 1.08))
COLD = grade_filter(sat=0.55, bright=0.9, tint=(0.9, 0.97, 1.1))


def talk(t, t0=0.0, t1=99.0, rate=11.0, amt=0.55):
    """Apertura de boca al hablar (sin audio de voz)."""
    if t < t0 or t > t1:
        return 0.0
    v = (math.sin(t * rate) * 0.5 + 0.5) * (0.6 + 0.4 * math.sin(t * rate * 0.37 + 1.3))
    return v * amt * pulse(t, t0, t1, 0.15)


def eyes(t, seed=0, closed=None):
    b = blink(t, seed)
    if closed is not None:
        b = min(b, 1 - closed)
    return b


# ---------------------------------------------------------------- Emilia en el escritorio (perfil)
EX, EY, ES = 965, 880, 0.7           # pies de Emilia y escala en el plano de perfil
CHAIR_X, CHAIR_S = 985, 0.36
SEAT_H = 440 * CHAIR_S / ES


def loc(xw, yw):
    """Coordenadas de mundo -> locales de Emilia en el plano de perfil."""
    return ((xw - EX) / ES, (yw - EY) / ES)


def hand_preset(name, t=0.0, side='L'):
    """Objetivos de mano (en mundo) para el plano de perfil."""
    tap = math.sin(t * 18) * 3
    kx, ky, kw = L.KEYB
    if name == 'key':
        return (kx + kw * (0.42 if side == 'L' else 0.3), ky + 6 + (tap if side == 'L' else 0))
    if name == 'type':
        return (kx + kw * (0.45 + 0.08 * math.sin(t * 3.1)), ky + 2 - abs(math.sin(t * 13)) * 12)
    if name == 'arrow':
        return (kx + kw * 0.86, ky + 14 + tap * 0.5)
    if name == 'mouse':
        return (1345, 618)
    if name == 'lap':
        return (EX + 120, 700 - (0 if side == 'L' else 6))
    if name == 'chest':
        return (EX + 38, 590)
    if name == 'mouth':
        return (EX + 78, 506)
    if name == 'collar':
        return (EX + 48, 560 + (10 if side == 'R' else 0))
    if name == 'ear':
        return (EX + 22, 478)
    if name == 'back':
        return (EX - 52, 690)
    if name == 'glasses':
        return (EX + 66, 462)
    if name == 'face':
        return (EX + 72, 480 + (10 if side == 'R' else -10))
    if name == 'phone_desk':
        return (1120, 630)
    if name == 'power':
        return (1660, 590)
    if name == 'card':
        return (EX + 165, 525)
    if name == 'cup':
        return (1420, 600)
    if name == 'backrest':
        return (EX - 30, 650)
    if name == 'up':
        return (EX + 140, 430)
    return name


def emi_desk(c, t, who=None, expr='neutral', hl='key', hr='key', look=(0.6, 0.0), head_rot=0.0, lean=0.0,
             screen=None, on=1.0, pressed=None, night=0.0, lamp=1.0, creak=0.0, cup=True, cup_spill=0.0,
             phone_fn=None, blush=0.0, eyes_closed=None, talk_amt=0.0, nod=0.0, hold_l=None, hold_r=None,
             handshape_l='fist', handshape_r='fist', extra_front=None, extra_desk=None, clock_hm=(5, 55),
             glow_a=1.0, emix=None, mouse=True, under_desk=None):
    """Plano de perfil: Emilia en la silla de mimbre frente a la computadora vieja.

    Se dibuja en dos pasadas: el cuerpo queda detrás de la tapa del escritorio (rodillas debajo) y los
    antebrazos y manos se vuelven a dibujar por encima del teclado."""
    who = who or EMI
    L.hall_bg(c, clock_hm=clock_hm, night=night)
    r = L.desk_back(c, t, screen_fn=screen, on=on, lamp_on=lamp, glow_a=glow_a)
    PR.wicker_chair(c, CHAIR_X, 880, CHAIR_S, back_only=True, creak=creak)
    PR.wicker_chair(c, CHAIR_X, 880, CHAIR_S, seat_only=True, creak=creak)
    pose = dict(sit=1, seat_h=SEAT_H, knee_x=230, foot_dx=14, expr=expr, look=look, head_rot=head_rot, lean=lean,
                eyes=eyes(t, 3, eyes_closed), blush=blush, talk=talk_amt, nod=nod,
                handshape_L=handshape_l, handshape_R=handshape_r, hold_L=hold_l, hold_R=hold_r)
    if emix:
        pose['expr2'], pose['emix'] = emix
    for key, h in (('hand_L', hl), ('hand_R', hr)):
        tgt = hand_preset(h, t, key[-1]) if isinstance(h, str) else h
        if tgt is not None:
            pose[key] = loc(*tgt)
    who.draw(c, EX, EY, ES, view='side', t=t, **dict(pose))
    if under_desk:
        under_desk(c)
    L.desk_front(c, t, pressed=pressed, mouse=mouse)
    if cup:
        PR.teacup(c, 1440, 632, 0.72, t, steam=0.8 if on else 0.4, spill=cup_spill)
    if extra_desk:
        extra_desk(c)
    # segunda pasada: antebrazos y manos sobre el escritorio
    with clip(c, (L.DESK_X0 - 6, -2000, 4000, L.DESK_TOP + 4)):
        who.draw(c, EX, EY, ES, view='side', t=t, **dict(pose))
    if extra_front:
        extra_front(c)
    if night > 0 and on > 0:
        glow(c, EX + 120, EY - 500, 280, '#a8ccff', 0.3 * night * on * glow_a)
    return r


# ---------------------------------------------------------------- contraplano desde la pantalla
FX_, FY_, FS_ = 960, 1540, 1.45


def emi_front(c, t, who=None, expr='neutral', hl=None, hr=None, look=(0.0, 0.0), head_rot=0.0, turn=0.0,
              night=0.0, screen_light=1.0, screen_col='#bcd8ff', typing=0.0, blush=0.0, eyes_closed=None,
              talk_amt=0.0, nod=0.0, lean=0.0, handshape_l='open', handshape_r='open', hold_l=None, hold_r=None,
              red=0.0, dy=0.0, emix=None, chair=True, desk=True, face=None, front_l=True, front_r=True, **kw):
    """Primer plano de Emilia visto desde el monitor (la cámara del espectador es la pantalla)."""
    who = who or EMI
    L.screen_cam_bg(c, night=night)
    if chair:
        PR.wicker_chair_front(c, 960, 860 + dy, 1.4)
    pose = dict(expr=expr, look=look, head_rot=head_rot, turn=turn, bust=True, eyes=eyes(t, 5, eyes_closed),
                blush=blush, talk=talk_amt, nod=nod, lean=lean, handshape_L=handshape_l, handshape_R=handshape_r,
                hold_L=hold_l, hold_R=hold_r, idle=1.0, front_L=front_l, front_R=front_r)
    pose.update(kw)
    if face:
        pose['face'] = face
    if emix:
        pose['expr2'], pose['emix'] = emix
    hl = hl if hl is not None else (165, -455 + math.sin(t * 15) * 6 * typing)
    hr = hr if hr is not None else (-165, -455 + math.sin(t * 15 + 2) * 6 * typing)
    if hl:
        pose['hand_L'] = hl
    if hr:
        pose['hand_R'] = hr
    who.draw(c, FX_, FY_ + dy, FS_, view='front', t=t, **pose)
    if desk:
        L.desk_edge_cam(c, t, typing=typing)
    if screen_light > 0:
        with layer(c, 1.0, blend=skia.BlendMode.kScreen):
            glow(c, 960, 520 + dy, 620, screen_col, 0.3 * screen_light, blend=None)
    if red > 0:
        c.drawRect(skia.Rect(0, 0, W, H), paint('#ff2a2a', 0.22 * red, blend=skia.BlendMode.kMultiply))
        glow(c, 960, 500, 700, '#ff4a4a', 0.25 * red)


# ---------------------------------------------------------------- vista del kentuki en lo de Eva
def pov_feed(t, cx, cy=540, zoom=1.0, extra=None, under=None, **bgkw):
    """Devuelve una función que dibuja el departamento de Eva visto desde el kentuki."""
    def feed(c):
        with U.cam(c, cx, cy, zoom):
            E.pov_bg(c, t, **bgkw)
            if extra:
                extra(c)
    return feed


def screen_of(feed, t, hud_kw=None, tilt=0.0, zoom=1.0, wet=0.0, dark=0.0, sub=None, shake=0.0, center=None):
    """Contenido de la pantalla de Emilia (vista del kentuki + controlador) en coords 1920x1080."""
    def fn(c):
        U.pov(c, t, feed, tilt=tilt, zoom=zoom, hud_kw=hud_kw, wet=wet, dark=dark, shake=shake, center=center)
        if sub:
            U.subtitle(c, t, *sub)
    return fn


def hands_over(c, person, scale, keys=('L', 'R')):
    """Redibuja las manos de un personaje encima de un objeto que sostiene."""
    r = person.s['hand_r'] * scale
    for k in keys:
        if k in person.hands_world:
            x, y = person.hands_world[k]
            shape(c, ellipse(x, y, r, r * 1.05, 0.4, 21), person.s['skin'], shadow=False, lw=2.6)


def head_at(person, s, hy):
    """Y de los pies para que el centro de la cabeza quede en hy (planos de busto)."""
    return hy + (person.s['height'] - person.s['head'][1]) * s


def sleeping(c, who, x, y, s, t, blanket='#9a7ab8', eyes_open=0.0, expr='closed'):
    """Persona acostada boca arriba (perfil), con la frazada por encima."""
    with at(c, x, y, 1.0, rot=-90):
        who.draw(c, 0, 0, s, view='side', t=t, expr=expr, eyes=eyes_open, bust=True, idle=0.3, shadow=False)


def label(c, t, text, t0, dur=3.6, x=110, y=950, size=64, light=True):
    fx.place_label(c, t, text, None, t0, dur, x, y, size, light)
