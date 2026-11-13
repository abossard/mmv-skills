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

float lookSource(vec2 uv) { return 0.0; }
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
