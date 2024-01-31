import os
import numpy as np
import copernicusmarine


def from_misc_pres_2_std_depth(
    a_pcm, ds_profiles, feature_name="temperature", max_pres_delta=50
):
    """Convert Argo dataset from irregular pressure to standard depth levels.

    Since PCM operates on standard depth levels, we first need to interpolate Argo original data on standard pressure levels
    (if you get an error here, make sure the PCM depth axis is smaller that the depth range of training set).

    Standard pressure levels are the absolute values of the PCM feature depth axis with an additional deepest level set to
    the maximum pressure + max_pres_delta.

    We then need use GSW to compute depths from Argo standard pressure levels and replace the vertical pressure axis with this depth.

    Parameters
    ----------
    a_pcm: :class:'pyxpcm.models'
        A PCM instance from which to extract a feature depth axis.
    ds_profiles: :class:'xarray.DataSet'
        The raw Argo data collection of profiles to transform (supposedly as returned by argopy).

    Other Parameters
    ----------------
    feature_name: str, default: 'temperature'
        Name of the feature to use to extract a PCM axis
    max_pres_delta: float, default: 50
        Pressure delta to increase the deepest standard pressure levels.

    Returns
    -------
    :class:'xarray.DataSet'
        A new data set with all measurements interpolated on the PCM feature axis depth levels.

    Raises
    ------
    ValueError
        If the interpolated profiles don't match the PCM axis which hence, will fail to fit.
    """
    import gsw

    # STEP 1

    # Get the PCM depth axis:
    pcm_dpt_axis = a_pcm.features[feature_name]

    # Define a pressure axis accordingly:
    # (possibly increase max_pres_delta to reach deeper values to match the PCM axis)
    standard_pressure_levels = np.append(
        np.abs(pcm_dpt_axis), np.max(np.abs(pcm_dpt_axis)) + max_pres_delta
    )

    # Interpolate raw Argo data onto this regular pressure axis:
    dsi = ds_profiles.argo.interp_std_levels(
        std_lev=standard_pressure_levels, axis="PRES"
    )
    dsi = dsi.assign_coords({"N_PROF": np.arange(len(dsi["N_PROF"]))})

    # STEP 2

    # Then compute depth of the regular pressure axis and replace the dataset z-axis from pressure to depth:
    zi = gsw.z_from_p(
        dsi["PRES_INTERPOLATED"],
        dsi["LATITUDE"],
        geo_strf_dyn_height=0,
        sea_surface_geopotential=0,
    )
    dsi = dsi.assign_coords({"PRES_INTERPOLATED": zi.isel(N_PROF=0).values})
    dsi["PRES_INTERPOLATED"].attrs["long_name"] = "Depth"
    dsi["PRES_INTERPOLATED"].attrs["unit"] = "m"
    dsi["PRES_INTERPOLATED"].attrs["axis"] = "Z"
    dsi = dsi.rename({"PRES_INTERPOLATED": "DEPTH_INTERPOLATED"})

    # FINAL CHECK
    # Check that the transformed dataset is suited for the vertical axis of the PCM:
    if not dsi["DEPTH_INTERPOLATED"].min() <= pcm_dpt_axis.min():
        raise ValueError(
            "\nThe interpolated Argo data set is not going deep enough for this PCM. To fix this:\n"
            "- you can try to increase the maximum standard pressure level to make sure some data will go deep enough,\n"
            "- or you can also try to reduce the maximum depth of the PCM vertical axis"
        )

    return dsi


def from_stp_2_std(ds_profiles):
    """Convert dataset standard pressures to standard depths levels"""
    # Then compute depth of the regular pressure axis and replace the dataset z-axis from pressure to depth:
    import gsw

    zi = gsw.z_from_p(
        ds_profiles["PRES_INTERPOLATED"],
        ds_profiles["LATITUDE"],
        geo_strf_dyn_height=0,
        sea_surface_geopotential=0,
    )
    dsi = ds_profiles.assign_coords({"PRES_INTERPOLATED": zi.isel(N_PROF=0).values})
    dsi["PRES_INTERPOLATED"].attrs["long_name"] = "Depth"
    dsi["PRES_INTERPOLATED"].attrs["unit"] = "m"
    dsi["PRES_INTERPOLATED"].attrs["axis"] = "Z"
    dsi = dsi.rename({"PRES_INTERPOLATED": "DEPTH_INTERPOLATED"})
    return dsi


