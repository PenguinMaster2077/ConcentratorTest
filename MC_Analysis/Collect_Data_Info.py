# Python
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd # 处理csv
import os
import sys
# Self-Defined
sys.path.append('./Heads')
import Head_Collect_Data_Info

for distance in range(1, 3):
    Head_Collect_Data_Info.Compute_Systemric_Error_Installation(distance)
    Head_Collect_Data_Info.Compute_Systemric_Error_Diameter(distance)
    Head_Collect_Data_Info.Compute_Total_Systemric_Error(distance)