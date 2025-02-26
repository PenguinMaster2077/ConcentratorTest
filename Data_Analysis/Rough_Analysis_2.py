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

def loadH5(f):
    with h5py.File(f, 'r') as ipt: # 已可读模式打开文件f，
        waves = ipt['Readout/Waveform'][:] # 读取Waveform下的所有数据
    return waves # 类型：numpy.ndarray
def Lgaussian(x0, A):
    mu, sigma = x0
    return np.sum(((A - mu) / sigma) ** 2) + A.shape[0] * np.log(sigma)
def gausfit(x0, args, bounds):
    return minimize(
            Lgaussian,
            x0=x0,
            args=args,
            bounds=bounds,
        )
    
def Baseline_Gausfit(baseline_array):
    baseline_array = np.array(baseline_array)
    rough_mean = np.mean(baseline_array)
    rough_sigma = np.std(baseline_array)
    range = [rough_mean - 3 * rough_sigma, rough_mean + 3 * rough_sigma]
    bounds = [(rough_mean - 3 * rough_sigma, rough_mean + 3 * rough_sigma), (0.001, 3 * rough_sigma)]
    res = gausfit(x0=[rough_mean, rough_sigma], args=baseline_array, bounds=bounds)
    fitted_mean, fitted_sigma = res.x
    return np.array([fitted_mean, fitted_sigma])

def Pedestal_Gausfit(am_array, rough_cut):
    small_peak = am_array[am_array < 2 * rough_cut]
    rough_mean = np.mean(small_peak)
    rough_sigma = np.std(small_peak)
    res = gausfit(x0=[rough_mean,rough_sigma], args=small_peak, bounds=[(0, rough_mean + 5 * rough_mean),(0.001, 5 * rough_sigma)])
    fitted_mean, fitted_sigma = res.x
    return np.array([fitted_mean, fitted_sigma])

def Rough_Analysis(file_path, wavelength, verbose):
    file = loadH5(file_path)
    # 声明变量
    baseline_array_ch0 = []
    baseline_array_ch1 = []
    peak_am_array_ch0 = []
    peak_am_array_ch1 = []
    peak_time_array_ch0 = []
    peak_time_array_ch1 = []
    # 循环
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
    rough_res = []
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
        res = gausfit(x0=[rough_mean, rough_sigma], args=baseline, bounds=bounds)
        baseline_fitted_mean, baseline_fitted_sigma = res.x
        # # Pedestal统计
        pedestal_rough_cut = 18
        small_peak = peak_am_array[peak_am_array < 2 * pedestal_rough_cut]
        rough_mean = np.mean(small_peak)
        rough_sigma = np.std(small_peak)
        res = gausfit(x0=[rough_mean,rough_sigma], args=small_peak, bounds=[(0, rough_mean + 5 * rough_mean),(0.001, 5 * rough_sigma)])
        pedestal_fitted_mean, pedestal_fitted_sigma = res.x
        # # Signal时间窗统计
        pedestal_cut = pedestal_fitted_mean + 5 * pedestal_fitted_sigma
        condition = peak_am_array > pedestal_cut
        filtered_peak_time_array = peak_time_array[condition]
        if wavelength == 365:
            time_range = [500, 750]
        elif wavelength == 415:
            time_range = [250, 400]
        else:
            time_range = [300, 700]
            
        filtered_peak_time_array = filtered_peak_time_array[(filtered_peak_time_array > time_range[0]) & (filtered_peak_time_array < time_range[1])]
        rough_mean = np.mean(filtered_peak_time_array)
        rough_sigma = np.std(filtered_peak_time_array)
        bounds=[(rough_mean - 3 * rough_sigma, rough_mean + 3 * rough_sigma), (0.001, 5 * rough_sigma)]
        res = gausfit(x0=[rough_mean, rough_sigma], args=filtered_peak_time_array, bounds=bounds)
        signal_fitted_mean, signal_fitted_sigma = res.x
        # # 记录
        rough_res.append(baseline_fitted_mean)
        rough_res.append(baseline_fitted_sigma)
        rough_res.append(pedestal_fitted_mean)
        rough_res.append(pedestal_fitted_sigma)
        rough_res.append(signal_fitted_mean)
        rough_res.append(signal_fitted_sigma)
        # # 画图
        if verbose[0]==1:
            # # # Baseline
            if channel==0:
                bounds = [390, 410]
            else:
                bounds = [480, 500]
            plt.figure(figsize = (8, 6))
            plt.hist(baseline, histtype='step', bins=100, range=bounds)
            plt.axvline(x=baseline_fitted_mean, color='red', linestyle='--', label=f'Fitted mean')
            plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.05,
                y=plt.gca().get_ylim()[1] * 0.9,
                s=f'Mean:{baseline_fitted_mean}\nSigma={baseline_fitted_sigma}\nRe={baseline_fitted_sigma/baseline_fitted_mean}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )
            plt.title(f"Baseline Distribution of ch{channel}")
            plt.xlabel("Baseline/ADC")
            plt.ylabel("Entries")
            plt.legend()
            if verbose[1]==1:
                plt.show()
            if verbose[2]==1:
                plt.savefig(verbose[3] + f"_Rough_Baseline_Distribution_ch{channel}.jpg")
                print(f"[Rough_Analysis] Save Baseline Distribution of ch{channel}")
            plt.close()
            
            # # Peak Amplitude Distribution
            bounds= [0, 1000]
            plt.figure(figsize=(8,6))
            plt.hist(peak_am_array, histtype='step', bins=1000, range=bounds)
            plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.05,
                y=plt.gca().get_ylim()[1] * 0.9,
                s=f'Pedestal mean:{pedestal_fitted_mean}\nPedestal sigma:{pedestal_fitted_sigma}\nPedestal cut:{pedestal_cut}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )
            plt.axvline(x=pedestal_cut, color='red', linestyle='--', linewidth=1.5, label=f'pedestal cut')
            plt.title(f"Peak Amplitude Distribution of ch{channel}")
            plt.xlabel("Peak/ADC")
            plt.ylabel("Entries")
            plt.yscale('log')
            plt.legend()
            if verbose[1]==1:
                plt.show()
            if verbose[2]==1:
                plt.savefig(verbose[3] + f"_Rough_Peak_Amplitude_Distribution_ch{channel}.jpg")
                print(f"[Rough_Analysis] Save Peak Amplitude Distribution of ch{channel}")
            plt.close()
            
            # # Peak Time Distribution
            bounds=[0, 1000]
            plt.figure(figsize=(8, 6))
            plt.hist(peak_time_array, histtype='step', bins=500, range=bounds)
            plt.axvline(x=signal_fitted_mean, color='red', linestyle='--', linewidth=1.5, label=f'fitted mean')
            plt.axvspan(np.min(filtered_peak_time_array), np.max(filtered_peak_time_array), color='green', alpha=0.3, label=f'Filted data')
            plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.05,
                y=plt.gca().get_ylim()[1] * 0.9,
                s=f'Fitted mean:{signal_fitted_mean}\nFitted sigma:{signal_fitted_sigma}\nSelected range:{int(np.min(filtered_peak_time_array)), int(np.max(filtered_peak_time_array))}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )
            plt.title(f"Peak Time Distritbution of ch{channel}")
            plt.xlabel("t/ns")
            plt.ylabel("Entries")
            plt.legend()
            if verbose[1]==1:
                plt.show()
            if verbose[2]==1:
                plt.savefig(verbose[3] + f"_Rough_Peak_Time_Distribution_ch{channel}.jpg")
                print(f"[Rough_Analysis] Save Peak Time Distribution of ch{channel}")
            plt.close()
            
            # # Signal Time Distribution
            bounds=[np.min(filtered_peak_time_array), np.max(filtered_peak_time_array)]
            plt.figure(figsize=(8, 6))
            plt.hist(filtered_peak_time_array, histtype='step', bins = int((bounds[1] - bounds[0])/2), range=bounds)
            plt.axvline(x= signal_fitted_mean, color='red', linestyle='--', linewidth=1.5, label=f'fitted mean')
            plt.axvspan(xmin= signal_fitted_mean - 3 * signal_fitted_sigma, xmax= signal_fitted_mean + 3 * signal_fitted_sigma, color='pink', alpha=0.3, label=f'LED window')
            plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.02,
                y=plt.gca().get_ylim()[1] * 0.9,
                s=f'Fitted mean:{signal_fitted_mean}\nFitted Sigma:{signal_fitted_sigma}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )
            plt.title(f"LED Signal Time Distribution of ch{channel}")
            plt.xlabel("t/ns")
            plt.ylabel("Entries")
            plt.legend()
            if verbose[1]==1:
                plt.show()
            if verbose[2]==1:
                plt.savefig(verbose[3] + f"_Rough_Led_Time_Distribution_ch{channel}.jpg")
                print(f"[Rough_Analysis] Save LED Window of ch{channel}")
            plt.close()

    # 返回
    return np.array(rough_res)

