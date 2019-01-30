#!/usr/bin/env python

from smalldata import MPIDataSource
from smalldata import SmallData

import numpy as np
import h5py

def yield_events(filename):
    with h5py.File(filename, 'r') as f:
        n_events = f['/data/JF07T32V01/data'].shape[0]
        timestamps = np.arange(n_events)
        print('Found %d events in file %s' % (n_events, filename))
        for i in range(10):
            event = {}
            event['timestamp'] = timestamps[i] # BETTER VALUE?
            event['data']      = np.array(f['/data/JF07T32V01/data'][i])
            yield event


ds = MPIDataSource(yield_events('/sf/bernina/data/p17743/res/waterJet_tests/scattering_WaterJet_test1.JF07T32V01.h5'))
smd = SmallData('example_output.h5', 'timestamp', keys_to_save=[])

for evt in ds.events():
    print(evt['timestamp'])
    smd.event(timestamp=evt['timestamp'],
              s=np.sum(evt['data'])) # evt is just a dict
smd.save()

