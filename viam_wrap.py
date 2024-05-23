#!/usr/bin/env python3
"run a low-boilerplate module by applying it on top of a base class"

import argparse, importlib, asyncio, sys, inspect, logging, os
from typing import List, Iterator, Sequence, Union
from types import FunctionType, ModuleType
import viam.logging
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily

logger = viam.logging.getLogger(__name__)
DEFAULT_FAMILY = ModelFamily('local', 'wrapped')

# append this to the bottom of an entrypoint to use it with pyinstaller
BUILD_STANZA = """
# START viam-wrap BUILD STANZA
import sys, viam_wrap
if __name__ == '__main__':
    viam_wrap.main(sys.modules.get(__name__))
# END viam-wrap BUILD STANZA
"""

def register_model(model_class: type):
    logger.info('registering %s %s', model_class.MODEL, model_class)
    Registry.register_resource_creator(model_class.SUBTYPE, model_class.MODEL, ResourceCreatorRegistration(model_class.new))

def import_class(full_path: str) -> type:
    "takes like x.y.z.ClassName, imports x.y.z and then returns the named class"
    module_name, _, class_name = full_path.rpartition('.')
    logger.debug('importing %s from %s', class_name, module_name)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

async def module_main(args, models: List[type]):
    "run module entrypoint with given class"
    module = Module(args.socket_path)
    for model in models:
        module.add_model_from_registry(model.SUBTYPE, model.MODEL)
    await module.start()

@classmethod
def dynamic_new(cls, config, dependencies):
    "we patch in this 'new' function to classes that don't have one"
    self = cls(config.name) # pylint: disable=not-callable
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

def parse_model(orig: Union[str,Model,None]) -> Model:
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

def import_path(path: str):
    "return a module given a file path"
    # per docs https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    module_name = path.removeprefix('./').removesuffix('.py').replace('-', '_').replace('/', '.')
    logger.debug('inferred import name %s from path %s', module_name, path)
    if module_name in sys.modules:
        if os.path.samefile(path, sys.modules[module_name].__file__):
            logger.debug('reusing module %s', path)
            return sys.modules[module_name]
        else:
            logger.warning('inferred module name %s will overwrite a real module', module_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def robust_subclass(cls: type, base: type) -> bool:
    "because issubclass doesn't work on typing.Protocol"
    return inspect.isclass(cls) and base in cls.mro()

def is_imported(val, mod: ModuleType) -> bool:
    "returns True if val is not declared in the given module"
    if val.__module__ == '__main__':
        # note: mod.__spec__ doesn't exist when val.__module__ is __main__, I think
        return False
    return val.__module__ != (mod.__spec__ and mod.__spec__.name)

def pymod_to_models(mod: ModuleType, register: bool = True) -> Iterator[type]:
    "takes a module and extracts any module classes"
    for attr in dir(mod):
        val = getattr(mod, attr)
        if not robust_subclass(val, viam.resource.base.ResourceBase):
            continue
        if is_imported(val, mod):
            continue
        if isinstance(val.MODEL, str):
            val.MODEL = parse_model(val.MODEL)
        patch_attrs(val, new=dynamic_new, reconfigure=dynamic_reconfigure)
        if register:
            register_model(val)
        yield val

def main(*extras: Sequence[str | ModuleType]):
    "entrypoint for this wrapper"
    # note: extras is to support programmatic invocation, i.e. pyinstaller
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('modules', nargs='*', help="0 or more .py files containing model classes")
    p.add_argument('socket_path', help="socket path")
    p.add_argument('--debug', '-d', action='store_true', help="debug logging")
    args = p.parse_args()

    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)
    models = []
    for item in args.modules + list(extras):
        if isinstance(item, ModuleType):
            models.extend(pymod_to_models(item))
        else:
            mod = import_path(item)
            models.extend(pymod_to_models(mod))
    asyncio.run(module_main(args, models))

if __name__ == '__main__':
    main()
