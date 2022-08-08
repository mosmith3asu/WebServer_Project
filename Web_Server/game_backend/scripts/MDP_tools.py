from Web_Server.game_backend.game_data.settings import REWARDS,ACTIONS,MDP_file_path
from  Web_Server.game_backend.game_data.worlds import WORLDS
import numpy as np
from math import dist
from collections import namedtuple


def main():
    iworld = 1
    MDP = MDP_DataClass(iworld)

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class MDP_DataClass(object):
    """
    NORMALIZE TRANSITION PROBS
    """
    def __init__(self, iworld, init_penalties=True,MDP_path=None):
        self.iworld = iworld
        self.P_pen = REWARDS['player_Ppenalty']
        self.R_pen = REWARDS['player_Rpenalty']
        self.start = WORLDS[iworld]['start']
        S, A, T, R_player, R_evader = load_MDP() if MDP_path is None else load_MDP(MDP_path)


        # Agent Space #######################
        agent_space = {}
        agent_space['S'] = get_adm_agent_states()
        agent_space['A'] = ACTIONS['list']
        agent_space['nS'] = np.shape(agent_space['S'])[0]
        agent_space['nA'] = np.shape(agent_space['A'])[0]
        agent_space['T'] = None
        agent_space['R_player'] = R_player
        agent_space['R_evader'] = R_evader
        self.agent = Struct(**agent_space)

        # Joint Space #######################

        nS = np.shape(S)[0]  # joint states
        nA = np.shape(A)[0]
        if init_penalties: R_player, Si_pen = penalty_init(iworld, S, R_player, self.P_pen, self.R_pen)
        else: self.Si_pen = None
        Si_terminal = np.array([is_caught(S[si]) for si in range(nS)]).T

        joint_space = {}
        joint_space['S'] = S
        joint_space['A'] = A
        joint_space['T'] = T
        joint_space['nS'] = nS
        joint_space['nA'] = nA
        joint_space['R_player'] = R_player
        joint_space['R_evader'] = R_evader
        joint_space['Si_terminal'] = Si_terminal

        self.joint = Struct(**joint_space)

        # self.S, self.A, self.T, self.R_player, self.R_evader = load_MDP()
        # if init_penalties:
        #     self.R_player, self.Si_pen = penalty_init(iworld, self.S, self.R_player, self.P_pen, self.R_pen)
        # else:
        #     self.Si_pen = None
        # self.Si_terminal = np.array([is_caught(self.S[si]) for si in range(self.nS)]).T
        # self.nS = np.shape(self.S)[0] # joint states
        # self.nAgents = 3
        # self.nA = np.shape(self.A)[0]
        # self.n_actions = 5 # single agent actions

#########################################################################
####### FUNCIONS+UTILS ##################################################

def penalty_init(iworld,S,R_player,P_pen,R_pen,nAgents=3):
    is_centralized = np.shape(R_player)[0]>1

    nS = np.shape(R_player)[0]
    world = WORLDS[iworld]['array']
    pen_states = np.array(np.where(world == WORLDS['pen_val'])).T
    Si_pen = np.zeros([nS,nAgents])
    for pen_state in pen_states:
        for player in [0,1]:
            i_pen_states = np.where(np.all(S[:, player,:] == pen_state,axis=1))
            Si_pen[i_pen_states,player]=1
            if is_centralized: R_player[i_pen_states,player] += P_pen*R_pen
            if player==0: R_player[i_pen_states] += P_pen*R_pen
    return R_player,Si_pen

def get_adm_agent_states():
    """
    Gets admissable states of a signle agent
    :return:
    """
    world = WORLDS['empty_world']['array']
    empty_val = WORLDS['empty_val']
    player_states = np.array(np.where(world == empty_val)).T
    return player_states

def are_adjacent(statei,statej):
    adjacent = True
    d1 = dist(statei[0], statej[0])
    d2 = dist(statei[1], statej[1])
    d3 = dist(statei[2], statej[2])
    if  not(d1 == 1 or d1==0): adjacent = False
    if  not(d2 == 1 or d2==0): adjacent = False
    if  not(d3 == 1 or d3==0): adjacent = False
    return adjacent
def contains_border(world,border_val,state):
    has_border = False
    r1,c1 = state[0]
    r2, c2 = state[1]
    r3, c3 = state[2]
    if world[r1, c1] == border_val: has_border =True
    if world[r2, c2] == border_val: has_border = True
    if world[r3, c3] == border_val: has_border = True
    return has_border
def is_caught(state):
    caught = True
    d1 = dist(state[0], state[2]) # p1 to evader
    d2 = dist(state[1], state[2]) # p2 to evader
    if  not(d1 == 1 or d1==0): caught = False
    if  not(d2 == 1 or d2==0): caught = False
    return caught
def evader_Rdist(state):
    scale = REWARDS['evader_scale_Rdist']
    d_max = dist([1,1], [5,5])
    r_max = pow(d_max, 2) + pow(d_max, 2)
    # r_max = 64 # maximum distance across board
    d1 = dist(state[0], state[2])  # p1 to evader
    d2 = dist(state[1], state[2])  # p2 to evader
    return scale*(pow(d1,2) + pow(d2,2))/r_max

def player1_Rdist(state):
    scale = REWARDS['player_scale_Rdist']
    d_max = dist([1,1],[5,5])
    r_max = (d_max-dist([1,1],[1,1]))
    d1 = dist(state[0], state[2])  # p1 to evader
    # return scale*(d1)/r_max
    return scale * (d_max-d1)/r_max


#########################################################################
####### DATA MANAGEMENT #################################################
def save_MDP(file_name, S, A,T,R_player,R_evader,REWARDS):
    np.savez_compressed(file_name, S=S, A=A,T=T,R_player=R_player,R_evader=R_evader,REWARDS=REWARDS)
    # with open('MDP/States.pkl', 'wb') as handle:
    #     pickle.dump(S, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open('MDP\\States.pkl', 'wb') as handle:
    #     pickle.dump(S, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open('MDP\\Actions.pkl', 'wb') as handle:
    #     pickle.dump(S, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open('MDP\\Trans.pkl', 'wb') as handle:
    #     pickle.dump(T, handle, protocol=pickle.HIGHEST_PROTOCOL)
def load_MDP(file_name=MDP_file_path):
    # try: loaded = np.load(file_name + '.npz')
    # except: loaded = np.load('MDP/'+file_name + '.npz')

    loaded = np.load(file_name + '.npz')
    return loaded['S'],loaded['A'],loaded['T'],loaded['R_player'],loaded['R_evader']


if __name__ == "__main__":
    main()