def Detailed_Analysis(file_path, rough_array, verbose):
    # 导入文件
    file = loadH5(file_path)
    # 定义变量
    dcr_ch0 = [] # index, amplitude, time
    dcr_ch1 = [] # index, amplitude, time
    signal_ch0 = [] # index, amplitude, time, charge
    signal_ch1 = [] # index, amplitude, time, charge
    info = [] # total number, ch0: led window, dcr, led; ch1: led window, dcr, led
    info.append(file.shape[0])
    # 循环
    for index in tqdm(range(file.shape[0])):
        waves = file[index]
        for channel in range(2):
            # 用于统计的变量
            if channel == 0:
                baseline = rough_array[0]
                pedestal_cut = rough_array[2] + 5 * rough_array[3]
                led_window = [rough_array[4] - 3 * rough_array[5], rough_array[4] + 3 * rough_array[5]]
                dcr_window = [40, led_window[0]]
            else:
                gap = 6
                baseline = rough_array[0 + gap]
                pedestal_cut = rough_array[2 + gap] + 5 * rough_array[3 + gap]
                led_window = [rough_array[4 + gap] - 3 * rough_array[5 + gap], rough_array[4 + gap] + 3 * rough_array[5 + gap]]
                dcr_window = [40, led_window[0]]
            # 转成int类型
            pedestal_cut = int(pedestal_cut)
            led_window = [int(value) for value in led_window]
            # 拿到数据
            if channel == 1:
                wave = 500 + waves[channel]
            else:
                wave = waves[channel]
            # 剪掉基线
            wave = wave - baseline
            # 反转
            if channel == 0: wave = - wave # ch0的peak会小于零，在此整体反转，便于后续统一分析
            # 定位peak
            peak_am = np.max(wave)
            peak_time = np.argmax(wave)
            # pedestal cut
            if peak_am < pedestal_cut: continue
            # 统计LED与暗噪声
            if peak_time > dcr_window[0] and peak_time < dcr_window[1]:
                charge = np.sum(wave[0 : led_window[0]])
                if channel == 0:
                    dcr_ch0.append([index, peak_am, peak_time, charge])
                else:
                    dcr_ch1.append([index, peak_am, peak_time, charge])
            elif (peak_time > led_window[0]) and (peak_time < led_window[1]):
                charge = np.sum(wave[led_window[0] : led_window[1]])
                if channel == 0:
                    signal_ch0.append([index, peak_am, peak_time, charge])                  
                else:
                    signal_ch1.append([index, peak_am, peak_time, charge])
    # 变成numpy数组
    dcr_ch0 = np.array(dcr_ch0)
    dcr_ch1 = np.array(dcr_ch1)
    signal_ch0 = np.array(signal_ch0)
    signal_ch1 = np.array(signal_ch1)        
    # 统计
    for channel in range(2):
        if channel == 0:
            if dcr_ch0.ndim > 1 and len(dcr_ch0) > 0:
                dcr_am = dcr_ch0[:, 1]
                dcr_time = dcr_ch0[:, 2]
                dcr_charge = dcr_ch0[:, 3]
                verbose_dcr = 1
            else:
                verbose_dcr = 0
                print(f"[Detialed Analysis] dcr_ch{channel} is zero. Skipping")
            if signal_ch0.ndim > 1 and len(signal_ch0) > 0:
                signal_am = signal_ch0[:, 1]
                signal_time = signal_ch0[:, 2]
                signal_charge = signal_ch0[:, 3]
                verbose_led = 1
            else:
                verbose_led = 0
                print(f"[Detailed Analysis] signal_ch{channel} is zero. Skipping")
        else:
            if dcr_ch1.ndim > 1 and len(dcr_ch1) > 0:
                dcr_am = dcr_ch1[:, 1]
                dcr_time = dcr_ch1[:, 2]
                dcr_charge = dcr_ch1[:, 3]
                verbose_dcr = 1
            else:
                verbose_dcr = 0
                print(f"[Detailed Analysis] dcr_ch{channel} is zero. Skipping")
            if signal_ch1.ndim > 1 and len(signal_ch1) > 0:
                signal_am = signal_ch1[:, 1]
                signal_time = signal_ch1[:, 2]
                signal_charge = signal_ch1[:, 3]
                verbose_led = 1
            else:
                verbose_led = 0
                print(f"[Detailed Analysis] signal_ch{channel} is zero. Skipping")
    # # 计算DCR、LED
        if channel == 0:
            led_window = [rough_array[4] - 3 * rough_array[5], rough_array[4] + 3 * rough_array[5]]
            dcr_window = [40, led_window[0]]
            dcr = len(dcr_ch0) / (1e-6 * (dcr_window[1] - dcr_window[0]) * file.shape[0]) # Unit: kHz
            dark_noise = len(dcr_ch0) * (led_window[1] - led_window[0]) / (dcr_window[1] - dcr_window[0])  # LED窗口内总共有多少个暗噪声
            led = len(signal_ch0) - dark_noise
            # # # 误差计算
            dcr_error = np.sqrt(len(dcr_ch0)) / (1e-6 * (dcr_window[1] - dcr_window[0]) * file.shape[0]) # Unit: kHz
            dark_noise_error = np.sqrt(len(dcr_ch0)) * (led_window[1] - led_window[0]) / (dcr_window[1] - dcr_window[0])
            signal_error = np.sqrt(len(signal_ch0))
            led_error = np.sqrt(dark_noise_error**2 + signal_error**2)
        else:
            gap = 6
            led_window = [rough_array[4 + gap] - 3 * rough_array[5 + gap], rough_array[4 + gap] + 3 * rough_array[5 + gap]]
            dcr_window = [40, led_window[0]]
            dcr = len(dcr_ch1) / (1e-6 * (dcr_window[1] - dcr_window[0]) * file.shape[0]) # Unit: kHz
            dark_noise = len(dcr_ch1) * (led_window[1] - led_window[0]) / (dcr_window[1] - dcr_window[0]) # LED窗口内总共有多少个暗噪声
            led = len(signal_ch1) - dark_noise
            # # # 误差计算
            dcr_error = np.sqrt(len(dcr_ch1)) / (1e-6 * (dcr_window[1] - dcr_window[0]) * file.shape[0]) # Unit: kHz
            dark_noise_error = np.sqrt(len(dcr_ch1)) * (led_window[1] - led_window[0]) / (dcr_window[1] - dcr_window[0])
            signal_error = np.sqrt(len(signal_ch1))
            led_error = np.sqrt(dark_noise_error**2 + signal_error**2)
        # # 通用计算
        trigger_ratio = led / file.shape[0]
        trigger_ratio_error = led_error / file.shape[0]
        Lambda = - np.log(1 - trigger_ratio)
        Lambda_error = trigger_ratio_error / (1 - trigger_ratio)
        # # 记录
        info.append(dcr_window[0])
        info.append(led_window[0])
        info.append(led_window[1])
        if channel==0:
            info.append(len(signal_ch0))
            info.append(len(dcr_ch0))
        else:
            info.append(len(signal_ch1))
            info.append(len(dcr_ch1))
        info.append(dcr) # Unit: kHz
        info.append(dcr_error) # Unit: kHz
        info.append(led)
        info.append(led_error)
        info.append(trigger_ratio)
        info.append(trigger_ratio_error)
        info.append(Lambda)
        info.append(Lambda_error)
            
        # # 画图、输出、保存
        if verbose[0] == 1:
            # # dcr Amplitude Distribution
            if verbose_dcr == 1:
                bounds = [0, 1000]
                bins = 500
                plt.figure(figsize=(8, 6))
                plt.hist(dcr_am, histtype='step', bins=bins, range=bounds)
                plt.title(f"Dark Noise Amplitude Distribution of ch{channel}")
                plt.xlabel("Amplitude/ADC")
                plt.ylabel("Entries")
                if verbose[1] == 1:
                    plt.show()
                if verbose[2] == 1:
                    plt.savefig(verbose[3] + f"_Detailed_DCR_Amplitude_Distribution_ch{channel}.jpg")
                    print(f"[Detailed_Analysis] Save DCR Amplitude Distribution of ch{channel}")
                plt.close()
            
            # # dcr Time Distribution
            if verbose_dcr == 1:
                if channel == 0:
                    gap = 0
                else:
                    gap = 6
                bounds = [0, int(rough_array[4 + gap] - 3 * rough_array[5 + gap])]
                bins = int((bounds[1] - bounds[0])/2)
                plt.figure(figsize=(8, 6))
                plt.hist(dcr_time, histtype='step', bins=bins, range=bounds)
                plt.title(f"Dark Noise Time Distribution of ch{channel}")
                plt.xlabel("Time/ns")
                plt.ylabel("Entries")
                if verbose[1] == 1:
                    plt.show()
                if verbose[2] == 1:
                    plt.savefig(verbose[3] + f"_Detailed_DCR_Time_Distribution_ch{channel}.jpg")
                    print(f"[Detailed_Analysis] Save DCR Time Distribution of ch{channel}")
                plt.close()
                
            # # dcr Charge Distribution
            # if verbose_dcr == 1:
            #     bounds = [np.min(dcr_charge), np.max(dcr_charge)]
            #     bins = int((bounds[1] - bounds[0])/10)
            #     plt.figure(figsize=(8, 6))
            #     plt.hist(dcr_charge, histtype='step', bins=bins, range=bounds)
            #     plt.title(f"Dark Noise Charge Distribution of ch{channel}")
            #     plt.xlabel("ADC*ns")
            #     plt.ylabel("Entries")
            #     if verbose[1] == 1:
            #         plt.show()
            #     if verbose[2] == 1:
            #         plt.savefig(verbose[3] + f"_Detailed_DCR_Charge_Distribution_ch{channel}.jpg")
            #         print(f"[Detailed_Analysis] Save DCR Charge Distribution of ch{channel}")
            #     plt.close()
            
            # # Signal Amplitude Distribution
            if verbose_led == 1:
                bounds = [0, 1000]
                bins = int((bounds[1] - bounds[0])/2)
                plt.figure(figsize=(8, 6))
                plt.hist(signal_am, histtype='step', bins=bins, range=bounds)
                plt.title(f"LED Amplitude Distribution of ch{channel}")
                plt.xlabel("Amplitude/ADC")
                plt.ylabel("Entries")
                if verbose[1] == 1:
                    plt.show()
                if verbose[2] == 1:
                    plt.savefig(verbose[3] + f"_Detailed_LED_Amplitude_Distribution_ch{channel}.jpg")
                    print(f"[Detailed_Analysis] Save LED Amplitude Distribution of ch{channel}")
                plt.close()
            
            # # Signal Time Distribution
            if verbose_led == 1:
                bounds = [np.min(signal_time), np.max(signal_time)]
                bins = int((bounds[1] - bounds[0])/2)
                plt.figure(figsize=(8, 6))
                plt.hist(signal_time, histtype='step', bins=bins, range=bounds)
                plt.title(f"LED Time Distribution of ch{channel}")
                plt.xlabel("Time/ns")
                plt.ylabel("Entries")
                if verbose[1] == 1:
                    plt.show()
                if verbose[2] == 1:
                    plt.savefig(verbose[3] + f"_Detailed_LED_Time_Distribution_ch{channel}.jpg")
                    print(f"[Detailed_Analysis] Save LED Time Distribution of ch{channel}")
                plt.close()
            
            # # Signal Charge Distribution
            # if verbose_led == 1:
            #     bounds = [np.min(signal_charge), np.max(signal_charge)]
            #     bins = int((bounds[1] - bounds[0])/4)
            #     plt.figure(figsize=(8, 6))
            #     plt.hist(signal_charge, histtype='step', bins=bins, range=bounds)
            #     plt.title(f"Charge Distribution of ch{channel}")
            #     plt.xlabel("ADC*ns")
            #     plt.ylabel("Entries")
            #     if verbose[1] == 1:
            #         plt.show()
            #     if verbose[2] == 1:
            #         plt.savefig(verbose[3] + f"_Detailed_LED_Charge_Distribution_ch{channel}.jpg")
            #         print(f"[Detailed_Analysis] Save LED Charge Distribution of ch{channel}")
            #     plt.close()
    # 输出
    return dcr_ch0, dcr_ch1, signal_ch0, signal_ch1, info

