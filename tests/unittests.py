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

# 10 subjects, 7 regions, 2 contrasts
Y = np.random.normal(size=(10, 100, 2))

n = Y.shape[0]
n1 = 5
age = np.random.rand(10)
X = design_matrix(n, n1, confounds=(age,))
invXtX = np.linalg.inv(np.dot(X.T, X))
pinvX = np.dot(invXtX, X.T)  # pseudo-inverse
T2 = np.zeros(Y.shape[1])
factor = 1 / invXtX[0, 0]
for i in range(Y.shape[1]):
    y = Y[:, i, :]
    beta = np.dot(pinvX, y)
    res = y - np.dot(X, beta)
    V = np.dot(res.T, res) / (n - X.shape[1])
    L, lower = cho_factor(V)  # V = L L.T
    x = cho_solve((L, lower), beta[0, :])
    T2[i] = factor * np.sum(x ** 2)



"""
# test hotelling stat without confounds
T0 = hotelling_t_square(Y, 5)

# test hotelling stat with confounds
age = np.random.rand(10)
T1 = hotelling_t_square(Y, 5, confounds=(age, ))

# test permutation test
t, T, pu, p = permutation_test(Y[0:5, ...], Y[5:, ...],
                               confounds=(age, ), permutations=10)

"""
