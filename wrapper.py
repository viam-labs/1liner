#!/usr/bin/env python3
"run a low-boilerplate module by applying it on top of a base class"

import argparse, importlib, asyncio
from typing import Type
from types import FunctionType
import viam.logging
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily

logger = viam.logging.getLogger(__name__)
DEFAULT_FAMILY = ModelFamily('local', 'wrapped')

def register_model(model_class: Type):
    Registry.register_resource_creator(model_class.SUBTYPE, model_class.MODEL, ResourceCreatorRegistration(model_class.new))

def import_class(full_path: str) -> Type:
    "takes like x.y.z.ClassName, imports x.y.z and then returns the named class"
    module_name, _, class_name = full_path.rpartition('.')
    logger.debug('importing %s from %s', class_name, module_name)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

async def module_main(model_class: Type):
    "run module entrypoint with given class"
    module = Module.from_args()
    module.add_model_from_registry(model_class.SUBTYPE, model_class.MODEL)
    await module.start()

@classmethod
def dynamic_new(cls, config, dependencies):
    "we patch in this 'new' function to classes that don't have one"
    self = cls(config.name)
    logger.info('created %s %s', self, config.name)
    self.reconfigure(config, dependencies)
    return self

def dynamic_reconfigure(self, config, dependencies):
    logger.info('reconfigure %s', self)

def class_from_module(py_module):
    "takes an imported python module and constructs a Model subclass from functions"
    funcs = {
        name: attr
        for name in dir(py_module)
        if isinstance((attr := getattr(py_module, name)), FunctionType)
    }
    model_class = type('ClasslessModule', (py_module.BaseClass,), funcs)
    logger.debug('model_class now has %s', dir(model_class))
    return model_class

def parse_model(orig: str|Model|None) -> Model:
    "take a model, string, or None and turn it into a Model"
    # todo: instead of doing this in wrapper, do it metaclass-style for every py module
    if isinstance(orig, Model):
        return orig
    elif orig is None:
        # todo: think about collisions here; maybe short random string
        return Model(DEFAULT_FAMILY, 'anonymous')
    elif ':' in orig:
        *family, name = orig.split(':')
        return Model(ModelFamily(*family), name)
    else:
        return Model(DEFAULT_FAMILY, name)

def patch_attrs(cls, **attrs):
    "set class attributes if not already present"
    for attr, val in attrs.items():
        if not hasattr(cls, attr):
            logger.debug('patching %s.%s with %s', cls, attr, val)
            setattr(cls, attr, val)

def main():
    "entrypoint for this wrapper"
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('socket_path', help="socket path")
    # todo: support multiple models or all models in module or something
    p.add_argument('--model', default='mymodel.Model', help="import spec for your override implementation. use trailing period for classless mode")
    p.add_argument('--name', help="model name in classless mode. if it has ':' it's used as is, otherwise you get 'local:classless:<name>'")
    args = p.parse_args()
    
    # logger.setLevel(logging.DEBUG)
    if args.model.endswith('.'):
        # todo: potentially also support 'all module subclasses from module'
        model_class = class_from_module(importlib.import_module(args.model[:-1]))
        model_class.MODEL = parse_model(args.name)
    else:
        model_class = import_class(args.model)
        if type(model_class.MODEL) is str:
            model_class.MODEL = parse_model(model_class.MODEL)
    patch_attrs(model_class, new=dynamic_new, reconfigure=dynamic_reconfigure)
    register_model(model_class)
    asyncio.run(module_main(model_class))

if __name__ == '__main__':
    main()
