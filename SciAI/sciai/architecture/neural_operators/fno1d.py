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
# ==============================================================================
"""FNO1d"""
import mindspore as ms
from mindspore import ops, nn, Tensor

from sciai.architecture.neural_operators.dft import SpectralConv1dDft
from sciai.utils.check_utils import _check_type
from sciai.utils.math_utils import _get_grid_1d


class FNOBlock(nn.Cell):
    def __init__(self, in_channels, out_channels, modes1, resolution=1024, gelu=True, dtype=ms.float32):
        super().__init__()
        self.conv = SpectralConv1dDft(in_channels, out_channels, modes1, resolution, dtype=dtype)
        self.w = nn.Conv1d(in_channels, out_channels, 1).to_float(dtype)
        self.act = ops.GeLU() if gelu else ops.Identity()

    def construct(self, x):
        return self.act(self.conv(x) + self.w(x)) + x


class FNO1D(nn.Cell):
    r"""
    The 1-dimensional Fourier Neural Operator (FNO1D) contains a lifting layer,
    multiple Fourier layers and a decoder layer.
    The details can be found in `Fourier neural operator for
    parametric partial differential equations <https://arxiv.org/pdf/2010.08895.pdf>`_.

    Args:
        in_channels (int): The number of channels in the input space.
        out_channels (int): The number of channels in the output space.
        resolution (int): The spatial resolution of the input.
        modes (int): The number of low-frequency components to keep.
        channels (int): The number of channels after dimension lifting of the input. Default: 20.
        depths (int): The number of FNO layers. Default: 4.
        mlp_ratio (int): The number of channels lifting ratio of the decoder layer. Default: 4.
        dtype (dtype.Number): The computation type of dense. It should be `ms.float16` or `ms.float32`.
            `ms.float32` is recommended for the GPU backend, and `ms.float16` is recommended for the Ascend backend.
            Default: `ms.float32`.

    Inputs:
        - **x** (Tensor) - Tensor of shape :math:`(batch\_size, resolution, in\_channels)`.

    Outputs:
        Tensor, the output of FNO network.

        - **output** (Tensor) -Tensor of shape :math:`(batch\_size, resolution, out\_channels)`.

    Raises:
        TypeError: If `in_channels` is not an int.
        TypeError: If `out_channels` is not an int.
        TypeError: If `resolution` is not an int.
        TypeError: If `modes` is not an int.
        ValueError: If `modes` is less than 1.

    Supported Platforms:
        ``Ascend`` ``GPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore.common.initializer import initializer, Normal
        >>> from sciai.architecture.neural_operators import FNO1D
        >>> B, W, C = 32, 1024, 1
        >>> x = initializer(Normal(), [B, W, C])
        >>> net = FNO1D(in_channels=1, out_channels=1, resolution=64, modes=12)
        >>> output = net(x)
        >>> print(output.shape)
        (32, 1024, 1)

    """

    def __init__(self,
                 in_channels,
                 out_channels,
                 resolution,
                 modes,
                 channels=20,
                 depths=4,
                 mlp_ratio=4,
                 dtype=ms.float32):
        super().__init__()
        _check_type(in_channels, "in_channels", target_type=int, exclude_type=bool)
        _check_type(out_channels, "out_channels", target_type=int, exclude_type=bool)
        _check_type(resolution, "resolution", target_type=int, exclude_type=bool)
        _check_type(modes, "modes", target_type=int, exclude_type=bool)
        if modes < 1:
            raise ValueError(
                "modes must at least 1, but got mode: {}".format(modes))
        self.modes1 = modes
        self.channels = channels
        self.fc_channel = mlp_ratio * channels
        self.fc0 = nn.Dense(in_channels + 1, self.channels).to_float(dtype)
        self.layers = depths

        self.fno_seq = nn.SequentialCell()
        for _ in range(self.layers - 1):
            self.fno_seq.append(
                FNOBlock(self.channels, self.channels, modes1=self.modes1, resolution=resolution, dtype=dtype))
        self.fno_seq.append(
            FNOBlock(self.channels, self.channels, self.modes1, resolution=resolution, gelu=False, dtype=dtype))

        self.fc1 = nn.Dense(self.channels, self.fc_channel).to_float(dtype)
        self.fc2 = nn.Dense(self.fc_channel, out_channels).to_float(dtype)

        self.grid = Tensor(_get_grid_1d(resolution), dtype=ms.float32)
        self.concat = ops.Concat(axis=-1)
        self.transpose = ops.Transpose()
        self.act = ops.GeLU()

    def construct(self, x: Tensor):
        """construct"""
        batch_size = x.shape[0]

        grid = self.grid.repeat(batch_size, axis=0)
        x = self.concat((x, grid))
        x = self.fc0(x)
        x = self.transpose(x, (0, 2, 1))

        x = self.fno_seq(x)

        x = self.transpose(x, (0, 2, 1))
        x = self.fc1(x)
        x = self.act(x)
        x = self.fc2(x)
        return x
