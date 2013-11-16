import csv
import pandas as pd
import dataset
import os

event_types = {
  0 : None,
  1 : "Threat",
  2 : "Action",
  3 : "Country",
  4 : "Person/Group",
  5 : "Issue",
  6 : "Human Rights Protest Actions"
}

classification_types = {
  1 : "Death",
  2 : "Incarceration with Impending Death",
  3 : "Violence",
  4 : "Incarceration",
  5 : "Ill-treatment",
  6 : "Forced Movement",
  7 : "Threat of Death",
  8 : "Threat of Violence ",
  9 : "Threat of Incarceration",
  10 : "Risk",
  11 : "legal issues",
  12 : "Health Concern" ,
  13 : "Abduction",
  14 : "Corporate Abuse",
  15 : "Discrimination",
  16 : "Torture",
  17 : "Threat of Torture"
}

# read in main csv
main_fieldnames = (
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
  "iso3"
)

main_file = open( '../cleaned_data/lotus_database_w_iso3.csv', 'r' )
reader = csv.DictReader(main_file, fieldnames = main_fieldnames)
main_data = []
for i, r in enumerate(reader):
  if i > 0:
    main_data.append(r)

clean_data = []
for row in main_data:
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

cat_fieldnames = (
  "category",
  "category_count",
  "event_type",
  "classification"
)

cat_file = open( '../raw_data/raw_categories.csv', 'rU' )
reader = csv.DictReader(cat_file, fieldnames = cat_fieldnames)
cat_lookup = {}
for i, r in enumerate(reader):
  if i>0:
    cat_lookup[r['category']] = r


def assign_categories(raw_category_row):
  
  # parse out categories
  raw_category_list = [
    c.strip() 
    for c in raw_category_row.split("|") 
    if c is not None and c !=''
  ]
  
  if len(raw_category_list) > 0:
    cat_dict = {}
    for c in raw_category_list:
     
      if cat_lookup.has_key(c):
        
        event_type = int(cat_lookup[c]['event_type'])
        class_type = int(cat_lookup[c]['classification'])
        
        if event_type != 0:
          event_key = "event_%d" % event_type
          if cat_dict.has_key(event_key):
            cat_dict[event_key] += 1
          else:
            cat_dict[event_key] = 1
        if class_type != 0:
          class_key = "class_%d" % class_type
          if cat_dict.has_key(class_key):
            cat_dict[class_key] += 1
          else:
            cat_dict[class_key] = 1

    return cat_dict
  else:
    return {}

def update_database(data):

  # assign the categories
  cat_rows = [assign_categories(d['category']) for d in data ]

  # identify set of unique keys
  key_set = set([k for row in cat_rows for k in row.keys()])
  
  # fill in rows with zeros
  full_cat_rows = []
  for row in cat_rows:
    for k in key_set:
      if not row.has_key(k):
        row[k] = 0
      full_cat_rows.append(row)

  # join with original data:
  joined_data = []
  for i, d in enumerate(data):
    joined_data.append(dict(d.items() + full_cat_rows[i].items()))

  return joined_data

if __name__ == '__main__':
  
  # update data
  print "updating data with categories..."
  updated_data = update_database(clean_data)

  # insert to postgres
  print "inserting data into postgres"
  db = dataset.connect(os.getenv('DATABASE_URL'))
  table = db['amnesty']
  table.delete()
  table.insert_many(updated_data)

  # write csv
  print "writing data to csv"
  df = pd.DataFrame(updated_data)
  df.to_csv('../cleaned_data/lotus_database_w_iso3_and_cats.csv')






