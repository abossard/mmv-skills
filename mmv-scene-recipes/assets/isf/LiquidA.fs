/*{
	"DESCRIPTION": "Liquid A: Neon ink jets in dark water. GPU fluid (vorticity confinement, 14 Jacobi iterations) driven by audio.",
	"CREDIT": "music-xray liquid",
	"ISFVSN": "2.0",
	"CATEGORIES": [
		"Generator",
		"Audio Visualizer"
	],
	"INPUTS": [
		{
			"NAME": "kick",
			"LABEL": "Kick",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "snare",
			"LABEL": "Snare",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "hat",
			"LABEL": "Hat",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "bass",
			"LABEL": "Bass",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "energy",
			"LABEL": "Energy",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "drop",
			"LABEL": "Drop",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "tension",
			"LABEL": "Tension",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 1
		},
		{
			"NAME": "phase",
			"LABEL": "Phase",
			"TYPE": "float",
			"DEFAULT": 0,
			"MIN": 0,
			"MAX": 4
		},
		{
			"NAME": "flowRate",
			"LABEL": "Flow",
			"TYPE": "float",
			"DEFAULT": 1.0,
			"MIN": 0.0,
			"MAX": 3.0
		},
		{
			"NAME": "curlAmt",
			"LABEL": "Swirl",
			"TYPE": "float",
			"DEFAULT": 8.0,
			"MIN": 0.0,
			"MAX": 100.0
		},
		{
			"NAME": "swirlKick",
			"LABEL": "Swirl Kick",
			"TYPE": "float",
			"DEFAULT": 0.6,
			"MIN": 0.0,
			"MAX": 6.0
		},
		{
			"NAME": "viscosity",
			"LABEL": "Viscosity",
			"TYPE": "float",
			"DEFAULT": 0.05,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "velFade",
			"LABEL": "Velocity Fade",
			"TYPE": "float",
			"DEFAULT": 0.45,
			"MIN": 0.0,
			"MAX": 5.0
		},
		{
			"NAME": "pressureKeep",
			"LABEL": "Pressure Keep",
			"TYPE": "float",
			"DEFAULT": 0.97,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "onset",
			"LABEL": "Onset",
			"TYPE": "float",
			"DEFAULT": 0.15,
			"MIN": 0.02,
			"MAX": 0.8
		},
		{
			"NAME": "splatForce",
			"LABEL": "Splat Force",
			"TYPE": "float",
			"DEFAULT": 2.0,
			"MIN": 0.0,
			"MAX": 10.0
		},
		{
			"NAME": "splatSize",
			"LABEL": "Splat Size",
			"TYPE": "float",
			"DEFAULT": 0.12,
			"MIN": 0.01,
			"MAX": 0.3
		},
		{
			"NAME": "fade",
			"LABEL": "Fade",
			"TYPE": "float",
			"DEFAULT": 0.4,
			"MIN": 0.0,
			"MAX": 5.0
		},
		{
			"NAME": "emit",
			"LABEL": "Emit",
			"TYPE": "float",
			"DEFAULT": 1.0,
			"MIN": 0.0,
			"MAX": 4.0
		},
		{
			"NAME": "exposure",
			"LABEL": "Exposure",
			"TYPE": "float",
			"DEFAULT": 2.6,
			"MIN": 0.1,
			"MAX": 6.0
		},
		{
			"NAME": "bloom",
			"LABEL": "Bloom",
			"TYPE": "float",
			"DEFAULT": 0.8,
			"MIN": 0.0,
			"MAX": 4.0
		},
		{
			"NAME": "bloomThresh",
			"LABEL": "Bloom Threshold",
			"TYPE": "float",
			"DEFAULT": 0.6,
			"MIN": 0.0,
			"MAX": 3.0
		},
		{
			"NAME": "shine",
			"LABEL": "Shine",
			"TYPE": "float",
			"DEFAULT": 1.0,
			"MIN": 0.0,
			"MAX": 4.0
		},
		{
			"NAME": "palette",
			"LABEL": "Palette",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "openFlow",
			"LABEL": "Open Flow",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "pourForce",
			"LABEL": "Pour Force",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "pixelate",
			"LABEL": "Pixelate",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 64.0
		},
		{
			"NAME": "zoom",
			"LABEL": "Zoom",
			"TYPE": "float",
			"DEFAULT": 1.0,
			"MIN": 0.25,
			"MAX": 4.0
		},
		{
			"NAME": "zoomKick",
			"LABEL": "Zoom Kick",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 0.5
		},
		{
			"NAME": "cloud",
			"LABEL": "Pixel Cloud",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "cloudSpread",
			"LABEL": "Cloud Spread",
			"TYPE": "float",
			"DEFAULT": 3.0,
			"MIN": 0.0,
			"MAX": 10.0
		},
		{
			"NAME": "cubes",
			"LABEL": "Cubes",
			"TYPE": "float",
			"DEFAULT": 0.6,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "slowMo",
			"LABEL": "Slow Motion",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "paletteSpeed",
			"LABEL": "Palette Speed",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "dropHue",
			"LABEL": "Drop Hue",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 0.5
		},
		{
			"NAME": "pop",
			"LABEL": "Pop",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 1.5
		},
		{
			"NAME": "hdr",
			"LABEL": "HDR",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 2.0
		},
		{
			"NAME": "flare",
			"LABEL": "Flare",
			"TYPE": "float",
			"DEFAULT": 0.0,
			"MIN": 0.0,
			"MAX": 2.0
		},
		{
			"NAME": "speedLimit",
			"LABEL": "Speed Limit",
			"TYPE": "float",
			"DEFAULT": 3000.0,
			"MIN": 20.0,
			"MAX": 3000.0
		},
		{
			"NAME": "flatStyle",
			"LABEL": "Glass",
			"TYPE": "float",
			"DEFAULT": 1.0,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "hdrPop",
			"LABEL": "HDR Pop",
			"TYPE": "float",
			"DEFAULT": 0.15,
			"MIN": 0.0,
			"MAX": 1.0
		},
		{
			"NAME": "popAuto",
			"LABEL": "Pop Auto",
			"TYPE": "float",
			"DEFAULT": 0.7,
			"MIN": 0.0,
			"MAX": 1.5
		}
	],
	"PASSES": [
		{
			"TARGET": "ctl",
			"WIDTH": "5",
			"HEIGHT": "1",
			"PERSISTENT": true,
			"FLOAT": true
		},
		{
			"TARGET": "velF",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "divB",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p0",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p1",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p2",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p3",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p4",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p5",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "p6",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true,
			"PERSISTENT": true
		},
		{
			"TARGET": "vel",
			"PERSISTENT": true,
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "dye",
			"PERSISTENT": true,
			"FLOAT": true
		},
		{
			"TARGET": "b1",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "b2",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{
			"TARGET": "b3",
			"WIDTH": "$WIDTH/4",
			"HEIGHT": "$HEIGHT/4",
			"FLOAT": true
		},
		{}
	]
}*/

