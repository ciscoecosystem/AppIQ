from datetime import timedelta  
from flask import Flask, make_response, request, current_app  
from functools import update_wrapper

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):  
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/')
@crossdomain(origin='*')
def landing():
    fd = open("MappingJSON.json")
    data = fd.read()
    return data

@app.route('/test')
@crossdomain(origin='*')
def testing():
    arg = request.args.get("testparam")
    return "Adad"

@app.route('/displayAppDApps')
@crossdomain(origin='*')
def getAppNames():
    fd = open("json.json")
    data = fd.read()
    return data

@app.route('/mapping.json')
@crossdomain(origin='*')
def getMappings():
    fd = open("MappingJSON.json")
    data = fd.read()
    return data

@app.route('/saveMapping.json', methods=['POST'])
@crossdomain(origin='*')
def saveMappings():
    data = request.data
    print data
    return data

if __name__ == '__main__':  
    app.run(host='127.0.0.1', port=5000)