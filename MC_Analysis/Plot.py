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
# Self-Defined
import Collect_Info
# Function
def Plot_Ratio_Angle(CSV_Path):
    data = pd.read_csv(CSV_Path)
    # Plot
    plt.figure(figsize=(8, 6))
    plt.errorbar(data["angle"], data["ratio"],
                        yerr=data["ratio_error"],
                        fmt='o',
                        label=f"MC",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.title(f"L1: Photon Ratio")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(f"Test/Cali")
    plt.ylim([0, 4.5])
    plt.legend()
    plt.show()
    # plt.close()
    
def Plot_Two_Ratio_Angle(CSV_PMT_Path, CSV_CON_Path):
    data_pmt = pd.read_csv(CSV_PMT_Path)
    data_con = pd.read_csv(CSV_CON_Path)
    # Plot
    plt.figure(figsize=(8, 6))
    plt.errorbar(data_pmt["angle"], data_pmt["ratio"],
                        yerr=data_pmt["ratio_error"],
                        fmt='o',
                        label=f"MC: PMT",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.errorbar(data_con["angle"], data_con["ratio"],
                        yerr=data_con["ratio_error"],
                        fmt='o',
                        label=f"MC: Con",
                        color='red',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.title(f"L1: Photon Ratio")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(f"Test/Cali")
    plt.ylim([0, 4.5])
    plt.legend()
    plt.show()
    # plt.close()
    
def Plot_Con_PMT(CSV_PMT_Path, CSV_CON_Path):
    # Read Files
    data_pmt = pd.read_csv(CSV_PMT_Path)
    data_con = pd.read_csv(CSV_CON_Path)
    # Compute
    data = data_con["ratio"]/data_pmt["ratio"]
    error = data * np.sqrt( (data_con["ratio_error"]/data_con["ratio"]) ** 2 + (data_pmt["ratio_error"]/data_pmt["ratio"]) ** 2)
    # Plot
    plt.figure(figsize=(8, 6))
    plt.errorbar(data_pmt["angle"], data,
                        yerr=error,
                        fmt='o',
                        label=f"MC",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.title(f"L1: Con/PMT Photon Ratio")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(f"Con/PMT")
    plt.ylim([0, 3.0])
    plt.legend()
    plt.show()
   
def Plot_Ratios_Angle(pmt1, con1, pmt2, con2, pmt3, con3, pmt4, con4):
    # Plot
    plt.figure(figsize=(8, 6))
    # Windows
    data = pd.read_csv(pmt1)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='o',
                    label=f"PMT:0%",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    data = pd.read_csv(con1)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='o',
                    label=f"Con:0%",
                    color='blue',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    # Windows Ref 25
    data = pd.read_csv(pmt2)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='^',
                    label=f"PMT:25%",
                    color='green',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    data = pd.read_csv(con2)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='^',
                    label=f"Con:25%",
                    color='green',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    # Windows Ref 50
    data = pd.read_csv(pmt3)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='s',
                    label=f"PMT:50%",
                    color='black',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    data = pd.read_csv(con3)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='s',
                    label=f"Con:50%",
                    color='black',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    # Data Con
    data = Collect_Data(1, 415, 1, 1, "5.0cm", 5)
    plt.errorbar(data[:, 3], data[:, -2],
                    yerr=data[:, -1],
                    fmt='o',
                    label=f"Data:Con",
                    color='pink',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    # Data PMT
    data = Collect_Data(1, 415, 1, 0, "5.0cm", 5)
    plt.errorbar(data[:, 3], data[:, -2],
                    yerr=data[:, -1],
                    fmt='o',
                    label=f"Data:PMT",
                    color='pink',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    # Con Ref 75
    data = pd.read_csv(pmt4)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='s',
                    label=f"PMT: Con 75%",
                    color='yellow',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    data = pd.read_csv(con4)
    plt.errorbar(data["angle"], data["ratio"],
                    yerr=data["ratio_error"],
                    fmt='s',
                    label=f"Con: Con 75%",
                    color='yellow',
                    markersize=5,
                    capsize=3,
                    linestyle='None',
                    ecolor='pink',
                    elinewidth=1,
                    capthick=1)
    plt.title(f"L1: Con/PMT Photon Ratio")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(f"Con/PMT")
    plt.ylim([0, 5.0])
    plt.legend()
    plt.show()

# 根据轨道和波长绘制MC和Data的Test/Cali和Con/PMT
def Plot_Data_MC(distance, wavelength):
    # Usage
    data_csv_dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/Data"
    mc_csv_dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/MC/Windows"
    # Get Data
    data_csv_path = data_csv_dir + "/" + f"L{distance}_{wavelength}.csv"
    data = pd.read_csv(data_csv_path)
    data_con = data[data["concentrator"] == 1]
    data_pmt = data[data["concentrator"] == 0]
    # Get MC
    mc_csv_path = mc_csv_dir + "/" + f"L{distance}_{wavelength}_Con.csv"
    mc_con = pd.read_csv(mc_csv_path)
    mc_csv_path = mc_csv_dir + "/" + f"L{distance}_{wavelength}_PMT.csv"
    mc_pmt = pd.read_csv(mc_csv_path)
    # Compute Ratio
    merged_data = pd.merge(data_con[['angle', 'total_test_cali']], data_pmt[['angle', 'total_test_cali']], on='angle', suffixes=('_con', '_pmt'))
    data_ratio = merged_data['total_test_cali_con'] / merged_data['total_test_cali_pmt']
    mc_ratio = mc_con['ratio'] / mc_pmt['ratio']
    # Plot
    # # Test/Cali
    plt.figure(figsize=(8, 6))
    plt.plot(data_con['angle'], data_con['total_test_cali'], marker='o', linestyle='None', color='blue', label=f"Data: Con")
    plt.plot(data_pmt['angle'], data_pmt['total_test_cali'], marker='o', linestyle='None', color='blue', label=f"Data: PMT")
    plt.plot(mc_con['angle'], mc_con['ratio'], marker='o', linestyle='None', color='red', label=f"MC: Con")
    plt.plot(mc_pmt['angle'], mc_pmt['ratio'], marker='o', linestyle='None', color='red', label=f"MC: PMT")
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
    pic_path = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Res" + "/" + f"L{distance}_{wavelength}_Test_Cali.jpg"
    plt.savefig(pic_path)
    plt.close()
    # # Ratio
    plt.figure(figsize=(8, 6))
    plt.plot(data_con['angle'], data_ratio, marker='o', linestyle='None', color='blue', label=f"Data")
    plt.plot(mc_pmt['angle'], mc_ratio, marker='o', linestyle='None', color='red', label=f"MC")
    plt.title(f"L{distance}_{wavelength}")
    plt.xlabel("Angle/deg")
    plt.ylabel("Con/PMT")
    plt.ylim(0, 2.5)
    plt.xlim(-5, 95)
    y_ticks = np.arange(0, 2.6, 0.2)
    plt.yticks(y_ticks)
    x_ticks = np.arange(-5, 96, 5)  # 从-5到95，步长为5
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend()
    # plt.show()
    pic_path = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Res" + "/" + f"L{distance}_{wavelength}_Con_PMT.jpg"
    plt.savefig(pic_path)
    plt.close()

# 计算散射球直径带来的系统误差
# # 根据Selection筛选数据，并用Mean Method处理多条数据
def Diameter_Get_Data_Base(selection):
    csv_path = "/home/penguin/PMTAnalysis/Run.csv"
    data = pd.read_csv(csv_path)
    tags = ["quality", "distance", "led", "angle", "concentrator", "duty", "ball/temperature"]
    for index in range(len(selection)):
        tag = tags[index]
        data = data[data[tag] == f"{selection[index]}"]
    # Mean Method
    res = []
    len_data = len(data)
    methods = ["weighted", "total"]
    if len_data > 1:
        print(f"[Diameter_Get_Data_Base] distance:{selection[1]}, led:{selection[2]}, angle:{selection[3]}, concentrator:{selection[4]}, duty:{selection[5]}, ball:{selection[6]} has more than one data. Using mean method!")
        for method in methods:
            value = np.mean(data[f"{method}_test_cali"])
            error = np.sqrt(np.sum(data[f"{method}_test_cali_error"] ** 2)) / len_data
            res.append(value)
            res.append(error)
    elif len_data == 1:
        for method in methods:
            value = data[f"{method}_test_cali"]
            error = data[f"{method}_test_cali_error"]
            res.append(value)
            res.append(error)
    # Return 
    return np.array(res)
# # 根据轨道、波长计算Ratio，画图并返回Mean, Error和Relative Error
def Diameter_Get_Data(distance, wavelength):
    # Get Duty
    if wavelength == 365:
        duty = "3.5%"
    elif wavelength == 415:
        duty = "0.2%"
    elif wavelength == 465 or wavelength == 480:
        duty = "2.0%"
    # Compute Ratio and Error
    balls = ["2.0cm", "3.0cm", "4.0cm", "5.0cm"]
    res = np.zeros((len(balls), 4))
    for index in range(len(balls)):
        ball = balls[index]
        # Get Data
        selection = [1, distance, wavelength, 0, 0, duty, ball] # "quality", "distance", "led", "angle", "concentrator", "duty", "ball/temperature"
        data_pmt = Diameter_Get_Data_Base(selection)
        selection = [1, distance, wavelength, 0, 1, duty, ball] # "quality", "distance", "led", "angle", "concentrator", "duty", "ball/temperature"
        data_con = Diameter_Get_Data_Base(selection)
        # Compute Data
        temp = []
        ratio = data_con[0] / data_pmt[0]
        error = ratio * np.sqrt((data_con[1] / data_con[0]) ** 2 + (data_pmt[1] / data_pmt[0]) ** 2)
        temp.append(ratio)
        temp.append(error)
        ratio = data_con[2] / data_pmt[2]
        error = ratio * np.sqrt((data_con[3] / data_con[2]) ** 2 + (data_pmt[3] / data_pmt[2]) ** 2)
        temp.append(ratio)
        temp.append(error)
        # Record
        temp = np.ravel(temp) # 列数组转化为行数组
        res[index] = temp
    # Plot
    balls = [2.0, 3.0, 4.0, 5.0]
    ratio = res[:, 0]
    error = res[:, 1]
    mean = np.mean(ratio)
    max_error = np.max(np.abs(ratio - mean))
    relative_error = max_error / mean
    output = [mean, max_error, relative_error]
    plt.figure(figsize=(8, 6))
    plt.errorbar(balls, ratio, yerr=error, fmt='o', capsize=5, capthick=1, label='Data', color='blue')
    plt.hlines(mean, 1, 6, colors='pink', linestyles='--', linewidth=1.5, label="Mean")
    plt.axhspan(mean - max_error, mean + max_error, color='pink', alpha=0.3, label=r"1$\sigma$")
    plt.title(f"L{distance}_{wavelength}: Ratio vs Diameter")
    plt.xlabel("Diameter/cm")
    plt.ylabel("Ratio")
    plt.xlim(1, 6)
    plt.ylim([1.5, 2.5])
    y_ticks = np.arange(1.5, 2.5, 0.1)
    plt.yticks(y_ticks)
    x_ticks = np.arange(1, 6, 1)  # 从-5到95，步长为5
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend()
    # plt.show()
    pic_dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Systemic_Error/Diameter"
    pic_path = pic_dir + "/" + f"L{distance}_{wavelength}.jpg"
    plt.savefig(pic_path)
    plt.close()
    # Return
    return output
# # 处理指定轨道下的所有波长
def Systemric_Error_Diameter(distance):
    csv_path = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Data/L{distance}_Systemic_Error_Diameter.csv"
    header = ['led', 'mean', 'max_error', 'relative_error']
    # Loop
    wavelengths = [365, 415, 465, 480]
    all_res = np.zeros((len(wavelengths), len(header)))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        res = Diameter_Get_Data(1, wavelength)
        all_res[index] = [wavelength, res[0], res[1], res[2]]

    df = pd.DataFrame(all_res, columns=header)
    df.to_csv(csv_path, mode='w', header=True, index=False)

    with open(csv_path, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate()
    
# 计算安装、拆卸带来的系统误差
# Usage
Systemric_Error_Diameter(1)