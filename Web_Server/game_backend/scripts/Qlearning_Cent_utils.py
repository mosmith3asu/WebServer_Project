
from Web_Server.game_backend.scripts.MDP_tools import MDP_DataClass,contains_border,Struct
import numpy as np
from scipy.signal import savgol_filter
from Web_Server.game_backend.game_data.worlds import WORLDS


#############################################
####### FILTERS #############################
#############################################
# Setting standard filter requirements.
def move_ave_filter(data,order=3):
    if np.size(data)>=500:
        window = int(np.size(data)/10) +1
        data_new = savgol_filter(data, window, order)
    #     data_new = np.array([np.mean(data[max(0,i-window):i]) for i in range(np.size(data))])
    else:  data_new = data
    return data_new

#
#
# def butter_lowpass(cutoff, fs, order=5):
#     nyq = 0.5 * fs
#     normal_cutoff = cutoff / nyq
#     b, a = butter(order, normal_cutoff, btype='low', analog=False)
#     return b, a
#
# def butter_lowpass_filter(data, cutoff, fs, order=5):
#     b, a = butter_lowpass(cutoff, fs, order=order)
#     y = lfilter(b, a, data)
#     return y


def noisy_rational(V,rationality,choose=False,admissable=None):
    nActions = np.size(V)
    pd = np.zeros(np.shape(V))
    if admissable is None: admissable=np.arange(nActions)
    iadm = admissable
    Vadm = np.copy(V[iadm])
    pd[iadm] = np.exp(rationality*Vadm)/np.sum(np.exp(rationality*Vadm))
    if choose: return np.random.choice(np.arange(len(pd)), p=pd)
    else: return pd

def eps_greedy(V,eps,choose=False,admissable=None):
    if admissable is None: admissable=np.arange(np.size(V))
    pd = np.zeros(np.shape(V))
    i_adm = admissable
    Vadm = np.copy(V[i_adm])
    nadm = np.size(i_adm)

    is_uniform = np.all(Vadm == Vadm[0])
    if is_uniform:
        pd[i_adm] = np.ones(np.shape(Vadm))/nadm

    else: # epsilon greedy -------------------
        p = np.random.random()
        if p<eps: # choose exploration
            imax_not = np.array(np.where(Vadm != np.max(Vadm))).flatten()
            pmax_not = 1 / np.size(imax_not)
            pd[i_adm[imax_not]] = pmax_not
            # ai = np.random.choice(nActions)
        else: # choose equally among best actions
            # imax = np.array(np.where(Vadm == np.max(Vadm))).flatten()
            imax = np.array(np.where(Vadm == np.max(Vadm))).flatten()
            pmax = 1/np.size(imax)
            pd[i_adm[imax]] = pmax

    if np.sum(pd) == 0: raise Exception('ERR zero sum pd')
    if not np.all([np.any(pdi == admissable) for pdi in np.where(pd>0)[0]]): raise Exception('ERR pos prob inadm transitions')
    if choose: return np.random.choice(np.arange(len(pd)), p=pd)
    else: return pd


def switch_P1P2(MDP,si,is_action=False):
    if is_action:
        ai = si
        actioni = np.copy(MDP.joint.A[ai])
        actioni = np.array([actioni[1], actioni[0]])  # switch agent 2 to 1st player
        ai_tmp = np.where(np.all(MDP.joint.A == actioni, axis=(1, 2)))[0][0]
        return ai_tmp
    else:
        statei = np.copy(MDP.joint.S[si])
        statei = np.array([statei[1], statei[0], statei[2]])  # switch agent 2 to 1st player
        si_tmp = np.where(np.all(MDP.joint.S == statei, axis=(1, 2)))[0][0]
        return si_tmp


def initQ_evader(MDP):
    evader = 2
    Q_evd = np.zeros([MDP.joint.nS, MDP.agent.nA])
    for si in range(MDP.joint.nS):
        statei = MDP.joint.S[si]
        print(f'\r\t| prog = {round(100 * si / MDP.joint.nS, 2)}% ', end='')
        for ai, action in enumerate(MDP.agent.A):
            statej = np.copy(statei)
            statej[evader] += action
            if not contains_border(WORLDS['empty_world']['array'], WORLDS['border_val'], statej):
                sj = np.where(np.all(MDP.joint.S == statej, axis=(1, 2)))[0][0]
                Q_evd[si, ai] = MDP.joint.R_evader[sj]

    return Q_evd

# def Q2V(Q):
#     V = np.array([np.shape(Q)[0],1])
#     for

def save_Qfun(file_name, Q,stats):
    np.savez_compressed(file_name, Q=Q,stats=stats)

def load_Qfun(file_name):
    # try: loaded = np.load(file_name + '.npz')
    # except: loaded = np.load('Qlearning/'+file_name + '.npz')
    loaded = np.load(file_name + '.npz',allow_pickle=True)
    return loaded['Q'],loaded['stats']


