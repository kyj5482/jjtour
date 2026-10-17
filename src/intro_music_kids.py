"""Synthesize the kids' intro soundtrack: drum roll -> bouncy marimba + claps -> glockenspiel tune -> big finish."""
import numpy as np, wave, sys

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 78.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i+len(sig)] += sig * gain * (1 - pan)
    R[i:i+len(sig)] += sig * gain * (1 + pan)

def snare(t0, g=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n) * np.exp(-t * 30) + 0.3 * np.sin(2*np.pi*190*t) * np.exp(-t * 40)
    add(s, t0, 0.12 * g, rng.uniform(-.2, .2))

def crash(t0, g=1.0):
    n = int(1.8 * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n); s = np.diff(np.concatenate([[0], s]))
    add(s * np.exp(-t * 2.2), t0, 0.07 * g)

def kick(t0, g=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    f = 50 + 120 * np.exp(-t * 40)
    add(np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t * 11), t0, 0.5 * g)

def clap(t0, g=1.0):
    for k, d in enumerate((0, 0.011, 0.022)):
        n = int(0.09 * SR); t = np.arange(n) / SR
        s = rng.standard_normal(n); s = np.diff(np.concatenate([[0], s]))
        add(s * np.exp(-t * (45 if k < 2 else 25)), t0 + d, 0.05 * g, 0.15)

def marimba(t0, m, g=1.0, pan=0.0):
    n = int(0.6 * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) + 0.25*np.sin(2*np.pi*f*4*t)*np.exp(-t*30)
    add(s * np.minimum(1, t/0.002) * np.exp(-t * 8), t0, 0.16 * g, pan)

def bell(t0, m, g=1.0, pan=0.0):
    n = int(1.6 * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t)*np.exp(-t*2.5) + 0.35*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*6)
    add(s * np.minimum(1, t/0.002), t0, 0.09 * g, pan)

def bass(t0, m, dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = (np.sin(2*np.pi*f*t) + 0.3*np.sin(4*np.pi*f*t)) * np.minimum(1, t/0.01) * np.clip((dur-t)/0.05, 0, 1) * (0.6+0.4*np.exp(-t*5))
    add(s, t0, 0.2 * g)

def pad(t0, notes, dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for det in (-0.06, 0.06):
            f = hz(m + det); s += np.sin(2*np.pi*f*t) + 0.2*np.sin(4*np.pi*f*t)
    s /= len(notes) * 2
    add(s * np.minimum(1, t/0.6) * np.clip((dur-t)/0.6, 0, 1), t0, 0.12 * g)

# drum roll 0 -> 3.5s, accelerating and growing
t = 0.2; gap = 0.16
while t < 3.4:
    snare(t, 0.3 + 0.9 * t / 3.4); t += gap; gap = max(0.035, gap * 0.9)
crash(3.5, 1.2); kick(3.5, 1.2)

BPM = 120; beat = 60 / BPM; bar = 4 * beat
START = 3.5
CH = [([65, 69, 72], 41), ([64, 67, 72], 48), ([62, 65, 69], 50), ([62, 65, 70], 46)]   # F C Dm Bb
TUNE = [77, 76, 74, 72, 74, 76, 77, 81]  # a small glockenspiel hook, one note per beat over 2 bars
end_music = DUR - 6.0
t = START; ci = 0
while t < end_music:
    notes, b = CH[ci % 4]; sec = t - START
    pad(t, [n + 12 for n in notes], bar + 0.4, 0.8)
    seq = [notes[0], notes[1], notes[2], notes[1] + 12, notes[2], notes[1], notes[0] + 12, notes[2]]
    for k in range(8):
        marimba(t + k * beat / 2, seq[k] + 12, 1.0, -0.3 if k % 2 else 0.3)
    for k in range(4):
        kick(t + k * beat, 0.7 if sec < 8 else 0.9)
        if k in (1, 3): clap(t + k * beat, 1.0 if sec > 4 else 0.6)
        bass(t + k * beat, b, beat * 0.9, 0.9 if sec > 8 else 0.5)
    if sec >= 16 and (ci // 4) % 2 == 0:
        for k in range(4):
            bell(t + k * beat, TUNE[(ci % 2) * 4 + k], 1.0, 0.2)
    t += bar; ci += 1

# finale
crash(t, 1.3); kick(t, 1.3)
for m in [53, 65, 69, 72, 77, 81]: marimba(t, m, 1.4)
pad(t, [65, 69, 72, 77], 5.5, 1.3)
for k, m in enumerate([84, 81, 77, 89]): bell(t + 0.3 + k * 0.22, m, 1.2)

def delay(x, sec, fb, mix):
    d = int(sec * SR); y = x.copy()
    for k in range(1, 4): y[d*k:] += x[:-d*k] * (fb ** k) * mix
    return y
L2 = delay(L, beat * 0.75, 0.35, 0.35); R2 = delay(R, beat * 0.5, 0.35, 0.35)
for d, g in [(0.029, .25), (0.051, .2), (0.083, .15)]:
    k = int(d * SR); L2[k:] += R[:-k] * g; R2[k:] += L[:-k] * g
mx = max(np.abs(L2).max(), np.abs(R2).max()); L2 /= mx / 0.9; R2 /= mx / 0.9
fade = np.clip((DUR - np.arange(N) / SR) / 2.0, 0, 1); L2 *= fade; R2 *= fade
st = np.tanh(np.stack([L2, R2], 1) * 1.1) / np.tanh(1.1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[1], DUR, "s")
