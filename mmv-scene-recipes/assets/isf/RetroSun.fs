/*{
	"DESCRIPTION": "Retro striped sun: vertical colour gradient, scrolling cut-out bands that thicken towards the bottom, soft glow, audio pulse input.",
	"CREDIT": "mmv-skills (original)",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Retro"],
	"INPUTS": [
		{"NAME": "sunPos", "LABEL": "Sun Pos", "TYPE": "point2D", "DEFAULT": [0.5, 0.45], "MIN": [0.0, 0.0], "MAX": [1.0, 1.0]},
		{"NAME": "radius", "LABEL": "Radius", "TYPE": "float", "DEFAULT": 0.28, "MIN": 0.02, "MAX": 0.8},
		{"NAME": "bands", "LABEL": "Bands", "TYPE": "float", "DEFAULT": 8.0, "MIN": 0.0, "MAX": 24.0},
		{"NAME": "bandStart", "LABEL": "Band Start", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "bandSpeed", "LABEL": "Band Speed", "TYPE": "float", "DEFAULT": 0.12, "MIN": -1.0, "MAX": 1.0},
		{"NAME": "glow", "LABEL": "Glow", "TYPE": "float", "DEFAULT": 0.6, "MIN": 0.0, "MAX": 2.0},
		{"NAME": "pulse", "LABEL": "Pulse", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "colorTop", "LABEL": "Top Color", "TYPE": "color", "DEFAULT": [1.0, 0.92, 0.25, 1.0]},
		{"NAME": "colorBottom", "LABEL": "Bottom Color", "TYPE": "color", "DEFAULT": [1.0, 0.1, 0.55, 1.0]},
		{"NAME": "glowColor", "LABEL": "Glow Color", "TYPE": "color", "DEFAULT": [1.0, 0.25, 0.6, 1.0]}
	]
}*/

void main() {
	vec2 uv = isf_FragNormCoord;
	float aspect = RENDERSIZE.x / RENDERSIZE.y;
	vec2 p = (uv - sunPos) * vec2(aspect, 1.0);
	float rad = radius * (1.0 + 0.06 * pulse);
	float d = length(p);
	float aa = 1.5 / RENDERSIZE.y;

	float disc = 1.0 - smoothstep(rad - aa, rad + aa, d);

	// v: 0 at the bottom of the disc, 1 at the top
	float v = clamp((p.y + rad) / (2.0 * rad), 0.0, 1.0);
	vec3 sunCol = mix(colorBottom.rgb, colorTop.rgb, v);

	// cut-out bands in the lower part, thicker towards the bottom
	float cut = 0.0;
	if (bands > 0.5 && v < bandStart) {
		float s = v / max(bandStart, 0.001);
		float gap = 0.1 + (1.0 - s) * 0.6;
		float x = s * bands - TIME * bandSpeed * bands * 0.5;
		cut = 1.0 - smoothstep(gap - 0.03, gap + 0.03, fract(x));
	}
	float body = disc * (1.0 - cut);

	float g = exp(-max(d - rad, 0.0) / (rad * 0.9)) * glow * (1.0 + 0.8 * pulse);
	vec3 col = sunCol * body + glowColor.rgb * g * (1.0 - body);
	gl_FragColor = vec4(col, 1.0);
}
