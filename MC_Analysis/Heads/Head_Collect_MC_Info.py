# Python
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd # 处理csv
import sys
import os
import csv
# Self-Defined
import Head_Collect_Data_Info
import Head_Base_Functions
import Head_Plot
# Function

# # 计算某个波长的Test/Cali的平均值及其误差
def Random_Seed_Compute_Average(wavelength, mode):
    CSV_Dir = "/mnt/e/PMT/RandomSeed"
    length = 5
    # Define Variables
    Angles = [[] for _ in range(length)]
    Test_Cali = [[] for _ in range(length)]
    Ratio = [[] for _ in range(length)]
    # Get Data
    for ii1 in range(0, length):
        CSV_PMT_Path = CSV_Dir + f"/0{ii1 + 1}/CSV/L1_{wavelength}_PMT.csv"
        CSV_CON_Path = CSV_Dir + f"/0{ii1 + 1}/CSV/L1_{wavelength}_Con.csv"
        data_pmt = pd.read_csv(CSV_PMT_Path)
        data_con = pd.read_csv(CSV_CON_Path)       
        # Compute Ratio
        Ratio[ii1] = (data_con["ratio"] / data_pmt["ratio"]).tolist()
        # Record Data
        if mode == 0:
            Angles[ii1] = data_pmt["angle"].tolist()
            Test_Cali[ii1] = data_pmt["ratio"].tolist()
        elif mode == 1:
            Angles[ii1] = data_con["angle"].tolist()
            Test_Cali[ii1] = data_con["ratio"].tolist()            
    # Compute Average and Return
    if mode == 0 or mode == 1:
        Average_Test_Cali = np.mean(Test_Cali, axis=0)
        Error_Test_Cali = np.max(np.abs(Test_Cali[:] - Average_Test_Cali), axis=0)
        return Test_Cali, Average_Test_Cali, Error_Test_Cali
    elif mode == 2:
        Average_Ratio = np.mean(Ratio, axis=0)
        Error_Ratio = np.max(np.abs(Ratio[:] - Average_Ratio), axis=0)
        return Ratio, Average_Ratio, Error_Ratio
