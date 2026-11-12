/*{
	"DESCRIPTION": "Music X-Ray Pulse: beat orbit (bar phase, lock, bar 1), who's playing (kick heart, snare burst, hat sparks, sub-bass floor) and drop radar (tension gauge and its three cues). Every input is a Global of the analysis bank.",
	"CREDIT": "mmv-skills music-xray",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Audio Visualizer"],
	"INPUTS": [
		{"NAME": "phase", "LABEL": "Phase", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 4.0},
		{"NAME": "downSlot", "LABEL": "DownSlot", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 3.0},
		{"NAME": "downSet", "LABEL": "DownSet", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "lock", "LABEL": "Lock", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "bpm", "LABEL": "Bpm", "TYPE": "float", "DEFAULT": 120.0, "MIN": 0.0, "MAX": 400.0},
		{"NAME": "nudge", "LABEL": "Nudge", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
		{"NAME": "sinceKick", "LABEL": "SinceKick", "TYPE": "float", "DEFAULT": 99.0, "MIN": 0.0, "MAX": 100000.0},
		{"NAME": "visualLead", "LABEL": "VisualLead", "TYPE": "float", "DEFAULT": 0.06, "MIN": -0.2, "MAX": 0.3},
		{"NAME": "kickLive", "LABEL": "KickLive", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "snareLive", "LABEL": "SnareLive", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "hatLive", "LABEL": "HatLive", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "sub", "LABEL": "Bass", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "air", "LABEL": "HatRaw", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 4.0},
		{"NAME": "kickCount", "LABEL": "KickCount", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 10000000.0},
		{"NAME": "snareCount", "LABEL": "SnareCount", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 10000000.0},
		{"NAME": "hatCount", "LABEL": "HatCount", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 10000000.0},
		{"NAME": "state", "LABEL": "State", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 4.0},
		{"NAME": "stateBars", "LABEL": "StateBars", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 100000.0},
		{"NAME": "barsSinceDrop", "LABEL": "BarsSinceDrop", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 100000.0},
		{"NAME": "tension", "LABEL": "Tension", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "subOut", "LABEL": "SubOut", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 100000.0},
		{"NAME": "toneRise", "LABEL": "ToneRise", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
		{"NAME": "snareRate", "LABEL": "SnareRate", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 128.0},
		{"NAME": "dropFlash", "LABEL": "DropFlash", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "liftFlash", "LABEL": "LiftFlash", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "energy", "LABEL": "Energy", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "subBar", "LABEL": "SubBar", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0}
	]
}*/

const float TAU = 6.2831853;
const vec3 BG = vec3(0.047, 0.043, 0.086);
const vec3 FG = vec3(0.925, 0.92, 1.0);
const vec3 MUTED = vec3(0.61, 0.6, 0.77);
const vec3 C_SUB = vec3(1.0, 0.31, 0.43);
const vec3 C_KICK = vec3(1.0, 0.57, 0.28);
const vec3 C_SNARE = vec3(1.0, 0.82, 0.4);
const vec3 C_PRES = vec3(0.44, 0.89, 0.63);
const vec3 C_HATS = vec3(0.39, 0.78, 1.0);

// @FONT

vec3 stateCol(float s) {
	if (s < 0.5) return vec3(0.5, 0.55, 1.0);      // intro / quiet
	if (s < 1.5) return vec3(0.5, 0.55, 1.0);      // (unused)
	if (s < 2.5) return vec3(1.0, 0.7, 0.28);      // buildup
	if (s < 3.5) return vec3(1.0, 0.31, 0.43);     // drop
	return vec3(0.25, 0.82, 0.79);                 // breakdown
}
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
float band(float d, float w) { return 1.0 - smoothstep(w * 0.5 - 0.75, w * 0.5 + 0.75, abs(d)); }
float disc(vec2 q, float r) { return 1.0 - smoothstep(r - 1.0, r + 1.0, length(q)); }
float rect(vec2 p, vec2 a, vec2 b) { return step(a.x, p.x) * step(p.x, b.x) * step(a.y, p.y) * step(p.y, b.y); }
float segment(vec2 p, vec2 a, vec2 b, float w) {
	vec2 pa = p - a, ba = b - a;
	float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
	return band(length(pa - ba * h), w);
}
vec3 over(vec3 c, vec3 col, float a) { return mix(c, col, clamp(a, 0.0, 1.0)); }

