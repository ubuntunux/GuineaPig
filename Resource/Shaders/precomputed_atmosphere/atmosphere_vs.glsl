#include "scene_constants.glsl"

#ifdef GL_VERTEX_SHADER
layout(location = 0) in vec4 vertex;
out vec3 eye_ray;
out vec3 screen_center_ray;
out vec2 uv;
void main()
{
    uv = vertex.xy * 0.5 + 0.5;
    eye_ray = (INV_VIEW_ORIGIN * vec4((INV_PROJECTION * vertex).xyz, 0.0)).xyz;
    screen_center_ray = normalize((INV_VIEW_ORIGIN * vec4((INV_PROJECTION * vec4(0.0, 0.0, 1.0, 0.0)).xyz, 0.0)).xyz);
    gl_Position = vertex;
}
#endif