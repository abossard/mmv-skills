/*{
	"DESCRIPTION": "CRT finish: scanlines, RGB split, barrel curvature, vignette and mild flicker. Cheap, single pass.",
	"CREDIT": "mmv-skills (original)",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Retro", "Stylize"],
	"INPUTS": [
		{"NAME": "inputImage", "TYPE": "image"},
		{"NAME": "scanlines", "LABEL": "Scanlines", "TYPE": "float", "DEFAULT": 0.35, "MIN": 0.0, "MAX": 1.0},
		{"NAME": "lineCount", "LABEL": "Line Count", "TYPE": "float", "DEFAULT": 360.0, "MIN": 60.0, "MAX": 1080.0},
		{"NAME": "split", "LABEL": "RGB Split", "TYPE": "float", "DEFAULT": 0.002, "MIN": 0.0, "MAX": 0.02},
		{"NAME": "curve", "LABEL": "Curvature", "TYPE": "float", "DEFAULT": 0.08, "MIN": 0.0, "MAX": 0.4},
		{"NAME": "vignette", "LABEL": "Vignette", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.5},
		{"NAME": "flicker", "LABEL": "Flicker", "TYPE": "float", "DEFAULT": 0.03, "MIN": 0.0, "MAX": 0.2}
	]
}*/

void main() {
	vec2 uv = isf_FragNormCoord;
	vec2 c = uv * 2.0 - 1.0;
	c *= 1.0 + curve * dot(c, c) * 0.5;
	vec2 suv = c * 0.5 + 0.5;
	if (suv.x < 0.0 || suv.x > 1.0 || suv.y < 0.0 || suv.y > 1.0) {
		gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
		return;
	}
	float r = IMG_NORM_PIXEL(inputImage, suv + vec2(split, 0.0)).r;
	float g = IMG_NORM_PIXEL(inputImage, suv).g;
	float b = IMG_NORM_PIXEL(inputImage, suv - vec2(split, 0.0)).b;
	vec3 col = vec3(r, g, b);
	float sl = 0.5 + 0.5 * sin(suv.y * lineCount * 6.2831853);
	col *= 1.0 - scanlines * (1.0 - sl);
	float vig = 1.0 - vignette * dot(c * 0.6, c * 0.6);
	col *= clamp(vig, 0.0, 1.0);
	col *= 1.0 + flicker * sin(TIME * 90.0);
	gl_FragColor = vec4(col, 1.0);
}
