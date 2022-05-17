import regionmask
import pandas as pd

import os
import json
import argopy
from argopy import IndexFetcher as ArgoIndexFetcher


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


def analyse_regions(dict_regions, regions):
    for r in regions:
        index_box = dict_regions[r.abbrev]['box']
        dict_regions[r.abbrev]['long_name'] = r.name
        dict_regions[r.abbrev]['name'] = r.abbrev
        dict_regions[r.abbrev]['fetcher'] = None
        dict_regions[r.abbrev]['index'] = []
        dict_regions[r.abbrev]['N_PROF'] = 0
        dict_regions[r.abbrev]['N_WMO'] = 0
        try:
            argo = ArgoIndexFetcher(src='gdac', cache=True).region(index_box).load()
            dict_regions[r.abbrev]['fetcher'] = argo
            dict_regions[r.abbrev]['index'] = argo.index
            dict_regions[r.abbrev]['N_PROF'] = len(argo.index)
            dict_regions[r.abbrev]['N_WMO'] = len(argo.index.groupby('wmo').count())
        except argopy.errors.DataNotFound:
            pass
        print("%30s: %i profiles in the last 10 days" % (r.name, len(argo.index)))
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
    outfile = os.path.join(out_dir, 'BCstatus_%s.json' % a_region['name'].replace(" ", "_").replace(".", ""))
    with open(outfile, 'w') as f:
        json.dump(data, f)
    return outfile


def index2csv(index, csvfile):
    institution_dict = argopy.utilities.load_dict('institutions')
    df = index.copy()

    txt_header = """# Title : Profile directory file of the Argo Global Data Assembly Center
    # Description : The directory file describes all individual profile files of the argo GDAC ftp site.
    # Project : ARGO
    # Format version : 2.0
    # Date of update : {}
    # FTP root number 1 : ftp://ftp.ifremer.fr/ifremer/argo/dac
    # FTP root number 2 : ftp://usgodae.org/pub/outgoing/argo/dac
    # GDAC node : -
    """.format(pd.to_datetime('now', utc=True).strftime('%Y%m%d%H%M%S'))
    with open(outfile, 'w') as f:
        f.write(txt_header)

    if len(df) > 0:
        with open(csvfile, 'a+') as f:
            df = df.drop(['profiler', 'institution_code'], axis=1)
            df = df.rename(columns={'institution_code': 'institution'})
            df['institution'] = df['institution'].apply(
                lambda x: list(institution_dict.keys())[list(institution_dict.values()).index(x)])
            df = df.rename(columns={'profiler_code': 'profiler_type'})
            df = df[['file', 'date', 'latitude', 'longitude', 'ocean', 'profiler_type', 'institution', 'date_update']]
            df.to_csv(f, index=False, date_format='%Y%m%d%H%M%S')

    return csvfile

if __name__ == '__main__':
    # Get the list of regionmask.Regions:
    dict_regions, regions = get_region_list()
    # Load index for the North Atlantic:
    ArgoIndexFetcher(src='gdac', cache=True).region([-80, 0., 15, 65])
    # Get metrics and index for each regions:
    dict_regions, regions = analyse_regions(dict_regions, regions)
    # Save metrics in json files:
    for region in dict_regions.keys():
        save_this_region_endpoint(dict_regions[region], out_dir='data')
    # Save index in csf files:
    for region in dict_regions.keys():
        a_region = dict_regions[region]
        outfile = os.path.join('data', 'BCindex_%s.txt' % a_region['name'].replace(" ", "_").replace(".", ""))
        index2csv(a_region['index'], outfile)
