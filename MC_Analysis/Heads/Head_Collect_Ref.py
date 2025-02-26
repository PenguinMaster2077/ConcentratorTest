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

# 将测量数据展现为3D图
def Plot_3D():
    csv_dir = "/mnt/d/JPE/Reflectivity"
    csv_angle_path = "/mnt/d/JPE/Reflectivity/Results Table.csv"
    angle_data = pd.read_csv(csv_angle_path)
    Length_Files = len(angle_data)

    # Create Array
    temp_data = pd.read_csv(csv_dir + "/" + angle_data["Sample ID"][1] + ".Sample.Raw.csv")
    Length_Row = len(temp_data["nm"])
    x = temp_data["nm"] # Wavelength
    y = np.zeros(Length_Files + 1) # Angles
    z = np.zeros((Length_Files + 1, Length_Row)) # Reflectivity

    # Loop Files
    for index in range(Length_Files + 1):
        # Record
        if index < Length_Files:
            name = angle_data["Sample ID"][index]
            angle = angle_data["Description"][index]
            file_name = csv_dir + "/" + f"{name}.Sample.Raw.csv"
            file_data = pd.read_csv(file_name)
            y[index] = angle
            z[index] = file_data[" %R"] * 0.01
        elif index == Length_Files:
            y[index] = 90
            z[index] = z[index - 1] * 0 + 1
        
        
    # 创建 2D 网格
    X, Y = np.meshgrid(x, y)

    # 绘制 3D 曲面图
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, z, cmap='plasma', edgecolor='none', alpha=0.8)

    # for index in range(Length_Files):
    #     ax.scatter(x, np.full_like(x, y[index]), z[index], label=f"{angle_data['Description'][index]}")
    ax.set_xlabel("Wavelength/nm", fontsize = 14)
    ax.set_ylabel("Incident angle/deg", fontsize = 14)
    ax.set_zlabel("Reflectivity", fontsize = 14)
    ax.set_xticks(range(200, 800, 50))
    ax.set_yticks(range(0, 90, 5))
    ax.view_init(elev=30, azim= - 45) # elev: 仰角（默认 30°），azim: 方位角（默认 45°）
    # Reverse x-axis (from large to small wavelength)
    ax.set_xlim([max(x), min(x)])
    # ax.legend()
    # plt.title("Reflectivity vs Wavelength vs Angle")
    plt.tight_layout()
    # plt.show()
    pic_path = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/3D_Plot.jpg"
    plt.savefig(pic_path, dpi=500)

# 从数据中抽取某个波长的反射率的数据
def Get_One_Wave_Reflectivity(wavelength):
    csv_dir = "/mnt/d/JPE/Reflectivity"
    csv_angle_path = "/mnt/d/JPE/Reflectivity/Results Table.csv"
    angle_data = pd.read_csv(csv_angle_path)
    Length_Files = len(angle_data)

    # Create Array
    x = np.zeros(Length_Files)
    z = np.zeros(Length_Files)
    # Loop Files
    for index in range(Length_Files):
        name = angle_data["Sample ID"][index]
        angle = angle_data["Description"][index]
        file_name = csv_dir + "/" + f"{name}.Sample.Raw.csv"
        file_data = pd.read_csv(file_name)
        # Record
        x[index] = angle
        if wavelength in [365, 415, 465]:
            temp_1 = file_data[file_data["nm"] == wavelength - 1][" %R"].squeeze()
            temp_2 = file_data[file_data["nm"] == wavelength + 1][" %R"].squeeze()
            z[index] = 0.5 * (temp_1 + temp_2) * 0.01
        elif wavelength == 480:
            temp_1 = file_data[file_data["nm"] == wavelength][" %R"].squeeze()
            z[index] = temp_1 * 0.01
    return x, z

# 从数据中绘制某个波长的反射率vs入射角
def Plot_One_Wave(wavelength):
    x, z = Get_One_Wave_Reflectivity(wavelength)
    # Plot
    plt.figure(figsize=(10, 8))
    plt.plot(x, z, marker='o', linestyle='-', color='black')
    plt.xlabel("Angle/deg")
    plt.ylabel("Reflectivity")
    plt.title(f"{wavelength}: Reflectivity vs Angle")
    plt.ylim([0, 1])
    # plt.show()
    pic_path = f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/{wavelength}_Plot.jpg"
    plt.savefig(pic_path, dpi=500)
    
# 将特定波长的反射率放到同一张图中
def Plot_All_Waves():
    wavelengths = [365, 415, 465, 480]
    colors = ['black', 'blue', 'red', 'green']

    plt.figure(figsize=(10, 8))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        x, z = Get_One_Wave_Reflectivity(wavelength=wavelength)
        plt.plot(x, z, marker='o', linestyle='-', color=colors[index], label=f"{wavelength}")
    plt.xlabel("Angle/deg")
    plt.ylabel("Reflectivity")
    plt.title(f"Reflectivity vs Angle")
    plt.xlim([-5, 95])
    plt.ylim([0, 1])
    plt.xticks(np.arange(0, 95, 5))  # 设置x轴刻度，每5度一个
    plt.yticks(np.arange(0, 1.1, 0.1))  # 设置y轴刻度，每0.1一个
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    plt.legend()
    # plt.show()
    pic_path = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/All_Waves_Plot.jpg"
    plt.savefig(pic_path, dpi=500)
    
