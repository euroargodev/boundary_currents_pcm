# "BC monitor" data output

There should be one file for each Boundary Current (BC) and for each monitors.

These monitors are hourly updated automatically with Github actions.

**Note**:  
- Files are updated only if the content has changed between 2 runs.
- Since csv index files have a ``# Date of update :`` line in the header, they look the most recent files above. But the list of profiles they contain may not change on each run.

## Census of profiles in BC

### ``BC_<BC-NAME>_index.txt``

These are the last 10 days GDAC-like profile index.  
Produced by ``cli/check_save_status.py``.

To load these index with [argopy](https://github.com/euroargodev/argopy), you can do the following:
```python
import os
from argopy.stores.argo_index_pd import indexstore_pandas as indexstore
index_file = "https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GoC_index.txt"
idx = indexstore(host=os.path.split(index_file)[0], index_file=os.path.split(index_file)[1])
index = idx.to_dataframe()
```

### ``BC_<BC-NAME>_status.json`` 
These are the last 10 days number of profiles reported.  
Produced by ``cli/check_save_status.py``. 

This is meant to be used with shields badges like:
```md
![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_status.json)
```
to produce badges like:  
![index](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_GSE_tight_status.json)


## PCM analysis results

### ``BC_<BC-NAME>_index_classified.png``

Figures with PCM analysis results from profiles of the last 10 days index.    
Produced by ``cli/load_classif_save.py``.

### ``BC_<BC-NAME>_index_classified.txt``

These are the results of the PCM analysis performed on the last 10 days GDAC-like profile index.  
Produced by ``cli/load_classif_save.py``.