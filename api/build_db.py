import dataset
import os
import csv

db_url = os.getenv('DATABASE_URL')
db = dataset.connect(db_url)

# read in csv
fieldnames = (
  "",
  "document",
  "id",
  "subject",
  "year",
  "year_case_count",
  "category",
  "country",
  "gender",
  "appeal_date",
  "issue_date",
  "action",
  "all_dates",
  "body",
  "iso3_country",
  "iso3_subject",
  "iso3_category"
)

f = open( '../cleaned_data/lotus_database_w_iso3.csv', 'r' )
reader = csv.DictReader(f, fieldnames = fieldnames)
raw_data = []
for i, r in enumerate(reader):
  if i > 0:
    raw_data.append(r)

clean_data = []
for row in raw_data:
  new_row = {}
  for k in row.keys():
    if k!="":
      v = row[k]
      if v == 'NA':
        v = None
      if k == "id":
        new_row['data_id'] = v
      if k == "action":
        new_row['action'] = str(v)
      if k == "year":
        if v is None:
          new_row['year'] = None
        else:
          new_row['year'] = int(v.strip())
      else:
        new_row[k] = v

      new_row.pop("id", None)

  clean_data.append(new_row)

print "inserting data into postgres"
db['amnesty'].delete()
db['amnesty'].insert_many(clean_data)