import importlib, pkgutil, os
SPEC = {}
for f in sorted(os.listdir(os.path.dirname(os.path.abspath(__file__)))):
    if f.startswith('spec2_') and f.endswith('.py'):
        SPEC.update(importlib.import_module(f[:-3]).S)
