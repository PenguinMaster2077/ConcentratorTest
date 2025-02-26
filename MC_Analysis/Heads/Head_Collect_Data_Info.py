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
import os
import sys
# Self-Defined
sys.path.append('/home/penguin/PMTAnalysis')
import Analysis_Plot

# 从Run.csv中收集某个波长的数据，并储存成CSV文件
def Collect_One_Wave(distance, wavelength, step):
    csv_wave_dir = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Data/L{distance}"
    csv_wave_path = csv_wave_dir + "/" + f"L{distance}_{wavelength}.csv"
    # Head of CSV File
    header = ['led','distance','concentrator', 'angle',
            
            'weighted_ch0_baseline_mean','weighted_ch0_baseline_sigma',
            'weighted_ch0_dcr','weighted_ch0_dcr_error',
            'weighted_ch0_led','weighted_ch0_led_error',
            'weighted_ch0_trigger_ratio','weighted_ch0_trigger_ratio_error',
            'weighted_ch0_lambda','weighted_ch0_lambda_error',
            
            'weighted_ch1_baseline_mean','weighted_ch1_baseline_sigma',
            'weighted_ch1_dcr','weighted_ch1_dcr_error',
            'weighted_ch1_led','weighted_ch1_led_error',
            'weighted_ch1_trigger_ratio','weighted_ch1_trigger_ratio_error',
            'weighted_ch1_lambda','weighted_ch1_lambda_error',
            
            'weighted_test_cali','weighted_test_cali_error',
            
            'total_ch0_baseline_mean','total_ch0_baseline_sigma',
            'total_ch0_dcr','total_ch0_dcr_error',
            'total_ch0_led','total_ch0_led_error',
            'total_ch0_trigger_ratio','total_ch0_trigger_ratio_error',
            'total_ch0_lambda','total_ch0_lambda_error',
            
            'total_ch1_baseline_mean','total_ch1_baseline_sigma',
            'total_ch1_dcr','total_ch1_dcr_error',
            'total_ch1_led','total_ch1_led_error',
            'total_ch1_trigger_ratio','total_ch1_trigger_ratio_error',
            'total_ch1_lambda','total_ch1_lambda_error',
            
            'total_test_cali','total_test_cali_error'
    ]
    # Concentrator Data
    total_data = Analysis_Plot.Collect_Data(1, wavelength, distance, 1, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    len_file = len(total_data)
    # # 创建一个 DataFrame，确保文件存在且包含header
    df_total_data = pd.DataFrame(columns=header)
    # # 循环遍历 total_data 并写入文件
    for index in range(len_file):
        temp_total_data = total_data[index]
        
        # 将 temp_total_data 转换为 DataFrame 并追加到原有 DataFrame
        temp_df = pd.DataFrame([temp_total_data], columns=header)
        
        # 如果文件不存在（即首次写入），写入header
        if index == 0:
            temp_df.to_csv(csv_wave_path, mode='w', header=True, index=False)
        else:
            # 否则，直接追加数据
            temp_df.to_csv(csv_wave_path, mode='a', header=False, index=False)
    # PMT Data
    total_data = Analysis_Plot.Collect_Data(1, wavelength, distance, 0, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    # # 追加数据到 CSV 文件
    for index in range(len_file):
        temp_total_data = total_data[index]
        
        # 将 temp_total_data 转换为 DataFrame 并追加到文件
        temp_df = pd.DataFrame([temp_total_data], columns=header)
        
        # 追加数据（mode='a'）并不再写入表头（header=False）
        temp_df.to_csv(csv_wave_path, mode='a', header=False, index=False)

    # 删除文件末尾的多余换行符
    with open(csv_wave_path, 'rb+') as file:
        file.seek(-2, os.SEEK_END)  # 定位到倒数第二个字符
        file.truncate()  # 删除最后的换行符
        
# 从Run.csv中收集4个波长的数据，并储存成4个CSV文件
def Collect_All_Waves(Distance):
    if Distance == 1:
        step = 5
    elif Distance == 2:
        step = 10
    Collect_One_Wave(Distance, 365, step)
    Collect_One_Wave(Distance, 415, step)
    Collect_One_Wave(Distance, 465, step)
    Collect_One_Wave(Distance, 480, step)

# 计算安装、拆卸带来的系统误差
# # 根据Selection筛选数据
def Installation_Get_Data_Base(selection):
    csv_path = "/home/penguin/PMTAnalysis/Run.csv"
    data = pd.read_csv(csv_path)
    # selection = [1, 1, 415, 0, 0, "0.2%", "5.0cm"]
    tags = ["quality", "distance", "led", "angle", "concentrator", "duty", "ball/temperature"]
    # Loop
    for index in range(len(tags)):
        tag = tags[index]
        data = data[data[tag] == f"{selection[index]}"]
    data = data[data["run"] > 350]
    # Record
    len_data = len(data)
    res = np.zeros((len_data, 5))
    for index in range(len_data):
        res[index] = [index + 1, data["weighted_test_cali"].iloc[index], data["weighted_test_cali_error"].iloc[index], data["total_test_cali"].iloc[index], data["total_test_cali_error"].iloc[index]]
    # Return
    return res
# # 根据轨道、波长计算Ratio，画图并么返回Mean, Error和Relatrive Error
def Installation_Get_Data(distance, wavelength):
    # Setup Variables
    if wavelength == 365:
        duty = "3.5%"
    elif wavelength == 415:
        duty = "0.2%"
    elif wavelength == 465 or wavelength == 480:
        duty = "2.0%"
    # Get Data
    selection = [1, distance, wavelength, 0, 0, duty, "5.0cm"] #quality, distance, led, angle, concentrator, duty, ball/temperature
    data_pmt = Installation_Get_Data_Base(selection)
    selection = [1, distance, wavelength, 0, 1, duty, "5.0cm"]
    data_con = Installation_Get_Data_Base(selection)
    # Compute Ratio
    len_data = len(data_pmt)
    res = np.zeros((len_data, 3))
    for index in range(len_data):
        no = data_pmt[index, 0]
        ratio = data_con[index, 1] / data_pmt[index, 1]
        error = ratio * np.sqrt((data_con[index, 2] / data_con[index, 1]) ** 2 + (data_pmt[index, 2] / data_pmt[index, 1]) ** 2)
        res[index] = [no, ratio, error]
    # Plot
    mean = np.mean(res[:, 1])
    max_error = np.max(np.abs(res[:, 1] - mean))
    relative_error = max_error / mean
    output = [mean, max_error, relative_error]
    plt.figure(figsize=(10, 8))
    plt.errorbar(res[:, 0], res[:, 1], yerr=res[:, 2], fmt='o', capsize=5, capthick=1, color='blue', label="Data")
    plt.axhline(mean, xmin=0, xmax=1, color='pink', linestyle='--', linewidth=1.5, label="Mean")
    plt.axhspan(mean - max_error, mean + max_error, color='pink', alpha=0.3, label=r"1$\sigma$")
    plt.title(f"L{distance}_{wavelength}: Ratio vs Installation")
    plt.xlabel("No.")
    plt.ylabel("Ratio")
    plt.xlim([0, 6])
    plt.ylim([1.0, 2.3])
    y_ticks = np.arange(1.0, 2.3, 0.1)
    plt.yticks(y_ticks)
    x_ticks = np.arange(0, 6, 1)
    plt.xticks(x_ticks)
    plt.grid(True, which='both', linestyle='--', color='gray', linewidth=0.5)
    plt.legend()
    # plt.show()
    pic_dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Data/Systemic_Error/Installation"
    pic_path = pic_dir + "/" + f"L{distance}_{wavelength}.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()
    # Return
    return output
# # 处理指定轨道下的所有波长
def Compute_Systemric_Error_Installation(distance):
    csv_path = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Data/L{distance}/L{distance}_Systemic_Error_Installation.csv"
    header = ['led', 'mean', 'max_error', 'relative_error']
    # Loop
    wavelengths = [365, 415, 465, 480]
    all_res = np.zeros((len(wavelengths), len(header)))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        res = Installation_Get_Data(distance, wavelength)
        all_res[index] = [wavelength, res[0], res[1], res[2]]

    df = pd.DataFrame(all_res, columns=header)
    df.to_csv(csv_path, mode='w', header=True, index=False)

    with open(csv_path, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate()
        
# 计算散射球直径带来的系统误差
# # 根据Selection筛选数据，并用Mean Method处理多条数据
def Ball_Get_Data_Base(selection):
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
        print(f"[Ball_Get_Data_Base] distance:{selection[1]}, led:{selection[2]}, angle:{selection[3]}, concentrator:{selection[4]}, duty:{selection[5]}, ball:{selection[6]} has more than one data. Using mean method!")
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
def Compute_Diameter_Get_Data(distance, wavelength):
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
        data_pmt = Ball_Get_Data_Base(selection)
        selection = [1, distance, wavelength, 0, 1, duty, ball] # "quality", "distance", "led", "angle", "concentrator", "duty", "ball/temperature"
        data_con = Ball_Get_Data_Base(selection)
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
    plt.figure(figsize=(10, 8))
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
    pic_dir = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Data/Systemic_Error/Diameter"
    pic_path = pic_dir + "/" + f"L{distance}_{wavelength}.jpg"
    plt.savefig(pic_path, dpi=500)
    plt.close()
    # Return
    return output
# # 处理指定轨道下的所有波长
def Compute_Systemric_Error_Diameter(distance):
    print(f"Systemric Error of distance {distance} is same to Errors of distance 1")
    csv_path = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Data/L{distance}/L{distance}_Systemic_Error_Diameter.csv"
    header = ['led', 'mean', 'max_error', 'relative_error']
    # Loop
    wavelengths = [365, 415, 465, 480]
    all_res = np.zeros((len(wavelengths), len(header)))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        res = Compute_Diameter_Get_Data(1, wavelength)
        all_res[index] = [wavelength, res[0], res[1], res[2]]

    df = pd.DataFrame(all_res, columns=header)
    df.to_csv(csv_path, mode='w', header=True, index=False)

    with open(csv_path, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate() 
# # 计算总系统误差
def Compute_Total_Systemric_Error(distance):
    CSV_Dir = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Data/L{distance}"
    CSV_Total_Relative_Error_Path = CSV_Dir + "/" + f"L{distance}_Total_Systemic_Error.csv"
    header = ['led', 'relative_error']
    # Create CSV File
    with open(CSV_Total_Relative_Error_Path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
    # 计算总系统误差
    CSV_Dia_Path = CSV_Dir + "/" + f"L{distance}_Systemic_Error_Diameter.csv"
    CSV_Insta_Path = CSV_Dir + "/" + f"L{distance}_Systemic_Error_Installation.csv"
    dia = pd.read_csv(CSV_Dia_Path)
    insta = pd.read_csv(CSV_Insta_Path)
    total_re_error = np.sqrt(dia["relative_error"] **2 + insta["relative_error"]**2).values
    # 写入CSV文件
    Wavelengths = [365, 415, 465, 480]
    with open(CSV_Total_Relative_Error_Path, mode="a", newline="") as file:
        writer = csv.writer(file)
        for wavelength , re_error in zip (Wavelengths, total_re_error):
            writer.writerow([wavelength, re_error])
    # 处理CSV文件结尾
    with open(CSV_Total_Relative_Error_Path, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        file.truncate()
# 拿到系统误差
def Get_Total_Systemic_Relative_Error(distance, wavelength):
    CSV_Dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/Data"
    CSV_File = CSV_Dir + f"/L{distance}/L{distance}_Total_Systemic_Error.csv"
    data = pd.read_csv(CSV_File)
    relative_error = data[data["led"] == wavelength]["relative_error"].values
    # Output
    return relative_error