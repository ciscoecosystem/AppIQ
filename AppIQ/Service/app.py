__author__ = 'nilayshah'

from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
from schema import schema
import AppD_Alchemy as Database
import AppDInfoData as AppDConnect
import os
import requests
#import urllib3
#urllib3.disable_warnings()

app = Flask(__name__)
CORS(app, resources={r"/graphql.json": {"origins": "*"}}) # CORS used for what?
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

app.add_url_rule('/graphql.json', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

database_object = Database.Database()
database_object.createTables()
#appd_object = AppDConnect.AppD('192.168.132.125', 'user1', 'customer1', 'Cisco!123')
# appd_object = AppDConnect.AppD('10.23.239.14', 'user1', 'customer1', 'welcome')
# appd_object.main()

path = "/home/app/data/credentials.json"
file_exists = os.path.isfile(path)
if file_exists:
    os.remove(path)


@app.teardown_appcontext
def shutdown_session(exception=None):
    # db_session.remove()
    pass


if __name__ == '__main__':
    #app.run()
    #init_db()
    database_object = Database.Database()
    database_object.createTables()
    #appd_object = AppDConnect.AppD('192.168.132.125', 'user1', 'customer1', 'Cisco!123')
    # appd_object = AppDConnect.AppD('10.23.239.14', 'user1', 'customer1', 'welcome')
    # appd_object.main()
    path = "/home/app/data/credentials.json"
    file_exists = os.path.isfile(path)
    if file_exists:
        os.remove(path)
    app.run(host='0.0.0.0', port=80, threaded=True)
    # app.run(host='127.0.0.1', port= 8000)
    #app.run(host='0.0.0.0', ssl_context='adhoc', port = 443, debug=True)
