# Data produced for BC monitoring

There should be one file for each Boundary Current (BC) and for each monitor.

**Note**:  
- Files are updated only if the content has changed between 2 runs.
- Since csv index files have a ``# Date of update :`` line in the header, they look the most recent files. But the list of profiles they contain may not change on each run.

## ``BCindex*.txt``

These are the last 10 days GDAC-like profile index.  
Produced by ``check_save_status.py``.

To load these index with [argopy](https://github.com/euroargodev/argopy), you can do the following:
```python
import os
from argopy.stores.argo_index_pd import indexstore_pandas as indexstore
index_file = "https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BCindex_GoC.txt"
idx = indexstore(host=os.path.split(index_file)[0], index_file=os.path.split(index_file)[1])
index = idx.to_dataframe()
```

## ``BCstatus*.json`` 
These are the last 10 days number of profiles reported.  
Produced by ``check_save_status.py``. 

This is meant to be used with shields badges like:
```md
![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BCstatus_GSE_tight.json)
```
to produce badges like:  
![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BCstatus_GSE_tight.json)

