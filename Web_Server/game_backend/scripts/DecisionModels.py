import numpy as np
# import matplotlib.pyplot as plt



def NR_decision(V, rationality, choose=False, admissable=None):
    nActions = np.size(V)
    pd = np.zeros(np.shape(V))
    if admissable is None: admissable = np.arange(nActions)
    iadm = admissable
    Vadm = np.copy(V[iadm])
    pd[iadm] = np.exp(rationality * Vadm) / np.sum(np.exp(rationality * Vadm))
    if choose: return np.random.choice(np.arange(len(pd)), p=pd)
    else: return pd


def CPT(r,T,CPT_params,bounds=(0.2,0.8)):
    """
    Utility weighting -------------
    :param b: reference point (framing effect)
    :param alpha: (r+) exp reward gain [0,1]
    :param beta: (r-) exp reward gain [0,1]
    :param lam: relative importance between r+ and r- [0,inf)
    Probability weighting ------------
    :param gamma: (r+) probability gain [0,1]
    :param delta: (r-) probability gain [0,1]
    Misc -----------------------------
    :param theta: rationality coeff
    """
    ##########################################
    # UNPACK PARAMS ##########################
    # Utility weighting ---------------------
    alpha   = max(min(CPT_params('alpha'), bounds[1]),bounds[0])
    beta    = max(min(CPT_params('beta'), bounds[1]),bounds[0])
    lam     =CPT_params('lam')
    # Probability weighting ------------
    gamma   = max(min(CPT_params('gamma') , bounds[1]),bounds[0])
    delta   = max(min(CPT_params('delta'), bounds[1]),bounds[0])
    # Misc -----------------------------
    theta   =CPT_params('theta')
    b       =CPT_params('b')

    ##########################################
    # GET STATS ##############################
    nS, nA, _ = np.shape(T)
    Ea = np.sum([T[ai, :] * r for ai in range(nA)])

