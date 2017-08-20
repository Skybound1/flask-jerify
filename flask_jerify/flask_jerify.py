import os
import json
import logging
import jsonschema
from functools import wraps
from flask import current_app, jsonify, request
from werkzeug.exceptions import BadRequest


try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


_DEFAULT_LOG_LEVEL = 'WARNING'
_DEFAULT_SCHEMA_DIR = './schemas'
_LOG_FORMAT = ('[%(asctime)s] [%(process)d] [%(levelname)s] [%(name)s] '
               '%(message)s')


class UnknownSchemaError(Exception):
    pass


class ValidationError(Exception):
    pass


class Jerify(object):

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

        self.logger = self._get_logger()
        # self.logger = self.app.logger
        self.schemas = self._get_schemas()

    def init_app(self, app):
        app.config.setdefault('JERIFY_SCHEMAS', _DEFAULT_SCHEMA_DIR)
        app.config.setdefault('JERIFY_LOG', _DEFAULT_LOG_LEVEL)

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

    def teardown(self, e):
        ctx = stack.top

    def _get_logger(self):
        logger = logging.getLogger(__name__)

        with self.app.app_context():
            loglevel = current_app.config['JERIFY_LOG']
            logger.setLevel(logging.getLevelName(loglevel))

        console = logging.StreamHandler()
        formatter = logging.Formatter(_LOG_FORMAT, '%Y-%m-%d %H:%M:%S +0000')
        console.setFormatter(formatter)
        logger.addHandler(console)

        return logger

    def _get_schemas(self):
        schemas = {}

        with self.app.app_context():
            schemas_dir = current_app.config['JERIFY_SCHEMAS']

        if not os.path.isdir(schemas_dir):
            return schemas

        for root, dirs, files in os.walk(schemas_dir):
            for file in files:
                if not file.endswith('.schema.json'):
                    continue

                with open(os.path.join(root, file), 'r') as file_handler:
                    try:
                        schema = json.load(file_handler)
                        jsonschema.Draft4Validator.check_schema(schema)
                        schema_name = file.replace('.schema.json', '')
                        schemas[schema_name] = schema
                    except json.decoder.JSONDecodeError as e:
                        self.logger.warning('Decoding failed: {}'.format(file))
                        self.logger.debug(e.msg)
                    except jsonschema.ValidationError as e:
                        self.logger.warning('Invalid schema: {}'.format(file))
                        self.logger.debug(e.msg)
                        continue
                    except Exception as e:
                        self.logger.warning('Failed to load: {}'.format(file))
                        self.logger.debug(e.msg)

        return schemas

    def check(self, schema=None):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    request.get_json()
                except Exception as e:
                    log = 'Received invalid JSON: {}'.format(request.data)
                    self.logger.info(log)
                    raise BadRequest('Invalid JSON')

                if schema and schema in self.schemas:
                    try:
                        jsonschema.validate(request.get_json(),
                                            self.schemas[schema])
                    except jsonschema.ValidationError as e:
                        log = ('JSON failed validation against schema\'{}\': '
                               '{}'.format(schema, request.get_json()))
                        self.logger.info(log)
                        raise BadRequest(e.message)
                elif schema:
                    log = 'Unknown schema: {}'.format(schema)
                    self.logger.error(log)
                    raise UnknownSchemaError(log)

                return f(*args, **kwargs)
            return wrapper
        return decorator

    def validate(self, doc, schema):
        if schema in self.schemas:
            try:
                jsonschema.validate(doc, self.schemas[schema])
            except jsonschema.ValidationError as e:
                log = ('JSON failed validation against schema\'{}\': '
                       '{}'.format(schema, request.get_json()))
                self.logger.info(log)
                raise ValidationError(e)
        else:
            log = 'Unknown schema: {}'.format(schema)
            self.logger.error(log)
            raise UnknownSchemaError(log)


class Jerror(Exception):
    def __init__(self, code, status, message):
        super(Jerror, self).__init__()
        self.code = code
        self.description = description


def jerror_handler(e):
    """http://jsonapi.org/format/#errors
    """
    response = {
        "errors": [
            {"status": e.name, "code": e.code, "detail": e.description}
        ]
    }
    return jsonify(response), e.code
