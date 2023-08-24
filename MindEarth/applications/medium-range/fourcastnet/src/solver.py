# Copyright 2023 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""FCNTrainer"""
from mindearth.module import Trainer

from .callback import EvaluateCallBack


class FCNTrainer(Trainer):
    def __init__(self, config, model, loss_fn, logger):
        super(FCNTrainer, self).__init__(config, model, loss_fn, logger)
        self.pred_cb = self._get_callback()

    def _get_callback(self):
        pred_cb = EvaluateCallBack(self.model, self.valid_dataset, self.config, self.logger)
        return pred_cb
