# Python
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.optimize import minimize
import pandas as pd # 处理csv
import sys
import os
import csv
# Self-Defined
import Head_Base_Functions
import Head_Collect_Data_Info
import Head_Collect_MC_Info
# Function

# 根据轨道和波长绘制MC和Data的Test/Cali和Con/PMT
def Plot_Data_MC(distance, wavelength, sys_mc_re_error, sys_data_re_error):
    Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Res" + f"/L{distance}"
    print(f"[Plot::Plot_Data_MC] Distance {distance}, Wavelength {wavelength}: All pics are saved in {Pic_Dir}")
    # Plot: Test/Cali
    plt.figure(figsize=(10, 8))
    # # Data
    angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 0, 0)
    plt.errorbar(angle, test_cali, yerr=test_cali_error,
                 fmt='o', capsize=5, capthick=1,
                 color='blue', label="Data: PMT")
    angle, test_cali, test_cali_error = Head_Base_Functions.Get_Data(distance, wavelength, 1, 0)
    plt.errorbar(angle, test_cali, yerr=test_cali_error,
                 fmt='o', capsize=5, capthick=1,
                 color='blue', label="Data: Con")
    # # MC
    angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 0, 0)
    plt.errorbar(angle, test_cali, yerr=test_cali_error,
                 fmt='o', capsize=5, capthick=1,
                 color='red', label="MC: PMT")
    angle, test_cali, test_cali_error = Head_Base_Functions.Get_Standard(distance, wavelength, 1, 0)
    plt.errorbar(angle, test_cali, yerr=test_cali_error,
                 fmt='o', capsize=5, capthick=1,
                 color='red', label="MC: CON")
    plt.title(f"L{distance}_{wavelength}")
    plt.xlabel("Angle/deg")
    plt.ylabel("Test/Cali")
    plt.ylim(0, 5)
    plt.xlim(-5, 95)
    y_ticks = np.arange(0, 5, 0.5)
    plt.yticks(y_ticks)
    x_ticks = np.arange(-5, 96, 5)  # 从-5到95，步长为5
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend()
    # plt.show()
    pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Test_Cali.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()
    # # Con/PMT
    plt.figure(figsize=(10, 8))
    angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, 3, sys_data_re_error)
    plt.errorbar(angle, con_pmt, yerr=con_pmt_error,
                 fmt='o', capsize=5, capthick=1,
                 color='blue', label="Data")
    # con_pmt_shift = con_pmt[-1]
    angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error)
    # con_pmt = con_pmt + con_pmt_shift
    plt.errorbar(angle, con_pmt, yerr=con_pmt_error,
                 fmt='o', capsize=5, capthick=1,
                 color='red', label="MC")
    plt.title(f"L{distance}_{wavelength}")
    plt.xlabel("Angle/deg")
    plt.ylabel("Con/PMT")
    plt.ylim(0, 2.5)
    plt.xlim(0, 75)
    y_ticks = np.arange(0, 2.6, 0.2)
    plt.yticks(y_ticks)
    x_ticks = np.arange(0, 75, 5)  # 从-5到95，步长为5
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend()
    # plt.show()
    pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Con_PMT.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()
    
    # # CON/PMT 和 Ratio
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.05)  # 上图3份高度，下图1份 
    ax1 = plt.subplot(gs[0])
    angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, sys_data_re_error)
    ax1.errorbar(angle, con_pmt, yerr=con_pmt_error, fmt='o', capsize=5, capthick=1, color='blue', label="Data")
    angle, mc_con_pmt, mc_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error)
    ax1.errorbar(angle, mc_con_pmt, yerr=mc_con_pmt_error, fmt='o', capsize=5, capthick=1, color='red', label="MC")
    ax1.set_ylabel("Con/PMT")
    ax1.set_xlim(0, 75)
    ax1.set_ylim(0, 2.5)
    ax1.set_xticks(np.arange(0, 75, 5))
    ax1.set_yticks(np.arange(0, 2.6, 0.2))
    ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
    ax1.legend()
    ax1.set_title(f"L{distance}_{wavelength}")
    # 下图：比值图
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ratio = con_pmt / mc_con_pmt  # 计算比值
    ratio_error = ratio * np.sqrt((con_pmt_error / con_pmt) ** 2 + (mc_con_pmt_error / mc_con_pmt) ** 2)  # 误差传播

    ax2.errorbar(angle, ratio, yerr=ratio_error, fmt='o', capsize=5, capthick=1, color='black', label="Data/MC")
    ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1)  # 参考线 y=1
    ax2.set_ylabel("Data/MC")
    ax2.set_xlabel("Angle/deg")
    ax2.set_xlim(-5, 95)
    ax2.set_ylim(0, 1.6)
    ax2.set_yticks(np.arange(0, 1.6, 0.2))
    ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
    pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Con_PMT_Ratio.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()