#define LIQ_BLOOM 1
#define LIQ_PHASE 0
// ---- Liquid: shared GPU fluid solver (stable fluids, vorticity confinement), one pass per PASSINDEX.
// Velocity is stored in sim cells per second; the sim grid has square cells, so curl/div/pressure use dx = 1.
// Measured in Magic 3.0b6: a shader that samples more than 16 buffers draws NOTHING (no error dialog), and a
// TARGET may appear in one pass only. Budget here: ctl vel velF divB dye b1 b2 b3 + 7 pressure buffers = 15.
// Samplers cannot be function arguments in ISF (IMG_NORM_PIXEL pastes the name), hence one accessor per buffer.

#define PI 3.14159265

float hash11(float n) { return fract(sin(n * 12.9898 + 4.1414) * 43758.5453); }
vec2 hash21(float n) { return fract(sin(vec2(n * 12.9898 + 1.3, n * 78.233 + 7.7)) * 43758.5453); }
float hash12(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
vec3 hsv(float h, float s, float v) {
	vec3 k = clamp(abs(fract(h + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0) - 1.0, 0.0, 1.0);
	return v * mix(vec3(1.0), k, s);
}
float max3(vec3 c) { return max(c.r, max(c.g, c.b)); }
float ASPECT() { return RENDERSIZE.x / RENDERSIZE.y; }
// Slow Motion 1 = almost frozen: the whole simulation and the looks' own clocks run at 3 %
float TS() { return mix(1.0, 0.03, slowMo); }
float DT() { return clamp(TIMEDELTA, 0.0, 0.034) * flowRate * TS(); }

// ctl: 4x1 state texel row, written by pass 0 from the previous frame's row
//  0: kick env prev, kick count, kick fired this frame, TIME of last kick
//  1: snare env prev, snare count, snare fired, swirl envelope
//  2: drop prev, drop count, drop fired, seconds since start
//  3: hat env prev, hat count, hat fired, surge (kick with inertia)
//  4: init marker (4242), frames since init, smoothed drop hue offset: buffers start with leftover memory, frame index is no reliable reset
// persistent buffers may start with undefined memory: drop NaN/Inf/huge values
vec4 clean(vec4 v) { return (any(isnan(v)) || any(isinf(v)) || max(max(abs(v.x), abs(v.y)), max(abs(v.z), abs(v.w))) > 1.0e5) ? vec4(0.0) : v; }
vec4 ctlAt(float i) { return clean(IMG_NORM_PIXEL(ctl, vec2((i + 0.5) / 5.0, 0.5))); }
// frames since this module started (0 on the first frame): every persistent buffer resets while AGE() < 2
float AGE() { vec4 m = ctlAt(4.0); return abs(m.x - 4242.0) < 0.5 ? m.y : 0.0; }

vec2 velAt(vec2 uv) { return clean(IMG_NORM_PIXEL(vel, uv)).xy; }
vec2 velFAt(vec2 uv) { return IMG_NORM_PIXEL(velF, uv).xy; }
float divAt(vec2 uv) { return IMG_NORM_PIXEL(divB, uv).x; }
vec4 dyeAt(vec2 uv) { return clean(IMG_NORM_PIXEL(dye, uv)); }
vec2 SIMTX() { return 1.0 / IMG_SIZE(vel); }
float pLastRaw(vec2 uv);       // generated: the solved pressure
float pPrev(int k, vec2 uv);   // generated: what pressure pass k reads
// open flow (openFlow = 1): left and right edges are open water at pressure 0, so a pour can run through the frame
bool outsideX(vec2 uv) { return openFlow > 0.5 && (uv.x < 0.0 || uv.x > 1.0); }
float pAt(int k, vec2 uv) { return outsideX(uv) ? 0.0 : pPrev(k, uv); }
float pLast(vec2 uv) { return outsideX(uv) ? 0.0 : pLastRaw(uv); }

// gaussian splat weight; p and c in uv, r in fraction of screen height
float splatW(vec2 p, vec2 c, float r) {
	vec2 d = (p - c) * vec2(ASPECT(), 1.0);
	return exp(-dot(d, d) / (r * r));
}

void passCtl() {
	float i = floor(gl_FragCoord.x);
	float age = AGE();
	if (i > 3.5) {             // texel 4: init marker, age, palette hue offset (glides 0.13 per drop over ~3 s)
		vec4 c4 = ctlAt(4.0);
		float target = dropHue * ctlAt(2.0).y;
		gl_FragColor = vec4(4242.0, age + 1.0, c4.z + (target - c4.z) * (1.0 - exp(-TIMEDELTA / 3.0)), 0.0);
		return;
	}
	if (age < 2.0) { gl_FragColor = vec4(0.0); return; }
	vec4 c = ctlAt(i);
	vec4 o = c;
	if (i < 0.5) {
		float fired = (kick - c.x > onset && kick > 0.35 && TIME - c.w > 0.12) ? 1.0 : 0.0;
		o = vec4(kick, c.y + fired, fired, fired > 0.5 ? TIME : c.w);
	} else if (i < 1.5) {
		float fired = (snare - c.x > onset && snare > 0.35) ? 1.0 : 0.0;
		o = vec4(snare, c.y + fired, fired, max(fired, c.w * exp(-TIMEDELTA / 0.35)));
	} else if (i < 2.5) {
		float fired = (drop > 0.9 && c.x < 0.9) ? 1.0 : 0.0;
		o = vec4(drop, c.y + fired, fired, c.w + TIMEDELTA * TS());
	} else {
		float fired = (hat - c.x > onset && hat > 0.35) ? 1.0 : 0.0;
		// surge: the kick envelope with liquid inertia (40 ms attack, 350 ms release)
		float tau = kick > c.w ? 0.04 : 0.35;
		o = vec4(hat, c.y + fired, fired, c.w + (kick - c.w) * (1.0 - exp(-TIMEDELTA / tau)));
	}
	gl_FragColor = o;
}

float curlOf(vec2 uv, vec2 t) {
	return 0.5 * (velAt(uv + vec2(t.x, 0.0)).y - velAt(uv - vec2(t.x, 0.0)).y - velAt(uv + vec2(0.0, t.y)).x + velAt(uv - vec2(0.0, t.y)).x);
}

vec2 lookForce(vec2 uv, float dt);

// velF = vel + vorticity confinement + look forces (curl computed inline: no curl buffer)
void passForce() {
	vec2 uv = isf_FragNormCoord, t = SIMTX();
	float dt = DT();
	vec2 v = velAt(uv);
	// a touch of viscosity: pull towards the 4-neighbour mean, kills grid-scale crumpling
	vec2 avg = 0.25 * (velAt(uv + vec2(t.x, 0.0)) + velAt(uv - vec2(t.x, 0.0)) + velAt(uv + vec2(0.0, t.y)) + velAt(uv - vec2(0.0, t.y)));
	v = mix(v, avg, viscosity);
	if (AGE() < 2.0) v = vec2(0.0);
	float cL = curlOf(uv - vec2(t.x, 0.0), t), cR = curlOf(uv + vec2(t.x, 0.0), t);
	float cT = curlOf(uv + vec2(0.0, t.y), t), cB = curlOf(uv - vec2(0.0, t.y), t), cC = curlOf(uv, t);
	vec2 f = 0.5 * vec2(abs(cT) - abs(cB), abs(cR) - abs(cL));
	f /= length(f) + 0.0001;
	float swirl = curlAmt * (1.0 + swirlKick * ctlAt(1.0).w + 1.5 * tension);
	f *= swirl * cC;
	f.y *= -1.0;
	v += f * dt;
	v += lookForce(uv, dt);
	float sp = length(v);                                         // speed limit: hits can't make the flow jump too fast
	if (sp > speedLimit) v *= speedLimit / sp;
	v.x += pourForce * dt * IMG_SIZE(vel).y;          // the pour: a gentle uniform push along +x
	gl_FragColor = vec4(clamp(v, -3000.0, 3000.0), 0.0, 1.0);
}

void passDiv() {
	vec2 uv = isf_FragNormCoord, t = SIMTX();
	vec2 C = velFAt(uv);
	float L = velFAt(uv - vec2(t.x, 0.0)).x, R = velFAt(uv + vec2(t.x, 0.0)).x;
	float T = velFAt(uv + vec2(0.0, t.y)).y, B = velFAt(uv - vec2(0.0, t.y)).y;
	// closed box: the wall reflects the normal component
	if (uv.x - t.x < 0.0) L = openFlow > 0.5 ? C.x : -C.x;     // open edge: the flow passes through
	if (uv.x + t.x > 1.0) R = openFlow > 0.5 ? C.x : -C.x;
	if (uv.y + t.y > 1.0) T = -C.y;
	if (uv.y - t.y < 0.0) B = -C.y;
	gl_FragColor = vec4(0.5 * (R - L + T - B), 0.0, 0.0, 1.0);
}

// Pressure pass k = two Jacobi iterations in one pass (13-point stencil of the buffer it reads).
// k == 0 reads the last frame's solved pressure, damped (warm start).
void passPressure(int k) {
	vec2 uv = isf_FragNormCoord, t = SIMTX();
	float s = 1.0;
	if (k == 0) s = AGE() < 2.0 ? 0.0 : pressureKeep;
	vec2 x = vec2(t.x, 0.0), y = vec2(0.0, t.y);
	float c = pAt(k, uv);
	float diag = pAt(k, uv + x + y) + pAt(k, uv + x - y) + pAt(k, uv - x + y) + pAt(k, uv - x - y);
	float axis2 = pAt(k, uv + 2.0 * x) + pAt(k, uv - 2.0 * x) + pAt(k, uv + 2.0 * y) + pAt(k, uv - 2.0 * y);
	float dn = divAt(uv + x) + divAt(uv - x) + divAt(uv + y) + divAt(uv - y);
	float p = 0.25 * (0.25 * ((4.0 * c + 2.0 * diag + axis2) * s - dn) - divAt(uv));
	gl_FragColor = vec4(p, 0.0, 0.0, 1.0);
}

// divergence-free velocity at any uv: velF minus the pressure gradient (no separate buffer)
vec2 velProj(vec2 uv, vec2 t) {
	return velFAt(uv) - 0.5 * vec2(pLast(uv + vec2(t.x, 0.0)) - pLast(uv - vec2(t.x, 0.0)), pLast(uv + vec2(0.0, t.y)) - pLast(uv - vec2(0.0, t.y)));
}

void passAdvectVel() {
	vec2 uv = isf_FragNormCoord, t = SIMTX();
	float dt = DT();
	vec2 v = velProj(uv - dt * velProj(uv, t) * t, t);
	v /= 1.0 + velFade * dt;
	gl_FragColor = vec4(v, 0.0, 1.0);
}

// cubic B-spline lookup of the coarse velocity grid (4 bilinear taps): C2 smooth, so no cell-sized steps in the dye
vec2 velSmooth(vec2 uv) {
	vec2 size = IMG_SIZE(vel), inv = 1.0 / size;
	vec2 sp = uv * size - 0.5, i = floor(sp), f = sp - i;
	vec2 f2 = f * f, f3 = f2 * f;
	vec2 w0 = (1.0 - 3.0 * f + 3.0 * f2 - f3) / 6.0, w1 = (4.0 - 6.0 * f2 + 3.0 * f3) / 6.0;
	vec2 w2 = (1.0 + 3.0 * f + 3.0 * f2 - 3.0 * f3) / 6.0, w3 = f3 / 6.0;
	vec2 g0 = w0 + w1, g1 = w2 + w3;
	vec2 h0 = (i - 0.5 + w1 / g0) * inv, h1 = (i + 1.5 + w3 / g1) * inv;
	return g0.y * (g0.x * velAt(vec2(h0.x, h0.y)) + g1.x * velAt(vec2(h1.x, h0.y)))
	     + g1.y * (g0.x * velAt(vec2(h0.x, h1.y)) + g1.x * velAt(vec2(h1.x, h1.y)));
}

vec4 lookDye(vec2 uv, vec4 d, float dt);
vec2 lookDrift(vec2 uv);      // extra advection in uv per second that the solver does not carry (laminar pour)

// Catmull-Rom dye lookup (9 bilinear taps) clamped to the 4 nearest texels: much less smearing than bilinear
// semi-Lagrangian advection, so thin bands and cell walls survive for seconds without ringing.
vec4 dyeCubic(vec2 uv) {
	vec2 size = RENDERSIZE, inv = 1.0 / RENDERSIZE;
	vec2 sp = uv * size;
	vec2 t1 = floor(sp - 0.5) + 0.5;
	vec2 f = sp - t1;
	vec2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f));
	vec2 w1 = 1.0 + f * f * (-2.5 + 1.5 * f);
	vec2 w2 = f * (0.5 + f * (2.0 - 1.5 * f));
	vec2 w3 = f * f * (-0.5 + 0.5 * f);
	vec2 w12 = w1 + w2;
	vec2 p0 = (t1 - 1.0) * inv, p3 = (t1 + 2.0) * inv, p12 = (t1 + w2 / w12) * inv;
	vec4 r = (dyeAt(vec2(p0.x, p0.y)) * w0.x + dyeAt(vec2(p12.x, p0.y)) * w12.x + dyeAt(vec2(p3.x, p0.y)) * w3.x) * w0.y
	       + (dyeAt(vec2(p0.x, p12.y)) * w0.x + dyeAt(vec2(p12.x, p12.y)) * w12.x + dyeAt(vec2(p3.x, p12.y)) * w3.x) * w12.y
	       + (dyeAt(vec2(p0.x, p3.y)) * w0.x + dyeAt(vec2(p12.x, p3.y)) * w12.x + dyeAt(vec2(p3.x, p3.y)) * w3.x) * w3.y;
	vec4 a = dyeAt(t1 * inv), b = dyeAt((t1 + vec2(1.0, 0.0)) * inv), c = dyeAt((t1 + vec2(0.0, 1.0)) * inv), d = dyeAt((t1 + 1.0) * inv);
	return clamp(r, min(min(a, b), min(c, d)), max(max(a, b), max(c, d)));
}

