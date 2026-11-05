/*{
	"DESCRIPTION": "Two layered mountain ridge silhouettes with a neon edge line. Transparent outside the ridges, so it composites over a sky.",
	"CREDIT": "mmv-skills (original)",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Retro"],
	"INPUTS": [
		{"NAME": "horizon", "LABEL": "Horizon", "TYPE": "float", "DEFAULT": 0.45, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "height", "LABEL": "Height", "TYPE": "float", "DEFAULT": 0.12, "MIN": 0.0, "MAX": 0.5},
		{"NAME": "ridgeScale", "LABEL": "Ridge Scale", "TYPE": "float", "DEFAULT": 3.0, "MIN": 0.5, "MAX": 12.0},
		{"NAME": "drift", "LABEL": "Drift", "TYPE": "float", "DEFAULT": 0.0, "MIN": -1.0, "MAX": 1.0},
		{"NAME": "seed", "LABEL": "Seed", "TYPE": "float", "DEFAULT": 3.0, "MIN": 0.0, "MAX": 100.0},
		{"NAME": "edgeGlow", "LABEL": "Edge Glow", "TYPE": "float", "DEFAULT": 1.0, "MIN": 0.0, "MAX": 3.0},
		{"NAME": "bodyColor", "LABEL": "Body Color", "TYPE": "color", "DEFAULT": [0.04, 0.0, 0.1, 1.0]},
		{"NAME": "edgeColor", "LABEL": "Edge Color", "TYPE": "color", "DEFAULT": [0.2, 0.9, 1.0, 1.0]}
	]
}*/

float h1(float n) { return fract(sin(n) * 43758.5453); }

float vnoise(float x) {
	float i = floor(x);
	float f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(h1(i), h1(i + 1.0), f);
}

// triangular ridge noise: abs() gives sharp peaks
float ridge(float x, float sd) {
	float v = 0.0;
	float a = 0.6;
	float fq = 1.0;
	for (int i = 0; i < 4; i++) {
		v += a * (1.0 - abs(2.0 * vnoise(x * fq + sd) - 1.0));
		fq *= 2.1;
		a *= 0.5;
	}
	return v;
}

void main() {
	vec2 uv = isf_FragNormCoord;
	float aspect = RENDERSIZE.x / RENDERSIZE.y;
	float x = uv.x * aspect * ridgeScale + TIME * drift;
	float far = horizon + height * ridge(x * 0.7, seed);
	float near = horizon + height * 0.7 * ridge(x * 1.3 + 17.0, seed + 9.0) - 0.01;

	float aa = 1.5 / RENDERSIZE.y;
	float fMask = 1.0 - smoothstep(far - aa, far + aa, uv.y);
	float nMask = 1.0 - smoothstep(near - aa, near + aa, uv.y);
	float fEdge = exp(-abs(uv.y - far) * RENDERSIZE.y * 0.18);
	float nEdge = exp(-abs(uv.y - near) * RENDERSIZE.y * 0.18);

	vec3 col = vec3(0.0);
	float a = 0.0;
	// far layer slightly lighter than near
	col = mix(col, bodyColor.rgb * 1.6, fMask);
	a = max(a, fMask);
	col += edgeColor.rgb * fEdge * edgeGlow * 0.6 * step(uv.y, far + 0.02);
	col = mix(col, bodyColor.rgb, nMask);
	a = max(a, nMask);
	col += edgeColor.rgb * nEdge * edgeGlow * step(uv.y, near + 0.02);
	a = max(a, clamp(max(fEdge, nEdge) * edgeGlow * 0.5, 0.0, 1.0));
	// below the horizon everything is floor: keep it transparent
	a *= step(horizon - 0.02, uv.y);
	gl_FragColor = vec4(col, a);
}
