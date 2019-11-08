# smalldata
Big data is all the rage, but true masters know its not the size of the data that counts.


## purpose

Many data processing workflows benefit from exposing easy parallelism. Smalldata
aims to provide very simple to deploy parallelism for a single for loop.

Nearly all XFEL-based experiments pre-process data with such a for loop. Smalldata
makes it possible to take a python script written for such an application and
quickly parallelize it to scale linearly to 1000s of cores.


## example

Here is a simple example of code that uses smalldata

```
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
```

You can run this script with MPI: `mpirun -n 6 python myscript.py`. It will output a single
file "my.h5". Note it also works in "serial" mode: `python myscript.py`


## how it works

The idea behind smalldata is fairly simple. Many cores are allocated via MPI. These
are split into "server" and "client" cores. The clients perform the data processing,
and when `SmallData.event(...)` or `Smalldata.save_summary(...)` are called, send
a chunk of the (indicated) data over to a server process.

The servers write HFD5 files, one per server, as they receive this data. At the end
of the job, these partial HDF5 files are joined into a unified "view" using HDF5's
virtual datasets. This means you interact with the data as if it were all contained
in a single file.

Missing data are handled naturally using a fill value. It's possible to declare
a dataset "unaligned" simply by pre-pending that string to the data field's name.
Useful if you expect a lot of missing data and want to trade disk space for
alignment.

Using callbacks, it's possible to send data somewhere else besides HDF5. But that's
up to you ;).


## smalldata classic

There is a "v1" version of smalldata. It uses MPI collective communication (gather)
vs "v2", which uses asynchronous send/recv. This means v2 will scale much better.

As a result of asynchrony, the results from v2 are not guarneteed to be time-sorted.
This was possible in v1. So v1 is retained here, called "classic", but is unmaintained.