void passDye() {
	vec2 uv = isf_FragNormCoord;
	float dt = DT();
	// C2-smooth velocity: bilinear (or tent) upsampling of the coarse grid drags the dye in blocks along shear lines
	vec2 v = velSmooth(uv);
	vec2 src = uv - dt * (v * SIMTX() + lookDrift(uv));
	vec4 d = dyeCubic(src);
	// what flows in from outside the frame is clear water: clamp-to-edge would re-read the edge column and an edge
	// that ever touched colour would feed it back in forever
	vec2 px = 1.0 / RENDERSIZE;
	if (src.x < px.x || src.y < px.y || src.x > 1.0 - px.x || src.y > 1.0 - px.y) d = vec4(0.0);
	if (AGE() < 2.0) d = vec4(0.0);
	gl_FragColor = lookDye(uv, d, dt);
}

#if LIQ_BLOOM
// ---- bloom: prefilter at 1/4 (4 taps cover the 4x4 block), separable 9-tap gaussian (5 bilinear reads)
vec3 bloomSource(vec2 uv);

void passBloomPre() {
	vec2 uv = isf_FragNormCoord, t = 1.0 / IMG_SIZE(dye);
	vec3 c = 0.25 * (bloomSource(uv + t * vec2(-1.0, -1.0)) + bloomSource(uv + t * vec2(1.0, -1.0))
	               + bloomSource(uv + t * vec2(-1.0, 1.0)) + bloomSource(uv + t * vec2(1.0, 1.0)));
	float br = max3(c);
	float knee = bloomThresh * 0.7 + 0.0001;
	float rq = clamp(br - bloomThresh + knee, 0.0, 2.0 * knee);
	rq = rq * rq / (4.0 * knee);
	c *= max(rq, br - bloomThresh) / max(br, 0.0001);
	gl_FragColor = vec4(c, 1.0);
}
vec4 b1At(vec2 uv) { return IMG_NORM_PIXEL(b1, uv); }
vec4 b2At(vec2 uv) { return IMG_NORM_PIXEL(b2, uv); }
vec4 b3At(vec2 uv) { return IMG_NORM_PIXEL(b3, uv); }
#define BLUR5(F, uv, d) (0.2270270 * F(uv) + 0.3162162 * (F(uv + d * 1.3846154) + F(uv - d * 1.3846154)) + 0.0702703 * (F(uv + d * 3.2307692) + F(uv - d * 3.2307692)))
void passBlur(int which) {
	vec2 uv = isf_FragNormCoord;
	vec2 tx = 2.0 / IMG_SIZE(b1);
	vec4 c;
	if (which == 0) c = BLUR5(b1At, uv, vec2(tx.x, 0.0));
	else c = BLUR5(b2At, uv, vec2(0.0, tx.y));
	gl_FragColor = c;
}
// near glow + a wide second ring from the same blurred buffer
vec3 bloomAt(vec2 uv) {
	vec2 w = 12.0 / IMG_SIZE(b3);
	vec3 wide = 0.25 * (b3At(uv + vec2(w.x, w.y)).rgb + b3At(uv - vec2(w.x, w.y)).rgb + b3At(uv + vec2(w.x, -w.y)).rgb + b3At(uv - vec2(w.x, -w.y)).rgb);
	return b3At(uv).rgb + 0.8 * wide;
}
#else
vec3 bloomSource(vec2 uv);
vec3 bloomAt(vec2 uv) { return vec3(0.0); }
#endif

