# sample_override.py -- example of how to create a low-boilerplate module
from viam.components.sensor import Sensor

class Model(Sensor):
    MODEL = "viam-labs:lowcode:sensor"

    async def get_readings(self, extra: dict | None, **kwargs) -> dict:
        return {"success?": True}
