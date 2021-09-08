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
"""Provides base Step interface."""

from typing import Any, Dict, List

from okpt.test import profile


class Step:
    """Test step interface.

    Attributes:
        label: Name of the step.
        measures: Metrics that the step should profile.

    Methods:
        execute: Run the step and return a step response with the label and corresponding measures.
    """

    label = 'base_step'
    measures: List[str] = []

    def _action(self):
        """Step logic/behavior to be executed and profiled."""
        pass

    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute step logic while profiling various measures.

        Returns:
            Dict containing step label and various step measures.
        """
        action = self._action
        # profile the action with measure decorators
        for measure in self.measures:
            action = getattr(profile, measure)(action)

        result = action(*args, **kwargs)
        if isinstance(result, dict):
            return {'label': self.label, **result}
        return {'label': self.label}
