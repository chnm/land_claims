# Mapping the Homestead Act

## Requirements

 - Python 3+ (with `openpyxl` and `sqlite3` modules installed)
 - SQLite 3+

## Migrating from XLSX to SQLite

Currently the `land_claims.py` migration script assumes the existence of a "land
claims by office" workbook (XLSX) alongside it. It also assumes that the list of
land offices and states on the "good keys" worksheet is comprehensive. There is
also an expectation that the structure of the workbook will not change beyond the
addition of as-of-yet untranscribed claims, patents, commutations, and their acreages.
Any further changes to the workbook may require changes to `land_claims.py`.

Run the migration script, where `<my_workbook>` is the XLSX file:
```
$ python3 land_claims.py <my_workbook>
```
This will create (or overwrite) a `land_claims.db` database file. You can open it
using:
```
$ sqlite3 land_claims.db
```

## Example usage

Select all claims with an acreage greater than 500,000:
```sql
SELECT states.state, land_offices.land_office, claims.year, claims.claims, claims.acres
FROM claims
INNER JOIN land_offices ON claims.land_office_id = land_offices.id
INNER JOIN states ON land_offices.state_id = states.id
WHERE acres > 500000
ORDER BY states.state, land_offices.land_office, claims.year;
```
Select the total number of claims for each land office:
```sql
SELECT states.state, land_offices.land_office, SUM(claims.claims)
FROM claims
INNER JOIN land_offices ON claims.land_office_id = land_offices.id
INNER JOIN states ON land_offices.state_id = states.id
GROUP BY land_offices.id
ORDER BY states.state, land_offices.land_office, claims.year;
```

## Schema

```sql
CREATE TABLE states (
    id INTEGER PRIMARY KEY,
    state TEXT NOT NULL UNIQUE
);
CREATE TABLE land_offices (
    id INTEGER PRIMARY KEY,
    state_id INTEGER,
    land_office TEXT NOT NULL UNIQUE,
    FOREIGN KEY (state_id) REFERENCES state (id) ON DELETE CASCADE
);
CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    land_office_id INTEGER,
    year INTEGER NOT NULL,
    claims INTEGER NULL,
    acres REAL NULL,
    FOREIGN KEY (land_office_id) REFERENCES land_offices (id) ON DELETE CASCADE
);
CREATE TABLE patents (
    id INTEGER PRIMARY KEY,
    land_office_id INTEGER,
    year INTEGER NOT NULL,
    patents INTEGER NULL,
    acres REAL NULL,
    FOREIGN KEY (land_office_id) REFERENCES land_offices (id) ON DELETE CASCADE
);
CREATE TABLE commutations (
    id INTEGER PRIMARY KEY,
    land_office_id INTEGER,
    year INTEGER NOT NULL,
    commutations INTEGER NULL,
    acres REAL NULL,
    FOREIGN KEY (land_office_id) REFERENCES land_offices (id) ON DELETE CASCADE
);
```

