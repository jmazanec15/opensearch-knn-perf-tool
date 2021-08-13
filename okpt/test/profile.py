import time
from typing import Callable, Dict


class Timer():
    def __init__(self):
        self.start_time = time.perf_counter()

    def start(self):
        self.start_time = time.perf_counter()

    def end(self) -> float:
        return (time.perf_counter() - self.start_time) * 1000


def measure(f: Callable[..., Dict]):
    def wrapper(*args, **kwargs):
        timer = Timer()
        timer.start()
        result = f(*args, **kwargs)
        took = timer.end()
        return {**result, 'took': took}

    return wrapper


def label(name: str):
    def label_decorator(f: Callable[..., Dict]):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            return {**result, 'label': name}

        return wrapper

    return label_decorator
