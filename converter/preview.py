'''
preview the data
'''
import h5py
from scipy.optimize import minimize
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
def loadH5(f):
    print(f'load file {f}')
    with h5py.File(f, 'r') as ipt:
        waves = ipt['Readout/Waveform'][:]
    return waves
import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm
import numpy as np
psr = argparse.ArgumentParser()
psr.add_argument('-i', dest='ipt', nargs='+', help='input files')
psr.add_argument('-o', dest='opt', type=str, help='output pdf')
psr.add_argument('-N_ch', type=int, help='number of channels')
psr.add_argument('-N', type=int, help='maximum number of waves')
psr.add_argument('-Ns', type=int, help='number of overlap the waves')
psr.add_argument('--onlywave', action='store_true', default=False, help='only plot the waves without the simple analysis')
psr.add_argument('--quick', action='store_true', default=False, help='if use fitting method for the baseline')
args = psr.parse_args()

waves = np.concatenate([loadH5(f) for f in args.ipt])
N_ch = args.N_ch

# ch1 positive; ch2 negative
if args.onlywave:
    with PdfPages(args.opt) as pdf:
        for i, w in enumerate(waves[:args.N]):
            fig, ax = plt.subplots()
            ax2 = ax.twinx()
            ax.plot(w[0], color='b', label='ch2')
            ax2.plot(w[1], color='r', label='ch1')
            ax.set_xlabel('t')
            ax.set_ylabel('ADC')
            ax.legend()
            pdf.savefig(fig)
            plt.close()
        fig, ax = plt.subplots()
        for i, w in enumerate(waves[:args.Ns]):
            ax.plot(w[0])
        ax.set_xlabel('t')
        ax.set_ylabel('ADC')
        pdf.savefig(fig)
        plt.close()
        fig, ax = plt.subplots()
        for i, w in enumerate(waves[:args.Ns]):
            ax.plot(w[1])
        ax.set_xlabel('t')
        ax.set_ylabel('ADC')
        pdf.savefig(fig)
        plt.close()
    exit(0)
res = np.empty((waves.shape[0], N_ch), dtype=[('eid', np.int32), ('Q', np.float64), ('baseline', np.float64), ('baseline_std', np.float64), ('peak', np.float64), ('peakPos', np.int32)])

# settings for preview
## rough baseline estimation window. pre_l=100: the first 100ns, which is used as the initial value of baseline
## w_l, w_r the charge integration window[t_p-w_l, t_p+w_r]
pre_l, w_l, w_r = 100, 20, 70
## hist for the selection range
binwidth, ranges = 2, [0, 1000] # choose 3ns as binwidth, range (0, 1000)ns
bins = int((ranges[1] - ranges[0]) / binwidth)

