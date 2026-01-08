import regionmask
import pandas as pd
import time
import os
import json
import argopy
# from argopy import IndexFetcher as ArgoIndexFetcher
from argopy import ArgoIndex


def rect_box(SW,NE):
    # SW: lon_south_west, lat_south_west
    # NE: lon_north_east, lat_north_east
    return [[SW[0],SW[1]],[NE[0],SW[1]],[NE[0],NE[1]],[SW[0],NE[1]]]


def get_region_list():

    # Create the list of regionmask.Regions:

    dict_regions = {
        # 'NATL': {'box': [-80,0.,15,65], 'name': 'North Atlantic'},
        'GSE tight': {'box': [-75.,-48.,33,45.5], 'name': 'Gulf Stream Extension'},
        # 'GSE': {'box': [-75.,-35.,33,50.], 'name': 'Gulf Stream Extension'},

        # 'GoC tight': {'box': [-9.,-6,33.,37.5], 'name': 'Gulf of Cadiz'},
        'GoC': {'box': [-10.,-6,32.,38.5], 'name': 'Gulf of Cadiz'},

        'West. Med.': {'box': [-1.,5,35,42.], 'name': 'Western Mediterranean Sea'},
        'Lig. Sea': {'box': [5.,10,42.,44.5], 'name': 'Ligurian Sea'},

        'EGC': {'box': [-20.,-5,69,77], 'name': 'Eastern Greenland Current'},
    }

    boxes, numbers, names, abbrevs, sources = [], [], [], [], []
    for ii, r in enumerate(dict_regions.items()):
        numbers.append(ii)
        names.append(r[1]['name'])
        abbrevs.append(r[0])
        # Last 10 days:
        t0 = pd.to_datetime('now', utc=True)
        r[1]['box'].append((t0 - pd.Timedelta("240 hours")).strftime('%Y-%m-%d %H:%M:%S'))
        r[1]['box'].append(t0.strftime('%Y-%m-%d %H:%M:%S'))
        boxes.append(rect_box([r[1]['box'][0],r[1]['box'][2]],[r[1]['box'][1],r[1]['box'][3]]))
        sources.append(None)
    regions = regionmask.Regions(boxes, numbers, names, abbrevs, name='BCmask', source=sources)

    return dict_regions, regions


def analyse_regions(dict_regions, regions, cachedir):
    print("\nLoad index for regions:")
    for r in regions:
        print("%30s..." % r.name)
        index_box = dict_regions[r.abbrev]['box']
        dict_regions[r.abbrev]['long_name'] = r.name
        dict_regions[r.abbrev]['name'] = r.abbrev
        dict_regions[r.abbrev]['index'] = []
        dict_regions[r.abbrev]['N_PROF'] = 0
        dict_regions[r.abbrev]['N_WMO'] = 0
        max_try = 10
        counter = 1
        while counter < max_try:
            # print(counter)
            try:
                idx = ArgoIndex(cache=True, cachedir=cachedir).query.box(index_box)
                dict_regions[r.abbrev]['index'] = idx
                dict_regions[r.abbrev]['N_PROF'] = idx.N_MATCH
                dict_regions[r.abbrev]['N_WMO'] = len(idx.read_wmo())
                counter = max_try + 1
            except argopy.errors.DataNotFound:
                counter = max_try + 1
                pass
            except argopy.errors.GdacPathError:
                print("%30s: GdacPathError, trying again in 30 seconds ... (%i/%i)" % (" ", counter, max_try))
                time.sleep(30)
                counter += 1
        if counter == max_try:
            print("%30s: Maximum attempts reached, can't get index !" % " ")
        else:
            print("%30s: %i profiles in the last 10 days" % (" ", dict_regions[r.abbrev]['N_PROF']))

    return dict_regions, regions


def save_this_region_endpoint(a_region, out_dir='data'):
    # Generate files like:
    # {"schemaVersion": 1, "label": "Gulf Stream Extension", "message": "51 profiles", "style": "social", "color": "green"}
    # to be used with:
    # https://img.shields.io/endpoint?url=https://api.ifremer.fr/argopy/data/BCstatus_GSE_tight.json
    label = "%s" % a_region['long_name']
    # status = "%i profiles" % a_region['N_PROF']
    status = "%i profiles (%i floats)" % (a_region['N_PROF'], a_region['N_WMO'])

    # Create json file with full results for badge:
    color = 'green'
    style = 'social'
    message = status

    data = {}
    data['schemaVersion'] = 1
    data['label'] = label
    data['message'] = message
    data['style'] = style
    data['color'] = color
    outfile = os.path.join(out_dir, 'BC_%s_status.json' % a_region['name'].replace(" ", "_").replace(".", ""))
    with open(outfile, 'w') as f:
        json.dump(data, f)
    return outfile


def index2csv(BCname, index, csvfile):
    df = index.to_dataframe()

    txt_header = """# Title : Profile directory file of the Boundary Currents Monitor
# Description : The directory file describes all individual profile files of the argo GDAC ftp site for one Boundary Current system ({})
# Project : ARGO, EARISE, BC-monitor
# Format version : 2.0
# Date of update : {}
# FTP root number 1 : ftp://ftp.ifremer.fr/ifremer/argo/dac
# FTP root number 2 : ftp://usgodae.org/pub/outgoing/argo/dac
# GDAC node : -
""".format(BCname, pd.to_datetime('now', utc=True).strftime('%Y%m%d%H%M%S'))
    with open(outfile, 'w') as f:
        f.write(txt_header)

    if len(df) > 0:
        with open(csvfile, 'a+') as f:
            df = df.drop(['profiler', 'institution_name'], axis=1)
            df = df.rename(columns={'profiler_code': 'profiler_type'})
            df = df[['file', 'date', 'latitude', 'longitude', 'ocean', 'profiler_type', 'institution', 'date_update']]
            df.to_csv(f, index=False, date_format='%Y%m%d%H%M%S')

    return csvfile


if __name__ == '__main__':

    # Get the list of regionmask.Regions:
    dict_regions, regions = get_region_list()

    # Load index for the North Atlantic:
    if os.uname()[0] == 'Darwin':
        cache_dir = os.path.join(*[os.path.split(os.path.realpath(__file__))[0], "cache"])
        argopy.set_options(cachedir=cache_dir)
    print(argopy.show_options())

    # Get metrics and index for each regions:
    dict_regions, regions = analyse_regions(dict_regions, regions, cache_dir)

    # Output directory:
    out_dir = os.path.join(*[os.path.split(os.path.realpath(__file__))[0], "..", "data"])

    # Save metrics in json files:
    for region in dict_regions.keys():
        save_this_region_endpoint(dict_regions[region], out_dir=out_dir)

    # Save index in csf files:
    for region in dict_regions.keys():
        a_region = dict_regions[region]
        outfile = os.path.join(out_dir, 'BC_%s_index.txt' % a_region['name'].replace(" ", "_").replace(".", ""))
        index2csv(a_region['name'], a_region['index'], outfile)

    #
    argopy.clear_cache()
