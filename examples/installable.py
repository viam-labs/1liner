#!/usr/bin/env viam-wrap
import sys
import viam_wrap
from viam.components.sensor import Sensor

class Whatever(Sensor):
    MODEL = 'viam:sensor:whatever'

    async def get_readings(self, **kwargs):
        return {"success?": True}

if __name__ == '__main__':
    # necessary for pyinstaller to see it
    # build this with: 
    # pyinstaller --onefile --hidden-import viam-wrap --paths $VIRTUAL_ENV/lib/python3.10/site-packages installable.py 
    # `--paths` arg may no longer be necessary once viam-wrap is published somewhere
    viam_wrap.main(sys.modules.get(__name__))
