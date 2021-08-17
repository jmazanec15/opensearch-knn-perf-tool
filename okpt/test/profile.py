# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
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
