import importlib

import celery

from .celery import app
from . import base


def class_import(cls_path):
    module_path, _, cls_name = cls_path.rpartition('.')
    path_module = importlib.import_module(module_path)
    cls = getattr(path_module, cls_name)
    return cls


@app.task
def run_probe(cls_path, address, port, timeout, count, threads, **kwargs):
    cls = class_import(cls_path)
    if issubclass(cls, base.Probe):
        cls(address, port, timeout, count, threads, **kwargs).test()
    else:
        raise RuntimeError(f'Called class `{cls_path}` which is not subclassed from `base.Probe`')


def execute(cls_path, addresses, ports, timeout, count, threads, **kwargs):
    celery.group(
        run_probe.si(
            cls_path, address, port, timeout, count, threads, **kwargs
        ) for address in addresses for port in ports
    )()
