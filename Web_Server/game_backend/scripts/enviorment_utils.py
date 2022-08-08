from Web_Server.game_backend.game_data.worlds import WORLDS
import numpy as np
from Web_Server.game_backend.scripts.MDP_tools  import is_caught
from Web_Server.game_backend.game_data.settings import *
# import matplotlib.pyplot as plt
import random
random.seed(0)
class Enviorment(object):
    def __init__(self,iworld,MDP):
        self.MDP = MDP
        self.iworld = iworld
        self.start = np.array(WORLDS[iworld]['start'])/100
        self.world = WORLDS[iworld]['array']
        self.si_start = np.where(np.all(self.MDP.joint.S==self.start,axis=(1,2)))[0][0]
        self.round,self.max_rounds = 0,20
        # self.si = self.generateInitialState()
        self.was_caught = 0
        self.init_params = {}
        self.init_params['round'] = self.round
        self.init_params['max_rounds'] = self.max_rounds
        self.init_params['was_caught'] = self.was_caught

        self.si = self.reset()

    def generateInitialState(self,rand_init=True):
        if rand_init:
            bad_start = True
            while bad_start:
                si = random.choice(np.arange(self.MDP.joint.nS))
                bad_start = is_caught(self.MDP.joint.S[si]) #self.is_done(si,is_init=True)
            return si
        else:
            return self.si_start

    def take_joint_pursuer_action(self,si, ai):
        if self.is_done(si): return REWARDS['player_Rcatch'] , "done"
        evader = 2
        statei = self.MDP.joint.S[si]
        actioni = self.MDP.joint.A[ai]
        statej = np.copy(statei)
        statej[0:2,:] += actioni
        sj1_adm = np.where(self.MDP.joint.T[si, ai, :] > 0)[0]
        sj2_adm = np.where(np.all(self.MDP.joint.S[:, evader, :] == statei[evader, :], axis=1))[0]
        try: sj = sj1_adm[np.where([(sj1 in sj2_adm) for sj1 in sj1_adm])[0][0]]
        except: raise Exception("Cannot find common sj")
        reward = self.MDP.joint.R_player[sj]
        return reward, sj

    # def takeNextAction(self,si, ai):
    #     if self.is_terminal(si): return 0, None
    #     # sj1_adm = np.array(np.where(self.MDP.T[si,ai[0],:]>0)).T
    #     # sj2_adm = np.array(np.where(self.MDP.T[si,ai[1],:]>0)).T
    #     # sj3_adm = np.array(np.where(self.MDP.T[si,ai[2],:]>0)).T
    #     sj1_adm = np.all(self.MDP.T[si, ai[0], :] > 0).T
    #     sj2_adm = np.all(self.MDP.T[si, ai[1], :] > 0).T
    #     sj3_adm = np.all(self.MDP.T[si, ai[2], :] > 0).T
    #     sj_adm = np.array([sj1_adm, sj2_adm, sj3_adm])
    #     sj = np.where(np.all(sj_adm==1,axis=1))
    #     reward = self.MDP.R_player[si]
    #     return reward,sj

    def is_done(self,si,is_init=False):
        done = False
        # if self.MDP.joint.Si_terminal[si]:
        #     self.was_caught=1
        #     print(f'\t EVADER CAUGHT \t {[list(stateik) for stateik in self.MDP.joint.S[si]]}')
        if si=="done": done=True
        elif is_caught(self.MDP.joint.S[si]):
            if not is_init: self.was_caught = 1
            done = True
        # try:
        #     if is_caught(self.MDP.joint.S[si]):
        #         if not is_init: self.was_caught=1
        #         done = True
        # except: raise Exception(f"Error in determining if game is done si={si}")
        elif self.round >= self.max_rounds: done=True
        return done

    def reset(self):
        for key in self.init_params:
            self.__dict__[key] = self.init_params[key]
        return self.generateInitialState()