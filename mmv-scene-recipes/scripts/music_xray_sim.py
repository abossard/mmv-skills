"""Frame-by-frame model of the Music X-Ray Globals (previous-frame semantics) on a synthetic 126 BPM track.

    python3 music_xray_sim.py

Runs the Globals of music_xray_example.add_globals without Magic: ExprTk `if` is evaluated lazily, every Global
reads the previous frame. Prints the detector state every 8 bars and every drop, lift and state change, so a
change to the analysis can be checked before loading it into Magic."""
import math, sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "mmv-audio-reactivity", "scripts"))
import music_xray_example as build_xray
import audio_bank
G = []
class FB:
    def glob(self, name, value=0, source=None, mods=()): G.append((name, value, source, list(mods)))
build_xray.add_globals(FB(), audio_bank)

def split(s):
    out, d, cur = [], 0, ""
    for ch in s:
        if ch == "," and d == 0: out.append(cur); cur = ""; continue
        d += (ch == "(") - (ch == ")"); cur += ch
    out.append(cur); return out
def lazy_if(e):
    i = e.find("if (")
    if i < 0: return e
    d, k = 0, i + 3
    while True:
        d += (e[k] == "(") - (e[k] == ")")
        if d == 0: break
        k += 1
    a, b, c = (lazy_if(x) for x in split(e[i + 4:k]))
    return e[:i] + "((%s) if (%s) else (%s))" % (b, a, c) + lazy_if(e[k + 1:])
def rnd(x): return math.floor(x + 0.5) if x >= 0 else -math.floor(-x + 0.5)
FUN = dict(exp=math.exp, log=lambda x: math.log(x) if x > 0 else -1e9, pow=math.pow, floor=math.floor, frac=lambda x: x - math.floor(x),
           clamp=lambda x, a, b: min(b, max(a, x)), min=min, max=max, abs=abs, round=rnd, sqrt=math.sqrt)
code = {}
for name, value, src, mods in G:
    for m in mods:
        if m[0] == "Expression":
            py = lazy_if(m[1])
            code[m[1]] = compile(re.sub(r"[A-Za-z_]\w*", lambda t: t.group(0) if t.group(0) in FUN or t.group(0) in ("x", "y", "if", "else", "and", "or", "not") else "V['%s']" % t.group(0).lower(), py), m[1], "eval")

BPM = 126.0; SPB = 60 / BPM; BAR = 4 * SPB
SECS = [("intro", 16), ("buildup", 8), ("drop", 16), ("breakdown", 16), ("buildup", 8), ("drop", 16), ("outro", 8)]
def section(bar):
    s = 0
    for L, n in SECS:
        if bar < s + n: return L, bar - s, n
        s += n
    return "outro", 7, 8
ROLL = [1, 1, 2, 2, 4, 4, 8, 8]
def audio(t):
    bf = t / SPB; bar = int(bf // 4); L, sb, n = section(bar); prog = (bf / 4 - (bar - sb)) / n; dtb = (bf % 1) * SPB
    kickon = (L == "intro" and sb >= 4) or L == "drop" or (L == "outro" and sb < 6)
    kick = math.exp(-dtb / 0.05) if kickon else 0
    hat = math.exp(-(((bf + 0.5) % 1) * SPB) / 0.03) if L in ("intro", "drop", "outro") else 0
    sn = 0
    if L == "drop":
        last = math.floor((bf - 1) / 2) * 2 + 1; sn = math.exp(-(bf - last) * SPB / 0.08)
    if L == "buildup":
        dv = ROLL[min(7, sb)]; last = math.floor(bf * dv) / dv; sn = (0.4 + 0.6 * prog) * math.exp(-(bf - last) * SPB / 0.05)
    sub = {"drop": 0.45 * (1 - 0.7 * kick), "intro": 0.14 if sb >= 8 else 0.05, "buildup": 0.02, "breakdown": 0.06, "outro": 0.12}[L]
    tone = {"buildup": 0.35 + 0.35 * prog ** 1.5, "drop": 0.6, "breakdown": 0.4, "intro": 0.45, "outro": 0.45}[L]
    crash = 0
    if L == "drop":
        for b0 in (0, 8):
            d = (bf / 4 - (bar - sb) - b0) * BAR
            if d >= 0: crash = max(crash, math.exp(-d / 1.2))
    return {"20-80 Hz": sub + 0.15 * kick, "80-320 Hz": 0.4 * kick + 0.1 * sub, "320-1.2k Hz": 0.1, "1.2k-5k Hz": 0.05 + 0.35 * sn + 0.03 * hat,
            "5k-20k Hz": 0.04 + 0.25 * hat + 0.3 * crash, "Volume": 0.2 + 0.2 * kick + 0.2 * sub, "Tone": tone}, (L, bar)

V = {n.lower(): 0.0 for n, *_ in G}
for n, v, src, mods in G:
    if src is None: V[n.lower()] = float(v)
def apply(n, src, mods, x, prev):
    y = prev
    for m in mods:
        k, a = m
        if k == "Expression": x = eval(code[a], {"V": V, **FUN, "x": x, "y": y})
        elif k == "Smooth": x = y * a + x * (1 - a)
        elif k == "Clamp": x = min(a, max(0, x))
        elif k == "Threshold": x = 1.0 if x > a else 0.0
        elif k == "Increase": x = y + a * Vdt
        elif k == "Trigger": x = y + 1 if x > a and V.get("_trig_" + n, 0) <= a else y
        elif k == "Wrap": x = x % a
    return x
FPS = 120.0; Vdt = 1 / FPS
events = []; prev = dict(V); song = sum(n for _, n in SECS) * BAR
f = 0; t = 0.0
while t < song:
    A, (L, bar) = audio(t)
    old = dict(V); new = {}
    for n, v, src, mods in G:
        if src is None: new[n.lower()] = old[n.lower()]; continue
        if src == "calc": x = 0.0
        elif src.startswith("global:"): x = old[src[7:].lower()]
        else:
            key = src.split(":")[-1]; x = A[key] if key in A else A["Volume" if src.endswith("Volume") else "Tone"]
        V.update(old)
        new[n.lower()] = apply(n, src, mods, x, old[n.lower()])
    V = new
    if V["droppulse"] > 0.5: events.append((t, "DROP", bar + 1, L))
    if V["liftpulse"] > 0.5: events.append((t, "LIFT", bar + 1, L))
    if abs(V["state"] - old["state"]) > 0.5: events.append((t, "state %d" % V["state"], bar + 1, L))
    if f % int(FPS * BAR * 8) == int(FPS * BAR * 4):
        print("t=%6.1f bar %3d %-9s bpm %6.2f lock %.2f phase %.2f subBar %.2f subOut %d tone+ %.3f snRate %.1f kRate %.1f state %d tension %.2f beatInBar %d" % (
            t, bar + 1, L, V["bpm"], V["lock"], V["phase"], V["subbar"], V["subout"], V["tonerise"], V["snarerate"], V["kickrate"], V["state"], V["tension"], V["beatinbar"]))
    f += 1; t = f / FPS
for e in events: print("%6.1f s  %-8s bar %3d  (%s)" % e)
print("counts kick %d snare %d hat %d  downSlot %d" % (V["kickcount"], V["snarecount"], V["hatcount"], V["downslot"]))
