"""Banda sonora del cortometraje: música instrumental y efectos ambientales sintetizados.

Todo el audio se genera por síntesis (sin muestras externas, sin voces). La mezcla queda a volumen
bajo para acompañar una exposición oral. Salida: build/audio.wav (48 kHz, estéreo, 16 bits).

Uso: python3 scripts/audio.py
"""
import os
import sys
import math
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scenes.meta import timeline, TOTAL  # noqa: E402

SR = 48000
N = int((TOTAL + 0.5) * SR)
RNG = np.random.default_rng(1234)
TL = {s['id']: s for s in timeline()}


def T(sid, t):
    """Tiempo global de un instante local de escena."""
    return TL[sid]['start'] + t


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def env_adsr(n, a, d, s, r, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    e = np.ones(n) * s
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a, endpoint=False) if a > 0 else e[:a]
    d2 = min(d, n - a)
    if d2 > 0:
        e[a:a + d2] = np.linspace(1, s, d2)
    if r > 0 and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


class Track:
    def __init__(self):
        self.L = np.zeros(N)
        self.R = np.zeros(N)

    def add(self, t, mono, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N or len(mono) == 0:
            return
        if i < 0:
            mono = mono[-i:]
            i = 0
        n = min(len(mono), N - i)
        gl = math.cos((pan + 1) * math.pi / 4) * gain
        gr = math.sin((pan + 1) * math.pi / 4) * gain
        self.L[i:i + n] += mono[:n] * gl
        self.R[i:i + n] += mono[:n] * gr

    def add_st(self, t, l, r, gain=1.0):
        i = int(t * SR)
        if i >= N:
            return
        n = min(len(l), N - i)
        self.L[i:i + n] += l[:n] * gain
        self.R[i:i + n] += r[:n] * gain


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc / (SR / 2), 0.99), 'low')
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, max(fc / (SR / 2), 1e-4), 'high')
    return signal.lfilter(b, a, x)


def bp(x, f0, f1, order=2):
    b, a = signal.butter(order, [f0 / (SR / 2), min(f1 / (SR / 2), 0.99)], 'band')
    return signal.lfilter(b, a, x)


def noise(dur):
    return RNG.standard_normal(int(dur * SR))


def pink(dur):
    w = noise(dur)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w) * 3.0


def reverb_ir(dur=2.2, decay=3.2, seed=0, bright=4000):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    tt = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-tt * decay)
    ir = lp(ir, bright)
    ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))


def apply_reverb(track, wet=0.3, dur=2.2, decay=3.2, bright=4000):
    irL = reverb_ir(dur, decay, 11, bright)
    irR = reverb_ir(dur, decay, 12, bright)
    wl = signal.fftconvolve(track.L, irL)[:N]
    wr = signal.fftconvolve(track.R, irR)[:N]
    track.L = track.L * (1 - wet * 0.4) + wl * wet
    track.R = track.R * (1 - wet * 0.4) + wr * wet


# ---------------------------------------------------------------- instrumentos
def piano(f, dur, vel=0.6):
    """Piano de fieltro por síntesis aditiva con leve inarmonicidad."""
    rel = 0.35
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    B = 0.00035
    for k in range(1, 9):
        fk = f * k * math.sqrt(1 + B * k * k)
        if fk > SR / 2.2:
            break
        amp = (1.0 / k ** 1.6) * (0.9 if k > 1 else 1.0)
        tau = 1.8 / (1 + 0.55 * k) * (440.0 / f) ** 0.25
        out += amp * np.sin(2 * np.pi * fk * t + k * 0.3) * np.exp(-t / tau)
    att = int(0.006 * SR)
    out[:att] *= np.linspace(0, 1, att)
    off = int(dur * SR)
    if off < n:
        out[off:] *= np.linspace(1, 0, n - off) ** 2
    out = lp(out, 2600 + vel * 2500)
    return out * vel * 0.25


