# Mapping the Homestead Act

Building dynamic maps to combine the spatial land claims statistics related to
the Homestead Act with further quantitative data and qualitative narratives.

## Requirements

 - Python 3+ (with the `openpyxl` module installed)
 - SQLite 3+

## Migration

### Migrate from XLSX to SQLite

Currently the migration script assumes the existence of the "Land claims by
office 1863-96.xlsx" workbook. It also assumes that the list of land offices and
states in the "good keys" worksheet is comprehensive. There is also an
expectation that the structure of the workbook will not change beyond the
addition of as-of-yet untranscribed claims, patents, commutations, and their
acreages. Any further changes to the workbook may require changes to the
migration script.

Run the migration script, where `<my_workbook_file>` is the path to the XLSX
file:
```
$ python3 migrate.py <my_workbook_file>
```
This will create (or overwrite) a `mapping_the_homestead_act.db` database file. You can open
it using:
```
$ sqlite3 mapping_the_homestead_act.db
```

## Database

### Example usage

With the `mapping_the_homestead_act.db` database in place, we can start asking
questions about the data, reflecting them in SQL statements, generating
geographic data structures (e.g. GeoJSON), and applying them to an interactive
map. Some very simple examples:

Select all claims with an acreage greater than 500,000:
```sql
SELECT states.state, land_offices.land_office, stats.year, stats.number, stats.acres
FROM stats
INNER JOIN land_offices ON stats.land_office_id = land_offices.id
INNER JOIN states ON land_offices.state_id = states.id
WHERE stats.type = "claim"
AND acres > 500000
ORDER BY states.state, land_offices.land_office, stats.year;
```
Select the total number of patents for each land office:
```sql
SELECT states.state, land_offices.land_office, SUM(stats.number)
FROM stats
INNER JOIN land_offices ON stats.land_office_id = land_offices.id
INNER JOIN states ON land_offices.state_id = states.id
WHERE stats.type = "patent"
GROUP BY land_offices.id
ORDER BY states.state, land_offices.land_office, stats.year;
```

## Dynamic map

In order to create a dynamic map you'll need to generate a geoJSON feature
collection for every type for every year.

```
$ python3 generate_feature_collections.py
```

After this you can copy the `/html` directory to your web server and view a
simple dynamic map.
