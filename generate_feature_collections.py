import json
import sqlite3

YEAR_FROM = 1863
YEAR_TO = 1912

conn = sqlite3.connect('mapping_the_homestead_act.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

def getFeatureCollection(type, year):
    sql = '''
    SELECT stats.year, stats.number, stats.acres, land_offices.land_office, states.state, states.coordinates
    FROM stats 
    INNER JOIN land_offices ON land_offices.id = stats.land_office_id
    INNER JOIN states ON states.id = land_offices.state_id
    WHERE stats.type = ?
    AND stats.year = ?
    '''

    states = {}
    for row in c.execute(sql, (type, year)):
        if row['state'] not in states:
            states[row['state']] = {'coordinates': json.loads(row['coordinates'])}
        if row['number'] not in states[row['state']]:
            states[row['state']]['total_number'] = 0
        if row['acres'] not in states[row['state']]:
            states[row['state']]['total_acres'] = 0
        if isinstance(row['number'], int):
            states[row['state']]['total_number'] = states[row['state']]['total_number'] + row['number']
        if isinstance(row['acres'], float):
            states[row['state']]['total_acres'] = states[row['state']]['total_acres'] + row['acres']

    features = []
    for state, data in states.items():
        features.append({
            'type': 'Feature',
            'id': state,
            'properties': {
                'state': state,
                'total_acres': data['total_acres'],
                'total_number': data['total_number'],
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

featureCollections = {}
for type in ['claim', 'patent', 'commutation']:
    if type not in featureCollections:
        featureCollections[type] = {}
    for year in range(YEAR_FROM, YEAR_TO):
        featureCollections[type][year] = getFeatureCollection(type, year)
with open('html/feature-collections.js', 'w') as outfile:
    outfile.write('var featureCollections = {}'.format(json.dumps(featureCollections)))
