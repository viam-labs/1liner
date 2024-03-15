#!/usr/bin/env python3
"run a low-boilerplate module by applying it on top of a base class"

import argparse, importlib, logging, asyncio
from typing import Type
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily

logger = logging.getLogger(__name__)

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
    return cls(config.name)

def main():
    "entrypoint for this wrapper"
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('socket_path', help="socket path")
    # todo: support multiple models or all models in module or something
    p.add_argument('--model', default='mymodel.Model', help="import spec for your override implementation")
    args = p.parse_args()
    
    logging.basicConfig(level=logging.DEBUG)
    model_class = import_class(args.model)
    if type(model_class.MODEL) is str:
        # note: we're testing type rather than isinstance() in case Model inherits str
        *family, name = model_class.MODEL.split(':')
        model_class.MODEL = Model(ModelFamily(*family), name)
        logger.debug('parsed MODEL to %s', model_class.MODEL)
    if not hasattr(model_class, 'new'):
        logger.debug('patching %s with dynamic_new', model_class)
        model_class.new = dynamic_new
    register_model(model_class)
    asyncio.run(module_main(model_class))

if __name__ == '__main__':
    main()
