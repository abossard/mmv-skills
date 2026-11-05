/*{
	"DESCRIPTION": "Template: audio spectrum bars. The audioFFT input becomes a `Source` param (value = Layer id). Row 0.5 of fftImage holds the magnitudes along x.",
	"CREDIT": "mmv-skills template",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Generator", "Audio Visualizer"],
	"INPUTS": [
		{"NAME": "fftImage", "LABEL": "Source", "TYPE": "audioFFT"},
		{"NAME": "gain", "LABEL": "Gain", "TYPE": "float", "DEFAULT": 2.0, "MIN": 0.5, "MAX": 8.0},
		{"NAME": "bars", "LABEL": "Bars", "TYPE": "float", "DEFAULT": 48.0, "MIN": 8.0, "MAX": 128.0},
		{"NAME": "lowColor", "LABEL": "Low Color", "TYPE": "color", "DEFAULT": [1.0, 0.1, 0.6, 1.0]},
		{"NAME": "highColor", "LABEL": "High Color", "TYPE": "color", "DEFAULT": [0.1, 0.9, 1.0, 1.0]}
	]
}*/
void main() {
	vec2 uv = isf_FragNormCoord;
	float cell = floor(uv.x * bars) / bars;
	// log-ish frequency axis so bass gets more bars
	float f = pow(cell, 2.0);
	float mag = IMG_NORM_PIXEL(fftImage, vec2(f, 0.5)).r * gain;
	float gap = step(0.15, fract(uv.x * bars));
	float on = step(uv.y, mag) * gap;
	vec3 col = mix(lowColor.rgb, highColor.rgb, cell);
	gl_FragColor = vec4(col * on, 1.0);
}
