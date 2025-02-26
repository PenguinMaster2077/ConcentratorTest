import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
def Compute(ratio, verbose = 0, title = ""):
    ratio_max = np.max(ratio)
    ratio_min = np.min(ratio)
    ratio_mean = np.mean(ratio)
    ratio_sigma = np.std(ratio)
    if verbose == 1:
        plt.figure(figsize=(8, 6))
        plt.plot(ratio)
        plt.xlabel("X-label")
        plt.ylabel("Y-label")
        plt.ylim([0, 2 * ratio_mean])
        plt.title(title)
        plt.show()
    print(f"mean {ratio_mean}, sigma:{ratio_sigma}, relative error:{ratio_sigma/ratio_mean}")
# # 365
ratio = [0.0543, 0.0545, 0.0543, 0.0543, 0.0538, 0.0543]
Compute(ratio)

# # 415
ratio = [0.1492, 0.1508, 0.1522, 0.1521, 0.1528, 0.1527]
Compute(ratio)