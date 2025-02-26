# Python
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd # 处理csv
import csv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Heads'))
# Self-Defined
import Head_Base_Functions
import Head_Collect_MC_Info
import Head_Collect_Data_Info
import Head_Plot

# CSV_Dir = "/mnt/e/PMT/Parallel_Light/01/CSV"
# wavelength = 365
# # # CON/PMT 和 Ratio
# plt.figure(figsize=(10, 8))
# Wavelengths = [365, 415, 465, 480]
# for index in range(len(Wavelengths)):
#     wavelength = Wavelengths[index]
#     CSV_PMT_Path = CSV_Dir + f"/{wavelength}_PMT.csv"
#     CSV_Con_Path = CSV_Dir + f"/{wavelength}_Con.csv"
#     data_pmt = pd.read_csv(CSV_PMT_Path)
#     data_con = pd.read_csv(CSV_Con_Path)
#     angles = data_pmt["angle"].values
#     con_pmt = data_con["num_photon"] / data_pmt["num_photon"]
#     con_pmt_error = con_pmt * np.sqrt(( data_con["num_error_photon"]/data_con["num_photon"])**2 + (data_pmt["num_error_photon"]/data_pmt["num_photon"])**2)
#     plt.errorbar(angles, con_pmt, yerr=con_pmt_error, fmt='o', capsize=5, capthick=1, label=f"{wavelength} nm", color=f'C{index}')
# plt.ylabel("Concentration factor", fontsize = 30)
# plt.xlabel("Angle/deg", fontsize = 30)
# plt.xlim(-5, 95)
# plt.ylim(0, 1.8)
# plt.xticks(np.arange(-5, 95, 5))
# plt.yticks(np.arange(0, 1.8, 0.1))
# plt.tick_params(axis='both', which='major', labelsize = 15)
# plt.grid(True, linestyle='--', color='black', linewidth=0.5)
# plt.legend(fontsize = 30)
# # plt.show()
# pic_path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Res/Parallel_Light_Ratio_All_Waves.jpg"
# plt.savefig(pic_path, dpi=500)

Head_Plot.Plot_Data_MC_All_Waves_Errors_All_Distance()