/*{
	"DESCRIPTION": "Three-stop sunset gradient sky with twinkling stars and a horizon haze band.",
	"CREDIT": "mmv-skills (original)",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Retro"],
	"INPUTS": [
		{"NAME": "horizon", "LABEL": "Horizon", "TYPE": "float", "DEFAULT": 0.45, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "skyTop", "LABEL": "Sky Top", "TYPE": "color", "DEFAULT": [0.02, 0.0, 0.12, 1.0]},
		{"NAME": "skyMid", "LABEL": "Sky Mid", "TYPE": "color", "DEFAULT": [0.45, 0.04, 0.45, 1.0]},
		{"NAME": "skyHorizon", "LABEL": "Sky Horizon", "TYPE": "color", "DEFAULT": [1.0, 0.35, 0.3, 1.0]},
		{"NAME": "starAmount", "LABEL": "Stars", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "twinkle", "LABEL": "Twinkle", "TYPE": "float", "DEFAULT": 0.6, "MIN": 0.0, "MAX": 1.0}
	]
}*/

float hash21(vec2 p) {
	p = fract(p * vec2(123.34, 456.21));
	p += dot(p, p + 45.32);
	return fract(p.x * p.y);
}

void main() {
	vec2 uv = isf_FragNormCoord;
	float aspect = RENDERSIZE.x / RENDERSIZE.y;
	float t = clamp((uv.y - horizon) / max(1.0 - horizon, 0.001), 0.0, 1.0);
	vec3 col = mix(skyHorizon.rgb, skyMid.rgb, smoothstep(0.0, 0.45, t));
	col = mix(col, skyTop.rgb, smoothstep(0.35, 1.0, t));

	// stars, only in the upper sky
	vec2 sp = vec2(uv.x * aspect, uv.y) * 90.0;
	vec2 cell = floor(sp);
	vec2 f = fract(sp) - 0.5;
	float r = hash21(cell);
	float present = step(1.0 - starAmount * 0.08, r);
	float size = 0.05 + 0.1 * hash21(cell + 7.1);
	float star = present * (1.0 - smoothstep(size * 0.5, size, length(f)));
	float tw = 1.0 - twinkle * 0.5 * (1.0 + sin(TIME * (2.0 + 5.0 * hash21(cell + 3.3)) + r * 40.0));
	col += vec3(1.0, 0.95, 1.0) * star * tw * smoothstep(0.25, 0.7, t);

	gl_FragColor = vec4(col, 1.0);
}
