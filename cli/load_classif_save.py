import os

import numpy as np
# import pandas as pd
# import xarray as xr
# xr.set_options(display_style="html", display_expand_attrs=False)
import warnings

import pyxpcm
import argopy
from argopy import DataFetcher
from argopy.stores.argo_index_pd import indexstore_pandas as indexstore
from pcmbc.utilities import from_misc_pres_2_std_depth, load_aviso_nrt, load_aviso_mdt
import matplotlib.pyplot as plt


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


def load_and_classify(this_m, this_df):
    # Load data for this profile:
    try:
        ds = DataFetcher(src='erddap', mode='expert', cache=True).profile(this_df['wmo'].values,
                                                                          this_df['cycle_number'].values).data
        ds = ds.argo.filter_data_mode()
        dsp_float = ds.argo.point2profile()
        # Rq: Here I use the 'expert' mode in order to only filter variables according to DATA MODE. If I use the 'standard' mode, data are
        # also filtered by QC, which can reduce the number of "classifiable" profiles.

        try:
            # Process profile:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dsi_float = from_misc_pres_2_std_depth(this_m, dsp_float, feature_name='temperature')

            # Predict:
            this_m.predict(dsi_float, features={'temperature': 'TEMP', 'salinity': 'PSAL'}, dim='DEPTH_INTERPOLATED',
                           inplace=True)

            # Add predictions to this float:
            this_df['pcm_label'] = dsi_float['PCM_LABELS'].values

        except:
            this_df['pcm_label'] = 999
            pass

    except:
        try:
            print("Error with WMO=%i, CYC=%i: %s" % (this_df['wmo'].values, this_df['cycle_number'].values,
                                                     argopy.dashboard(wmo=this_df['wmo'].values,
                                                                      cyc=this_df['cycle_number'].values,
                                                                      url_only=True)))
        except:
            print("Error with WMO=%i, CYC=%i: %s" % (this_df['wmo'].values, this_df['cycle_number'].values,
                                                     argopy.dashboard(wmo=this_df['wmo'].values, url_only=True)))
            pass
        this_df['pcm_label'] = np.nan

    return this_df


