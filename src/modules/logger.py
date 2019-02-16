import logging
import json
from functools import wraps
from sys import stdout

from .types import Dict, Any
from .settings import logger_settings

PRIVET_ARGS = {'password'}


def debug_wrapper(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        logging.debug(
            f'Function {func.__name__} called with ' +
            f'args: [ {stringify_args(func, args)} ] ' +
            f'and kwargs: [ {stringify_kwargs(kwargs)} ]'
        )
        returning_value = func(*args, **kwargs)
        logging.debug(
            f'Function {func.__name__} return {returning_value}'
        )
        return returning_value

    return wrap


def stringify_kwargs(kwargs: Dict[str, Any]) -> str:
    return ', '.join(f'{key}={value}' for key, value in kwargs.items() if key not in PRIVET_ARGS)


def stringify_args(func, args: tuple) -> str:
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]

    pairs = dict(zip(arg_names, args))

    return stringify_kwargs(pairs)


def stringify_object(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)


logging.basicConfig(
    **logger_settings,
    stream=stdout
)