#if LIQ_PHASE > 0
// ---- phase field (Cahn-Hilliard with an Ohta-Kawasaki term) on a 1/4-res grid, LIQ_PHASE substeps per frame:
// passMu(k) then passPhase(k). The look supplies phaseMean() (balance of the two phases), phaseSigma(uv)
// (sets the structure size) and phaseBurst() (noise a drop adds). The flow carries phi once per frame.
float phaseMean();
float phaseSigma(vec2 uv);
float phaseBurst();
float phaseSeed(vec2 uv, float noise);   // phi of fresh paint
float phaseInject(vec2 uv);              // 0..1: where fresh paint replaces phi this frame (sources, inflow)
float phiIn(int k, vec2 uv);    // generated accessors
float muAt(int k, vec2 uv);
float phiAt(vec2 uv);
vec2 PTX() { return 1.0 / IMG_SIZE(phi); }

void passMu(int k) {
	vec2 uv = isf_FragNormCoord, t = PTX();
	float c = phiIn(k, uv);
	float lap = phiIn(k, uv + vec2(t.x, 0.0)) + phiIn(k, uv - vec2(t.x, 0.0)) + phiIn(k, uv + vec2(0.0, t.y)) + phiIn(k, uv - vec2(0.0, t.y)) - 4.0 * c;
	gl_FragColor = vec4(c * c * c - c - lap, 0.0, 0.0, 1.0);
}

