"""Top-level package for the RUGS.FUN trading bot."""
from importlib import import_module
from pkgutil import extend_path

# Allow importing submodules from the internal implementation package
__path__ = extend_path(__path__, __name__)


def __getattr__(name):
    return getattr(import_module('rugsbot.rugsbot'), name)
