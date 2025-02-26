import h5py
import os
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from scipy.optimize import minimize
import pandas as pd # 处理csv
import argparse # 传参
import sys
import os
sys.path.append("/home/penguin/Jinping/JSAP-install/Codes/Heads")
sys.path.append("/home/penguin/PMTAnalysis/Heads")
# Self-Defined
import Head_Base_Functions
import Head_Collect_Data_Info
import Head_Collect_MC_Info
import Rough_Analysis
import Head_Plot_Paper

Head_Plot_Paper.Plot_Peak_Amplitude_Time_Distribution()