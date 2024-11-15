'''
transfer the binary data into hdf5
'''

class Reader():
    def __init__(self, filename, N_ch, length=0, trig_length=4):
        self.filename = filename
        self.file_data = np.memmap(filename, dtype='int16', mode='r')
        # HEADER value
        self.HEADER, self.TAIL = 31354, 42919
        self.N_ch = N_ch
        self.length = length
        self.trig_length = 4
    def calculate_pack_indices(self, arr, header, tail, length=0):
        '''
        calculate_pack_indices calculates the pack indices of data in arr based on header and tail
        arr    : numpy 1-d array that contains data from one board
        header : header of data per trigger
        tail   : tail of data per trigger
        length : length of data per trigger
        '''
        self.header_flag = (arr == header)
        header_flag_diff = np.diff(self.header_flag.astype(int))
        header_indices = []
        for i in np.where(header_flag_diff == -1)[0] + 1:# diff need +1 to set the true start
            if np.sum(self.header_flag[(i-3):i])==3:
                header_indices.append(i)
        header_indices = np.array(header_indices)
        if length == 0:
            self.tail_flag = (arr == tail)
            tail_indices = np.where((np.diff(self.tail_flag.astype(int)) == 1))[0]
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
        self.header_indices, self.tail_indices, N_event = self.calculate_pack_indices(self.file_data, self.HEADER, self.TAIL, self.length * self.N_ch)
        waveform = np.empty((N_event-1, self.length * self.N_ch), dtype='int16')
        trig = np.empty((N_event-1, self.trig_length), dtype='int16')
        # the order of the binary: [ch2, ch2, ch2, ch2, ch1, ch1, ch1, ch1, ch2...]
        # TODO: -2 for trigger in different board
        for i in range(N_event-1):
            # TODO: /4, waveform is padding with 2 0, need /4
            waveform[i] = self.file_data[self.header_indices[i]:self.tail_indices[i]] / 4
            trig[i] = self.file_data[self.tail_indices[i]:(self.tail_indices[i]+4)]
        return waveform.reshape(N_event-1, -1, self.N_ch, 4).transpose(0, 2, 1, 3).reshape(N_event-1, self.N_ch, -1), trig
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
waveform, trig = reader.extract_data()
reader.close()
with h5py.File(args.opt, 'w') as opt:
    opt.create_dataset('Readout/Waveform', data=waveform, compression='gzip')
    opt.create_dataset('Readout/Triggerinfo', data=trig, compression='gzip')
