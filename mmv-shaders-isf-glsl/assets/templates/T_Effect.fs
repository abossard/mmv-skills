/*{
	"DESCRIPTION": "Template: single-input effect. Always sample with IMG_NORM_PIXEL and write alpha.",
	"CREDIT": "mmv-skills template",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Color Effect"],
	"INPUTS": [
		{"NAME": "inputImage", "TYPE": "image"},
		{"NAME": "amount", "LABEL": "Amount", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "shift", "LABEL": "Shift", "TYPE": "point2D", "DEFAULT": [0.01, 0.0], "MIN": [-0.1, -0.1], "MAX": [0.1, 0.1]}
	]
}*/
void main() {
	vec2 uv = isf_FragNormCoord;
	vec4 c = IMG_NORM_PIXEL(inputImage, uv);
	vec4 r = IMG_NORM_PIXEL(inputImage, uv + shift * amount);
	vec4 b = IMG_NORM_PIXEL(inputImage, uv - shift * amount);
	gl_FragColor = vec4(r.r, c.g, b.b, c.a);
}
