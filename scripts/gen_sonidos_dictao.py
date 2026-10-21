"""Genera los temas de sonido de inicio/fin de Dictao (src-tauri/resources).

Sintesis simple (senos con envolvente exponencial), sin silencio inicial para
que el sonido suene apenas se aprieta la tecla. Solo usa la libreria estandar.

    python scripts/gen_sonidos_dictao.py
"""

import math
import random
import struct
import wave
from pathlib import Path

SR = 44100
PEAK = 0.8  # mismo rango que marimba/pop
OUT = Path(__file__).resolve().parent.parent / "src-tauri" / "resources"


def silence(seconds):
    return [0.0] * int(SR * seconds)


def mix(buf, other, start=0.0):
    i0 = int(SR * start)
    need = i0 + len(other)
    if len(buf) < need:
        buf.extend([0.0] * (need - len(buf)))
    for i, v in enumerate(other):
        buf[i0 + i] += v
    return buf


def tone(freq, dur, freq_end=None, wave_type="sine", attack=0.008, gain=1.0):
    """Tono con ataque corto y caida exponencial; glissando opcional."""
    n = int(SR * (dur + 0.05))
    out, phase = [], 0.0
    for i in range(n):
        t = i / SR
        f = freq
        if freq_end:
            k = min(t / (dur * 0.6), 1.0)
            f = freq * (freq_end / freq) ** k
        phase += 2 * math.pi * f / SR
        if wave_type == "triangle":
            v = 2 / math.pi * math.asin(math.sin(phase))
        else:
            v = math.sin(phase)
        if t < attack:
            env = t / attack
        else:
            env = math.exp(-6.9 * (t - attack) / max(dur - attack, 1e-3))
        out.append(v * env * gain)
    return out


def air(rising):
    """Soplo: ruido filtrado por un pasabanda que barre la frecuencia."""
    rnd = random.Random(7)
    dur = 0.45
    n = int(SR * dur)
    out, y1, y2, x1, x2 = [], 0.0, 0.0, 0.0, 0.0
    for i in range(n):
        t = i / SR
        k = min(t / 0.4, 1.0)
        f0, f1 = (600, 2200) if rising else (2200, 600)
        fc = f0 * (f1 / f0) ** k
        w0 = 2 * math.pi * fc / SR
        alpha = math.sin(w0) / (2 * 1.2)
        b0, a0 = alpha, 1 + alpha
        a1, a2 = -2 * math.cos(w0), 1 - alpha
        x = rnd.uniform(-1, 1)
        y = (b0 * x - b0 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, x, y1, y
        env = t / 0.15 if t < 0.15 else math.exp(-6.9 * (t - 0.15) / 0.27)
        out.append(y * env)
    return out


def gota(start):
    return tone(500, 0.22, 1100) if start else tone(1000, 0.22, 450)


def campanita(start):
    a, b = (1046.5, 1318.5) if start else (1318.5, 1046.5)
    buf = []
    mix(buf, tone(a, 0.6, gain=0.8))
    mix(buf, tone(a * 2, 0.3, gain=0.15))
    mix(buf, tone(b, 0.7, gain=0.8), 0.11)
    mix(buf, tone(b * 2, 0.35, gain=0.15), 0.11)
    return buf


def burbuja(start):
    return tone(380, 0.12, 900, attack=0.004) if start else tone(700, 0.12, 300, attack=0.004)


def cristal(start):
    f = 2093 if start else 1568
    buf = []
    mix(buf, tone(f, 0.25, wave_type="triangle", gain=0.5, attack=0.003))
    mix(buf, tone(f * 1.5, 0.18, gain=0.2, attack=0.003))
    return buf


def madera(start):
    f = 784 if start else 587
    buf = []
    mix(buf, tone(f, 0.35, gain=0.9, attack=0.003))
    mix(buf, tone(f * 4, 0.06, gain=0.25, attack=0.002))
    mix(buf, tone(f * 10, 0.02, gain=0.08, attack=0.001))
    return buf


def aire(start):
    return air(start)


def ascenso(start):
    a, b = (659.3, 987.8) if start else (987.8, 659.3)
    buf = []
    mix(buf, tone(a, 0.18, gain=0.7))
    mix(buf, tone(b, 0.32, gain=0.7), 0.09)
    return buf


THEMES = {
    "droplet": gota,
    "chime": campanita,
    "bubble": burbuja,
    "crystal": cristal,
    "wood": madera,
    "air": aire,
    "rise": ascenso,
}


def write_wav(path, samples):
    peak = max(abs(v) for v in samples) or 1.0
    scale = PEAK / peak
    # Fade final de 5 ms para no terminar con un click.
    fade = int(SR * 0.005)
    for i in range(fade):
        samples[-1 - i] *= i / fade
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for v in samples:
            s = int(max(-1.0, min(1.0, v * scale)) * 32767)
            frames += struct.pack("<hh", s, s)
        w.writeframes(bytes(frames))


if __name__ == "__main__":
    for name, fn in THEMES.items():
        for kind, start in (("start", True), ("stop", False)):
            path = OUT / f"{name}_{kind}.wav"
            write_wav(path, fn(start))
            print(path.name)
