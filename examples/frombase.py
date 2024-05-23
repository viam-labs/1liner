#!/usr/bin/env python3
# frombase.py
import argparse, asyncio, logging
from viam.components.sensor import Sensor
from viam.resource.types import Model, ModelFamily
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.module.module import Module

logger = logging.getLogger(__name__)
DEFAULT_FAMILY = ModelFamily('local', 'wrapped')

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

def module_main(*models):
    "run module entrypoint with given class"
    p = argparse.ArgumentParser()
    p.add_argument('socket_path', help="todo fill me in")
    args = p.parse_args()

    asyncio.run(module_main_inner(args, *models))

async def module_main_inner(args, *models):
    module = Module(args.socket_path)
    for model in models:
        module.add_model_from_registry(model.SUBTYPE, model.MODEL)
    await module.start()

class EasyBase:
    "mixin for easy model creation"
    def __init_subclass__(cls, register=True, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.MODEL = parse_model(cls.MODEL)
        if register:
            cls.register()

    @classmethod
    def register(cls):
        # logger.info('registering %s %s', model_class.MODEL, model_class)
        Registry.register_resource_creator(cls.SUBTYPE, cls.MODEL, ResourceCreatorRegistration(cls.new))

    @classmethod
    def new(cls, config, dependencies):
        "we patch in this 'new' function to classes that don't have one"
        self = cls(config.name)
        logger.info('created %s %s', self, config.name)
        self.reconfigure(config, dependencies)
        return self

    def reconfigure(self, config, dependencies):
        logger.info('reconfigure %s', self)

############ pretend above this line is library code

class MyModel(Sensor, EasyBase):
    MODEL = "viam-labs:lowcode:sensor"

    async def get_readings(self, **kwargs):
        return {"success?": True}

if __name__ == '__main__':
    module_main(MyModel)
