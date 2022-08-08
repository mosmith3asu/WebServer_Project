import copy
import itertools
# import matplotlib.pyplot as plt
from Web_Server.game_backend.game_data.settings import *
from Web_Server.game_backend.scripts.Qlearning_Cent_utils import load_Qfun
from Web_Server.game_backend.scripts.MDP_tools import load_MDP,is_caught
import numpy as np
# import nashpy as nash
# from functools import partial
from itertools import product
from  Web_Server.game_backend.game_data.worlds import WORLDS
from Web_Server.game_backend.scripts.Qlearning_Cent_utils import *
from Web_Server.game_backend.scripts.enviorment_utils import Enviorment
from Web_Server.game_backend.scripts.Qlearning_Cent_utils import initQ_evader
from scipy.optimize import minimize
import scipy.stats as stats
from pandas import DataFrame
from flask import Flask, render_template
import time


class JointPursuitGame:
    def __init__(self):
        # MDP_path ='C:\\Users\\mason\\Desktop\\Effects_of_CPT_Accuracy\\learning\\MDP\\Cent_MDP_data'
        # loaded = np.load(MDP_path + '.npz')
        # S, A, T_int, R_player, R_evader = loaded['S'], loaded['A'], loaded['T'], loaded['R_player'], loaded['R_evader']
        # # A = np.array(list(product(ACTIONS['list'],  ACTIONS['list'])), dtype='int8')
        # nS = np.shape(S)[0]
        # Ak = ACTIONS['list']
        # nA = np.shape(A)[0]
        # nAk = np.shape(Ak)[0]

        # SETTINGS #########################################################################
        self.nGames = 7
        self.ihuman = 0
        self.irobot = 1
        self.ievader = 2
        self.client_delay = 0.0 # used to offset interface delay


        # INIT CURRENT GAME DATA ###########################################################
        self.playing_game = False
        self.iWorld = None
        self.timer = None
        self.player_pen = None
        self.moves = None
        self.pos = None
        self.world_data = None
        self.world = None
        self.clock = {'start': time.time(),'now':time.time(),'elapsed':time.time()-time.time()}
        self.execute = {'enable':False,'last_turn':-1,'this_turn':-1,'last_action':[0,0]}

        # MASTER STAGES #####################################################################
        # self.MASTER_STAGE = 1
        self.MASTER_STAGE = 0
        self.MASTER_STAGES = {}
        self.MASTER_STAGES['pretrial'] = 0
        self.MASTER_STAGES['trial'] = 1
        self.MASTER_STAGES['debrief'] = 2
        self.MASTER_STAGES['close'] = 3

        # PRETRIAL STAGE ####################################################################
        # self.pretrial_stage = 9 # <======= DEBUGGING ===========
        self.pretrial_stage = 0

        self.pretrial_dict = {}
        self.pretrial_dict[0] = {'type':'page','html': 'image_button_page.html', 'file': 'Page_Consent.jpg'}
        self.pretrial_dict[1] = {'type':'page','html': 'image_button_page.html', 'file':'Page_Background.jpg'}
        self.pretrial_dict['Unable to participate'] = {'html': 'img_page', 'file': 'Page_Exclusion.jpg'}
        self.pretrial_dict[2] =  {'type':'page','html': 'image_button_page.html', 'file': 'Page_Survey.jpg'}
        self.pretrial_dict[3] =  {'type':'survey','html': 'survey_pretrial.html', 'file': None}
        self.pretrial_dict[4] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_GameInfo.jpg'}
        self.pretrial_dict[5] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_Objective.jpg'}
        self.pretrial_dict[6] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_Environment.jpg'}
        self.pretrial_dict[7] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_Scoring.jpg'}
        self.pretrial_dict[8] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_Turns.jpg'}
        self.pretrial_dict[9] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_Controls.jpg'}
        self.pretrial_dict[10] =  {'type':'page','html': 'image_button_page.html', 'file':'Page_Practice.jpg'}
        # self.pretrial_dict[9] = {'type':'practice','html': 'game_canvas.html', 'file': 'Game_Practice.jpg','params':  self.load_practice_game()}
        self.pretrial_max_stages = len(self.pretrial_dict)-2

        # TRIAL STAGE #######################################################################
        self.trial_stage = 0
        game_params = self.load_game_params()
        treatment = self.load_treatment()
        self.trial_dict = {}
        self.pages_per_game = 3

        for iG in range(self.nGames):
            self.trial_dict[self.pages_per_game*iG + 0] = {'html': 'risk_information.html', 'params': treatment}
            self.trial_dict[self.pages_per_game*iG + 1] = {'html': 'game_canvas.html', 'params': game_params[iG]}
            self.trial_dict[self.pages_per_game*iG + 2] = {'html': 'survey.html', 'params': None}
        self.trial_max_stages = len(self.trial_dict)


        # DEBRIEF STAGE #####################################################################
        self.debrief_stage = 0
        self.debrief_max_stages = 2
        self.debrief_dict = {}
        self.debrief_dict[0] = {'html': 'image_button_page.html', 'file': 'Page_Debrief.jpg'}
        self.debrief_dict[1] = {'html': 'image_button_page.html', 'file': 'Page_DebriefInfo.jpg'}

