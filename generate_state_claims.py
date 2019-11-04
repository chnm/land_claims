import json
import sqlite3

conn = sqlite3.connect('mapping_the_homestead_act.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

def getFeatureCollection(year):
    sql = '''
    SELECT claims.year, claims.claims, claims.acres, land_offices.land_office, states.state, states.coordinates
    FROM claims 
    INNER JOIN land_offices ON land_offices.id = claims.land_office_id
    INNER JOIN states ON states.id = land_offices.state_id
    WHERE claims.year = ?
    '''

    states = {}
    for row in c.execute(sql, (year,)):
        if row['claims'] is not None and not isinstance(row['acres'], str):
            if row['state'] not in states:
                states[row['state']] = {'coordinates': json.loads(row['coordinates'])}
            if row['claims'] not in states[row['state']]:
                states[row['state']]['total_claims'] = 0
            if row['acres'] not in states[row['state']]:
                states[row['state']]['total_acres'] = 0
            states[row['state']]['total_claims'] = states[row['state']]['total_claims'] + row['claims']
            states[row['state']]['total_acres'] = states[row['state']]['total_acres'] + row['acres']

    features = []
    for state, data in states.items():
        features.append({
            'type': 'Feature',
            'id': state,
            'properties': {
                'state': state,
                'total_acres': data['total_acres'],
                'total_claims': data['total_claims'],
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
for year in range(1863, 1897):
    featureCollections[year] = getFeatureCollection(year)
with open('html/claims.js', 'w') as outfile:
    outfile.write('var featureCollections = {}'.format(json.dumps(featureCollections)))
