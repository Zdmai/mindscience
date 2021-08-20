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
# ============================================================================
'''pme reciprocal force'''
from mindspore import numpy as np

from .common import get_full_tensor
from .pme_common import get_pme_kxyz, PME_Atom_Near, PME_Q_Spread, to_tensor, \
PERIODIC_FACTOR_INVERSE, PME_Ma, PME_Mb, PME_Mc, PME_Md, fft3d, ifft3d


MAXINT = 1073741824
PME_dMa = np.array([0.5, -1.5, 1.5, -0.5], np.float32)
PME_dMb = np.array([0, 1, -2, 1], np.float32)
PME_dMc = np.array([0, 0.5, 0, -0.5], np.float32)


def pme_final(pme_atom_near, charge, pme_Q, pme_frxyz, pme_kxyz, pme_inverse_box_vector, atom_numbers):
    '''pme final'''
    dQf = -pme_Q[pme_atom_near] * np.expand_dims(charge, -1)     # N * 64

    fxyz = np.expand_dims(pme_frxyz, -2)
    fxyz_2 = fxyz ** 2

    # N * 64 * 3
    pme_kxyz = pme_kxyz.astype(np.int32)
    xyz = (PME_Ma[pme_kxyz] * fxyz * fxyz_2 + PME_Mb[pme_kxyz] * fxyz_2 +
           PME_Mc[pme_kxyz] * fxyz + PME_Md[pme_kxyz])
    dxyz = PME_dMa[pme_kxyz] * fxyz_2 + PME_dMb[pme_kxyz] * fxyz + PME_dMc[pme_kxyz]
    Qxyz = dxyz * pme_inverse_box_vector

    x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]
    Qx, Qy, Qz = Qxyz[..., 0], Qxyz[..., 1], Qxyz[..., 2]

    Qx *= y * z * dQf
    Qy *= x * z * dQf
    Qz *= x * y * dQf

    force = np.stack((Qx, Qy, Qz), axis=-1)
    return np.sum(force, axis=1)


def pme_reciprocal_force(atom_numbers, beta, fftx, ffty, fftz, box_length_0, box_length_1,
                         box_length_2, pme_bc, uint_crd, charge):
    """
    Calculate the reciprocal part of long-range Coulumb force using
    PME(Particle Meshed Ewald) method. Assume the number of atoms is N.

    The detailed calculation formula of PME(Particle Meshed Ewald) method
    can be found in this paper: A Smooth Particle Mesh Ewald Method. DOI:
    10.1063/1.470117.

    Args:
        atom_numbers (int): the number of atoms, N.
        beta (float): the PME beta parameter, determined by the
                       non-bond cutoff value and simulation precision tolerance.
        fftx (int): the number of points for Fourier transform in dimension X.
        ffty (int): the number of points for Fourier transform in dimension Y.
        fftz (int): the number of points for Fourier transform in dimension Z.
        box_length_0 (float): the value of boxlength idx 0
        box_length_1 (float): the value of boxlength idx 1
        box_length_2 (float): the value of boxlength idx 2
        uint_crd (Tensor, uint32): [N, 3], the unsigned int coordinates value of each atom.
        charge (Tensor, float32): [N,], the charge carried by each atom.

    Outputs:
        force (Tensor, float32): [N, 3], the force felt by each atom.

    Supported Platforms:
        ``GPU``
    """
    pme_Nall = fftx * ffty * fftz
    pme_Nin = ffty * fftz
    pme_atom_near = get_full_tensor((atom_numbers, 64), 0, np.int32)
    pme_uxyz = get_full_tensor((atom_numbers, 3), MAXINT, np.uint32)
    pme_kxyz = get_pme_kxyz()
    pme_inverse_box_vector = to_tensor((fftx / box_length_0, ffty / box_length_1, fftz / box_length_2))

    pme_frxyz, pme_uxyz, pme_atom_near = PME_Atom_Near(
        uint_crd, pme_atom_near, pme_Nin, PERIODIC_FACTOR_INVERSE * fftx, PERIODIC_FACTOR_INVERSE * ffty,
        PERIODIC_FACTOR_INVERSE * fftz, atom_numbers, fftx, ffty, fftz, pme_kxyz, pme_uxyz)

    pme_Q = get_full_tensor(pme_Nall, 0, np.float32)
    pme_Q = PME_Q_Spread(pme_atom_near, charge, pme_frxyz, pme_Q, pme_kxyz, atom_numbers)

    pme_Q = pme_Q.reshape(fftx, ffty, fftz)
    pme_bc = pme_bc.reshape(fftx, ffty, fftz // 2 + 1)
    pme_FQ_real, pme_FQ_imag = fft3d(pme_Q)
    pme_FQ_real *= pme_bc
    pme_FQ_imag *= pme_bc
    pme_Q = ifft3d(pme_FQ_real, pme_FQ_imag)
    pme_Q = pme_Q.ravel()

    return pme_final(
        pme_atom_near, charge, pme_Q, pme_frxyz, pme_kxyz, pme_inverse_box_vector, atom_numbers)
