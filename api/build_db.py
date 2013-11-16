import pandas as pd 
import dataset
import math

db_url = os.getenv('DATABASE_URL')
db = dataset.connect(db_url)

df = pd.read_csv('../cleaned_data/lotus_database.csv')

data = []
for i in df.index:
  row = {}
  for k in df.keys():
    v = df[k][i]
    if pd.isnull(v):
      v = None
    if k == "id":
      row['data_id'] = v
    if k == "action":
      row['action'] = str(v)
    if k == "year":
      if v is None:
        row['year'] = None
      else:
        row['year'] = int(math.floor(float(v)))
    else:
      row[k] = v
    row.pop("id", None)

  data.append(row)

print "inserting data into postgres"
db['amnesty'].delete()
db['amnesty'].insert_many(data)