// Catmull-Rom lookup of last frame's phi (9 bilinear taps): bilinear resampling every substep smears the cells
// along the flow faster than surface tension can round them
float phiCubic(vec2 uv) {
	vec2 size = IMG_SIZE(phi), inv = 1.0 / size;
	vec2 sp = uv * size, t1 = floor(sp - 0.5) + 0.5, f = sp - t1;
	vec2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f)), w1 = 1.0 + f * f * (-2.5 + 1.5 * f);
	vec2 w2 = f * (0.5 + f * (2.0 - 1.5 * f)), w3 = f * f * (-0.5 + 0.5 * f), w12 = w1 + w2;
	vec2 p0 = (t1 - 1.0) * inv, p3 = (t1 + 2.0) * inv, p12 = (t1 + w2 / w12) * inv;
	return (phiAt(vec2(p0.x, p0.y)) * w0.x + phiAt(vec2(p12.x, p0.y)) * w12.x + phiAt(vec2(p3.x, p0.y)) * w3.x) * w0.y
	     + (phiAt(vec2(p0.x, p12.y)) * w0.x + phiAt(vec2(p12.x, p12.y)) * w12.x + phiAt(vec2(p3.x, p12.y)) * w3.x) * w12.y
	     + (phiAt(vec2(p0.x, p3.y)) * w0.x + phiAt(vec2(p12.x, p3.y)) * w12.x + phiAt(vec2(p3.x, p3.y)) * w3.x) * w3.y;
}

void passPhase(int k) {
	vec2 uv = isf_FragNormCoord, t = PTX();
	vec2 src = uv - DT() * velAt(uv) * SIMTX();                           // the flow moves phi once per frame (k == 0)
	float c = k == 0 ? phiCubic(src) : phiIn(k, uv);
	float mu = muAt(k, uv);
	float lapMu = muAt(k, uv + vec2(t.x, 0.0)) + muAt(k, uv - vec2(t.x, 0.0)) + muAt(k, uv + vec2(0.0, t.y)) + muAt(k, uv - vec2(0.0, t.y)) - 4.0 * mu;
	float m = phaseMean();
	float noise = hash12(uv * 913.0 + fract(TIME * 7.13) * 91.0) - 0.5;
	c += 0.025 * (lapMu - phaseSigma(uv) * (c - m));                        // explicit Cahn-Hilliard step (stable below ~0.03)
	if (k == 0) c = mix(c, phaseSeed(uv, noise), phaseInject(uv));         // fresh paint at the sources
	if (AGE() < 2.0) c = phaseSeed(uv, noise);
	vec4 c2 = ctlAt(2.0);
	if (c2.z > 0.5 && k == 0) c += phaseBurst() * noise * splatW(uv, vec2(0.5), 0.45);   // drop: a burst of fresh structure
	gl_FragColor = vec4(clamp(c, -1.5, 1.5), 0.0, 0.0, 1.0);
}
#endif

// ---- optional hard pixelate (Pixelate param = block size in px, 0 = off): sample at block centres, thin dark grid
vec2 pixUV(vec2 uv) {
	if (pixelate < 1.5) return uv;
	vec2 b = vec2(floor(pixelate + 0.5)) / RENDERSIZE;
	return (floor(uv / b) + 0.5) * b;
}
vec3 pixGrid(vec3 c) {
	if (pixelate < 1.5) return c;
	vec2 f = fract(gl_FragCoord.xy / floor(pixelate + 0.5));
	return c * (pixelate > 5.5 && min(f.x, f.y) < 1.0 / floor(pixelate + 0.5) ? 0.55 : 1.0);
}

// ---- final pass: zoom (with a kick punch), optional hard pixelate, optional spatial pixel cloud
vec3 shade(vec2 uv);
float cloudDepth(vec2 uv);
vec3 flareTint();
vec3 dither(vec3 c, vec2 fc);

