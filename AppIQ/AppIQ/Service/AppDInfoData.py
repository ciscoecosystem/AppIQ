__author__ = 'nilayshah'
import requests
import json, time
from pprint import pprint
import AppD_Alchemy as AppD_Database
import threading
from flask import current_app

class AppD(object):
    def __init__(self, host, port, user, account, password):
        self.host = str(host)
        self.port = str(port)
        self.user = str(user) + "@" + str(account)
        self.password = password
        # self.protocol = "https://"  # Check for connection if not try http
        self.login_url = self.host + ':' + self.port + '/controller/auth?action=login'
        try:
            login_status = self.check_connection()
            current_app.logger.info('App Login Status:'+str(login_status))
            if str(login_status) != '200':# and str(login_status) != '201':
                current_app.logger.info('Initial connection to AppDynamics failed!')
                if 'https://' in self.host:
                    current_app.logger.info('Trying http instead...')
                    self.host = self.host.replace('https','http')
                elif 'http://' in self.host:
                    current_app.logger.info('Trying https instead...')
                    self.host = self.host.replace('http','https')
                self.login_url = self.host + ':' + self.port + '/controller/auth?action=login'
                self.check_connection()
            self.databaseObject = AppD_Database.Database()
            current_app.logger.info('AppD Database schema generated.')
            self.count = 0
        except:
            current_app.logger.info('AppD Connection Failure. Please check that the AppDynamics Controller is available with valid credentials')

    def check_connection(self):
        try:
            self.appd_session = requests.Session()
            self.appd_session.auth = (self.user, self.password)
            login = self.appd_session.get(self.login_url,timeout=10)
            if login.status_code == 200 or login.status_code == 201:
                current_app.logger.info('Connection to AppDynamics Successful!')
                self.token = login.cookies['X-CSRF-TOKEN']
                self.JSessionId = login.cookies['JSESSIONID']
                self.headers = {
                    'x-csrf-token': self.token,
                    'content-type': "application/json"
                }
                return login.status_code
            else:
                return login.status_code
        except Exception as e:
            current_app.logger.info('Connection to AppDynamics Failed!')
            return "404"

    def get_app_health(self, id):
        payload = {
            "requestFilter": [id],
            "resultColumns": ["APP_OVERALL_HEALTH"],
            "offset": 0,
            "limit": -1,
            "timeRangeStart": int(round(time.time() * 1000)) - 5 * 60 * 1000,
            "timeRangeEnd": int(round(time.time() * 1000))
        }
        try:
            apps_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/app/list/ids",
                                                 headers=self.headers, data=json.dumps(payload))
            if apps_health.status_code == 200:
                return apps_health.json()  # ['data'][0]['severitySummary']['performanceState']
            else:
                # Refresh
                self.check_connection()
                try:
                    apps_health = self.appd_session.post(
                        self.host + ":" + self.port + "/controller/restui/app/list/ids",
                        headers=self.headers, data=json.dumps(payload))
                    if apps_health.status_code == 200:
                        return apps_health.json()
                    else:
                        return ""
                except Exception as e:
                    current_app.logger.info('Error Fetching AppD apps health, ' + str(e))
                    return ""
        except Exception as e:
            current_app.logger.info('Error Fetching AppD apps health, ' + str(e))
            return ""

    def get_tier_health(self, id):
        payload = {
            "requestFilter": [id],
            "resultColumns": ["HEALTH"],
            "offset": 0,
            "limit": -1,
            "timeRangeStart": int(round(time.time() * 1000)) - 5 * 60 * 1000,
            "timeRangeEnd": int(round(time.time() * 1000))
        }
        try:
            tiers_health = self.appd_session.post(
                self.host + ":" + self.port + "/controller/restui/tiers/list/health/ids",
                headers=self.headers,
                data=json.dumps(payload))
            if tiers_health.status_code == 200:
                if 'data' in tiers_health.json():
                    if 'healthMetricStats' in tiers_health.json()['data'][0]:
                        if 'state' in tiers_health.json()['data'][0]['healthMetricStats']:
                            return tiers_health.json()['data'][0]['healthMetricStats']['state']
                        else:
                            return 'UNDEFINED'
                    else:
                        return 'UNDEFINED'
                else:
                    return 'UNDEFINED'
            else:
                # Refresh
                self.check_connection()
                try:
                    tiers_health = self.appd_session.post(
                        self.host + ":" + self.port + "/controller/restui/tiers/list/health/ids", headers=self.headers,
                        data=json.dumps(payload))
                    if tiers_health.status_code == 200:
                        if 'data' in tiers_health.json():
                            if 'healthMetricStats' in tiers_health.json()['data'][0]:
                                if 'state' in tiers_health.json()['data'][0]['healthMetricStats']:
                                    return tiers_health.json()['data'][0]['healthMetricStats']['state']
                                else:
                                    return 'UNDEFINED'
                            else:
                                return 'UNDEFINED'
                        else:
                            return 'UNDEFINED'
                    else:
                        return 'UNDEFINED'
                except Exception as e:
                    current_app.logger.info('Error Fetching AppD tiers health, ' + str(e))
                    return "UNDEFINED"
        except Exception as e:
            current_app.logger.info('Error Fetching AppD tiers health, ' + str(e))
            return "UNDEFINED"

    def get_node_health(self, id):
        payload = {
            "requestFilter": [id],
            "resultColumns": ["HEALTH"],
            "offset": 0,
            "limit": -1,
            "timeRangeStart": int(round(time.time() * 1000)) - 5 * 60 * 1000,
            "timeRangeEnd": int(round(time.time() * 1000))
        }
        try:
            nodes_health = self.appd_session.post(
                self.host + ":" + self.port + "/controller/restui/nodes/list/health/ids",
                headers=self.headers,
                data=json.dumps(payload))
            if nodes_health.status_code == 200:
                if 'data' in nodes_health.json():
                    if 'healthMetricStats' in nodes_health.json()['data'][0]:
                        if 'state' in nodes_health.json()['data'][0]['healthMetricStats']:
                            return nodes_health.json()['data'][0]['healthMetricStats']['state']
                        else:
                            return 'UNDEFINED'
                    else:
                        return 'UNDEFINED'
                else:
                    return 'UNDEFINED'
            else:
                # Refresh
                self.check_connection()
                try:
                    nodes_health = self.appd_session.post(
                        self.host + ":" + self.port + "/controller/restui/nodes/list/health/ids", headers=self.headers,
                        data=json.dumps(payload))
                    if nodes_health.status_code == 200:
                        if 'data' in nodes_health.json():
                            if 'healthMetricStats' in nodes_health.json()['data'][0]:
                                if 'state' in nodes_health.json()['data'][0]['healthMetricStats']:
                                    return nodes_health.json()['data'][0]['healthMetricStats']['state']
                                else:
                                    return 'UNDEFINED'
                            else:
                                return 'UNDEFINED'
                        else:
                            return 'UNDEFINED'
                    else:
                        return 'UNDEFINED'
                except Exception as e:
                    current_app.logger.info('Error Fetching AppD nodes health, ' + str(e))
                    return "UNDEFINED"
        except Exception as e:
            current_app.logger.info('Error Fetching AppD nodes health, ' + str(e))
            return "UNDEFINED"

    def get_service_endpoints(self, app_id, tier_id):
        url = self.host + ':' + self.port + '/controller/restui/serviceEndpoint/listViewData/' + str(
            app_id) + '/' + str(
            tier_id) + '?time-range=last_5_minnutes.BEFORE_NOW.-1.-1.5'
        try:
            service_endpoints = self.appd_session.get(url, headers=self.headers)
            # if session expired Exception occurs - refresh and try the method again
            if str(service_endpoints.status_code) != "200":
                self.check_connection()
                try:
                    service_endpoints = self.appd_session.get(url, headers=self.headers)
                except Exception as e:
                    current_app.logger.info('Service EP API cal failed,  ' + str(e))
                    return []
            if service_endpoints.status_code == 200:
                if not service_endpoints:
                    return []
                # current_app.logger.info('AppD Service Endpoints fetched for AppId' + str(app_id))
                if 'serviceEndpointListEntries' in service_endpoints.json():
                    service_endpoints = service_endpoints.json()['serviceEndpointListEntries']
                else:
                    service_endpoints = []
                service_endpoints_list = []
                if service_endpoints:
                    for sep in service_endpoints:
                        if 'performanceSummary' in sep:
                            if 'type' in sep:
                                if sep.get('performanceSummary') and str(sep.get('type')) == "SERVLET":
                                    sepId = sep.get('id')
                                    sepName = sep.get('name')
                                    if 'performanceStats' in sep.get('performanceSummary'):
                                        if 'errorPercentage' in sep.get('performanceSummary').get('performanceStats'):
                                            errorP = sep.get('performanceSummary').get('performanceStats').get(
                                                'errorPercentage')
                                        else:
                                            errorP = '0'
                                        if 'numberOfErrors' in sep.get('performanceSummary').get('performanceStats'):
                                            if 'value' in sep.get('performanceSummary').get('performanceStats'):
                                                errorCount = sep.get('performanceSummary').get('performanceStats').get(
                                                    'numberOfErrors').get('value')
                                            else:
                                                errorCount = '0'
                                        else:
                                            errorCount = '0'
                                        if 'errorsPerMinute' in sep.get('performanceSummary').get('performanceStats'):
                                            if 'value' in sep.get('performanceSummary').get('performanceStats').get(
                                                    'errorsPerMinute'):
                                                errorPMin = sep.get('performanceSummary').get('performanceStats').get(
                                                    'errorsPerMinute').get('value')
                                            else:
                                                errorCount = '0'
                                        else:
                                            errorCount = '0'
                                        if str(errorPMin) == "-1":
                                            errorPMin = '0'
                                        if str(errorCount) == "-1":
                                            errorCount = '0'
                                        sepType = sep.get('type')
                                        service_endpoints_list.append(
                                           {'sepId': sepId, 'sepName': str(sepName), 'Error Percentage': str(errorP),
                                             'Total Errors': str(errorCount),
                                             'Errors/Min': str(errorPMin),
                                             'Type': str(sepType)})
                    return service_endpoints_list
        except Exception as e:
            current_app.logger.info('Service EP API call failed,  ' + str(e))
            return []

    def get_app_info(self):
        try:
            applications = requests.get(self.host + ':' + self.port + '/controller/rest/applications' + '?output=JSON',
                                        auth=(self.user, self.password))
            # current_app.logger.info('app code -'+str(applications.status_code))
            if applications.status_code == 200:
                #                 current_app.logger.info('Fetched AppD applications.')
                return applications.json()
            else:
                # Refresh
                self.check_connection()
                try:
                    applications = requests.get(
                        self.host + ':' + self.port + '/controller/rest/applications' + '?output=JSON',
                        auth=(self.user, self.password))
                    if applications.status_code == 200:
                        #                         current_app.logger.info('Fetched AppD applications.')
                        return applications.json()
                    else:
                        return []
                except Exception as e:
                    current_app.logger.info('Apps API call failed,  ' + str(e))
                    return []
        except Exception as e:
            current_app.logger.info('Apps API call failed,  ' + str(e))
            return []

    def get_tier_info(self, app_id):
        try:
            tiers_response = requests.get(str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(
                app_id) + '/tiers?output=JSON',
                                          auth=(self.user, self.password))
            # current_app.logger.info('tier code -'+str(tiers_response.status_code))
            if tiers_response.status_code == 200:
                #                 current_app.logger.info('Fetched Tiers for AppID - ' + str(app_id))
                return tiers_response.json()
            else:
                # Refresh
                self.check_connection()
                try:
                    tiers_response = requests.get(
                        str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(
                            app_id) + '/tiers?output=JSON', auth=(self.user, self.password))
                    if tiers_response.status_code == 200:
                        #                         current_app.logger.info('Fetched Tiers for AppID - ' + str(app_id))
                        return tiers_response.json()
                    else:
                        return []
                except Exception as e:
                    current_app.logger.info('Tiers API call failed,  ' + str(e))
                    return []
        except Exception as e:
            current_app.logger.info('Tiers API call failed,  ' + str(e))
            return []

    def get_node_info(self, app_id, tier_id):
        try:
            nodes_response = requests.get(
                str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(app_id) + '/tiers/' + str(
                    tier_id) + '/nodes?output=JSON', auth=(self.user, self.password))
            # current_app.logger.info('node code -'+str(nodes_response.status_code))
            if nodes_response.status_code == 200:
                #current_app.logger.info('Fetched AppD Nodes for Tier -' + str(tier_id) + ', App - ' + str(app_id))
                if nodes_response.json():
                    return nodes_response.json()
                else:
                    return []
            else:
                # Refresh
                self.check_connection()
                try:
                    nodes_response = requests.get(
                        str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(
                            app_id) + '/tiers/' + str(tier_id) + '/nodes?output=JSON', auth=(self.user, self.password))
                    if nodes_response.status_code == 200:
                        # current_app.logger.info(
                        #    'Fetched AppD Nodes for Tier -' + str(tier_id) + ', App - ' + str(app_id))
                        if nodes_response.json():
                            return nodes_response.json()
                        else:
                            return []
                    else:
                        return []
                except Exception as e:
                    current_app.logger.info('Nodes API call failed,  ' + str(e))
                    return []
        except Exception as e:
            current_app.logger.info('Nodes API call failed,  ' + str(e))
            return []

    def getHealthViolations(self, app_id, tier_id=None, node_id=None):
        healthV_url = self.host + ':' + self.port + '/controller/restui/incidents/application/' + str(app_id)
        payload = {"healthRuleIdFilter": -1,
                   "rangeSpecifier": {"type": "BEFORE_NOW", "durationInMinutes": 5}, "pageSize": -1, "pageNumber": 0}
        final_violate_list = []
        violate_list = []
        try:
            health_violations = self.appd_session.post(healthV_url, headers={'x-csrf-token': self.token,
                                                                             'jsessionid': self.JSessionId,
                                                                             'content-type': 'application/json'},
                                                       data=json.dumps(payload))
            # current_app.logger.info('HEV code -'+str(health_violations.status_code))
            if tier_id and str(health_violations.status_code) != "200":
                self.check_connection()
                try:
                    health_violations = self.appd_session.post(healthV_url, headers={'x-csrf-token': self.token,
                                                                                     'jsessionid': self.JSessionId,
                                                                                     'content-type': 'application/json'},
                                                               data=json.dumps(payload))
                    # current_app.logger.info('HEV code -'+str(health_violations.status_code))
                except Exception as e:
                    current_app.logger.info('HEV API call failed,  ' + str(e))
                    return []
            if tier_id and health_violations.status_code == 200:
                health_violations = health_violations.json()
                if not health_violations:
                    return []
                if 'entityMap' in health_violations:
                    for key1, val1 in health_violations.get('entityMap').iteritems():
                        key = str(key1).split(',')
                        if key:
                            bt_tier_id = key[1].split(':')[1]
                            if 'componentId' in health_violations.get('entityMap').get(key1):
                                if health_violations.get('entityMap').get(key1).get('componentId') == tier_id:
                                    violate = {'id': bt_tier_id,
                                               'bt': str(health_violations.get('entityMap').get(key1).get('name'))}
                                    violate_list.append(violate)
                if 'incidents' in health_violations:
                    for key2 in health_violations.get('incidents'):
                        for key3 in violate_list:
                            if str(key2['status']) == "OPEN" and str(key2.get('affectedEntity').get('entityId')) in \
                                    key3[
                                        'id']:
                                violation_startTime = key2['startTime']

                                startTime = time.strftime('%Y-%m-%d %H:%M:%S',
                                                          time.localtime(int(str(violation_startTime)) / 1000))
                                description = key2['description']
                                severity = key2['severity']
                                final_violate_list.append({'Description': str(description), 'Severity': str(severity),
                                                           'Violation Id': int(key3['id']),
                                                           'Affected Object': key3['bt'],
                                                           'Start Time': str(startTime)})
            else:
                return []
            return final_violate_list
        except Exception as e:
            current_app.logger.info('HEV API call failed,  ' + str(e))
            return []

    def getAppDApps(self):
        apps = self.databaseObject.returnValues('Application')
        list_of_apps = []
        for each in apps:
            app_data = {'appProfileName': str(each.appName), 'isViewEnabled': each.isViewEnabled}
            list_of_apps.append(app_data)
        return {'app': list_of_apps}

    def get_node_details(self, appId, nodeId):
        try:
            node_details_response = requests.get(
                str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(appId) + '/nodes/' + str(
                    nodeId) + '?output=JSON', auth=(self.user, self.password))
            if node_details_response.status_code == 200:
                if node_details_response.json():
                    return node_details_response.json()
                else:
                    return []
            else:
                # Refresh
                self.check_connection()
                node_details_response = requests.get(
                    str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(appId) + '/nodes/' + str(
                        nodeId) + '?output=JSON', auth=(self.user, self.password))
                if node_details_response.status_code == 200:
                    if node_details_response.json():
                        return node_details_response.json()
                    else:
                        return []
                else:
                    return []
        except Exception as ex:
            current_app.logger.info('Failed to get Node Details for NodeID: ' + nodeId + ' in Application with AppID: ' + appId + '\nException: ' + str(ex))
            return []


    def main(self):
        while True:
            self.databaseObject = AppD_Database.Database()
            self.check_connection()
            current_app.logger.info('Starting Database Update!')
            try:
                apps = self.get_app_info()
                current_app.logger.info('Total apps found in the DB:' + str(len(apps)))
            except Exception as e:
                current_app.logger.info('Exception in fetching Apps, Error:' + str(e))
            appidList = []
            tieridList = []
            nodeidlist = []
            sepList = []
            violationList = []
            try:
                if apps:
                    for app in apps:
                        app_metrics = self.get_app_health(app.get('id'))
                        appidList.append(app.get('id'))
                        self.databaseObject.checkIfExistsandUpdate('Application',
                                                                   [app.get('id'), str(app.get('name')), app_metrics])
                    for app in apps:
                        tiers = self.get_tier_info(app.get('id'))
                        if tiers:
                            for tier in tiers:
                                tier_health = self.get_tier_health(tier.get('id'))
                                if tier_health != 'UNDEFINED':
                                    #continue
                                    tieridList.append(tier.get('id'))
                                    # tierId, tierName, appId, tierHealth
                                    self.databaseObject.checkIfExistsandUpdate('Tiers',
                                                                               [tier.get('id'), str(tier.get('name')),
                                                                                app.get('id'),
                                                                                str(tier_health)])

                                # current_app.logger.info('Updated Tiers: Total - ' + str(len(tiers)))
                            for tier in tiers:
                                tier_health = self.get_tier_health(tier.get('id'))
                                if tier_health != 'UNDEFINED':
                                    #current_app.logger.info('Tier health:' + str(tier_health))
                                    #continue
                                    # Service Endpoints
                                    #current_app.logger.info('Updating SEVs')
                                    service_endpoints = self.get_service_endpoints(app.get('id'), tier.get('id'))
                                    if service_endpoints:
                                        # sepId, sep, tierId
                                        try:
                                            for sep in service_endpoints:
                                                self.databaseObject.checkIfExistsandUpdate('ServiceEndpoints',
                                                                                           [sep.get('sepId'), sep,
                                                                                            tier.get('id'),
                                                                                            app.get('id')])
                                                sepList.append(sep['sepId'])
                                                # self.databaseObject.commitSession()
                                        except Exception as e:
                                            current_app.logger.info('Exception in SEV, Error:'+str(e))
                                    #current_app.logger.info('Updating HEVs')
                                    # HealthViolations
                                    tierViolations = self.getHealthViolations(str(app.get('id')), tier_id=tier.get('id'))
                                    if tierViolations:
                                        try:
                                            for violations in tierViolations:
                                                self.databaseObject.checkIfExistsandUpdate('HealthViolations',
                                                                                           [violations.get('Violation Id'),
                                                                                            violations.get('Start Time'),
                                                                                            violations.get('Affected Object'),
                                                                                            violations.get('Description'),
                                                                                            violations.get('Severity'),
                                                                                            tier.get('id'), app.get('id')])
                                                violationList.append(violations.get('Violation Id'))
                                        except Exception as e:
                                            current_app.logger.info('Exception in HEV, Error:'+str(e))
                                    #current_app.logger.info('Updated SEPs and HEVs')

                                    # Nodes
                                    if tier.get('numberOfNodes') > 0:
                                        nodes = self.get_node_info(app.get('id'), tier.get('id'))
                                        ipList = []
                                        #current_app.logger.info('Nodes for tier'+str(tier.get('id'))+', app:'+str(app.get('id')))
                                        #current_app.logger.info(nodes)
                                        if len(nodes) > 0:
                                            for node in nodes:
                                                node_health = self.get_node_health(node.get('id'))
                                                if node_health != 'UNDEFINED':
                                                    #current_app.logger.info('Node health:' + str(node_health))
                                                    #continue
                                                        
                                                    if 'ipAddresses' in node:

                                                        # If 'ipAddresses' key is None, we make another API Call to get the Node Details
                                                        if not node.get('ipAddresses'):
                                                            node_details = self.get_node_details(app.get('id'), node.get('id'))
                                                            if node_details:
                                                                node = node_details[0]

                                                                if not node.get('ipAddresses'):
                                                                    current_app.logger.info("No 'ipAddresses' found in Node Details Response. \nResponse : " + str(node_details))
                                                                    continue
                                                        
                                                        if 'ipAddresses' in node.get('ipAddresses') and node.get('ipAddresses').get('ipAddresses'):
                                                            for i in range(len(node.get('ipAddresses').get('ipAddresses'))):
                                                                if '%' in node.get('ipAddresses').get('ipAddresses')[i]:
                                                                    ipv6 = node.get('ipAddresses').get('ipAddresses')[i].split('%')[0]
                                                                    ipList.append(str(ipv6))
                                                                else:
                                                                    ipv4 = node.get('ipAddresses').get('ipAddresses')[i]
                                                                    ipList.append(str(ipv4))
                                                            self.databaseObject.checkIfExistsandUpdate('Nodes',
                                                                                                       [node.get('id'),
                                                                                                        str(node.get('name')),
                                                                                                        tier.get('id'),
                                                                                                        str(node_health),
                                                                                                        ipList, app.get('id')])
                                                            nodeidlist.append(node.get('id'))
                                                            ipList = []
                                                            current_app.logger.info(
                                                                'Record: App_id - ' + str(app.get('id')) + ', AppName - ' + str(
                                                                    app.get('name')) + ', Tier - ' + str(
                                                                    tier.get('id')) + ', Node - ' + str(node.get('id')))
                                                        
                                                    # if 'ipAddresses' in node and node.get('ipAddresses'):
                                                    #     if 'ipAddresses' in node.get('ipAddresses') and node.get('ipAddresses').get('ipAddresses'):
                                                    #         for i in range(len(node.get('ipAddresses').get('ipAddresses'))):
                                                    #             if '%' in node.get('ipAddresses').get('ipAddresses')[i]:
                                                    #                 ipv6 = node.get('ipAddresses').get('ipAddresses')[i].split('%')[0]
                                                    #                 ipList.append(str(ipv6))
                                                    #             else:
                                                    #                 ipv4 = node.get('ipAddresses').get('ipAddresses')[i]
                                                    #                 ipList.append(str(ipv4))
                                                    #         self.databaseObject.checkIfExistsandUpdate('Nodes',
                                                    #                                                    [node.get('id'),
                                                    #                                                     str(node.get('name')),
                                                    #                                                     tier.get('id'),
                                                    #                                                     str(node_health),
                                                    #                                                     ipList, app.get('id')])
                                                    #         nodeidlist.append(node.get('id'))
                                                    #         ipList = []
                                                    #         current_app.logger.info(
                                                    #             'Record: App_id - ' + str(app.get('id')) + ', AppName - ' + str(
                                                    #                 app.get('name')) + ', Tier - ' + str(
                                                    #                 tier.get('id')) + ', Node - ' + str(node.get('id')))
                                                    
                    self.databaseObject.checkAndDelete('Application', appidList)
                    self.databaseObject.checkAndDelete('Tiers', tieridList)
                    self.databaseObject.checkAndDelete('ServiceEndpoints', sepList)
                    self.databaseObject.checkAndDelete('HealthViolations', violationList)
                    self.databaseObject.checkAndDelete('Nodes', nodeidlist)
                    self.databaseObject.commitSession()
                    current_app.logger.info('Database Update Complete!')
                    time.sleep(30)  # threading.Timer(60, self.main).start()
            except Exception as e:
                current_app.logger.info('Exception in AppDInfoData Main, Error: ' + str(e))
                self.databaseObject.commitSession()
                time.sleep(60)
                self.main()
                # except:
                #     self.databaseObject.commitSession()
                # print "Database Failed to update!"

                # def startThread(self):
                #     try:
                #         self.main()
                # print "Starting Thread!"
                # threading.Timer(10, self.main).start()
                # except:
                #     self.databaseObject.commitSession()

                # def dbtest(self):
                #     nodes = self.databaseObject.returnValues('Nodes')
                #     for each in nodes:
                #         print str(each.nodeId) + "  /  " + (each.nodeName)
                #         print (each.nodeHealth) + "  /  " + str(each.tierId) + "  /  " + str(each.appId)
                #         print each.ipAddress
                #     apps = self.databaseObject.returnValues('Application')
                #     tiers = self.databaseObject.returnValues('Tiers')
                #     nodes = self.databaseObject.returnValues('Nodes')
                #     seps = self.databaseObject.returnValues('ServiceEndpoints')
                #     hevs = self.databaseObject.returnValues('HealthViolations')
                #     #self.databaseObject.commitSession()
                # for each in apps:
                #     print str(each.appId) + "  /  " + (each.appName)
                #     pprint(each.appMetrics)
                # print each.isViewEnabled
                # for each in tiers:
                #     print str(each.tierId) + "  /  " + (each.tierName)
                #     print (each.tierHealth) + "  /  " + str(each.appId)
                # for each in nodes:
                #     print str(each.nodeId) + "  /  " + (each.nodeName)
                #     print (each.nodeHealth) + "  /  " + str(each.tierId) + "  /  " + str(each.appId)
                #     print each.ipAddress
                # for each in seps:
                #     print str(each.sepId) + "  /  " + str(each.tierId) + "  /  " + str(each.appId)
                #     print each.sep
                # for each in hevs:
                #     print (each.violationId)
                #     print str(each.description)
                #     print each.tierId
                #     print each.appId
                # self.databaseObject.checkAndDelete('Nodes', [])
                # self.databaseObject.commitSession()

                ##################### To test it on local machine #####################
                # databaseObject = AppD_Database.Database()
                # databaseObject.createTables() #Create Database tables
                # appd_object = AppD('192.168.132.125', "8090", 'user1', 'customer1', 'Cisco!123') # DMZ AppD Controller
                # appd_object.main() # Use it to Fetch AppD data and store it in Database
                # appd_object.dbtest() # Use it to test the database stored objects (AppD data)
                #
                # appd_object = AppD('10.23.239.14',"8090", 'user1', 'customer1', 'welcome') # Cisco network B13 AppD Controller
                # pprint(appd_object.getHealthViolations(5)7,8,10,11,12,13,14,18)
                # pprint(appd_object.get_app_health(5))
                # print appd_object.getAppDApps()
                # print appd_object.check_connection()
