__author__ = 'nilayshah'

import requests
import json, time, os
from pprint import pprint
import AppD_Alchemy as AppD_Database
import ACI_Local as aci_local
import datetime
import threading
from flask import current_app
from custom_logger import CustomLogger

logger = CustomLogger.get_logger("/home/app/log/app.log")

class AppD(object):
    def __init__(self, host, port, user, account, password):
        self.host = str(host)
        self.port = str(port)
        self.user = str(user) + "@" + str(account)
        self.password = password

        self.appd_session = requests.Session()
        # self.protocol = "https://"  # Check for connection if not try http
        self.login_url = self.host + ':' + self.port + '/controller/auth?action=login'
        try:
            login_status = self.check_connection()
            logger.info('App Login Status:'+str(login_status))
            if str(login_status) != '200':# and str(login_status) != '201':
                logger.warning('Initial connection to AppDynamics failed!')
                if 'https://' in self.host:
                    logger.info('Trying http instead...')
                    self.host = self.host.replace('https','http')
                elif 'http://' in self.host:
                    logger.info('Trying https instead...')
                    self.host = self.host.replace('http','https')
                self.login_url = self.host + ':' + self.port + '/controller/auth?action=login'
                self.check_connection()
            self.databaseObject = AppD_Database.Database()
            logger.info('AppD Database schema generated.')
        except:
            logger.exception('AppD Connection Failure. Please check that the AppDynamics Controller is available with valid credentials')


    def check_connection(self):
        start_time = datetime.datetime.now()
        logger.info('In check_connection')
        try:
            self.appd_session.auth = (self.user, self.password)
            login = self.appd_session.get(self.login_url,timeout=10)
            logger.info('login in check connection: ' + str(login))
            if login.status_code == 200 or login.status_code == 201:
                logger.info('Connection to AppDynamics Successful!')
                logger.info('login.cookies: ' + str(login.cookies))
                self.token = login.cookies['X-CSRF-TOKEN']
                # The response of get returns the JSESSSIONID only first time.
                if login.cookies.get('JSESSIONID'):
                    self.JSessionId = login.cookies['JSESSIONID']
                self.headers = {
                   'x-csrf-token': self.token,
                   'content-type': "application/json"
                }
                return login.status_code
            else:
                return login.status_code
        except Exception as e:
            logger.exception('Connection to AppDynamics Failed! Error:' + str(e))
            return "404"
        finally:
            # self.appd_session.close()
            end_time =  datetime.datetime.now()
            logger.info("Time for check_connection: " + str(end_time - start_time))
            

    def get_app_health(self, id):
        start_time = datetime.datetime.now()
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
            if apps_health.status_code == 404:
                apps_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/v1/app/list/ids",
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
                    if apps_health.status_code == 404:
                        apps_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/v1/app/list/ids",
                                                 headers=self.headers, data=json.dumps(payload))
                    if apps_health.status_code == 200:
                        return apps_health.json()
                    else:
                        return ""
                except Exception as e:
                    logger.exception('Error Fetching AppD apps health, ' + str(e))
                    return ""
        except Exception as e:
            logger.exception('Error Fetching AppD apps health, ' + str(e))
            return ""
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_app_health: " + str(end_time - start_time))


    def get_tier_health(self, id):
        start_time = datetime.datetime.now()
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
            if tiers_health.status_code == 404:
                tiers_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/v1/tiers/list/health/ids",
                                                 headers=self.headers, data=json.dumps(payload))
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
                    if tiers_health.status_code == 404:
                        tiers_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/v1/tiers/list/health/ids",
                                                 headers=self.headers, data=json.dumps(payload))
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
                    logger.exception('Error Fetching AppD tiers health, ' + str(e))
                    return "UNDEFINED"
        except Exception as e:
            logger.exception('Error Fetching AppD tiers health, ' + str(e))
            return "UNDEFINED"
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_tier_health: " + str(end_time - start_time))


    def get_node_health(self, id):
        start_time = datetime.datetime.now()
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
            if nodes_health.status_code == 404:
                nodes_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/v1/nodes/list/health/ids",
                                                 headers=self.headers, data=json.dumps(payload))
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
                    if nodes_health.status_code == 404:
                        nodes_health = self.appd_session.post(self.host + ":" + self.port + "/controller/restui/v1/nodes/list/health/ids",
                                                 headers=self.headers, data=json.dumps(payload))
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
                    logger.exception('Error Fetching AppD nodes health, ' + str(e))
                    return "UNDEFINED"
        except Exception as e:
            logger.exception('Error Fetching AppD nodes health, ' + str(e))
            return "UNDEFINED"
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_node_health: " + str(end_time - start_time))


    def get_service_endpoints(self, app_id, tier_id):
        start_time = datetime.datetime.now()
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
                    logger.exception('Service EP API cal failed,  ' + str(e))
                    return []
            if service_endpoints.status_code == 200:
                if not service_endpoints:
                    return []
                # logger.info('AppD Service Endpoints fetched for AppId' + str(app_id))
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
            logger.exception('Service EP API call failed,  ' + str(e))
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_service_endpoints: " + str(end_time - start_time))


    def get_node_mac(self, node_id):
        mac = []

        try:
            # if node_id == 416:
            #     mac.append('00:50:56:89:AA:BA')
            #     return mac
            # elif node_id == 420:
            #     mac.append('00:50:56:89:AA:BA')
            #     return mac

            node_mac_details_response = self.appd_session.get(
                str(self.host)+':'+ self.port + '/controller/sim/v2/user/machines?'+'nodeIds=' + str(
                    node_id) + '&output=JSON', auth=(self.user, self.password))
            if node_mac_details_response.status_code == 200:
                logger.info('Fetched mac for Nodes ' + str(node_id))
                if node_mac_details_response.json() != []:
                    for all_data in node_mac_details_response.json():
                            interfaces = all_data['networkInterfaces']
                            for interface in interfaces:
                                mac.append(str(interface['macAddress']))
            else:
                # Refresh
                self.check_connection()
                mac = self.get_node_mac(node_id)
            return mac
        except Exception as e:
            logger.exception("error : "+str(e))


    def get_app_info(self):
        start_time = datetime.datetime.now()
        try:
            # self.appd_session
            applications = self.appd_session.get(self.host + ':' + self.port + '/controller/rest/applications' + '?output=JSON',
                                        auth=(self.user, self.password))
            # logger.info('app code -'+str(applications.status_code))
            if applications.status_code == 200:
                # logger.info('Fetched AppD applications.')
                return applications.json()
            else:
                # Refresh
                self.check_connection()
                try:
                    # self.appd_session
                    applications = self.appd_session.get(
                        self.host + ':' + self.port + '/controller/rest/applications' + '?output=JSON',
                        auth=(self.user, self.password))
                    if applications.status_code == 200:
                        # logger.info('Fetched AppD applications.')
                        return applications.json()
                    else:
                        return []
                except Exception as e:
                    logger.exception('Apps API call failed,  ' + str(e))
                    return []
        except Exception as e:
            logger.exception('Apps API call failed,  ' + str(e))
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_app_info: " + str(end_time - start_time))

    def get_tier_info(self, app_id):
        start_time = datetime.datetime.now()
        try:
            # self.appd_session
            tiers_response = self.appd_session.get(str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(
                app_id) + '/tiers?output=JSON',
                                          auth=(self.user, self.password))
            # logger.info('tier code -'+str(tiers_response.status_code))
            if tiers_response.status_code == 200:
                # logger.info('Fetched Tiers for AppID - ' + str(app_id))
                return tiers_response.json()
            else:
                # Refresh
                self.check_connection()
                try:
                    # self.appd_session
                    tiers_response = self.appd_session.get(
                        str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(
                            app_id) + '/tiers?output=JSON', auth=(self.user, self.password))
                    if tiers_response.status_code == 200:
                        # logger.info('Fetched Tiers for AppID - ' + str(app_id))
                        return tiers_response.json()
                    else:
                        return []
                except Exception as e:
                    logger.exception('Tiers API call failed,  ' + str(e))
                    return []
        except Exception as e:
            logger.exception('Tiers API call failed,  ' + str(e))
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_tier_info: " + str(end_time - start_time))


    def get_node_info(self, app_id, tier_id):
        start_time = datetime.datetime.now()
        try:
            # self.appd_session
            nodes_response = self.appd_session.get(
                str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(app_id) + '/tiers/' + str(
                    tier_id) + '/nodes?output=JSON', auth=(self.user, self.password))
            # logger.info('node code -'+str(nodes_response.status_code))
            if nodes_response.status_code == 200:
                #logger.info('Fetched AppD Nodes for Tier -' + str(tier_id) + ', App - ' + str(app_id))
                if nodes_response.json():
                    return nodes_response.json()
                else:
                    return []
            else:
                # Refresh
                self.check_connection()
                try:
                    # self.appd_session
                    nodes_response = self.appd_session.get(
                        str(self.host) + ':' + self.port + '/controller/rest/applications/' + str(
                            app_id) + '/tiers/' + str(tier_id) + '/nodes?output=JSON', auth=(self.user, self.password))
                    if nodes_response.status_code == 200:
                        # logger.info(
                        #    'Fetched AppD Nodes for Tier -' + str(tier_id) + ', App - ' + str(app_id))
                        if nodes_response.json():
                            return nodes_response.json()
                        else:
                            return []
                    else:
                        return []
                except Exception as e:
                    logger.exception('Nodes API call failed,  ' + str(e))
                    return []
        except Exception as e:
            logger.exception('Nodes API call failed,  ' + str(e))
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_node_info: " + str(end_time - start_time))

    def getHealthViolations(self, app_id, tier_id=None, node_id=None):
        start_time = datetime.datetime.now()
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
            # logger.info('HEV code -'+str(health_violations.status_code))
            if tier_id and str(health_violations.status_code) != "200":
                self.check_connection()
                try:
                    health_violations = self.appd_session.post(healthV_url, headers={'x-csrf-token': self.token,
                                                                                     'jsessionid': self.JSessionId,
                                                                                     'content-type': 'application/json'},
                                                               data=json.dumps(payload))
                    # logger.info('HEV code -'+str(health_violations.status_code))
                except Exception as e:
                    logger.exception('HEV API call failed,  ' + str(e))
                    return []
            if tier_id and health_violations.status_code == 200:
                health_violations = health_violations.json()
                if not health_violations:
                    return []
                
                #logger.info("=====health_violations======" + str(health_violations))
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

                                startTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(violation_startTime)) / 1000))
                                
                                violation_end_time = int(str(key2['endTime']))
                                
                                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(violation_end_time / 1000)) if violation_end_time != -1 else ""
                                
                                description = key2['description']
                                severity = key2['severity']

                                status = key2['status']
                                eval_states_list = []
                                eval_states = key2["evaluationStates"]

                                # Get List of Evaluation States
                                for state in eval_states:
                                    eval_state = {
                                        "Severity": state["severity"],
                                        "Description": state["description"],
                                        "Start Time": "",
                                        "End Time": "",
                                        "Summary": state["summary"]
                                    }
                                    eval_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(state["startTime"])) / 1000))

                                    eval_end_time = state["endTime"]
                                    eval_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(str(eval_end_time)) / 1000)) if eval_end_time else ""
                                    
                                    eval_state["Start Time"] = eval_start_time
                                    eval_state["End Time"] = eval_end_time
                                    eval_states_list.append(eval_state)
                                    
                                final_violate_list.append(
                                    {
                                        'Description': str(description),
                                        'Severity': str(severity),
                                        'Violation Id': int(key3['id']),
                                        'Affected Object': key3['bt'],
                                        'Start Time': str(startTime),
                                        'End Time': str(end_time),
                                        'Status': status,
                                        "Evaluation States": eval_states_list
                                    }
                                )
            else:
                return []
            return final_violate_list
        except Exception as e:
            logger.exception('HEV API call failed,  ' + str(e))
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for getHealthViolations: " + str(end_time - start_time))


    def getAppDApps(self):
        apps = self.databaseObject.returnValues('Application')
        list_of_apps = []
        for each in apps:
            app_data = {'appProfileName': str(each.appName), 'isViewEnabled': each.isViewEnabled}
            list_of_apps.append(app_data)
        return {'app': list_of_apps}


    def get_node_details(self, appId, nodeId):
        start_time = datetime.datetime.now()
        try:
            # self.appd_session
            node_details_response = self.appd_session.get(
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
                # self.appd_session
                node_details_response = self.appd_session.get(
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
            logger.exception('Failed to get Node Details for NodeID: ' + nodeId + ' in Application with AppID: ' + appId + '\nException: ' + str(ex))
            return []
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_node_details: " + str(end_time - start_time))


    def get_dict_records(self, list_of_records, key):
        records_dict = dict()
        records_dict[key] = list_of_records
        return records_dict


    def get_epg_history(self, timeStamp, aci_local_object):
        start_time = datetime.datetime.now()
        try:
            self.check_and_wait_till_locked()
            # aci_local_object = aci_local.ACI_Local("")

            self.check_and_wait_till_locked()
            epg_resp = aci_local_object.get_all_mo_instances("fvAEPg")

            if (epg_resp["status"]):
                epg_list = epg_resp["payload"]
                if (epg_list):
                    for epg in epg_list:
                        epg_dn = epg["fvAEPg"]["attributes"]["dn"]
                        
                        self.check_and_wait_till_locked()
                        fault_query_string = "rsp-subtree-include=fault-records,no-scoped,subtree"
                        faults_list = aci_local_object.get_mo_related_item(epg_dn, fault_query_string, "")
                        faults_dict = self.get_dict_records(faults_list, "faultRecords")
                        
                        self.check_and_wait_till_locked()
                        events_query_string = "rsp-subtree-include=event-logs,no-scoped,subtree"
                        events_list = aci_local_object.get_mo_related_item(epg_dn, events_query_string, "")
                        events_dict = self.get_dict_records(events_list, "eventRecords")

                        self.check_and_wait_till_locked()
                        audit_logs_query_string = "rsp-subtree-include=audit-logs,no-scoped,subtree"
                        audit_logs_list = aci_local_object.get_mo_related_item(epg_dn, audit_logs_query_string, "")
                        audit_logs_dict = self.get_dict_records(audit_logs_list, "auditLogRecords")

                        self.check_and_wait_till_locked()
                        health_records = aci_local_object.get_mo_related_item(epg_dn, "", "HealthRecords")
                        health_records_dict = self.get_dict_records(health_records, "healthRecords")

                        epgHistoryData = [faults_dict, health_records_dict, events_dict, audit_logs_dict, timeStamp]
                        
                        self.databaseObject.insertOrUpdate("EpgHistory", epg_dn, epgHistoryData)
                        # self.get_epg_summary(epg_dn, timeStamp)

                else:
                    logger.warning("EPgs not found")
        except Exception as ex:
            logger.exception("Exception while processing Epg History : " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_epg_history: " + str(end_time - start_time))
    
    
    def get_epg_summary(self, epg_dn, timeStamp, aci_local_object):
        start_time = datetime.datetime.now()
        try:
            # aci_local_object = aci_local.ACI_Local("")
            
            domains_dict = {"domainRecords" : []}
            subnets_dict = {"subnetRecords" : []}
            static_eps_dict = {"staticEpRecords": []}
            static_leaves_dict = {"staticLeafRecords" : []}
            fc_path_dict = {"fcPathRecords" : []}
            static_ports_dict = {"staticPortRecords" : []}

            multiple_obj_query_string = "query-target=children&target-subtree-class=fvRsDomAtt,fvSubnet,fvStCEp,fvRsNodeAtt,fvRsFcPathAtt,fvRsPathAtt"
            multiple_objs_list = aci_local_object.get_mo_related_item(epg_dn, multiple_obj_query_string, "")
            
            contracts_query_string = "query-target=subtree&target-subtree-class=fvRsCons&target-subtree-class=fvRsConsIf,fvRsProtBy,fvRsProv,vzConsSubjLbl,vzProvSubjLbl,vzConsLbl,vzProvLbl,fvRsIntraEpg"
            contracts_list = aci_local_object.get_mo_related_item(epg_dn, contracts_query_string, "")
            contracts_dict = self.get_dict_records(contracts_list, "contractRecords")

            epg_labels_query_string = "query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsToVm,fvRsVm,fvRsHyper,fvRsCEpToPathEp,fvIp,fvPrimaryEncap"
            epg_labels_list = aci_local_object.get_mo_related_item(epg_dn, epg_labels_query_string, "")
            epg_labels_dict = self.get_dict_records(epg_labels_list, "epgLabelRecords")

            if_conn_query_string = "query-target=subtree&target-subtree-class=fvIfConn"
            if_conn_list = aci_local_object.get_mo_related_item(epg_dn, if_conn_query_string, "ifConnRecords")
            if_conn_dict = self.get_dict_records(if_conn_list, "ifaceConnRecords")

            for obj in multiple_objs_list:
                for key in obj:
                    if key == "fvRsDomAtt":
                        domains_dict["domainRecords"].append(obj)
                    elif key == "fvSubnet":
                        subnets_dict["subnetRecords"].append(obj)
                    elif key == "fvStCEp":
                        static_eps_dict["staticEpRecords"].append(obj)
                    elif key == "fvRsNodeAtt":
                        static_leaves_dict["staticLeafRecords"].append(obj)
                    elif key == "fvRsFcPathAtt":
                        fc_path_dict["fcPathRecords"].append(obj)
                    elif key == "fvRsPathAtt":
                        static_ports_dict["staticPortRecords"].append(obj)

            epgSummaryData = [domains_dict, subnets_dict, static_eps_dict, static_leaves_dict, fc_path_dict, static_ports_dict, if_conn_dict, contracts_dict, epg_labels_dict, timeStamp]
            
            self.databaseObject.insertOrUpdate("EpgSummary", epg_dn, epgSummaryData)
            
        except Exception as ex:
            logger.exception("Exception while processing Epg Summary : " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_epg_summary: " + str(end_time - start_time))
    

    def get_ap_history(self, timeStamp, aci_local_object):
        start_time = datetime.datetime.now()
        try:
            self.check_and_wait_till_locked()
            # aci_local_object = aci_local.ACI_Local("")

            self.check_and_wait_till_locked()
            ap_resp = aci_local_object.get_all_mo_instances("fvAp")
            
            if (ap_resp["status"]):
                ap_list = ap_resp["payload"]
                if (ap_list):
                    for ap in ap_list:
                        ap_dn = ap["fvAp"]["attributes"]["dn"]
                        
                        self.check_and_wait_till_locked()
                        fault_query_string = "rsp-subtree-include=fault-records,no-scoped,subtree"
                        faults_list = aci_local_object.get_mo_related_item(ap_dn, fault_query_string, "")
                        faults_dict = self.get_dict_records(faults_list, "faultRecords")

                        self.check_and_wait_till_locked()
                        events_query_string = "rsp-subtree-include=event-logs,no-scoped,subtree"
                        events_list = aci_local_object.get_mo_related_item(ap_dn, events_query_string, "")
                        events_dict = self.get_dict_records(events_list, "eventRecords")

                        self.check_and_wait_till_locked()
                        audit_logs_query_string = "rsp-subtree-include=audit-logs,no-scoped,subtree"
                        audit_logs_list = aci_local_object.get_mo_related_item(ap_dn, audit_logs_query_string, "")
                        audit_logs_dict = self.get_dict_records(audit_logs_list, "auditLogRecords")
                        
                        self.check_and_wait_till_locked()
                        health_records = aci_local_object.get_mo_related_item(ap_dn, "", "HealthRecords")
                        health_records_dict = self.get_dict_records(health_records, "healthRecords")

                        apHistoryData = [faults_dict, health_records_dict, events_dict, audit_logs_dict, timeStamp]
                        
                        self.databaseObject.insertOrUpdate("ApHistory", ap_dn, apHistoryData)
                        # self.get_ap_summary(ap_dn, timeStamp)

                else:
                    logger.warning("Application Profiles not found")
        except Exception as ex:
            logger.exception("Exception while processing Application Profile History : " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_ap_history: " + str(end_time - start_time))
    

    def get_ap_summary(self, ap_dn, timeStamp, aci_local_object):
        start_time = datetime.datetime.now()
        try:
            # aci_local_object = aci_local.ACI_Local("")
            
            epg_query_string = "query-target=subtree&target-subtree-class=fvAEPg"
            epg_list = aci_local_object.get_mo_related_item(ap_dn, epg_query_string, "")
            epgs_dict = self.get_dict_records(epg_list, "epgRecords")
            
            useg_epg_query_string = "query-target=subtree&target-subtree-class=fvAEPg&query-target-filter=eq(fvAEPg.isAttrBasedEPg,\"true\")&rsp-subtree=children&rsp-subtree-class=fvRsBd"
            useg_epg_list = aci_local_object.get_mo_related_item(ap_dn, useg_epg_query_string, "")
            useg_epgs_dict = self.get_dict_records(useg_epg_list, "usegEpgRecords")
            
            ap_summary_data = [epgs_dict, useg_epgs_dict, timeStamp]

            self.databaseObject.insertOrUpdate("ApSummary", ap_dn, ap_summary_data)

        except Exception as ex:
            logger.exception("Exception while processing Ap Summary \n Error :  " + str(ex))
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_ap_summary: " + str(end_time - start_time))


    def get_config_data(self, data_key):
        start_time = datetime.datetime.now()
        path = "/home/app/data/credentials.json"
        try:
            if os.path.isfile(path):
                with open(path, "r") as creds:
                    config_data = json.load(creds)
                    data_value = config_data[data_key]
                    return data_value
        except KeyError as key_err:
            logger.error("Could not find " + data_key + " in Configuration File" + str(key_err))
            return ""
        except Exception as err:
            logger.error("Exception while fetching data from Configuration file " + str(err))
            return ""
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for get_config_data: " + str(end_time - start_time))

    def check_and_wait_till_locked(self):
        while True:
            path = "/home/app/data/SleepVar.json"
            try:
                if os.path.isfile(path):
                    with open(path, "r") as creds:
                        config_data = json.load(creds)
                        logger.debug("Sleep arg "+ config_data["sleep_var"])
                        if config_data["sleep_var"] == '1':
                            logger.debug("API calls to APIC locked since UI action is invoked. Would retry after 5 seconds")
                            time.sleep(5)
                            continue
                        else:
                            return
                else:
                    logger.error("Could not find SleepVar File")
            except Exception as err:
                err_msg = "Exception while reading sleep_var : " + str(err)
                logger.exception("{}".format(err_msg))
        

    def main(self):
        while True:
            
            start_time = datetime.datetime.now()
            timeStamp = datetime.datetime.utcnow()

            self.databaseObject = AppD_Database.Database()
            self.check_connection()
            logger.info('===Starting Database Update!')
            
            
            try:
                apps = self.get_app_info()
                logger.info('Total apps found in the DB:' + str(len(apps)))
            except Exception as e:
                logger.exception('Exception in fetching Apps, Error:' + str(e))
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
                                                                   [app.get('id'), str(app.get('name')), app_metrics, timeStamp])
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

                                # logger.info('Updated Tiers: Total - ' + str(len(tiers)))
                            for tier in tiers:
                                tier_health = self.get_tier_health(tier.get('id'))
                                if tier_health != 'UNDEFINED':
                                    #logger.info('Tier health:' + str(tier_health))
                                    #continue
                                    # Service Endpoints
                                    #logger.info('Updating SEVs')
                                    service_endpoints = self.get_service_endpoints(app.get('id'), tier.get('id'))
                                    if service_endpoints:
                                        # sepId, sep, tierId
                                        try:
                                            for sep in service_endpoints:
                                                self.databaseObject.checkIfExistsandUpdate('ServiceEndpoints',
                                                                                           [sep.get('sepId'), sep,
                                                                                            tier.get('id'),
                                                                                            app.get('id'), timeStamp])
                                                sepList.append(sep['sepId'])
                                                # self.databaseObject.commitSession()
                                        except Exception as e:
                                            logger.exception('Exception in SEV, Error:'+str(e))
                                    #logger.info('Updating HEVs')
                                    # HealthViolations
                                    tierViolations = self.getHealthViolations(str(app.get('id')), tier_id=tier.get('id'))
                                    if tierViolations:
                                        try:
                                            for violations in tierViolations:
                                                eval_states_dict = self.get_dict_records(violations.get('Evaluation States'), "evaluationStates")
                                                violations_list = [
                                                    violations.get('Start Time'), violations.get('Affected Object'),
                                                    violations.get('Description'), violations.get('Severity'),
                                                    tier.get('id'), app.get('id'), timeStamp,
                                                    violations.get('End Time'), violations.get('Status'), eval_states_dict
                                                ]
                                                self.databaseObject.insertOrUpdate('HealthViolations', violations.get('Violation Id'), violations_list)
                                                violationList.append(violations.get('Violation Id'))
                                        except Exception as e:
                                            logger.exception('Exception in HEV, Error:'+str(e))
                                    #logger.info('Updated SEPs and HEVs')

                                    # Nodes
                                    if tier.get('numberOfNodes') > 0:
                                        nodes = self.get_node_info(app.get('id'), tier.get('id'))
                                        ipList = []
                                        macList = []
                                        #logger.info(nodes)
                                        if len(nodes) > 0:
                                            for node in nodes:
                                                node_health = self.get_node_health(node.get('id'))
                                                if node_health != 'UNDEFINED':
                                                    #logger.info('Node health:' + str(node_health))

                                                    # get mac-address for node
                                                    macList = self.get_node_mac(node.get('id'))
                                                    logger.info("mac list::"+str(macList)+" for node "+str(node.get("id")))
                                                    # get ip-address for node
                                                    if 'ipAddresses' in node:
                                                        # If 'ipAddresses' key is None, we make another API Call to get the Node Details
                                                        if not node.get('ipAddresses'):
                                                            node_details = self.get_node_details(app.get('id'), node.get('id'))                                                            
                                                            if node_details:
                                                                node = node_details[0]

                                                                if not node.get('ipAddresses'):
                                                                    logger.warning("No 'ipAddresses' found in Node Details Response. \nResponse : " + str(node_details))
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
                                                                                                ipList, app.get('id'), timeStamp, macList])
                                                    nodeidlist.append(node.get('id'))
                                                    logger.info(
                                                        'Record: App_id - ' + str(app.get('id')) + ', AppName - ' + str(
                                                            app.get('name')) + ', Tier - ' + str(
                                                            tier.get('id')) + ', Node - ' + str(node.get('id')))
                                                        
                    self.databaseObject.checkAndDelete('Application', appidList)
                    self.databaseObject.checkAndDelete('Tiers', tieridList)
                    self.databaseObject.checkAndDelete('ServiceEndpoints', sepList)
                    self.databaseObject.checkAndDelete('HealthViolations', violationList)
                    self.databaseObject.checkAndDelete('Nodes', nodeidlist)

                    self.databaseObject.commitSession()

                    aci_local_object = aci_local.ACI_Local("")

                    self.check_and_wait_till_locked()
                    self.get_epg_history(timeStamp, aci_local_object)
                    
                    self.check_and_wait_till_locked()
                    self.get_ap_history(timeStamp, aci_local_object)
                    
                    self.databaseObject.commitSession()

                    polling_interval = self.get_config_data("polling_interval")
                    
                    # Get Polling Interval from Config File
                    if not polling_interval:
                        logger.exception("Exception while getting Polling Interval\nTaking Default Polling Interval of 60 Seconds...")
                        polling_interval = 60
                    else:
                        polling_interval = int(polling_interval)
                        polling_interval = polling_interval * 60

                    end_time =  datetime.datetime.now()
                    total_time = str(end_time - start_time)
                    
                    logger.info("===Time for main_thread===" + total_time)
                    logger.info("====polling_interval====" + str(polling_interval))
                    logger.info('===Database Update Complete!')
                    
                    # logger.info(total_time)
                    
                    time.sleep(polling_interval)  # threading.Timer(60, self.main).start()
            except Exception as e:
                logger.exception('Exception in AppDInfoData Main, Error: ' + str(e))
                self.databaseObject.commitSession()
                time.sleep(polling_interval)
                self.main()