def musicbox(f, vel=0.5):
    """Caja de música: modos de barra libre (1, 2.756, 5.404, 8.933)."""
    n = int(2.6 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a, tau in ((1.0, 1.0, 1.6), (2.756, 0.32, 0.5), (5.404, 0.16, 0.18), (8.933, 0.07, 0.08)):
        if f * r < SR / 2.2:
            out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau)
    out[:int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
    return out * vel * 0.2


def pad(freqs, dur, vel=0.4, bright=1400, attack=1.6, release=2.2, detune=0.004):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for d in (-detune, 0, detune):
            ph = RNG.random() * 2 * np.pi
            # triángulo suave
            out += signal.sawtooth(2 * np.pi * f * (1 + d) * t + ph, 0.5) * 0.33
    out = lp(out, bright, 2)
    e = env_adsr(n, attack, 0.5, 0.85, release)
    return out * e * vel * 0.12 / max(1, len(freqs) ** 0.5)


def pluck(f, dur=0.6, vel=0.5, damp=0.996):
    """Cuerda pulsada (Karplus-Strong vía filtro IIR)."""
    Np = max(2, int(SR / f))
    n = int(dur * SR)
    x = np.zeros(n)
    x[:Np] = RNG.uniform(-1, 1, Np)
    a = np.zeros(Np + 2)
    a[0] = 1.0
    a[Np] = -0.5 * damp
    a[Np + 1] = -0.5 * damp
    y = signal.lfilter([1.0], a, x)
    y *= np.linspace(1, 0, n) ** 0.5
    return lp(y, 3000) * vel * 0.3


def drone(f, dur, vel=0.3, attack=2.5, release=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    lfo = 1 + 0.15 * np.sin(2 * np.pi * 0.17 * t)
    out = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.003 * t) + 0.2 * np.sin(2 * np.pi * f * 3.01 * t))
    out *= lfo
    out += lp(noise(dur), f * 3) * 0.15
    return out * env_adsr(n, attack, 0.5, 1.0, release) * vel * 0.18


def heartbeat(vel=0.5):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for t0, a in ((0.0, 1.0), (0.18, 0.7)):
        tt = np.clip(t - t0, 0, None)
        f = 55 * np.exp(-tt * 6) + 40
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += a * np.sin(ph) * np.exp(-tt * 18) * (t >= t0)
    return out * vel * 0.6


def bell(f, vel=0.4, dur=4.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a, tau in ((0.5, 0.6, 2.5), (1.0, 1.0, 1.8), (1.19, 0.5, 1.2), (1.56, 0.35, 0.9), (2.0, 0.3, 0.7),
                      (2.51, 0.2, 0.5), (3.01, 0.12, 0.4)):
        out += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau)
    out[:int(0.003 * SR)] *= np.linspace(0, 1, int(0.003 * SR))
    return out * vel * 0.12


# ---------------------------------------------------------------- efectos
def click(vel=0.5, f0=2500, f1=6000, dur=0.012):
    x = bp(noise(dur), f0, f1) * np.exp(-np.arange(int(dur * SR)) / SR * 400)
    return x * vel * 0.5


def chirp_s(vel=0.5):
    """Chillido del kentuki: dos barridos agudos breves."""
    out = []
    for f0, f1, d in ((1500, 2600, 0.09), (1800, 2900, 0.11)):
        n = int(d * SR)
        f = np.linspace(f0, f1, n)
        ph = 2 * np.pi * np.cumsum(f) / SR
        out.append(np.sin(ph) * np.hanning(n))
        out.append(np.zeros(int(0.04 * SR)))
    return np.concatenate(out) * vel * 0.35


def purr(dur, vel=0.4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 24 * t)
    x = lp(noise(dur), 300) * am + 0.3 * np.sin(2 * np.pi * 95 * t) * am
    return x * env_adsr(n, 0.15, 0.1, 1, 0.3) * vel * 0.5


def whir(dur, vel=0.4, f=180):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) * 0.4 + np.sin(2 * np.pi * f * 2 * t) * 0.2 + bp(noise(dur), 800, 2400) * 0.3
    return x * env_adsr(n, 0.05, 0.05, 1, 0.1) * vel * 0.3


