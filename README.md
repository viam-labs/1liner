# 1-liner POC

Example of a low-boilerplate python module.

## contents

- wrapper.py: standard wrapper that can start a low-code module
- mymodel.py: example of a low-code module (version 1). this uses a class
- classless.py: example of a low-code module (version 2). this only requires a single function and is the shortest approach

## todo

- [ ] does this work with pyinstaller? 1) can we pre-set the class(es), 2) will it detect the runtime imports
- [x] accept multiple models
- [x] if no class, use all Model subclasses from imported module
- [ ] dynamic meta.json?

## design decisions

- is classless mode valuable? or too confusing. it's shorter
- how does this integrate with sdk, what is the ideal way to run it? (module entrypoints are shell strings in meta.json but binaries in local modules)
    - maybe dump wrapper.py into `viam.module.wrap` and can do `python -m viam.module.wrap mymodel.py sock`
    - and maybe register a python entrypoint `viam_wrap` for convenience
- how does this work with rdk? specifically, how does shebang find virtualenv
    - for local modules: set cwd, allow shell command (with args), do `venv/bin/python viam.module_wrapper mymodel.py (sock)`
    - or even better: viam sdk exports executable `viam_module`, command is `venv/bin/viam_module mymodel.py (sock)`
    - for registry modules -- is entrypoint a shell now? I think maybe yes
    - also how will registry modules install deps? --venv param to wrapper.py?
    - or make rdk virtualenv aware and life gets a million times easier for py modules
    - could make shebang `#!venv/bin/python viam.module.wrap` but rdk would need to set up virtualenv anyway
    - generic way: one-time install command (set up venv), then path augmentation before start (prepend ./venv/bin)
- anything special to do with requirements.txt? imo no
