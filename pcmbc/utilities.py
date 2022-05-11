import numpy as np
import gsw

def from_misc_press_2_std_depth(a_pcm, ds_profiles, feature_name='temperature', max_pres_delta=50):
    """Convert argo dataset from irregular pressure to standard depth levels.

    Since PCM operates on standard depth levels, we first need to interpolate Argo original data on standard pressure levels
    (if you get an error here, make sure the PCM depth axis is smaller that the depth range of training set).

    Standard pressure levels are the absolute values of the PCM feature depth axis with an additionnal deepest level set to
    the maximum pressure + max_pres_delta.

    We then need use GSW to compute depths from Argo standard pressure levels and replace the vertical pressure axis with this depth.

    Parameters
    ----------
    a_pcm: :class:'pyxpcm.models'
        A PCM instance from which to extract a feature depth axis.
    ds_profiles: :class:'xarray.DataSet'
        The raw Argo data collection of profiles to transform (supposidly as returned by argopy).

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
    # STEP 1

    # Get the PCM depth axis:
    pcm_dpt_axis = a_pcm.features[feature_name]

    # Define a pressure axis accordingly:
    # (possibly increase max_pres_delta to reach deeper values to match the PCM axis)
    standard_pressure_levels = np.append(np.abs(pcm_dpt_axis), np.max(np.abs(pcm_dpt_axis)) + max_pres_delta)

    # Interpolate raw Argo data onto this regular pressure axis:
    dsi = ds_profiles.argo.interp_std_levels(std_lev=standard_pressure_levels, axis='PRES')
    dsi = dsi.assign_coords({'N_PROF': np.arange(len(dsi['N_PROF']))})

    # STEP 2

    # Then compute depth of the regular pressure axis and replace the dataset z-axis from pressure to depth:
    zi = gsw.z_from_p(dsi['PRES_INTERPOLATED'], dsi['LATITUDE'], geo_strf_dyn_height=0, sea_surface_geopotential=0)
    dsi = dsi.assign_coords({'PRES_INTERPOLATED': zi.isel(N_PROF=0).values})
    dsi['PRES_INTERPOLATED'].attrs['long_name'] = 'Depth'
    dsi['PRES_INTERPOLATED'].attrs['unit'] = 'm'
    dsi['PRES_INTERPOLATED'].attrs['axis'] = 'Z'
    dsi = dsi.rename({'PRES_INTERPOLATED': 'DEPTH_INTERPOLATED'})

    # FINAL CHECK
    # Check that the transformed dataset is suited for the vertical axis of the PCM:
    if not dsi['DEPTH_INTERPOLATED'].min() <= pcm_dpt_axis.min():
        raise ValueError("\nThe interpolated Argo data set is not going deep enough for this PCM. To fix this:\n"
                         "- you can try to increase the maximum standard pressure level to make sure some data will go deep enough,\n"
                         "- or you can also try to reduce the maximum depth of the PCM vertical axis")

    return dsi