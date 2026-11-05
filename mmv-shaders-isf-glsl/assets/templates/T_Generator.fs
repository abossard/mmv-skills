/*{
	"DESCRIPTION": "Template: generator (no image input). Copy, rename, change main(). Param names in Magic: LABEL else NAME with a capital first letter.",
	"CREDIT": "mmv-skills template",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator"],
	"INPUTS": [
		{"NAME": "scale", "LABEL": "Scale", "TYPE": "float", "DEFAULT": 4.0, "MIN": 0.5, "MAX": 20.0},
		{"NAME": "level", "LABEL": "Level", "TYPE": "float", "DEFAULT": 0.0, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "center", "LABEL": "Center", "TYPE": "point2D", "DEFAULT": [0.5, 0.5], "MIN": [0.0, 0.0], "MAX": [1.0, 1.0]},
		{"NAME": "mode", "LABEL": "Mode", "TYPE": "long", "VALUES": [0, 1], "LABELS": ["Rings", "Stripes"], "DEFAULT": 0},
		{"NAME": "tint", "LABEL": "Tint", "TYPE": "color", "DEFAULT": [1.0, 0.3, 0.7, 1.0]}
	]
}*/
void main() {
	vec2 uv = isf_FragNormCoord;
	float aspect = RENDERSIZE.x / RENDERSIZE.y;
	vec2 p = (uv - center) * vec2(aspect, 1.0);
	float d = (mode == 0) ? length(p) : p.x;       // VALUES [0, 1]: option index and value are the same here
	float v = 0.5 + 0.5 * sin(d * scale * 6.2831853 - TIME * 2.0);
	v *= 0.4 + 0.6 * level;
	gl_FragColor = vec4(tint.rgb * v, 1.0);
}