def Subrun_Weighted_Analysis(data, channel):
    # Baseline
    weight = 1/(data[f"ch{channel}_baseline_sigma"]**2)
    baseline = np.sum(weight * data[f"ch{channel}_baseline_mean"]) / np.sum(weight)
    baseline_error = np.sqrt(1/np.sum(weight))
    # DCR
    weight = 1 / (data[f"ch{channel}_dcr_error"]**2)
    dcr = np.sum(weight * data[f"ch{channel}_dcr"]) / np.sum(weight)
    dcr_error = np.sqrt(1/np.sum(weight))
    # LED
    weight = 1 / (data[f"ch{channel}_led_error"]**2)
    led = np.sum(weight * data[f"ch{channel}_led"]) / np.sum(weight)
    led_error = np.sqrt(1/np.sum(weight))
    # Trigger Ratio
    weight = 1 / (data[f"ch{channel}_trigger_ratio_error"]**2)
    trigger_ratio = np.sum(weight * data[f"ch{channel}_trigger_ratio"]) / np.sum(weight)
    trigger_ratio_error = np.sqrt(1 / np.sum(weight))
    # Lambda
    weight = 1 / (data[f"ch{channel}_lambda_error"]**2)
    Lambda = np.sum(weight * data[f"ch{channel}_lambda"]) / np.sum(weight)
    Lambda_error = np.sqrt(1/np.sum(weight))
    # 记录
    res = [baseline, baseline_error, dcr, dcr_error, led, led_error, trigger_ratio, trigger_ratio_error, Lambda, Lambda_error]
    res = np.array(res)
    # 输出
    return res

