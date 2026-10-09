"""S01 — Lima: apertura sobre los acantilados y la ventana de Emilia."""
from scenes.common import *


def draw(c, t):
    p = ease_io(clamp(t / 10.0))
    # capa lejana: cielo
    with U.cam(c, 960, lerp(380, 620, p), 1.0):
        L.lima_sky(c, t)
    # capa media: mar, acantilados, ciudad (paralaje)
    with U.cam(c, lerp(900, 1150, p), lerp(800, 1150, p), lerp(0.86, 1.1, p)):
        L.lima_sea_cliffs(c, t)
        L.lima_city(c, t)
    L.pelicans(c, t, -300, 260, n=6, speed=120, s=0.9)
    # capa cercana: el edificio de Emilia sube desde abajo
    q = ease_io(clamp((t - 1.5) / 8.5))
    lit = prog(t, 5.6, 6.6, smooth)
    with U.cam(c, lerp(1250, 1380, q), lerp(250, 1930, q), lerp(0.55, 1.45, q)):
        L.lima_facade(c, t, lit=lit)
    label(c, t, 'Lima, Perú', 1.6, 4.4)
