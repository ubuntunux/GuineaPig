from OpenGL.GL import *

from Common import logger
from App import CoreManager
from Object import Quad
from OpenGLContext import RenderTargets, RenderTargetManager


class PostProcess:
    def __init__(self, name, material_instance):
        logger.info("Create PostProcess : %s" % name)
        self.name = name
        self.material_instance = material_instance

    def bind(self):
        self.material_instance.useProgram()
        self.material_instance.bind()


class CopyRenderTarget(PostProcess):
    def __init__(self, name):
        material_instance = CoreManager.instance().resource_manager.getMaterialInstance("copy_rendertarget")
        PostProcess.__init__(self, name, material_instance)

    def bind(self, src_texture, dst_texture):
        '''
        :param src_texture: enum RenderTargets
        :param dst_texture: Texture2D
        :return:
        '''
        CoreManager.instance().renderer.framebuffer.bind_rendertarget(dst_texture, clear_color=False, depthtexture=None,
                                                                      clear_depth=False)
        texture_diffuse = RenderTargetManager.instance().get_rendertarget(src_texture)
        self.material_instance.set_uniform_data("texture_diffuse", texture_diffuse)
        PostProcess.bind(self)


class Tonemapping(PostProcess):
    def __init__(self, name):
        material_instance = CoreManager.instance().resource_manager.getMaterialInstance("tonemapping")
        PostProcess.__init__(self, name, material_instance)

    def bind(self):
        PostProcess.bind(self)
        backbuffer = RenderTargetManager.instance().get_rendertarget(RenderTargets.BACKBUFFER)
        self.material_instance.bind_uniform_data("texture_diffuse", backbuffer)

        texture_diffuse = RenderTargetManager.instance().get_rendertarget(RenderTargets.DIFFUSE)
        CoreManager.instance().renderer.framebuffer.bind_rendertarget(texture_diffuse,
                                                                      clear_color=True,
                                                                      depthtexture=None,
                                                                      clear_depth=False)
