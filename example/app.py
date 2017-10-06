from flask import Flask, request, jsonify, json
from werkzeug.exceptions import default_exceptions
from flask_jerify import Jerify, jerror_handler


app = Flask(__name__)

# Use custom json error handler
for code in default_exceptions:
    app.errorhandler(code)(jerror_handler)

jerify = Jerify(app)


@app.route('/test', methods=['POST'])
@jerify.request('test')
def test():
    return jerify.response({'target': 'world'}, 'test'), 200


app.run(debug=True)
