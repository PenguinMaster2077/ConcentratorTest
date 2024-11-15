'''
preview the data
'''
def loadH5(f):
    return waves
import argparse
import matplotlib.pyplot as plt
import matplotlib.backend.PdfPages as PdfPages
import numpy as np
psr = argparse.ArgumentParser()
psr.add_argument('-i', dest='ipt', nargs='+', help='input files')
psr.add_argument('-o', dest='opt', type=str, help='output pdf')
psr.add_argument('-N', type=int, help='maximum number of waves')
psr.add_argument('-Ns', type=int, help='number of overlap the waves')
args = psr.parse_args()

waves = np.concatenate([loadH5(f) for f in args.ipt])
res = np.empty(waves.shape[0], dtype=[('eid', np.int32), ('Q', np.float64), ('baseline', np.float64), ('peak', np.float64), ('peakPos', np.int32)])

# omit the first 200ns, which is used as baseline
pre_l, w_l, w_r = 200, 20, 70
for i, w in enumerate(waves):
    baseline = np.mean(w[:pre_l])
    peakPos = np.argmin(w[pre_l:]) + pre_l
    peak = baseline - w[peakPos]
    Q = np.sum(baseline - w[(peakPos-w_l):(peakPos+w_r)])
    res[i] = (i, Q, baseline, peak, peakPos)
with PdfPages(args.opt) as pdf:
    fig, ax = plt.subplots()
    ax.hist(res['peakPos'], bins=1000, range=[0, 1000], histtype='step')
    ax.set_xlabel('t')
    ax.set_ylable('entries')
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    ax.hist(res['Q'], bins=1000, histtype='step')
    ax.set_xlabel('charge')
    ax.set_ylable('entries')
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    ax.hist(res['peak'], bins=1000, histtype='step')
    ax.set_xlabel('peak')
    ax.set_ylable('entries')
    pdf.savefig(fig)

    fig, ax = plt.subplots()
    for i in range(args.Ns)
        ax.plot(waves[i])
    ax.set_xlabel('t')
    ax.set_ylable('ADC')
    pdf.savefig(fig)


