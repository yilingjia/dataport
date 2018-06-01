import autograd.numpy as np
from autograd import multigrad
from autograd import grad
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors


cases = {
    1: {'HA': 'Ma, Nb -> MNab', 'HAT': 'MNab, Oab -> MNO'},
    2: {'HA': 'Ma, Nab -> MNb', 'HAT': 'MNb, Ob -> MNO'},
    3: {'HA': 'Mab, Na -> MNb', 'HAT': 'MNb, Ob -> MNO'},
    4: {'HA': 'Ma, Na -> MNa', 'HAT': 'MNa, Oa -> MNO'}
}

def multiply_case(H, A, T, case):
    HA = np.einsum(cases[case]['HA'], H, A)
    HAT = np.einsum(cases[case]['HAT'], HA, T)
    return HAT



def cost_abs(H, A, T, E_np_masked, case):
    HAT = multiply_case(H, A, T, case)
    mask = ~np.isnan(E_np_masked)
    # error = (HAT - E_np_masked)[mask].flatten()
    error = (HAT - E_np_masked)[mask].flatten()
    return np.sqrt((error ** 2).mean())


def learn_HAT_adagrad(case, tensor, num_home_factors, num_season_factors, num_iter=2000, lr=0.01, dis=False, random_seed=0, eps=1e-8, A_known=None, T_known=None, cost=cost_abs):
    np.random.seed(random_seed)
    args_num = [0, 1, 2]

    mg = multigrad(cost, argnums=args_num)

    params = {}
    params['M'], params['N'], params['O'] = tensor.shape
    params['a'] = num_home_factors
    params['b'] = num_season_factors
    H_dim_chars = list(cases[case]['HA'].split(",")[0].strip())
    H_dim = tuple(params[x] for x in H_dim_chars)
    A_dim_chars = list(cases[case]['HA'].split(",")[1].split("-")[0].strip())
    A_dim = tuple(params[x] for x in A_dim_chars)
    T_dim_chars = list(cases[case]['HAT'].split(",")[1].split("-")[0].strip())
    T_dim = tuple(params[x] for x in T_dim_chars)

    H = np.random.rand(*H_dim)
    A = np.random.rand(*A_dim)
    T = np.random.rand(*T_dim)

    if A_known is not None:
        A = set_known(A, A_known)
    sum_square_gradients_A = np.zeros_like(A)
    sum_square_gradients_H = np.zeros_like(H)
    sum_square_gradients_T = np.zeros_like(T)

    # GD procedure
    for i in range(num_iter):
        del_h, del_a, del_t = mg(H, A, T, tensor, case)

        sum_square_gradients_A += eps + np.square(del_a)
        lr_a = np.divide(lr, np.sqrt(sum_square_gradients_A))
        A -= lr_a * del_a

        sum_square_gradients_H += eps + np.square(del_h)
        sum_square_gradients_T += eps + np.square(del_t)

        lr_h = np.divide(lr, np.sqrt(sum_square_gradients_H))
        lr_t = np.divide(lr, np.sqrt(sum_square_gradients_T))

        H -= lr_h * del_h
        T -= lr_t * del_t

        if T_known is not None:
            T = set_known(T, T_known)
        if A_known is not None:
            A = set_known(A, A_known)

        # Projection to non-negative space
        H[H < 0] = 1e-8
        A[A < 0] = 1e-8
        T[T < 0] = 1e-8

        if i % 500 == 0:
            if dis:
                print(cost(H, A, T, tensor, case), i)
                # sys.stdout.flush()

    return H, A, T