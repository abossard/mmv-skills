/*{
	"DESCRIPTION": "Template: persistent buffer (feedback trails). Pass 0 accumulates into `trailBuf` (kept between frames), pass 1 shows it. Reset with FRAMEINDEX == 0.",
	"CREDIT": "mmv-skills template",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Stylize"],
	"INPUTS": [
		{"NAME": "inputImage", "TYPE": "image"},
		{"NAME": "decay", "LABEL": "Decay", "TYPE": "float", "DEFAULT": 0.92, "MIN": 0.5, "MAX": 0.995},
		{"NAME": "zoom", "LABEL": "Zoom", "TYPE": "float", "DEFAULT": 1.003, "MIN": 0.98, "MAX": 1.02}
	],
	"PASSES": [
		{"TARGET": "trailBuf", "PERSISTENT": true, "FLOAT": true},
		{}
	]
}*/
void main() {
	vec2 uv = isf_FragNormCoord;
	if (PASSINDEX == 0) {
		vec2 c = (uv - 0.5) / zoom + 0.5;
		vec4 prev = IMG_NORM_PIXEL(trailBuf, c) * decay;
		vec4 now = IMG_NORM_PIXEL(inputImage, uv);
		if (FRAMEINDEX == 0) prev = vec4(0.0);
		gl_FragColor = max(prev, now);
	} else {
		gl_FragColor = IMG_NORM_PIXEL(trailBuf, uv);
	}
}