#####################################################################################
# MAIN RENDER #######################################################################
#####################################################################################
    def get_page(self):
        self.update()
        # recalculate current stage after advanced
        is_pretrial = (self.MASTER_STAGE == self.MASTER_STAGES['pretrial'])
        is_trial = (self.MASTER_STAGE == self.MASTER_STAGES['trial'])
        is_debrief = (self.MASTER_STAGE == self.MASTER_STAGES['debrief'])
        is_close = (self.MASTER_STAGE == self.MASTER_STAGES['close'])

        # PRETRIAL ------------------------------------------
        if is_pretrial:
            print('rendering pretrial page....')
            print(f'\t| html: {self.pretrial_dict[self.pretrial_stage]["html"]}')
            print(f'\t| html: {self.pretrial_dict[self.pretrial_stage]["file"]}')

            # Render survey form
            if self.pretrial_dict[self.pretrial_stage]["type"] == 'survey':
                return render_template(self.pretrial_dict[self.pretrial_stage]['html'])

            # Render practice game
            elif self.pretrial_dict[self.pretrial_stage]["type"] == 'practice':
                pass

            # Render instruction pages
            else:
                return render_template(self.pretrial_dict[self.pretrial_stage]['html'], user_image=self.pretrial_dict[self.pretrial_stage]['file'])

        # TRIAL ------------------------------------------
        elif is_trial:
            print('rendering game....')
            print(f'\t| html: {self.trial_dict[self.trial_stage]["html"]}')
            print(f'\t| html: {self.trial_dict[self.trial_stage]["params"]}')

            # if playing game, dump current game params into root class params
            is_new_game = (self.trial_stage % 3) == 0 # at risk info page
            if is_new_game:
                print('\t| Dumping new game data to parent...')
                for key in self.trial_dict[self.trial_stage+1]['params']:
                    self.__dict__[key] = self.trial_dict[self.trial_stage+1]['params'][key]

            return render_template(self.trial_dict[self.trial_stage]['html'], **self.trial_dict[self.trial_stage]['params'])

        # DEBRIEF ------------------------------------------
        elif is_debrief:
            msg = 'TEMP DEBRIEF PAGE'
            return render_template('render_error.html', msg = msg)

        # CLOSE ------------------------------------------
        elif is_close:
            msg = 'TEMP CLOSE PAGE'
            return render_template('render_error.html', msg = msg)

        # TROW ERROR -------------------------------------
        else:
            msg = 'ERROR: Game Handler failed to generate page'
            return render_template('render_error.html', msg = msg)

#####################################################################################
# PLAY GAME #########################################################################
#####################################################################################
    def start_new_game(self):
        self.playing_game = True
        self.moves = 20
        self.clock['start'] = time.time()
        self.clock['now'] = time.time()
        self.clock['elapsed'] = self.clock['now'] - self.clock['start']
        self.timer = (self.clock['elapsed']) % 2 - 1
        self.execute['enable'] = False
        self.execute['last_turn'] = (-1 if self.timer < 0 else 1)

    def tictock(self):
        """  advance gamestate """
        self.clock['now'] = time.time()
        self.clock['elapsed'] = self.clock['now'] - self.clock['start']
        self.timer = (self.clock['elapsed']) % 2 - 1
        self.moves = 20 - int((self.clock['elapsed']) / 2)

        self.execute['this_turn'] = -1 if self.timer < 0 else 1
        is_turn_changed = (self.execute['this_turn'] != self.execute['last_turn'])

        if is_turn_changed:
            is_evader_turn = True if self.execute['this_turn'] == -1 else False
            if is_evader_turn: self.execute['enable'] = True
            self.execute['last_turn'] = self.execute['this_turn']


    def move_player(self,new_action):
        def apply_bounds(val,bnds):
            return min(max(val,bnds[0]),bnds[1])

        self.execute['last_action'] = new_action

        if self.execute['enable']:
            action = self.execute['last_action']
            bounds = [1,5]
            ix, iy = 1, 0
            x0 = self.pos[self.ihuman][ix]
            y0 = self.pos[self.ihuman][iy]

            # Check boundries
            x1 = apply_bounds(x0+action[ix],bounds)
            y1 = apply_bounds(y0+action[iy],bounds)
            if    np.all([x1, y1] == [2, 2]): is_valid = False
            elif  np.all([x1, y1] == [2, 4]): is_valid = False
            elif  np.all([x1, y1] == [4, 2]): is_valid = False
            elif  np.all([x1, y1] == [4, 4]): is_valid = False
            else: is_valid = True
            self.pos[self.ihuman] = [y1, x1] if is_valid else [y0, x0]
            # self.pos[self.ihuman] = [x1, y1] if is_valid else [x0,y0]

            self.execute['enable'] = False
            self.execute['last_action'] = [0,0]

        return self.pos
    def check_finished(self):
        done = (is_caught(self.pos) or self.moves == 0)
        if done: self.playing_game = False
        return done
    def check_player_in_penalty(self):
        ix, iy = 1, 0
        x0 = self.pos[self.ihuman][ix]
        y0 = self.pos[self.ihuman][iy]
        pen_val = WORLDS['pen_val']
        world = WORLDS[self.iWorld]['array'].T
        if world[y0,x0] == pen_val: in_pen = True
        else: in_pen = False
        return in_pen

    def get_timer(self):
        return self.timer
