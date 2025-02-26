import h5py
import os
import glob
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd # 处理csv
import argparse # 传参
import sys
import os
sys.path.append("/home/penguin/Jinping/JSAP-install/Codes/Heads")
sys.path.append("/home/penguin/PMTAnalysis")
# Self-Defined
import Head_Base_Functions
import Head_Collect_Data_Info
import Head_Collect_MC_Info
import Rough_Analysis

def Plot_Concentrator():
    Wavelengths = [365, 415, 465, 480]
    for wavelength in Wavelengths:
        plt.figure(figsize=(10, 8))
        for distance in range(1, 3):
            if distance == 1:
                fmt='o'
            elif distance == 2:
                fmt='s'
            data_total_sys_error = Head_Collect_Data_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
            data_angle, data_con_pmt, data_con_pmt_error = Head_Base_Functions.Get_Data(distance, wavelength, 2, data_total_sys_error)
            plt.errorbar(data_angle, data_con_pmt, yerr=data_con_pmt_error,
                        fmt=fmt, capsize=5, capthick=1,
                        color=f'C{distance + 3}', label=f"Data: L{distance}")
            con_pmt_shift = data_con_pmt[-1]
            mc_total_sys_error = Head_Collect_MC_Info.Get_Total_Systemic_Relative_Error(distance, wavelength)
            mc_angle, mc_con_pmt, mc_con_pmt_error = Head_Base_Functions.Get_Standard(distance, wavelength, 2, mc_total_sys_error)
            mc_con_pmt = mc_con_pmt + con_pmt_shift
            plt.errorbar(mc_angle, mc_con_pmt, yerr=mc_con_pmt_error,
                        fmt=fmt, capsize=5, capthick=1,
                        color=f'C{distance}', label=f"MC: L{distance}")
        plt.xlabel("Angle/deg")
        plt.ylabel("Concentration Factor")
        plt.ylim(0, 2.5)
        plt.xlim(-5, 92)
        y_ticks = np.arange(0, 2.5, 0.2)
        plt.yticks(y_ticks)
        x_ticks = np.arange(0, 95, 5)
        plt.xticks(x_ticks)
        plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
        plt.legend()
        # plt.show()
        pic_path = f"/home/penguin/PMTAnalysis/Pics/Paper/Concentration_Factor_{wavelength}.jpg"
        plt.savefig(pic_path, dpi=500)

def Plot_Original_Waves():
    no = 363
    wavelength = 415
    file_path = f"/home/penguin/PMTAnalysis/Data/0.h5"
    file = Rough_Analysis.loadH5(file_path)
    # 声明变量
    time = []
    amplitude = []
    # 循环
    waves_ch0 = file[29][0]
    waves_ch1 = 300 + file[4938][1]
    # for index in tqdm(range(file.shape[0])):
    #     channel = 1
    #     waves = file[index]
    #     wave = waves[channel]
        # if (np.max(wave) - np.mean(wave) > 50):
        #     print(index)
        #     exit()
    plt.figure(figsize=(10, 8))
    plt.plot(waves_ch0, color='blue', label="Cali PMT")
    plt.plot(waves_ch1, color='red', label="Test PMT")
    plt.xlabel("Times/ns", fontsize=30)
    plt.ylabel("ADC", fontsize=30)
    plt.xlim(-10, 1010)
    plt.ylim(275, 410)
    x_ticks = range(0, 1010, 100)
    plt.xticks(x_ticks)
    y_ticks = range(280, 410, 10)
    plt.yticks(y_ticks)
    plt.tick_params(axis='both', which='major', labelsize=20)
    plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=30) # 图例文字大小
    # plt.show()
    Pic_Path = f"/home/penguin/PMTAnalysis/Pics/Paper/L1_{wavelength}_Original_Wave_ch0_ch1.jpg"
    plt.savefig(Pic_Path, dpi=500)
    