def Plot_Data_MC_V2(distance, wavelength, sys_mc_re_error, sys_data_re_error):
    Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Res" + f"/L{distance}"
    print(f"[Plot::Plot_Data_MC] Distance {distance}, Wavelength {wavelength}: All pics are saved in {Pic_Dir}")
    # # Con/PMT
    plt.figure(figsize=(10, 8))
    angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, sys_data_re_error)
    length = len(angle[angle <= 70])
    print(length)
    plt.errorbar(angle, con_pmt, yerr=con_pmt_error,
                    fmt='o', capsize=5, capthick=1,
                    color='blue', label="Data")
    # con_pmt_shift = con_pmt[-1]
    angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error[:length])
    # con_pmt = con_pmt + con_pmt_shift
    plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
                    color='green', alpha=0.3, label="MC")
    plt.title(f"L{distance}_{wavelength}")
    plt.xlabel("Angle/deg", fontsize = 20)
    plt.ylabel("Con/PMT", fontsize = 20)
    plt.ylim(0, 2.5)
    plt.xlim(-2, 74)
    y_ticks = np.arange(0, 2.6, 0.2)
    plt.yticks(y_ticks)
    x_ticks = np.arange(0, 75, 5)  # 从-5到95，步长为5
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend(fontsize = 20)
    # plt.show()
    pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Con_PMT.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()

    # # CON/PMT 和 Ratio
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.0)  # 上图3份高度，下图1份 
    ax1 = plt.subplot(gs[0])
    data_angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, sys_data_re_error[:length])
    length = len(data_angle[angle <= 70])
    ax1.errorbar(data_angle[:length], con_pmt[:length], yerr=con_pmt_error[:length], fmt='o', capsize=5, capthick=1, color='blue', label="Data")
    angle, mc_con_pmt, mc_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error[:length])
    ax1.fill_between(angle[:length + 2], mc_con_pmt[:length + 2] - mc_con_pmt_error[:length + 2], mc_con_pmt[:length + 2] + mc_con_pmt_error[:length + 2],
                    color='green', alpha=0.3, label="MC")
    ax1.plot(angle, mc_con_pmt, color='green', alpha=0.3, linestyle='--')
    ax1.set_ylabel("Concentration Factor", fontsize = 20)
    ax1.set_xlabel("Angle/deg", fontsize = 20)
    ax1.set_xlim(-2, 74)
    ax1.set_ylim(0, 2.5)
    ax1.set_xticks(np.arange(0, 75, 5))
    ax1.set_yticks(np.arange(0, 2.6, 0.2))
    ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
    ax1.legend()
    ax1.set_title(f"L{distance}_{wavelength}")
    # 下图：比值图
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ratio = con_pmt / mc_con_pmt  # 计算比值
    ratio_error = ratio * np.sqrt((con_pmt_error / con_pmt) ** 2 + (mc_con_pmt_error / mc_con_pmt) ** 2)  # 误差传播

    ax2.errorbar(data_angle, ratio, yerr=ratio_error, fmt='o', capsize=5, capthick=1, color='black', label="Data/MC")
    ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1)  # 参考线 y=1
    ax2.set_ylabel("Ratio", fontsize = 20)
    ax2.set_xlabel("Angle/deg", fontsize = 20)
    ax2.set_xlim(-2, 74)
    ax2.set_ylim(0, 1.6)
    ax2.set_yticks(np.arange(0, 1.6, 0.2))
    ax2.set_xticks(np.arange(0, 75, 5))
    ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
    # plt.show()
    pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Con_PMT_Ratio.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()
