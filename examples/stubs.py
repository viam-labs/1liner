#!/usr/bin/env viam-wrap
# #!/usr/bin/env python3
# stubs.py -- experiment with default implementations of missing functions
from viam.components.sensor import Sensor
from viam.components.motor import Motor

def create_stub_fn(name, orig, ret_value, is_async=False):
    # careful; ret_value is mutable; probably fine given grpc?
    if is_async:
        async def f(self, *args, **kwargs):
            print('fake', name)
            return ret_value
    else:
        def f(self, *args, **kwargs):
            print('fake', name)
    f.__name__ = f'{name}_stub'
    return f

def stubme(cls):
    import typing, inspect
    for attr in cls.__abstractmethods__:
        val = getattr(cls, attr)
        is_async = inspect.iscoroutinefunction(val)
        hints = typing.get_type_hints(val)
        if (ret := hints.get('return')):
            match ret._name:
                case 'Mapping':
                    f = create_stub_fn(attr, val, {}, is_async)
                    setattr(cls, attr, f)
                    print('patched', attr, 'with', f)
                    cls.__abstractmethods__ = cls.__abstractmethods__ - {attr}
                case _:
                    print('unk return type', ret._name)
    return cls

@stubme
class MySensor(Sensor):
    MODEL = "viam-labs:lowcode:sensor"

class MyMotor(Motor):
    MODEL = "viam-labs:lowcode:motor"

# 2024-04-08T04:23:18.103Z   error robot_server.rdk:component:sensor/sensor   resource/graph_node.go:230   resource build error: rpc error: code = Unknown desc = TypeError - Can't instantiate abstract class MySensor with abstract method get_readings - file_name='/home/awinter/demo/1liner/viam_wrap.py' func_name='dynamic_new' line_num=45   resource rdk:component:sensor/sensor   model viam-labs:lowcode:sensor
