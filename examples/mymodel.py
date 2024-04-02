#!.direnv/python-3.10.12/bin/python ./wrapper.py
# mymodel.py -- example low-boilerplate module
from viam.components.sensor import Sensor

class Model(Sensor):
    MODEL = "viam-labs:lowcode:sensor"

    async def get_readings(self, **kwargs):
        return {"success?": True}