void main() {
	vec2 P = isf_FragNormCoord * RENDERSIZE;
	float W = RENDERSIZE.x, H = RENDERSIZE.y, k = H / 1080.0;
	float fs = 5.0 * k;                       // body text cell
	vec3 sc = stateCol(state);
	// kick on the predicted beat while the clock is locked and kicks are running (no detection delay);
	// otherwise the live band. VisualLead moves the drawn beat earlier to match what you hear.
	float spb = 60.0 / max(bpm, 60.0);
	float sinceBeat = fract(phase + visualLead / spb) * spb;
	float predicted = exp(-sinceBeat / 0.12);
	float useBeat = step(0.6, lock) * step(sinceKick, 1.3);
	float kick = mix(kickLive, predicted, useBeat);
	float snare = snareLive, hat = hatLive;
	vec3 col = BG;

	// ambience: state colour breathing with energy, flashes on drop and lift
	vec2 C = vec2(W * 0.42, H * 0.52);
	float R = H * 0.27;
	col += sc * (0.05 + 0.18 * energy) * exp(-pow(length(P - C) / (H * 0.75), 2.0));
	col += C_SUB * dropFlash * 0.25 + FG * liftFlash * 0.12;

	// ---- hats: sparks overhead -------------------------------------------------
	float topY = H * 0.84;
	if (P.y > topY) {
		vec2 cell = floor(P / (24.0 * k));
		vec2 f = fract(P / (24.0 * k)) - 0.5;
		float hh = hash(cell + floor(TIME * 14.0));
		vec2 off = vec2(hash(cell + 3.1), hash(cell + 7.7)) - 0.5;
		float on = step(1.0 - hat * 0.55, hh);
		col += C_HATS * on * (1.0 - smoothstep(0.03, 0.12, length(f - off * 0.6))) * 1.4;
		col += C_HATS * clamp(air - 0.5, 0.0, 1.0) * 0.08;       // crash wash
	}

	// ---- sub-bass floor --------------------------------------------------------
	float wl = 260.0 * k, fy = H * 0.07, amp = H * 0.035 * subBar;   // 2-beat sub-bass level: calmer than the raw band
	float wy = fy + sin(P.x / wl * TAU - TIME * 2.4) * amp;
	if (P.y < wy) col = over(col, C_SUB, 0.13 + 0.25 * sub);
	col = over(col, C_SUB, band(P.y - wy, 3.0 * k));

	// ---- beat orbit ------------------------------------------------------------
	vec2 q = P - C;
	float r = length(q);
	float ang = fract(atan(q.x, q.y) / TAU);          // 0 at top, clockwise
	float barPhase = mod(phase - downSlot, 4.0) / 4.0;
	float beatInBar = floor(barPhase * 4.0);
	float free = step(lock, 0.45);
	float dash = mix(1.0, step(0.5, fract(ang * 48.0)), free);
	col = over(col, FG, band(r - R, 2.0 * k) * dash * mix(0.22, 0.4, free));
	col = over(col, C_KICK, band(r - R, 6.0 * k) * step(ang, barPhase) * 0.6);
	for (int i = 0; i < 4; i++) {
		float a = float(i) * TAU / 4.0;
		vec2 m = C + R * vec2(sin(a), cos(a));
		float big = float(i == 0);
		float rad = mix(6.0, 11.0, big) * k;
		vec3 mc = mix(FG, C_SUB, big);
		float passed = step(float(i), beatInBar);
		col = over(col, BG, disc(P - m, rad));
		col = over(col, mc, disc(P - m, rad) * passed);
		col = over(col, mix(MUTED, C_SUB, big), band(length(P - m) - rad, 2.0 * k));
	}
	// bar 1 label
	vec2 m0 = C + vec2(16.0 * k, R + 10.0 * k);
	col = over(col, downSet > 0.5 ? C_PRES : MUTED, downSet > 0.5 ? TEXT(P, m0, fs, "BAR 1") : TEXT(P, m0, fs, "BAR 1 GUESS"));
	// planet
	vec2 pl = C + R * vec2(sin(barPhase * TAU), cos(barPhase * TAU));
	col += C_KICK * 0.6 * exp(-pow(length(P - pl) / (22.0 * k), 2.0));
	col = over(col, FG, disc(P - pl, 7.0 * k));

	// snare burst between sun and orbit
	float sr = R * 0.2 * (1.0 + 0.45 * kick);
	float ray = step(0.55, fract(ang * 24.0 + TIME * 0.05));
	float rin = R * 0.36, rout = rin + snare * R * 0.45 * (0.6 + 0.4 * hash(vec2(floor(ang * 24.0), 1.0)));
	col = over(col, C_SNARE, ray * step(rin, r) * step(r, rout) * (0.3 + 0.7 * snare));

	// kick heart with a shock ring
	float tk = -0.12 * log(max(kick, 0.0001));
	col = over(col, C_KICK, band(r - sr * (1.0 + tk * 2.2), 2.0 * k) * clamp(1.0 - tk / 0.8, 0.0, 1.0));
	col += C_KICK * (0.2 + 0.6 * kick) * exp(-pow(r / (sr * 2.4), 2.0));
	col = over(col, C_KICK, disc(q, sr) * 0.92);
	vec2 kl = C + vec2(-23.0 * k, -7.5 * k);
	col = over(col, BG, TEXT(P, kl, 3.0 * k, "KICK"));

	// bars since drop: 16 segments outside the orbit
	float R2 = R * 1.2;
	float seg = floor(ang * 16.0);
	float onSeg = downSet > 0.5 ? step(seg, mod(barsSinceDrop, 16.0)) : 0.0;
	float gapS = step(0.12, fract(ang * 16.0)) * step(fract(ang * 16.0), 0.88);
	col = over(col, mix(FG * 0.18, C_SUB, onSeg), band(r - R2, mix(3.0, 5.0, onSeg) * k) * gapS);

	// ---- left: readouts -----------------------------------------------------------
	float x0 = W * 0.04;
	vec2 o = vec2(x0, H * 0.74);
	col = over(col, FG, num(P, o, 9.0 * k, bpm, 1.0));
	col = over(col, MUTED, TEXT(P, o + vec2(21.0 * 9.0 * k, 0.0), fs, "BPM"));
	o.y -= 70.0 * k;
	if (free > 0.5) col = over(col, C_SNARE, TEXT(P, o, fs, "FREE RUNNING"));
	else {
		col = over(col, C_PRES, TEXT(P, o, fs, "LOCKED"));
		col = over(col, C_PRES, num(P, o + vec2(28.0 * fs, 0.0), fs, floor(lock * 100.0), 0.0));
		col = over(col, C_PRES, TEXT(P, o + vec2(40.0 * fs, 0.0), fs, "%"));
	}
	o.y -= 40.0 * k;
	col = over(col, FG, TEXT(P, o, fs, "BEAT"));
	col = over(col, FG, num(P, o + vec2(20.0 * fs, 0.0), fs, beatInBar + 1.0, 0.0));
	col = over(col, MUTED, TEXT(P, o + vec2(28.0 * fs, 0.0), fs, "OF 4"));
	o.y -= 40.0 * k;
	col = over(col, MUTED, TEXT(P, o, fs, "NUDGE"));
	col = over(col, MUTED, num(P, o + vec2(24.0 * fs, 0.0), fs, nudge * 60000.0 / max(bpm, 60.0), 0.0));
	col = over(col, MUTED, TEXT(P, o + vec2(44.0 * fs, 0.0), fs, "MS"));
	o.y -= 40.0 * k;
	if (downSet > 0.5) {
		col = over(col, MUTED, TEXT(P, o, fs, "SINCE DROP"));
		col = over(col, FG, num(P, o + vec2(44.0 * fs, 0.0), fs, barsSinceDrop, 0.0));
	} else col = over(col, MUTED, TEXT(P, o, fs, "NO DROP YET"));
	o.y -= 64.0 * k;
	col = over(col, C_KICK, TEXT(P, o, fs, "KICK"));   col = over(col, C_KICK, num(P, o + vec2(28.0 * fs, 0.0), fs, kickCount, 0.0));
	o.y -= 32.0 * k;
	col = over(col, C_SNARE, TEXT(P, o, fs, "SNARE")); col = over(col, C_SNARE, num(P, o + vec2(28.0 * fs, 0.0), fs, snareCount, 0.0));
	o.y -= 32.0 * k;
	col = over(col, C_HATS, TEXT(P, o, fs, "HATS"));   col = over(col, C_HATS, num(P, o + vec2(28.0 * fs, 0.0), fs, hatCount, 0.0));
	col = over(col, C_SUB, TEXT(P, vec2(x0, fy + H * 0.07), fs, "SUB-BASS 20-80 HZ"));
	col = over(col, C_HATS, TEXT(P, vec2(x0, H * 0.95), fs, "HATS 5-20 KHZ"));
	col = over(col, C_SNARE, TEXT(P, C + vec2(-R * 0.36, -R * 0.36 - 40.0 * k), 3.0 * k, "SNARE 1.2-5 KHZ"));

	// ---- right: drop radar -----------------------------------------------------------
	vec2 G = vec2(W * 0.82, H * 0.6);
	float gr = H * 0.17;
	vec2 g = P - G;
	float gl = length(g);
	float ga = atan(g.x, g.y);                      // -pi..pi, 0 = up
	float gt = clamp((ga + 1.5708) / 3.14159, 0.0, 1.0);   // 0 left .. 1 right over the top
	float upper = step(0.0, g.y + 2.0 * k);
	vec3 grad = mix(vec3(0.25, 0.82, 0.79), vec3(1.0, 0.7, 0.28), smoothstep(0.0, 0.6, gt));
	grad = mix(grad, C_SUB, smoothstep(0.6, 1.0, gt));
	col = over(col, FG * 0.25, band(gl - gr, 14.0 * k) * upper * 0.35);
	col = over(col, grad, band(gl - gr, 14.0 * k) * upper * step(gt, tension));
	float tickA = fract(gt * 10.0 + 0.5) - 0.5;
	col = over(col, FG, step(abs(tickA), 0.04) * step(gr - 26.0 * k, gl) * step(gl, gr - 16.0 * k) * upper * 0.4);
	float na = -1.5708 + 3.14159 * tension;
	col = over(col, FG, segment(P, G, G + (gr - 26.0 * k) * vec2(sin(na), cos(na)), 3.0 * k));
	col = over(col, FG, disc(g, 5.0 * k));
	float ts = 7.0 * k;
	vec2 to = G + vec2(-gr, -40.0 * k);
	if (state < 1.5) col = over(col, sc, energy < 0.02 ? TEXT(P, to, ts, "LISTENING") : TEXT(P, to, ts, "INTRO"));
	else if (state < 2.5) { col = over(col, sc, TEXT(P, to, ts, "BUILDUP")); col = over(col, sc, num(P, to + vec2(32.0 * ts, 0.0), ts, stateBars + 1.0, 0.0)); }
	else if (state < 3.5) col = over(col, sc, TEXT(P, to, ts, "DROP"));
	else { col = over(col, sc, TEXT(P, to, ts, "BREAKDOWN")); col = over(col, sc, num(P, to + vec2(40.0 * ts, 0.0), ts, stateBars + 1.0, 0.0)); }
	vec2 so = to + vec2(0.0, -30.0 * k);
	if (state > 1.5 && state < 2.5) col = over(col, MUTED, TEXT(P, so, fs, "DROP CAN COME ANY BAR"));
	else if (state > 2.5 && state < 3.5) col = over(col, MUTED, liftFlash > 0.3 ? TEXT(P, so, fs, "SECOND HIT SAME DROP") : TEXT(P, so, fs, "SUB-BASS BACK ON THE BAR"));
	else if (state > 3.5) col = over(col, MUTED, TEXT(P, so, fs, "WAITING FOR A RISER"));
	else col = over(col, MUTED, TEXT(P, so, fs, "NO DROP YET IN THIS TRACK"));
	// shockwave from the gauge on drop / lift
	float fl = max(dropFlash, liftFlash);
	float wave = 1.0 - fl;
	col = over(col, dropFlash > liftFlash ? C_SUB : FG, band(gl - gr * (0.3 + 1.8 * wave), (2.0 + 8.0 * fl) * k) * fl);

	// cue rows
	vec2 c0 = vec2(W * 0.69, H * 0.33);
	float cw = W * 0.26;
	float cue1 = clamp(subOut / 4.0, 0.0, 1.0), cue2 = clamp(toneRise / 0.15, 0.0, 1.0), cue3 = clamp(snareRate / 16.0, 0.0, 1.0);
	float ok1 = step(2.0, subOut), ok2 = step(0.06, toneRise), ok3 = step(6.0, snareRate);
	col = over(col, mix(MUTED, FG, ok1), TEXT(P, c0, fs, "SUB-BASS OUT"));
	col = over(col, MUTED, num(P, c0 + vec2(cw - 40.0 * fs, 0.0), fs, subOut, 0.0));
	col = over(col, MUTED, TEXT(P, c0 + vec2(cw - 28.0 * fs, 0.0), fs, "BARS"));
	col = over(col, FG * 0.12, rect(P, c0 + vec2(0.0, -16.0 * k), c0 + vec2(cw, -10.0 * k)));
	col = over(col, C_SUB, rect(P, c0 + vec2(0.0, -16.0 * k), c0 + vec2(cw * cue1, -10.0 * k)));
	c0.y -= 64.0 * k;
	col = over(col, mix(MUTED, FG, ok2), TEXT(P, c0, fs, "GETTING BRIGHTER"));
	col = over(col, MUTED, num(P, c0 + vec2(cw - 28.0 * fs, 0.0), fs, toneRise, 2.0));
	col = over(col, FG * 0.12, rect(P, c0 + vec2(0.0, -16.0 * k), c0 + vec2(cw, -10.0 * k)));
	col = over(col, C_PRES, rect(P, c0 + vec2(0.0, -16.0 * k), c0 + vec2(cw * cue2, -10.0 * k)));
	c0.y -= 64.0 * k;
	col = over(col, mix(MUTED, FG, ok3), TEXT(P, c0, fs, "SNARE ROLL"));
	vec2 rl = c0 + vec2(cw - 24.0 * fs, 0.0);
	if (snareRate < 1.5) col = over(col, MUTED, TEXT(P, rl, fs, "NONE"));
	else if (snareRate < 5.0) col = over(col, MUTED, TEXT(P, rl, fs, "4THS"));
	else if (snareRate < 10.0) col = over(col, MUTED, TEXT(P, rl, fs, "8THS"));
	else if (snareRate < 20.0) col = over(col, MUTED, TEXT(P, rl, fs, "16THS"));
	else col = over(col, MUTED, TEXT(P, rl, fs, "32NDS"));
	col = over(col, FG * 0.12, rect(P, c0 + vec2(0.0, -16.0 * k), c0 + vec2(cw, -10.0 * k)));
	col = over(col, C_SNARE, rect(P, c0 + vec2(0.0, -16.0 * k), c0 + vec2(cw * cue3, -10.0 * k)));

	gl_FragColor = vec4(col, 1.0);
}