// pixel cloud: the image as square pixels floating at different depths (bright = near). Near pixels grow, drift out
// from the centre and parallax against a slowly orbiting camera; the nearest square covering the fragment wins.
vec3 cloudShade(vec2 uv) {
	float px = pixelate > 1.5 ? floor(pixelate + 0.5) : 12.0;
	vec2 B = vec2(px) / RENDERSIZE;
	vec2 cell = floor(uv / B);
	vec2 cam = 0.6 * vec2(sin(ctlAt(2.0).w * 0.21), cos(ctlAt(2.0).w * 0.17));       // in cells
	float bestZ = -1.0;
	vec2 bestC = vec2(0.0), bestL = vec2(0.0);
	for (int j = -2; j <= 2; j++) for (int i = -2; i <= 2; i++) {
		vec2 cc = (cell + vec2(float(i), float(j)) + 0.5) * B;
		float z = cloudDepth(cc) * cloud;
		if (z < 0.01) continue;
		vec2 off = clamp(((cc - 0.5) * vec2(ASPECT(), 1.0) * cloudSpread + cam) * z, -1.6, 1.6);   // cells
		vec2 centre = cc + off * B;
		float hs = 0.5 * (0.75 + 0.5 * z);
		vec2 q = abs(uv - centre) / B;
		if (max(q.x, q.y) < hs && z > bestZ) { bestZ = z; bestC = cc; bestL = (uv - centre) / B / hs; }
	}
	if (bestZ < 0.0) return vec3(0.0);
	// cube look: lit top-left bevel, shaded bottom-right bevel, like a voxel seen slightly from above
	float bev = 0.22;
	float lit = 1.0;
	if (bestL.y > 1.0 - bev || bestL.x < -1.0 + bev) lit = 1.0 + 0.45 * cubes;
	if (bestL.y < -1.0 + bev || bestL.x > 1.0 - bev) lit = 1.0 - 0.5 * cubes;
	return shade(bestC) * (0.8 + 0.4 * bestZ) * lit;
}

void passRender() {
	vec2 uv = isf_FragNormCoord;
	float z = max(zoom, 0.05) * (1.0 + zoomKick * ctlAt(3.0).w);
	uv = 0.5 + (uv - 0.5) / z;
	vec3 c = cloud > 0.01 ? cloudShade(uv) : pixGrid(shade(pixUV(uv)));
	// loudness drive: smoothed energy plus the kick surge (no one-frame jumps)
	float loud = clamp(smoothstep(0.35, 0.85, energy) + 0.6 * ctlAt(3.0).w, 0.0, 1.5);
	// pop: saturation and contrast around mid grey, more when it is loud
	float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
	c = mix(vec3(l), c, 1.0 + pop * (0.6 + 0.6 * loud));
	c = max(c, 0.0);
	c = c * (1.0 + hdr * 0.8 * loud);                                       // HDR push: highlights blow out on hits
	if (flare > 0.01) {
		// lens flare from the bright fluid (cloudDepth = cheap brightness): ghosts mirrored through the centre,
		// growing with loudness (a horizontal streak drew banding, removed)
		vec2 m = 0.5 - uv;
		vec3 fl = vec3(0.0);
		// ghosts take the frame's own colour (flareTint from the look) so they never add foreign hues
		fl += flareTint() * pow(cloudDepth(0.5 + m * 0.6), 3.0) * 0.6;
		fl += flareTint() * vec3(1.0, 0.85, 0.7) * pow(cloudDepth(0.5 + m * 1.4), 3.0) * 0.4;
		fl += flareTint() * pow(cloudDepth(0.5 + m * 2.2), 3.0) * 0.25;
		c += fl * flare * (0.25 + loud);
	}
	// soft shoulder above 0.8 (the looks are already display-referred): blown highlights roll off, burn towards white
	vec3 over = max(c - 0.8, 0.0);
	c = min(c, 0.8) + 0.2 * (1.0 - exp(-over / 0.2));
	c += vec3(max(0.0, max3(over) - 0.3) * 0.25);
	gl_FragColor = vec4(dither(c, gl_FragCoord.xy), 1.0);
}

// palette rotation: base hue (Palette) + slow drift (Palette Speed, cycles per minute of look time) + drop glide
float paletteHue() { return palette + paletteSpeed * ctlAt(2.0).w / 60.0 + ctlAt(4.0).z; }
// rotate a colour's hue by `turns` keeping its luminance (YIQ rotation)
vec3 hueShift(vec3 c, float turns) {
	float a = turns * 6.2831853;
	vec3 yiq = vec3(dot(c, vec3(0.299, 0.587, 0.114)), dot(c, vec3(0.596, -0.274, -0.322)), dot(c, vec3(0.211, -0.523, 0.312)));
	float ca = cos(a), sa = sin(a);
	yiq.yz = vec2(yiq.y * ca - yiq.z * sa, yiq.y * sa + yiq.z * ca);
	return max(vec3(yiq.x + 0.956 * yiq.y + 0.621 * yiq.z, yiq.x - 0.272 * yiq.y - 0.647 * yiq.z, yiq.x - 1.106 * yiq.y + 1.703 * yiq.z), 0.0);
}

// ---- shared finishing: dither against banding in the dark gradients
vec3 dither(vec3 c, vec2 fc) { return c + (hash12(fc + fract(TIME) * 37.0) - 0.5) / 255.0; }

