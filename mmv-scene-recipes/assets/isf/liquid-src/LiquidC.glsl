// ---- Look C: oily fire. Burners along the bottom inject hot ink; buoyancy lifts it, vorticity curls it into flame
// licks, it cools from white-yellow through orange to deep red and fades. Inside the flames B's phase field draws dark
// oily streaks (burning oil); cooling flames turn into smoke. dye.a = temperature, dye.r = smoke.
// Kick: the burners surge (with inertia); every bar a soft puff from the burner that is due; drop: all burners flare.

const int NB = 3;

float t2() { return ctlAt(2.0).w; }
float surge() { return ctlAt(3.0).w; }
float cellsPerH() { return IMG_SIZE(vel).y; }

// burner i: position on the floor (drifts slowly sideways), flame direction (up, swaying), strength
void burner(int i, out vec2 p, out vec2 dir, out float s) {
	float fi = float(i), t = t2();
	p = vec2((fi + 0.5) / float(NB) + 0.12 * sin(t * 0.05 + fi * 2.1), -0.04);     // below the frame: no visible burner disc
	float sway = 0.25 * sin(t * 0.3 + fi * 1.7) + 0.12 * sin(t * 0.83 + fi * 4.0);
	dir = vec2(sin(sway), cos(sway));
	float gate = 0.45 + 0.55 * smoothstep(-0.4, 0.6, sin(t * 0.11 + fi * 2.4));
	s = emit * gate * (0.35 + 1.3 * surge() * hitGain + 0.4 * bass + 0.5 * tension);
}

vec2 lookForce(vec2 uv, float dt) {
	float k = cellsPerH();
	vec2 f = vec2(0.0, lift * (1.0 + 1.5 * surge() * hitGain) * dyeAt(uv).a * dt * k);   // buoyancy: hot ink rises, harder on hits
	// on hits the flames go wild: a curl-noise gust (divergence-free, so it swirls instead of pushing) scaled by the surge
	vec2 q = uv * vec2(ASPECT(), 1.0) * 3.0 + vec2(0.0, -t2() * 0.7);
	float e = 0.02;
	float n0 = fbm(q), nx = fbm(q + vec2(e, 0.0)), ny = fbm(q + vec2(0.0, e));
	vec2 curlN = vec2(ny - n0, -(nx - n0)) / e;
	f += curlN * surge() * hitGain * gust * dt * k;
	for (int i = 0; i < NB; i++) {
		vec2 p, d; float s;
		burner(i, p, d, s);
		f += d * s * splatW(uv, p, ribbon) * dt * k * 3.0;
	}
	vec4 c0 = ctlAt(0.0);
	if (c0.z > 0.5 && mod(c0.y, 4.0) < 0.5) {                            // a bar puff (velocity only, no dye pop)
		vec2 p, d; float s;
		burner(int(mod(floor(c0.y / 4.0), float(NB))), p, d, s);
		f += d * splatForce * 0.6 * splatW(uv, p + vec2(0.0, 0.08), splatSize) * k;
	}
	return f;
}

// dye.a = temperature, dye.r = smoke: the heat a flame loses as it cools turns into smoke, which lingers longer
vec4 lookDye(vec2 uv, vec4 d, float dt) {
	float T0 = d.a;
	d.a *= exp(-fade * dt * (1.0 + 6.0 * smoothstep(0.8, 1.0, uv.y)));   // cooling, fast near the ceiling: no heat pool at the top
	float smoke = d.r * exp(-smokeFade * dt) + smokeAmt * (T0 - d.a);
	float hueT = d.g * exp(-fade * dt * (1.0 + 6.0 * smoothstep(0.8, 1.0, uv.y)));   // hue offset x heat, cools with it
	vec4 c2 = ctlAt(2.0);
	float flare = c2.z > 0.5 ? 1.0 : 0.0;
	for (int i = 0; i < NB; i++) {
		vec2 p, dd; float s;
		burner(i, p, dd, s);
		// licking, uneven burner: noise along x and time breaks the injection disc into tongues
		float lick = 0.35 + 1.3 * fbm(vec2(uv.x * 18.0, t2() * 3.0 + float(i) * 7.0));
		float add = splatW(uv, p, ribbon) * lick * (0.25 + s + 0.5 * flare) * dt * 16.0;
		d.a += add;
		hueT += add * variety * (float(i) - 1.0 + 0.6 * sin(t2() * 0.13 + float(i) * 2.0));   // each burner its own subtle hue
	}
	return vec4(min(smoke, 3.0), clamp(hueT, -3.0, 3.0), 0.0, min(d.a, 3.0));
}

float lookSource(vec2 uv) { return 0.0; }
vec2 lookDrift(vec2 uv) { return vec2(0.0); }
vec3 bloomSource(vec2 uv) { return vec3(0.0); }

// ---- phase-field hooks (solver in fluid_common.glsl): oil streaks seeded at the burners, folded by the flames
float phaseMean() { return 0.1; }
float phaseSigma(vec2 uv) { float l = max(fiber * 0.25 * mix(0.7, 1.4, fbm(uv * 3.0 + 5.0)), 4.0); return pow(6.2832 / l, 4.0); }
float phaseBurst() { return 0.6; }
float phaseSeed(vec2 uv, float noise) { return phaseMean() + 1.4 * (vnoise(vec2(uv.x * 40.0, t2() * 2.0)) - 0.5) + 0.2 * noise; }
float phaseInject(vec2 uv) {
	float w = 0.0;
	for (int i = 0; i < NB; i++) {
		vec2 p, d; float s;
		burner(i, p, d, s);
		w = max(w, splatW(uv, p, ribbon * 1.2));
	}
	return clamp(w * 1.5, 0.0, 1.0);
}

