__author__ = 'nilayshah'

from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, time, logging, os, pprint
import threading
import flask
from flask_cors import CORS, cross_origin
import ACI_Info as aci_info
# import
import AppDInfoData as AppDConnect
import AppD_Alchemy as Database
import generate_d3 as d3
import RecommendedDNObjects as Recommend
# import ACI_Local as aci_local
import ACI_Info as ACI_AppD

from flask import render_template

# import ACI_AppD_App as ACI_AppD
app = Flask(__name__, template_folder="../UIAssets", static_folder="../UIAssets")
# app = Flask(__name__)
app.debug = True
# aci_appd_object = ACI_AppD.ACI_AppD()
appd_object = AppDConnect.AppD('192.168.132.125', 'user1', 'customer1', 'Cisco!123')
database_object = Database.Database()
d3Object = d3.generateD3Dict()


# @app.route('/check.json', methods=['GET', 'POST'])
# def checkFile():
#     app.logger.info('Checking if File Exists')
#     path = '/home/app/credentials/credentials.json'
#     file_exists = os.path.isfile(path)
#     # print file_exists
#     if file_exists == False:
#         return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}
#         # return 'False'
#     else:
#         return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
#         # return 'True'

#
# @app.route('/login.json', methods=['GET', 'POST'])
# def login():
#     app.logger.info('Entered Login')
#     if request.method == 'POST':
#         # if 1 == 1:
#         appd_creds = request.json
#         appd_ip = appd_creds["appd_ip"]
#         appd_user = appd_creds["appd_user"]
#         appd_account = appd_creds["appd_account"]
#         appd_pw = appd_creds["appd_pw"]
#         credentials = {'appd_ip': appd_ip, 'appd_user': appd_user, 'appd_account': appd_account, 'appd_pw': appd_pw}
#         with open('/home/app/credentials/credentials.json', 'w+') as creds:
#             creds.seek(0)
#             creds.truncate()
#             json.dump(credentials, creds)
#             creds.close()
#             app.logger.info('-- Values received:')
#             app.logger.info('appd_url: {}'.format(appd_ip))
#             app.logger.info('appd_user: {}'.format(appd_user))
#             app.logger.info('appd_user: {}'.format(appd_account))
#             app.logger.info('appd_pw: {}'.format(appd_pw))
#             app.logger.info('Login Complete')
#             appd_store_data = run_aciappd()
#             app.logger.info('AppD Data Stored')
#             app.logger.info(appd_store_data)
#     return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
#     # run_aciappd()
#     # return "LoggedIn"  # render_template('app.html')
#

# Correlates ACI and AppD Data
#
# @app.route('/run.json', methods=['GET', 'POST'])
# def getACIAppDdata():
#     app.logger.info('Running getACIAppData...')
#     tenantName = request.args.get('tn')
#     # appd_store_data = run_aciappd()
#
#     # tenantName = 'AppD'  # Hard coded - Need to fetch from UI
#     data = None
#     merged_data = aci_appd_object.mergeData(tenantName)
#     app.logger.info('Merged data...')
#     app.logger.info(merged_data)
#     d3_data = d3Object.generateD3Dict(merged_data)  # generate_d3_compatible_dict(merged_data)
#     app.logger.info('d3_data')
#     app.logger.info(d3_data)
#     return json.dumps(d3_data)
    # merged_data = "Fetch merged data"
    # response = flask.jsonify(json.dumps(d3_data))
    # print json.dumps(d3_data)
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # return json.dumps(merged_data)
    # return response


# Call every 30 seconds to store data in database
# @app.route('/run_aciappd.json')
# def run_aciappd():
#     app.logger.info('FORM DATA SENDING...')
#     # with open('/home/app/credentials/credentials.json', 'r+') as creds:
#     #     appd_creds = json.load(creds)
#     #     creds.close()
#     # appd_creds = {'appd_ip':'10.23.239.14','appd_user':'user1','appd_account':'customer1','appd_pw':'welcome'}
#     appd_creds = {'appd_ip': '192.168.132.125', 'appd_user': 'user1', 'appd_account': 'customer1',
#                   'appd_pw': 'Cisco!123'}
#     # Start Thread-1 Here
#     app.logger.info("Starting Thread 1")
#     store_thread = threading.Thread(target=storeAppDData, args=(
#         appd_creds['appd_ip'], appd_creds['appd_user'], appd_creds['appd_account'], appd_creds['appd_pw']))
#     store_thread.start()
#     time.sleep(5)
#
#     return "Initialized db.... "
#

