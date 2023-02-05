import importlib
from collections.abc import Iterable


def chain_iterables(iterables: Iterable) -> Iterable:
    for it in iterables:
        for element in it:
            yield element


def deduplicate_iterables(*iterables) -> list:
    return list(dict.fromkeys(chain_iterables(iterables)))


def reload_module(module):
    # this is not recommended
    return importlib.reload(module)
