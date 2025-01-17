sponge.potential.EnergyCell
===============================

.. py:class:: sponge.potential.EnergyCell(name: str = 'energy', length_unit: str = 'nm', energy_unit: str = 'kj/mol', use_pbc: bool = None, **kwargs)

    能量项的基础类。 `EnergyCell` 通常被用作传统力场中单独的能量项的一个基类。力场参数通常有单位，因此作为能量项的 `EnergyCell` 的单位必须与力场参数的单位保持一致，而不是与全局单位相同。

    .. note::
        - **B** - 批处理大小，用于模拟的walkers数目。

    参数：
        - **name** (str) - 能量的名称。默认值： ``"energy"`` 。
        - **length_unit** (str) - 长度单位。如果是None的话，与全局长度单位保持一致。默认值： ``"nm"`` 。
        - **energy_unit** (str) - 能量单位。如果是None的话，与全局能量单位保持一致。默认值： ``"kj/mol"`` 。
        - **use_pbc** (bool) - 是否使用周期性边界条件。默认值： ``None``。
        - **kwargs** (dict) - 其他参数字典。

    返回：
        Tensor。能量，shape为 :math:`(B, 1)` ，数据类型为float。
        

    .. py:method:: check_system(system: Molecule)
        :property:

        检查系统是否需要计算这个能量形式。

        参数：
            - **system** (Molecule) - 系统。

    .. py:method:: convert_energy_from(unit: str)

        将能量数值从外部单位换算到内部单位。

        参数：
            - **unit** (str) - 能量的单位。

        返回：
            float，从外部单位换算到内部单位的能量数值。

    .. py:method:: convert_energy_to(unit: str)

        将能量数值从内部单位换算到外部单位。

        参数：
            - **unit** (str) - 能量的单位。

        返回：
            float，从内部单位换算到外部单位的能量数值。

    .. py:method:: energy_unit()
        :property:

        能量单位。

        返回：
            str，能量单位。

    .. py:method:: length_unit()
        :property:

        长度单位。

        返回：
            str，长度单位。

    .. py:method:: name()
        :property:
        
        能量的名称。

        返回：
            str，能量的名称。

    .. py:method:: set_cutoff(cutoff: float, unit: str=None)

        设置截断距离。

        参数：
            - **cutoff** (float) - 截断距离。
            - **unit** (str) - 长度单位。默认值： ``None``。

    .. py:method:: set_input_unit(length_unit: Union[str, Units, Length])

        设置输入坐标的长度单位。

        参数：
            - **length_unit** (Union[str, Units, Length]) - 输入坐标的长度单位。

    .. py:method:: set_pbc(use_pbc: bool)

        设置是否使用周期性边界条件。

        参数：
            - **use_pbc** (bool) - 是否使用周期性边界条件。

    .. py:method:: set_units(length_unit: str=None, energy_unit: str=None, units: Units=None)

        设置长度、能量单位。

        参数：
            - **length_unit** (str) - 长度单位。默认值： ``None`` 。
            - **energy_unit** (str) - 能量单位。默认值： ``None`` 。
            - **units** (Units) - 单位。默认值： ``None`` 。

    .. py:method:: use_pbc()
        :property:

        判断是否使用周期性边界条件。

        返回：
            bool，返回一个标志来判断是否使用了周期性边界条件。