# @app.route('/storeAppD')
# def storeAppDData(appd_ip, appd_user, appd_account, appd_pw):
#     while True:
#         print "Connnecting to AppD to store data"
#         aci_appd_object.getAppDynamics(appd_ip, appd_user, appd_account, appd_pw)
#         aci_appd_object.addAppDdata()
#         print "Thread 1 start"
#         time.sleep(20)  # Runs every 20 seconds
#     return json.dumps("Table Created:")


@app.route('/displayAppDApps')
def displayAppDApps():  # change format:> {'app': [{'appProfileName': 'NPMApplication', 'isViewEnabled': False},{'appProfileName': 'NPMApplication', 'isViewEnabled': False}]}
    app_list = appd_object.getAppDApps()
    return jsonify(app_list)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('/index.html', name=name)

# @app.route('/showACItemp')
# def ACItemp():
#     eps = database_object.returnValues('ACItemp')
#     zero_list = []
#     one_list = []
#     for ep in eps:
#         if ep.selector == 0:
#             zero_list.append({"ipaddress": str(ep.IP)})
#         else:
#             one_list.append({"ipaddress": str(ep.IP)})
#     mappings = {"source_cluster": {"data": zero_list}, "destination_cluster": {"data": one_list}}
#     return mappings
#
#
# @app.route('/addToACIperm')
# def addToACIperm(ipdnlist):  # change ACI temp, selector = 1, dnlist = [dn1, dn2, dn3]
#     for dn in ipdnlist:
#         database_object.storechangesinACItemp(dn)


# print(displayAppDApps())

# pprint.pprint(ACItemp())
# addToACIperm(['uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ord/cep-00:50:56:9D:FE:EB',
#               'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-MiscAppVMs/cep-00:50:56:9D:57:89',
#               'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Inv/cep-00:50:56:9D:16:17',
#               'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ecomm/cep-00:50:56:9D:8D:DB'])


# pprint.pprint(ACItemp())
# for each in database_object.returnValues('ACItemp'):
#     print(str(each.selector))


########################################################################################################################
#     New implementations

@app.route('/apps.json')  # This shall be called from /check.json, for Cisco Live this is the first/start Route
def apps():
    # tenantName = request.args.get('tn') # Gets tenant from UI (current tab URL)
    appsList = database_object.getappList()
    return json.dumps(appsList)



@app.route('/mapping.json',methods=['GET', 'POST'])
def mapping():
    appId = request.args.get('appId')
    mapping_dict = {"source_cluster": [], "target_cluster": []}
    tenant = request.args.get('tn')
    # tenant = 'AppDynamics'
    already_mapped_data = database_object.returnMapping(appId)
    if already_mapped_data != None:
        mapping_dict['target_cluster'] = already_mapped_data
    rec_object = Recommend.Recommend()
    mapped_objects = rec_object.correlate_ACI_AppD(tenant, appId)
    # print "mapped_objects"
    # print mapped_objects
    ips_mapped = []
    if already_mapped_data != None:
        for each in already_mapped_data:
            ips_mapped.append(each['ipaddress'])
    for new in mapped_objects:  # CONFIRM with Shivang, if src cluster needs to have data about dst also or not
        # if new['ipaddress'] not in ips_mapped:
        mapping_dict['source_cluster'].append(new)
    return json.dumps(mapping_dict)  # {"source_cluster": mapped_objects, "target_cluster": {{dn:IP},{dn:IP}}}


@app.route('/saveMapping.json',methods=['GET', 'POST'])
def saveMapping(appId, mappedData): # Shivang to implement request.data
    # mappedData = request.data
    # appId = 5
    # IP, IP2, dn, dn2 = ""
    # mappedData = {{'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti1', '20.20.20.11'},
    #               {'20.20.20.12': 'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti2'}}
    if not mappedData:
        print "DeleteEntry"
        database_object.deleteEntry('Mapping', appId)
        enableView(appId, False)
        return "Deleted Mappings"
    else:
        print "Save Mapping"
        database_object.deleteEntry('Mapping', appId)
        database_object.checkIfExistsandUpdate('Mapping', [appId, mappedData])
        view_enabled = enableView(appId, True)
        return "Saved Mappings"


# This will be called from the UI - after the Mappings are completed
@app.route('/enableView.json')
def enableView(appid, bool):
    return database_object.enableViewUpdate(appid, bool)


@app.route('/tree.json')
def tree():
    appId = request.args.get('appId')
    tenantName = request.args.get('tn')  # Gets tenant from UI (current tab URL)
    # tenantName = 'AppDynamics'
    # aci_data = aci_appd_object.mergeData(tenantName)
    # get app info for appId == 5
    merged_data = merge_aci_appd(tenantName, appId)
    return json.dumps(merged_data)


    # TBD - generating d3list
    # return json.dumps(d3Object.generate_d3_compatible_dict(merged_data))


