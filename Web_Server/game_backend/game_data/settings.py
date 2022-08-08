import numpy as np
#######################################################################################
######################## GAME SETTINGS  ###############################################
#######################################################################################
BOUNDS01 = (0.2,0.8)
page_file_root = "G:\\My Drive\\1. Classes\\1. RISE Labs\\1. Dissertation\\Paper Writing\\Joint-Pursuit Evasion Game\\WebServer_Project\\Web_Server\\game_backend\\assets\\"


#######################################################################################
######################### MDP SETTINGS  ###############################################
#######################################################################################
MDP_path ='G:\\My Drive\\1. Classes\\1. RISE Labs\\1. Dissertation\\Paper Writing\\Joint-Pursuit Evasion Game\\WebServer_Project\\Web_Server\\game_backend\\game_data\\Cent_MDP_data'

# import matplotlib.pyplot as plt

# MDP_file_path = 'Dec_MDP_data'
MDP_file_path = 'Cent_MDP_data'
# MDP_file_path = 'MDP_nAgents1_data'
# MDP_file_path = 'MDP_nAgents2_data'


REWARDS = {}
REWARDS['player_Rcatch'] = 20
REWARDS['player_Rtime'] = -1
REWARDS['player_scale_Rdist'] = 1
REWARDS['player_Rpenalty'] = -3
REWARDS['player_Ppenalty'] = 0.5

REWARDS['evader_Rcatch'] = -20
REWARDS['evader_Rtime'] = 1
REWARDS['evader_scale_Rdist'] = 1


ACTIONS = {}
ACTIONS['wait' ]  = np.array([0, 0])
ACTIONS['up'   ]  = np.array([-1, 0])
ACTIONS['right']  = np.array([0, 1])
ACTIONS['down' ]  = np.array([1, 0])
ACTIONS['left' ]  = np.array([0, -1])
ACTIONS['list'] = np.array([ACTIONS['wait' ],ACTIONS['up'   ] ,ACTIONS['right'],ACTIONS['down' ],ACTIONS['left' ]])

