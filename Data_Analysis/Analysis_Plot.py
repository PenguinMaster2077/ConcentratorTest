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


# 利用selection来筛选数据
def Select_Data(run_csv_path, selection):
    data = pd.read_csv(run_csv_path)
    data = data[data["quality"] == selection[0]]
    data = data[data["led"] == selection[1]]
    data = data[data["distance"] == selection[2]]
    data = data[data["concentrator"] == selection[3]]
    data = data[data["angle"] == selection[4] ]
    data = data[data["ball/temperature"] == selection[5]]
    return data

# 如果通过筛选的数据有多个，用它们的平均值代替最终结果
# 长度48：Method, ch, baseline, dcr, led, trigger ratio, lambda, ratio
def Mean_Result(data):
    Length = len(data)
    res = []
    # Weighted: 22 = 5 * 2 * 2 + 2
    method = "weighted"
    for channel in range(2):
        mean_head = [f"{method}_ch{channel}_baseline_mean", f"{method}_ch{channel}_dcr", f"{method}_ch{channel}_led", f"{method}_ch{channel}_trigger_ratio", f"{method}_ch{channel}_lambda"]
        error_head = [f"{method}_ch{channel}_baseline_sigma", f"{method}_ch{channel}_dcr_error", f"{method}_ch{channel}_led_error", f"{method}_ch{channel}_trigger_ratio_error", f"{method}_ch{channel}_lambda_error"]
        for index in range(len(mean_head)):
            mean = np.mean(data[mean_head[index]])
            error = np.sqrt(sum(data[error_head[index]] ** 2)) / Length
            res.append(mean)
            res.append(error)
    # Test/Cali
    mean = np.mean(data[f"{method}_test_cali"])
    error = np.sqrt(sum(data[f"{method}_test_cali_error"])) / Length
    res.append(mean)
    res.append(error)
    # Total: 22 = 5 * 2 * 2 + 2
    method = "total"
    for channel in range(2):
        mean_head = [f"{method}_ch{channel}_baseline_mean", f"{method}_ch{channel}_dcr", f"{method}_ch{channel}_led", f"{method}_ch{channel}_trigger_ratio", f"{method}_ch{channel}_lambda"]
        error_head = [f"{method}_ch{channel}_baseline_sigma", f"{method}_ch{channel}_dcr_error", f"{method}_ch{channel}_led_error", f"{method}_ch{channel}_trigger_ratio_error", f"{method}_ch{channel}_lambda_error"]
        for index in range(len(mean_head)):
            mean = np.mean(data[mean_head[index]])
            error = np.sqrt(sum(data[error_head[index]] ** 2)) / Length
            res.append(mean)
            res.append(error)
        # Test/Cali
    mean = np.mean(data[f"{method}_test_cali"])
    error = np.sqrt(sum(data[f"{method}_test_cali_error"] ** 2)) / Length
    res.append(mean)
    res.append(error)
    # 输出
    return res
# 收集同一波长的所有结果
# 58 = 4 + 44; LED, Distance, Concentrator, Angle, Method, ch, baseline, dcr, led, trigger ratio, lambda, ratio
def Collect_Data(quality, led, distance, concentrator, ball, step):
    run_csv_path = "/home/penguin/PMTAnalysis/Run.csv"
    total_res = []
    for angle in range(0, 95, step):
        run_res = []
        selection = [f"{quality}", f"{led}", f"{distance}", f"{concentrator}", f"{angle}", ball] # quality, led, distance, concentrator, angle, ball
        data = Select_Data(run_csv_path=run_csv_path, selection=selection)
        if len(data) == 1:
            mean_data = Mean_Result(data)
            run_res.append(int(selection[1])) # LED
            run_res.append(int(selection[2])) # Distance
            run_res.append(int(selection[3])) # Concentrator
            run_res.append(angle)
            run_res = run_res + mean_data
        else:
            print(f"[Compute_Ratio] LED: {led}, Distance: {distance}, Concentrator:{concentrator}, Ball:{ball}, Angle: {angle} has {len(data)} data. Using mean value represents result")
            mean_data = Mean_Result(data)
            run_res.append(int(selection[1])) # LED
            run_res.append(int(selection[2])) # Distance
            run_res.append(int(selection[3])) # Concentrator
            run_res.append(angle)
            run_res = run_res + mean_data
        total_res.append(run_res)
    total_res = np.array(total_res)
    # 输出
    return np.array(total_res)

def Compute_Ratio(data_con, data_pmt):
    Length = len(data_con)
    ratio = data_con[:, -2] / data_pmt[:, -2]
    error = ratio * np.sqrt((data_con[:, -1]/data_con[:, -2])**2 + (data_pmt[:, -1]/data_pmt[:, -2])**2)
    res = np.zeros((Length, 6))
    res[:, :4] = data_con[:, :4]
    res[:, 4] = ratio
    res[:, 5] = error
    # 输出
    return res