def merge_aci_appd(tenant, appId):
    # To change to ACI LOCAL
    # aci_local_object = aci_local.ACI_Local(tenant)
    # aci_login = aci_local_object.login()
    # aci_data = aci_local_object.main()

    aci_object = aci_info.ACI("192.168.130.10", "admin", "Cisco!123")
    aci_data = aci_object.main(tenant)
    # pprint.pprint(aci_data)
    mappings = database_object.returnMapping(appId)
    # print type(mappings)

    # appd_data = getappD(appId,'10.10.10.15')
    merge_list = []
    for aci in aci_data:
        if mappings:
            for each in mappings:
                # print each
                if aci['IP'] == each['ipaddress'] and each['domainName'] == str(aci['dn']):
                    appd_data = getappD(appId, aci['IP'])
                    for each in appd_data:
                        each.update(aci)
                        merge_list.append(each)
    return merge_list


def getappD(appId, ep):
    app = database_object.returnApplication('appId', appId)
    tiers = database_object.returnTiers('appId', appId)
    # nodes =

    hevs = database_object.returnHealthViolations('appId', appId)  # TBD
    aci_ips_list = []
    appd_list = []
    appd_each_dict = {}
    for application in app:
        hev = database_object.returnHealthViolations('appId', application.appId)
        for tier in tiers:
            seps = database_object.returnServiceEndpoints('tierId', tier.tierId)
            sepList = []
            for sep in seps:
                if isinstance(sep.sep, dict):
                    sepList.append(sep.sep)
            hevList = []
            hevs = database_object.returnHealthViolations('tierId', tier.tierId)
            for hev in hevs:
                if isinstance(int(hev.violationId) >= 0):
                    hevList.append({"Violation id": str(hev.violationId), "Start Time": str(hev.startTime),
                                    'Business Transaction': str(hev.businessTransaction),
                                    'Description': str(hev.description), 'Severity': str(hev.severity)})
            nodes = database_object.returnNodes('tierId', tier.tierId)
            for node in nodes:
                if ep in node.ipAddress:
                    appd_list.append({'appId': application.appId, 'appName': str(application.appName), 'appHealth': str(
                        application.appMetrics['data'][0]['severitySummary']['performanceState']),
                                      'tierId': tier.tierId, 'tierName': str(tier.tierName),
                                      'tierHealth': str(tier.tierHealth),
                                      'nodeId': node.nodeId, 'nodeName': str(node.nodeName),
                                      'nodeHealth': str(node.nodeHealth), 'ipAddressList': node.ipAddress,
                                      'serviceEndpoints': sepList, 'hev': hevList})
    return appd_list


# ######################################################################################################################
# Test codes for URLs
# merge_aci_appd('AppDynamics')
# -1. Create the database
# database_object.createTables()
# 0. Fill in the database
# appd_object = AppDConnect.AppD('192.168.132.125', 'user1', 'customer1', 'Cisco!123')
# appd_object.main('Start')
# 1. List apps:
# pprint.pprint(apps())
# time.sleep(3)
# 2. Select app = appId (5,8)
# appId = 5

# 3. Get current mappings
# pprint.pprint(mapping(appId))
# time.sleep(3)
# 4. Select mapped objects and save
# mapped_data = []
# mapped_data = [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ord',
#                      'ipaddress': '10.10.10.18'},{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ord',
#                      'ipaddress': '10.10.10.19'}]
# mapped_data = [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti1',
#                 'ipaddress': '20.20.20.11'},
#                {'domainName': 'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti2', 'ipaddress': '20.20.20.12'}]
# pprint.pprint(saveMapping(appId, mapped_data))
# time.sleep(3)
# 5. show if app is enabled:
# pprint.pprint(apps())
# time.sleep(3)
# 6. Show current mappings
# pprint.pprint(mapping(appId))
# time.sleep(3)

# 7. Show merged data
# pprint.pprint(tree(appId))
# time.sleep(3)
# 8. Show d3 compatible data



