import h5py
import os
from tqdm import tqdm
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import minimize

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

def Compute_Rough_Fitted(file, channel):
    rough_means = []
    fitted_means = []
    rough_sigmas = []
    fitted_sigmas = []
    # # 循环
    for index in tqdm(range(file.shape[0])):
    # for index in tqdm(range(500)):
    # for index in tqdm(range(100)):
        waves = file[index]
        wave = waves[channel]
        if channel == 1:
            wave = 500 + waves[channel]
        else:
            wave = waves[channel]
        # # # 处理baseline
        rough_mean = np.mean(wave)
        rough_sigma = np.std(wave)
        rough_means.append(rough_mean)
        rough_sigmas.append(rough_sigma)
        if channel == 0:
            baseline_data = wave[wave > rough_mean - rough_sigma]
        else:
            baseline_data = wave[wave < rough_mean + rough_sigma]
        # # 统计 mean和sigma的分布
        x0=[np.mean(baseline_data), np.std(baseline_data)]
        res = gausfit(x0=x0, args=baseline_data, bounds=[(np.min(baseline_data), np.max(baseline_data)), (0.001, 3 * rough_sigma)])
        fitted_mean, fitted_sigma = res.x
        fitted_means.append(fitted_mean)
        fitted_sigmas.append(fitted_sigma)
        
    return np.array(rough_means), np.array(fitted_means), np.array(rough_sigmas), np.array(fitted_sigmas)

# 处理数据
file_path = "/home/penguin/PMTAnalysis/Data/0/0.h5"

file = loadH5(file_path)
rough_means, fitted_means, rough_sigmas, fitted_sigmas = Compute_Rough_Fitted(file=file, channel=0)

plt.figure(figsize=(8, 6))
plt.hist(rough_means, bins=200, range=[380, 400], histtype='step', color='blue', label='rough ch0')
plt.hist(fitted_means, bins=200, range=[380, 400], histtype='step', color='red', label='fitted ch0')
plt.xlabel("ADC")
plt.ylabel("Entries")
plt.legend()
plt.title(f"Baseline mean distribution of ch0")
plt.yscale('log')
plt.savefig("./Pics/Compare_Rough_Fitted/Baseline_Mean_ch0.jpg")
plt.close()


plt.figure(figsize=(8, 6))
plt.hist(rough_sigmas, bins=150, range=[4, 50], histtype='step', color='blue', label='rough')
plt.hist(fitted_sigmas, bins=150, range=[4, 50], histtype='step', color='red', label='fitted')
plt.xlabel("ADC")
plt.ylabel("Entries")
plt.title(f"Baseline sigma distribution of ch0")
plt.legend()
plt.yscale('log')
plt.savefig("./Pics/Compare_Rough_Fitted/Baseline_Sigma_ch0.jpg")
plt.close()

rough_means, fitted_means, rough_sigmas, fitted_sigmas = Compute_Rough_Fitted(file=file, channel=1)

plt.figure(figsize=(8, 6))
plt.hist(rough_means, bins=300, range=[470, 500], histtype='step', color='blue', label='rough')
plt.hist(fitted_means, bins=300, range=[470, 500], histtype='step', color='red', label='fitted')
plt.xlabel("ADC")
plt.ylabel("Entries")
plt.legend()
plt.title(f"Baseline mean distribution of ch1")
plt.yscale('log')
plt.savefig("./Pics/Compare_Rough_Fitted/Baseline_Mean_ch1.jpg")
plt.close()


plt.figure(figsize=(8, 6))
plt.hist(rough_sigmas, bins=150, range=[2, 50], histtype='step', color='blue', label='rough')
plt.hist(fitted_sigmas, bins=150, range=[2, 50], histtype='step', color='red', label='fitted')
plt.xlabel("ADC")
plt.ylabel("Entries")
plt.title(f"Baseline sigma distribution of ch1")
plt.legend()
plt.yscale('log')
plt.savefig("./Pics/Compare_Rough_Fitted/Baseline_Sigma_ch1.jpg")
plt.close()
        
        
        