def Subrun_Total_Analysis(data, channel):
    # Baseline
    weight = 1/(data[f"ch{channel}_baseline_sigma"]**2)
    baseline = np.sum(weight * data[f"ch{channel}_baseline_mean"]) / np.sum(weight)
    baseline_error = np.sqrt(1/np.sum(weight))
    # Time Windows
    led_window = [np.average(data[f"ch{channel}_led_window_left"]), np.average(data[f"ch{channel}_led_window_right"])]
    dark_window = [np.average(data[f"ch{channel}_dcr_window_left"]), led_window[0]]
    # Total Signals
    signals = np.sum(data[f"ch{channel}_signal"])
    signals_error = np.sqrt(signals)
    # Dark Noises
    dark_noise = np.sum(data[f"ch{channel}_dark_noise"])
    dcr = dark_noise / ((dark_window[1] - dark_window[0]) * np.sum(data[f"total"]) * 1e-6) # Unit: kHz
    dcr_error = np.sqrt(dark_noise) / ((dark_window[1] - dark_window[0]) * np.sum(data[f"total"]) * 1e-6) # Unit: kHz
    # LED Signals
    dark_noise = np.sum(data[f"ch{channel}_dark_noise"]) * (led_window[1] - led_window[0]) / (dark_window[1] - dark_window[0])
    dark_noise_error = np.sqrt(np.sum(data[f"ch{channel}_dark_noise"])) * (led_window[1] - led_window[0]) / (dark_window[1] - dark_window[0])
    led = signals - dark_noise 
    led_error = np.sqrt(signals_error**2 + dark_noise_error**2)
    # Trigger Ratio
    trigger_ratio = led / np.sum(data[f"total"])
    trigger_ratio_error = led_error/ np.sum(data[f"total"])
    # Lambda
    Lambda = -np.log(1 - trigger_ratio)
    Lambda_error = trigger_ratio_error / (1 - trigger_ratio)
    # 记录
    res = [baseline, baseline_error, dcr, dcr_error, led, led_error, trigger_ratio, trigger_ratio_error, Lambda, Lambda_error]
    res = np.array(res)
    # 输出
    return res