# ######################################################################################################################
#
# Steps to take: This guide i to provide a step by step instructions for the code flow:
#     0. Initialize all vars and create database tables and autopopulate any variables
#     1. App login: use /login route
#         a. If not loggged in already> Load login page
#         b. Once submitted, start the thread and load database tables
#         c. populate it with AppD data
#         d. Run it every 30 seconds and insert new data or update existing data
#
#     2. (First view of the app) List of AppD applications. Use /apps route
#         a. List will show total number of apps and app health, app Name, app Id for each app
#         b. There will be two buttons for each app: i. Mapping ii. View
#         c. The Mapping will always be clickable, the View will be clickable once mapping is complete by the user
#         d. Once mapping is complete app table will be populated with 'isViewEnabled' = True (defaults to False)
#         e. To change from False to True use /enableView route - this will be called from mapping view upon save
#
#     3. (Second view of the app) This will be the mapping view for the clicked app
#         a. The route to populate the details for the clicked app will be /mapping route
#         b. The mapping table will show the IPs and their corresponding dns for a given tenant for the given app
#             a. The IPs will be taken by correlating IPs in the App and IPs in the given tenant
#         c. There is one table with three columns:
#             i. IP address
#             ii. dn object - One IP address can have two or more dn object
#                 1. For this case, show two dns for the same IP address (row)
#                 2. Show the recommended one - if the IP exists for the same app profile and same epg,
#                     it is the recommended one else if the same app profile, else same tenant
#                 3. Based of the 1st, 2nd or the 3rd case - put out the recommendation - 1, then 2, then 3
#             iii. Radio button for each of the dn
#         d. Once the radio buttons are selected and the save button is clicked, run a route /saveMapping
#         e. This mapping will be saved in a table with appId for the given app and primary key as the dn
#         f. The save will change isViewEnabled value in the app table and redirect the page to the First View '/apps'
#
#     4. The Tree(View) button will be enabled for the apps that have mapping complete and show the tree structure and
#         upon clicking the button, the UI will redirect to app view tree structure diagram (html)
#         a. The tree will consists of the app node, tier node, and Node node as already has been developed
#         b. The backend will give the data as previously done
#         c. The route /tree will be run for the data fetch
#         d. This will be run in the background every some seconds until user goes back to the app view
#
#     5. The user comes back again to the app, the /check route checks if the app is configured or not,
#         and redirects it to /login route or the /apps route depending on the return value
#
#
# *if there are two same IPs for handle them in mapping view
#
# NOTE: The following is the user interaction and its process from UI to backend and then backend to UI
# User Interaction with the App |  AppRoute to the backend |  Data UI passes to backend |  Data Backend gives to the front end
# 1. Click on the App             |  /apps.json              |  tenantName                |  [{'appName': u'EComm-NPM-Demo', 'isViewEnabled': True, 'appHealth': 'WARNING', 'appId': 5}, {'appName': u'NPMApplication', 'isViewEnabled': True, 'appHealth': 'NORMAL', 'appId': 8}]
# 2. Click on Mapping button      | /mapping.json            |  appId, tenantName         |  # mappings = [{'IP': IP1, 'dns': [{'dn': dn1_1, 'isRecommended': True}, {{'dn': dn1_2, 'isRecommended': False}}]},
# 3. User Adds & exits the mapping view |  /saveMapping.json |  appId, mappedData = [{'IP': IP, 'dn': dn}, {'IP': IP2, 'dn': dn2}] |  None
# 4. User Clicks on Tree view for an app | /tree.json        |  tenant, appId             | d3 compatible dict
#
# #######################################################################################################################

# pprint.pprint(apps())
#
# pprint.pprint(mapping(appId))
# pprint.pprint(mapping(appId))

# pprint.pprint(mapping(5))
# appd_object.main('Start')
# mapped_data = []

# mapped_data = [{'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti1': '20.20.20.11'},{'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti2':'20.20.20.12'}]
# mapped_data = [{'domains': [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP2-Jeti/epg-AppD-Jeti1',
#                                   'recommended': True},],
#                      'ipaddress': '20.20.20.11'}]
# mapped_data = [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ord',
#                      'ipaddress': '10.10.10.18'}]
# pprint.pprint(saveMapping(5, mapped_data))
# print(database_object.returnMapping(5))
# print "==="
# pprint.pprint(mapping(appId))
# pprint.pprint(enableView())
# pprint.pprint(tree(appId))
app.route('/')
def hello():
    print "hello"
    return "HelloWorld"

if __name__ == '__main__':
    # Setup logging
    fStr = '%(asctime)s %(levelname)5s %(message)s'
    # logging.basicConfig(filename='/home/app/log/app.log', format=fStr, level=logging.DEBUG)

    # Run app flask server
    # app.run(host='0.0.0.0', ssl_context='adhoc', port = 443, debug=True)
    # app.run(host='0.0.0.0', port=80, threaded=True)
    # app.run(host='127.0.0.1', port=5000, threaded=True)
    database_object.createTables()
    appd_object = AppDConnect.AppD('192.168.132.125', 'user1', 'customer1', 'Cisco!123')
    appd_object.main('Start')
    appId = 5
    mapped_data = [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ord',
                     'ipaddress': '10.10.10.18'},{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ord',
                     'ipaddress': '10.10.10.19'}]
    pprint.pprint(saveMapping(appId, mapped_data))

    app.run()
