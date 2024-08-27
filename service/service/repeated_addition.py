import numpy as np


def repeated_addition(x, addition, num_repeat):
    return x + np.arange(1, num_repeat+1) * addition


if __name__ == '__main__':
    # 使用例
    x_initial = 1.0
    a         = 0.5
    n         = 5
    output    = repeated_addition(x_initial, a, n)
    print(output) # --> [1.5 2.  2.5 3.  3.5]
