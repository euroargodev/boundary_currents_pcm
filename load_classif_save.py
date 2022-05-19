import pandas as pd
import xarray as xr
xr.set_options(display_style="html", display_expand_attrs=False)

# from argopy.stores.argo_index_pd import indexstore_pandas as indexstore

import sys, os
# sys.path.insert(0, os.sep.join([os.getcwd(), '..']))
from pcmbc.utilities import load_aviso_nrt, load_aviso_mdt

if __name__ == '__main__':
    # Get a short name from the dict_regions:
    BC = 'GSE tight'

    # The corresponding box:
    box = [-75., -48., 33, 45.5]

    WEKEO_USERNAME, WEKEO_PASSWORD = os.getenv('WEKEO_USERNAME'), os.getenv('WEKEO_PASSWORD')
    if not WEKEO_USERNAME:
        raise ValueError("No WEKEO_USERNAME in environment ! ")

    # index_file = "https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BCindex_%s.txt" % (BC.replace(" ", "_").replace(".", ""))
    # print("index_file", index_file)
    # idx = indexstore(host=os.path.split(index_file)[0], index_file=os.path.split(index_file)[1])
    # index = idx.to_dataframe()

    # aviso = load_aviso_nrt(box, index['date'].max(), WEKEO_USERNAME, WEKEO_PASSWORD, vname='sla')
    aviso = load_aviso_nrt(box, pd.to_datetime('now', utc=True), WEKEO_USERNAME, WEKEO_PASSWORD, vname='sla')
    print(aviso)

    # aviso_clim = load_aviso_mdt(box, index['date'].max(), WEKEO_USERNAME, WEKEO_PASSWORD, vname='mdt')
