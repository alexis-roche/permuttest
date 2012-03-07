import numpy as np
from scikits.permuttest.two_sample import (permutation_test,
                                           t_stat,
                                           hotelling_t_square,
                                           design_matrix)





"""
Y = np.random.normal(size=(10, 10000))
t = t_stat(Y, 5)
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
                               confounds=(age, ), permutations=100)

t, T, pu, p = permutation_test(Y[0:5, :, 0] + 2, Y[5:, :, 0],
                               confounds=(age, ), permutations=100)

#t, T, pu, p = permutation_test(Y[0:5, :, 0] + 2, Y[5:, :, 0], permutations=100)
