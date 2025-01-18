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
# Self-Defined
sys.path.append('/home/penguin/PMTAnalysis')
from Analysis_Plot import Select_Data, Mean_Result, Collect_Data

# 从Run.csv中收集某个波长的数据，并储存成CSV文件
def Collect_One_Wave(distance, wavelength, step):
    csv_wave_dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/Data"
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
    total_data = Collect_Data(1, wavelength, distance, 1, "5.0cm", step) # quality, led, distance, concentrator, ball, step
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
    total_data = Collect_Data(1, wavelength, distance, 0, "5.0cm", step) # quality, led, distance, concentrator, ball, step
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