#####################################################################################
# UTILITIES #########################################################################
#####################################################################################
    def report(self):
        msg = {}
        msg['MASTER_STAGE  '] = self.MASTER_STAGE
        msg['pretrial_stage'] = f'{self.pretrial_stage}/{self.pretrial_max_stages}'
        msg['trial_stage   '] = f'{self.trial_stage}/{self.trial_max_stages}'
        msg['debrief_stage '] = f'{self.debrief_stage}/{self.debrief_max_stages}'
        print('\n--------------------------------------')
        print('-- GAME HANDLER REPORT ---------------')
        print('--------------------------------------')
        for key in msg: print(f'\t| {key}: \t {msg[key]}')
        print('--------------------------------------')
        print('--------------------------------------\n')

    def update(self):
        # CALC MASTER STAGE ---------------------------------
        # check current master stage
        is_pretrial = (self.MASTER_STAGE == self.MASTER_STAGES['pretrial'])
        is_trial = (self.MASTER_STAGE == self.MASTER_STAGES['trial'])
        is_debrief = (self.MASTER_STAGE == self.MASTER_STAGES['debrief'])

        # Check if master stage should advance
        if is_pretrial and self.pretrial_stage > self.pretrial_max_stages:
            self.MASTER_STAGE = self.MASTER_STAGES['trial']
            self.pretrial_stage = -1
            print('ADVANCING TO \t=\t TRIAL')
        elif is_trial and self.trial_stage > self.trial_max_stages:
            self.MASTER_STAGE = self.MASTER_STAGES['debrief']
        elif is_debrief and self.debrief_stage > self.debrief_max_stages:
            self.MASTER_STAGE = self.MASTER_STAGES['close']


#####################################################################################
# LOAD DATA #########################################################################
#####################################################################################
    def load_treatment(self):
        treatment = {}
        treatment['pen'] = 5
        treatment['prob'] = 0.9
        return treatment

    def load_game_params(self):
        games = []
        for iWorld in range(1,self.nGames+1):
            G = {}
            G['iWorld'] = iWorld
            G['timer'] = -1
            G['player_pen'] = 0
            G['moves'] = 20
            G['pos'] = WORLDS[iWorld]['start']
            G['received_penalty'] = 0
            world_data = []
            for row in  WORLDS[iWorld]['array']:  world_data.append(list(row))
            G['world'] = world_data
            games.append(G)
        return games

    def load_practice_game(self):
        iWorld = 0
        G = {}
        G['iWorld'] = 0
        G['timer'] = -1
        G['player_pen'] = 0
        G['moves'] = 20
        G['pos'] = WORLDS[iWorld]['start']
        world_data = []
        for row in  WORLDS[iWorld]['array']:  world_data.append(list(row))
        G['world'] = world_data
        return G



if __name__ == "__main__":
    # main()
    # world = WORLDS[self.iWorld]['array']
    # world_data = []
    # stage = 0
    # player_penalty = 0
    # round = 0
    # turn_timer = 0  # from [-1,1] indicating evader -> player turn
    #
    # for row in world:
    #     world_data.append(list(row))
    #
    # return render_template("index.html", world=world_data, pos=WORLDS[self.iWorld]['start'], stage=stage)

    # return render_template("image_button_page.html", img_name=self.page_root + self.stage_dict[0]['file'])
    # return render_template("image_button_page.html", img_name=self.stage_dict[0]['file'])

    pass