/*{
	"DESCRIPTION": "Music X-Ray Tempo: how tempo is found. Kick hits of the last 3 s, a histogram of the time between kicks (slowly forgetting, so it follows a DJ set), and every interval as BPM folded into one tempo octave.",
	"CREDIT": "mmv-skills music-xray",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Audio Visualizer"],
	"INPUTS": [
		{"NAME": "pulse", "LABEL": "KickPulseLag", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "ioi", "LABEL": "Ioi", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 100000.0},
		{"NAME": "kickCount", "LABEL": "KickCount", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 10000000.0},
		{"NAME": "bpm", "LABEL": "Bpm", "TYPE": "float", "DEFAULT": 120.0, "MIN": 0.0, "MAX": 400.0},
		{"NAME": "lock", "LABEL": "Lock", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "tempoLo", "LABEL": "TempoLo", "TYPE": "float", "DEFAULT": 90.0, "MIN": 40.0, "MAX": 200.0},
		{"NAME": "memory", "LABEL": "Memory", "TYPE": "float", "DEFAULT": 30.0, "MIN": 2.0, "MAX": 300.0}
	],
	"PASSES": [
		{"TARGET": "hist", "PERSISTENT": true, "FLOAT": true, "WIDTH": "48", "HEIGHT": "1"},
		{"TARGET": "ring", "PERSISTENT": true, "FLOAT": true, "WIDTH": "24", "HEIGHT": "1"},
		{}
	]
}*/

const float NBIN = 48.0;
const float NRING = 24.0;
const float LO = 0.15;
const float HI = 1.1;
const vec3 BG = vec3(0.047, 0.043, 0.086);
const vec3 FG = vec3(0.925, 0.92, 1.0);
const vec3 MUTED = vec3(0.61, 0.6, 0.77);
const vec3 C_KICK = vec3(1.0, 0.57, 0.28);
const vec3 C_SNARE = vec3(1.0, 0.82, 0.4);
const vec3 C_PRES = vec3(0.44, 0.89, 0.63);

// @FONT

float band(float d, float w) { return 1.0 - smoothstep(w * 0.5 - 0.75, w * 0.5 + 0.75, abs(d)); }
vec3 over(vec3 c, vec3 col, float a) { return mix(c, col, clamp(a, 0.0, 1.0)); }
vec4 ringAt(float j) { return IMG_NORM_PIXEL(ring, vec2((j + 0.5) / NRING, 0.5)); }
float histAt(float b) { return IMG_NORM_PIXEL(hist, vec2((b + 0.5) / NBIN, 0.5)).r; }
float foldBpm(float b) { return b / pow(2.0, floor(log2(b / tempoLo))); }

