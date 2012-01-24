import numpy as np
from scikits.permuttest.two_sample import (permutation_test,
                                           t_stat,
                                           hotelling_t_square,
                                           design_matrix,
                                           _hotelling_t_square)





"""
Y = np.random.normal(size=(10, 10000))
t = t_stat(Y, 5)
"""

from scipy.linalg import cho_solve, cho_factor


def test_hotelling_t_square():
    Y = np.random.normal(size=(10, 100, 1))
    t2 = t_stat(Y.squeeze(), 5) ** 2
    T2 = hotelling_t_square(Y, 5)
    return t2, T2

"""
# 10 subjects, 7 regions, 2 contrasts
Y = np.random.normal(size=(10, 100, 2))

# test hotelling stat without confounds
T0 = hotelling_t_square(Y, 5)

# test hotelling stat with confounds
age = np.random.rand(10)
T1 = hotelling_t_square(Y, 5, confounds=(age, ))

# test permutation test
t, T, pu, p = permutation_test(Y[0:5, ...], Y[5:, ...],
                               confounds=(age, ), permutations=10)

"""
