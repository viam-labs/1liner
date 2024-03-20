# 1-liner POC

Example of a low-boilerplate python module.

## contents

- wrapper.py: standard wrapper that can start a low-code module
- mymodel.py: example of a low-code module (version 1). this uses a class
- classless.py: example of a low-code module (version 2). this only requires a single function and is the shortest approach

## todo

- [ ] does this work with pyinstaller? 1) can we pre-set the class(es), 2) will it detect the runtime imports
- [ ] accept multiple models
- [ ] if no class, use all Model subclasses from imported module
- [ ] dynamic meta.json?
