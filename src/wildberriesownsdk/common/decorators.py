import functools
import time
from typing import Any, Union, Callable


def retry(target_value: Any, tries: int = 1, delay: int = 1) -> Any:
    def func_exc(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_value = None
            for i in range(tries):
                last_value = func(*args, **kwargs)
                if target_value == last_value:
                    break

                if i + 1 < tries:
                    time.sleep(delay)

            return last_value

        return wrapper

    return func_exc


def request_per_seconds(seconds: Union[int, float] = 1) -> Any:
    def func_exc(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            returned_value = func(*args, **kwargs)

            elapsed_seconds = time.time() - start_time
            sleep_time = seconds - round(elapsed_seconds, 2)
            if sleep_time > 0:
                time.sleep(sleep_time)

            return returned_value

        return wrapper

    return func_exc
