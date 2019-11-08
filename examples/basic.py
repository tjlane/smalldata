
import numpy as np
from smalldata import SmallData

# we assume you have some raw data to process that
# you can iterate over
raw_data = np.random.randn(100, 10)

# you can make custom callback functions that are
# called-back on every smd.event(...) call with
# the collected data as an argument
callbacks=[print]

smd = SmallData(servers=2,        # the number of file writers
                clients=4,        # the number of data processors
                filename='my.h5', # the HDF5 file to put results in
                callbacks=callbacks)

for i,data in enumerate(raw_data):

    # do some processing ...

    # save per-event data
    # here "i" is a timestamp or other unique ID
    smd.event(i, mydata=np.sum(data))

    # or use nested dictionaries to structure the output
    smd.event(i, {'group' : {'field' : np.arange(5)}})
              

# you can also save "summary data", typically at a lower frequency
if smd.summary:
    n_workers = smd.sum(1) # reduce across all cores
    smd.save_summary(n_workers=n_workers)

# finish up any last communication
smd.done()

