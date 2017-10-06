# Flask-Jerify

"JSON Verify". Easy validation against JSON schemas for Flask APIs.

Leverages `jsonschema`.

## Installation

```
pip install flask-jerify
```

## Usage

### Loading JSON Schemas

`flask-jerify` will by default look for a `./schemas` directory in the running
directory and read all `.schema.json`  files:

```
.
├── app.py
└── schemas
    └── test-schame.schema.json
```

The sample `test.schema.json` demands a compulsory `target` parameter and 
doesn't accept any additional parameters:

```
{
    "title": "test schema",
    "type": "object",
    "properties": {
        "target": {
            "type": "string"
        }
    },
    "required": [
      "target"
    ],
    "additionalProperties": false
}
```

The schema can then be accessed with the file prefix, ie: `test-schame` within 
Jerify.

### Validate Requests and JSON Error Responses

The following snippet sets up an `app` with `jerify`'s custom error handler, 
instantiates `Jerify`, and sets up a route that accepts JSON conforming to the 
defined `test-schema.schema.json` JSON schema.

```
from flask_jerify import Jerify, jerror_handler
from werkzeug.exceptions import default_exceptions

app = Flask(__name__)

for code in default_exceptions:
    app.errorhandler(code)(jerror_handler)

jerify = Jerify(app)

@app.route('/test', methods=['POST'])
@jerify.request('test-schema')
def test():
    return '{"validated": "true"}', 200
```

#### Invalid JSON

```
$ curl -d '{"target":' -H "Content-Type: application/json" -X POST http://localhost:5000/test
{
  "errors": [
    {
      "code": 400, 
      "detail": "Invalid JSON", 
      "status": "Bad Request"
    }
  ]
}
```

#### Invalid Requests

```
$ curl -d '{"hello":"world"}' -H "Content-Type: application/json" -X POST http://localhost:5000/test
{
  "errors": [
    {
      "code": 400, 
      "detail": "'target' is a required property", 
      "status": "Bad Request"
    }
  ]
}

```

```
$ curl -d '{"target": "test", "hello":"world"}' -H "Content-Type: application/json" -X POST http://localhost:5000/test
{
  "errors": [
    {
      "code": 400, 
      "detail": "Additional properties are not allowed ('hello' was unexpected)", 
      "status": "Bad Request"
    }
  ]
}
```

### Validate Responses

```
@app.route('/test', methods=['POST'])
def test():
    return jerify.validate({'hello': 'world'}, 'test-schema'), 200
```

```
$ curl -d '{"target": "test"}' -H "Content-Type: application/json" -X POST http://localhost:5000/test
{
  "errors": [
    {
      "code": 500, 
      "detail": "The server encountered an internal error and was unable to complete your request.  Either the server is overloaded or there is an error in the application.", 
      "status": "Internal Server Error"
    }
  ]
}
```

```
[2017-08-26 02:36:05 +0000] [11857] [INFO] [flask_jerify.flask_jerify] JSON failed validation against schema'test': {'target': 'test', 'hello': 'world'}
```


## Configuration

### Schemas Directory

```
JERIFY_SCHEMAS=./schemas
```

### Jerify Log Level

```
JERIFY_LOG=WARNING
```