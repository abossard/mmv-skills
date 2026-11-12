/*{
	"DESCRIPTION": "Music X-Ray Terrain: the live spectrum as a landscape flowing towards the viewer, over an endless song river (loudness as width, live section state as colour, pins where the detector noticed a drop, lift, buildup, breakdown or beat entry). No start or end: both scroll forever.",
	"CREDIT": "mmv-skills music-xray",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Audio Visualizer"],
	"INPUTS": [
		{"NAME": "fftImage", "LABEL": "Source", "TYPE": "audioFFT"},
		{"NAME": "gain", "LABEL": "Gain", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.05, "MAX": 4.0},
		{"NAME": "energy", "LABEL": "Energy", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "energySlow", "LABEL": "EnergySlow", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "sub", "LABEL": "Bass", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "state", "LABEL": "State", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 4.0},
		{"NAME": "eventCode", "LABEL": "EventCode", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 8.0},
		{"NAME": "terrainTick", "LABEL": "TerrainTick", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "riverTick", "LABEL": "RiverTick", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "kick", "LABEL": "Kick", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "subLow", "LABEL": "SubLow", "TYPE": "float", "DEFAULT": 0.3, "MIN": 0.0, "MAX": 1.0}
	],
	"PASSES": [
		{"TARGET": "spec", "PERSISTENT": true, "FLOAT": true, "WIDTH": "96", "HEIGHT": "40"},
		{"TARGET": "river", "PERSISTENT": true, "FLOAT": true, "WIDTH": "600", "HEIGHT": "2"},
		{}
	]
}*/

const float NB = 96.0;
const float ROWS = 40.0;
const float COLS = 600.0;
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
	if (s < 0.5) return vec3(0.5, 0.55, 1.0);
	if (s < 1.5) return vec3(0.6, 0.63, 0.78);
	if (s < 2.5) return vec3(1.0, 0.7, 0.28);
	if (s < 3.5) return vec3(1.0, 0.31, 0.43);
	return vec3(0.25, 0.82, 0.79);
}
// colour along the frequency axis: sub, bass, mids, presence, air
vec3 bandCol(float u) {
	vec3 c = mix(C_SUB, C_KICK, smoothstep(0.05, 0.25, u));
	c = mix(c, C_SNARE, smoothstep(0.3, 0.45, u));
	c = mix(c, C_PRES, smoothstep(0.5, 0.65, u));
	return mix(c, C_HATS, smoothstep(0.72, 0.85, u));
}
float uOf(float f) { return log(f / 30.0) / log(16000.0 / 30.0); }
float band(float d, float w) { return 1.0 - smoothstep(w * 0.5 - 0.75, w * 0.5 + 0.75, abs(d)); }
vec3 over(vec3 c, vec3 col, float a) { return mix(c, col, clamp(a, 0.0, 1.0)); }
vec4 riverAt(float c, float row) { return IMG_NORM_PIXEL(river, vec2((c + 0.5) / COLS, (row + 0.5) / 2.0)); }
float specAt(float u, float row) { return IMG_NORM_PIXEL(spec, vec2(u * (NB - 1.0) / NB + 0.5 / NB, (row + 0.5) / ROWS)).r; }

float pinLabel(vec2 P, vec2 o, float s, float code) {
	if (code < 1.5) return TEXT(P, o, s, "DROP");
	if (code < 2.5) return TEXT(P, o, s, "LIFT");
	if (code < 3.5) return TEXT(P, o, s, "BUILDUP");
	if (code < 4.5) return TEXT(P, o, s, "BREAKDOWN");
	if (code < 5.5) return TEXT(P, o, s, "BEAT IN");
	return TEXT(P, o, s, "INTRO");
}
vec3 pinCol(float code) {
	if (code < 1.5) return C_SUB;
	if (code < 2.5) return FG;
	if (code < 3.5) return vec3(1.0, 0.7, 0.28);
	if (code < 4.5) return vec3(0.25, 0.82, 0.79);
	if (code < 5.5) return vec3(0.6, 0.63, 0.78);
	return vec3(0.5, 0.55, 1.0);
}