## signal window
signal_ranges = [400,800] # for 365nm
#signal_ranges = [240,540] # for 415nm
#signal_ranges = [300, 750] # for 465, 480 nm
signal_index = [signal_ranges[0]//binwidth, signal_ranges[1]//binwidth]
## darknoise window
noise_ranges = [40, 240] # [0,240] from aiqiang
noise_index = [noise_ranges[0]//binwidth, noise_ranges[1]//binwidth]
print('range: {}, binwidth: {}, entries: {}'.format(ranges, binwidth, waves.shape[0]))
print('total range: {}; signal range: {}, darknoise range: {}'.format(ranges, signal_ranges, noise_ranges))
print('total range index: {}; signal range index: {}, darknoise range index: {}'.format([ranges[0]//binwidth, ranges[1]//binwidth], signal_index, noise_index))
for i in tqdm(range(waves.shape[0])):
    ws = waves[i]
    for j in range(N_ch):
        if j==1:
            w = -ws[j]
        else:
            w = ws[j]
        baseline_rough, baseline_std_rough = np.mean(w[:pre_l]), np.std(w[:pre_l])
        if args.quick:
            baseline, baseline_std = baseline_rough, baseline_std_rough
        else:
            # estimate the baseline use the guass fit
            x = gausfit(x0=[baseline_rough, baseline_std_rough],
                args=w[w>(baseline_rough - 10*baseline_std_rough)],
                bounds=[
                    (baseline_rough - 10 * baseline_std_rough, baseline_rough + 10 * baseline_std_rough),
                    (0.001, 3 * baseline_std_rough),
                ])
            baseline_rough, baseline_std_rough = x.x
            # re-estimate the baseline use the guass fit with cutting waveform
            x = gausfit(x0=[baseline_rough, baseline_std_rough],
                args=w[w>(baseline_rough - 10*baseline_std_rough)],
                bounds=[
                    (baseline_rough - 5 * baseline_std_rough, baseline_rough + 5 * baseline_std_rough),
                    (0.001, 3 * baseline_std_rough),
                ])
            baseline, baseline_std = x.x
        # calculate the peak position, peak height, charge
        peakPos = np.argmin(w[:])
        peak = baseline - w[peakPos]
        Q = np.sum(baseline - w[np.max([peakPos-w_l, 0]):np.min([peakPos+w_r, w.shape[0]])])
        res[i, j] = (i, Q, baseline, baseline_std, peak, peakPos)
with PdfPages(args.opt) as pdf:
    fig, ax = plt.subplots()
    res_text = 'Total entries:{}\n'.format(waves.shape[0])
    for j in range(N_ch):
        h = ax.hist(res[:, j]['peakPos'][res[:, j]['peak']>30], bins=bins, range=ranges, histtype='step', label=f'ch{j}')
        # choose 300ns window
        pedestal = np.sum(h[0][noise_index[0]:noise_index[1]])
        signal = np.sum(h[0][signal_index[0]:signal_index[1]])
        darkRate = pedestal / (noise_ranges[1] - noise_ranges[0]) / waves.shape[0]*1E6
        signal_num = signal - pedestal / (noise_ranges[1] - noise_ranges[0]) * (signal_ranges[1] - signal_ranges[0])
        part1=np.sqrt(pedestal) / (noise_ranges[1] - noise_ranges[0]) * (signal_ranges[1] - signal_ranges[0])
        signal_num_error= np.sqrt(signal +part1*part1)
        trigger_ratio=signal_num/waves.shape[0]
        trigger_ratio_error=signal_num_error/waves.shape[0]
        #res_text += 'ch{} signal entries:{}, ratio{:.4f}, darkRate:{:.4f}kHz\n'.format(j, signal-pedestal, signal_num/waves.shape[0], darkRate)
        lam = -np.log(1-trigger_ratio)
        res_text += 'ch{} signal entries:{},signal error:{:.2f}, ratio{:.4f}, ratio err{:.4f}, lambda{:.2f}, darkRate:{:.4f}kHz\n'.format(j, signal_num, signal_num_error, trigger_ratio,trigger_ratio_error,lam,darkRate)
    ax.set_yscale('log')
    ax.set_xlabel('t')
    ax.set_ylabel('entries')
    ax.set_title('peak pos (peak>3mV)')
    print(res_text)
    ax.text(0, 0.9, res_text, transform=ax.transAxes, fontsize=5)
    ax.legend()
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    for j in range(N_ch):
        ax.hist(res[:, j]['Q'], bins=1000, histtype='step', label=f'ch{j}')
    ax.set_xlabel('charge')
    ax.set_ylabel('entries')
    ax.set_yscale('log')
    ax.legend()
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    for j in range(N_ch):
        ax.hist(res[:, j]['peak'], bins=1000, histtype='step', label=f'ch{j}')
    ax.set_xlabel('peak')
    ax.set_ylabel('entries')
    ax.set_yscale('log')
    ax.legend()
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    ax.hist(res[:, 0]['baseline'], bins=1000, histtype='step', label='ch0')
    ax.set_yscale('log')
    ax.set_xlabel('baseline')
    ax.set_ylabel('entries')
    ax.legend()
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    ax.hist(res[:, 1]['baseline'], bins=1000, histtype='step', label='ch1')
    ax.set_yscale('log')
    ax.set_xlabel('baseline')
    ax.set_ylabel('entries')
    ax.legend()
    pdf.savefig(fig)

