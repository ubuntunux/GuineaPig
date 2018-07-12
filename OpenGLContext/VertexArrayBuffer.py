import math
from ctypes import c_void_p
import random

import numpy as np
from OpenGL.GL import *

from Common import logger
from Utilities import compute_tangent
from .OpenGLContext import OpenGLContext


def CreateVertexArrayBuffer(geometry_data):
    geometry_name = geometry_data.get('name', 'VertexArrayBuffer')
    logger.info("Load %s geometry." % geometry_name)

    vertex_count = len(geometry_data.get('positions', []))
    if vertex_count == 0:
        logger.error("%s geometry has no position data." % geometry_name)
        return None

    positions = np.array(geometry_data['positions'], dtype=np.float32)

    if 'indices' not in geometry_data:
        logger.error("%s geometry has no index data." % geometry_name)
        return None

    indices = np.array(geometry_data['indices'], dtype=np.uint32)

    bone_indicies = np.array(geometry_data.get('bone_indicies', []), dtype=np.float32)

    bone_weights = np.array(geometry_data.get('bone_weights', []), dtype=np.float32)

    colors = np.array(geometry_data.get('colors', []), dtype=np.float32)
    if len(colors) == 0:
        colors = np.array([[1.0, 1.0, 1.0, 1.0]] * vertex_count, dtype=np.float32)

    texcoords = np.array(geometry_data.get('texcoords', []), dtype=np.float32)
    if len(texcoords) == 0:
        texcoords = np.array([[0.0, 0.0]] * vertex_count, dtype=np.float32)

    normals = np.array(geometry_data.get('normals', []), dtype=np.float32)
    if len(normals) == 0:
        normals = np.array([[0.0, 0.0, 1.0], ] * vertex_count, dtype=np.float32)

    tangents = np.array(geometry_data.get('tangents', []), dtype=np.float32)
    if len(tangents) == 0:
        tangents = compute_tangent(positions, texcoords, normals, indices)
        geometry_data['tangents'] = tangents.tolist()

    if 0 < len(bone_indicies) and 0 < len(bone_weights):
        vertex_array_buffer = VertexArrayBuffer(geometry_name,
                                                [positions, colors, normals, tangents, texcoords, bone_indicies,
                                                 bone_weights], indices)
    else:
        vertex_array_buffer = VertexArrayBuffer(geometry_name, [positions, colors, normals, tangents, texcoords],
                                                indices)
    return vertex_array_buffer


#  Reference : https://learnopengl.com/Advanced-OpenGL/Instancing
class InstanceBuffer:
    def __init__(self, name, layout_location, element_data):
        self.name = name
        self.instance_buffer = glGenBuffers(1)
        self.layout_location = layout_location
        # One of the elements of the instance data list
        self.component_count = len(element_data)
        self.size_of_data = element_data.nbytes
        # The instance data is a 16-byte boundary. For example, since mat4 is 64 bytes,
        # you need to divide it into 4 by 16 bytes.
        self.divide_count = math.ceil(element_data.nbytes / 16)

    def bind_instance_buffer(self, instance_data, divisor=1):
        glBindBuffer(GL_ARRAY_BUFFER, self.instance_buffer)
        glBufferData(GL_ARRAY_BUFFER, instance_data, GL_STATIC_DRAW)

        if self.divide_count == 1:
            glEnableVertexAttribArray(self.layout_location)
            glVertexAttribPointer(self.layout_location, self.component_count, GL_FLOAT, GL_FALSE, self.size_of_data,
                                  c_void_p(0))
            # divisor == 0, not instancing.
            # divisor > 0, the attribute advances once per divisor instances of the set(s) of vertices being rendered.
            glVertexAttribDivisor(self.layout_location, divisor)
        else:
            for i in range(self.divide_count):
                glEnableVertexAttribArray(self.layout_location + i)
                glVertexAttribPointer(self.layout_location + i, self.component_count, GL_FLOAT, GL_FALSE,
                                      self.size_of_data, c_void_p(self.divide_count * self.component_count * i))
                glVertexAttribDivisor(self.layout_location + i, divisor)


class VertexArrayBuffer:
    def __init__(self, name, datas, index_data):
        self.name = name
        self.vertex_component_count = []
        self.data_types = []
        self.vertex_buffer_offset = []
        self.vertex_buffer_size = 0

        for data in datas:
            element = data[0] if hasattr(data, '__len__') and 0 < len(data) else data
            stride = len(element) if hasattr(element, '__len__') else 1
            if stride == 0:
                continue
            self.vertex_component_count.append(stride)
            self.vertex_buffer_offset.append(ctypes.c_void_p(self.vertex_buffer_size))
            self.vertex_buffer_size += element.nbytes
            self.data_types.append(OpenGLContext.get_gl_dtype(data.dtype))
        self.layout_location_count = range(len(self.vertex_component_count))

        vertex_datas = np.hstack(datas).astype(np.float32)

        self.vertex_array = glGenVertexArrays(1)
        self.vertex_buffer = glGenBuffers(1)
        glBindVertexArray(self.vertex_array)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertex_datas, GL_STATIC_DRAW)

        self.index_buffer_size = index_data.nbytes
        self.index_buffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_size, index_data, GL_STATIC_DRAW)

    def delete(self):
        glDeleteVertexArrays(1, self.vertex_array)
        glDeleteBuffers(1, self.vertex_buffer)
        glDeleteBuffers(1, self.index_buffer)

    def __bind_vertex_buffer(self):
        if OpenGLContext.need_to_bind_vertex_array(self.vertex_buffer):
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)

            for layout_location in self.layout_location_count:
                glEnableVertexAttribArray(layout_location)
                glVertexAttribPointer(layout_location, self.vertex_component_count[layout_location],
                                      self.data_types[layout_location], GL_FALSE, self.vertex_buffer_size,
                                      self.vertex_buffer_offset[layout_location])
                # important : divisor reset
                glVertexAttribDivisor(layout_location, 0)

            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)

    def draw_elements(self):
        self.__bind_vertex_buffer()
        glDrawElements(GL_TRIANGLES, self.index_buffer_size, GL_UNSIGNED_INT, c_void_p(0))

    def draw_elements_instanced(self, count):
        self.__bind_vertex_buffer()
        glDrawElementsInstanced(GL_TRIANGLES, self.index_buffer_size, GL_UNSIGNED_INT, c_void_p(0), count)
