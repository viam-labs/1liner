# viam-wrap

This is a python package providing `viam-wrap`, a command for running low-boilerplate python modules. It takes over entrypoint and registration logic.

Install in a fresh virtualenv with:

```sh
pip install git+https://github.com/viam-labs/1liner
```

Check out an example at [mymodel.py](examples/mymodel.py), but it's basically:

```python
#!/usr/bin/env viam-wrap
from viam.components.sensor import Sensor

class Model(Sensor):
    MODEL = "viam-labs:lowcode:sensor"

    async def get_readings(self, **kwargs):
        return {"success?": True}
```

Note the shebang calling `viam-wrap`. You can execute `./mymodel.py sock-path` in a suitable virtualenv, and it will call the viam-wrap command with your module. A less magical way to do that is `viam-wrap ./mymodel.py sock-path`.

There's also a [pyinstaller example](examples/installable.py) to bundle these for distribution.

## defaults

(todo: describe `new()` and `reconfigure` defaults)

## todo

- [x] does this work with pyinstaller? 1) can we pre-set the class(es), 2) will it detect the runtime imports
- [x] accept multiple models
- [x] if no class, use all Model subclasses from imported module
- [ ] dynamic meta.json?

## dev instructions

To build for distribution:

```sh
pip install build # if you haven't
python -m build --sdist --wheel
```
