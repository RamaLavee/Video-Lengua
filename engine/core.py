"""Núcleo: constantes, interpolación, easing, ruido y colores."""
import math
import functools
import skia

W, H = 1920, 1080
FPS = 24


# ---------------------------------------------------------------- matemática
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    if isinstance(a, (tuple, list)):
        return tuple(lerp(x, y, t) for x, y in zip(a, b))
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_io(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_sine(t):
    t = clamp(t)
    return -(math.cos(math.pi * t) - 1) / 2


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t * t * t


def ease_back(t):
    t = clamp(t)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def linear(t):
    return clamp(t)


def prog(t, a, b, ease=ease_io):
    """Progreso 0..1 entre los tiempos a y b, con easing."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return ease((t - a) / (b - a))


def kf(t, keys, ease=ease_io):
    """Interpola una lista de claves [(tiempo, valor), ...]."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, prog(t, t0, t1, ease))
    return keys[-1][1]


def pulse(t, a, b, fade=0.3):
    """1 dentro de [a,b] con rampas suaves, 0 fuera."""
    return prog(t, a, a + fade, smooth) * (1 - prog(t, b - fade, b, smooth))


def bump(t, center, width):
    """Campana suave centrada en center."""
    x = (t - center) / max(width, 1e-6)
    return math.exp(-x * x * 4)


# ---------------------------------------------------------------- ruido
def _hash(i, seed):
    n = (i * 374761393 + seed * 668265263) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFF) / 32767.5 - 1.0


def noise1(x, seed=0):
    """Ruido de valor 1D suave en [-1, 1]."""
    i = math.floor(x)
    f = x - i
    u = f * f * (3 - 2 * f)
    return _hash(i, seed) * (1 - u) + _hash(i + 1, seed) * u


def fbm(x, seed=0, octaves=2):
    v, a, s = 0.0, 1.0, 0.0
    for o in range(octaves):
        v += a * noise1(x * (2 ** o), seed + o * 31)
        s += a
        a *= 0.5
    return v / s


def wob(t, seed, freq=0.5, amp=1.0):
    return noise1(t * freq, seed) * amp


def rnd(seed, i=0):
    """Pseudoaleatorio determinista en [0,1)."""
    return (_hash(i, seed) + 1) / 2


def blink(t, seed=0, period=3.6, dur=0.16):
    """Devuelve apertura de ojos (1 abierto, 0 cerrado) con parpadeos naturales."""
    k = math.floor(t / period)
    off = rnd(seed, k) * (period - dur - 0.2)
    local = t - k * period - off
    if 0 <= local <= dur:
        x = local / dur
        return abs(2 * x - 1) ** 0.7
    # doble parpadeo ocasional
    if rnd(seed + 7, k) > 0.75:
        local2 = local - dur - 0.12
        if 0 <= local2 <= dur:
            x = local2 / dur
            return abs(2 * x - 1) ** 0.7
    return 1.0


# ---------------------------------------------------------------- color
@functools.lru_cache(maxsize=4096)
def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_rgb(c):
    if isinstance(c, str):
        return hexrgb(c)
    return tuple(c[:3])


def cmix(a, b, t):
    a, b = to_rgb(a), to_rgb(b)
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def shade(c, k):
    """k<0 oscurece, k>0 aclara (hacia blanco cálido)."""
    c = to_rgb(c)
    if k < 0:
        dark = (0.18, 0.12, 0.16)
        return cmix(c, dark, -k)
    return cmix(c, (1.0, 0.98, 0.94), k)


def col(c, a=1.0):
    r, g, b = to_rgb(c)
    return skia.Color4f(r, g, b, a).toColor()


def col4(c, a=1.0):
    r, g, b = to_rgb(c)
    return skia.Color4f(r, g, b, a)
