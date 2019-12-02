import json
import sqlite3

YEAR_FROM = 1863
YEAR_TO = 1912

conn = sqlite3.connect('mapping_the_homestead_act.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

def getFeatureCollectionStates(type, date_start):
    sql = '''
    SELECT stats.date_start, stats.number, stats.acres, land_offices.land_office, states.state, states.coordinates
    FROM stats 
    INNER JOIN land_offices ON land_offices.id = stats.land_office_id
    INNER JOIN states ON states.id = land_offices.state_id
    WHERE stats.type = ?
    AND stats.date_start = ?
    '''

    states = {}
    for row in c.execute(sql, (type, date_start)):
        if row['state'] not in states:
            states[row['state']] = {
                'coordinates': json.loads(row['coordinates']),
                'land_offices': {}
            }
        if row['land_office'] not in states[row['state']]['land_offices']:
            states[row['state']]['land_offices'][row['land_office']] = {
                'total_number': 0,
                'total_acres': 0,
            }
        if 'total_number' not in states[row['state']]:
            states[row['state']]['total_number'] = 0
        if 'total_acres' not in states[row['state']]:
            states[row['state']]['total_acres'] = 0
        if isinstance(row['number'], int):
            states[row['state']]['total_number'] += row['number']
            states[row['state']]['land_offices'][row['land_office']]['total_number'] += row['number']
        if isinstance(row['acres'], (int, float)):
            states[row['state']]['total_acres'] += row['acres']
            states[row['state']]['land_offices'][row['land_office']]['total_acres'] += row['acres']

    features = []
    for state, data in states.items():
        features.append({
            'type': 'Feature',
            'id': state,
            'properties': {
                'state': state,
                'total_acres': data['total_acres'],
                'total_number': data['total_number'],
                'land_offices': data['land_offices']
            },
            'geometry': {
                'type': 'Polygon' if (1 == len(data['coordinates'])) else 'MultiPolygon',
                'coordinates': data['coordinates']
            }
        });

    featureCollection = {
        'type': 'FeatureCollection',
        'features': features
    }
    return featureCollection

def getFeatureCollectionLandOffices(type, date_start):
    sql = '''
    SELECT stats.date_start, stats.number, stats.acres, land_offices.land_office, land_offices.coordinates
    FROM stats
    INNER JOIN land_offices ON land_offices.id = stats.land_office_id
    WHERE stats.type = ?
    AND stats.date_start = ?
    '''

    features = []
    for row in c.execute(sql, (type, date_start)):
        features.append({
            'type': 'Feature',
            'id': row['land_office'],
            'properties': {
                'land_office': row['land_office'],
                'number': row['number'],
                'acres': row['acres'],
            },
            'geometry': {
                'type': 'Point',
                'coordinates': json.loads(row['coordinates'])
            }
        });

    featureCollection = {
        'type': 'FeatureCollection',
        'features': features
    }
    return featureCollection

featureCollectionsStates = {}
featureCollectionsLandOffices = {}
for type in [
    'claim', 'patent', 'commutation_sec2301', 'commutation_june151880',
    'claim_indianland', 'patent_indianland', 'commutation_indianland'
]:
    if type not in featureCollectionsStates:
        featureCollectionsStates[type] = {}
    if type not in featureCollectionsLandOffices:
        featureCollectionsLandOffices[type] = {}
    for year in range(YEAR_FROM, YEAR_TO + 1):
        date_start = '1863-01-01' if (1863 == year) else '{}-07-01'.format(year - 1)
        featureCollectionsStates[type][date_start] = getFeatureCollectionStates(type, date_start)
        featureCollectionsLandOffices[type][date_start] = getFeatureCollectionLandOffices(type, date_start)
with open('html/feature-collections-states.js', 'w') as outfile:
    outfile.write('var featureCollectionsStates = {}'.format(json.dumps(featureCollectionsStates)))
with open('html/feature-collections-land-offices.js', 'w') as outfile:
    outfile.write('var featureCollectionsLandOffices = {}'.format(json.dumps(featureCollectionsLandOffices)))