def Plot_Peak_Time_Distribution_After_Pedestal_Cut():
    no = 363
    wavelength = 415
    pic_dir = f"/home/penguin/PMTAnalysis/Pics/Paper/L1_{wavelength}"
    verbose = [1, 0, 1, f"{pic_dir}"]
    all_waves = []
    for index in range(11):
        file_path = f"/home/penguin/PMTAnalysis/Data/{index}.h5"
        print(f"[Plot_Peak_Time_Distribution_After_Pedestal_Cut] Load {file_path}")
        file = Rough_Analysis.loadH5(file_path)
        all_waves.append(file)
    file = np.concatenate(all_waves, axis=0)
    # 声明变量
    baseline_array_ch0 = []
    baseline_array_ch1 = []
    peak_am_array_ch0 = []
    peak_am_array_ch1 = []
    peak_time_array_ch0 = []
    peak_time_array_ch1 = []
    # 处理、记录数据
    for index in tqdm(range(file.shape[0])):
        waves = file[index]
        for channel in range(2):
            if channel == 1:
                wave = 500 + waves[channel] # 平移，方便后续处理
            else:
                wave = waves[channel]
            # # 处理baseline
            rough_mean = np.mean(wave)
            # # 记录基线
            if channel == 0:
                baseline_array_ch0.append(rough_mean)
            else:
                baseline_array_ch1.append(rough_mean)
            # # 剪掉基线
            wave = wave - rough_mean
            # # 统计peak的ADC分布和时间分布
            if channel == 0: wave = - wave # ch0的peak会小于零，在此整体反转，便于后续统一分析
            peak_am = np.max(wave)
            peak_time = np.argmax(wave)
            if channel == 0:
                peak_am_array_ch0.append(peak_am)
                peak_time_array_ch0.append(peak_time)
            else:
                peak_am_array_ch1.append(peak_am)
                peak_time_array_ch1.append(peak_time)
    # 处理两个channel
    Peak_Time_After_Filted_ch0 = []
    Peak_Time_After_Filted_ch1 = []
    Peak_Time_Fit_Range_ch0 = []
    Peak_Time_Fit_Range_ch1 = []
    Means = [0 for _ in range(2)]
    Sigmas = [0 for _ in range(2)]
    for channel in range(2):
        if channel == 0:
            baseline = np.array(baseline_array_ch0)
            peak_am_array = np.array(peak_am_array_ch0)
            peak_time_array = np.array(peak_time_array_ch0)
        else:
            baseline = np.array(baseline_array_ch1)
            peak_am_array = np.array(peak_am_array_ch1)
            peak_time_array = np.array(peak_time_array_ch1)
        # # 基线统计
        rough_mean = np.mean(baseline)
        rough_sigma = np.std(baseline)
        bounds = [(rough_mean - 3 * rough_sigma, rough_mean + 3 * rough_sigma), (0.001, 3 * rough_sigma)]
        res = Rough_Analysis.gausfit(x0=[rough_mean, rough_sigma], args=baseline, bounds=bounds)
        baseline_fitted_mean, baseline_fitted_sigma = res.x
        # # Pedestal统计
        pedestal_rough_cut = 18
        small_peak = peak_am_array[peak_am_array < 2 * pedestal_rough_cut]
        rough_mean = np.mean(small_peak)
        rough_sigma = np.std(small_peak)
        res = Rough_Analysis.gausfit(x0=[rough_mean,rough_sigma], args=small_peak, bounds=[(0, rough_mean + 5 * rough_mean),(0.001, 5 * rough_sigma)])
        pedestal_fitted_mean, pedestal_fitted_sigma = res.x
        # # Signal时间窗统计
        pedestal_cut = pedestal_fitted_mean + 5 * pedestal_fitted_sigma
        condition = peak_am_array > pedestal_cut
        filtered_peak_time_array = peak_time_array[condition]
        if wavelength == 365:
            time_range = [500, 750]
        elif wavelength == 415:
            time_range = [250, 400]
        elif wavelength == 465 or wavelength == 480:
            time_range = [300, 700]
        elif wavelength == 0:
            time_range = [800, 900]
        filtered_peak_time_array_all_range = filtered_peak_time_array
        filtered_peak_time_array = filtered_peak_time_array[(filtered_peak_time_array > time_range[0]) & (filtered_peak_time_array < time_range[1])]
        rough_mean = np.mean(filtered_peak_time_array)
        rough_sigma = np.std(filtered_peak_time_array)
        bounds=[(rough_mean - 3 * rough_sigma, rough_mean + 3 * rough_sigma), (0.001, 5 * rough_sigma)]
        res = Rough_Analysis.gausfit(x0=[rough_mean, rough_sigma], args=filtered_peak_time_array, bounds=bounds)
        signal_fitted_mean, signal_fitted_sigma = res.x 
        # Record
        if channel == 0:
            Peak_Time_After_Filted_ch0 = filtered_peak_time_array_all_range
            Peak_Time_Fit_Range_ch0 = filtered_peak_time_array
            Means[0] = signal_fitted_mean
            Sigmas[0] = signal_fitted_sigma
        elif channel == 1:
            Peak_Time_After_Filted_ch1 = filtered_peak_time_array_all_range
            Peak_Time_Fit_Range_ch1 = filtered_peak_time_array
            Means[1] = signal_fitted_mean
            Sigmas[1] = signal_fitted_sigma
    # 画图
    plt.figure(figsize=(10, 8))
    plt.hist(Peak_Time_After_Filted_ch0, histtype='step', bins=1000, color='blue', label="Cali PMT")
    plt.hist(Peak_Time_After_Filted_ch1, histtype='step', bins=1000, color='red', label="Test PMT")
    plt.xlabel("Time/ns", fontsize=30)
    plt.ylabel("Entries", fontsize=30)
    x_ticks = range(0, 1000, 100)
    plt.xticks(x_ticks)
    # y_ticks = range(0, 1e4, )
    # plt.yticks(y_ticks)
    plt.tick_params(axis='both', which='major', labelsize=20)
    plt.xlim(1, 998)
    plt.ylim(1, 1e4)
    plt.yscale('log')
    plt.legend(fontsize=30)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    # plt.show()
    pic_path = pic_dir + f"_Rough_Peak_Time_Distribution_All_ch0_ch1.jpg"
    plt.savefig(pic_path, dpi=500)

