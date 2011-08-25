import numpy as np
from scipy.linalg import cho_solve, cho_factor


def hotelling_t_square(Y, n1):
    M1 = np.mean(Y[0:n1, ...], 0)
    M2 = np.mean(Y[n1::, ...], 0)
    dM = M1 - M2
    n = Y.shape[0]
    T2 = np.zeros(Y.shape[1])
    for i in range(Y.shape[1]):
        y = Y[:, i, :]
        y -= np.mean(y, 0)
        V = np.dot(y.T, y) / (n - 1)
        L, lower = cho_factor(V)  # V = L L.T
        x = cho_solve((L, lower), dM[i, :])
        T2[i] = n * np.sum(x ** 2)
    return T2


def permutation_test(Y1, Y2, permutations=1000, stat=hotelling_t_square):
    Y = np.concatenate((Y1, Y2))
    n1 = Y1.shape[0]
    t = np.reshape(stat(Y, n1), (1, Y1.shape[1]))
    n = Y.shape[0]
    # generate random permutations
    T = np.zeros((permutations, Y.shape[1]))
    for i in range(permutations):
        Yp = Y[np.random.permutation(n), ...]
        T[i, :] = stat(Yp, n1)
    # uncorrected p-values
    pu = np.sum(T >= t, 0) / float(permutations)
    # p-values corrected for the family-wise error rate
    Tmax = T.max(1)
    p = np.sum(Tmax >= t.T, 1) / float(permutations)
    return t, T, pu, p
