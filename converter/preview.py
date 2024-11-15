'''
preview the data
'''
import h5py
def loadH5(f):
    with h5py.File(f) as ipt:
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
    exit(0)
res = np.empty((waves.shape[0], N_ch), dtype=[('eid', np.int32), ('Q', np.float64), ('baseline', np.float64), ('peak', np.float64), ('peakPos', np.int32)])

# omit the first 200ns, which is used as baseline
pre_l, w_l, w_r = 200, 20, 70
for i, ws in enumerate(waves):
    for j in range(N_ch):
        w = ws[j]
        baseline = np.mean(w[:pre_l])
        peakPos = np.argmin(w[pre_l:]) + pre_l
        peak = baseline - w[peakPos]
        Q = np.sum(baseline - w[(peakPos-w_l):(peakPos+w_r)])
        res[i, j] = (i, Q, baseline, peak, peakPos)
with PdfPages(args.opt) as pdf:
    fig, ax = plt.subplots()
    for j in range(N_ch):
        ax.hist(res[:, j]['peakPos'](res[:, j]['peak']>30), bins=1000, range=[0, 1000], histtype='step')
    ax.set_xlabel('t')
    ax.set_ylable('entries')
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    for j in range(N_ch):
        ax.hist(res[:, j]['Q'], bins=1000, histtype='step')
    ax.set_xlabel('charge')
    ax.set_ylable('entries')
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    for j in range(N_ch):
        ax.hist(res[:, j]['peak'], bins=1000, histtype='step')
    ax.set_xlabel('peak')
    ax.set_ylable('entries')
    pdf.savefig(fig)

