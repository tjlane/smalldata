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

import karabo_data


class ExampleDataSource:
    """
    EXAMPLE ONLY.

    This class could be re-worked to better match exFEL data access patterns.
    
    The basic idea is that we need to define a function that returns per-shot
    data of interest. That 'event-built' data is then round-robined to different
    cores.
    """

    def __init__(self, file_path):

        # load data
        self.run = karabo_data.RunDirectory(file_path)
        self.agipd_selector = self.run.select('*/DET/*', 'image.data')

        return 

    
    def __call__(self, i):
        tid, train_data = self.agipd_selector.train_from_index(i)
        stacked = karabo_data.stack_detector_data(train_data, 'image.data')
        event = {'train_id' : tid,
                 'agipd' :    stacked
                }
        return event



# (1) create a function that produces "event built" shot data in some fashion
event_generator = ExampleDataSource('/home/tjlane/p002214/raw/r0036')


# (2) all this really does is round-robin the events from (1)
ds = MPIDataSource(event_generator, 
                   break_after=10,           # only do 10 shots
                   global_gather_interval=3) # gather every 3 shots


# (3) finally, create a handle to a 'smalldata' HDF5 that contains the results
#     here, pulse_id is used to ensure shots are not duplicated and appear
#     in time-sorted order in the final file
smd = ds.small_data('example_output.h5', 'train_id')


# loop over events & perform analysis
run_2dsum = np.zeros(( 16, 512, 128 )) 

for i,evt in enumerate(ds.events()):

    print('train: %s, train_id = %d' % (i, evt['train_id']))

    # do whatever calculations you like
    image      = evt['agipd'][0,0]
    run_2dsum += image

    # save per-event data to HDF5
    smd.event(train_id     = evt['train_id'], # this name is special
              shot_sum = np.sum(image))

    # you can call event many times per event
    # and also use dictionaries to make a heirarchy in the final HDF5
    smd.event({'base' : {'field1' : 1,
                         'field2' : 2}},
              train_id = evt['train_id'])


smd.sum(run_2dsum)              # sum across all cores
smd.save(agpid_2dsum = run_2dsum) # save run summary data
smd.close()

