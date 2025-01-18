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
    x = temp_data["nm"]
    y = np.zeros(Length_Files)
    z = np.zeros((Length_Files, Length_Row))

    # Loop Files
    for index in range(Length_Files):
        name = angle_data["Sample ID"][index]
        angle = angle_data["Description"][index]
        file_name = csv_dir + "/" + f"{name}.Sample.Raw.csv"
        file_data = pd.read_csv(file_name)
        # Record
        y[index] = angle
        z[index] = file_data[" %R"] * 0.01
        
    # Creat 3D Plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    for index in range(Length_Files):
        ax.scatter(x, np.full_like(x, y[index]), z[index], label=f"{angle_data['Description'][index]}")
    ax.set_xlabel("Wavelength/nm")
    ax.set_ylabel("Angle/deg")
    ax.set_zlabel("Reflectivity")
    # Reverse x-axis (from large to small wavelength)
    ax.set_xlim([max(x), min(x)])
    # ax.legend()
    plt.title("Reflectivity vs Wavelength vs Angle")
    plt.tight_layout()
    # plt.show()
    plt.savefig("/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/3D_Plot.jpg")

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

# 冲数据中绘制某个波长的反射率vs入射角
def Plot_One_Wave(wavelength):
    x, z = Get_One_Wave_Reflectivity(wavelength)
    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(x, z, marker='o', linestyle='-', color='black')
    plt.xlabel("Angle/deg")
    plt.ylabel("Reflectivity")
    plt.title(f"{wavelength}: Reflectivity vs Angle")
    plt.ylim([0, 1])
    # plt.show()
    plt.savefig(f"/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/{wavelength}_Plot.jpg")
    
# 将特定波长的反射率放到同一张图中
def Plot_All_Waves():
    wavelengths = [365, 415, 465, 480]
    colors = ['black', 'blue', 'red', 'green']

    plt.figure(figsize=(8, 6))
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
    plt.savefig("/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/All_Waves_Plot.jpg")
    
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

# 将特定波长的数据和外推结果绘制到一张图中
def Plot_All_Waves_Full_Angles():
    wavelengths = [365, 415, 465, 480]
    colors = ['black', 'blue', 'red', 'green']

    plt.figure(figsize=(8, 6))
    for index in range(len(wavelengths)):
        wavelength = wavelengths[index]
        x, z = Get_One_Wave_Reflectivity_Full(wavelength=wavelength)
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
    plt.savefig("/home/penguin/Jinping/JSAP-install/Codes/Pics/Reflectivity/All_Waves_Full_Angles_Plot.jpg")

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
        file_name = f"/home/penguin/Jinping/JSAP-install/Codes/CSV/Reflectivity/{wavelength}.csv"
        df.to_csv(file_name, index=False)

Save_All_Waves_CSV()

    