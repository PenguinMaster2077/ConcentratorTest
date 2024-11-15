'''
transfer the binary data into hdf5
'''

class Reader():
    def __init__(self, filename, N_ch, length=0):
        self.filename = filename
        self.file_data = np.memmap(filename, dtype='uint16', mode='r')
        # HEADER value
        self.HEADER, self.TAIL = 31354, 42919
        self._N_ch = N_ch
        self.length = length
    def calculate_pack_indices(self, arr, header, tail, length=0):
        '''
        calculate_pack_indices calculates the pack indices of data in arr based on header and tail
        arr    : numpy 1-d array that contains data from one board
        header : header of data per trigger
        tail   : tail of data per trigger
        length : length of data per trigger
        '''
        header_flag = (arr == header)
        header_indices = np.where((np.diff(header_flag) == -1))[0]
        if length == 0:
            tail_flag = (arr == tail)
            tail_indices = np.where((np.diff(tail_flag) == 1))[0]
        else:
            tail_indices = header_indices + length
        
        return header_indices, tail_indices, header_indices.shape[0]
    def checkPackNum(self, header_indices, num_limit=100000):
        if header_indices.shape[0] < num_limit:
            return True
        else:
            return False
    def extract_data(self):
        '''
        extract_data extracts data from arr based on header_indices and tail_indices
        arr            : numpy 1-d array that contains data from one board
        '''
        header_indices, tail_indices, N_event = self.calculate_pack_indices(self.file_data, self.HEADER, self.TAIL, self.length * self.N_ch)
        return self.file_data[header_indices:tail_indices].reshape(N_event, self.N_ch, -1)
    def close(self):
        self.file_data._mmap.close()

import argparse
import numpy as np, h5py
psr = argparse.ArgumentParser()
psr.add_argument('-i', dest='ipt', type=str, help='input binary file')
psr.add_argument('-o', dest='opt', type=str, help='output hdf5 file')
psr.add_argument('-N', type=int, default=1000, help='waveform length')
psr.add_argument('-N_ch', type=int, default=2, help='waveform length')
args = psr.parse_args()

reader = Reader(args.ipt, args.N_ch, args.N)
waveform = reader.extract_data()
reader.close()
with h5py.File(args.opt, 'w') as opt:
    opt.create_dataset('waveform', data=waveform, compression='gzip')