def Plot_Peak_Amplitude_Time_Distribution():
    no = 363
    wavelength = 415
    pic_dir = f"/home/penguin/PMTAnalysis/Pics/Paper/L1_{wavelength}"
    verbose = [1, 0, 1, f"{pic_dir}"]
    all_waves = []
    for index in range(2):
        file_path = f"/home/penguin/PMTAnalysis/Data/{index}.h5"
        print(f"[Plot_Peak_Time_Distribution_After_Pedestal_Cut] Load {file_path}")
        file = Rough_Analysis.loadH5(file_path)
        all_waves.append(file)
    file = np.concatenate(all_waves, axis=0)
    # 声明变量
    baseline_array_ch0 = []
    baseline_array_ch1 = []
    peak_am_array_ch0 = []
    peak_am_array_ch1 = []
    peak_time_array_ch0 = []
    peak_time_array_ch1 = []
    # 处理、记录数据
    for index in tqdm(range(file.shape[0])):
        waves = file[index]
        for channel in range(2):
            if channel == 1:
                wave = 500 + waves[channel] # 平移，方便后续处理
            else:
                wave = waves[channel]
            # # 处理baseline
            rough_mean = np.mean(wave)
            # # 记录基线
            if channel == 0:
                baseline_array_ch0.append(rough_mean)
            else:
                baseline_array_ch1.append(rough_mean)
            # # 剪掉基线
            wave = wave - rough_mean
            # # 统计peak的ADC分布和时间分布
            if channel == 0: wave = - wave # ch0的peak会小于零，在此整体反转，便于后续统一分析
            peak_am = np.max(wave)
            peak_time = np.argmax(wave)
            if channel == 0:
                peak_am_array_ch0.append(peak_am)
                peak_time_array_ch0.append(peak_time)
            else:
                peak_am_array_ch1.append(peak_am)
                peak_time_array_ch1.append(peak_time)

    # 画图---Amplitude Distribution
    plt.figure(figsize=(10, 8))
    plt.hist(peak_am_array_ch0, histtype='step', bins=1000, color='blue', label="Cali PMT")
    plt.hist(peak_am_array_ch1, histtype='step', bins=1000, color='red', label="Test PMT")
    plt.xlabel("Amplitude/ADC", fontsize=30)
    plt.ylabel("Entries", fontsize=30)
    x_ticks = range(0, 1000, 100)
    plt.xticks(x_ticks)
    # y_ticks = range(0, 1e4, )
    # plt.yticks(y_ticks)
    plt.tick_params(axis='both', which='major', labelsize=20)
    plt.xlim(0, 1000)
    plt.ylim(1, 5e5)
    plt.yscale('log')
    plt.legend(fontsize=30)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    # plt.show()
    pic_path = pic_dir + f"_Rough_Peak_Amplitude_Distribution_All_ch0_ch1.jpg"
    plt.savefig(pic_path, dpi=500)

    # 画图--Time Distribution
    plt.figure(figsize=(10, 8))
    plt.hist(peak_time_array_ch0, histtype='step', bins=1000, color='blue', label="Cali PMT")
    plt.hist(peak_time_array_ch1, histtype='step', bins=1000, color='red', label="Test PMT")
    plt.xlabel("Time/ns", fontsize=30)
    plt.ylabel("Entries", fontsize=30)
    x_ticks = range(0, 1000, 100)
    plt.xticks(x_ticks)
    # y_ticks = range(0, 1e4, )
    # plt.yticks(y_ticks)
    plt.tick_params(axis='both', which='major', labelsize=20)
    plt.xlim(0, 1000)
    plt.ylim(3e1, 2e3)
    plt.yscale('log')
    plt.legend(fontsize=30)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
    # plt.show()
    pic_path = pic_dir + f"_Original_Peak_Time_Distribution_All_ch0_ch1.jpg"
    plt.savefig(pic_path, dpi=500)

# 绘制Baselinevs时间。但是数据太多，效果太差，放弃
def Plot_Baseline():
    ################# Baseline
    CSV_File_Path = "/home/penguin/PMTAnalysis/Run.csv"
    data = pd.read_csv(CSV_File_Path)
    data = data[data["quality"] == "1"]
    data = data[data["pmt1"] == 1015]
    data = data[data["led"] != "---"]
    # data = data.reset_index(True)
    Dates = data["date"].values
    Baseline_ch0 = data["weighted_ch0_baseline_mean"].values
    Baseline_Error_ch0 = data["weighted_ch0_baseline_sigma"].values
    # Plot
    plt.figure(figsize=(10, 8))
    plt.errorbar(Dates, Baseline_ch0, yerr=Baseline_Error_ch0, fmt='o', capsize=5)
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))  # 限制最多 10 个刻度
    plt.xticks(rotation=90)  # 旋转以防止重叠
    plt.show()