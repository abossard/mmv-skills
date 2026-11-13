// ---- Look E: radial burst of thick, oily paint. Wandering mass sources push fluid out on every side (all edges open, so it can
// leave); pigment injected in the source with colour varying by angle is stretched by the outflow into fine radial
// streaks, then the flow relaxes into swirls (vorticity confinement, snare torque).
// Audio: kick = burst strength (the kick surge envelope, with inertia), sub-bass and buildup = pigment feed,
// drop = a big burst (DropFlash envelope) and a palette glide (Drop Hue), snare = swirl.

float t2() { return ctlAt(2.0).w; }
float surge() { return ctlAt(3.0).w; }
float cellsPerH() { return IMG_SIZE(vel).y; }

// Three emitters wander over the middle of the frame on slow, independent paths; each fades in and out over several
// seconds (life), so bursts appear, move, overlap (merge) and die. Nothing is pinned to a fixed pixel.
const int NE = 3;
float fi(int i) { return float(i); }
void emitter(int i, out vec2 p, out float life) {
	float fi = float(i), t = t2();
	float sp = 0.035 + 0.012 * fi;
	p = vec2(0.5) + vec2(0.24 * sin(t * sp + fi * 2.1) + 0.06 * sin(t * sp * 2.7 + fi * 5.0),
	                     0.2 * cos(t * sp * 1.3 + fi * 3.7) + 0.05 * sin(t * sp * 3.1 + fi));
	life = smoothstep(-0.35, 0.45, sin(t * (0.06 + 0.015 * fi) + fi * 2.09));
	if (i == 0) life = max(life, 0.35);                                 // never fully empty
}

// source strength 0..: idle flow, kick surge, drop burst
float burstLevel() { return 0.4 + burstKick * surge() + burstDrop * drop + 0.5 * tension; }

float lookSource(vec2 uv) {
	float src = 0.0;
	for (int i = 0; i < NE; i++) {
		vec2 p; float life;
		emitter(i, p, life);
		vec2 q = (uv - p) * vec2(ASPECT(), 1.0);
		float r = length(q) / burstRadius;
		src += life * exp(-r * r);                                       // soft discs: no ring artefact at the edge
	}
	return sourceRate * burstLevel() * src;
}

vec2 lookDrift(vec2 uv) { return vec2(0.0); }

vec2 curlNoise(vec2 n) {
	float e = 0.02, n0 = vnoise(n);
	return vec2(vnoise(n + vec2(0.0, e)) - n0, -(vnoise(n + vec2(e, 0.0)) - n0)) / e;
}

vec2 lookForce(vec2 uv, float dt) {
	float k = cellsPerH(), t = t2();
	vec2 f = vec2(0.0);
	float near = 0.0;
	for (int i = 0; i < NE; i++) {
		vec2 p; float life;
		emitter(i, p, life);
		vec2 q = (uv - p) * vec2(ASPECT(), 1.0);
		float r = length(q);
		vec2 tang = vec2(-q.y, q.x) / max(r, 0.001);
		float sgn = mod(fi(i), 2.0) < 0.5 ? 1.0 : -1.0;
		// a constant slow spin per emitter (alternating sense) plus the snare swirl: the core always turns
		f += tang * sgn * torque * (0.35 + ctlAt(1.0).w) * life * exp(-r * r / 0.03) * dt * k;
		// the kick also pushes outward directly (a pressure pulse), so the hit shows at once
		f += q / max(r, 0.001) * push * surge() * life * exp(-r * r / 0.04) * dt * k;
		near = max(near, life * exp(-r * r / 0.02));
	}
	// turbulence: divergence-free curl noise, strong at the emitters (the core breaks up and churns), weak elsewhere,
	// fading towards the open edges (a frame-wide gust would sweep the pigment off one side, measured)
	float edge = smoothstep(0.0, 0.2, min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y)));
	vec2 a = uv * vec2(ASPECT(), 1.0);
	f += curlNoise(a * 7.0 + vec2(t * 0.05, -t * 0.04)) * stir * edge * dt * k;
	f += curlNoise(a * 14.0 + vec2(-t * 0.4, t * 0.3)) * coreStir * near * (1.0 + surge()) * dt * k;
	return f;
}