def vibrate(dur, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    gate = (np.sin(2 * np.pi * 1.6 * t) > -0.2).astype(float)
    gate = lp(gate, 30)
    x = signal.square(2 * np.pi * 170 * t) * 0.5
    return lp(x, 900) * gate * vel * 0.25


def chimes(vel=0.5):
    """«Campanitas chinas» del teléfono (pentatónica)."""
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate((84, 88, 91, 96)):
        b = bell(mtof(m), 1.0, 1.4)
        j = int(i * 0.09 * SR)
        out[j:j + len(b)] += b[:len(out) - j]
    return out * vel


def water(dur, vel=0.5, bright=3000):
    x = bp(noise(dur), 300, bright) + 0.5 * lp(noise(dur), 300)
    n = len(x)
    return x * env_adsr(n, 0.2, 0.1, 1, 0.4) * vel * 0.18


def crinkle(dur, vel=0.5):
    n = int(dur * SR)
    x = hp(noise(dur), 3000)
    gate = (RNG.random(n) > 0.997).astype(float)
    gate = signal.lfilter([1], [1, -0.995], gate)
    return x * np.clip(gate, 0, 1) * vel * 0.35


def doorbell(vel=0.5):
    a = bell(mtof(76), 1.0, 1.5)
    b = bell(mtof(72), 1.0, 2.0)
    out = np.zeros(int(2.4 * SR))
    out[:len(a)] += a
    j = int(0.5 * SR)
    out[j:j + len(b)] += b[:len(out) - j]
    return out * vel * 1.6


def creak(dur, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 260 + 60 * np.cumsum(RNG.standard_normal(n)) / np.sqrt(n) * 3
    ph = 2 * np.pi * np.cumsum(np.clip(f, 120, 500)) / SR
    gate = (RNG.random(n) > 0.6).astype(float)
    x = signal.sawtooth(ph) * lp(gate, 200)
    return bp(x, 300, 2500) * env_adsr(n, 0.05, 0.1, 1, 0.2) * vel * 0.25


def thump(vel=0.5, f=70):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    ff = f * np.exp(-t * 4) + f * 0.5
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 14) * vel * 0.5


def tone(f, dur, vel=0.3, attack=0.02, release=0.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * env_adsr(n, attack, 0.05, 1, release) * vel * 0.3


def swell(dur, vel=0.3, f0=200, f1=1600):
    x = bp(noise(dur), f0, f1)
    return x * env_adsr(len(x), dur * 0.6, 0.1, 1, dur * 0.35) * vel * 0.2


def frying(dur, vel=0.4):
    n = int(dur * SR)
    crack = (RNG.random(n) > 0.995).astype(float)
    crack = signal.lfilter([1], [1, -0.97], crack)
    return (hp(noise(dur), 2500) * 0.15 + hp(crack * noise(dur), 1500)) * vel * 0.3


# ---------------------------------------------------------------- música
F_CHORDS = [(53, [65, 69, 72]), (50, [62, 65, 69]), (46, [58, 62, 65]), (48, [60, 64, 67])]   # F Dm Bb C
THEME = [(69, 1), (72, 1), (77, 1), (76, 1), (74, 1), (72, 1), (69, 2),
         (70, 1), (74, 1), (79, 1), (77, 1), (76, 1), (72, 1), (None, 2),
         (69, 1), (72, 1), (77, 1), (81, 1), (79, 1), (77, 1), (76, 1), (74, 1),
         (72, 1), (69, 1), (70, 1), (67, 1), (65, 4)]


def play_theme(mus, t0, beat, inst='box', vel=0.5, octave=12, n_notes=None, detune=0.0, slow=0.0, pan=0.2):
    t = t0
    notes = THEME if n_notes is None else THEME[:n_notes]
    for i, (m, d) in enumerate(notes):
        b = beat * (1 + slow * i / max(1, len(notes)))
        if m is not None:
            f = mtof(m + octave) * (1 + detune * math.sin(i * 1.7))
            snd = musicbox(f, vel) if inst == 'box' else piano(f, d * b * 0.9, vel)
            mus.add(t, snd, 1.0, pan)
        t += d * b
    return t


def arps(mus, t0, t1, beat, chords=F_CHORDS, vel=0.35, octave=0, pattern=(0, 1, 2, 1), bass=True):
    t = t0
    k = 0
    while t < t1 - 0.05:
        root, triad = chords[k % len(chords)]
        if bass:
            mus.add(t, piano(mtof(root - 12 + octave), beat * 3.6, vel * 0.9), 1.0, -0.2)
        for j, idx in enumerate(pattern):
            tt = t + j * beat
            if tt < t1:
                mus.add(tt, piano(mtof(triad[idx] + octave), beat * 1.6, vel * (0.75 + 0.1 * (j == 0))), 1.0,
                        0.15 * (idx - 1))
        t += beat * len(pattern)
        k += 1


def build_music():
    mus = Track()
    beat = 60 / 84.0
    # --- Lima y el comienzo de la conexión (cálido, Fa mayor)
    s10 = TL['s10']['start']
    arps(mus, 0.8, TL['s09']['start'] + 3.0, beat, vel=0.3)
    mus.add(0.3, pad([mtof(53), mtof(60), mtof(65)], 12, 0.35), 1.0)
    play_theme(mus, T('s02', 1.0), beat, 'box', 0.45)
    # entrada en la pantalla: brillo
    mus.add(T('s03', 2.6), pad([mtof(77), mtof(81), mtof(84)], 3.0, 0.3, bright=4000, attack=0.6, release=2.0), 1.0)
    # juego: punteos en contratiempo
    for i in range(14):
        tt = T('s04', 0.4) + i * beat * 2 + beat
        mus.add(tt, pluck(mtof([72, 77, 76, 74][i % 4]), 0.5, 0.35), 1.0, 0.4)
    # la ventana: el tema completo, más pleno
    mus.add(T('s06', 2.5), pad([mtof(53), mtof(57), mtof(60), mtof(65)], 9.0, 0.55, bright=2200), 1.0)
    play_theme(mus, T('s06', 3.0), beat * 0.9, 'piano', 0.42, 12, n_notes=14, pan=-0.1)
    play_theme(mus, T('s08', 0.2), beat, 'box', 0.4, 12, n_notes=16)
    for i in range(18):
        tt = T('s08', 0.2) + i * beat
        mus.add(tt, pluck(mtof([53, 60, 57, 60][i % 4]), 0.4, 0.3), 1.0, -0.3)
    # la batería: el tema se detiene; ternura nocturna y cadencia final
    mus.add(T('s09', 5.0), pad([mtof(58), mtof(62), mtof(65)], 4.0, 0.4), 1.0)
    play_theme(mus, T('s09', 5.2), beat * 1.1, 'box', 0.4, 12, n_notes=8)
    for m in (53, 65, 69, 72):
        mus.add(T('s09', 8.6), piano(mtof(m), 2.5, 0.3), 1.0)
    # --- Inquietud (re menor)
    mus.add(s10, drone(mtof(38), 16.5, 0.45, attack=3.0), 1.0)
    for i, (dt, m) in enumerate(((1.5, 62), (3.8, 65), (5.5, 69), (7.6, 61), (9.0, 62), (10.3, 63))):
        mus.add(T('s10', dt), piano(mtof(m), 1.8, 0.28), 1.0, 0.2 * (i % 3 - 1))
    hb = T('s10', 11.2)
    while hb < T('s10', 14.0):
        mus.add(hb, heartbeat(0.55), 1.0)
        hb += 0.52
    mus.add(T('s10', 14.0), pad([mtof(38), mtof(39), mtof(50)], 2.2, 0.5, bright=600, attack=0.05, release=1.5), 1.0)
    # robo y agua: ostinato grave
    for i in range(22):
        tt = T('s11', 0.1) + i * 0.42
        mus.add(tt, pluck(mtof([38, 38, 39, 38][i % 4]), 0.45, 0.5 + 0.02 * i), 1.0, -0.1)
    mus.add(T('s11', 0.0), drone(mtof(38), 11.0, 0.35, attack=1.0), 1.0)
    # «la cámara»: momento de ternura y luego la mirada
    mus.add(T('s12', 6.0), pad([mtof(53), mtof(60), mtof(65), mtof(69)], 2.4, 0.5, bright=2000, attack=0.4), 1.0)
    for i, m in enumerate((77, 81, 84)):
        mus.add(T('s12', 6.3 + i * 0.5), musicbox(mtof(m), 0.45), 1.0, 0.2)
    mus.add(T('s12', 10.3), drone(mtof(38), 3.0, 0.45, attack=0.8, release=1.0), 1.0)
    mus.add(T('s12', 10.6), tone(mtof(88), 2.2, 0.08, attack=1.0, release=0.8), 1.0, 0.3)
    # --- El kentuki del hijo (la menor, melancólico)
    am = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]
    arps(mus, T('s13', 0.2), T('s13', 10.5), beat * 1.25, am, vel=0.25, pattern=(0, 1, 2, 1))
    play_theme(mus, T('s13', 5.0), beat * 1.3, 'box', 0.3, 12, n_notes=6, detune=0.003)
    # --- Klaus Berger: pulso de investigación
    tt = T('s14', 0.2)
    i = 0
    while tt < T('s14', 9.4):
        mus.add(tt, pluck(mtof([50, 53, 50, 57, 50, 53, 50, 58][i % 8]), 0.35, 0.3 + 0.015 * i), 1.0, 0.3)
        tt += 60 / 104.0 / 2
        i += 1
    mus.add(T('s14', 0.0), drone(mtof(38), 9.6, 0.25, attack=1.5, release=0.3), 1.0)
    mus.add(T('s14', 11.4), pad([mtof(38), mtof(44), mtof(49)], 5.0, 0.4, bright=700, attack=1.2), 1.0)
    for dt in (13.8, 14.6, 15.4):
        mus.add(T('s14', dt), piano(mtof(38), 0.8, 0.4), 1.0)
    mus.add(T('s14', 16.5), tone(mtof(26), 1.5, 0.2, attack=0.3, release=0.8), 1.0)
    # --- Gloria, el perdón, ama y ser (el tema regresa, frágil)
    arps(mus, T('s15', 1.2), T('s15', 9.5), beat, vel=0.22, pattern=(0, 2, 1, 2))
    mus.add(T('s16', 0.0), pad([mtof(41), mtof(48), mtof(57)], 7.0, 0.3, bright=900), 1.0)
    play_theme(mus, T('s16', 7.2), beat, 'box', 0.4, 12, n_notes=10)
    mus.add(T('s16', 10.0), pad([mtof(53), mtof(60), mtof(65), mtof(69)], 3.5, 0.4, bright=1800), 1.0)
    arps(mus, T('s17', 0.0), T('s17', 5.2), beat, vel=0.24, pattern=(0, 1, 2, 1))
    mus.add(T('s17', 5.3), tone(mtof(73) * 1.01, 1.9, 0.09, attack=0.4, release=0.5), 1.0, -0.3)
    mus.add(T('s17', 5.3), drone(mtof(37), 2.0, 0.3, attack=0.3, release=0.6), 1.0)
    play_theme(mus, T('s17', 8.4), beat, 'box', 0.35, 12, n_notes=8)
    for m in (50, 62, 65, 69):
        mus.add(T('s17', 12.0), piano(mtof(m), 2.0, 0.25), 1.0)
    # --- La llamada: tensión creciente
    mus.add(T('s18', 0.0), drone(mtof(38), 16.0, 0.5, attack=2.0, release=1.0), 1.0)
    hb = T('s18', 6.4)
    period = 0.95
    while hb < T('s18', 14.2):
        mus.add(hb, heartbeat(0.5), 1.0)
        hb += period
        period = max(0.55, period * 0.94)
    for dt in (3.6, 7.0, 9.6):
        mus.add(T('s18', dt), swell(2.4, 0.4, 150, 900), 1.0)
    mus.add(T('s18', 14.1), pad([mtof(37), mtof(38), mtof(44)], 2.2, 0.55, bright=500, attack=0.05, release=1.2), 1.0)
    # --- Conexión finalizada: casi silencio
    mus.add(T('s19', 6.7), drone(mtof(26), 3.3, 0.5, attack=0.5, release=1.5), 1.0)
    # --- La pileta: la caja de música se desafina y se detiene
    play_theme(mus, T('s20', 0.6), beat * 1.15, 'box', 0.3, 12, n_notes=5, detune=0.012, slow=0.6)
    tt = T('s20', 7.2)
    for i in range(6):
        mus.add(tt, musicbox(mtof(81) * (1 - 0.006 * i), 0.22 * (1 - i / 7)), 1.0, 0.25)
        tt += 0.55 + i * 0.12
    mus.add(T('s20', 11.8), pad([mtof(41), mtof(48), mtof(56)], 2.6, 0.32, bright=700, attack=1.0, release=2.0), 1.0)
    apply_reverb(mus, wet=0.38, dur=2.6, decay=2.6)
    return mus


# ---------------------------------------------------------------- efectos
def build_sfx():
    fx = Track()
    # Lima: mar y ciudad
    sea = lp(pink(11.5), 900)
    n = len(sea)
    tt = np.arange(n) / SR
    sea *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * tt)) * env_adsr(n, 1.5, 0.1, 1, 2.0)
    fx.add_st(0.0, sea, lp(pink(11.5), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * tt + 1)) * env_adsr(n, 1.5, 0.1, 1, 2.0),
              0.10)
    # S02: celofán, reloj, teclas
    for k in range(13):
        fx.add(T('s02', 0.4 + k), click(0.25, 1500, 4000, 0.01), 1.0, 0.5)
    fx.add(T('s02', 0.6), crinkle(2.6, 0.6), 1.0, 0.2)
    for i in range(12):
        fx.add(T('s02', 7.1 + i * 0.3), click(0.35), 1.0, 0.2)
    fx.add(T('s02', 10.8), tone(mtof(84), 0.18, 0.25) + 0, 1.0, 0.2)
    fx.add(T('s02', 10.95), tone(mtof(91), 0.3, 0.25), 1.0, 0.2)
    # S03: clic y conexión
    fx.add(T('s03', 2.15), click(0.5, 2000, 5000), 1.0, 0.3)
    fx.add(T('s03', 2.6), swell(1.6, 0.4, 600, 4000), 1.0)
    fx.add(T('s03', 4.7), whir(0.5, 0.3), 1.0)
    # S04: clics, aplausos, ruedas
    for dt in (5.05, 6.5):
        fx.add(T('s04', dt), click(0.45), 1.0, -0.3)
    for i in range(7):
        fx.add(T('s04', 6.65 + i * 0.17), bp(noise(0.03), 800, 5000) * np.hanning(int(0.03 * SR)) * 0.25, 1.0, 0.5)
    fx.add(T('s04', 8.6), whir(0.6, 0.35), 1.0, 0.4)
    fx.add(T('s04', 9.6), whir(0.6, 0.35, 160), 1.0, 0.4)
    # S05: chillido, ruedas
    fx.add(T('s05', 9.0), whir(1.8, 0.3), 1.0, 0.2)
    fx.add(T('s05', 10.9), chirp_s(0.5), 1.0, 0.2)
    # S06: campanas lejanas sobre Erfurt
    for i, m in enumerate((55, 52, 55, 50)):
        fx.add(T('s06', 3.4 + i * 1.1), lp(bell(mtof(m), 0.7, 3.5), 2000), 1.0, -0.4 + 0.25 * i)
    fx.add(T('s06', 3.0), lp(pink(5.0), 1200) * env_adsr(int(5 * SR), 1.0, 0.1, 1, 1.5) * 0.25, 1.0)
    fx.add(T('s06', 10.2), whir(1.8, 0.35), 1.0)
    fx.add(T('s06', 10.9), chirp_s(0.35), 1.0)
    # S07: tazas
    for i, dt in enumerate((5.2, 6.8, 8.9, 9.4)):
        fx.add(T('s07', dt), bell(mtof(96 + i), 0.25, 0.8), 1.0, 0.3 * (i - 1.5))
    for i in range(6):
        fx.add(T('s07', 7.3 + i * 0.25), thump(0.15, 140), 1.0, 0.4)
    # S08: ronroneo, ruedas
    fx.add(T('s08', 7.0), whir(1.4, 0.3), 1.0, 0.3)
    fx.add(T('s08', 9.4), purr(1.6, 0.5), 1.0)
    fx.add(T('s08', 12.2), whir(1.8, 0.4), 1.0, -0.3)
    fx.add(T('s08', 12.4), chirp_s(0.3), 1.0, -0.3)
    # S09: llamada, batería baja, carga
    fx.add(T('s09', 0.2), vibrate(0.8, 0.4), 1.0, 0.3)
    for dt in (3.5, 3.75):
        fx.add(T('s09', dt), tone(1320, 0.12, 0.3), 1.0, -0.2)
    fx.add(T('s09', 5.2), tone(mtof(79), 0.2, 0.2), 1.0, 0.4)
    fx.add(T('s09', 6.6), tone(mtof(84), 0.25, 0.2), 1.0, 0.4)
    # S10: pies, ducha, sartén, persecución
    for i in range(8):
        fx.add(T('s10', 2.6 + i * 0.32), thump(0.18, 90), 1.0, 0.2 * (i % 2))
    fx.add(T('s10', 6.6), chirp_s(0.5), 1.0)
    fx.add(T('s10', 7.8), hp(noise(8.0), 2500) * env_adsr(int(8 * SR), 0.6, 0.1, 1, 1.0) * 0.06, 1.0, 0.6)
    fx.add(T('s10', 8.4), frying(2.8, 0.6), 1.0, -0.3)
    fx.add(T('s10', 11.2), whir(2.8, 0.55, 220), 1.0)
    for i in range(7):
        fx.add(T('s10', 11.3 + i * 0.38), thump(0.45, 75), 1.0, -0.2)
    fx.add(T('s10', 12.8), chirp_s(0.55), 1.0)
    fx.add(T('s10', 14.0), chirp_s(0.6), 1.0)
    # S11: chillidos, agua
    for dt in (2.4, 2.8, 3.6, 4.0):
        fx.add(T('s11', dt), chirp_s(0.45), 1.0)
    fx.add(T('s11', 4.8), whir(1.8, 0.5, 240), 1.0)
    for dt in (5.0, 5.6, 6.2, 7.2, 7.9):
        fx.add(T('s11', dt), chirp_s(0.5), 1.0)
    fx.add(T('s11', 6.8), water(4.2, 0.9), 1.0)
    # S12: toalla
    fx.add(T('s12', 3.6), lp(noise(1.0), 1500) * np.hanning(int(SR)) * 0.08, 1.0)
    # S13: mensaje con foto
    fx.add(T('s13', 4.9), tone(mtof(88), 0.12, 0.2), 1.0, 0.2)
    fx.add(T('s13', 5.05), tone(mtof(93), 0.15, 0.2), 1.0, 0.2)
    # S14: teclas, mensaje, campanitas, vibración, luz que se apaga
    for i in range(10):
        fx.add(T('s14', 2.6 + i * 0.18), click(0.3), 1.0, 0.2)
    for i in range(9):
        fx.add(T('s14', 6.7 + i * 0.14), click(0.25, 3000, 7000, 0.008), 1.0, 0.0)
    fx.add(T('s14', 7.9), swell(0.4, 0.35, 1500, 6000), 1.0)
    fx.add(T('s14', 9.6), chimes(0.7), 1.0)
    fx.add(T('s14', 10.5), vibrate(1.1, 0.6), 1.0)
    fx.add(T('s14', 11.1), thump(0.3, 120), 1.0)
    fx.add(T('s14', 14.9), whir(1.4, 0.3), 1.0)
    fx.add(T('s14', 16.9), click(0.6, 800, 3000, 0.02), 1.0)
    # S15: timbre, papel
    fx.add(T('s15', 0.2), doorbell(0.6), 1.0, -0.3)
    fx.add(T('s15', 1.1), thump(0.25, 90), 1.0, -0.4)
    fx.add(T('s15', 4.6), crinkle(1.4, 0.45), 1.0)
    for i in range(6):
        fx.add(T('s15', 6.1 + i * 0.13), bp(noise(0.03), 800, 5000) * np.hanning(int(0.03 * SR)) * 0.2, 1.0, -0.3)
    fx.add(T('s15', 8.6), tone(mtof(84), 0.2, 0.15), 1.0, -0.5)
    # S16: reloj, carga, obturador
    for k in range(3):
        fx.add(T('s16', 0.2 + k), click(0.2, 1500, 4000, 0.01), 1.0, -0.4)
    fx.add(T('s16', 1.4), click(0.4, 600, 2500, 0.02), 1.0, -0.5)
    fx.add(T('s16', 5.3), click(0.35), 1.0)
    fx.add(T('s16', 11.35), click(0.6, 1500, 6000, 0.03), 1.0)
    fx.add(T('s16', 11.42), click(0.4, 1000, 4000, 0.03), 1.0)
    # S17: pava, ronroneo, teléfono
    fx.add(T('s17', 3.0), hp(noise(2.3), 3000) * env_adsr(int(2.3 * SR), 0.8, 0.1, 1, 0.6) * 0.05, 1.0, -0.4)
    fx.add(T('s17', 3.4), purr(1.8, 0.5), 1.0, 0.3)
    fx.add(T('s17', 5.3), vibrate(1.9, 0.6), 1.0)
    fx.add(T('s17', 10.8), purr(2.0, 0.4), 1.0, 0.4)
    # S18: sartén, teléfono de Klaus, teléfono de Emilia, té derramado
    fx.add(T('s18', 0.0), frying(1.6, 0.5), 1.0, -0.3)
    fx.add(T('s18', 0.1), vibrate(1.5, 0.45), 1.0, 0.2)
    fx.add(T('s18', 9.6), vibrate(1.3, 0.65), 1.0)
    fx.add(T('s18', 9.9), whir(0.8, 0.3), 1.0, 0.3)
    fx.add(T('s18', 13.8), thump(0.5, 80), 1.0)
    fx.add(T('s18', 13.9), water(0.8, 0.5), 1.0, 0.3)
    fx.add(T('s18', 14.0), creak(0.5, 0.4), 1.0)
    # S19: apagar, prender, botón rojo, diálogo, crujido del mimbre
    fx.add(T('s19', 1.75), click(0.6, 600, 3000, 0.025), 1.0)
    fx.add(T('s19', 1.8), tone(90, 0.4, 0.3, 0.005, 0.35), 1.0)
    fx.add(T('s19', 3.15), click(0.5, 600, 3000, 0.025), 1.0)
    fx.add(T('s19', 4.55), click(0.45), 1.0)
    fx.add(T('s19', 6.0), click(0.5), 1.0)
    fx.add(T('s19', 6.15), tone(mtof(45), 1.2, 0.3, 0.01, 0.8), 1.0)
    fx.add(T('s19', 8.6), creak(1.3, 0.8), 1.0)
    # S20: pasos, canilla, agua, chillido ahogado, gota final
    for i in range(5):
        fx.add(T('s20', 4.7 + i * 0.45), thump(0.25, 85), 1.0)
    fx.add(T('s20', 5.0), chirp_s(0.3), 1.0)
    fx.add(T('s20', 6.9), click(0.4, 500, 2000, 0.03), 1.0)
    fx.add(T('s20', 7.0), water(7.4, 1.0, 2600), 1.0)
    fx.add(T('s20', 7.4), lp(chirp_s(0.45), 900), 1.0)
    fx.add(T('s20', 8.3), lp(chirp_s(0.35), 700), 1.0)
    fx.add(T('s20', 9.1), lp(chirp_s(0.2), 600), 1.0)
    for k in range(3):
        fx.add(T('s20', 12.4 + k * 0.9), tone(1900 - k * 120, 0.06, 0.12, 0.002, 0.05), 1.0, 0.2)
    apply_reverb(fx, wet=0.18, dur=0.9, decay=6.0, bright=5000)
    return fx


