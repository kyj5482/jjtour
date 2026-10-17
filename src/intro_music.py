"""Synthesize the intro soundtrack: heartbeat -> pluck arpeggio -> full band -> resolve."""
import numpy as np, wave, sys

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 92.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i+len(sig)] += sig * gain * (1 - pan) / 1.0
    R[i:i+len(sig)] += sig * gain * (1 + pan) / 1.0

def env(n, a, d, s_lvl=0.0, rel=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    e = e * np.exp(-np.maximum(0, t - a) / d) * (1 - s_lvl) + s_lvl * np.minimum(1, t / max(a, 1e-4))
    if rel:
        e *= np.clip((n / SR - t) / rel, 0, 1)
    return e

hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def heartbeat(t0, g=1.0):
    for k, (off, amp) in enumerate([(0, 1.0), (0.24, 0.7)]):
        n = int(0.32 * SR); t = np.arange(n) / SR
        f = 48 + 40 * np.exp(-t * 30)
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.sin(ph) * np.exp(-t * 14) * amp
        s += 0.15 * np.sin(2 * ph) * np.exp(-t * 25)
        add(s, t0 + off, 0.9 * g)

def kick(t0, g=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 35)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    add(s, t0, 0.55 * g)

def hat(t0, g=1.0, pan=0.3):
    n = int(0.06 * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n); s = np.diff(np.concatenate([[0], s]))
    add(s * np.exp(-t * 70), t0, 0.05 * g, pan)

def pluck(t0, m, g=1.0, pan=0.0, dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = (np.sin(2*np.pi*f*t) + 0.35*np.sin(4*np.pi*f*t)*np.exp(-t*6) + 0.12*np.sin(6*np.pi*f*t)*np.exp(-t*9))
    s *= np.minimum(1, t / 0.004) * np.exp(-t * 3.2)
    add(s, t0, 0.16 * g, pan)

def pad(t0, notes, dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        for det in (-0.08, 0.0, 0.08):
            f = hz(m + det)
            s += np.sin(2*np.pi*f*t) + 0.3*np.sin(4*np.pi*f*t) + 0.12*np.sin(6*np.pi*f*t)
    s /= len(notes) * 3
    e = np.minimum(1, t / 1.2) * np.clip((dur - t) / 1.2, 0, 1)
    add(s * e, t0, 0.22 * g, 0)

def bass(t0, m, dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) + 0.25*np.sin(4*np.pi*f*t)
    s *= np.minimum(1, t / 0.01) * np.clip((dur - t) / 0.08, 0, 1) * (0.7 + 0.3*np.exp(-t*4))
    add(s, t0, 0.22 * g)

def bell(t0, m, g=1.0, pan=0.0):
    n = int(2.5 * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) * np.exp(-t*1.6) + 0.4*np.sin(2*np.pi*f*2.76*t) * np.exp(-t*4)
    add(s * np.minimum(1, t/0.003), t0, 0.07 * g, pan)

# ---- arrangement (D major, 100 bpm) ----
BPM = 100; beat = 60 / BPM; bar = 4 * beat
START = 6.0
# I  V  vi  IV   (D A Bm G)
CH = [([62, 66, 69], 50), ([61, 64, 69], 45), ([62, 66, 71], 47), ([62, 67, 71], 43)]
ARP = [0, 1, 2, 1, 2, 3, 2, 1]  # pattern over chord tones (+octave as 3)

# heartbeat: 0 - 11s, tempo rising slightly
t = 0.4; hb = 0.86
while t < 11.0:
    heartbeat(t, 1.0 if t < 6 else max(0, 1 - (t - 6) / 5))
    t += hb; hb = max(0.62, hb - 0.012)

# shimmering pad swell under heartbeat
pad(1.0, [74, 78, 81], 6.0, 0.35)

end_music = DUR - 8.0
t = START; ci = 0
while t < end_music:
    notes, b = CH[ci % 4]
    sec = t - START
    pad(t, notes, 2 * bar + 1.0, 0.9 if sec > 22 else 0.6)
    tones = notes + [notes[0] + 12]
    for k in range(16):  # eighth notes across 2 bars
        tk = t + k * beat / 2
        m = tones[ARP[k % 8]] + (12 if sec > 54 and k % 4 == 3 else 0)
        pluck(tk, m, 1.0 if sec > 5 else 0.5 + sec / 10, pan=(-0.35 if k % 2 else 0.35))
    if sec >= 22:  # drums from ~28s
        for k in range(8):
            kick(t + k * beat, 0.8 if sec < 54 else 1.0)
            hat(t + k * beat + beat / 2, 1.0)
            if sec >= 54: hat(t + k * beat + beat / 4, 0.5, -0.3); hat(t + k * beat + 3*beat/4, 0.5, -0.3)
    if sec >= 38:
        for k in range(4):
            bass(t + k * 2 * beat, b, 2 * beat * 0.95, 1.0)
    if sec >= 54 and ci % 2 == 0:
        for k, m in enumerate([81, 78, 76, 74]):
            bell(t + k * bar / 2 + beat, m, 1.0, 0.2)
    t += 2 * bar; ci += 1

# finale: big D chord ring + bell
for m in [50, 62, 66, 69, 74, 78]:
    pluck(t, m, 1.4, pan=0, dur=6.0)
pad(t, [62, 66, 69, 74], 7.5, 1.2)
bell(t + 0.5, 86, 1.5); bell(t + 1.3, 81, 1.2, -0.3)
kick(t, 1.0)

# ---- fx: stereo delay + simple reverb ----
def delay(x, sec, fb, mix):
    d = int(sec * SR); y = x.copy()
    for k in range(1, 5):
        y[d*k:] += x[:-d*k] * (fb ** k) * mix
    return y
L2 = delay(L, beat * 0.75, 0.45, 0.6); R2 = delay(R, beat * 0.5, 0.45, 0.6)
for d, g in [(0.031, .3), (0.047, .25), (0.071, .2), (0.113, .15), (0.173, .1)]:
    k = int(d * SR)
    L2[k:] += R[:-k] * g; R2[k:] += L[:-k] * g
mx = max(np.abs(L2).max(), np.abs(R2).max())
L2 /= mx / 0.89; R2 /= mx / 0.89
fade = np.clip((DUR - np.arange(N) / SR) / 2.5, 0, 1)
L2 *= fade; R2 *= fade
st = np.stack([L2, R2], 1)
st = np.tanh(st * 1.1) / np.tanh(1.1)
pcm = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1], DUR, "s")
