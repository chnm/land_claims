# Mapping the Homestead Act

Building dynamic maps to combine the spatial land claims statistics related to
the Homestead Act with further quantitative data and qualitative narratives.

## Requirements

 - Python 3+ (with the `openpyxl` module installed)
 - SQLite 3+

## Migration

### Migrate from XLSX to SQLite

Currently the migration script assumes the existence of a "Land claims by
office" XLSX workbook. It also assumes that the list of land offices and states
in the "good keys" worksheet is comprehensive. There is also an expectation that
the structure of the workbook will not change beyond the addition of as-of-yet
untranscribed claims, patents, commutations, and their acreages. Any further
changes to the workbook may require changes to the migration script.

Run the migration script, where `<my_workbook_file>` is the path to the XLSX
file:
```
$ python3 migrate.py <my_workbook_file>
```
This will create (or overwrite) a `mapping_the_homestead_act.db` database file.
You can open it using:
```
$ sqlite3 mapping_the_homestead_act.db
```

With the database in place, we can start asking questions about the data,
reflecting them in SQL statements, generating geographic data structures (e.g.
GeoJSON), and applying them to an interactive map.

## Dynamic map

In order to create a dynamic map you'll need to generate a geoJSON feature
collection for every type for every year.

```
$ python3 generate_feature_collections.py
```

After this you can copy the `/html` directory to your web server and view a
simple dynamic map. To get the most out of the map, you'll need to edit
`index.html` and provide the following:

- Your [Mapbox](https://www.mapbox.com/) API access token (for the tile layer)
- The URL to the [Religious Ecologies Data API](https://github.com/religious-ecologies/relecapi) (for historical states boundaries)