# 绘制同一轨道下的所有波长
def Plot_Data_MC_All_Waves(distance):
    print(f"[Plot::Plot_Data_MC_All_Waves] Plot All waves in distance {distance}")
    Wavelengths = [365, 415, 465, 480]
    for wavelength in Wavelengths:
        data_relative_error = Head_Collect_Data_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
        mc_relative_error = Head_Collect_MC_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
        print(f"Wavelength {wavelength}, Data Systemic Relative Error: {data_relative_error}")
        print(f"Wavelength {wavelength}, MC Systemic Relative Error: {mc_relative_error}")
        Plot_Data_MC_V2(distance, wavelength, mc_relative_error , data_relative_error)
# 绘制同一轨道下所有波长：Data + MC，既有统计误差又有系统误差
def Plot_Data_MC_All_Waves_Errors(distance):
    Wavelengths = [365, 415, 465, 480]
    for wavelength in Wavelengths:
        sys_data_re_error = Head_Collect_Data_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
        sys_mc_re_error = Head_Collect_MC_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
        Pic_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Res" + f"/L{distance}"
        print(f"[Plot::Plot_Data_MC] Distance {distance}, Wavelength {wavelength}: All pics are saved in {Pic_Dir}")
        # # Con/PMT
        fontsize = 20
        plt.figure(figsize=(10, 8))
        angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, sys_data_re_error)
        length = len(angle[angle <= 70])
        plt.errorbar(angle, con_pmt, yerr=con_pmt_error,
                        fmt='o', capsize=5, capthick=1,
                        color='blue', label="Data")
        # con_pmt_shift = con_pmt[-1]
        angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error)
        # print(angle)
        # con_pmt = con_pmt + con_pmt_shift
        plt.fill_between(angle, con_pmt - con_pmt_error, con_pmt + con_pmt_error,
                        color='green', alpha=0.3, label="MC")
        # plt.title(f"L{distance}_{wavelength}")
        plt.xlabel("Angle/deg", fontsize = fontsize)
        plt.ylabel("Con/PMT", fontsize = fontsize)
        plt.ylim(0, 2.5)
        plt.xlim(-2, 74)
        y_ticks = np.arange(0, 2.6, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(0, 75, 5)  # 从-5到95，步长为5
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend(fontsize = fontsize)
        # plt.show()
        pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Con_PMT.jpg"
        plt.savefig(pic_path, dpi=500)
        plt.close()

        # # CON/PMT 和 Ratio
        fig = plt.figure(figsize=(10, 10))
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.0)  # 上图3份高度，下图1份 
        ax1 = plt.subplot(gs[0])
        data_angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, sys_data_re_error)
        length = len(data_angle[data_angle <= 70])
        ax1.errorbar(data_angle[:length], con_pmt[:length], yerr=con_pmt_error[:length], fmt='o', capsize=5, capthick=1, color='blue', label="Data")
        angle, mc_con_pmt, mc_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error)
        ax1.fill_between(angle, mc_con_pmt - mc_con_pmt_error, mc_con_pmt + mc_con_pmt_error,
                        color='green', alpha=0.3, label="MC")
        ax1.plot(angle, mc_con_pmt, color='green', alpha=0.3, linestyle='--')
        ax1.set_ylabel("Concentration Factor", fontsize = 30)
        ax1.set_xlabel("Angle/deg", fontsize = 30)
        ax1.set_xlim(-2, 74)
        ax1.set_ylim(0, 2.5)
        ax1.set_xticks(np.arange(0, 75, 5))
        ax1.set_yticks(np.arange(0, 2.6, 0.2))
        ax1.tick_params(axis='y', which='major', labelsize = fontsize)
        ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
        ax1.legend(fontsize = 30)
        # ax1.set_title(f"L{distance}_{wavelength}")
        # # 下图：比值图
        ax2 = plt.subplot(gs[1], sharex=ax1)
        mc_con_pmt = mc_con_pmt[:length]
        mc_con_pmt_error = mc_con_pmt_error[:length]
        con_pmt = con_pmt[:length]
        con_pmt_error = con_pmt_error[length]
        ratio = con_pmt / mc_con_pmt  # 计算比值
        ratio_error = ratio * np.sqrt((con_pmt_error / con_pmt) ** 2 + (mc_con_pmt_error / mc_con_pmt) ** 2)  # 误差传播

        ax2.errorbar(data_angle[:length], ratio, yerr=ratio_error, fmt='o', capsize=5, capthick=1, color='black', label="Data/MC")
        print(data_angle[:length])
        ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1)  # 参考线 y=1
        ax2.set_ylabel("Ratio", fontsize = 30)
        ax2.set_xlabel("Angle/deg", fontsize = 30)
        ax2.set_xlim(-2, 74)
        ax2.set_ylim(0.6, 1.4)
        ax2.set_yticks(np.arange(0.6, 1.4, 0.2))
        ax2.set_xticks(np.arange(0, 75, 5))
        ax2.tick_params(axis='both', which='major', labelsize = fontsize)
        ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
        # plt.show()
        pic_path = Pic_Dir + "/" + f"L{distance}_{wavelength}_Con_PMT_Ratio.jpg"
        plt.savefig(pic_path, dpi=500)
        plt.close()
        
