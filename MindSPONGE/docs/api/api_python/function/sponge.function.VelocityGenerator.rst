sponge.function.VelocityGenerator
=====================================

.. py:class:: sponge.function.VelocityGenerator(temperature: float = 300, remove_translation: bool = True, seed: int = 0, seed2: int = 0, length_unit: str = None, energy_unit: str = None)

    根据温度产生系统中原子的速度。

    参数：
        - **temperature** (float) - 温度。默认值： ``300.0`` 。
        - **remove_translation** (bool) - 是否在基于周期性边界条件的情况下计算距离。默认值： ``True`` 。
        - **seed** (int) - 标准常态下的随机种子。默认值： ``0`` 。
        - **seed2** (int) - 标准常态下的随机种子2。默认值： ``0`` 。
        - **length_unit** (str) - 长度单位。默认值： ``None`` 。
        - **energy_unit** (str) - 能量单位。默认值： ``None`` 。

    .. py:method:: set_temperature(temperature: float)

        设定温度。

        参数：
            - **temperature** (float) - 温度值。
