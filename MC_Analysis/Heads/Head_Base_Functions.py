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

# 拿到测量数据
def Get_Data(daistance, wavelength, mode, sys_error = 0):
    data_csv_dir = "/home/penguin/Jinping/JSAP-install/Codes/CSV/Data"
     # Get Data
    data_csv_path = data_csv_dir + f"/L{daistance}/L{daistance}_{wavelength}.csv"
    data = pd.read_csv(data_csv_path)
    data_con = data[data["concentrator"] == 1].reset_index(drop=True)
    data_pmt = data[data["concentrator"] == 0].reset_index(drop=True)
    if mode == 0:
        Angle = data_pmt['angle']
        Test_Cali = data_pmt['total_test_cali']
        Test_Cali_Error = data_pmt['total_test_cali_error']
        Angle = np.array(Angle)
        Test_Cali = np.array(Test_Cali)
        Test_Cali_Error = np.array(Test_Cali_Error)
        return Angle, Test_Cali, Test_Cali_Error
    elif mode == 1:
        Angle = data_con['angle']
        Test_Cali = data_con['total_test_cali']
        Test_Cali_Error = data_con['total_test_cali_error']
        Angle = np.array(Angle)
        Test_Cali = np.array(Test_Cali)
        Test_Cali_Error = np.array(Test_Cali_Error)
        return Angle, Test_Cali, Test_Cali_Error
    elif mode == 2:
        Angle = data_pmt['angle']
        Ratio = data_con['total_test_cali'] / data_pmt['total_test_cali']
        Ratio_Error = Ratio * np.sqrt(sys_error **2 + (data_con["total_test_cali_error"] / data_con["total_test_cali"])**2 + (data_pmt["total_test_cali_error"] / data_pmt["total_test_cali"])**2)
        Angle = np.array(Angle)
        Ratio = np.array(Ratio)
        Ratio_Error = np.array(Ratio_Error)
        return Angle, Ratio, Ratio_Error
    
# 估算MC的系统误差
def Get_Standard(distance, wavelength, mode, angle_shift, sys_error = 0, cut_off = 0):
    CSV_Dir = f"/mnt/e/PMT/Standard/L{distance}/01/CSV"
    CSV_PMT_Path = CSV_Dir + f"/L{distance}_{wavelength}_PMT.csv"
    CSV_CON_Path = CSV_Dir + f"/L{distance}_{wavelength}_Con.csv"
    if distance == 1:
        data_pmt = pd.read_csv(CSV_PMT_Path).iloc[:-1]
        data_con = pd.read_csv(CSV_CON_Path).iloc[:-1]
    elif distance == 2:
        data_pmt = pd.read_csv(CSV_PMT_Path)
        data_con = pd.read_csv(CSV_CON_Path)
    # Return 
    if mode == 0:
        Angle = data_pmt["angle"] + angle_shift
        Test_Cali = data_pmt["ratio"]
        Test_Cali_Error = data_pmt["ratio_error"]
        Angle = np.array(Angle)
        Test_Cali = np.array(Test_Cali)
        Test_Cali_Error = np.array(Test_Cali_Error)
        return Angle, Test_Cali, Test_Cali_Error
    elif mode == 1:
        Angle = data_con["angle"] + angle_shift
        Test_Cali = data_con["ratio"]
        Test_Cali_Error = data_con["ratio_error"]
        Angle = np.array(Angle)
        Test_Cali = np.array(Test_Cali)
        Test_Cali_Error = np.array(Test_Cali_Error)
        return Angle, Test_Cali, Test_Cali_Error
    elif mode == 2:
        Angle = data_con["angle"] + angle_shift
        Ratio = data_con["ratio"] / data_pmt["ratio"]
        if not np.isscalar(sys_error): # 当sys_error为数组时，自动扩充
            pad_length = len(Angle) - len(sys_error)
            if pad_length > 0:
                sys_error = np.pad(sys_error, (0, pad_length), mode='constant', constant_values=0)
        Ratio_Error = Ratio * np.sqrt(sys_error ** 2 + (data_con["ratio_error"] / data_con["ratio"])**2 + (data_pmt["ratio_error"] / data_pmt["ratio"])**2)
        if cut_off == 0:
            Angle = np.array(Angle)
            Ratio = np.array(Ratio)
            Ratio_Error = np.array(Ratio_Error)
        elif cut_off > 0:        
            Angle = Angle[Angle <= cut_off]
            Angle = np.array(Angle)
            Ratio = Ratio[:len(Angle)]
            Ratio = np.array(Ratio)
            Ratio_Error = Ratio_Error[:len(Angle)]
            Ratio_Error = np.array(Ratio_Error)
        return Angle, Ratio, Ratio_Error
# 创建CSV与去掉CSV最后一行
def CSV_Operation(CSV_Path, header, mode):
    if mode == 1:
        with open(CSV_Path) as file:
            writer = csv.writer(CSV_Path)
            writer.writerow(header)
    elif mode == -1: # 生成CSV文件最后再调用
        with open(CSV_Path, 'rb+') as file:
            file.seek(-2, os.SEEK_END)
            file.truncate()
    elif mode == -2: # 修改已经生成的CSV文件
        with open(CSV_Path, 'rb+') as file:
            file.seek(-1, os.SEEK_END)
            file.truncate()