vec4 lookDye(vec2 uv, vec4 d, float dt) {
	d.rgb /= 1.0 + fade * dt;
	float t = t2();
	float level = feed * (0.55 + 0.5 * bass + 0.4 * tension + 0.3 * surge() + 0.6 * drop);
	for (int i = 0; i < NE; i++) {
		vec2 p; float life;
		emitter(i, p, life);
		vec2 q = (uv - p) * vec2(ASPECT(), 1.0);
		float rr = length(q) / (burstRadius * 2.0);
		if (rr > 1.6) continue;
		// the pigment pattern turns over time (each emitter its own way), so the streaks it feeds into the outflow
		// change angle all the time instead of pinning a fixed star
		float rot = t * (0.1 + 0.04 * fi(i)) * (mod(fi(i), 2.0) < 0.5 ? 1.0 : -1.0);
		vec2 dir = q / max(length(q), 0.0001);
		dir = vec2(cos(rot) * dir.x - sin(rot) * dir.y, sin(rot) * dir.x + cos(rot) * dir.y);
		vec2 qq = q / burstRadius;
		float hueDir = vnoise(dir * 2.2 + vec2(t * 0.1, 7.0 + fi(i) * 9.0)) + 0.35 * vnoise(dir * 7.0 + vec2(3.0, t * 0.15));
		float hueCore = vnoise(qq * 2.5 + vec2(t * 0.6, fi(i) * 5.0)) * 1.3 + 0.5 * vnoise(qq * 6.0 - vec2(0.0, t * 0.8));
		float hue = paletteHue() + 0.3 * fi(i) + spread * mix(hueCore, hueDir, smoothstep(0.25, 0.75, rr));
		float fine = vnoise(dir * 30.0 + vec2(t * 0.1, 1.0)) * 0.65 + vnoise(dir * 55.0 + vec2(5.0, t * 0.15)) * 0.35;
		float clumpCore = 0.15 + 0.85 * smoothstep(0.42, 0.52, vnoise(qq * 4.0 + vec2(t * 0.5, 3.0)));   // cohesive blobs, sharp fronts
		float clump = mix(clumpCore, 0.04 + 0.96 * smoothstep(0.5, 0.58, fine), smoothstep(0.35, 0.8, rr));
		float white = smoothstep(0.7, 0.8, vnoise(dir * 9.0 + vec2(t * 0.2, 20.0)));
		vec3 col = mix(hsv(hue, 0.9, 1.0), vec3(1.0, 0.97, 0.94), white * 0.8);
		// a soft deposit, not an overwrite: what the flow already carries there stays visible, so the core churns
		float w = exp(-rr * rr * rr * rr) * life;
		d.rgb = mix(d.rgb, col * clump * level, clamp(w * dt * deposit, 0.0, 1.0));
	}
	return d;
}

vec3 bloomSource(vec2 uv) { return dyeAt(uv).rgb * exposure; }

// glass look: dye between two glass sheets, smooth colour, glow. The tone map scales by the strongest channel, so
// colours keep their full saturation at any brightness (HDR pop); only the very hottest pigment burns to white.
vec3 shade(vec2 uv) {
	vec3 lin = dyeAt(uv).rgb * exposure;
	float loud = clamp(smoothstep(0.35, 0.85, energy) + 0.7 * surge() + drop, 0.0, 1.5);
	float pp = hdrPop + popAuto * loud;
	lin *= 1.0 + 1.2 * pp;
	float l = dot(lin, vec3(0.2126, 0.7152, 0.0722));
	lin = max(mix(vec3(l), lin, 1.25 + 0.5 * pp), 0.0);                 // paint is saturated
	// oil: where a pigment layer thins out (its edge, a stretched filament) the light shows a thin-film colour shift,
	// as on an oil skin. It follows the pigment thickness the flow carries, nothing is drawn; no relief or outlines.
	float thick = max3(lin);
	float thin = smoothstep(0.08, 0.5, thick) * (1.0 - smoothstep(0.6, 2.0, thick));
	lin += thinFilm(260.0 + 520.0 * clamp(thick, 0.0, 1.5)) * thin * oilSheen * (0.6 + 0.4 * thick);
	lin += bloomAt(uv) * bloom * (0.6 + 0.6 * pp);
	float m = max3(lin);
	vec3 c = lin * (1.0 - exp(-m)) / max(m, 0.0001);                    // keeps the hue and saturation of bright pigment
	c = mix(c, vec3(1.0), smoothstep(2.5, 8.0, m) * 0.7);                // the very hottest burns towards white
	return pow(min(c, 1.0), vec3(0.9));
}

vec3 flareTint() { return hsv(paletteHue() + 0.1, 0.5, 1.0); }
float cloudDepth(vec2 uv) { return clamp(max3(dyeAt(uv).rgb) * 0.8, 0.0, 1.0); }
