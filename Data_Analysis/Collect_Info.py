import csv
import numpy as np
import pandas as pd # 处理csv
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

def Read_Subrun(csv_path):
    data = pd.read_csv(csv_path)
    # # Lambda Ratio
    res_weighted_0 = Subrun_Weighted_Analysis(data=data, channel=0)
    res_weighted_1 = Subrun_Weighted_Analysis(data=data, channel=1)
    res_total_0 = Subrun_Total_Analysis(data=data, channel=0)
    res_total_1 = Subrun_Total_Analysis(data=data, channel=1)
    weighted_mean = res_weighted_1[-2] / res_weighted_0[-2]
    weighted_error = weighted_mean * np.sqrt((res_weighted_1[-1]/res_weighted_1[-2])**2 + (res_weighted_0[-1]/res_weighted_0[-2])**2)
    total_mean = res_total_1[-2] / res_total_0[-2]
    total_error = total_mean * np.sqrt((res_total_1[-1]/res_total_1[-2])**2 + (res_total_0[-1]/res_total_0[-2])**2)    
    # 输出信息
    res = np.concatenate((res_weighted_0, res_weighted_1, [weighted_mean, weighted_error], res_total_0, res_total_1, [total_mean, total_error]))
    return res

def Read_Subrun_DCR(csv_path):
    data = pd.read_csv(csv_path)
    channel = 1
    # # Lambda Ratio
    res_weighted_1 = Subrun_Weighted_Analysis(data=data, channel=1)
    res_total_1 = Subrun_Total_Analysis(data=data, channel=1)
    res_weighted_0 = res_weighted_1 * 0
    res_total_0 = res_total_1 * 0
    weighted_mean = 0
    weighted_error = 0
    total_mean = 0
    total_error = 0
    
    # 输出信息
    res = np.concatenate((res_weighted_0, res_weighted_1, res_total_0, res_total_1, [weighted_mean, weighted_error, total_mean, total_error]))
    return res

# 创建Run.csv，并写入文件头
run_csv_file_path = "/home/penguin/PMTAnalysis/Run.csv"
with open(run_csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
    # 文件头
    part1 = "run,files,angle,distance,concentrator,pmt1,pmt2,duty,led,ball/temperature,quality,attenuator,date,light,tri_fre,tri_ch01_am,tri_ch01_bias,tri_ch02_am,tri_ch02_bias"
    
    channel = 0
    method = "weighted"
    part2 = f"{method}_ch{channel}_baseline_mean,{method}_ch{channel}_baseline_sigma,{method}_ch{channel}_dcr,{method}_ch{channel}_dcr_error,{method}_ch{channel}_led,{method}_ch{channel}_led_error,{method}_ch{channel}_trigger_ratio,{method}_ch{channel}_trigger_ratio_error,{method}_ch{channel}_lambda,{method}_ch{channel}_lambda_error"
    channel = 1
    part3 = f"{method}_ch{channel}_baseline_mean,{method}_ch{channel}_baseline_sigma,{method}_ch{channel}_dcr,{method}_ch{channel}_dcr_error,{method}_ch{channel}_led,{method}_ch{channel}_led_error,{method}_ch{channel}_trigger_ratio,{method}_ch{channel}_trigger_ratio_error,{method}_ch{channel}_lambda,{method}_ch{channel}_lambda_error,{method}_test_cali,{method}_test_cali_error"
    
    channel = 0
    method = "total"
    part4 = f"{method}_ch{channel}_baseline_mean,{method}_ch{channel}_baseline_sigma,{method}_ch{channel}_dcr,{method}_ch{channel}_dcr_error,{method}_ch{channel}_led,{method}_ch{channel}_led_error,{method}_ch{channel}_trigger_ratio,{method}_ch{channel}_trigger_ratio_error,{method}_ch{channel}_lambda,{method}_ch{channel}_lambda_error"
    channel = 1
    part5 = f"{method}_ch{channel}_baseline_mean,{method}_ch{channel}_baseline_sigma,{method}_ch{channel}_dcr,{method}_ch{channel}_dcr_error,{method}_ch{channel}_led,{method}_ch{channel}_led_error,{method}_ch{channel}_trigger_ratio,{method}_ch{channel}_trigger_ratio_error,{method}_ch{channel}_lambda,{method}_ch{channel}_lambda_error,{method}_test_cali,{method}_test_cali_error"
    
    head = f"{part1},{part2},{part3},{part4},{part5}\n"
    file.write(head)

# 读取setting.csv并把对应run的info写入
setting_file_path = "/home/penguin/PMTAnalysis/setting.csv"
run_csv_dir = "/home/penguin/PMTAnalysis/Infos"
# setting_file_path = "/home/penguin/PMTAnalysis/Infos/150/150.csv"
with open(setting_file_path, mode='r', encoding='utf-8-sig') as file:
    csv_reader = csv.reader(file)
    for index, line in enumerate(csv_reader):
        if index == 0:
            continue
        if len(line) == 14:
            date = "2024-01-01 0:00:00"
            quality = 0
            concentrator = 1
            attenuator = 0
            ball = "5.0cm"
        elif len(line) == 16:
            date = line[14]
            quality = line[15]
            concentrator = 1
            attenuator = 0
            ball = "5.0cm"
        elif len(line) == 17:
            date = line[14]
            quality = line[15]
            concentrator = line[16]
            attenuator = 0
            ball = "5.0cm"
        elif len(line) == 18:
            date = line[14]
            quality = line[15]
            concentrator = line[16]
            attenuator = line[17]
            ball = "5.0cm"
        elif len(line) == 19:
            date = line[14]
            quality = line[15]
            concentrator = line[16]
            attenuator = line[17]
            ball = line[18]
                
        # elif len(line) == 16:
        # elif len(line) == 19:
        run = line[0]
        number_runs = line[1]
        angle = line[2]
        distance = line[3]
        duty = line[4]
        wavelength = line[5]
        trifre = line[6]
        ch01am = line[7]
        ch01bias = line[8]
        ch02am = line[9]
        ch02bias = line[10]
        pmt1 = line[11]
        pmt2 = line[12]
        light = line[13]
        # run < 36的为0结果
        if int(run) < 36:
            length = 4 * len(part2.split(','))
            res_run = [0] * length
        elif int(run) == 149 or int(run) == 235 or int(run) == 62:
            quality = 0
            length = 4 * len(part2.split(','))
            res_run = [0] * length
        else:
            run_csv_file = run_csv_dir + f"/{run}/{run}.csv"
            # 统计行数
            with open(run_csv_file, 'r') as file:
                line_count = sum(1 for _ in file)
                if line_count != 21:
                    print(f"[Collect_Info] Run {run}, led:{wavelength} isn't completely analysed!")
                    continue
                if duty == '---%':
                    res_run = Read_Subrun_DCR(run_csv_file)
                else:
                    res_run = Read_Subrun(run_csv_file)             
        # 写入数据   
        res = [run, number_runs, angle, distance, concentrator, pmt1, pmt2, duty, wavelength, ball, quality, attenuator, date, light, trifre, ch01am, ch01bias, ch02am, ch02bias]
        res = res + list(map(str, res_run))
        with open(run_csv_file_path, mode='a', encoding='utf-8-sig') as Runfile:
            res_str = ','.join(map(str, res))
            if int(run) == 559:
                Runfile.write(res_str)
            else:
                Runfile.write(res_str + '\n')
        