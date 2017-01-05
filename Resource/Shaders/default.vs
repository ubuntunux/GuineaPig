#version 430 core

layout(location=0) in vec3 position;
layout(location=1) in vec4 color;
layout(location=2) in vec3 normal;
layout(location=3) in vec3 tangent;
layout(location=4) in vec2 texcoord;

layout(std140) uniform sceneConstants
{
    mat4 view;
    mat4 perspective;
    vec4 camera_position;
};

layout(std140) uniform lightConstants
{
    vec4 light_position;
};

uniform mat4 model;
uniform mat4 mvp;

out struct DATA
{
    vec3 worldPosition;
    vec4 vertexColor;
    vec3 normalVector;
    mat4 tangentToWorld;
    vec2 textureCoordinate;
    vec3 cameraVector;
    vec3 cameraPosition;
    vec3 lightVector;
    vec3 lightPosition;
} data;

void main() {
    data.vertexColor = color;
    data.worldPosition = (model * vec4(position, 1.0)).xyz;
    data.normalVector = (model * vec4(normal, 0.0)).xyz;
    vec3 bitangent = cross(tangent, normal);
    data.tangentToWorld = model * mat4(vec4(tangent, 0.0), vec4(bitangent,0.0), vec4(normal, 0.0), vec4(0.0, 0.0, 0.0, 1.0));
    data.textureCoordinate = texcoord;

    data.cameraPosition = camera_position.xyz;
    data.cameraVector = camera_position.xyz - data.worldPosition;
    //data.cameraVector = normalize(data.cameraVector);

    data.lightPosition = light_position.xyz;
    data.lightVector = light_position.xyz - data.worldPosition;
    //data.lightVector = normalize(data.lightVector);
    gl_Position = mvp * vec4(position, 1.0f);
}