// smoke density blurred over r px: 12 taps on a golden-angle spiral
float smokeAt(vec2 uv, float r) {
	float acc = dyeAt(uv).r, wsum = 1.0;
	for (int i = 1; i <= 12; i++) {
		float fi = float(i);
		float a = fi * 2.39996;
		vec2 o = vec2(cos(a), sin(a)) * sqrt(fi / 12.0) * r / RENDERSIZE;
		float w = 1.0 - 0.5 * fi / 12.0;
		acc += dyeAt(uv + o).r * w;
		wsum += w;
	}
	return acc / wsum;
}

// flat flame bands: temperature thresholds with hard, anti-aliased edges (1 px), one flat colour per band
vec3 flameFlat(float T, float aa) {
	vec3 c = vec3(0.0);
	c = mix(c, vec3(0.55, 0.04, 0.02), smoothstep(fireEdge - aa, fireEdge + aa, T));
	c = mix(c, vec3(1.0, 0.27, 0.02), smoothstep(fireEdge * 2.2 - aa, fireEdge * 2.2 + aa, T));
	c = mix(c, vec3(1.0, 0.62, 0.05), smoothstep(fireEdge * 3.6 - aa, fireEdge * 3.6 + aa, T));
	c = mix(c, vec3(1.0, 0.93, 0.6), smoothstep(fireEdge * 5.5 - aa, fireEdge * 5.5 + aa, T));
	return c;
}

// blackbody-like flame colour for temperature T (0 cold .. ~2.5 white hot), used by the soft style
vec3 flame(float T) {
	vec3 c = vec3(0.0);
	c = mix(c, vec3(0.45, 0.03, 0.01), smoothstep(0.05, 0.35, T));
	c = mix(c, vec3(1.0, 0.25, 0.02), smoothstep(0.3, 0.8, T));
	c = mix(c, vec3(1.0, 0.65, 0.12), smoothstep(0.7, 1.3, T));
	c = mix(c, vec3(1.0, 0.95, 0.75), smoothstep(1.3, 2.2, T));
	return c;
}

// soft style (Flat = 0): glowing gradient flames, dark oil streaks with a warm edge sheen, lit smoke, glow halo
vec3 shadeSoft(vec2 uv) {
	vec4 d = dyeAt(uv);
	float T = d.a;
	float p = phiAt(uv);
	float w = fwidth(p) * 1.2 + 0.02;
	float oil = smoothstep(w, -w, p);
	vec3 fire = flame(T);
	float edge = exp(-pow(p / (0.25 + w), 2.0));
	vec3 c = mix(fire, fire * 0.3, oil * smoothstep(0.1, 0.7, T)) + flame(T * 1.4) * edge * 0.25 * iridescence * smoothstep(0.2, 0.9, T);
	float sm = smokeAt(uv, smokeBlur);
	vec2 t = vec2(smokeBlur * 1.5 + 6.0) / RENDERSIZE;
	float gy = smokeAt(uv + vec2(0.0, t.y), smokeBlur) - smokeAt(uv - vec2(0.0, t.y), smokeBlur);
	float lit = clamp(0.7 + 1.2 * gy, 0.4, 1.1);
	float glowBelow = dyeAt(uv - vec2(0.0, 0.06)).a;
	vec3 smokeCol = vec3(0.45, 0.44, 0.43) * lit + vec3(1.0, 0.35, 0.08) * 0.35 * clamp(glowBelow, 0.0, 1.0);
	float cover = (1.0 - exp(-sm * smokeDensity)) * 0.85;
	c = mix(c, smokeCol * smokeBright, cover * (1.0 - smoothstep(0.3, 1.2, T)));
	float halo = 0.25 * (dyeAt(uv + vec2(0.015, 0.0)).a + dyeAt(uv - vec2(0.015, 0.0)).a + dyeAt(uv + vec2(0.0, 0.03)).a + dyeAt(uv - vec2(0.0, 0.03)).a);
	c += vec3(1.0, 0.3, 0.05) * 0.15 * halo;
	return c * 1.8;
}

// the look's colour at uv: 100 % flat. Fire = hard-edged temperature bands, oil = flat darker streaks inside the
// fire (hard edges from the phase field), smoke = soft blurred flat grey behind
vec3 shade(vec2 uv) {
	vec4 d = dyeAt(uv);
	float hue = paletteHue() + d.g / max(d.a, 0.05);                    // palette rotation + per-burner variety
	if (flatStyle < 0.5) return hueShift(shadeSoft(uv), hue);
	float T = d.a;
	float aa = fwidth(T) * 0.75 + 0.0005;
	vec3 fire = hueShift(flameFlat(T, aa), hue);
	float isFire = smoothstep(fireEdge - aa, fireEdge + aa, T);
	float p = phiAt(uv);
	float pw = fwidth(p) * 0.75 + 0.002;
	float oil = smoothstep(pw, -pw, p) * smoothstep(fireEdge * 2.2 - aa, fireEdge * 2.2 + aa, T);
	fire = mix(fire, fire * (1.0 - 0.45 * iridescence), oil);
	float sm = smokeAt(uv, smokeBlur);
	float cover = (1.0 - exp(-sm * smokeDensity)) * 0.85;
	vec3 c = hueShift(vec3(0.44, 0.4, 0.37), paletteHue() * 0.5) * smokeBright * cover;   // flat smoke, faintly tinted
	c = mix(c, fire, isFire);
	return c * exposure;
}

vec3 flareTint() { return hueShift(vec3(1.0, 0.55, 0.2), paletteHue()); }
float cloudDepth(vec2 uv) { vec4 d = dyeAt(uv); return clamp(d.a * 1.0 + d.r * 0.8, 0.0, 1.0); }
