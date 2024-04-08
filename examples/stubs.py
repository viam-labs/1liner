#!/usr/bin/env viam-wrap
# #!/usr/bin/env python3
# stubs.py -- experiment with default implementations of missing functions
from viam.components.sensor import Sensor
from viam.components.motor import Motor

def stubme(cls):
    import typing
    for attr in cls.__abstractmethods__:
        val = getattr(cls, attr)
        hints = typing.get_type_hints(val)
        if (ret := hints.get('return')):
            match ret._name:
                case 'Mapping':
                    # todo: detect sync / async
                    async def f(self, *args, **kwargs): print('fake', attr); return {}
                    f.__name__ = f"{attr}_stub"
                    setattr(cls, attr, f)
                    print('patched', attr, 'with', f)
                    cls.__abstractmethods__ = cls.__abstractmethods__ - {attr}
                case _:
                    print('unk return type', ret._name)
    return cls

class MySensor(Sensor):
    MODEL = "viam-labs:lowcode:sensor"

MySensor = stubme(MySensor)

class MyMotor(Motor):
    MODEL = "viam-labs:lowcode:motor"

# 2024-04-08T04:23:18.103Z   error robot_server.rdk:component:sensor/sensor   resource/graph_node.go:230   resource build error: rpc error: code = Unknown desc = TypeError - Can't instantiate abstract class MySensor with abstract method get_readings - file_name='/home/awinter/demo/1liner/viam_wrap.py' func_name='dynamic_new' line_num=45   resource rdk:component:sensor/sensor   model viam-labs:lowcode:sensor