def Plot_Subrun(csv_path, run, verbose):
    data = pd.read_csv(csv_path)
    for channel in range(2):
        # Method I: Weighted Analysis
        res_weighted = Subrun_Weighted_Analysis(data=data, channel=channel)
        # Method II: Total Analysis
        res_total = Subrun_Total_Analysis(data=data, channel=channel)
        # # Baseline
        weighted_mean = res_weighted[0]
        weighted_error = res_weighted[1]
        total_mean = res_total[0]
        total_error = res_total[1]
        plt.figure(figsize=(8, 6))
        plt.errorbar(data["subrun"], data[f"ch{channel}_baseline_mean"],
                    yerr=data[f"ch{channel}_baseline_sigma"],
                    fmt='o',
                    label=f"Subrun",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='red',
                    elinewidth=1,
                    capthick=1)
        bounds=[0,20]
        plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.1,
                y=np.max(data[f"ch{channel}_baseline_mean"]) + np.min(data[f"ch{channel}_baseline_sigma"]/2),
                s=f'Weighted:{weighted_mean:.4f},{weighted_error:.4f}\nTotal:{total_mean:.4f},{total_error:.4f}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
        plt.axhspan(weighted_mean - weighted_error, weighted_mean + weighted_error, color='pink', alpha=0.3, label=f"I: Weighted Analysis")
        plt.axhline(weighted_mean, color='pink')
        plt.axhspan(total_mean - total_error, total_mean + total_error, color='green', alpha=0.3, label=f"II: Total Analysis")
        plt.axhline(total_mean, color='green')
        plt.title(f"Baseline Distribution of ch{channel}")
        plt.xlabel(f"Subrun")
        plt.ylabel(f"ADC")
        plt.legend()
        if verbose[0] == 1:
            plt.show()
        if verbose[1] == 1:
            plt.savefig(verbose[2] + f"_baseline_ch{channel}.jpg")
            print(f"[Plot_Subrun] Save Baseline of ch{channel}")
        plt.close()

        # # DCR
        gap = 2
        weighted_mean = res_weighted[0 + gap]
        weighted_error = res_weighted[1 + gap]
        total_mean = res_total[0 + gap]
        total_error = res_total[1 + gap]
        plt.figure(figsize=(8, 6))
        plt.errorbar(data["subrun"], data[f"ch{channel}_dcr"],
                    yerr=data[f"ch{channel}_dcr_error"],
                    fmt='o',
                    label=f"Subrun",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='red',
                    elinewidth=1,
                    capthick=1)
        bounds=[0,20]
        plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.02,
                y=np.max(data[f"ch{channel}_dcr"]) + np.min(data[f"ch{channel}_dcr_error"]/2),
                s=f'Weighted:{weighted_mean:.4f},{weighted_error:.4f}\nTotal:{total_mean:.4f},{total_error:.4f}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
        plt.axhspan(weighted_mean - weighted_error, weighted_mean + weighted_error, color='pink', alpha=0.3, label=f"I: Weighted Analysis")
        plt.axhline(weighted_mean, color='pink')
        plt.axhspan(total_mean - total_error, total_mean + total_error, color='green', alpha=0.3, label=f"I: Total Analysis")
        plt.axhline(total_mean, color='green')
        plt.title(f"DCR of ch{channel}")
        plt.xlabel(f"Subrun")
        plt.ylabel(f"DCR/kHz")
        plt.legend()
        if verbose[0] == 1:
            plt.show()
        if verbose[1] == 1:
            plt.savefig(verbose[2] + f"_dcr_ch{channel}.jpg")
            print(f"[Plot_Subrun] Save DCR of ch{channel}")
        plt.close()

        # # LED
        gap = 4
        weighted_mean = res_weighted[0 + gap]
        weighted_error = res_weighted[1 + gap]
        total_mean = res_total[0 + gap]/20
        total_error = res_total[1 + gap]/20
        plt.figure(figsize=(8, 6))
        plt.errorbar(data["subrun"], data[f"ch{channel}_led"],
                    yerr=data[f"ch{channel}_led_error"],
                    fmt='o',
                    label=f"Subrun",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='red',
                    elinewidth=1,
                    capthick=1)
        bounds=[0,20]
        plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.02,
                y=np.max(data[f"ch{channel}_led"]) + np.min(data[f"ch{channel}_led_error"]/2),
                s=f'Weighted:{weighted_mean:.4f},{weighted_error:.4f}\nTotal:{total_mean:.4f},{total_error:.4f}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
        plt.axhspan(weighted_mean - weighted_error, weighted_mean + weighted_error, color='pink', alpha=0.3, label=f"I: Weighted Analysis")
        plt.axhline(weighted_mean, color='pink')
        plt.axhspan(total_mean - total_error, total_mean + total_error, color='green', alpha=0.3, label=f"II: Total Analysis")
        plt.axhline(total_mean, color='green')
        plt.title(f"LED Signals of ch{channel}")
        plt.xlabel(f"Subrun")
        plt.ylabel(f"LED Signals")
        plt.legend()
        if verbose[0] == 1:
            plt.show()
        if verbose[1] == 1:
            plt.savefig(verbose[2] + f"_LED_ch{channel}.jpg")
            print(f"[Plot_Subrun] Save LED Signals of ch{channel}")
        plt.close()   

        # Trigger Ratio
        gap = 6
        weighted_mean = res_weighted[0 + gap]
        weighted_error = res_weighted[1 + gap]
        total_mean = res_total[0 + gap]
        total_error = res_total[1 + gap]
        plt.figure(figsize=(8, 6))
        plt.errorbar(data["subrun"], data[f"ch{channel}_trigger_ratio"],
                    yerr=data[f"ch{channel}_trigger_ratio_error"],
                    fmt='o',
                    label=f"Subrun",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='red',
                    elinewidth=1,
                    capthick=1)
        bounds=[0,20]
        plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.02,
                y=np.max(data[f"ch{channel}_trigger_ratio"]) + np.min(data[f"ch{channel}_trigger_ratio_error"]/2),
                s=f'Weighted:{weighted_mean:.4f},{weighted_error:.4f}\nTotal:{total_mean:.4f},{total_error:.4f}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
        plt.axhspan(weighted_mean - weighted_error, weighted_mean + weighted_error, color='pink', alpha=0.3, label=f"I: Weighted Analysis")
        plt.axhline(weighted_mean, color='pink')
        plt.axhspan(total_mean - total_error, total_mean + total_error, color='green', alpha=0.3, label=f"II: Total Analysis")
        plt.axhline(total_mean, color='green')
        plt.title(f"Trigger Ratio of ch{channel}")
        plt.xlabel(f"Subrun")
        plt.ylabel(f"Trigger Ratio")
        plt.legend()
        if verbose[0] == 1:
            plt.show()
        if verbose[1] == 1:
            plt.savefig(verbose[2] + f"_trigger_ratio_ch{channel}.jpg")
            print(f"[Plot_Subrun] Save Trigger Ratio of ch{channel}")
        plt.close() 
            
        # # Lambda
        gap = 8
        weighted_mean = res_weighted[0 + gap]
        weighted_error = res_weighted[1 + gap]
        total_mean = res_total[0 + gap]
        total_error = res_total[1 + gap]
        plt.figure(figsize=(8, 6))
        plt.errorbar(data["subrun"], data[f"ch{channel}_lambda"],
                    yerr=data[f"ch{channel}_lambda_error"],
                    fmt='o',
                    label=f"Subrun",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='red',
                    elinewidth=1,
                    capthick=1)
        bounds=[0,20]
        plt.text(
                x=bounds[1] - (bounds[1] - bounds[0]) * 0.02,
                y=np.max(data[f"ch{channel}_lambda"]) + np.min(data[f"ch{channel}_lambda_error"]/2),
                s=f'Weighted:{weighted_mean:.4f},{weighted_error:.4f}\nTotal:{total_mean:.4f},{total_error:.4f}',
                ha='right',
                va='top',
                fontsize=12,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
                )
        plt.axhspan(weighted_mean - weighted_error, weighted_mean + weighted_error, color='pink', alpha=0.3, label=f"I: Weighted Analysis")
        plt.axhline(weighted_mean, color='pink')
        plt.axhspan(total_mean - total_error, total_mean + total_error, color='green', alpha=0.3, label=f"II: Total Analysis")
        plt.axhline(total_mean, color='green')
        plt.title(f"$\lambda$ of ch{channel}")
        plt.xlabel(f"Subrun")
        plt.ylabel(f"$\lambda$")
        plt.legend()
        if verbose[0] == 1:
            plt.show()
        if verbose[1] == 1:
            plt.savefig(verbose[2] + f"_lambda_ch{channel}.jpg")
            print(f"[Plot_Subrun] Save Lambda of ch{channel}")
        plt.close()

    # # Lambda Ratio
    res_weighted_0 = Subrun_Weighted_Analysis(data=data, channel=0)
    res_weighted_1 = Subrun_Weighted_Analysis(data=data, channel=1)
    res_total_0 = Subrun_Total_Analysis(data=data, channel=0)
    res_total_1 = Subrun_Total_Analysis(data=data, channel=1)
    weighted_mean = res_weighted_1[-2] / res_weighted_0[-2]
    weighted_error = weighted_mean * np.sqrt((res_weighted_1[-1]/res_weighted_1[-2])**2 + (res_weighted_0[-1]/res_weighted_0[-2])**2)
    total_mean = res_total_1[-2] / res_total_0[-2]
    total_error = total_mean * np.sqrt((res_total_1[-1]/res_total_1[-2])**2 + (res_total_0[-1]/res_total_0[-2])**2)

    plt.figure(figsize=(8, 6))
    ratio = data["ch1_lambda"]/data["ch0_lambda"]
    ratio_error = ratio * np.sqrt((data["ch1_lambda_error"]/data["ch1_lambda"])**2 + (data["ch0_lambda_error"]/data["ch0_lambda"])**2)
    plt.errorbar(data["subrun"], ratio,
                yerr=ratio_error,
                fmt='o',
                label=f"Subrun",
                color='blue',
                markersize=5,
                capsize=3,
                linestyle='None',
                ecolor='red',
                elinewidth=1,
                capthick=1)
    bounds=[0,20]
    plt.text(
            x=bounds[1] - (bounds[1] - bounds[0]) * 0.02,
            y=plt.gca().get_ylim()[1] * 0.88,
            s=f'Weighted:{weighted_mean:.4f},{weighted_error:.4f}\nTotal:{total_mean:.4f},{total_error:.4f}',
            ha='right',
            va='top',
            fontsize=12,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )
    plt.axhspan(weighted_mean - weighted_error, weighted_mean + weighted_error, color='pink', alpha=0.3, label=f"I: Weighted Analysis")
    plt.axhline(weighted_mean, color='pink')
    plt.axhspan(total_mean - total_error, total_mean + total_error, color='green', alpha=0.3, label=f"II: Total Analysis")
    plt.axhline(total_mean, color='green')
    plt.title(f"Ratio of No.{run}")
    plt.xlabel(f"Subrun")
    plt.ylabel(r"$\lambda_{test}/\lambda_{cali}$")
    plt.legend()
    if verbose[0] == 1:
            plt.show()
    if verbose[1] == 1:
        plt.savefig(verbose[2] + f"_test_cali_ch{channel}.jpg")
        print(f"[Plot_Subrun] Save Test/Cali")
    plt.close()
    
    # 输出信息
    res = np.concatenate((res_weighted_0, res_weighted_1, res_total_0, res_total_1, [weighted_mean, weighted_error, total_mean, total_error]))
    return res

