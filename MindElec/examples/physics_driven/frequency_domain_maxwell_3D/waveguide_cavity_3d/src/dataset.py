# Copyright 2021 Huawei Technologies Co., Ltd
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
# ==============================================================================
"""
create dataset
"""
import numpy as np

from mindelec.data import Dataset
from mindelec.geometry import Cuboid
from mindelec.geometry import create_config_from_edict

from src.config import maxwell_3d_config, cuboid_sampling_config


def create_train_dataset() -> Dataset:
    """
    Create trainning dataset.
    """
    cuboid_space = Cuboid(name=maxwell_3d_config["geom_name"],
                          coord_min=maxwell_3d_config["coord_min"],
                          coord_max=maxwell_3d_config["coord_max"],
                          sampling_config=create_config_from_edict(cuboid_sampling_config))
    geom_dict = {cuboid_space: ["domain", "BC"]}
    train_dataset = Dataset(geom_dict)
    return train_dataset


def test_data_prepare(config):
    """
    Create test dataset.
    """
    coord_min = config["coord_min"]
    coord_max = config["coord_max"]
    axis_size = config["axis_size"]
    wave_number = config.get("wave_number", 2.0)

    # input
    axis_x = np.linspace(coord_min[0], coord_max[0],
                         num=axis_size, endpoint=True)
    axis_y = np.linspace(coord_min[1], coord_max[1],
                         num=axis_size, endpoint=True)
    mesh_x, mesh_y = np.meshgrid(axis_y, axis_x)
    input_data = np.hstack(
        (mesh_x.flatten()[:, None], mesh_y.flatten()[:, None])).astype(np.float32)

    # label
    label = np.zeros((axis_size, axis_size, 1))
    for i in range(axis_size):
        for j in range(axis_size):
            label[i, j, 0] = np.sin(wave_number * axis_x[j])

    label = label.reshape(-1, 1).astype(np.float32)

    return input_data, label
