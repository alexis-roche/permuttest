import numpy as np
from scikits.permuttest.two_sample import (permutation_test,
                                           hotelling_t_square,
                                           _hotelling_t_square)


# 10 subjects, 7 regions, 2 contrasts
Y = np.random.normal(size=(10, 7, 2))

# test hotelling stat without confounds
T = hotelling_t_square(Y, 5)

# test hotelling stat with confounds
age = np.random.rand(10)
T1 = hotelling_t_square(Y, 5, confounds=(age, ))

# test permutation test 
t, T, pu, p = permutation_test(Y[0:5, ...], Y[5:, ...],
                               confounds=(age, ), permutations=10)
