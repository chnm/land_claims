import csv
import json
from datetime import datetime
from pprint import pprint

# This script is intended to be run only once because it draws from an idiosyncratic
# dataset. It generates a GeoJSON file containing polygons of tribal ceded land
# organized by year.

# USDA's "Tribal Ceded Lands" dataset:
#   - Shapefile: https://data.fs.usda.gov/geodata/edw/edw_resources/shp/S_USA.TRIBALCEDEDLANDS.zip
#   - MapServer: https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TribalCessionLands_01/MapServer

# GeoJSON extracted from "Tribal Ceded Lands" shapefile.
file_geojson = '/home/jimsafley/Desktop/Mapping Homestead Act/mygeodata/S_USA.TRIBALCEDEDLANDS.geojson'

# CSV extracted from "Tribal Ceded Lands" shapefile attribute table. It contains
# a custom column "end date n" derived from the column "Royce Schedule Date 1".
file_csv = '/home/jimsafley/Desktop/Mapping Homestead Act/land cession dates.csv'

YEAR_FROM = 1863
YEAR_TO = 1912

land_cession_coordinates = {}
with open(file_geojson) as f:
    tribal_ceded_lands = json.load(f)
    for tribal_ceded_land in tribal_ceded_lands['features']:
        cessnum = tribal_ceded_land['properties']['CESSNUM']
        cesscoordinates = tribal_ceded_land['geometry']['coordinates']
        land_cession_coordinates[cessnum] = cesscoordinates

land_cession_data = {}
with open(file_csv, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            cessnum = row['TribalCe_1']
            end_date = datetime.strptime(row['end date n'], '%Y-%m-%d')
        except ValueError:
            continue
        land_cession_data[cessnum] = {
            'end_date': end_date,
            'cession_tribes': row['TribalCe12'],
            'present_tribes': row['TribalCe13']
        }

feature_collections = {}
for year in range(YEAR_FROM, YEAR_TO + 1):
    year = int(year)
    date_start = '1863-01-01' if (1863 == year) else '{}-07-01'.format(year - 1)
    date_end = '{}-06-30'.format(year)
    date_start_datetime = datetime.strptime(date_start, '%Y-%m-%d')
    date_end_datetime = datetime.strptime(date_end, '%Y-%m-%d')
    features = []
    for cessnum, data in land_cession_data.items():
        # Include this cession only if its end date happens after the current start date.
        if data['end_date'] > date_start_datetime:
            features.append({
                'type': 'Feature',
                'properties': {
                    'cession_tribes': data['cession_tribes'],
                    'present_tribes': data['present_tribes']
                },
                'geometry': {
                    'type': 'Polygon' if (1 == len(land_cession_coordinates[cessnum])) else 'MultiPolygon',
                    'coordinates': land_cession_coordinates[cessnum]
                },
            })
    feature_collections[date_start] = {
        'type': 'FeatureCollection',
        'features': features
    }

with open('html/feature-collections-tribal-ceded-lands.js', 'w') as outfile:
    outfile.write('var featureCollectionsTribalCededLands = {}'.format(json.dumps(feature_collections)))