def Plot_Data_MC_All_Waves_Errors_All_Distance():
    Wavelengths = [365, 415, 465, 480]
    for wavelength in Wavelengths:
        angle_cut_off = 70
        Data_Angles = [[] for _ in range(2)]
        Data_Con_PMT = [[] for _ in range(2)]
        Data_Con_PMT_Error = [[] for _ in range(2)]
        MC_Angles = [[] for _ in range(2)]
        MC_Con_PMT = [[] for _ in range(2)]
        MC_Con_PMT_Error = [[] for _ in range(2)]
        Ratio = [[] for _ in range(2)]
        Ratio_Error = [[] for _ in range(2)]
        for distance in range(1, 3):
            sys_data_re_error = Head_Collect_Data_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
            sys_mc_re_error = Head_Collect_MC_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
            # # Data
            data_angle, con_pmt, con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, sys_data_re_error)
            length = len(data_angle[data_angle <= angle_cut_off])
            Data_Angles[distance - 1] = data_angle[:length]
            Data_Con_PMT[distance - 1] = con_pmt[:length]
            Data_Con_PMT_Error[distance - 1] = con_pmt_error[:length]
            # # MC
            angle, mc_con_pmt, mc_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, 3, sys_mc_re_error)
            MC_Angles[distance - 1] = angle
            MC_Con_PMT[distance - 1] = mc_con_pmt
            MC_Con_PMT_Error[distance - 1] = mc_con_pmt_error
            # # Ratio
            mc_con_pmt = mc_con_pmt[:length]
            mc_con_pmt_error = mc_con_pmt_error[:length]
            con_pmt = con_pmt[:length]
            con_pmt_error = con_pmt_error[length]
            ratio = con_pmt / mc_con_pmt  # 计算比值
            ratio_error = ratio * np.sqrt((con_pmt_error / con_pmt) ** 2 + (mc_con_pmt_error / mc_con_pmt) ** 2)  # 误差传播
            Ratio[distance - 1] = ratio
            Ratio_Error[distance - 1] = ratio_error
        # Plot
        fontsize = 20
        fig = plt.figure(figsize=(10, 10))
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.0)  # 上图3份高度，下图1份 
        ax1 = plt.subplot(gs[0])
        ax1.set_title(f"{wavelength} nm", fontsize = 30)
        for index in range(2):
            if index == 0:
                color='blue'
            elif index == 1:
                color='red'
            ax1.errorbar(Data_Angles[index], Data_Con_PMT[index], yerr=Data_Con_PMT_Error[index], fmt='o', capsize=5, capthick=1, color=color, label=f"Data: L{index + 1}")
            if index == 0:
                color='green'
            elif index == 1:
                color='pink'
            ax1.fill_between(MC_Angles[index], MC_Con_PMT[index] - MC_Con_PMT_Error[index], MC_Con_PMT[index] + MC_Con_PMT_Error[index],
                            color=color, alpha=0.3, label=f"MC: L{index + 1}")
            ax1.plot(MC_Angles[index], MC_Con_PMT[index], color=color, alpha=0.3, linestyle='--')
        ax1.set_ylabel("Concentration Factor", fontsize = 30)
        ax1.set_xlabel("Angle/deg", fontsize = 30)
        # ax1.set_xlim(-2, 74)
        ax1.set_ylim(0, 2.5)
        ax1.set_xticks(np.arange(0, 75, 5))
        ax1.set_yticks(np.arange(0, 2.5, 0.2))
        ax1.tick_params(axis='y', which='major', labelsize = fontsize)
        ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
        ax1.legend(fontsize = 30)
        if wavelength == 365: tag = '(a)'
        elif wavelength == 415: tag = '(b)'
        elif wavelength == 465: tag = '(c)'
        elif wavelength == 480: tag = '(d)'
        ax1.text(0.02, 0.98, tag, transform=ax1.transAxes, fontsize=30, verticalalignment='top', horizontalalignment='left', weight='bold')
        # Ratio
        ax2 = plt.subplot(gs[1], sharex=ax1)
        for index in range(2):
            if index == 0:
                color='blue'
            elif index ==1:
                color='red'
            ax2.errorbar(Data_Angles[index], Ratio[index], yerr=Ratio_Error[index], fmt='o', capsize=5, capthick=1, color=color, label=f"L{index + 1}")
        ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1)  # 参考线 y=1
        ax2.set_ylabel("Data/MC", fontsize = 30)
        ax2.set_xlabel("Angle/deg", fontsize = 30)
        ax2.set_xlim(-2, 74)
        ax2.set_ylim(0.6, 1.4)
        ax2.set_yticks(np.arange(0.6, 1.4, 0.2))
        ax2.set_xticks(np.arange(0, 75, 5))
        ax2.tick_params(axis='both', which='major', labelsize = fontsize)
        ax2.grid(True, linestyle='--', color='gray', linewidth=0.5)
        ax2.legend(fontsize = 13)
        # plt.show()
        Pic_Path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Res" + f"/{wavelength}_Con_PMT.jpg"
        plt.savefig(Pic_Path, dpi = 500)
        plt.close()
        