if __name__ == "__main__":

    #######################
    # Define all parameters specific to a given Boundary Current
    #######################

    # Get a short name from the dict_regions:
    BC = "GSE tight"
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
        "https://raw.githubusercontent.com/euroargodev/boundary_currents_pcm/main/data/BCindex_%s.txt"
        % (BC.replace(" ", "_").replace(".", ""))
    )
    idx = indexstore(host=os.path.split(index_file)[0], index_file=os.path.split(index_file)[1])
    index = idx.to_dataframe()
    WMO_list = idx.read_wmo()

    # Download the PCM for this BC:
    pcm_file = (
        "https://github.com/euroargodev/boundary_currents_pcm/blob/main/pcmbc/assets/%s?raw=true"
        % pcm_name
    )
    with argopy.stores.httpstore(cache=True).open(pcm_file) as f:
        open(pcm_name, "wb").write(f.read())
    m = pyxpcm.load_netcdf(pcm_name)

    # Load AVISO data for the map:
    try:
        aviso_nrt, aviso_mdt = download_aviso_from_wekeo(box, index["date"].max())
    except:
        aviso_nrt, aviso_mdt = None, None
        pass
    # download_aviso_from_wekeo(box, pd.to_datetime('now', utc=True))
    # print(aviso_nrt)
    # print(aviso_mdt)

    #######################
    # Load floats data and classify them
    #######################

    # Prepare index with new columns:
    index['cycle_number'] = np.nan
    index['url'] = np.nan
    index['pcm_label'] = np.nan

    # Then add cycle number of each profiles:
    index['cycle_number'] = index.apply(lambda x: int(x['file'].split("/")[-1].split("_")[-1].split(".nc")[0]), axis=1)

    # Add url to profiles:
    for prof, df in index.groupby(['wmo', 'cycle_number']):
        wmo, cyc = prof[0], prof[1]
        try:
            df['url'] = argopy.dashboard(wmo=df['wmo'].values, cyc=df['cycle_number'].values, url_only=True)
            index = index.mask(np.logical_and(index['wmo'] == wmo, index['cycle_number'] == cyc), df)
        except:
            pass

    # Load profiles data and classify:
    # pcm_label==999: could not interpolate and classify for this PCM
    # pcm_label==NaN: could not laod the data
    for prof, df in index.groupby(['wmo', 'cycle_number']):
        wmo, cyc = prof[0], prof[1]
        df_updated = load_and_classify(m, df)
        index = index.mask(np.logical_and(index['wmo'] == wmo, index['cycle_number'] == cyc), df_updated)

    # Re-order class labels according to the PCM best fit ordering
    index['reordered_label'] = index.apply(
        lambda x: korder[int(x['pcm_label'])] if (not np.isnan(x['pcm_label']) and x['pcm_label'] < 999) else np.nan,
        axis=1)
    index['reordered_label'] = index.apply(
        lambda x: 999 if (np.isnan(x['reordered_label']) and x['pcm_label'] >= 999) else x['reordered_label'], axis=1)

    #######################
    # Figures
    #######################

    yticklabels = {}
    for k in m:
        # print(np.count_nonzero(index['pcm_label']==k))
        n = np.count_nonzero(index['reordered_label'] == korder[k])
        print("%i profiles in k=%i (%s)" % (n, korder[k], class_descriptions[korder[k]]))
        yticklabels[korder[k]] = "Class #%i:%s\n%i profiles" % (korder[k], class_descriptions[korder[k]], n)
    print(yticklabels)

    proj = argopy.plot.utils.cartopy.crs.PlateCarree()
    dx, dy = 1, 1  # How much to extent the map contours wrt to the data set real domain
    subplot_kw = {'projection': proj, 'extent': np.array(box) + np.array([-dx, +dx, -dy, +dy])}
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 5), dpi=120, facecolor='w', edgecolor='k',
                           subplot_kw=subplot_kw)

    # topo['elevation'].plot.contour(levels=[-2000, -1000], ax=ax, colors='b', zorder=0, linewidths=0.5)

    if aviso_nrt:
        # aviso_clim['mdt'].isel(time=0).plot.contour(levels=np.arange(-2,2,0.1), ax=ax, colors='red', zorder=0, linewidths=0.5)
        aviso_nrt['sla'].isel(time=0).plot.contour(levels=np.arange(-2, 2, 0.1), ax=ax, colors='gray', zorder=0, linewidths=0.5)

    classified = index.where(np.logical_and(index['reordered_label'] < 999, ~np.isnan(index['reordered_label'])))
    sc = ax.scatter(classified['longitude'], classified['latitude'], s=28, c=classified['reordered_label'],
                    cmap=m.plot.cmap(name=cname), transform=proj, vmin=0, vmax=m.K)
    cbar = m.plot.colorbar(ax=ax, name=cname)
    cbar.ax.set_yticklabels([yticklabels[k] for k in m])

    impossible = index.where(index['reordered_label'] >= 999)
    ax.plot(impossible['longitude'], impossible['latitude'], '*', color='pink', transform=proj)

    missing = index.where(np.isnan(index['reordered_label']))
    ax.plot(missing['longitude'], missing['latitude'], '.', color='lightgray', transform=proj)

    argopy.plot.utils.latlongrid(ax)
    ax.add_feature(argopy.plot.utils.land_feature)
    ax.set_title(
        "Gulf Stream PCM monitor\nCurrently %i floats in the area, reporting %i profiles (%i classified)\nFrom %s to %s" % (
            len(WMO_list),
            len(index),
            len(np.where(index['pcm_label'])[0]),
            index['date'].min().strftime('%Y/%m/%d %H:%M'),
            index['date'].max().strftime('%Y/%m/%d %H:%M')),
        horizontalalignment='center', fontsize=12)

    out_name = os.path.join("../data", os.path.split(index_file)[1].replace(".txt", ".png"))
    plt.savefig(out_name, bbox_inches='tight', pad_inches=0.1)

    # Tear down
    os.remove(pcm_name)
    if aviso_nrt:
        os.remove(aviso_nrt.attrs['local_file'])
    if aviso_mdt:
        os.remove(aviso_mdt.attrs['local_file'])
