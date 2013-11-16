import flask
from flask import request
import json
import dataset
import os
import json

app = flask.Flask(__name__)
db_url = os.getenv('DATABASE_URL')
db = dataset.connect(db_url)

class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def encode(self, obj):
        if hasattr(obj, 'to_dict'):
            obj = obj.to_dict()
        return super(JSONEncoder, self).encode(obj)

    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        raise TypeError("%r is not JSON serializable" % obj)


def jsonify(obj, status=200, headers=None):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    jsondata = json.dumps(obj, cls=JSONEncoder)
    if 'callback' in request.args:
        jsondata = '%s(%s)' % (request.args.get('callback'), jsondata)
    return Response(jsondata, headers=headers,
                    status=status, mimetype='application/json')

@app.route("/")
def query():
  # parse args  
  query = request.args.get('q', None)

  # return json 
  return jsonify([row for row in db.query(query)])
  
if __name__ == "__main__":
  app.debug = True
  app.run(host='0.0.0.0', port=5000)