def Plot_Parallel_Light(wavelength):
    CSV_Dir = "/mnt/e/PMT/Parallel_Light/01/CSV"

    CSV_PMT_Path = CSV_Dir + f"/{wavelength}_PMT.csv"
    CSV_Con_Path = CSV_Dir + f"/{wavelength}_Con.csv"
    data_pmt = pd.read_csv(CSV_PMT_Path)
    data_con = pd.read_csv(CSV_Con_Path)

    angles = data_pmt["angle"].values
    con_pmt = data_con["num_photon"] / data_pmt["num_photon"]
    con_pmt_error = con_pmt * np.sqrt(( data_con["num_error_photon"]/data_con["num_photon"])**2 + (data_pmt["num_error_photon"]/data_pmt["num_photon"])**2)


    # # CON/PMT 和 Ratio
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1], hspace=0.0)  # 上图3份高度，下图1份 
    ax1 = plt.subplot(gs[0])
    ax1.errorbar(angles, data_pmt["num_photon"], yerr=data_pmt["num_error_photon"], fmt='o', capsize=5, capthick=1,
                color='red', label='PMT')
    ax1.errorbar(angles, data_con["num_photon"], yerr=data_con["num_error_photon"], fmt='o', capsize=5, capthick=1,
                color='blue', label='Con')
    ax1.set_ylabel("Number of photon", fontsize = 14)
    ax1.set_xlabel("Angle/deg", fontsize = 14)
    ax1.set_xlim(-5, 95)
    ax1.set_ylim(0, 30000)
    ax1.set_xticks(np.arange(-5, 95, 5))
    ax1.set_yticks(np.arange(0, 30000, 2500))
    ax1.grid(True, linestyle='--', color='gray', linewidth=0.5)
    ax1.legend(fontsize = 14)
    # 下图：比值图
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax2.errorbar(angles, con_pmt, yerr=con_pmt_error, fmt='o', capsize=5, capthick=1)
    ax2.axhline(y=1, color='gray', linestyle='--', linewidth=1)  # 参考线 y=1
    ax2.set_ylabel("Concentration factor", fontsize = 14)
    ax2.set_xlabel("Angle/deg", fontsize = 14)
    ax2.set_xlim(-5, 95)
    ax2.set_ylim(0, 1.8)
    ax2.set_yticks(np.arange(0, 1.8, 0.2))
    ax2.set_xticks(np.arange(-5, 95, 5))
    ax2.grid(True, linestyle='--', color='black', linewidth=0.5)
    # plt.show()
    pic_path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Res/{wavelength}_Parallel_Light.jpg"
    plt.savefig(pic_path, dpi=500)