# 利用数据，用一阶导数做线性外推
def Get_One_Wave_Reflectivity_Full(wavelength):
    x, z = Get_One_Wave_Reflectivity(wavelength)
    gap = 0 - x[0]
    delta_x = x[1] - x[0]
    delta_z = z[1] - z[0]
    res = z[0] + (delta_z / delta_x) * gap
    x = np.insert(x, 0, 0)
    z = np.insert(z, 0, res)
    gap = 90 - x[-1]
    delta_x = x[-2] - x[-1]
    delta_z = z[-2] - z[-1]
    res = z[-1] + (delta_z / delta_x) * gap
    x = np.append(x, 90)
    z = np.append(z, res)
    return x, z
# 由于数据的原因，去掉85°的数据，利用80°的数据，90°=1，直接做线性外推85°的数据
def Get_One_Wave_Reflectivity_Full_V2(wavelength):
    # Get Data
    x, z = Get_One_Wave_Reflectivity(wavelength)
    # 0°
    gap = 0 - x[0]
    delta_x = x[1] - x[0]
    delta_z = z[1] - z[0]
    res = z[0] + (delta_z / delta_x) * gap
    x = np.insert(x, 0, 0)
    z = np.insert(z, 0, res)
    # 计算斜率
    gap = 90 - x[-2] # 80°
    delta_x = gap
    delta_z = 1 - z[-2]
    slope = delta_z / gap
    # 计算85°的数据
    res = z[-2] + slope * (x[-1] - x[-2])
    z[-1] = res
    # 记录90°数据
    x = np.append(x, 90)
    z = np.append(z, 1)
    return x, z

# 将特定波长的数据和外推结果绘制到一张图中
def Plot_All_Waves_Full_Angles():
    wavelengths = [365, 415, 465, 480]
    colors = ['black', 'blue', 'red', 'green']

    plt.figure(figsize=(10, 8))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        x, z = Get_One_Wave_Reflectivity_Full(wavelength=wavelength)
        plt.plot(x, z, marker='o', linestyle='-', color=colors[index], label=f"{wavelength}")
    plt.xlabel("Angle/deg")
    plt.ylabel("Reflectivity")
    plt.title(f"Reflectivity vs Angle")
    plt.xlim([-5, 95])
    plt.ylim([0, 1.2])
    plt.xticks(np.arange(0, 95, 5))  # 设置x轴刻度，每5度一个
    plt.yticks(np.arange(0, 1.2, 0.1))  # 设置y轴刻度，每0.1一个
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    plt.legend()
    # plt.show()
    pic_path = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/V1/All_Waves_Full_Angles_Plot.jpg"
    plt.savefig(pic_path, dpi=500)
    
# 将特定波长的数据和外推结果绘制到一张图中
def Plot_All_Waves_Full_Angles_V2():
    wavelengths = [365, 415, 465, 480]
    colors = ['black', 'blue', 'red', 'green']

    plt.figure(figsize=(10, 8))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        x, z = Get_One_Wave_Reflectivity_Full_V2(wavelength=wavelength)
        plt.plot(x, z, marker='o', linestyle='-', color=colors[index], label=f"{wavelength}")
    plt.xlabel("Angle/deg")
    plt.ylabel("Reflectivity")
    plt.title(f"Reflectivity vs Angle")
    plt.xlim([-5, 95])
    plt.ylim([0, 1.2])
    plt.xticks(np.arange(0, 95, 5))  # 设置x轴刻度，每5度一个
    plt.yticks(np.arange(0, 1.2, 0.1))  # 设置y轴刻度，每0.1一个
    plt.grid(True, which='both', axis='both', linestyle='--', color='gray', alpha=0.5)
    plt.legend()
    # plt.show()
    pic_path = "/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/V2/All_Waves_Full_Angles_Plot.jpg"
    plt.savefig(pic_path, dpi=500)

# 将特定波长的数据和外推结果保存
def Save_All_Waves_CSV():
    wavelengths = [365, 415, 465, 480]
    # Loop
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        x, z = Get_One_Wave_Reflectivity_Full(wavelength=wavelength)
        df = pd.DataFrame({
            'Angle': x,
            'Reflectivity': z
        })
        file_name = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Reflectivity/V1/{wavelength}.csv"
        df.to_csv(file_name, index=False)
        
def Save_All_Waves_CSV_V2():
    wavelengths = [365, 415, 465, 480]
    # Loop
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        x, z = Get_One_Wave_Reflectivity_Full_V2(wavelength=wavelength)
        df = pd.DataFrame({
            'Angle': x,
            'Reflectivity': z
        })
        file_name = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Reflectivity/V2/{wavelength}.csv"
        df.to_csv(file_name, index=False)



    