// ---- debug view (build with --debug): 4x2 tiles of the buffers; magenta NaN, yellow Inf, blue negative
vec3 dbg(vec4 v, float s) {
	if (any(isnan(v))) return vec3(1.0, 0.0, 1.0);
	if (any(isinf(v))) return vec3(1.0, 1.0, 0.0);
	vec3 c = abs(v.rgb) * s;
	if (v.r < 0.0 || v.g < 0.0) c.b += 0.5;
	return c;
}
void passDebug() {
	vec2 uv = isf_FragNormCoord;
	vec2 cell = floor(uv * vec2(4.0, 2.0));
	vec2 q = fract(uv * vec2(4.0, 2.0));
	float i = cell.x + 4.0 * (1.0 - cell.y);
	vec3 c;
	if (i < 0.5) c = dbg(IMG_NORM_PIXEL(dye, q), 1.0);
	else if (i < 1.5) c = dbg(IMG_NORM_PIXEL(vel, q), 0.01);
	else if (i < 2.5) c = dbg(IMG_NORM_PIXEL(velF, q), 0.01);
	else if (i < 3.5) c = dbg(vec4(pLast(q)), 0.01);
	else if (i < 4.5) c = dbg(IMG_NORM_PIXEL(divB, q), 0.1);
#if LIQ_BLOOM
	else if (i < 5.5) c = dbg(IMG_NORM_PIXEL(b1, q), 1.0);
	else if (i < 6.5) c = dbg(IMG_NORM_PIXEL(b3, q), 1.0);
#endif
	else {      // ctl row: per texel green = valid, red = rejected by clean(); bottom strip blue while AGE() < 2
		float ti = floor(q.x * 5.0);
		vec4 raw = IMG_NORM_PIXEL(ctl, vec2((ti + 0.5) / 5.0, 0.5));
		bool bad = any(isnan(raw)) || any(isinf(raw)) || max(max(abs(raw.x), abs(raw.y)), max(abs(raw.z), abs(raw.w))) > 1.0e5;
		c = bad ? vec3(1.0, 0.0, 0.0) : vec3(0.0, 0.7, 0.0);
		if (q.y < 0.3) c = AGE() < 2.0 ? vec3(0.0, 0.0, 1.0) : vec3(0.4);
		if (q.y > 0.8) c = vec3(fract(abs(raw.x) / 1000.0), fract(abs(raw.w) / 1000.0), 0.0);
	}
	if (min(q.x, q.y) < 0.004) c = vec3(0.3);
	gl_FragColor = vec4(c, 1.0);
}

// ---- shared material helpers
// thin-film interference (soap film / oil slick): film thickness in nm -> reflected colour
vec3 thinFilm(float nm) {
	vec3 lam = vec3(650.0, 532.0, 450.0);
	return 0.5 + 0.5 * cos(4.0 * PI * 1.33 * nm / lam);
}
float vnoise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash12(i), hash12(i + vec2(1.0, 0.0)), f.x), mix(hash12(i + vec2(0.0, 1.0)), hash12(i + 1.0), f.x), f.y);
}
float fbm(vec2 p) { return 0.5 * vnoise(p) + 0.25 * vnoise(p * 2.03 + 7.1) + 0.125 * vnoise(p * 4.07 + 3.3) + 0.0625 * vnoise(p * 8.1 + 1.7); }

float pLastRaw(vec2 uv) { return IMG_NORM_PIXEL(p6, uv).x; }
float pPrev(int k, vec2 uv) {
	if (k == 0) return clean(IMG_NORM_PIXEL(p6, uv)).x;
	if (k == 1) return IMG_NORM_PIXEL(p0, uv).x;
	if (k == 2) return IMG_NORM_PIXEL(p1, uv).x;
	if (k == 3) return IMG_NORM_PIXEL(p2, uv).x;
	if (k == 4) return IMG_NORM_PIXEL(p3, uv).x;
	if (k == 5) return IMG_NORM_PIXEL(p4, uv).x;
	return IMG_NORM_PIXEL(p5, uv).x;
}


// ---- Look A: neon ink jets in dark water.
// Two jets enter from the frame edges and drift slowly; the kick surges them (with inertia, not one-frame jolts),
// every 4th kick (about a bar) fires a splat from the jet that is due, sub-bass and buildup feed the jets,
// a drop fires two big opposing splats and turns the ink pair.

const int NJ = 2;

float cellsPerH() { return IMG_SIZE(vel).y; }
float t2() { return ctlAt(2.0).w; }
float surge() { return ctlAt(3.0).w; }

// jet i: origin near the frame edge (drifts around the frame over minutes), direction into the frame (sways slowly)
void jet(int i, out vec2 p, out vec2 dir, out float s) {
	float fi = float(i), t = t2();
	float a = 2.0 * PI * (fi * 0.5 + 0.007 * t + 0.05 * sin(t * 0.05 + fi * 3.0));
	vec2 e = vec2(cos(a), sin(a));
	p = 0.5 + vec2(0.47, 0.45) * e;
	float wob = 0.45 * sin(t * 0.21 + fi * 2.3) + 0.15 * sin(t * 0.53 + fi * 5.1);
	vec2 d = normalize(-e * vec2(1.0, ASPECT()));
	float cw = cos(wob), sw = sin(wob);
	dir = vec2(cw * d.x - sw * d.y, sw * d.x + cw * d.y);
	float gate = 0.35 + 0.65 * smoothstep(-0.3, 0.5, sin(t * 0.09 + fi * PI));
	s = emit * gate * (0.25 + 1.4 * surge() + 0.6 * bass + 0.8 * tension);
}

// one complementary pair at a time (the reference shows one or two inks, never a rainbow); a drop turns the pair
float pairHue() { return paletteHue() + 0.003 * t2(); }             // slow drift only: no colour jumps on drops
vec3 ink(int i) { return hsv(pairHue() + (i == 0 ? 0.0 : 0.47), 0.92, 1.0); }

bool accent(out vec2 p, out vec2 d, out int which) {
	vec4 c0 = ctlAt(0.0);
	which = int(mod(floor(c0.y / 4.0), 2.0));
	if (c0.z < 0.5 || mod(c0.y, 4.0) > 0.5) return false;
	float s;
	jet(which, p, d, s);
	p += d * vec2(0.06 / ASPECT(), 0.06);
	return true;
}

