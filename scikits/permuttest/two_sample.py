import numpy as np

TINY = 1e-100


def design_matrix(n, n1, confounds):
    """
    First column: 1st group indicator function
    Second column: baseline
    Further columns: confounds
    """
    if confounds == None:
        confounds = []
    X = np.zeros((n, 2 + len(confounds)))
    X[0:n1, 0] = 1
    X[:, 1] = 1
    for i in range(len(confounds)):
        X[:, i + 2] = confounds[i]
    return X


def t_stat(Y, n1, confounds=None):
    """
    Assume that Y.ndim == 2
    """
    n = Y.shape[0]
    X = design_matrix(n, n1, confounds)
    invXtX = np.linalg.inv(np.dot(X.T, X))
    pinvX = np.dot(invXtX, X.T)  # pseudo-inverse
    beta = np.dot(pinvX, Y)
    res = Y - np.dot(X, beta)
    s2 = np.sum(res ** 2, 0) / (n - X.shape[1])
    return beta[0] / np.maximum(np.sqrt(s2 * invXtX[0, 0]), TINY)


def t_square(Y, n1, confounds=None):
    return t_stat(Y, n1, confounds) ** 2


def hotelling_t_square(Y, n1, confounds=None):
    """
    Use Cholesky decomposition to invert the variance matrix
    """
    n = Y.shape[0]
    X = design_matrix(n, n1, confounds)
    invXtX = np.linalg.inv(np.dot(X.T, X))
    pinvX = np.dot(invXtX, X.T)  # pseudo-inverse
    T2 = np.zeros(Y.shape[1])
    factor = 1 / invXtX[0, 0]
    for i in range(Y.shape[1]):
        y = Y[:, i, :]
        beta = np.dot(pinvX, y)
        res = y - np.dot(X, beta)
        V = np.dot(res.T, res) / (n - X.shape[1])
        x = np.linalg.solve(V, beta[0, :])
        T2[i] = factor * np.dot(beta[0, :], x)

    return T2


def permutation_test(Y1, Y2, permutations=1000, confounds=None,
                     two_sided=True):
    """
    Each input array should be of shape (subjects, regions, contrasts).
    """
    Y = np.concatenate((Y1, Y2))
    univ_stat = (t_stat, t_square)
    if Y.ndim == 2:
        stat = univ_stat[two_sided]
    elif Y.ndim == 3:
        if Y.shape[2] == 1:
            Y = Y.reshape(Y.shape[0:2])
            stat = univ_stat[two_sided]
        else:
            stat = hotelling_t_square
    else:
        raise ValueError('Weird input array')
    n1 = Y1.shape[0]
    t = np.reshape(stat(Y, n1, confounds), (1, Y1.shape[1]))
    n = Y.shape[0]
    # generate random permutations
    T = np.zeros((permutations, Y.shape[1]))
    for i in range(permutations):
        permut = np.random.permutation(n)
        Yp = Y[permut, ...]
        confounds_p = None
        if not confounds == None:
            confounds_p = tuple([c[permut] for c in confounds])
        T[i, :] = stat(Yp, n1, confounds_p)
    # uncorrected p-values
    pu = np.sum(T >= t, 0) / float(permutations)
    # p-values corrected for the family-wise error rate
    Tmax = T.max(1)
    p = np.sum(Tmax >= t.T, 1) / float(permutations)
    return t, T, pu, p