def process_list_in_parallel(
    item_processor,
    items,
    max_workers: int = 112,
    method: str = "thread",
    progress: bool = True,
    errors="ignore",
):
    """Process files independantly in parallel

    Use a Threads Pool by default for parallelization.

    Parameters
    ----------
    item_processor: function
        The function to call with on item value. Must have ``item`` as argument to receive item value.
    items: list
        List of items to process

    max_workers: int
        Maximum number of threads or processes
    method: str, efault: 'thread'
        The parallelization method to execute calls asynchronously:
            - ``thread``: use a pool of at most ``max_workers`` threads
            - ``process``: use a pool of at most ``max_workers`` processes
    progress: bool, default: True
        Display a progress bar with tqdm
    errors: str
        Should it 'raise' or 'ignore' errors. Default: 'ignore'

    Examples
    --------
    >>> data, failed = process_files_in_parallel(lambda file: os.path.getsize(file), file_list)

    """
    import concurrent.futures

    if progress:
        # from tqdm import tqdm
        from tqdm.notebook import tqdm

    if method == "thread":
        ConcurrentExecutor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        )
    else:
        if max_workers == 112:
            import multiprocessing

            max_workers = multiprocessing.cpu_count()
        ConcurrentExecutor = concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        )

    results = []
    failed = []

    with ConcurrentExecutor as executor:
        future_to_url = {
            executor.submit(item_processor, item=item): item for item in items
        }
        futures = concurrent.futures.as_completed(future_to_url)
        if progress:
            futures = tqdm(futures, total=len(items))

        for future in futures:
            data = None
            try:
                data = future.result()
            except Exception:
                failed.append(future_to_url[future])
                if errors == "ignore":
                    # print(
                    #     "Ignored error with this file: %s\nException raised: %s"
                    #     % (future_to_url[future], str(e.args)))
                    pass
                else:
                    raise
            finally:
                results.append(data)

    return results, failed


def cal_dist_matrix(lats, lons):
    """Calculate distance matrix

        Parameters
        ----------
        lats: latitude vector
        lons: longitude vector

        Returns
        ------
        Distance maytrix in int16

    Function taken from: https://github.com/euroargodev/DMQC-PCM/blob/main/PCM-design/PCM_utils_forDMQC/data_processing.py
    """
    from sklearn.metrics.pairwise import haversine_distances
    from math import radians

    lats_in_radians = np.array([radians(_) for _ in lats])
    lons_in_radians = np.array([radians(_) for _ in lons])
    coords_in_radians = np.column_stack((lats_in_radians, lons_in_radians))
    dist_matrix = haversine_distances(coords_in_radians).astype(np.float32)
    dist_matrix = dist_matrix * 6371  # multiply by Earth radius to get kilometers
    dist_matrix = dist_matrix.astype(np.int16)

    return dist_matrix