vec2 lookForce(vec2 uv, float dt) {
	vec2 f = vec2(0.0);
	float k = cellsPerH();
	for (int i = 0; i < NJ; i++) {
		vec2 p, d; float s;
		jet(i, p, d, s);
		f += d * s * splatW(uv, p, 0.06) * dt * k * 2.2;
	}
	vec2 p, d; int w;
	if (accent(p, d, w)) f += d * splatForce * 0.5 * splatW(uv, p, splatSize) * k;
	vec4 c2 = ctlAt(2.0);
	if (c2.z > 0.5) {
		float a = c2.y * 1.7;
		vec2 e = vec2(cos(a), sin(a));
		f += e * splatForce * 1.6 * splatW(uv, 0.5 - e * vec2(0.3 / ASPECT(), 0.3), splatSize * 1.3) * k;
		f -= e * splatForce * 1.6 * splatW(uv, 0.5 + e * vec2(0.3 / ASPECT(), 0.3), splatSize * 1.3) * k;
	}
	return f;
}

vec4 lookDye(vec2 uv, vec4 d, float dt) {
	d.rgb /= 1.0 + fade * dt;
	for (int i = 0; i < NJ; i++) {
		vec2 p, dd; float s;
		jet(i, p, dd, s);
		d.rgb += ink(i) * s * splatW(uv, p, 0.055) * dt * 3.0;
	}
	vec2 p, dd; int w;
	// no one-frame dye pops (they flicker on dense music): the jets' surge carries the beat
	vec4 c2 = ctlAt(2.0);
	if (c2.z > 0.5) {
		float a = c2.y * 1.7;
		vec2 e = vec2(cos(a), sin(a));
		d.rgb += ink(0) * 0.25 * splatW(uv, 0.5 - e * vec2(0.3 / ASPECT(), 0.3), splatSize * 1.1);
		d.rgb += ink(1) * 0.25 * splatW(uv, 0.5 + e * vec2(0.3 / ASPECT(), 0.3), splatSize * 1.1);
	}
	d.rgb = min(d.rgb, vec3(3.0));
	return d;
}

vec2 lookDrift(vec2 uv) { return vec2(0.0); }

vec3 bloomSource(vec2 uv) { return dyeAt(uv).rgb * exposure; }

float dens(vec2 uv) { return sqrt(length(dyeAt(uv).rgb)); }

vec3 flareTint() { return 0.5 * (ink(0) + ink(1)); }
float cloudDepth(vec2 uv) { return clamp(length(dyeAt(uv).rgb) * 1.5, 0.0, 1.0); }

// the look's colour at uv (zoom, pixelate and pixel cloud are applied by passRender in fluid_common)
// glass style (Style = 1, default): dye in a thin layer between two glass sheets, glowing. No relief, gloss or
// banding: colour is a smooth function of dye amount (light through a coloured layer, 1 - exp(-k d)), so every
// edge on screen is a front the flow itself made (filaments, shear, folds).
vec3 shadeGlass(vec2 uv) {
	vec3 lin = dyeAt(uv).rgb * exposure;
	// HDR pop: base level (HDR Pop) plus an audio part (Pop Auto) that rises with energy, kicks and drops and relaxes
	// in quiet parts. It saturates the colour and drives the densest dye (jet cores, fresh splats, collisions) past
	// white; everything stays continuous, tone mapping keeps it smooth.
	float loud = clamp(smoothstep(0.35, 0.85, energy) + 0.7 * ctlAt(3.0).w + drop, 0.0, 1.5);
	float pp = hdrPop + popAuto * loud;
	float dens = max3(lin);
	lin *= 1.0 + pp * 2.5 * smoothstep(0.8, 3.0, dens);                  // hot cores get much brighter
	float l = dot(lin, vec3(0.2126, 0.7152, 0.0722));
	lin = max(mix(vec3(l), lin, 1.0 + 0.6 * pp), 0.0);                   // fuller saturation
	lin += bloomAt(uv) * bloom * (1.0 + pp);                              // the glow
	vec3 c = 1.0 - exp(-lin);
	c += vec3(smoothstep(2.0, 7.0, dens * (1.0 + pp))) * 0.55;           // past-white spots where it is hottest
	return pow(min(c, 1.0), vec3(0.9));
}

vec3 shade(vec2 uv) {
	if (flatStyle > 0.5) return shadeGlass(uv);
	vec2 t = 5.0 / RENDERSIZE;
	vec3 d = dyeAt(uv).rgb;
	// relief: the ink layer as a height field (compressed density), lit from the top left, glossy
	float hx = dens(uv + vec2(t.x, 0.0)) - dens(uv - vec2(t.x, 0.0));
	float hy = dens(uv + vec2(0.0, t.y)) - dens(uv - vec2(0.0, t.y));
	vec3 n = normalize(vec3(-hx * shine * 3.0, -hy * shine * 3.0, 0.25));
	vec3 L = normalize(vec3(-0.45, 0.6, 0.65));
	float diffuse = 0.55 + 0.6 * max(dot(n, L), 0.0);
	float spec = pow(max(dot(reflect(-L, n), vec3(0.0, 0.0, 1.0)), 0.0), 28.0);
	float cover = smoothstep(0.02, 0.4, length(d));
	vec3 c = d * exposure * diffuse;
	c += vec3(0.9, 0.95, 1.0) * spec * cover * 0.35 * shine;
	c += bloomAt(uv) * bloom;
	c = 1.0 - exp(-c);
	c = pow(c, vec3(0.9));
	return c;
}

void main() {
	if (PASSINDEX == 0) passCtl();
	else if (PASSINDEX == 1) passForce();
	else if (PASSINDEX == 2) passDiv();
	else if (PASSINDEX < 10) passPressure(PASSINDEX - 3);
	else if (PASSINDEX == 10) passAdvectVel();
	else if (PASSINDEX == 11) passDye();
	else if (PASSINDEX == 12) passBloomPre();
	else if (PASSINDEX == 13) passBlur(0);
	else if (PASSINDEX == 14) passBlur(1);
	else passRender();
}