void main() {
	vec2 uv = isf_FragNormCoord;

	// pass 0: interval histogram, forgetting with a time constant of `memory` seconds
	if (PASSINDEX == 0) {
		if (FRAMEINDEX == 0) { gl_FragColor = vec4(0.0); return; }
		float b = floor(uv.x * NBIN);
		float v = IMG_NORM_PIXEL(hist, uv).r * exp(-TIMEDELTA / memory);
		float hb = floor((ioi - LO) / (HI - LO) * NBIN);
		if (pulse > 0.5 && ioi > LO && ioi < HI && abs(hb - b) < 0.5) v += 1.0;
		gl_FragColor = vec4(v, 0.0, 0.0, 1.0);
		return;
	}
	// pass 1: ring of the last 24 kicks (time, interval before it, valid)
	if (PASSINDEX == 1) {
		if (FRAMEINDEX == 0) { gl_FragColor = vec4(0.0); return; }
		float j = floor(uv.x * NRING);
		vec4 prev = IMG_NORM_PIXEL(ring, uv);
		gl_FragColor = (pulse > 0.5 && abs(mod(kickCount, NRING) - j) < 0.5) ? vec4(TIME, ioi, 1.0, 0.0) : prev;
		return;
	}

	vec2 P = uv * RENDERSIZE;
	float W = RENDERSIZE.x, H = RENDERSIZE.y, k = H / 1080.0, fs = 5.0 * k;
	float xa = W * 0.05, xb = W * 0.95, wd = xb - xa;
	vec3 col = BG;

	// header
	col = over(col, FG, TEXT(P, vec2(xa, H * 0.92), 7.0 * k, "TEMPO LENS"));
	col = over(col, FG, num(P, vec2(xb - 64.0 * 10.0 * k / 1.0 * 0.5, H * 0.9), 10.0 * k, bpm, 1.0));
	col = over(col, MUTED, TEXT(P, vec2(xb - 12.0 * fs, H * 0.86), fs, "BPM"));
	if (lock > 0.45) { col = over(col, C_PRES, TEXT(P, vec2(xb - 24.0 * fs, H * 0.82), fs, "LOCKED")); }
	else col = over(col, C_SNARE, TEXT(P, vec2(xb - 48.0 * fs, H * 0.82), fs, "FREE RUNNING"));

	// kick strip: the last 3 seconds, now at the right
	float sy = H * 0.76, win = 3.0;
	col = over(col, MUTED, TEXT(P, vec2(xa, sy + 40.0 * k), fs, "KICK HITS  LAST 3 S  MS BETWEEN THEM"));
	col = over(col, FG, band(P.y - sy, 1.0 * k) * step(xa, P.x) * step(P.x, xb) * 0.2);
	bool inLabels = P.y > sy - 34.0 * k && P.y < sy - 20.0 * k + 5.0 * 4.0 * k;
	for (int i = 0; i < 24; i++) {
		vec4 r = ringAt(float(i));
		float age = TIME - r.r;
		if (r.b < 0.5 || age < 0.0 || age > win) continue;
		float x = xb - age / win * wd;
		col = over(col, C_KICK, step(abs(P.x - x), 1.5 * k) * step(abs(P.y - sy), 14.0 * k));
		float span = r.g / win * wd;
		if (inLabels && span > 70.0 * k && r.g < win && x - span > xa) {
			vec2 lo = vec2(x - span * 0.5 - 6.0 * 4.0 * k, sy - 32.0 * k);
			col = over(col, MUTED, num(P, lo, 4.0 * k, r.g * 1000.0, 0.0));
		}
	}

	// interval histogram
	float hy = H * 0.36, hh = H * 0.26;
	col = over(col, MUTED, TEXT(P, vec2(xa, hy + hh + 16.0 * k), fs, "TIME BETWEEN KICKS"));
	if (P.y > hy - 2.0 * k && P.y < hy + hh) {
		float mx = 0.0001, pk = 0.0;
		for (int i = 0; i < 48; i++) { float v = histAt(float(i)); if (v > mx) { mx = v; pk = float(i); } }
		float b = floor((P.x - xa) / wd * NBIN);
		if (b >= 0.0 && b < NBIN) {
			float v = histAt(b) / mx;
			float inBar = step(0.12, fract((P.x - xa) / wd * NBIN)) * step(P.y, hy + v * hh) * step(hy, P.y);
			col = over(col, abs(b - pk) < 0.5 ? C_KICK : FG * 0.38, inBar);
		}
		col = over(col, FG, band(P.y - hy, 1.0 * k) * step(xa, P.x) * step(P.x, xb) * 0.25);
	}
	for (int i = 1; i <= 4; i++) {
		float s = float(i) * 0.25;
		vec2 lo = vec2(xa + (s - LO) / (HI - LO) * wd - 12.0 * 4.0 * k, hy - 26.0 * k);
		col = over(col, MUTED, num(P, lo, 4.0 * k, s * 1000.0, 0.0));
		col = over(col, MUTED, TEXT(P, lo + vec2(17.0 * 4.0 * k, 0.0), 4.0 * k, "MS"));
	}

	// BPM axis: each interval as BPM, folded into [TempoLo, 2*TempoLo)
	float ay = H * 0.12, bl = 50.0, bh = 270.0;
	float wx0 = xa + (tempoLo - bl) / (bh - bl) * wd, wx1 = xa + (2.0 * tempoLo - bl) / (bh - bl) * wd;
	col = over(col, C_PRES, step(wx0, P.x) * step(P.x, wx1) * step(ay - 4.0 * k, P.y) * step(P.y, ay + 60.0 * k) * 0.14);
	col = over(col, FG, band(P.y - (ay - 4.0 * k), 1.0 * k) * step(xa, P.x) * step(P.x, xb) * 0.25);
	for (int i = 0; i < 7; i++) {
		float bv = 60.0 + 30.0 * float(i);
		col = over(col, MUTED, num(P, vec2(xa + (bv - bl) / (bh - bl) * wd - 6.0 * 4.0 * k, ay - 30.0 * k), 4.0 * k, bv, 0.0));
	}
	vec2 fo = vec2(wx0 + 4.0 * k, ay + 66.0 * k);
	col = over(col, C_PRES, TEXT(P, fo, 4.0 * k, "FOLDED INTO"));
	col = over(col, C_PRES, num(P, fo + vec2(48.0 * 4.0 * k, 0.0), 4.0 * k, tempoLo, 0.0));
	col = over(col, C_PRES, TEXT(P, fo + vec2(60.0 * 4.0 * k, 0.0), 4.0 * k, "-"));
	col = over(col, C_PRES, num(P, fo + vec2(64.0 * 4.0 * k, 0.0), 4.0 * k, 2.0 * tempoLo, 0.0));
	col = over(col, C_PRES, TEXT(P, fo + vec2(80.0 * 4.0 * k, 0.0), 4.0 * k, "BPM"));
	if (P.y > ay - 6.0 * k && P.y < ay + 60.0 * k) {
		for (int i = 0; i < 24; i++) {
			vec4 r = ringAt(float(i));
			if (r.b < 0.5 || r.g <= 0.0) continue;
			float raw = 60.0 / r.g;
			if (raw < bl || raw > bh) continue;
			float fb = foldBpm(raw);
			float x0 = xa + (raw - bl) / (bh - bl) * wd, x1 = xa + (fb - bl) / (bh - bl) * wd;
			float y = ay + mod(float(i), 4.0) * 5.0 * k;
			bool moved = abs(x1 - x0) > 3.0 * k;
			if (moved) {   // flat arc from the raw BPM to its folded place
				float lo = min(x0, x1), hi = max(x0, x1);
				float t = clamp((P.x - lo) / (hi - lo), 0.0, 1.0);
				col = over(col, C_SNARE, band(P.y - (y + 38.0 * k * sin(3.14159 * t)), 1.5 * k) * step(lo, P.x) * step(P.x, hi) * 0.6);
			}
			col = over(col, moved ? C_SNARE : C_KICK, 1.0 - smoothstep(2.5 * k, 3.5 * k, length(P - vec2(x0, y))));
		}
	}
	float bx = xa + (bpm - bl) / (bh - bl) * wd;
	col = over(col, FG, step(abs(P.x - bx), 1.2 * k) * step(ay - 10.0 * k, P.y) * step(P.y, ay + 56.0 * k));

	gl_FragColor = vec4(col, 1.0);
}
