import sys, os

import numpy as np
# import pandas as pd
# import xarray as xr
# xr.set_options(display_style="html", display_expand_attrs=False)
import warnings
import matplotlib.pyplot as plt
from tqdm import tqdm

import pyxpcm
import argopy
from argopy import DataFetcher
from argopy.stores.argo_index_pd import indexstore_pandas as indexstore

sys.path.insert(0, os.sep.join([os.path.split(os.path.realpath(__file__))[0], '..']))
from pcmbc.utilities import from_misc_pres_2_std_depth, load_aviso_nrt, load_aviso_mdt


def download_aviso_from_wekeo(a_box, a_date):
    WEKEO_USERNAME, WEKEO_PASSWORD = (
        os.getenv("WEKEO_USERNAME"),
        os.getenv("WEKEO_PASSWORD"),
    )
    if not WEKEO_USERNAME:
        raise ValueError("No WEKEO_USERNAME in environment ! ")

    aviso = load_aviso_nrt(a_box, a_date, WEKEO_USERNAME, WEKEO_PASSWORD, vname="sla")
    aviso_clim = load_aviso_mdt(a_box, WEKEO_USERNAME, WEKEO_PASSWORD, vname="mdt")

    return aviso, aviso_clim


if __name__ == "__main__":

    #######################
    # Define all parameters specific to a given Boundary Current: Gulf Stream
    #######################

    # Get a short name from the dict_regions:
    BCname = "GSE tight"
    pcm_name = "PCM_GulfStream.nc"

    # The corresponding box:
    box = [-75.0, -48.0, 33, 45.5]

    # Also select the colormap to use for this PCM label plots:
    cname = 'Paired'

    # Define the possible re-ordering of class labels:
    # (this was determined in See PCM-GulfStream-step02-fit.ipynb)
    korder = [0, 3, 1, 2]

    class_descriptions = {
        0: 'Cold northern flank',
        1: 'Fuzzy cold',
        2: 'Fuzzy warm',
        3: 'Warm southern flank',
    }

    #######################
    # Load files necessary to start NRT processing
    #######################

    # Load the BC profile index:
    index_file = (
        "https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BC_%s_index.txt"
        % (BCname.replace(" ", "_").replace(".", ""))
    )
    idx = indexstore(host=os.path.split(index_file)[0], index_file=os.path.split(index_file)[1])
    index = idx.to_dataframe()
    WMO_list = idx.read_wmo()

    # Load AVISO data for the map:
    aviso_nrt, aviso_mdt = download_aviso_from_wekeo(box, index["date"].max())

    print(aviso_nrt)
    print(aviso_mdt)

    # Tear down
    if aviso_nrt:
        os.remove(aviso_nrt.attrs['local_file'])
    if aviso_mdt:
        os.remove(aviso_mdt.attrs['local_file'])