def Run_Analysis(data_dir, pic_dir, csv_dir, wavelength, verbose):
    # 检查必要的文件夹、文件是否存在
    print(f"[Run_Analysis] Process Data {data_dir}")
    run = int(data_dir.split('/')[-1])
    print(f"[Run_Analysis] Process run {run}")
    csv_dir = os.path.join(csv_dir, f"{run}")
    # # 检查 csv 所在文件夹是否存在
    if not os.path.exists(csv_dir):
        # 如果文件夹不存在，则创建
        os.makedirs(csv_dir)
        print(f"[Run_Analysis] CSV Directory {csv_dir} created successfully.")
    else:
        print(f"[Run_Analysis] CSV Directory {csv_dir} already exists.")
    # # 检查 csv 文件是否存在
    run_csv_path = os.path.join(csv_dir, f"{run}.csv")
    with open(run_csv_path, "w") as csv_file:
        part1 = f"run,subrun"
        part2 = f"ch0_baseline_mean,ch0_baseline_sigma,ch0_pedestal_mean,ch0_pedestal_sigma,ch0_signal_mean,ch0_signal_sigma"
        part3 = f"ch1_baseline_mean,ch1_baseline_sigma,ch1_pedestal_mean,ch1_pedestal_sigma,ch1_signal_mean,ch1_signal_sigma"
        part4 = f"ch0_dcr_window_left,ch0_led_window_left,ch0_led_window_right,ch0_signal,ch0_dark_noise,ch0_dcr,ch0_dcr_error,ch0_led,ch0_led_error,ch0_trigger_ratio,ch0_trigger_ratio_error,ch0_lambda,ch0_lambda_error"
        part5 = f"ch1_dcr_window_left,ch1_led_window_left,ch1_led_window_right,ch1_signal,ch1_dark_noise,ch1_dcr,ch1_dcr_error,ch1_led,ch1_led_error,ch1_trigger_ratio,ch1_trigger_ratio_error,ch1_lambda,ch1_lambda_error"
        csv_file.write(part1 + "," + part2 + "," + part3 + ",total," + part4 + "," + part5 + "\n")
    print(f"[Run_Analysis] CSV File is {run_csv_path}")
    # # 图片地址
    pic_dir = pic_dir + f"/{run}"
    # # 检查 pic_path 文件夹是否存在
    if not os.path.exists(pic_dir):
        # 如果文件夹不存在，则创建
        os.makedirs(pic_dir)
        print(f"[Run_Analysis] Plots Directory {pic_dir} created successfully.")
    else:
        print(f"[Run_Analysis] Plots Directory {pic_dir} already exists.")
    print(f"[Run_Analysis] Most of plos are in {pic_dir}")
    # 处理run
    print(f"[Run_Analysis] Start Processing")
    directory = data_dir + "/"
    h5_files = glob.glob(os.path.join(directory, "*.h5"))
    h5_files = sorted(h5_files, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    for file_path in h5_files:
        print(f"[Run_Analysis::Loop] Processing {file_path}.")
        subrun = int(file_path.split('/')[-1].split('.')[0])
        pic_path = pic_dir + f"/{subrun}"
        if verbose[0] == 1:
            verbose=[1, 0, 1, pic_path] # verbose总开关、show、save、save地址
        rough_res = Rough_Analysis(file_path=file_path, wavelength=wavelength, verbose=verbose)
        if verbose[1] == 1:
            verbose=[1, 0, 1, pic_path] # verbose总开关、show、save、save地址
        dcr_ch0, dcr_ch1, led_ch0, led_ch1, info = Detailed_Analysis(file_path=file_path, rough_array=rough_res, verbose=verbose)
        # # 结果输出
        rough_res = ",".join(map(str, rough_res))
        info = ",".join(map(str,info))
        res = f"{run},{subrun},{rough_res},{info}"
        # # # 追加写入 CSV 文件
        with open(run_csv_path, "a") as csv_file:  # 使用 "a" 模式追加写入
            if subrun == 19:
                csv_file.write(res)
            else:
                csv_file.write(res + "\n")
        print(f"[Main] Complete Processing {file_path}\n")
        
    # 画图
    if verbose[2] == 1:
        verbose = [0, 1, csv_dir + f"/{run}"] # Show, Save, Save地址
        Plot_Subrun(csv_path=run_csv_path, run=run, verbose=verbose)
       
            
# if __name__ == "__main__":
#     # 传入参数
#     parser = argparse.ArgumentParser(description="Run PMT Analysis")
#     parser.add_argument("--data_dir", type=str, required=True, help="Path to the data directory")
#     parser.add_argument("--pic_dir", type=str, default="/home/penguin/PMTAnalysis/Pics/Data", help="Path to the picture directory")
#     parser.add_argument("--csv_dir", type=str, default="/home/penguin/PMTAnalysis/Infos", help="Path to the CSV directory")
#     parser.add_argument("--verbose", type=int, nargs=3, default=[1, 1, 1], help="Verbose levels:[Rough, Detailed, Subrun]")
    
#     # 解析参数
#     args = parser.parse_args()
    
#     # 程序运行
#     Run_Analysis(data_dir=args.data_dir, pic_dir=args.pic_dir, csv_dir=args.csv_dir, verbose=args.verbose)
    
# 测试代码(可删)
data_dir = "/mnt/e/PMT/Data/93"
pic_dir = "/home/penguin/PMTAnalysis/Pics/Data"
csv_dir = "/home/penguin/PMTAnalysis/Infos"
verbose = [1, 0, 0] # Rough, Detailed, Subrun的画图
Run_Analysis(data_dir=data_dir, pic_dir=pic_dir, csv_dir=csv_dir, wavelength=465, verbose=verbose)
      


# # # # 收集每个run的信息
# res = Plot_Subrun(csv_path=csv_dir + f"/36/36.csv", run=36, verbose=[0, 0])
# part1 = "weighted_ch0_baseline_mean,weighted_ch0_baseline_error,weighted_ch0_dcr,weighted_ch0_dcr_error,weighted_ch0_led,weighted_ch0_led_error,weighted_ch0_trigger_ratio,weighted_ch0_trigger_ratio_error,weighted_ch0_lambda,weighted_ch0_lambda_error"
# part2 = "weighted_ch1_baseline_mean,weighted_ch1_baseline_error,weighted_ch1_dcr,weighted_ch1_dcr_error,weighted_ch1_led,weighted_ch1_led_error,weighted_ch1_trigger_ratio,weighted_ch1_trigger_ratio_error,weighted_ch1_lambda,weighted_ch1_lambda_error"
# part3 = "total_ch0_baseline_mean,total_ch0_baseline_error,total_ch0_dcr,total_ch0_dcr_error,total_ch0_led,total_ch0_led_error,total_ch0_trigger_ratio,total_ch0_trigger_ratio_error,total_ch0_lambda,total_ch0_lambda_error"
# part4 = "total_ch1_baseline_mean,total_ch1_baseline_error,total_ch1_dcr,total_ch1_dcr_error,total_ch1_led,total_ch1_led_error,total_ch1_trigger_ratio,total_ch1_trigger_ratio_error,total_ch1_lambda,total_ch1_lambda_error"
# part5 = "weighted_test_cali,weighted_test_tail_error,total_test_cali,total_test_cali_error"
# head = part1 + "," + part2 + "," + part3 + "," + part4 + "," + part5
# print(len(res))
# print(head)