def get_regulargrid_dataset(
    ds_in,
    corr_dist,
    season="all",
    sample_dim="N_PROF",
    lat_dim="LATITUDE",
    lon_dim="LONGITUDE",
    tim_dim="TIME",
):
    """Re-sampling of the dataset selecting profiles separated by a minimum correlation distance

    Function taken from: https://github.com/euroargodev/DMQC-PCM/blob/main/PCM-design/PCM_utils_forDMQC/data_processing.py

        Parameters
        ----------
        ds: profiles dataset
        corr_dist: correlation distance
        season: choose season: 'DJF', 'MAM', 'JJA','SON' (default: 'all')

        Returns
        -------
        :class:`xarray.DataArray`
        Re-sampled dataset

    """

    ds = ds_in.copy()
    ds[sample_dim] = np.arange(len(ds[sample_dim]))
    # create mask
    mask_s = np.empty((1, len(ds[sample_dim].values)))
    mask_s[:] = np.NaN
    ds["mask_s"] = ([sample_dim], np.squeeze(mask_s))

    plus_degrees = corr_dist / 111 + 1  # from km to degrees

    # loop
    n_iterations = range(len(ds[sample_dim].values))

    for i in n_iterations:

        # Choose 1 profile randomly:
        random_p = np.random.choice(
            ds[sample_dim].where(np.isnan(ds["mask_s"]), drop=True).values,
            1,
            replace=False,
        )
        random_p = int(random_p[0])
        lat_p = ds[lat_dim].loc[{sample_dim: random_p}].values
        long_p = ds[lon_dim].loc[{sample_dim: random_p}].values

        # Subset the dataset around this profile (rectangular box):
        ds_slice = ds[[lat_dim, lon_dim, "mask_s"]]
        ds_slice = ds_slice.where(ds[lat_dim] > (lat_p - plus_degrees), drop=True)
        ds_slice = ds_slice.where(ds_slice[lat_dim] < (lat_p + plus_degrees), drop=True)
        ds_slice = ds_slice.where(
            ds_slice[lon_dim] > (long_p - plus_degrees), drop=True
        )
        ds_slice = ds_slice.where(
            ds_slice[lon_dim] < (long_p + plus_degrees), drop=True
        )
        random_p_i = np.argwhere(ds_slice[sample_dim].values == random_p)

        # Calculate the distance matrix (i.e. distance between all subset profiles and the random one):
        dist_matrix = cal_dist_matrix(
            ds_slice[lat_dim].values, ds_slice[lon_dim].values
        )

        # Points near than corr_dist = 1
        mask_dist = np.isnan(ds_slice["mask_s"].values) * 1
        dist_vector = np.array(np.squeeze(dist_matrix[:, random_p_i])).astype(
            "float"
        ) * np.array(mask_dist)
        dist_vector[dist_vector == 0] = np.NaN
        bool_near_points = dist_vector < corr_dist
        n_profiles_near_points = ds_slice[sample_dim].values[bool_near_points]

        # change mask
        ds["mask_s"][random_p] = 1
        ds["mask_s"][n_profiles_near_points] = 0

        # stop condition
        # print(sum(np.isnan(ds['mask_s'].values)))
        if np.any(np.isnan(ds["mask_s"])) == False:
            # print('no more points to delete')
            # print(i)
            break

    # choose season
    if "all" not in season:
        season_idxs = ds.groupby("%s.season" % tim_dim).groups

        season_select = []
        for key in season:
            season_select = np.concatenate(
                (season_select, np.squeeze(season_idxs.get(key)))
            )

        if len(season) == 1:
            season_select = np.array(season_select)

        season_select = np.sort(season_select.astype(int))
        ds = ds[{sample_dim: season_select}]

    ds_t = ds.where(ds["mask_s"] == 1, drop=True)

    del dist_matrix

    return ds_t


def reorder_class(this_ds, m, func, dim="pcm_class", sampling_dim="N_PROF"):
    """Reorder classes according to a specific metric

    Be careful, this has to be down every time a prediction is done, since the order/name of classes
    in the PCM instance are not modified !

    Parameters
    ----------
    this_ds: :class:`xarray.DataSet`
        The input dataset with PCM result variables
    m: :class:`pyxpcm.pcm`
        The PCM instance used to predict values in ``this_ds``
    func: :function:
        The function to call to reduce the dataset to single metric value for each class

    Returns
    -------
    :class:`xarray.DataSet`
        Where PCM_LABELS and all other array with the ``dim`` dimension have been updated.

    Examples
    --------
    # Reduce a dataset to a single metric value: maximum latitude:
    >>> reduce_by_lat = lambda x: np.nanmax(x['LATITUDE'])
    # Reduce a dataset to a single metric value: median of vertical mean temperature:
    >>> reduce_by_temp = lambda x: x['TEMP'].mean('DEPTH_INTERPOLATED').median().values[np.newaxis][0]
    # Apply:
    >>> dsi = reorder_class(dsi, m, reduce_by_temp, dim='pcm_class', sampling_dim='N_PROF')
    """

    class_metrics = []
    [
        class_metrics.append(func(this_ds.where(this_ds["PCM_LABELS"] == k, drop=True)))
        for k in m
    ]
    new_order = np.argsort(class_metrics)
    print(class_metrics, new_order)

    # Re-order the PCM dimension:
    # (this will automatically update variables with ``dim`` as dimension
    this_ds = this_ds[{dim: new_order}]
    this_ds[dim] = range(m.K)

    # Compute new labels for each profile:
    # (I could not figure how to run this on the whole array, without going through each profiles)
    new_labels = []
    for ii in range(len(this_ds[sampling_dim])):
        new_labels.append(np.argmax(this_ds["PCM_POST"][{sampling_dim: ii}].values))
    this_ds["PCM_LABELS"].values = new_labels

    return this_ds


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

def load_aviso_mdt(a_box, vname='mdt'):
    if not isinstance(vname, list):
        vname = [vname]

    ds = copernicusmarine.open_dataset(
        dataset_id="cnes_obs-sl_glo_phy-mdt_my_0.125deg_P20Y",
        minimum_longitude=a_box[0],
        maximum_longitude=a_box[1],
        minimum_latitude=a_box[2],
        maximum_latitude=a_box[3],
        variables=vname,
    )
    ds = ds.isel(time=0)
    return ds