void main() {
	vec2 uv = isf_FragNormCoord;

	// ---- pass 0: spectrum history. Row 0 is live, older rows move back one step per TerrainTick ----
	if (PASSINDEX == 0) {
		if (FRAMEINDEX == 0) { gl_FragColor = vec4(0.0); return; }
		float row = floor(uv.y * ROWS);
		vec4 prev = IMG_NORM_PIXEL(spec, uv);
		if (row > 0.5) { gl_FragColor = terrainTick > 0.5 ? IMG_NORM_PIXEL(spec, uv - vec2(0.0, 1.0 / ROWS)) : prev; return; }
		// row 0: r = drawn height, g = this bin's slow average magnitude (auto level)
		float u = (floor(uv.x * NB) + 0.5) / NB;
		float x = 30.0 * pow(16000.0 / 30.0, u) / 22050.0;   // FFT x is linear up to Nyquist
		float m = 0.0;
		for (int i = -2; i <= 2; i++) m += IMG_NORM_PIXEL(fftImage, vec2(x * (1.0 + 0.04 * float(i)), 0.5)).r;
		m = max(m / 5.0, 0.0);
		float avg = FRAMEINDEX < 2 ? m : mix(prev.g, m, 0.004);          // about 4 s at 60 fps
		float level = 0.0;
		for (int i = 0; i < 96; i++) level += IMG_NORM_PIXEL(spec, vec2((float(i) + 0.5) / NB, 0.5 / ROWS)).g;
		level = level / NB + 0.00001;
		// the song's own loudness divides out, so loud masters do not clip; soft knee instead of a flat top
		float v = 1.0 - exp(-gain * m * (0.6 + 1.2 * u) / level);
		float h = v > prev.r ? mix(prev.r, v, 0.45) : mix(prev.r, v, 0.1);   // quick rise, slow fall: calmer
		gl_FragColor = vec4(h, avg, 0.0, 1.0);
		return;
	}

	// ---- pass 1: river history. Last column is live, everything moves left one column per RiverTick ----
	if (PASSINDEX == 1) {
		if (FRAMEINDEX == 0) { gl_FragColor = vec4(0.0); return; }
		float c = floor(uv.x * COLS), row = floor(uv.y * 2.0);
		vec4 prev = IMG_NORM_PIXEL(river, uv);
		bool last = c > COLS - 1.5;
		// row 1: r = loudest fast energy in the column, g = 1 once the column holds data
		if (riverTick > 0.5) {
			if (!last) gl_FragColor = IMG_NORM_PIXEL(river, uv + vec2(1.0 / COLS, 0.0));
			else gl_FragColor = row < 0.5 ? vec4(energySlow, sub, state, 0.0) : vec4(energy, 1.0, 0.0, 0.0);
		} else if (last) {
			gl_FragColor = row < 0.5 ? vec4(energySlow, sub, state, eventCode) : vec4(max(prev.r, energy), 1.0, 0.0, 0.0);
		} else gl_FragColor = prev;
		return;
	}

	// ---- pass 2: draw ----
	vec2 P = uv * RENDERSIZE;
	float W = RENDERSIZE.x, H = RENDERSIZE.y, k = H / 1080.0, fs = 4.0 * k;
	vec3 col = BG;

	// terrain: rows from front (newest) to back; the first row whose fill covers the pixel wins
	float frontY = H * 0.44;
	for (int i = 0; i < 40; i++) {
		float d = float(i) / (ROWS - 1.0);
		float y0 = mix(frontY, H * 0.86, d);
		if (P.y < y0 - 1.0) break;
		float xa = mix(W * 0.05, W * 0.22, d), xb = mix(W * 0.95, W * 0.78, d);
		if (P.x < xa || P.x > xb) continue;
		float u = (P.x - xa) / (xb - xa);
		float ridge = y0 + specAt(u, float(i)) * mix(H * 0.36, H * 0.09, d);
		float lw = (i == 0 ? 3.0 : 1.4) * k;
		if (P.y <= ridge + lw) {
			float fade = mix(1.0, 0.12, pow(d, 0.8));
			col = BG + bandCol(u) * 0.05 * (1.0 - d);
			col = over(col, bandCol(u), band(P.y - ridge, lw) * fade);
			break;
		}
	}
	// band names under the front edge
	float xa0 = W * 0.05, xb0 = W * 0.95, ly = frontY - 16.0 * k;
	float u = clamp((P.x - xa0) / (xb0 - xa0), 0.0, 1.0);
	float edges = step(abs(P.y - (frontY - 6.0 * k)), 1.5 * k) * step(xa0, P.x) * step(P.x, xb0);
	float gapB = 1.0 - step(abs(u - uOf(80.0)), 0.002) - step(abs(u - uOf(320.0)), 0.002) - step(abs(u - uOf(1200.0)), 0.002) - step(abs(u - uOf(5000.0)), 0.002);
	col = over(col, bandCol(u), edges * gapB);
	vec2 bo = vec2(mix(xa0, xb0, uOf(36.0)), ly - 5.0 * fs);
	col = over(col, C_SUB, TEXT(P, bo, fs, "SUB"));
	bo.x = mix(xa0, xb0, uOf(130.0)); col = over(col, C_KICK, TEXT(P, bo, fs, "BASS"));
	bo.x = mix(xa0, xb0, uOf(480.0)); col = over(col, C_SNARE, TEXT(P, bo, fs, "MIDS"));
	bo.x = mix(xa0, xb0, uOf(1700.0)); col = over(col, C_PRES, TEXT(P, bo, fs, "PRESENCE"));
	bo.x = mix(xa0, xb0, uOf(7500.0)); col = over(col, C_HATS, TEXT(P, bo, fs, "AIR"));
	// instrument tags over the front ridge
	float ts = 5.0 * k;
	vec2 tg = vec2(mix(xa0, xb0, uOf(60.0)) - 8.0 * ts, frontY + specAt(uOf(60.0), 0.0) * H * 0.36 + 14.0 * k);
	col = over(col, C_KICK, TEXT(P, tg, ts, "KICK") * smoothstep(0.4, 0.6, kick));
	col = over(col, MUTED, TEXT(P, vec2(W * 0.03, H * 0.95), fs, "SPECTRAL TERRAIN  NEWEST AT THE FRONT"));

	// river: oldest left, now right, about 4 minutes wide
	float ra = W * 0.03, rb = W * 0.97, cy = H * 0.2;
	float c = floor((P.x - ra) / (rb - ra) * COLS);
	vec4 s1c = riverAt(clamp(c, 0.0, COLS - 1.0), 1.0);
	if (c >= 0.0 && c < COLS && s1c.g > 0.5) {
		vec4 s0 = riverAt(c, 0.0), s1 = s1c;
		float hw = 2.0 * k + s0.r * H * 0.14, hf = 2.0 * k + s1.r * H * 0.14;
		col = over(col, FG, step(abs(P.y - cy), hf) * 0.1);
		col = over(col, stateCol(s0.b), step(abs(P.y - cy), hw) * 0.88);
		// sub-bass lane and its "low" line
		float base = H * 0.03, hh = H * 0.06;
		col = over(col, C_SUB, band(P.y - (base + s0.g * hh), 2.0 * k));
		col = over(col, FG, band(P.y - (base + subLow * hh), 1.0 * k) * step(0.5, fract(P.x / (8.0 * k))) * 0.25);
		// pins
		if (s0.a > 0.5) {
			vec3 pc = pinCol(s0.a);
			col = over(col, pc, step(cy, P.y) * step(P.y, H * 0.31) * 0.7);
			col = over(col, pc, 1.0 - smoothstep(4.0 * k, 5.5 * k, length(P - vec2(P.x, cy))));
		}
	}
	// pin labels: look left for an event whose label covers this pixel
	float lbY = H * 0.31;
	if (P.y > lbY && P.y < lbY + 6.0 * fs) {
		float colW = (rb - ra) / COLS;
		for (int j = 0; j < 80; j++) {
			float cj = c - float(j);
			if (cj < 0.0) break;
			float e = riverAt(cj, 0.0).a;
			if (e > 0.5) {
				vec2 lo = vec2(ra + (cj + 0.5) * colW + 4.0 * k, lbY + 2.0 * k);
				col = over(col, pinCol(e), pinLabel(P, lo, fs, e));
				break;
			}
		}
	}
	// now line, time axis, legend
	col = over(col, FG, step(abs(P.x - rb), 1.0 * k) * step(H * 0.02, P.y) * step(P.y, H * 0.34));
	col = over(col, FG, TEXT(P, vec2(rb - 11.0 * fs, H * 0.005), fs, "NOW"));
	col = over(col, MUTED, TEXT(P, vec2(ra, H * 0.005), fs, "-4 MIN"));
	col = over(col, MUTED, TEXT(P, vec2(mix(ra, rb, 0.5) - 12.0 * fs, H * 0.005), fs, "-2 MIN"));
	col = over(col, C_SUB, TEXT(P, vec2(ra, H * 0.105), fs, "SUB-BASS"));
	col = over(col, MUTED, TEXT(P, vec2(ra, H * 0.36), fs, "SONG RIVER  WIDTH: LOUDNESS  COLOUR: WHAT THE DETECTOR HEARS"));
	vec2 lg = vec2(W * 0.55, H * 0.36);
	for (int i = 0; i < 4; i++) {
		vec2 sq = lg + vec2(float(i) * 40.0 * fs, 0.0);
		col = over(col, stateCol(i == 0 ? 0.0 : float(i) + 1.0), step(sq.x, P.x) * step(P.x, sq.x + 4.0 * fs) * step(sq.y, P.y) * step(P.y, sq.y + 4.0 * fs));
	}
	vec2 lt = lg + vec2(6.0 * fs, 0.0);
	col = over(col, MUTED, TEXT(P, lt, fs, "INTRO"));
	lt.x += 40.0 * fs; col = over(col, MUTED, TEXT(P, lt, fs, "BUILDUP"));
	lt.x += 40.0 * fs; col = over(col, MUTED, TEXT(P, lt, fs, "DROP"));
	lt.x += 40.0 * fs; col = over(col, MUTED, TEXT(P, lt, fs, "BREAKDOWN"));

	gl_FragColor = vec4(col, 1.0);
}
