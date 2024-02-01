import os
from argopy.stores.argo_index_pd import indexstore_pandas as indexstore
import copernicusmarine


def load_aviso_nrt(a_box, a_date, vname='sla'):
    if not isinstance(vname, list):
        vname = [vname]

    ds = copernicusmarine.open_dataset(
        dataset_id="cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D",
        minimum_longitude=a_box[0],
        maximum_longitude=a_box[1],
        minimum_latitude=a_box[2],
        maximum_latitude=a_box[3],
        start_datetime=a_date.strftime('%Y-%m-%d 00:00:00'),
        end_datetime=a_date.strftime('%Y-%m-%d 00:00:00'),
        variables=vname,
    )

    return ds


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
    idx = indexstore(host=os.path.split(index_file)[0], index_file=os.path.split(index_file)[1], convention='ar_index_global_prof')
    index = idx.to_dataframe()
    WMO_list = idx.read_wmo()

    # Load AVISO data for the map:
    aviso_nrt = load_aviso_nrt(box, index["date"].max())

    print(aviso_nrt)
