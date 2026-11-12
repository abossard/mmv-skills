"""126 BPM test track with intro, buildups, drops (sub-bass step, crash, lift at drop bar 8) and a breakdown. Mono 44.1 kHz.

    python3 music_xray_testtrack.py xray_test.wav      # 92 s; bars: intro 4, buildup 8, drop 12, breakdown 8, buildup 8, drop 8
"""
import math, random, struct, sys, wave
SR, BPM = 44100, 126.0
SPB = 60 / BPM; BAR = 4 * SPB
SECS = [("intro", 4), ("buildup", 8), ("drop", 12), ("breakdown", 8), ("buildup", 8), ("drop", 8)]
total = sum(n for _, n in SECS); N = int(total * BAR * SR) + SR
buf = [0.0] * N
random.seed(1)
noise = [random.uniform(-1, 1) for _ in range(SR * 2)]
def add(t, samples, amp=1.0):
    i0 = int(t * SR)
    for i, v in enumerate(samples):
        if i0 + i < N: buf[i0 + i] += v * amp
kick = []
ph = 0.0
for i in range(int(0.35 * SR)):
    t = i / SR; f = 50 + 110 * math.exp(-t / 0.03); ph += 2 * math.pi * f / SR
    kick.append(math.sin(ph) * math.exp(-t / 0.12))
hat, prev = [], 0.0
for i in range(int(0.05 * SR)):
    n = noise[i]; hp = n - prev; prev = n; hat.append(hp * 0.5 * math.exp(-i / SR / 0.012))
snare, lp = [], 0.0
for i in range(int(0.18 * SR)):
    n = noise[(i * 7) % len(noise)]; lp += (n - lp) * 0.35; t = i / SR
    snare.append((n - lp) * 0.6 * math.exp(-t / 0.06) + 0.4 * math.sin(2 * math.pi * 190 * t) * math.exp(-t / 0.04))
crash, prev = [], 0.0
for i in range(int(1.8 * SR)):
    n = noise[(i * 3) % len(noise)]; hp = n - prev; prev = n; crash.append(hp * 0.45 * math.exp(-i / SR / 0.7))
ROOTS = [55.0, 43.65, 65.41, 49.0]
bar0 = 0; sub_env = [0.0] * N; sub_f = [55.0] * N
for L, n in SECS:
    for b in range(n):
        bar = bar0 + b; tb = bar * BAR; prog = b / n
        for beat in range(4):
            tt = tb + beat * SPB
            if (L == "intro" and b >= 1) or L == "drop": add(tt, kick, 0.9)
            if L in ("intro", "drop"): add(tt + SPB / 2, hat, 0.5)
            if L == "drop" and beat in (1, 3): add(tt, snare, 0.7)
            if L == "buildup":
                div = [1, 1, 2, 2, 4, 4, 8, 8][b]
                for k in range(div): add(tt + k * SPB / div, snare, 0.25 + 0.5 * prog)
        if L == "drop" and b in (0, 8): add(tb, crash, 1.0)
        lvl = {"intro": 0.12 if b >= 2 else 0.0, "buildup": 0.0, "drop": 0.55, "breakdown": 0.06}[L]
        i0, i1 = int(tb * SR), int((tb + BAR) * SR)
        for i in range(i0, min(i1, N)):
            sub_env[i] = lvl; sub_f[i] = ROOTS[bar % 4]
        if L == "buildup":   # riser: noise through a rising one-pole low-pass, louder towards the drop
            lp = 0.0
            for i in range(i0, min(i1, N)):
                p = (b + (i - i0) / (i1 - i0)) / n; a = 0.02 + 0.5 * p * p
                lp += (noise[i % len(noise)] - lp) * a; buf[i] += (noise[i % len(noise)] - lp) * (0.05 + 0.25 * p * p)
    bar0 += n
ph = 0.0
for i in range(N):
    t = i / SR; beatf = (t / SPB) % 1.0
    duck = 1 - 0.7 * math.exp(-beatf * SPB / 0.08)
    ph += 2 * math.pi * sub_f[i] / SR
    buf[i] += math.sin(ph) * sub_env[i] * duck
peak = max(abs(v) for v in buf)
with wave.open(sys.argv[1], "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", int(32767 * 0.9 * v / peak)) for v in buf))
print("wrote", sys.argv[1], "%.1f s" % (N / SR))
