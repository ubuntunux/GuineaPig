from collections import OrderedDict


class Attribute:
    def __init__(self, attrName, attrValue, attrType, isReadOnly):
        self.name = attrName
        self.value = attrValue
        self.type = attrType
        self.isReadOnly = isReadOnly


class Attributes:
    def __init__(self):
        self.attributeMap = OrderedDict()

    def clear(self):
        self.attributeMap = OrderedDict()

    def get_attribute(self, attrname):
        return self.attributeMap[attrname] if attrname in self.attributeMap else None

    def get_attributes(self):
        return self.attributeMap.values()

    def get_attributeNames(self):
        return self.attributeMap.keys()

    def set_attribute(self, attrName, attrValue, isReadOnly=False):
        if attrValue is None:
            attrValue = ""
            attrType = None
        else:
            # get type
            attrType = type(attrValue)
            # class object use name as attrValue.
            if hasattr(attrValue, "name"):
                attrValue = attrValue.name
        self.attributeMap[attrName] = Attribute(attrName, attrValue, attrType, isReadOnly)
