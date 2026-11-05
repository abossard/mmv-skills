/*{
	"DESCRIPTION": "Template: two independent image inputs (pin 1 = inputImage, pin 2 = inputImage2), like Mix/Mask.",
	"CREDIT": "mmv-skills template",
	"ISFVSN": "2.0",
	"CATEGORIES": ["Blend"],
	"INPUTS": [
		{"NAME": "inputImage", "TYPE": "image"},
		{"NAME": "inputImage2", "TYPE": "image"},
		{"NAME": "amount", "LABEL": "Amount", "TYPE": "float", "DEFAULT": 0.5, "MIN": 0.0, "MAX": 1.0}
	]
}*/
void main() {
	vec2 uv = isf_FragNormCoord;
	vec4 a = IMG_NORM_PIXEL(inputImage, uv);
	vec4 b = IMG_NORM_PIXEL(inputImage2, uv);
	gl_FragColor = mix(a, b, amount);
}
