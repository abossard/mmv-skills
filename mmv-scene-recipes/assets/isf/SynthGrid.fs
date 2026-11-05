/*{
	"DESCRIPTION": "Perspective neon floor grid that scrolls towards the camera. Lines fade into the horizon. Transparent above the horizon.",
	"CREDIT": "mmv-skills (original)",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Retro"],
	"INPUTS": [
		{"NAME": "horizon", "LABEL": "Horizon", "TYPE": "float", "DEFAULT": 0.45, "MIN": 0.1, "MAX": 0.9},
		{"NAME": "camHeight", "LABEL": "Cam Height", "TYPE": "float", "DEFAULT": 0.35, "MIN": 0.05, "MAX": 2.0},
		{"NAME": "density", "LABEL": "Density", "TYPE": "float", "DEFAULT": 4.0, "MIN": 1.0, "MAX": 20.0},
		{"NAME": "speed", "LABEL": "Scroll", "TYPE": "float", "DEFAULT": 0.6, "MIN": -4.0, "MAX": 4.0},
		{"NAME": "lineWidth", "LABEL": "Line Width", "TYPE": "float", "DEFAULT": 1.5, "MIN": 0.2, "MAX": 6.0},
		{"NAME": "fadeAmount", "LABEL": "Horizon Fade", "TYPE": "float", "DEFAULT": 0.8, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "glow", "LABEL": "Glow", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 2.0},
		{"NAME": "pulse", "LABEL": "Pulse", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "lineColor", "LABEL": "Line Color", "TYPE": "color", "DEFAULT": [1.0, 0.2, 0.75, 1.0]},
		{"NAME": "floorColor", "LABEL": "Floor Color", "TYPE": "color", "DEFAULT": [0.06, 0.0, 0.14, 1.0]},
		{"NAME": "horizonColor", "LABEL": "Horizon Glow", "TYPE": "color", "DEFAULT": [1.0, 0.35, 0.5, 1.0]}
	]
}*/

float gridLine(float c, float w) {
	// distance to the nearest integer line, in cell units; w is the half width in cell units
	float f = abs(fract(c - 0.5) - 0.5);
	float aa = fwidth(c) * 0.75;
	return 1.0 - smoothstep(w - aa, w + aa + 0.0001, f);
}

void main() {
	vec2 uv = isf_FragNormCoord;
	float aspect = RENDERSIZE.x / RENDERSIZE.y;
	float h = horizon - uv.y;
	if (h <= 0.0005) {
		gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
		return;
	}
	float z = camHeight / h;
	float x = (uv.x - 0.5) * aspect * z;
	vec2 g = vec2(x * density * 0.25, z * density * 0.25 - TIME * speed);
	float w = lineWidth * 0.5 / RENDERSIZE.y * z * density * 0.25;
	w = clamp(w * (1.0 + 0.6 * pulse), 0.01, 0.45);
	float lines = max(gridLine(g.x, w), gridLine(g.y, w));
	float fade = mix(1.0, smoothstep(0.0, 0.25, h), fadeAmount);
	float haze = exp(-h * 9.0);
	vec3 col = floorColor.rgb * (0.4 + 0.6 * (1.0 - haze));
	col += horizonColor.rgb * haze * 0.55 * glow;
	vec3 neon = lineColor.rgb * (1.0 + 0.8 * pulse);
	col = mix(col, neon, lines * fade);
	col += lineColor.rgb * lines * fade * glow * 0.6;
	gl_FragColor = vec4(col, 1.0);
}
