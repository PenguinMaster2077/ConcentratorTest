# Python
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd # 处理csv
import csv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Heads'))
# Self-Defined
import Head_Collect_MC_Info
import Head_Base_Functions
import Head_Collect_Data_Info

distance = 2
if distance == 1:
    angle_cut_off = 75
elif distance == 2:
    angle_cut_off = 80
    
# Head_Collect_MC_Info.Compute_MC_Systematic_Error_Angle_Shift(distance, 0, angle_cut_off)
# Head_Collect_MC_Info.Compute_MC_Systematic_Error_Z_Shift(distance, 3, 0, angle_cut_off)
# Head_Collect_MC_Info.Compute_MC_Systematic_Error_Radius_Shift(distance, 3, 0, angle_cut_off)
Head_Collect_MC_Info.Compute_Total_Systematic_Relative_Error(distance, angle_cut_off)
    
