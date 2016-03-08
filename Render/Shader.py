from OpenGL.GL.shaders import *

from Core import coreManager
from Utilities import Singleton

DEFAULT_VERTEX_SHADER = '''
    varying vec3 normal;
    void main() {
        normal = gl_NormalMatrix * gl_Normal;
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    }'''

DEFAULT_PIXEL_SHADER = '''
     varying vec3 normal;
    void main() {
        float intensity;
        vec4 color;
        vec3 n = normalize(normal);
        vec3 l = normalize(gl_LightSource[0].position).xyz;        
        intensity = saturate(dot(l, n));
        color = gl_LightSource[0].ambient + gl_LightSource[0].diffuse * intensity;
    
        gl_FragColor = color;
    }'''


def createShader(vertexShader, pixelShader):
    return compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER), compileShader(pixelShader, GL_FRAGMENT_SHADER), )

#------------------------------#
# CLASS : ShaderManager
#------------------------------#
class ShaderManager(Singleton):
    def __init__(self):
        self.shaders = {}
        self.default_shader = None
        # regist
        coreManager.regist("ShaderManager", self)

    def initialize(self):
        self.default_shader = createShader(DEFAULT_VERTEX_SHADER, DEFAULT_PIXEL_SHADER)

    def createShader(self, shaderName, vertexShader, pixelShader):
        shader = createShader(vertexShader, pixelShader)
        self.shaders[shaderName] = shader

#------------------------------#
# Globals
#------------------------------#
shaderManager = ShaderManager.instance()