def main():
    mus = build_music()
    fxs = build_sfx()
    L = mus.L * 0.9 + fxs.L * 1.0
    R = mus.R * 0.9 + fxs.R * 1.0
    # tono de ambiente muy bajo para que los silencios no suenen a corte digital
    room_l = lp(pink(N / SR), 400)
    room_r = lp(pink(N / SR), 400)
    k = 10 ** (-60 / 20) / (np.sqrt(np.mean(room_l ** 2)) + 1e-9)
    L += room_l[:N] * k * 18
    R += room_r[:N] * k * 18
    # silencios intencionales y fade final
    t = np.arange(N) / SR
    fade = np.clip((TOTAL - t) / 2.5, 0, 1)
    L *= fade
    R *= fade
    L = hp(L, 35)
    R = hp(R, 35)
    # normalización suave: RMS objetivo bajo (acompaña la voz del expositor)
    rms = np.sqrt(np.mean((L ** 2 + R ** 2) / 2))
    target = 10 ** (-27 / 20)
    g = target / max(rms, 1e-9)
    L, R = L * g, R * g
    peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
    lim = 10 ** (-4 / 20)
    if peak > lim:
        # limitador suave
        L = np.tanh(L / lim) * lim
        R = np.tanh(R / lim) * lim
    os.makedirs(os.path.join(ROOT, 'build'), exist_ok=True)
    out = os.path.join(ROOT, 'build', 'audio.wav')
    data = np.stack([L, R], 1)
    wavfile.write(out, SR, (np.clip(data, -1, 1) * 32767).astype(np.int16))
    rms2 = 20 * np.log10(np.sqrt(np.mean(data ** 2)) + 1e-12)
    pk = 20 * np.log10(np.max(np.abs(data)) + 1e-12)
    print('->', out, 'duración %.2fs  RMS %.1f dBFS  pico %.1f dBFS' % (N / SR, rms2, pk))


if __name__ == '__main__':
    main()
