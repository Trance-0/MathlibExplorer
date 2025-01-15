precision highp float;

in vec3 position;
in vec4 color;
in float alpha;

uniform float scale;

uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

out vec4 vColor;
out float vAlpha;
uniform bool picking;

void main() {
    vColor = color;
    vAlpha = alpha;

    vec4 mvPosition = modelViewMatrix * vec4(position.xy, 0.0, 1.0);

    gl_PointSize = position.z * min(scale, 10.0) * 3.0;
    if(!picking) gl_PointSize = gl_PointSize * 1.5;

    gl_Position = projectionMatrix * mvPosition;
}