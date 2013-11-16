import flask
from flask import request
import json
import dataset
import os

app = flask.Flask(__name__)
db_url = os.getenv('DATABASE_URL')
db = dataset.connect(db_url)

@app.route("/")
def query():
  # parse args  
  query = request.args.get('q', None)

  # return json 
  return json.dumps([row for row in db.query(query)])
  
if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0', port=5000)