def Plot_Con_PMT(distance, step):
    angles = range(0, 95, step)
    # 读取并计算数据
    con_365 = Collect_Data(1, 365, distance, 1, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    pmt_365 = Collect_Data(1, 365, distance, 0, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    res_365 = Compute_Ratio(con_365, pmt_365)

    con_415 = Collect_Data(1, 415, distance, 1, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    pmt_415 = Collect_Data(1, 415, distance, 0, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    res_415 = Compute_Ratio(con_415, pmt_415)

    con_465 = Collect_Data(1, 465, distance, 1, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    pmt_465 = Collect_Data(1, 465, distance, 0, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    res_465 = Compute_Ratio(con_465, pmt_465)

    con_480 = Collect_Data(1, 480, distance, 1, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    pmt_480 = Collect_Data(1, 480, distance, 0, "5.0cm", step) # quality, led, distance, concentrator, ball, step
    res_480 = Compute_Ratio(con_480, pmt_480)
    # 读取立体角
    computed_solid = pd.read_csv(f"/home/penguin/PMTAnalysis/SolidAngle/L{distance}.txt", header=None)
    computed_solid[computed_solid == 0] = 999
    # 在Ratio中扣除solid影响
    # # 365
    res_365_Solid = np.zeros((len(con_365), 2))
    res_365_Solid[:, 0] = res_365[:, -2] / computed_solid.iloc[:, 1].values
    res_365_Solid[:, 1] = res_365[:, -1] / computed_solid.iloc[:, 1].values
    # # 415
    res_415_Solid = np.zeros((len(con_365), 2))
    res_415_Solid[:, 0] = res_415[:, -2] / computed_solid.iloc[:, 1].values
    res_415_Solid[:, 1] = res_415[:, -1] / computed_solid.iloc[:, 1].values
    # # 465
    res_465_Solid = np.zeros((len(con_365), 2))
    res_465_Solid[:, 0] = res_465[:, -2] / computed_solid.iloc[:, 1].values
    res_465_Solid[:, 1] = res_465[:, -1] / computed_solid.iloc[:, 1].values
    # # 480
    res_480_Solid = np.zeros((len(con_365), 2))
    res_480_Solid[:, 0] = res_480[:, -2] / computed_solid.iloc[:, 1].values
    res_480_Solid[:, 1] = res_480[:, -1] / computed_solid.iloc[:, 1].values
    # 画图
    # # Test/Cali vs Angle for different LEDs
    plt.figure(figsize=(8, 6))
    # # # 365
    plt.errorbar(con_365[:, 3], con_365[:, -2],
                        yerr=con_365[:, -1],
                        fmt='o',
                        label=f"365: Con",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.errorbar(pmt_365[:, 3], pmt_365[:, -2],
                        yerr=pmt_365[:, -1],
                        fmt='o',
                        label=f"365: PMT",
                        color='red',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # # # 415
    plt.errorbar(con_415[:, 3], con_415[:, -2],
                        yerr=con_415[:, -1],
                        fmt='s',
                        label=f"415: Con",
                        color='green',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.errorbar(pmt_415[:, 3], pmt_415[:, -2],
                        yerr=pmt_415[:, -1],
                        fmt='s',
                        label=f"415: PMT",
                        color='black',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # # # 465
    plt.errorbar(con_465[:, 3], con_465[:, -2],
                        yerr=con_465[:, -1],
                        fmt='^',
                        label=f"465: Con",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.errorbar(pmt_465[:, 3], pmt_465[:, -2],
                        yerr=pmt_465[:, -1],
                        fmt='^',
                        label=f"465: PMT",
                        color='red',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # # # 480
    plt.errorbar(con_480[:, 3], con_480[:, -2],
                        yerr=con_480[:, -1],
                        fmt='d',
                        label=f"480: Con",
                        color='green',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.errorbar(pmt_480[:, 3], pmt_480[:, -2],
                        yerr=pmt_480[:, -1],
                        fmt='d',
                        label=f"480: PMT",
                        color='black',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.title(r"$\lambda_{test}/\lambda_{cali}$")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(r"$\lambda_{test}/\lambda_{cali}$")
    plt.legend()
    # plt.show()
    plt.savefig(f"/home/penguin/PMTAnalysis/Pics/Preliminary_Res/L{distance}_Test_Cali_LEDs.jpg")
    plt.close()

    # # Ratio vs Angle for different LEDs
    plt.figure(figsize=(8, 6))
    # # # 365
    plt.errorbar(res_365[:, 3], res_365[:, -2],
                        yerr=res_365[:, -1],
                        fmt='o',
                        label=f"365",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # # # 415
    plt.errorbar(res_415[:, 3], res_415[:, -2],
                        yerr=res_415[:, -1],
                        fmt='s',
                        label=f"415",
                        color='red',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # # # 465
    plt.errorbar(res_465[:, 3], res_465[:, -2],
                        yerr=res_465[:, -1],
                        fmt='^',
                        label=f"465",
                        color='green',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # # # 480
    plt.errorbar(res_480[:, 3], res_480[:, -2],
                        yerr=res_480[:, -1],
                        fmt='d',
                        label=f"480",
                        color='black',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.title(f"Com/PMT for different LEDs")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(f"Con/PMT")
    plt.legend()
    # plt.show()
    plt.savefig(f"/home/penguin/PMTAnalysis/Pics/Preliminary_Res/L{distance}_Con_PMT_LEDs.jpg")
    plt.close()
    
    # 输出
    return angles, res_365_Solid, res_415_Solid, res_465_Solid, res_480_Solid

def Plot_Ratio_Solid(distance, step):
    dis_angle, dis_365, dis_415, dis_465, dis_480 = Plot_Con_PMT(distance, step)
    plt.figure(figsize=(8, 6))
    plt.errorbar(dis_angle, dis_365[:, 0],
                            yerr=dis_365[:, 1],
                            fmt='o',
                            label=f"L1:365",
                            color='blue',
                            markersize=5,
                            capsize=3,
                            linestyle='None',
                            ecolor='pink',
                            elinewidth=1,
                            capthick=1)
    plt.errorbar(dis_angle, dis_415[:, 0],
                            yerr=dis_415[:, 1],
                            fmt='s',
                            label=f"L1:415",
                            color='red',
                            markersize=5,
                            capsize=3,
                            linestyle='None',
                            ecolor='pink',
                            elinewidth=1,
                            capthick=1)
    plt.errorbar(dis_angle, dis_465[:, 0],
                            yerr=dis_465[:, 1],
                            fmt='^',
                            label=f"L1:465",
                            color='green',
                            markersize=5,
                            capsize=3,
                            linestyle='None',
                            ecolor='pink',
                            elinewidth=1,
                            capthick=1)
    plt.errorbar(dis_angle, dis_480[:, 0],
                            yerr=dis_480[:, 1],
                            fmt='d',
                            label=f"L1:480",
                            color='black',
                            markersize=5,
                            capsize=3,
                            linestyle='None',
                            ecolor='pink',
                            elinewidth=1,
                            capthick=1)
    plt.title(f"Ratio/Solid vs Angle for LEDs")
    plt.xlabel(f"Angle/deg")
    plt.ylabel(f"Ratio/Solid Angle")
    plt.legend()
    # plt.show()
    plt.savefig(f"/home/penguin/PMTAnalysis/Pics/Preliminary_Res/L{distance}_Con_PMT_Solid_LEDs.jpg")
    plt.close()
    
    # 输出
    return dis_angle, dis_365, dis_415, dis_465, dis_480

def Plot_Ratio_Solid_Complete():
    l1_angle, l1_365, l1_415, l1_465, l1_480 = Plot_Ratio_Solid(1, 5)
    l2_angle, l2_365, l2_415, l2_465, l2_480 = Plot_Ratio_Solid(2, 10)

    # 365
    plt.figure(figsize=(8, 6))
    plt.errorbar(l1_angle, l1_365[:, 0],
                                yerr=l1_365[:, 1],
                                fmt='o',
                                label=f"L1:365",
                                color='blue',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.errorbar(l2_angle, l2_365[:, 0],
                                yerr=l2_365[:, 1],
                                fmt='o',
                                label=f"L2:365",
                                color='red',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.title(f"Ratio/Solid of 365")
    plt.xlabel("Angle/deg")
    plt.ylabel("Ratio/Solid Angle")
    plt.legend()
    # plt.show()
    plt.savefig("/home/penguin/PMTAnalysis/Pics/Preliminary_Res/Ratio_Solid_365.jpg")
    plt.close()
    # 415
    plt.figure(figsize=(8, 6))
    plt.errorbar(l1_angle, l1_415[:, 0],
                                yerr=l1_415[:, 1],
                                fmt='o',
                                label=f"L1:415",
                                color='blue',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.errorbar(l2_angle, l2_415[:, 0],
                                yerr=l2_415[:, 1],
                                fmt='o',
                                label=f"L2:415",
                                color='red',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.title(f"Ratio/Solid of 415")
    plt.xlabel("Angle/deg")
    plt.ylabel("Ratio/Solid Angle")
    plt.legend()
    # plt.show()
    plt.savefig("/home/penguin/PMTAnalysis/Pics/Preliminary_Res/Ratio_Solid_415.jpg")
    plt.close()
    # 465
    plt.figure(figsize=(8, 6))
    plt.errorbar(l1_angle, l1_465[:, 0],
                                yerr=l1_465[:, 1],
                                fmt='o',
                                label=f"L1:465",
                                color='blue',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.errorbar(l2_angle, l2_465[:, 0],
                                yerr=l2_465[:, 1],
                                fmt='o',
                                label=f"L2:465",
                                color='red',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.title(f"Ratio/Solid of 465")
    plt.xlabel("Angle/deg")
    plt.ylabel("Ratio/Solid Angle")
    plt.legend()
    # plt.show()
    plt.savefig("/home/penguin/PMTAnalysis/Pics/Preliminary_Res/Ratio_Solid_465.jpg")
    plt.close()
    # 480
    plt.figure(figsize=(8, 6))
    plt.errorbar(l1_angle, l1_480[:, 0],
                                yerr=l1_480[:, 1],
                                fmt='o',
                                label=f"L1:480",
                                color='blue',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.errorbar(l2_angle, l2_480[:, 0],
                                yerr=l2_480[:, 1],
                                fmt='o',
                                label=f"L2:480",
                                color='red',
                                markersize=5,
                                capsize=3,
                                linestyle='None',
                                ecolor='pink',
                                elinewidth=1,
                                capthick=1)
    plt.title(f"Ratio/Solid of 480")
    plt.xlabel("Angle/deg")
    plt.ylabel("Ratio/Solid Angle")
    plt.legend()
    # plt.show()
    plt.savefig("/home/penguin/PMTAnalysis/Pics/Preliminary_Res/Ratio_Solid_480.jpg")
    plt.close()

def Plot_Baseline_Run():
    run_csv_path = "/home/penguin/PMTAnalysis/Run.csv"
    data = pd.read_csv(run_csv_path)
    data = data[data["quality"] == "1"]
    data = data[data["led"] !="---"]
    # # ch0
    plt.figure(figsize=(8, 6))
    plt.errorbar(data["run"], data["weighted_ch0_baseline_mean"],
                        yerr=data["weighted_ch0_baseline_sigma"],
                        fmt='o',
                        label=f"Data",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # plt.errorbar(data["run"], data["total_ch0_baseline_mean"],
    #                     yerr=data["total_ch0_baseline_sigma"],
    #                     fmt='o',
    #                     label=f"Total",
    #                     color='red',
    #                     markersize=5,
    #                     capsize=3,
    #                     linestyle='None',
    #                     ecolor='pink',
    #                     elinewidth=1,
    #                     capthick=1)
    plt.title(f"Baseline of ch0")
    plt.xlabel("Run")
    plt.ylabel("Amplitude/ADC")
    plt.legend()
    # plt.show()
    plt.savefig("/home/penguin/PMTAnalysis/Pics/Preliminary_Res/Baseline_ch0.jpg")
    plt.close()
    # # ch1
    plt.figure(figsize=(8, 6))
    plt.errorbar(data["run"], data["weighted_ch1_baseline_mean"],
                        yerr=data["weighted_ch1_baseline_sigma"],
                        fmt='o',
                        label=f"Data",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    # plt.errorbar(data["run"], data["total_ch0_baseline_mean"],
    #                     yerr=data["total_ch0_baseline_sigma"],
    #                     fmt='o',
    #                     label=f"Total",
    #                     color='red',
    #                     markersize=5,
    #                     capsize=3,
    #                     linestyle='None',
    #                     ecolor='pink',
    #                     elinewidth=1,
    #                     capthick=1)
    plt.title(f"Baseline of ch1")
    plt.xlabel("Run")
    plt.ylabel("Amplitude/ADC")
    plt.legend()
    # plt.show()
    plt.savefig("/home/penguin/PMTAnalysis/Pics/Preliminary_Res/Baseline_ch1.jpg")
    plt.close()
    
def Plot_DCR_Temperature():
    run_csv_path = "/home/penguin/PMTAnalysis/Run.csv"
    data = pd.read_csv(run_csv_path)
    data = data[data["quality"] == "1"]
    data = data[data["pmt1"] == 1064]
    data = data[data["ball/temperature"] != "5.0cm"]
    plt.figure(figsize=(8, 6))
    plt.errorbar(data["ball/temperature"], data["weighted_ch1_dcr"],
                        yerr=data["weighted_ch1_dcr_error"],
                        fmt='o',
                        label=f"Weighted",
                        color='blue',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.errorbar(data["ball/temperature"], data["total_ch1_dcr"],
                        yerr=data["total_ch1_dcr_error"],
                        fmt='o',
                        label=f"Total",
                        color='red',
                        markersize=5,
                        capsize=3,
                        linestyle='None',
                        ecolor='pink',
                        elinewidth=1,
                        capthick=1)
    plt.title("DCR vs Temperature")
    plt.xlabel("Temperature/Celsius")
    plt.ylabel("DCR/kHz")
    plt.show()
    plt.close()
    
# Plot_Ratio_Solid_Complete()