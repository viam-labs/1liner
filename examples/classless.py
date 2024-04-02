# classless.py -- short-mode low-code sample

from viam.components.sensor import Sensor as BaseClass

async def get_readings(self, **kwargs):
    return {"success?": True}
