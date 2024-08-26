# import numpy as np
import random

# mass_candidates = [
#     0.01,
#     0.04,
#     0.1,
#     0.2,
# ]


mass_candidates = [
    0.05,
    0.08,
    0.3,
    0.6,
]


def random_mass_sampling():
    # サンプルする数（K）
    K = 4

    # 重複を許容してサンプルする
    sampled_values = [random.choice(mass_candidates) for _ in range(K)]

    print(f"\n mass sampled_values = {sampled_values} \n")

    return sampled_values

if __name__ == '__main__':
    random_mass_sampling()
    random_mass_sampling()
    random_mass_sampling()
