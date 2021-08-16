import time
from typing import Callable, Dict

import psutil


class Timer():
    def __init__(self):
        self.start_time = time.perf_counter()

    def start(self):
        self.start_time = time.perf_counter()

    def end(self) -> float:
        return (time.perf_counter() - self.start_time) * 1000


def memory(f: Callable[..., Dict]):
    def wrapper(*args, **kwargs):
        svmem = psutil.virtual_memory()
        used_memory_start = svmem.used
        result = f(*args, **kwargs)
        used_memory_end = svmem.used
        return {**result, 'memory': used_memory_end - used_memory_start}

    return wrapper


def took(f: Callable[..., Dict]):
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
