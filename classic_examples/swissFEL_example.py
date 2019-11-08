#!/usr/bin/env python

"""
smalldata code for parallel processing at SwissFEL

try and run me, first in serial:
 $ python swissfel_example.py

then in parallel:
 $ mpirun -n 4 swissfel_example.py

... and look at the resulting 'example_output.h5'
"""


from smalldata import MPIDataSource
from smalldata import SmallData

import numpy as np
import h5py

from escape.parse import swissfel


class ExampleDataSource:
    """
    EXAMPLE ONLY.

    This class could be re-worked to better match SwissFEL data access patterns.
    
    The basic idea is that we need to define a function that returns per-shot
    data of interest. That 'event-built' data is then round-robined to different
    cores.
    """

    def __init__(self, file_path):

        # load data
        data = swissfel.parseScanEco_v01(file_path,
                                         createEscArrays=True,
                                         memlimit_mD_MB=50)

        jf7 = data['JF07T32V01']
        total_shots = jf7.data.shape[jf7.eventDim]

        # get event IDs at 100Hz and match with JF pulse IDs at 25 Hz
        jf_pulse_id = jf7.eventIds                  # event ID at 25 Hz
        evcodes = data['SAR-CVME-TIFALL5:EvtSet']   # trigger codes in 256 channels at 100 Hz
        laser_on_100Hz = evcodes.data[:,20]         # laser trigger at 100 Hz

        pulse_id = evcodes.eventIds                 # event ID at 100 Hz
        matched_id = np.isin(pulse_id, jf_pulse_id) # matched IDs at 25 Hz in 100 Hz arrays
        assert (np.sum(matched_id) ==  len(jf_pulse_id))
        
        self.jf_pulse_id = jf_pulse_id
        self.jf7         = jf7
        self.laser_on_100Hz = laser_on_100Hz
        self.matched_id = matched_id

        return 

    
    def __call__(self, i):
        event = {'pulse_id' : self.jf_pulse_id[i],
                 'jf7' :      self.jf7.data[i].compute(),
                 'laser_on' : self.laser_on_100Hz[self.matched_id][i].compute()
                }
        return event



# (1) create a function that produces "event built" shot data in some fashion
event_generator = ExampleDataSource('/sf/bernina/data/p17743/res/scan_info/run0069_droplets_10um_2mm.json')


# (2) all this really does is round-robin the events from (1)
ds = MPIDataSource(event_generator, 
                   break_after=10,           # only do 10 shots
                   global_gather_interval=3) # gather every 3 shots


# (3) finally, create a handle to a 'smalldata' HDF5 that contains the results
#     here, pulse_id is used to ensure shots are not duplicated and appear
#     in time-sorted order in the final file
smd = ds.small_data('example_output.h5', 'pulse_id')


# loop over events & perform analysis
jf7_run_2dsum = np.zeros(( 16384, 1024 )) 

for i,evt in enumerate(ds.events()):

    print('shot: %s, pulse_id = %d' % (i, evt['pulse_id']))

    # do whatever calculations you like
    jf7_image      = evt['jf7']
    jf7_run_2dsum += jf7_image

    # save per-event data to HDF5
    smd.event(pulse_id     = evt['pulse_id'], # this name is special
              jf7_shot_sum = np.sum(jf7_image),
              is_laser_on  = evt['laser_on'])

    # you can call event many times per event
    # and also use dictionaries to make a heirarchy in the final HDF5
    smd.event({'base' : {'field1' : 1,
                         'field2' : 2}},
              pulse_id = evt['pulse_id'])


smd.sum(jf7_run_2dsum)              # sum across all cores
smd.save(jf7_2dsum = jf7_run_2dsum) # save run summary data


