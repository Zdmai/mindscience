sponge.function.calc_distance_nopbc
=============================================

.. py:function:: sponge.function.calc_distance_nopbc(position_a: Tensor, position_b: Tensor, keepdims: bool = False)

    在没有周期性边界条件的情况下计算位置A和B之间的距离，用绝对坐标计算。

    参数：
        - **position_a** (Tensor) - 位置A的坐标，shape为 :math:`(..., D)` ，D是模拟系统的空间维度, 一般为3。
        - **position_b** (Tensor) - 位置B的坐标，shape为 :math:`(..., D)` 。
        - **keepdims** (bool) - 默认值： ``False`` 。

    返回：
        Tensor。A和B之间的距离。shape为 :math:`(..., 1)` 。
