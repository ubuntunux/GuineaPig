#version 430 core

#include "utility.glsl"
#include "scene_constants.glsl"
#include "default_vs.glsl"

//-------------- MATERIAL_COMPONENTS ---------------//

#include "default_material.glsl"

//----------- FRAGMENT_SHADER ---------------//


#ifdef FRAGMENT_SHADER
in VERTEX_OUTPUT vs_output;
out vec4 fs_output;

void main() {
    vec4 baseColor = get_base_color(vs_output.texCoord.xy);

    if(baseColor.a < 0.333f && enable_blend != 1)
    {
        discard;
    }

    fs_output = vec4(vec3(gl_FragCoord.z, 0.0, 0.0), 1.0);
}
#endif