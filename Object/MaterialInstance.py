import configparser
from collections import OrderedDict
import os
import re
import traceback

from Common import logger
from App import CoreManager
from OpenGLContext import CreateUniformDataFromString
from Utilities import Attributes


class MaterialInstance:
    def __init__(self, material_instance_name, filePath):
        self.valid = False
        logger.info("Load Material Instance : " + material_instance_name)
        self.name = material_instance_name
        self.material = None
        self.uniform_datas = {}
        self.linked_uniform_map = OrderedDict({})
        self.Attributes = Attributes()

        # open material instance file
        material_inst_file = configparser.ConfigParser()
        material_inst_file.optionxform = lambda option: option  # prevent the key value being lowercase
        material_inst_file.read(filePath)

        # Load data - create uniform data from config file
        shader_name = ""
        macros = OrderedDict()
        for data_type in material_inst_file.sections():
            if data_type == 'Shader':
                # get shader name
                if material_inst_file.has_option('Shader', 'shader'):
                    shader_name = material_inst_file.get('Shader', 'shader')
            elif data_type == 'Define':
                # gather preprocess
                for data_name in material_inst_file[data_type]:
                    macros[data_name] = material_inst_file.get(data_type, data_name)
            else:
                # create uniform data
                for data_name in material_inst_file[data_type]:
                    strValue = material_inst_file.get(data_type, data_name)
                    data = CreateUniformDataFromString(data_type, strValue)
                    if data is not None:
                        self.uniform_datas[data_name] = data
                    else:
                        logger.error("%s MaterialInstance, %s is None." % (self.name, data_type))
        # link uniform_buffers and uniform_data
        material = CoreManager.instance().resource_manager.getMaterial(shader_name, macros)
        self.set_material(material)

        if self.material is None:
            logger.error("%s material instance has no material." % self.name)
            return

        self.valid = True

    def clear(self):
        self.linked_uniform_map = OrderedDict({})
        self.Attributes.clear()

    def set_material(self, material):
        if material and self.material != material:
            self.material = material

            # link_uniform_buffers
            self.linked_uniform_map = OrderedDict({})
            uniform_names = self.material.uniform_buffers.keys()
            for uniform_name in uniform_names:
                uniform_buffer = self.material.uniform_buffers[uniform_name]
                # find uniform data
                if uniform_name in self.uniform_datas:
                    uniform_data = self.uniform_datas[uniform_name]
                else:
                    # cannot found uniform data. just set default uniform data.
                    uniform_data = CreateUniformDataFromString(uniform_buffer.data_type)
                    if uniform_data is not None:
                        self.uniform_datas[uniform_name] = uniform_data

                if uniform_data is None:
                    logger.error("Material requires %s data. %s material instance has no %s." % (
                        uniform_name, self.name, uniform_name))

                # link between uniform buffer and data.
                self.linked_uniform_map[uniform_name] = [uniform_buffer, uniform_data]

    def bind(self):
        for uniform_buffer, uniform_data in self.linked_uniform_map.values():
            uniform_buffer.bind_uniform(uniform_data)

    def bind_uniform_data(self, uniform_name, uniform_data):
        if uniform_name in self.linked_uniform_map:
            self.linked_uniform_map[uniform_name][0].bind_uniform(uniform_data)
        else:
            logger.error('%s material instance has no %s uniform variable.' % (self.name, uniform_name))

    def set_uniform_data(self, uniform_name, uniform_data):
        if uniform_name in self.linked_uniform_map:
            self.linked_uniform_map[uniform_name][1] = uniform_data
        else:
            logger.error('%s material instance has no %s uniform variable.' % (self.name, uniform_name))

    def get_program(self):
        return self.material.program

    def useProgram(self):
        self.material.useProgram()

    def getAttribute(self):
        self.Attributes.setAttribute('name', self.name)
        self.Attributes.setAttribute('material', self.material)
        for uniform_buffer, uniform_data in self.linked_uniform_map.values():
            self.Attributes.setAttribute(uniform_buffer.name, uniform_data)
        return self.Attributes