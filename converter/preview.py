'''
preview the data
'''
import h5py
def loadH5(f):
    print(f'load file {f}')
    with h5py.File(f, 'r') as ipt:
        waves = ipt['Readout/Waveform'][:]
    return waves
import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
psr = argparse.ArgumentParser()
psr.add_argument('-i', dest='ipt', nargs='+', help='input files')
psr.add_argument('-o', dest='opt', type=str, help='output pdf')
psr.add_argument('-N_ch', type=int, help='number of channels')
psr.add_argument('-N', type=int, help='maximum number of waves')
psr.add_argument('-Ns', type=int, help='number of overlap the waves')
psr.add_argument('--onlywave', action='store_true', default=False, help='only plot the waves without the simple analysis')
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
res = np.empty((waves.shape[0], N_ch), dtype=[('eid', np.int32), ('Q', np.float64), ('baseline', np.float64), ('peak', np.float64), ('peakPos', np.int32)])

# omit the first 100ns, which is used as baseline
pre_l, w_l, w_r = 100, 20, 70
for i, ws in enumerate(waves):
    for j in range(N_ch):
        if j==1:
            w = -ws[j]
        else:
            w = ws[j]
        baseline = np.mean(w[:pre_l])
        peakPos = np.argmin(w[pre_l:]) + pre_l
        peak = baseline - w[peakPos]
        Q = np.sum(baseline - w[(peakPos-w_l):(peakPos+w_r)])
        res[i, j] = (i, Q, baseline, peak, peakPos)
with PdfPages(args.opt) as pdf:
    fig, ax = plt.subplots()
    for j in range(N_ch):
        ax.hist(res[:, j]['peakPos'][res[:, j]['peak']>30], bins=1000, range=[0, 1000], histtype='step', label=f'ch{j}')
    ax.set_yscale('log')
    ax.set_xlabel('t')
    ax.set_ylabel('entries')
    ax.set_title('peak pos (peak>3mV)')
    ax.legend()
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    res_text = 'Total entries:{}\n'.format(waves.shape[0])
    binwidth, ranges = 3, [120, 990] # choose 3ns as binwidth, range (120, 990)
    bins = int((ranges[1] - ranges[0]) / binwidth)
    for j in range(N_ch):
        h = ax.hist(res[:, j]['peakPos'][res[:, j]['peak']>30], bins=bins, range=ranges, histtype='step', label=f'ch{j}')
        # choose 300ns window
        pedestal = np.sum(h[0][-100:])
        signal = np.sum(h[0][:100])
        darkRate = pedestal / 300 / waves.shape[0]*1E6
        res_text += 'ch{} signal entries:{}, ratio{:.2f}, darkRate:{:.2f}kHz\n'.format(j, signal-pedestal, (signal-pedestal)/waves.shape[0], darkRate)
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

