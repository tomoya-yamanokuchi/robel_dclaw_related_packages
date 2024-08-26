import numpy as np


class TaskSpaceDifferentialPositionValue_2D_Plane:
    _min = -0.15
    _max =  0.15
    _dim = 6

    def __init__(self, value: np.ndarray):
        self.value = value
        self.__validation__()

    def __validation__ (self):
        assert len(self.value.shape) == 3
        assert  self.value.shape[-1] == self._dim, print("{} != {}".format(self.value.shape[-1], self._dim))  #(2dim * 3claw)
        self.value = self.value.clip(self._min, self._max)

    def __eq__(self, other: object) -> bool:
        return True if (other.value == self.value).all() else False

    def __add__(self, other: object):
        return TaskSpaceDifferentialPositionValue_2D_Plane(self.value + other.value)

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def dim(self):
        return self._dim


if __name__ == '__main__':
    import numpy as np

    data1 = np.random.rand(1,1,2)*1
    data2 = np.random.rand(1,1,2)*2

    x = TaskSpacePositionValueObject_2D_Plane(data1)
    y = TaskSpacePositionValueObject_2D_Plane(data2)

    print(x.value)
    print(y.value)
    print(x == y)
    print(x.min, x.max)
    print(y.min, y.max)
    z = x + y
    print(z.value)

    print(TaskSpacePositionValueObject_2D_Plane._min)
    print(TaskSpacePositionValueObject_2D_Plane.min)
    import ipdb; ipdb.set_trace()
    # print(y.__min, y.__max)


