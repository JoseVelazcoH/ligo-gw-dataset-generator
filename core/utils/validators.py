from functools import wraps
from typing import (
    Callable,
    Dict,
    Iterable
)

def enforce_arguments(choices: Dict[int | str, Iterable]) -> Callable:
    err_fmt = "Value of '{}' is not a valid choice in {}"

    def decorator(func):
        @wraps(func)
        def decorated_func(*args, **kwargs):
            for arg_index in range(len(args)):
                param_name = func.__code__.co_varnames[arg_index]
                if arg_index in choices and args[arg_index] not in choices[arg_index]:
                    raise ValueError(err_fmt.format(param_name, choices[arg_index]))
                elif param_name in choices and args[arg_index] not in choices[param_name]:
                    raise ValueError(err_fmt.format(param_name, choices[param_name]))
            for param_name in kwargs:
                if param_name in choices and kwargs[param_name] not in choices[param_name]:
                    raise ValueError(err_fmt.format(param_name, choices[param_name]))

            return func(*args, **kwargs)

        return decorated_func

    return decorator