# # 估算随机种子对模拟的影响 (舍弃)
def Plot_MC_Random_Seed():
    CSV_Dir = "/mnt/e/PMT/RandomSeed"
    length = 5
    Wavelengths = [365, 415, 465, 480]
    Angles_PMT = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Angles_CON = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Ratios_PMT = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Ratios_CON = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Ratios_Error_PMT = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Ratios_Error_CON = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Con_PMT = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    Con_PMT_Error = [[[ ] for _ in range(len(Wavelengths))] for _ in range(length)]
    # Get Data
    for Number in range(1, length + 1):
        for index in range(len(Wavelengths)):
            wavelength = Wavelengths[index]
            CSV_PMT_Path = CSV_Dir + f"/0{Number}/CSV/L1_{wavelength}_PMT.csv"
            CSV_CON_Path = CSV_Dir + f"/0{Number}/CSV/L1_{wavelength}_Con.csv"
            # Get Data
            data_pmt = pd.read_csv(CSV_PMT_Path)
            data_con = pd.read_csv(CSV_CON_Path)
            # Record Data
            Angles_PMT[Number - 1][index] = data_pmt["angle"].tolist()
            Angles_CON[Number - 1][index] = data_con["angle"].tolist()
            Ratios_PMT[Number - 1][index] = data_pmt["ratio"].tolist()
            Ratios_CON[Number - 1][index] = data_con["ratio"].tolist()
            Ratios_Error_PMT[Number - 1][index] = data_pmt["ratio_error"].tolist()
            Ratios_Error_CON[Number - 1][index] = data_con["ratio_error"].tolist()
            # Compute Con/PMT
            Con_PMT[Number - 1][index] = (data_con["ratio"] / data_pmt["ratio"]).tolist()
            Con_PMT_Error[Number - 1][index] = Con_PMT[Number - 1][index] * np.sqrt((data_con["ratio_error"]/data_con["ratio"])**2 + (data_pmt["ratio_error"]/data_pmt["ratio"])**2)
    # Compute Mean and Max Bias
    Ratios_PMT = np.array(Ratios_PMT)
    Ratios_CON = np.array(Ratios_CON)
    Con_PMT = np.array(Con_PMT)

    Means_PMT = [[] for _ in range(len(Wavelengths))]
    Bias_PMT = [[] for _ in range(len(Wavelengths))]
    Means_CON = [[] for _ in range(len(Wavelengths))]
    Bias_CON = [[] for _ in range(len(Wavelengths))]
    Means_Con_PMT = [[] for _ in range(len(Wavelengths))]
    Bias_Con_PMT = [[] for _ in range(len(Wavelengths))]
    for ii1 in range(len(Wavelengths)):
        # PMT
        Means_PMT[ii1] = np.mean(Ratios_PMT[:, ii1], axis=0)
        Bias_PMT[ii1] = np.max(np.abs(Ratios_PMT[:, ii1] - Means_PMT[ii1]), axis=0)
        # Con
        Means_CON[ii1] = np.mean(Ratios_CON[:, ii1], axis=0)
        Bias_CON[ii1] = np.max(np.abs(Ratios_CON[:, ii1] - Means_CON[ii1]), axis=0)
        # Con/PMT
        Means_Con_PMT[ii1] = np.mean(Con_PMT[:, ii1], axis=0)
        Bias_Con_PMT[ii1] = np.max(np.abs(Con_PMT[:, ii1] - Means_Con_PMT[ii1]), axis=0)
        
    # Plot PMT Data
    for ii1 in range(len(Wavelengths)):
        plt.figure(figsize=(10, 8))
        for ii2 in range(0, length):
            plt.errorbar(Angles_PMT[ii2][ii1], Ratios_PMT[ii2][ii1],
                        yerr=Ratios_Error_PMT[ii2][ii1],
                        fmt='o', capsize=5, capthick=1,
                        label=f'No{ii2 + 1}',
                        color=f"C{ii2}"
                        )
        plt.fill_between(Angles_PMT[0][0], Means_PMT[ii1] - Bias_PMT[ii1], Means_PMT[ii1] + Bias_PMT[ii1],
                        color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
        plt.plot(Angles_PMT[0][0], Means_PMT[ii1], linestyle="--", color="black", linewidth=1.5, label="Mean")
        plt.title(f"Random Seed: {Wavelengths[ii1]} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Test/Cali")
        plt.ylim(0, 2.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 2.5, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Random_Seed/L1_{Wavelengths[ii1]}_PMT.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot Concentrator Data
    for ii1 in range(len(Wavelengths)):
        plt.figure(figsize=(10, 8))
        for ii2 in range(0, length):
            plt.errorbar(Angles_CON[ii2][ii1], Ratios_CON[ii2][ii1],
                        yerr=Ratios_Error_CON[ii2][ii1],
                        fmt='o', capsize=5, capthick=1,
                        label=f'No{ii2 + 1}',
                        color=f"C{ii2}"
                        )
        plt.fill_between(Angles_PMT[0][0], Means_CON[ii1] - Bias_CON[ii1], Means_CON[ii1] + Bias_CON[ii1],
                        color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
        plt.plot(Angles_PMT[0][0], Means_CON[ii1], linestyle="--", color="black", linewidth=1.5, label="Mean")
        plt.title(f"Random Seed: {Wavelengths[ii1]} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Test/Cali")
        plt.ylim(0, 4.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 4.5, 0.25)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Random_Seed/L1_{Wavelengths[ii1]}_CON.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot Con/PMT
    for ii1 in range(len(Wavelengths)):
        plt.figure(figsize=(10, 8))
        for ii2 in range(0, length):
            plt.errorbar(Angles_CON[ii2][ii1], Con_PMT[ii2][ii1],
                        yerr=Con_PMT_Error[ii2][ii1],
                        fmt='o', capsize=5, capthick=1,
                        label=f'No{ii2 + 1}',
                        color=f"C{ii2}"
                        )
        plt.fill_between(Angles_PMT[0][0], Means_Con_PMT[ii1] - Bias_Con_PMT[ii1], Means_Con_PMT[ii1] + Bias_Con_PMT[ii1],
                        color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
        plt.plot(Angles_PMT[0][0], Means_Con_PMT[ii1], linestyle="--", color="black", linewidth=1.5, label="Mean")
        plt.title(f"Random Seed: {Wavelengths[ii1]} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Con/PMT")
        plt.ylim(0, 2.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 2.6, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Random_Seed/L1_{Wavelengths[ii1]}_Ratio.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot Relative Error of Con/PMT
    plt.figure(figsize=(10, 8))
    for ii1 in range(len(Wavelengths)):
        plt.plot(Angles_CON[0][0], Bias_Con_PMT[ii1] / Means_Con_PMT[ii1],
                label=f'{Wavelengths[ii1]}', color=f"C{ii1}")
    plt.title(f"Random Seed: Relative Error")
    plt.xlabel("Angle/deg")
    plt.ylabel("Relative Error")
    plt.ylim(0, 1)
    plt.xlim(-5, 95)
    y_ticks = np.arange(0, 1, 0.05)
    plt.yticks(y_ticks)
    x_ticks = np.arange(-5, 96, 5)
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend()
    # plt.show()
    Pic_Path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Random_Seed/L1_Ratio_Relative_Error.jpg"
    plt.savefig(Pic_Path, dpi=500)
    plt.close()
# # 估算散射球在Z移动带来的误差，写的比较失败
def Compute_MC_Systematic_Error_Z_Shift(distance, angle_shift, sys_error = 0.0, angle_cut_off = 0):
    CSV_Dir = f"/mnt/e/PMT/Z_Shift/L{distance}/Z_"
    # Dirs = ["N1", "N2", "N3", "P1", "P2", "P3"]
    Dirs = ["N1", "P1"]
    # Dirs = ["N3", "P3"]
    Wavelengths = [365, 415, 465, 480]
    # Record CSV
    CSV_Relative_Error = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_Z_Shift.csv"
    print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Z_Shift] The result is save in {CSV_Relative_Error}")
    header = ['distance','led','tag', 'angle', 'relative_error']
    with open(CSV_Relative_Error, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
    # Get Data
    for ii1 in range(len(Wavelengths)):
        wavelength = Wavelengths[ii1]
        length = len(Dirs)
        Angles_PMT = [[] for _ in range(length)]
        Angles_CON = [[] for _ in range(length)]
        Test_Cali_PMT = [[] for _ in range(length)]
        Test_Cali_CON = [[] for _ in range(length)]
        Test_Cali_Error_PMT = [[] for _ in range(length)]
        Test_Cali_Error_CON = [[] for _ in range(length)]
        Con_PMT = [[] for _ in range(length)]
        Con_PMT_Error = [[] for _ in range(length)]
        # Get Data
        for ii2 in range(length):
            CSV_PMT_Dir = CSV_Dir + Dirs[ii2] + f"/CSV/L{distance}_{wavelength}_PMT.csv"
            CSV_CON_Dir = CSV_Dir + Dirs[ii2] + f"/CSV/L{distance}_{wavelength}_Con.csv"
            if distance == 1:
                data_pmt = pd.read_csv(CSV_PMT_Dir).iloc[:-1]
                data_con = pd.read_csv(CSV_CON_Dir).iloc[:-1]
            elif distance == 2:
                data_pmt = pd.read_csv(CSV_PMT_Dir)
                data_con = pd.read_csv(CSV_CON_Dir)
            data_pmt = data_pmt.apply(pd.to_numeric, errors='coerce')
            data_con = data_con.apply(pd.to_numeric, errors='coerce')
            # 用0代替Nan
            data_pmt.fillna(0, inplace=True)
            data_con.fillna(0, inplace=True)
            # Compute
            ratio = (data_con["ratio"] / data_pmt["ratio"])
            ratio_error = ratio * np.sqrt((data_con["ratio_error"] / data_con["ratio"])**2 + (data_pmt["ratio_error"] / data_pmt["ratio"])**2 + sys_error**2)
            # Record Data
            Angles_PMT[ii2] = (angle_shift + data_pmt["angle"]).values
            Angles_CON[ii2] = (angle_shift + data_con["angle"]).values
            Test_Cali_PMT[ii2] = data_pmt["ratio"].values
            Test_Cali_CON[ii2] = data_con["ratio"].values
            Test_Cali_Error_PMT[ii2] = data_pmt["ratio_error"].values
            Test_Cali_Error_CON[ii2] = data_con["ratio_error"].values
            Con_PMT[ii2] = ratio.values
            Con_PMT_Error[ii2] = ratio_error.values
    # Plot PMT Data
        Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/MC/Z_Shift/L{distance}"
        print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Z_Shift] Pics are save in {Pic_Dir}")
        plt.figure(figsize=(10, 8))
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 0, 0)
        plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Data")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                        color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 0, 0, 0)
        plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Standard")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                            color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
        for ii2 in range(length):
            plt.errorbar(Angles_PMT[ii2], Test_Cali_PMT[ii2],
                        yerr=Test_Cali_Error_PMT[ii2],
                        fmt='o', capsize=5, capthick=1,
                        label=f'{Dirs[ii2]}',
                        color=f"C{ii2}"
                        )
        plt.title(f"Z Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Test/Cali")
        plt.ylim(0, 2.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 2.5, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_PMT.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot Concentrator Data
        plt.figure(figsize=(10, 8))
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 1)
        plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Data")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                        color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 1, 0, 0)
        plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Standard")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                            color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
        for ii2 in range(length):
            plt.errorbar(Angles_CON[ii2], Test_Cali_CON[ii2],
                        yerr=Test_Cali_Error_CON[ii2],
                        fmt='o', capsize=5, capthick=1,
                        label=f'{Dirs[ii2]}',
                        color=f"C{ii2}"
                        )
        plt.title(f"Z Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Test/Cali")
        plt.ylim(0, 4.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 4.5, 0.25)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_CON.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot Con/PMT
        plt.figure(figsize=(10, 8))
        angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2)
        angle = angle[angle <= angle_cut_off]
        con_pmt = con_pmt[:len(angle)]
        con_pmt_error = con_pmt_error[:len(angle)]
        plt.plot(angle, con_pmt, linestyle="--", color="black", linewidth=1.5, label="Data")
        plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
                        color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
        angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, angle_shift, 0, angle_cut_off)
        angle = angle[angle <= angle_cut_off]
        con_pmt = con_pmt[:len(angle)]
        con_pmt_error = con_pmt_error[:len(angle)]
        plt.plot(angle, con_pmt, linestyle="--", color="black", linewidth=1.5, label="Standard")
        plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
                            color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
        for ii2 in range(0, length):
            plt.errorbar(Angles_CON[ii2][:15], Con_PMT[ii2][:15],
                        yerr=Con_PMT_Error[ii2][:15],
                        fmt='o', capsize=5, capthick=1,
                        label=f'{Dirs[ii2]}',
                        color=f"C{ii2}"
                        )
        plt.title(f"Z Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Con/PMT")
        plt.ylim(0, 2.5)
        plt.xlim(0, 70)
        y_ticks = np.arange(0, 2.6, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(0, 70, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_Ratio.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Relative Error
        plt.figure(figsize=(10, 8))
        angle, std_con_pmt, std_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, angle_shift, 0, angle_cut_off)
        angle = angle[angle <= angle_cut_off]
        std_con_pmt = std_con_pmt[:len(angle)]
        for ii2 in range(length):
            relative_error = np.abs((std_con_pmt - Con_PMT[ii2][:len(std_con_pmt)]) / std_con_pmt)
            plt.plot(angle, relative_error, label=f"{Dirs[ii2]}", color=f"C{ii2}")
            # Write in CSV
            with open(CSV_Relative_Error, mode="a", newline="") as file:
                writer = csv.writer(file)
                for ang, re_err in zip(angle, relative_error):
                    writer.writerow([distance, wavelength, Dirs[ii2], ang, re_err])
        plt.title(f"Z Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Relative Error")
        plt.ylim(0, 1)
        plt.xlim(0, 70)
        y_ticks = np.arange(0, 1, 0.05)
        plt.yticks(y_ticks)
        x_ticks = np.arange(0, 70, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_Ratio_Relative_Error.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    with open(CSV_Relative_Error, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate()
# # 估算角度变化带来的误差
# def Compute_MC_Systematic_Error_Angle_Shift(distance, sys_error = 0.00):
#     CSV_Dir = f"/mnt/e/PMT/Angle_Shift/L{distance}/"
#     Wavelengths = [365, 415, 465, 480]
#     Dirs = ["N1", "P1"]
#     length = len(Dirs)
#     # Record CSV
#     CSV_Relative_Error = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_Angle_Shift.csv"
#     print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Angle_Shift] The result is save in {CSV_Relative_Error}")
#     header = ['distance','led','tag', 'angle', 'relative_error']
#     with open(CSV_Relative_Error, mode="w", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerow(header)
#     for ii1 in range(len(Wavelengths)):
#         wavelength = Wavelengths[ii1]
#         length = len(Dirs)
#         Angles_PMT = [[ ] for _ in range(length)]
#         Angles_CON = [[ ] for _ in range(length)]
#         Test_Cali_PMT = [[ ] for _ in range(length)]
#         Test_Cali_CON = [[ ] for _ in range(length)]
#         Test_Cali_Error_PMT = [[ ] for _ in range(length)]
#         Test_Cali_Error_CON = [[ ] for _ in range(length)]
#         Con_PMT = [[ ] for _ in range(length)]
#         Con_PMT_Error = [[ ] for _ in range(length)]
#     # Get Data
#         for ii2 in range(length):
#             CSV_PMT_Dir = CSV_Dir + Dirs[ii2] + f"/CSV/L{distance}_{wavelength}_PMT.csv"
#             CSV_CON_Dir = CSV_Dir + Dirs[ii2] + f"/CSV/L{distance}_{wavelength}_Con.csv"
#             if distance == 1:
#                 data_pmt = pd.read_csv(CSV_PMT_Dir).iloc[:-1]
#                 data_con = pd.read_csv(CSV_CON_Dir).iloc[:-1]
#             elif distance == 2:
#                 data_pmt = pd.read_csv(CSV_PMT_Dir)
#                 data_con = pd.read_csv(CSV_CON_Dir)
#             data_pmt = data_pmt.apply(pd.to_numeric, errors='coerce')
#             data_con = data_con.apply(pd.to_numeric, errors='coerce')
#             # 用0代替Nan
#             data_pmt.fillna(0, inplace=True)
#             data_con.fillna(0, inplace=True)
#             # Compute
#             ratio = data_con["ratio"] / data_pmt["ratio"]
#             ratio_error = ratio * np.sqrt((data_con["ratio_error"] / data_con["ratio"])**2 + (data_pmt["ratio_error"] / data_pmt["ratio"])**2 + sys_error**2)
#             # Record Data
#             Angles_PMT[ii2] = (5 + data_pmt["angle"]).values
#             Angles_CON[ii2] = (5 + data_con["angle"]).values
#             Test_Cali_PMT[ii2] = data_pmt["ratio"].values
#             Test_Cali_CON[ii2] = data_con["ratio"].values
#             Test_Cali_Error_PMT[ii2] = data_pmt["ratio_error"].values
#             Test_Cali_Error_CON[ii2] = data_con["ratio_error"].values
#             Con_PMT[ii2] = ratio.values
#             Con_PMT_Error[ii2] = ratio_error.values
#     # Plot PMT Data
#         Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/MC/Angle_Shift/L{distance}"
#         print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Angle_Shift] Pics are save in {Pic_Dir}")
#         plt.figure(figsize=(10, 8))
#         angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 0)
#         plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Data")
#         plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
#                         color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
#         angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 0)
#         plt.plot(angle, test_cali, linestyle="--", color="gray", linewidth=1.5, label="Standard")
#         plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
#                             color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
#         for ii2 in range(length):
#             plt.errorbar(Angles_PMT[ii2], Test_Cali_PMT[ii2],
#                         yerr=Test_Cali_Error_PMT[ii2],
#                         fmt='o', capsize=5, capthick=1,
#                         label=f'{Dirs[ii2]}',
#                         color=f"C{ii2}"
#                         )
#         plt.title(f"Angle Shift: {wavelength} nm")
#         plt.xlabel("Angle/deg")
#         plt.ylabel("Test/Cali")
#         plt.ylim(0, 2.5)
#         plt.xlim(-5, 95)
#         y_ticks = np.arange(0, 2.5, 0.2)
#         plt.yticks(y_ticks)
#         x_ticks = np.arange(-5, 96, 5)
#         plt.xticks(x_ticks)
#         plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
#         plt.legend()
#         # plt.show()
#         Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_PMT.jpg"
#         plt.savefig(Pic_Path, dpi=500)
#         plt.close()  
#     # Plot Concentrator Data
#         plt.figure(figsize=(10, 8))
#         angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 1)
#         plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Data")
#         plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
#                         color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
#         angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 1)
#         plt.plot(angle, test_cali, linestyle="--", color="gray", linewidth=1.5, label="Standard")
#         plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
#                             color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
#         for ii2 in range(length):
#             plt.errorbar(Angles_CON[ii2], Test_Cali_CON[ii2],
#                         yerr=Test_Cali_Error_CON[ii2],
#                         fmt='o', capsize=5, capthick=1,
#                         label=f'{Dirs[ii2]}',
#                         color=f"C{ii2}"
#                         )
#         plt.title(f"Angle Shift: {wavelength} nm")
#         plt.xlabel("Angle/deg")
#         plt.ylabel("Test/Cali")
#         plt.ylim(0, 4.5)
#         plt.xlim(-5, 95)
#         y_ticks = np.arange(0, 4.5, 0.25)
#         plt.yticks(y_ticks)
#         x_ticks = np.arange(-5, 96, 5)
#         plt.xticks(x_ticks)
#         plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
#         plt.legend()
#         # plt.show()
#         Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_CON.jpg"
#         plt.savefig(Pic_Path, dpi=500)
#         plt.close()
#     # Plot Con/PMT
#         plt.figure(figsize=(10, 8))
#         angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2)
#         plt.plot(angle, con_pmt, linestyle="--", color="black", linewidth=1.5, label="Data")
#         plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
#                         color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
#         # con_pmt_shift = con_pmt[-1]
#         angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2)
#         # con_pmt = con_pmt + con_pmt_shift
#         plt.plot(angle, con_pmt, linestyle="--", color="gray", linewidth=1.5, label="Standard")
#         plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
#                             color="gray", alpha=0.3, label=r"Mean $\pm$ Bias")
#         for ii2 in range(0, length):
#             plt.errorbar(Angles_CON[ii2], Con_PMT[ii2],
#                         yerr=Con_PMT_Error[ii2],
#                         fmt='o', capsize=5, capthick=1,
#                         label=f'{Dirs[ii2]}',
#                         color=f"C{ii2}"
#                         )
#         plt.title(f"Angle Shift: {wavelength} nm")
#         plt.xlabel("Angle/deg")
#         plt.ylabel("Con/PMT")
#         plt.ylim(0, 2.5)
#         plt.xlim(-5, 95)
#         y_ticks = np.arange(0, 2.6, 0.2)
#         plt.yticks(y_ticks)
#         x_ticks = np.arange(-5, 96, 5)
#         plt.xticks(x_ticks)
#         plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
#         plt.legend()
#         # plt.show()
#         Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_Ratio.jpg"
#         plt.savefig(Pic_Path, dpi=500)
#         plt.close()
#     # Relative Error
#         plt.figure(figsize=(10, 8))
#         angle, std_con_pmt, std_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2)
#         for ii2 in range(length):
#             relative_error = np.abs((std_con_pmt - Con_PMT[ii2]) / std_con_pmt)
#             plt.plot(angle, relative_error, label=f"{Dirs[ii2]}", color=f"C{ii2}")
#             # Write in CSV
#             with open(CSV_Relative_Error, mode="a", newline="") as file:
#                 writer = csv.writer(file)
#                 for ang, re_err in zip(angle, relative_error):
#                     writer.writerow([distance, wavelength, Dirs[ii2], ang, re_err])
#         plt.title(f"Angle Shift: {wavelength} nm")
#         plt.xlabel("Angle/deg")
#         plt.ylabel("Relative Error")
#         plt.ylim(0, 1)
#         plt.xlim(-5, 95)
#         y_ticks = np.arange(0, 1, 0.05)
#         plt.yticks(y_ticks)
#         x_ticks = np.arange(-5, 96, 5)
#         plt.xticks(x_ticks)
#         plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
#         plt.legend()
#         # plt.show()
#         Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_Ratio_Relative_Error.jpg"
#         plt.savefig(Pic_Path, dpi=500)
#         plt.close()
#     with open(CSV_Relative_Error, 'rb+') as file:
#         file.seek(-2, os.SEEK_END)
#         file.truncate()
# # MC整体平移后，根据线性插值计算新的曲线
def Compute_Shifted_Line(distance, wavelength, angle_shift, input_angles, mc_total_relatie_error, angle_cut_off):
    angles, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, angle_shift, mc_total_relatie_error, 0)

    Res = []
    Angles = []
    Error = []
    for index in range(len(input_angles)):
        angle = input_angles[index]
        index_angle = np.searchsorted(angles, angle) - 1
        if angle <= angle_cut_off :
            temp = con_pmt[index_angle] + (angle - angles[index_angle]) * (con_pmt[index_angle + 1] - con_pmt[index_angle]) / (angles[index_angle + 1] - angles[index_angle])
            Angles.append(angle)
            Res.append(temp)
            Error.append(con_pmt_error[index])
    Angles = np.array(Angles)
    Res = np.array(Res)
    # Res = np.maximum(Res, 0)
    Error = np.array(Error)
    # Return
    return Angles, Res, Error
def Compute_MC_Systematic_Error_Angle_Shift(distance, sys_error = 0.0, angle_cut_off = 0):
    Wavelengths = [365, 415, 465, 480]
    pic_dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/MC/Angle_Shift/L{distance}"
    # CSV_Dir = f"/mnt/e/PMT/Angle_Shift/L{distance}/"
    # CSV File
    CSV_Relative_Error = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_Angle_Shift.csv"
    print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Angle_Shift] The result is save in {CSV_Relative_Error}")
    header = ['distance','led','tag', 'angle', 'relative_error']
    with open(CSV_Relative_Error, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
    # Loop Data
    for wavelength in Wavelengths:
        plt.figure(figsize=(10, 8))
        data_total_relative_error = Head_Collect_Data_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
        data_angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, data_total_relative_error)
        data_angle = data_angle[data_angle <= angle_cut_off]
        con_pmt = con_pmt[:len(data_angle)]
        con_pmt_error = con_pmt_error[:len(data_angle)]
        plt.fill_between(data_angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error, color='black', alpha=0.3, label="Data")
        plt.plot(data_angle, con_pmt, color='black')
        Angle_Shifts = np.array([3, 1, 2, 4, 5])
        mc_angle, _, _ = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, 0, angle_cut_off)
        _, mc_standard_con_pmt, _ = Compute_Shifted_Line(distance, wavelength, Angle_Shifts[0], mc_angle , 0, angle_cut_off)
        # _, mc_standard_con_pmt, _ = Compute_Shifted_Line(distance, wavelength, Angle_Shifts[0], data_angle , 0, angle_cut_off)
        error = [[] for _ in range(len(Angle_Shifts) - 1)]
        re_error = [[] for _ in range(len(Angle_Shifts) - 1)]
        for index in range(len(Angle_Shifts[1:])):
            # _, con_pmt, _ = Compute_Shifted_Line(distance, wavelength, Angle_Shifts[index + 1], data_angle , 0, angle_cut_off)
            _, con_pmt, _ = Compute_Shifted_Line(distance, wavelength, Angle_Shifts[index + 1], mc_angle , 0, angle_cut_off)
            error[index] = np.abs(con_pmt - mc_standard_con_pmt)
            re_error[index] = error[index] / con_pmt
            # Record
            Tags = ["N2", "N1", "P1", "P2"]
            print(wavelength, Tags[index], error[index], con_pmt)
            with open(CSV_Relative_Error, mode="a", newline="") as file:
                writer = csv.writer(file)
                for ang, re_err in zip(mc_angle, re_error[index]):
                    writer.writerow([distance, wavelength, f"{Tags[index]}", ang, re_err])    
    # Plot
    # # Ratio
        # angle, con_pmt, con_pmt_error = Compute_Shifted_Line(distance, wavelength, 0, data_angle , 0, angle_cut_off)
        angle, con_pmt, con_pmt_error = Compute_Shifted_Line(distance, wavelength, 0, mc_angle , 0, angle_cut_off)
        plt.errorbar(angle, con_pmt, yerr=con_pmt_error, color=f"red", label=f"MC: 0")
        for index in range(len(Angle_Shifts)):
            angle_shift = Angle_Shifts[index]
            # angle, con_pmt, con_pmt_error = Compute_Shifted_Line(distance, wavelength, angle_shift, data_angle , 0, angle_cut_off)
            angle, con_pmt, con_pmt_error = Compute_Shifted_Line(distance, wavelength, angle_shift, mc_angle , 0, angle_cut_off)
            plt.errorbar(angle, con_pmt, yerr=con_pmt_error, color=f"C{index}", label=f"MC:{angle_shift}")
        plt.legend()
        # plt.show()
        pic_path = pic_dir + f"/L{distance}_{wavelength}_Ratio.jpg"
        plt.savefig(pic_path, dpi=500)
        plt.close()
    # # Relative Error
        plt.figure(figsize=(10, 8))
        data_angle = mc_angle
        plt.plot(data_angle, re_error[0], label="MC: +1")
        plt.plot(data_angle, re_error[1], label="MC: +2")
        plt.plot(data_angle, re_error[2], label="MC: +4")
        plt.plot(data_angle, re_error[3], label="MC: +5")
        plt.title(f"L{distance}_{wavelength}")
        plt.xlabel("Angle/deg")
        plt.ylabel("Relative Error")
        plt.ylim(0, 1)
        plt.grid(True, which='both', linestyle='--', linewidth=1.5)
        plt.legend()
        # plt.show()
        pic_path = pic_dir + f"/L{distance}_{wavelength}_Ratio_Relative_Error.jpg"
        plt.savefig(pic_path, dpi=500)
    with open(CSV_Relative_Error, 'rb+') as file:
            file.seek(-2, os.SEEK_END)
            file.truncate() 
# # 估算半径变化带来的误差
def Compute_MC_Systematic_Error_Radius_Shift(distance, angle_shift, sys_error = 0.00, angle_cut_off = 0):
    CSV_Dir = f"/mnt/e/PMT/Radius_Shift/L{distance}/R_"
    # Dirs = ["N1", "N2", "N3", "P1", "P2", "P3"]
    Dirs = ["N1", "P1"]
    length = len(Dirs)
    Wavelengths = [365, 415, 465, 480]
    # Record CSV
    CSV_Relative_Error = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_Radius_Shift.csv"
    print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Radius_Shift] The result is save in {CSV_Relative_Error}")
    header = ['distance','led','tag', 'angle', 'relative_error']
    with open(CSV_Relative_Error, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
    for ii1 in range(len(Wavelengths)):
        wavelength = Wavelengths[ii1]
        Angles_PMT = [[] for _ in range(length)]
        Angles_CON = [[] for _ in range(length)]
        Test_Cali_PMT = [[] for _ in range(length)]
        Test_Cali_CON = [[] for _ in range(length)]
        Test_Cali_Error_PMT = [[] for _ in range(length)]
        Test_Cali_Error_CON = [[] for _ in range(length)]
        Con_PMT = [[] for _ in range(length)]
        Con_PMT_Error = [[] for _ in range(length)]
        for ii2 in range(length):
            CSV_PMT_Dir = CSV_Dir + Dirs[ii2] + f"/CSV/L{distance}_{wavelength}_PMT.csv"
            CSV_CON_Dir = CSV_Dir + Dirs[ii2] + f"/CSV/L{distance}_{wavelength}_Con.csv"
            if distance == 1:
                data_pmt = pd.read_csv(CSV_PMT_Dir).iloc[:-1]
                data_con = pd.read_csv(CSV_CON_Dir).iloc[:-1]
            elif distance == 2:
                data_pmt = pd.read_csv(CSV_PMT_Dir)
                data_con = pd.read_csv(CSV_CON_Dir)
            data_pmt = data_pmt.apply(pd.to_numeric, errors='coerce')
            data_con = data_con.apply(pd.to_numeric, errors='coerce')
            # 用0代替Nan
            data_pmt.fillna(0, inplace=True)
            data_con.fillna(0, inplace=True)
            # Compute
            ratio = (data_con["ratio"] / data_pmt["ratio"])
            ratio_error = ratio * np.sqrt((data_con["ratio_error"] / data_con["ratio"])**2 + (data_pmt["ratio_error"] / data_pmt["ratio"])**2 + sys_error**2)
            # Record Data
            Angles_PMT[ii2] = (3 + data_pmt["angle"]).values
            Angles_CON[ii2] = (3 + data_con["angle"]).values
            Test_Cali_PMT[ii2] = data_pmt["ratio"].values
            Test_Cali_CON[ii2] = data_con["ratio"].values
            Test_Cali_Error_PMT[ii2] = data_pmt["ratio_error"].values
            Test_Cali_Error_CON[ii2] = data_con["ratio_error"].values
            Con_PMT[ii2] = ratio.values
            Con_PMT_Error[ii2] = ratio_error.values
    # Plot PMT Data
        Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/MC/Radius_Shift/L{distance}"
        print(f"[Collect_MC_Info::Compute_MC_Systematic_Error_Radius_Shift] Pics are save in {Pic_Dir}")
        plt.figure(figsize=(10, 8))
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 0)
        plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Data")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                        color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 0, 0, 0)
        plt.plot(angle, test_cali, linestyle="--", color="gray", linewidth=1.5, label="Standard")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                        color="gray", alpha=0.3, label=r"Standard: Mean $\pm$ Error")
        for ii2 in range(length):
            plt.errorbar(Angles_PMT[ii2], Test_Cali_PMT[ii2], yerr=Test_Cali_Error_PMT[ii2],
                        fmt='o', capsize=5, capthick=1,
                        label=f'{Dirs[ii2]}', color=f'C{ii2}')
        plt.title(f"Radius Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Test/Cali")
        plt.ylim(0, 2.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 2.5, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_PMT.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot CON Data
        plt.figure(figsize=(10, 8))
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 1)
        plt.plot(angle, test_cali, linestyle="--", color="black", linewidth=1.5, label="Data")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                        color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
        angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 1, 0, 0)
        plt.plot(angle, test_cali, linestyle="--", color="gray", linewidth=1.5, label="Standard")
        plt.fill_between(angle, test_cali - test_cali_error, test_cali + test_cali_error,
                        color="gray", alpha=0.3, label=r"Mean $\pm$ Error")
        for ii2 in range(length):
            plt.errorbar(Angles_CON[ii2], Test_Cali_CON[ii2], yerr=Test_Cali_Error_CON[ii2],
                        fmt='o', capsize=5, capthick=1,
                        label=f'{Dirs[ii2]}', color=f'C{ii2}')
        plt.title(f"Radius Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Test/Cali")
        plt.ylim(0, 4.5)
        plt.xlim(-5, 95)
        y_ticks = np.arange(0, 4.5, 0.25)
        plt.yticks(y_ticks)
        x_ticks = np.arange(-5, 96, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_CON.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Plot Con/PMT
        plt.figure(figsize=(10, 8))
        angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2)
        angle = angle[angle <= angle_cut_off]
        con_pmt = con_pmt[:len(angle)]
        con_pmt_error = con_pmt_error[:len(angle)]
        plt.plot(angle, con_pmt, linestyle="--", color="black", linewidth=1.5, label="Data")
        plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
                        color="black", alpha=0.3, label=r"Data: Mean $\pm$ Error")
        # con_pmt_shift = con_pmt[-1]
        angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, angle_shift, 0, angle_cut_off)
        angle = angle[angle <= angle_cut_off]
        con_pmt = con_pmt[:len(angle)]
        con_pmt_error = con_pmt_error[:len(angle)]
        plt.plot(angle, con_pmt, linestyle="--", color="gray", linewidth=1.5, label="Standard")
        plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
                        color="gray", alpha=0.3, label=r"Mean $\pm$ Error")
        for ii2 in range(length):
            plt.errorbar(Angles_CON[ii2][:15], Con_PMT[ii2][:15], yerr=Con_PMT_Error[ii2][:15],
                        fmt='o', capsize=5, capthick=1,
                        label=f'{Dirs[ii2]}', color=f'C{ii2}')
        plt.title(f"Radius Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Con/PMT")
        plt.ylim(0, 2.5)
        plt.xlim(0, 70)
        y_ticks = np.arange(0, 2.6, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(0, 70, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_Ratio.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    # Relative Error
        plt.figure(figsize=(10, 8))
        angle, std_con_pmt, std_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, 0)
        angle = angle[angle <= angle_cut_off]
        std_con_pmt = std_con_pmt[:len(angle)]
        for ii2 in range(length):
            relative_error = np.abs((std_con_pmt - Con_PMT[ii2][:len(std_con_pmt)]) / std_con_pmt)
            plt.plot(angle, relative_error, label=f"{Dirs[ii2]}", color=f"C{ii2}")
            # Write in CSV
            with open(CSV_Relative_Error, mode="a", newline="") as file:
                writer = csv.writer(file)
                for ang, re_err in zip(angle, relative_error):
                    writer.writerow([distance, wavelength, Dirs[ii2], ang, re_err])
        plt.title(f"Radius Shift: {wavelength} nm")
        plt.xlabel("Angle/deg")
        plt.ylabel("Relative Error")
        plt.ylim(0, 1)
        plt.xlim(0, 70)
        y_ticks = np.arange(0, 1, 0.05)
        plt.yticks(y_ticks)
        x_ticks = np.arange(0, 70, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        Pic_Path = Pic_Dir + f"/L{distance}_{wavelength}_Ratio_Relative_Error.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
    with open(CSV_Relative_Error, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate()
# # 计算Z、Angle、Radius带来的误差，并写进CSV文件中
def Compute_Total_Systematic_Relative_Error(distance, angle_cut_off):
    print(f"[Collect_MC_Info::Compute_Total_Systematic_Relative_Error] Processing Total Relative Error of distance {distance}")
    CSV_Dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error"
    CSV_Relative_Error = CSV_Dir + f"/L{distance}/L{distance}_Total_Relative_Error.csv"
    header = ['distance', 'led', 'tag', 'angle', 'relative_error']
    with open(CSV_Relative_Error, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
    Wavelengths = [365, 415, 465, 480]
    for wavelength in Wavelengths:
        Names = ["Angle_Shift", "Radius_Shift", "Z_Shift"]
        Relative_Error = [[] for _ in range(len(Names))]
        Max_Tag = ""
        for ii1 in range(len(Names)):
            name = Names[ii1]
            if name != "Angle_Shift":
                Tags = ["P1", "N1"]
            elif name == "Angle_Shift":
                Tags = ["N2", "P2"]
            CSV_Path = CSV_Dir + f"/L{distance}/L{distance}_{Names[ii1]}.csv"
            data = pd.read_csv(CSV_Path)
            data = data[data["led"] == wavelength]
            data = data[data["angle"] <= angle_cut_off]
            max = -999
            max_index = 0
            for ii2 in range(len(Tags)):
                tag = Tags[ii2]
                temp_data = data[data["tag"] == Tags[ii2]].reset_index(drop=True)
                if (np.mean(temp_data["relative_error"]) > max):
                    max = np.mean(temp_data["relative_error"])
                    max_index = ii2
                    Relative_Error[ii1] = temp_data
            # 更新Tag
            Max_Tag = Max_Tag + Tags[max_index]
        # Compute Total Systemic Error
        Total_Systemic_Error = np.sqrt( sum((Relative_Error[ii1]["relative_error"]) **2 for ii1 in range(len(Names))))
        Total_Systemic_Error = np.clip(Total_Systemic_Error, None, 1)  # 限制最大值为 1
        # Write in CSV File
        with open(CSV_Relative_Error, mode="a", newline="") as file:
            writer = csv.writer(file)
            for angle, re_er in zip(temp_data["angle"], Total_Systemic_Error):
                writer.writerow([distance, wavelength, Max_Tag, angle, re_er])
    with open(CSV_Relative_Error, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate()
# # 拿到MC的系统误差
def Get_Total_Systemic_Relative_Error(distance, wavelength):
    CSV_Relative_Error = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_Total_Relative_Error.csv"
    data = pd.read_csv(CSV_Relative_Error)
    data = data[data["led"] == wavelength].reset_index(drop=True)
    Relative_Error = np.array(data["relative_error"].values)
    # Output
    return Relative_Error
# # 将各系统误差和总系统误差回到一块
def Plot_Relative_Errors(distance):
    CSV_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_"
    Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/MC/Other/"
    Wavelengths = [365, 415, 465, 480]
    for wavelength in Wavelengths:
        print(f"[Plot_Relative_Errors] Plot Distance {distance}, Wavelength {wavelength}" )
        plt.figure(figsize=(10, 8))
        Names = ["Total_Relative_Error", "Z_Shift", "Angle_Shift", "Radius_Shift"]
        Tags = [0 for _ in range(len(Names) - 1)]
        for index in range(len(Names)):
            name = Names[index]
            CSV_File_Path = CSV_Dir + f"{name}.csv"
            data = pd.read_csv(CSV_File_Path)
            data = data[data['led'] == wavelength].reset_index(drop=True)
            if index >= 1:
                tag = Tags[index - 1]
                data = data[data['tag'] == tag].reset_index(drop=True)
            angles = data["angle"].values
            relative_error = data["relative_error"].values
            ###### Tags
            if name == "Total_Relative_Error":
                Tags[0] = data['tag'][0][:2]
                Tags[1] = data['tag'][0][2:4]
                Tags[2] = data['tag'][0][4:6]
            plt.plot(angles, relative_error, color=f'C{index}', label=f'{name}')

        # plt.title(f"Relative Error of {wavelength}")
        plt.xlabel("Angle/deg", fontsize = 14)
        plt.ylabel("Relative Error", fontsize = 14)
        x_ticks = np.arange(0, 70, 5)
        plt.xticks(x_ticks)
        y_ticks = np.arange(0, 1.1, 0.1)
        plt.yticks(y_ticks)
        plt.xlim(0, 70)
        plt.ylim(0, 1.1)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend(fontsize = 14)
        # plt.show()
        Pic_Path = Pic_Dir + f"L{distance}_{wavelength}_Relative_Error.jpg"
        plt.savefig(Pic_Path, dpi=500)
        plt.close()
# 将所有波长的总相对误差画到一起
def Plot_Total_Relative_Erros(distance):
    CSV_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Relative_Error/L{distance}/L{distance}_"
    Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/MC/Other/"
    Wavelengths = [365, 415, 465, 480]
    plt.figure(figsize=(10, 8))
    for ii1 in range(len(Wavelengths)):
        wavelength = Wavelengths[ii1]
        print(f"[Plot_Relative_Errors] Plot Distance {distance}, Wavelength {wavelength}" )
        Names = ["Total_Relative_Error"]
        Tags = [0 for _ in range(len(Names) - 1)]
        for index in range(len(Names)):
            name = Names[index]
            CSV_File_Path = CSV_Dir + f"{name}.csv"
            data = pd.read_csv(CSV_File_Path)
            data = data[data['led'] == wavelength].reset_index(drop=True)
            angles = data['angle'].values
            relative_error = data["relative_error"].values
        plt.plot(angles, relative_error, color=f'C{ii1}', label=f'{wavelength}')
    plt.xlabel("Angle/deg", fontsize = 20)
    plt.ylabel("Relative Error", fontsize = 20)
    x_ticks = np.arange(0, 75, 5)
    plt.xticks(x_ticks)
    y_ticks = np.arange(0, 1.1, 0.1)
    plt.yticks(y_ticks)
    plt.xlim(0, 75)
    plt.ylim(0, 1.1)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend(fontsize = 20)
    # plt.show()
    Pic_Path = Pic_Dir + f"L{distance}_Relative_Error.jpg"
    plt.savefig(Pic_Path, dpi=500)
    plt.close()