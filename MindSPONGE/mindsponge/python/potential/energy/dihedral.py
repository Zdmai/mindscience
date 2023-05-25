# Copyright 2021-2023 @ Shenzhen Bay Laboratory &
#                       Peking University &
#                       Huawei Technologies Co., Ltd
#
# This code is a part of MindSPONGE:
# MindSpore Simulation Package tOwards Next Generation molecular modelling.
#
# MindSPONGE is open-source software based on the AI-framework:
# MindSpore (https://www.mindspore.cn/)
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
"""Torsion energy"""

from typing import Union, List
from numpy import ndarray

import mindspore as ms
from mindspore import Tensor
from mindspore.ops import functional as F
from mindspore import Parameter

from .energy import EnergyCell
from ...colvar import Torsion
from ...function import functions as func
from ...function import get_ms_array, get_arguments


class DihedralEnergy(EnergyCell):
    r"""Energy term of dihedral (torsion) angles.

    Math:

    .. math::

        E_{dihedral}(\omega) = \sum_n \frac{1}{2} V_n [1 - \cos{(n \omega - \gamma_n)}]

    Args:

        index (Union[Tensor, ndarray, List[int]]):
                            Array of the indices of the atoms forming the dihedral angles.
                            The shape of array is `(B, d, 4)`, and the data type is int.

        force_constant (Union[Tensor, ndarray, List[float]]):
                            Array of the harmonic force constant :math:`V_n` for the dihedral angles.
                            The shape of array is `(B, d)`, and the data type is float.

        periodicity (Union[Tensor, ndarray, List[float]]):
                            Array of the periodicity :math:`n` for the dihedral angles.
                            The shape of array is `(B, d)`, and the data type is int.

        phase (Union[Tensor, ndarray, List[float]]):
                            Array of the phase shift :math:`\gamma_n` for the dihedral angles.
                            The shape of array is `(B, d)`, and the data type is float.

        parameters (dict):  Force field parameters. Default: None

        use_pbc (bool):     Whether to use periodic boundary condition.

        length_unit (str):  Length unit. If None is given, it will be assigned with the global length unit.
                            Default: 'nm'

        energy_unit (str):  Energy unit. If None is given, it will be assigned with the global energy unit.
                            Default: 'kj/mol'

        name (str):         Name of the energy. Default: 'dihedral'

    Supported Platforms:

        ``Ascend`` ``GPU``

    Symbols:

        B:  Batchsize, i.e. number of walkers in simulation

        d:  Number of dihedral angles.

        D:  Spatial dimension of the simulation system. Usually is 3.

    """
    def __init__(self,
                 index: Union[Tensor, ndarray, List[int]] = None,
                 force_constant: Union[Tensor, ndarray, List[float]] = None,
                 periodicity: Union[Tensor, ndarray, List[float]] = None,
                 phase: Union[Tensor, ndarray, List[float]] = None,
                 parameters: dict = None,
                 use_pbc: bool = None,
                 length_unit: str = 'nm',
                 energy_unit: str = 'kj/mol',
                 name: str = 'dihedral',
                 **kwargs,
                 ):

        super().__init__(
            name=name,
            use_pbc=use_pbc,
            length_unit=length_unit,
            energy_unit=energy_unit,
        )
        self._kwargs = get_arguments(locals(), kwargs)

        if parameters is not None:
            energy_unit = parameters.get('energy_unit')
            self.units.set_energy_unit(energy_unit)

            index = parameters.get('index')
            force_constant = parameters.get('force_constant')
            periodicity = parameters.get('periodicity')
            phase = parameters.get('phase')

        # (1,d,4)
        index = get_ms_array(index, ms.int32)
        if index.shape[-1] != 4:
            raise ValueError(f'The last dimension of index in DihedralEnergy must be 2 but got: {index.shape[-1]}')
        if index.ndim == 2:
            index = F.expand_dims(index, 0)
        if index.ndim != 3:
            raise ValueError(f'The rank of index must be 2 or 3 but got shape: {index.shape}')
        self.index = Parameter(index, name='dihedral_index', requires_grad=False)

        # (d)
        self.get_torsion = Torsion(atoms=self.index, use_pbc=use_pbc, batched=True)
        # d
        self.num_torsions = self.get_torsion.shape[-1]

        # (1,d)
        force_constant = get_ms_array(force_constant, ms.float32)
        if force_constant.shape[-1] != self.num_torsions:
            raise ValueError(f'The last shape of force_constant ({force_constant.shape[-1]}) must be equal to '
                             f'the num_torsions ({self.num_torsions})!')
        if force_constant.ndim == 1:
            force_constant = F.expand_dims(force_constant, 0)
        if force_constant.ndim > 2:
            raise ValueError('The rank of force_constant cannot be larger than 2!')
        self.force_constant = Parameter(force_constant, name='dihedral_force_constant')

        periodicity = get_ms_array(periodicity, ms.int32)
        if periodicity.shape[-1] != self.num_torsions:
            raise ValueError(f'The last shape of periodicity ({periodicity.shape[-1]}) must be equal to '
                             f'the num_torsions ({self.num_torsions})!')
        if periodicity.ndim == 1:
            periodicity = F.expand_dims(periodicity, 0)
        if periodicity.ndim > 2:
            raise ValueError('The rank of periodicity cannot be larger than 2!')
        self.periodicity = Parameter(periodicity, name='periodicity')

        phase = get_ms_array(phase, ms.float32)
        if phase.shape[-1] != self.num_torsions:
            raise ValueError(f'The last shape of phase ({phase.shape[-1]}) must be equal to '
                             f'the num_torsions ({self.num_torsions})!')
        if phase.ndim == 1:
            phase = F.expand_dims(phase, 0)
        if phase.ndim > 2:
            raise ValueError('The rank of phase cannot be larger than 2!')
        self.dihedral_phase = Parameter(phase, name='phase')

    def set_pbc(self, use_pbc: bool = None):
        self._use_pbc = use_pbc
        self.get_torsion.set_pbc(use_pbc)
        return self

    def construct(self,
                  coordinate: Tensor,
                  neighbour_index: Tensor = None,
                  neighbour_mask: Tensor = None,
                  neighbour_vector: Tensor = None,
                  neighbour_distance: Tensor = None,
                  pbc_box: Tensor = None
                  ):
        r"""Calculate energy term.

        Args:
            coordinate (Tensor):            Tensor of shape (B, A, D). Data type is float.
                                            Position coordinate of atoms in system
            neighbour_index (Tensor):       Tensor of shape (B, A, N). Data type is int.
                                            Index of neighbour atoms.
            neighbour_mask (Tensor):        Tensor of shape (B, A, N). Data type is bool.
                                            Mask for neighbour index.
            neighbour_vector (Tensor):       Tensor of shape (B, A, N). Data type is bool.
                                            Vectors from central atom to neighbouring atoms.
            neighbour_distance (Tensor):    Tensor of shape (B, A, N). Data type is float.
                                            Distance between neighbours atoms.
            inv_neigh_dis (Tensor):         Tensor of shape (B, A, N). Data type is float.
                                            Reciprocal of distances.
            pbc_box (Tensor):               Tensor of shape (B, D). Data type is float.
                                            Tensor of PBC box. Default: None

        Returns:
            energy (Tensor):    Tensor of shape (B, 1). Data type is float.

        Symbols:
            B:  Batchsize, i.e. number of walkers in simulation
            A:  Number of atoms.
            D:  Spatial dimension of the simulation system. Usually is 3.

        """
        # (B,M)
        phi = self.get_torsion(coordinate, pbc_box)

        # (B,M) = (1,M) * (B,M)
        nphi = self.periodicity * phi

        # (B,M)
        cosphi = F.cos(nphi - self.dihedral_phase) + 1

        # (B,M) = (1,M) + (B,M)
        energy = 0.5 * self.force_constant * cosphi

        # (B,1) <- (B,M)
        energy = func.keepdims_sum(energy, -1)

        return energy
