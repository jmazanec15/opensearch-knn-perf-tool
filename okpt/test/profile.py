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
"""Provides decorators to profile functions.

The decorators work by adding a `measureable` (time, memory, etc) field to a
dictionary returned by the wrapped function. So the wrapped functions must
return a dictionary in order to be profiled.
"""
import functools
import time
from typing import Callable, Dict

import psutil


class TimerStoppedWithoutStartingError(Exception):
    """Error raised when Timer is stopped without having been started."""

    def __init__(self):
        super().__init__()
        self.message = 'Timer must call start() before calling end().'


class _Timer():
    """Timer class for timing.

    Methods:
        start: Starts the timer.
        end: Stops the timer and returns the time elapsed since start.

    Raises:
        TimerStoppedWithoutStartingError: Timer must start before ending.
    """

    def __init__(self):
        self.start_time = None

    def start(self):
        """Starts the timer."""
        self.start_time = time.perf_counter()

    def end(self) -> float:
        """Stops the timer.

        Returns:
            The time elapsed in milliseconds.
        """
        # ensure timer has started before ending
        if self.start_time == None:
            raise TimerStoppedWithoutStartingError()

        elapsed = (time.perf_counter() - self.start_time) * 1000
        self.start_time = None
        return elapsed


def took(f: Callable):
    """Profiles a functions execution time.

    Args:
        f: Function to profile.

    Returns:
        A function that wraps the passed in function and adds a time took field
        to the return value.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        """Wrapper function."""
        timer = _Timer()
        timer.start()
        result = f(*args, **kwargs)
        time_took = timer.end()

        # if result already has a `took` field, don't modify the result
        if isinstance(result, dict) and 'took' in result:
            return result
        # `result` may not be a dictionary, so it may not be unpackable
        elif isinstance(result, dict):
            return {**result, 'took': time_took}
        return {'took': time_took}

    return wrapper


def memory(f: Callable[..., Dict]):
    """Profiles a functions memory usage.

    Args:
        f: Function to profile.

    Returns:
        A function that wraps the passed in function and adds a memory field to
        the return value.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        """Wrapper function."""
        svmem = psutil.virtual_memory()
        used_memory_start = svmem.used
        result = f(*args, **kwargs)
        used_memory_end = svmem.used
        return {**result, 'memory': used_memory_end - used_memory_start}

    return wrapper
