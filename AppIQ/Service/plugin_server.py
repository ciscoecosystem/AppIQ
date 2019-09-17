__author__ = 'nilayshah'

from flask import Flask, render_template, request, redirect, url_for, jsonify
import json, time, logging, os, pprint
import threading
import socket
import re
import datetime
# import ACI_Info as aci_local
import ACI_Local as aci_local
import AppDInfoData as AppDConnect
import AppD_Alchemy as Database
import generate_d3 as d3
import RecommendedDNObjects as Recommend
from multiprocessing import Process, Value
from custom_logger import CustomLogger

app = Flask(__name__, template_folder="../UIAssets", static_folder="../UIAssets/public")
app.debug = True

logger = CustomLogger.get_logger("/home/app/log/app.log")

# appd_object = AppDConnect.AppD('10.23.239.14', 'user1', 'customer1', 'welcome')
# appd_object = AppDConnect.AppD('192.168.132.125', 'user1', 'customer1', 'Cisco!123')

# To run anywhere other than APIC
# aci_object = aci_local.ACI("10.23.239.23", "admin", "cisco123")
# aci_object = aci_local.ACI("192.168.130.10", "admin", "Cisco!123")
database_object = Database.Database()
d3Object = d3.generateD3Dict()


def  getInstanceName():
    instance_path = '/home/app/data/credentials.json' # On APIC
    instance_exists = os.path.isfile(instance_path)
    if instance_exists:
        try:
            with open(instance_path, 'r') as creds:
                instance_creds = json.load(creds)
                instanceName = str(str(instance_creds['appd_ip']).split('//')[1])
                #print "AppD Controller = "+ instanceName
                return instanceName
        except:
            instanceName = "N/A"
            pass
    else:
        return "N/A"


@app.route('/check.json', methods=['GET', 'POST'])
def checkFile():
    start_time = datetime.datetime.now()
    logger.info('Checking if File Exists')
    path = '/home/app/data/credentials.json'
    # path = "/Users/nilayshah/Desktop/AppD_cisco23lab/Cisco_AppIQ/Service/credentials.json"
    file_exists = os.path.isfile(path)
    # print file_exists
    if not file_exists:
        end_time =  datetime.datetime.now()
        logger.error("Time for checkFile File NOT found: " + str(end_time - start_time))
        
        return json.dumps({"payload": "File does not exists", "status_code": "300",
                           "message": "AppDynamics is not configured. Please login!"})
        # return 'False'
    else:
        try:
            with open(path, 'r') as creds:
                # with open('/Users/nilayshah/Desktop/AppD_cisco23lab/Cisco_AppIQTest/Service/credentials.json', 'w+') as creds:
                app_creds = json.load(creds)
                appd_ip = app_creds["appd_ip"]
                appd_port = app_creds["appd_port"]
                appd_user = app_creds["appd_user"]
                appd_account = app_creds["appd_account"]
                appd_pw = app_creds["appd_pw"]
            # print appd_ip
            appd_object = AppDConnect.AppD(appd_ip, appd_port, appd_user, appd_account, appd_pw)
            status = appd_object.check_connection()
            # print status - Change it to logger
            if status == 200 or status == 201:
                return json.dumps({"payload": "Signed in", "status_code": "200", "message": "OK"})
            else:
                return json.dumps({"payload": "Not signed in", "status_code": str(status),
                                   "message": "Exited with code: " + str(
                                       status) + ". Please verify AppDynamics connection"})
        except Exception as e:
            return json.dumps({"payload": "Not logged in", "status_code": "300",
                               "message": str(e) + ". Please re-configure AppDynamics Controller!"})
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for checkFile: " + str(end_time - start_time))
    


def parseHost(ip):
    try:
        parsed_host = socket.gethostbyname(ip)
        if parsed_host:
            return ip
    except:
        return ""


@app.route('/login.json', methods=['GET', 'POST'])
def login(appd_creds):
    start_time = datetime.datetime.now()
    logger.info('Entered Login')
    host = str(appd_creds["appd_ip"])
    appd_port = str(appd_creds["appd_port"])
    appd_user = str(appd_creds["appd_user"])
    appd_account = str(appd_creds["appd_account"])
    appd_pw = str(appd_creds["appd_pw"])
    if 'http://' in host or 'https://' in host:
        parsed_ip = host.split('://')[1]
        if '/' in parsed_ip:
            ip = parsed_ip.split('/')[0]
        else:
            ip = parsed_ip
        valid_ip = parseHost(ip)
        proto = host.split('://')[0]
        appd_ip = proto + "://"+valid_ip
    else:
        appd_ip = "https://"+parseHost(host)
    # parsed_host = parseHost(appd_ip)
    credentials = {'appd_ip': appd_ip, 'appd_port': appd_port, 'appd_user': appd_user, 'appd_account': appd_account,
                   'appd_pw': appd_pw, 'polling_interval': '1'}
    sleep_cred = {'sleep_var': '0'}
    appd_object = AppDConnect.AppD(appd_ip, appd_port, appd_user, appd_account, appd_pw)
    try:
        login_check = appd_object.check_connection()
        # print login_check

        if login_check == 200 or login_check == 201:
            # path = "/Users/nilayshah/Desktop/AppD_cisco23lab/Cisco_AppIQ/Service/credentials.json"
            path = "/home/app/data/credentials.json"

            # New file for sleep_var
            with open("/home/app/data/SleepVar.json", 'w+') as screds:
                screds.seek(0)
                screds.truncate()
                json.dump(sleep_cred, screds)
                screds.close()

            # This is the main process being started.
            Process(target=appd_object.main).start()
            
            # with open('/home/app/credentials/credentials.json', 'w+') as creds:
            with open(path, 'w+') as creds:
                creds.seek(0)
                creds.truncate()
                json.dump(credentials, creds)
                creds.close()
            logger.info('Login Successful!')
            #threading.Thread(target=appd_object.main).start()#appd_object.main()
            # time.sleep(4)
            return json.dumps({"payload": "Connection Successful", "status_code": "200",
                               "message": "Credentials Saved!"})  # login_resp
        else:
            logger.error("login failed:"+str(login_check))
            return json.dumps({"payload": "Login to AppDynamics Failed", "status_code": str(login_check),
                                "message": "Login to AppDynamics failed, exited with code: " + str(
                                    login_check) + ". Please verify AppDynamics connection"})

    except Exception as e:
        return json.dumps({"payload": "Not signed in", "status_code": "300",
                           "message": "An error occured while saving AppDynamics Credentials. Please try again! Error: "+str(e)})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for LOGIN to APP: " + str(end_time - start_time))


def setPollingInterval(interval):
    """
    Sets the polling interval in AppDynamics config file
    """

    start_time = datetime.datetime.now()
    path = "/home/app/data/credentials.json"
    try:
        if os.path.isfile(path):
            with open(path, "r+") as creds:
                config_data = json.load(creds)
                config_data["polling_interval"] = str(interval)

                creds.seek(0)
                creds.truncate()
                json.dump(config_data, creds)
            
            return "200", "Polling Interval Set!"
        else:
            return "300", "Could not find Configuration File"
    except Exception as err:
        err_msg = "Exception while setting polling Interval : " + str(err)
        logger.error(err_msg)
        return "300", err_msg
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for setPollingInterval: " + str(end_time - start_time))
    

def setSleepVar(sleep_var):
    """
    Sets the sleeping variable in config file
    """
    
    start_time = datetime.datetime.now()
    path = "/home/app/data/SleepVar.json"
    try:
        if os.path.isfile(path):
            with open(path, "r+") as creds:
                config_data = json.load(creds)
                if sleep_var:
                    config_data["sleep_var"] = str(1)
                else:
                    config_data["sleep_var"] = str(0)

                creds.seek(0)
                creds.truncate()
                json.dump(config_data, creds)
            
            return True
        else:
            raise Exception
    except Exception as err:
        err_msg = "Exception while setting sleeping variable : " + str(err)
        logger.error(err_msg)
        return False, err_msg
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for setSleepVar: " + str(end_time - start_time))


#@app.route('/apps.json', methods=['GET'])  # This shall be called from /check.json, for Cisco Live this is the first/start Route
def apps(tenant):
    start_time = datetime.datetime.now()
    try:
        logger.info("UI Action app.json started")
        
        appsList = database_object.getappList()
        app_dict = {}
        app_list = []
        for each in appsList:
            temp_dict = {'appProfileName': each['appName'], 'isViewEnabled': each['isViewEnabled'],
                         'health': str(each['appHealth']), 'appId': each['appId']}
            app_list.append(temp_dict)
            if each.get('isViewEnabled') == True:
                mapped_objects = mapping(tenant,each['appId'])
        app_dict['app'] = app_list
        
        logger.info("UI Action app.json ended")
        #time.sleep(5)
        return json.dumps({"instanceName":getInstanceName(),"payload": app_dict, "status_code": "200", "message": "OK"})
        # return json.dumps(dict)
    except Exception as e:
        logger.exception("Could not fetch applications from databse. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not fetch applications from databse. Error: "+str(e)})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for APPS: " + str(end_time - start_time))


@app.route('/mapping.json', methods=['GET'])
def mapping(tenant, appDId):
    start_time = datetime.datetime.now()
    try:
        #time.sleep(1)
        appId = str(appDId) + str(tenant)
        mapping_dict = {"source_cluster": [], "target_cluster": []}
        
        # returns the mapping from Mapping Table
        already_mapped_data = database_object.returnMapping(appId)
        #logger.info('Already Mapped Data:'+str(already_mapped_data))
        rec_object = Recommend.Recommend()
        mapped_objects = rec_object.correlate_ACI_AppD(tenant, appDId)
        logger.info('Post correlation of ACI and AppD')
        #logger.info(mapped_objects)
        if not mapped_objects:
            logger.info('Empty Mapping dict for appDId:'+str(appDId))
            return json.dumps({"instanceName":getInstanceName(),"payload": mapping_dict, "status_code": "200","message": "OK"})
        if already_mapped_data != None:
            logger.info('Mapping to target cluster already exists')
            mapping_dict['target_cluster'] = already_mapped_data
        else:
            app_list = database_object.getappList()
            logger.info('AppD App List for Mapping after already mapped: '+str(app_list))
            
            # Why not get the App with given AppId from DB??
            for each in app_list:
                if each.get('appId') == appDId and each.get('isViewEnabled') == True:
                    logger.info("Mapping Empty!")
                    target = []
                    for each in mapped_objects:
                        # print each
                        for entry in each['domains']:
                            if entry['recommended'] == True:
                                target.append({'domainName': entry['domainName'], 'ipaddress': each['ipaddress']})
                                mapping_dict['target_cluster'] = target
                    data_list = []
                    logger.info('Target mapping for app:'+str(appDId))
                    for mapping in target:
                        data_list.append({'ipaddress': mapping['ipaddress'], 'domainName': mapping['domainName']})
                    database_object.checkIfExistsandUpdate('Mapping', [appId, data_list])
                    # saveMapping(appId,target)
                    view_enabled = enableView(appId, True)
        if mapped_objects:
            for new in mapped_objects:
                mapping_dict['source_cluster'].append(new)

        return json.dumps({"instanceName":getInstanceName(),"payload": mapping_dict, "status_code": "200",
                           "message": "OK"})  # {"source_cluster": mapped_objects, "target_cluster": {{dn:IP},{dn:IP}}}
    except Exception as e:
        logger.exception('Exception in Mapping, Error:'+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not fetch mappings from the database. Error: "+str(e)})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for MAPPING: " + str(end_time - start_time))


@app.route('/saveMapping.json', methods=['POST'])
def saveMapping(appDId, tenant, mappedData):
    start_time = datetime.datetime.now()
    try:
        appId = str(appDId) + str(tenant)
        logger.info('Saving Mappings for app:'+str(appId))
        mappedData_dict = json.loads(
            (str(mappedData).strip("'<>() ").replace('\'', '\"')))  # new implementation for GraphQL
        data_list = []
        for mapping in mappedData_dict:
            data_list.append({'ipaddress': mapping['ipaddress'], 'domainName': mapping['domains'][0]['domainName']})
        if not data_list:
            database_object.deleteEntry('Mapping', appId)
            #enableView(appDId, False)
            return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})
        else:
            database_object.deleteEntry('Mapping', appId)
            database_object.checkIfExistsandUpdate('Mapping', [appId, data_list])
            enableView(appDId, True)
            return json.dumps({"payload": "Saved Mappings", "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not save mappings to the database. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not save mappings to the database. Error: "+str(e)})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for saveMapping: " + str(end_time - start_time))


def getFaults(dn):
    """
    Get List of Faults related to the given MO from Database
    """
    faults_resp = database_object.returnFaults(dn)
    if faults_resp["status"]:
        faults_list = faults_resp["payload"]
        faults_payload = []
        for fault in faults_list:
            fault_attr = fault["faultRecord"]["attributes"]
            fault_dict = {
                "code" : fault_attr["code"],
                "severity" : fault_attr["severity"],
                "affected" : fault_attr["affected"],
                "descr" : fault_attr["descr"],
                "created" : fault_attr["created"]
            }
            faults_payload.append(fault_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": faults_payload
        })
    else:
        logger.error("Error in fetching Fault List from Databse!")
        return json.dumps({
            "status_code": "300",
            "message": faults_resp["message"],
            "payload": []
        })

def getEvents(dn):
    """
    Get List of Events related to the given MO from Database
    """
    events_resp = database_object.returnEvents(dn)
    if events_resp["status"]:
        events_list = events_resp["payload"]
        events_payload = []
        for event in events_list:
            event_attr = event["eventRecord"]["attributes"]
            event_dict = {
                "code" : event_attr["code"],
                "severity" : event_attr["severity"],
                "affected" : event_attr["affected"],
                "descr" : event_attr["descr"],
                "created" : event_attr["created"],
                "cause" : event_attr["cause"]
            }
            events_payload.append(event_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": events_payload
        })
    else:
        logger.error("Error in fetching Event List from Databse!")
        return json.dumps({
            "status_code": "300",
            "message": events_resp["message"],
            "payload": []
        })

def getAuditLogs(dn):
    """
    Get List of Audit Log Records related to the given MO from Database
    """
    audit_logs_resp = database_object.returnAuditLogs(dn)
    if audit_logs_resp["status"]:
        audit_logs_list = audit_logs_resp["payload"]
        audit_logs_payload = []
        for audit_log in audit_logs_list:
            audit_log_attr = audit_log["aaaModLR"]["attributes"]
            audit_log_dict = {
                "affected" : audit_log_attr["affected"],
                "descr" : audit_log_attr["descr"],
                "created" : audit_log_attr["created"],
                "id" : audit_log_attr["id"],
                "action" : audit_log_attr["ind"],
                "user" : audit_log_attr["user"]
            }
            audit_logs_payload.append(audit_log_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": audit_logs_payload
        })
    else:
        logger.error("Error in fetching Audit Logs List from Databse!")
        return json.dumps({
            "status_code": "300",
            "message": audit_logs_resp["message"],
            "payload": []
        })

def getChildrenEpInfo(dn, mo_type, ip_list):
    start_time = datetime.datetime.now()
    aci_local_object = aci_local.ACI_Local("")
    if mo_type == "ep":
        ip_list = ip_list.split(",")
        ip_query_filter_list = []
        for ip in ip_list:
            ip_query_filter_list.append('eq(fvCEp.ip,"' + ip + '")')
        ip_query_filter = ",".join(ip_query_filter_list)

        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&query-target-filter=or(' + ip_query_filter +')&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsVm'
    elif mo_type == "epg":
        ep_info_query_string = 'query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsHyper,fvRsCEpToPathEp,fvRsVm'

    ep_list = aci_local_object.get_mo_related_item(dn, ep_info_query_string, "")
    ep_info_list = []
    try:
        for ep in ep_list:
            ep_info_dict = dict()

            ep_children = ep["fvCEp"]["children"]
            ep_info = getEpInfo(ep_children, aci_local_object)
            ep_attr = ep["fvCEp"]["attributes"]

            mcast_addr = ep_attr["mcastAddr"]
            if mcast_addr == "not-applicable":
                mcast_addr = "---"

            ep_info_dict = {
                "ip" : ep_attr["ip"],
                "mac" : ep_attr["mac"],
                "mcast_addr" : mcast_addr,
                "learning_source" : ep_attr["lcC"],
                "encap" : ep_attr["encap"],
                "ep_name" : ep_info["ep_name"],
                "hosting_server_name" : ep_info["hosting_server_name"],
                "iface_name" : ep_info["iface_name"],
                "ctrlr_name" : ep_info["ctrlr_name"]
            }
            ep_info_list.append(ep_info_dict)
        return json.dumps({
            "status_code": "200",
            "message": "OK",
            "payload": ep_info_list
        })
    except Exception as e:
        logger.exception("Exception while getting Children Ep Info : " + str(e))
        return json.dumps({
            "status_code": "300",
            "message": {'errors':str(e)},
            "payload": []
        })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for getChildrenEpInfo: " + str(end_time - start_time))
    

def getEpInfo(ep_children_list, aci_local_object):

    ep_info = {
        "ctrlr_name" : "",
        "hosting_server_name" : "",
        "iface_name" : "",
        "ep_name" : ""
    }
    for ep_child in ep_children_list:
        
        child_name = ep_child.keys()[0]
        if child_name == "fvRsHyper":
            hyperDn = ep_child["fvRsHyper"]["attributes"]["tDn"]
            try:
                ctrlr_name = re.compile("\/ctrlr-\[.*\]-").split(hyperDn)[1].split("/")[0]
            except Exception as e:
                logger.exception("Exception in EpInfo: " + str(e))
                ctrlr_name = ""

            hyper_query_string = 'query-target-filter=eq(compHv.dn,"' + hyperDn + '")'
            hyper_resp = aci_local_object.get_all_mo_instances("compHv", hyper_query_string)

            if hyper_resp["status"]:
                if hyper_resp["payload"]:
                    hyper_name = hyper_resp["payload"][0]["compHv"]["attributes"]["name"]
                else:
                    logger.error("Could not get Hosting Server Name using Hypervisor info")
                    hyper_name = ""
            else:
                hyper_name = ""
            ep_info["ctrlr_name"] = ctrlr_name
            ep_info["hosting_server_name"] = hyper_name

        elif child_name == "fvRsCEpToPathEp":
            name = ep_child["fvRsCEpToPathEp"]["attributes"]["tDn"]
            if re.match('topology\/pod-+\d+\/pathgrp-.*',name):
                pod_number = name.split("/pod-")[1].split("/")[0]
                node_number = get_node_from_interface(name)
                #The ethernet name is NOT available
                eth_name = ''
                iface_name = "Pod-" + pod_number + "/Node-" + node_number + "/" + eth_name
                ep_info["iface_name"] = iface_name
            elif re.match('topology\/pod-+\d+\/paths-\d+\/pathep-.*',name):
                pod_number = name.split("/pod-")[1].split("/")[0]
                node_number = get_node_from_interface(name)
                eth_name = name.split("/pathep-[")[1][0:-1]
                iface_name = "Pod-" + pod_number + "/Node-" + node_number + "/" + eth_name
                ep_info["iface_name"] = iface_name
            elif re.match('topology\/pod-+\d+\/protpaths-\d+\/pathep-.*',name):
                pod_number = name.split("/pod-")[1].split("/")[0]
                node_number = get_node_from_interface(name)
                eth_name = name.split("/pathep-[")[1][0:-1]
                iface_name = "Pod-" + pod_number + "/Node-" + node_number + "/" + eth_name
                ep_info["iface_name"] = iface_name
            else:
                logger.error("Different format of interface is found: {}".format(name))
                raise Exception("Different format of interface is found: {}".format(name))

        elif child_name == "fvRsVm":
            vm_dn = ep_child["fvRsVm"]["attributes"]["tDn"]

            vm_query_string = 'query-target-filter=eq(compVm.dn,"' + vm_dn + '")'
            vm_resp = aci_local_object.get_all_mo_instances("compVm", vm_query_string)

            if vm_resp["status"]:
                if vm_resp["payload"]:
                    vm_name = vm_resp["payload"][0]["compVm"]["attributes"]["name"]
                else:
                    logger.error("Could not get Name of EP using VM info")
                    vm_name = ""
            else:
                vm_name = ""
            ep_info["ep_name"] = vm_name
    
    return ep_info


def getConfiguredAccessPolicies(tn, ap, epg):
    start_time = datetime.datetime.now()
    aci_local_object = aci_local.ACI_Local("")
    cap_url = "/mqapi2/deployment.query.json?mode=epgtoipg&tn=" + tn + "&ap=" + ap + "&epg=" + epg
    cap_resp = aci_local_object.get_mo_related_item("", cap_url, "other_url")
    cap_list = []
    try:
        for cap in cap_resp:
            cap_dict = {
                "domain" : "",
                "switch_prof" : "",
                "aep" : "",
                "iface_prof" : "",
                "pc_vpc" : "",
                "node" : "",
                "path_ep" : "",
                "vlan_pool" : ""
            }
            cap_attr = cap["syntheticAccessPolicyInfo"]["attributes"]
            if re.search("/vmmp-",cap_attr["domain"]):
                # Get Domain Name of Configure Access Policy
                cap_vmm_prof = cap_attr["domain"].split("/vmmp-")[1].split("/")[0]
            else:
                logger.error("Attribute {} not found".format("domain"))
                raise Exception("Attribute {} not found".format("domain"))
            if re.search("/dom-",cap_attr["domain"]):
                cap_domain_name = cap_attr["domain"].split("/dom-")[1]
            else:
                logger.error("Attribute {} not found".format("domain"))
                raise Exception("Attribute {} not found".format("domain"))
            cap_dict["domain"] = cap_vmm_prof + "/" + cap_domain_name
            if re.search("/nprof-",cap_attr["nodeP"]):
                cap_dict["switch_prof"] = cap_attr["nodeP"].split("/nprof-")[1]
            else:
                logger.error("Attribute {} not found".format("nodeP"))
                raise Exception("Attribute {} not found".format("nodeP"))
            if re.search("/attentp-",cap_attr["attEntityP"]):
                cap_dict["aep"] = cap_attr["attEntityP"].split("/attentp-")[1]
            else:
                logger.error("Attribute {} not found".format("attEntityP"))
                raise Exception("Attribute {} not found".format("attEntityP"))
            if re.search("/accportprof-",cap_attr["accPortP"]):
                cap_dict["iface_prof"] = cap_attr["accPortP"].split("/accportprof-")[1]
            else:
                logger.error("Attribute {} not found".format("accPortP"))
                raise Exception("Attribute {} not found".format("accPortP"))
            if re.search("/accportgrp-",cap_attr["accBndlGrp"]):
                cap_dict["pc_vpc"] = cap_attr["accBndlGrp"].split("/accportgrp-")[1]
            elif re.search("/accbundle-",cap_attr["accBndlGrp"]):
                cap_dict["pc_vpc"] = cap_attr["accBndlGrp"].split("/accbundle-")[1]
            pc_pvc = re.search('\w+\/\w+\/\w+\/\w+-(.*)',cap_attr["accBndlGrp"])
            if pc_pvc:
                cap_dict["pc_vpc"] = pc_pvc.groups()[0]
            else:
                logger.error("Attribute {} not found".format("accBndlGrp"))
                raise Exception("Attribute {} not found".format("accBndlGrp"))
            cap_dict["node"] = get_node_from_interface(cap_attr["pathEp"])
            if not cap_dict["node"]:
                logger.error("Attribute {} not found".format("node"))
                raise Exception("attribute node not found")
            if re.search("/pathep-",cap_attr["pathEp"]):
                cap_dict["path_ep"] = cap_attr["pathEp"].split("/pathep-")[1][1:-1]
            else:
                logger.error("Attribute {} not found".format("pathEP"))
                raise Exception("Attribute {} not found".format("pathEp"))
            if re.search("/from-",cap_attr["vLanPool"]):
                cap_dict["vlan_pool"] = cap_attr["vLanPool"].split("/from-")[1]
            else:
                logger.error("Attribute {} not found".format("vLanpool"))
                raise Exception("Attribute {} not found".format("vLanpool"))
            cap_list.append(cap_dict)
        
        return json.dumps({
            "status_code": "200",
            "message": "",
            "payload": cap_list
        })
    except Exception as ex:
        return json.dumps({
            "status_code": "300",
            "message": {'errors':str(ex)},
            "payload": []
        })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for getConfiguredAccessPolicies: " + str(end_time - start_time))


def getSubnets(dn):
    """
    Gets the Subnets Information for an EPG
    """
    start_time = datetime.datetime.now()
    aci_local_object = aci_local.ACI_Local("")
    subnet_query_string = "query-target=children&target-subtree-class=fvSubnet"
    subnet_resp = aci_local_object.get_mo_related_item(dn, subnet_query_string, "")
    subnet_list = []
    try:
        for subnet in subnet_resp:
            subnet_dict = {
                "ip" : "",
                "to_epg" : "",
                "epg_alias" : ""
            }
            subnet_attr = subnet["fvSubnet"]["attributes"]
            subnet_dict["ip"] = subnet_attr["ip"]
            subnet_list.append(subnet_dict)
        
        return json.dumps({
            "status_code": "200",
            "message": "",
            "payload": subnet_list
        })
    except Exception as ex:
        return json.dumps({
            "status_code": "300",
            "message": str(ex),
            "payload": []
        })
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for one: " + str(end_time - start_time))


def getToEpgTraffic(epg_dn):
    """
    Gets the Traffic Details from the given EPG to other EPGs
    """

    start_time = datetime.datetime.now()
    aci_local_object = aci_local.ACI_Local("")
    epg_traffic_query_string = 'query-target-filter=eq(vzFromEPg.epgDn,"' + epg_dn + '")&rsp-subtree=full&rsp-subtree-class=vzToEPg,vzRsRFltAtt,vzCreatedBy&rsp-subtree-include=required'
    epg_traffic_resp = aci_local_object.get_all_mo_instances("vzFromEPg", epg_traffic_query_string)
    if epg_traffic_resp["status"]:
        epg_traffic_resp = epg_traffic_resp["payload"]

        from_epg_dn = epg_dn
        
        to_epg_traffic_list = []
        to_epg_traffic_set = set()
        
        try:
            for epg_traffic in epg_traffic_resp:
                to_epg_children = epg_traffic["vzFromEPg"]["children"]

                for to_epg_child in to_epg_children:

                    vz_to_epg_child = to_epg_child["vzToEPg"]

                    to_epg_dn = vz_to_epg_child["attributes"]["epgDn"]
                    if re.match("/tn-",to_epg_dn):
                        tn = to_epg_dn.split("/tn-")[1].split("/")[0]
                    else :
                        logger.error("attribute 'tn' not found in epgDn")
                        raise Exception("attribute 'tn' not found in epgDn")
                    if re.match("/ap-",to_epg_dn):
                        ap = to_epg_dn.split("/ap-")[1].split("/")[0]
                    else :
                        logger.error("attribute 'ap' not found in epgDn")
                        raise Exception("attribute 'ap' not found in epgDn")
                    if re.match("/epg-",to_epg_dn):
                        epg = to_epg_dn.split("/epg-")[1]
                    else :
                        logger.error("attribute 'epg' not found in epgDn")
                        raise Exception("attribute 'epg' not found in epgDn")
                    parsed_to_epg_dn = tn + "/" + ap + "/" + epg

                    flt_attr_children = vz_to_epg_child["children"]

                    for flt_attr in flt_attr_children:
                        to_epg_traffic_dict = {
                            "to_epg" : "",
                            "contract_subj" : "",
                            "filter_list" : [],
                            "ingr_pkts" : "",
                            "egr_pkts" : "",
                            "epg_alias" : "",
                            "contract_type" : ""
                        }

                        to_epg_traffic_dict["to_epg"] = parsed_to_epg_dn

                        flt_attr_child = flt_attr["vzRsRFltAtt"]
                        flt_attr_tdn = flt_attr_child["attributes"]["tDn"]

                        traffic_id = parsed_to_epg_dn + "||" + flt_attr_tdn

                        # Check if we have already encountered the filter for a particular destination EPG
                        if traffic_id in to_epg_traffic_set:
                            to_epg_traffic_set.add(traffic_id)
                            continue
                        if re.match("/fp-",flt_attr_tdn):
                            flt_name = flt_attr_tdn.split("/fp-")[1]
                        else:
                            logger.error("filter not found")
                            raise Exception("filter not found")
                        flt_attr_subj_dn = flt_attr_child["children"][0]["vzCreatedBy"]["attributes"]["ownerDn"]
                        if re.match("/rssubjFiltAtt-",flt_attr_subj_dn):
                            subj_dn = flt_attr_subj_dn.split("/rssubjFiltAtt-")[0]
                        else:
                            logger.error("filter attribute subject not found")
                            raise Exception("filter attribute subject not found")
                        if re.match("/tn-",flt_attr_subj_dn):
                            subj_tn = flt_attr_subj_dn.split("/tn-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute subject dn not found")
                            raise Exception("filter attribute subject dn not found")
                        
                        if re.match("/brc-",flt_attr_subj_dn):
                            subj_ctrlr = flt_attr_subj_dn.split("/brc-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute ctrlr not found")
                            raise Exception("filter attribute ctrlr not found")
                        if re.match("/subj-",flt_attr_subj_dn):
                            subj_name = flt_attr_subj_dn.split("/subj-")[1].split("/")[0]
                        else:
                            logger.error("filter attribute subj_name not found")
                            raise Exception("filter attribute subj_name not found")
                        
                        contract_subject = subj_tn + "/" + subj_ctrlr + "/" + subj_name
                        flt_list = getFilterList(flt_attr_tdn, aci_local_object)
                        ingr_pkts, egr_pkts = getIngressEgress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_local_object)
                                            
                        to_epg_traffic_dict["contract_subj"] = contract_subject
                        to_epg_traffic_dict["filter_list"] = flt_list
                        to_epg_traffic_dict["ingr_pkts"] = ingr_pkts
                        to_epg_traffic_dict["egr_pkts"] = egr_pkts

                        to_epg_traffic_set.add(traffic_id)
                        to_epg_traffic_list.append(to_epg_traffic_dict)

            return json.dumps({
                "status_code": "200",
                "message": "",
                "payload": to_epg_traffic_list
            })

        except Exception as ex:
            logger.exception("Exception while fetching To EPG Traffic List : \n" + str(ex))
            
            return json.dumps({
                "status_code": "300",
                "message": {'errors':str(ex)},
                "payload": []
            })
        finally:
            end_time =  datetime.datetime.now()
            logger.info("Time for getToEpgTraffic: " + str(end_time - start_time))
    else:
        logger.error("Could not get Traffic Data related to EPG")
        end_time =  datetime.datetime.now()
        logger.info("Time for getToEpgTraffic: " + str(end_time - start_time))
        return json.dumps({
            "status_code": "300",
            "message": "Exception while fetching Traffic Data related to EPG",
            "payload": []
        })


def getIngressEgress(from_epg_dn, to_epg_dn, subj_dn, flt_name, aci_local_object):
    """
    Returns the Cumulative Ingress and Egress packets information for the last 15 minutes
    """
    start_time = datetime.datetime.now()
    cur_aggr_stats_query_url = "/api/node/mo/" + from_epg_dn + "/to-[" + to_epg_dn + "]-subj-[" + subj_dn + "]-flt-" + flt_name + "/CDactrlRuleHitAg15min.json"
    cur_aggr_stats_list = aci_local_object.get_mo_related_item("", cur_aggr_stats_query_url, "other_url")

    if cur_aggr_stats_list:
        cur_ag_stat_attr = cur_aggr_stats_list[0]["actrlRuleHitAg15min"]["attributes"]
        ingr_pkts = cur_ag_stat_attr["ingrPktsCum"]
        egr_pkts = cur_ag_stat_attr["egrPktsCum"]
        end_time =  datetime.datetime.now()
        logger.info("Time for getIngressEgress: " + str(end_time - start_time))
        return ingr_pkts, egr_pkts
    else:
        end_time =  datetime.datetime.now()
        logger.info("Time for getIngressEgress: " + str(end_time - start_time))
        return "0", "0"


def getFilterList(flt_dn, aci_local_object):
    """
    Returns the list of filters for a given destination EPG
    """
    start_time = datetime.datetime.now()
    flt_list = []
    flt_entry_query_string = "query-target=children&target-subtree-class=vzRFltE"
    flt_entries = aci_local_object.get_mo_related_item(flt_dn, flt_entry_query_string, "")

    for flt_entry in flt_entries:
        flt_attr = flt_entry["vzRFltE"]["attributes"]
        
        ether_type = flt_attr["etherT"]

        if ether_type == "unspecified":
            flt_list.append("*")
            continue
        
        protocol = flt_attr["prot"] if flt_attr["prot"] != "unspecified" else "*"
        src_from_port = flt_attr["sFromPort"]
        src_to_port = flt_attr["sToPort"]
        dest_from_port = flt_attr["dFromPort"]
        dest_to_port = flt_attr["dToPort"]

        # If Source From Port or Source To port is unspecified, set value of source to "*"
        if src_from_port == "unspecified" or src_to_port == "unspecified":
            src_str = "*"
        else:
            src_str = src_from_port + "-" + src_to_port
        
        # If Destination From Port or Destination To port is unspecified, set value of destination to "*"
        if dest_from_port == "unspecified" or dest_to_port == "unspecified":
            dest_str = "*"
        else:
            dest_str = dest_from_port + "-" + dest_to_port

        flt_str = ether_type + ":" + protocol + ":" + src_str + " to " +dest_str

        flt_list.append(flt_str)

    
    end_time =  datetime.datetime.now()
    logger.info("Time for getFilterList: " + str(end_time - start_time))
    return flt_list


# This will be called from the UI - after the Mappings are completed
@app.route('/enableView.json')
def enableView(appid, bool):
    try:
        return database_object.enableViewUpdate(appid, bool)
    except Exception as e:
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not enable the view. Error: "+str(e)})


@app.route('/run.json')
def tree(tenantName, appId):
    try:
        
        start_time = datetime.datetime.now()
        logger.info('UI Action TREE started')
        setSleepVar(True)
        aci_local_object = aci_local.ACI_Local(tenantName)
        merged_data = merge_aci_appd(tenantName, appId, aci_local_object)
        #logger.info("Merged data"+str(merged_data))
        response = json.dumps(d3Object.generate_d3_compatible_dict(merged_data))
        return json.dumps({"instanceName":getInstanceName(),"payload": response, "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Error while run.json" + str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the View. Error: "+str(e)})
    finally:
        setSleepVar(False)
        end_time =  datetime.datetime.now()
        logger.info("Time for TREE: " + str(end_time - start_time))


def merge_aci_appd(tenant, appDId, aci_local_object):
    start_time = datetime.datetime.now()
    logger.info('Merging objects for Tenant:'+str(tenant)+', app_id'+str(appDId))
    try:
        # To change to ACI LOCAL
        # aci_local_object = aci_local.ACI_Local(tenant)
        aci_login = aci_local_object.login()
        aci_data = aci_local_object.main()

        # To run anywhere other than on the APIC
        # aci_login = aci_object.apic_login()
        # aci_data = aci_object.main(tenant)
        # aci_object = aci_local.ACI("192.168.130.10", "admin", "Cisco!123")
        # aci_object = aci_local.ACI("10.23.239.23", "admin", "cisco123")
        # aci_data = aci_object.main(tenant)
        # pprint.pprint(aci_data)
        appId = str(appDId) + str(tenant)
        mappings = database_object.returnMapping(appId)
        merge_list = []
        merged_eps = []
        epg_list = []
        total_epg_count = {}
        merged_epg_count = {}
        non_merged_ep_dict = {}
        
        for aci in aci_data:
            if aci['EPG'] not in epg_list:
                epg_list.append(aci['EPG'])
                total_epg_count[aci['EPG']] = 1
            else:
                total_epg_count[aci['EPG']] += 1
            #     epg_count[aci['EPG']] = 1
            if mappings:
                for each in mappings:
                    if aci['IP'] == each['ipaddress'] and each['domainName'] == str(aci['dn']):
                        appd_data = getappD(appDId, aci['IP'])
                        if appd_data:
                            for each in appd_data:
                                each.update(aci)
                                merge_list.append(each)
                                if aci['IP'] not in merged_eps:
                                    merged_eps.append(aci['IP'])
                                    if aci['EPG'] not in merged_epg_count:
                                        merged_epg_count[aci['EPG']] = [aci['IP']]
                                    else:
                                        merged_epg_count[aci['EPG']].append(aci['IP'])
        for aci in aci_data:
            if aci['IP'] not in merged_eps:
                if aci['EPG'] not in non_merged_ep_dict:
                    non_merged_ep_dict[aci['EPG']] = {aci['CEP-Mac']: str(aci['IP'])}
                else:
                    if not non_merged_ep_dict[aci['EPG']]:
                        non_merged_ep_dict[aci['EPG']] = {}
                    if aci['CEP-Mac'] in non_merged_ep_dict[aci['EPG']].keys():
                        multipleips = non_merged_ep_dict[aci['EPG']][aci['CEP-Mac']]+", " + str(aci['IP'])
                        non_merged_ep_dict[aci['EPG']].update({aci['CEP-Mac']: multipleips})
                    else:
                        non_merged_ep_dict[aci['EPG']].update({aci['CEP-Mac']: str(aci['IP'])})
        final_non_merged = {}
        if non_merged_ep_dict:
            for key,value in non_merged_ep_dict.items():
                if not value:
                    continue
                final_non_merged[key] = value
        fractions = {}
        if total_epg_count:
            for epg in total_epg_count.keys():
                #fractions[epg] = str(len(merged_epg_count.get(epg, [])))+"/"+str(total_epg_count.get(epg, []))
                un_map_eps = int(total_epg_count.get(epg, [])) - len(merged_epg_count.get(epg, []))
                fractions[epg] = int(un_map_eps)
                logger.info('Total Unmapped Eps (Inactive):'+str(un_map_eps))
        updated_merged_list = []
        if fractions:
            for key, value in fractions.iteritems():
                for each in merge_list:
                    if key == each['EPG']:
                        each['fraction'] = value
                        each['Non_IPs'] = final_non_merged.get(key, {})
                        updated_merged_list.append(each)
        final_list = []
        for each in updated_merged_list:
            if 'fraction' not in each.keys():
                each['fraction'] = '0'
                each['Non_IPs'] = {}
            final_list.append(each)
        logger.info('Merge complete. Total objects correlated :'+str(len(final_list)))
        return final_list#updated_merged_list#,total_epg_count # TBD for returning values
    except Exception as e:
        logger.exception("Error while merge_aci_data : "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the Merge ACI and AppDynamics objects. Error: "+str(e)})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for merge_aci_appd: " + str(end_time - start_time))


def getappD(appId, ep):
    start_time = datetime.datetime.now()
    try:
        app = database_object.returnApplication('appId', appId)
        tiers = database_object.returnTiers('appId', appId)
        hevs = database_object.returnHealthViolations('appId', appId)
        
        appd_list = []

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
                    if (int(hev.violationId) >= 0):
                        hevList.append(
                            {
                                "Violation Id": (hev.violationId),
                                "Start Time": str(hev.startTime),
                                'Affected Object': str(hev.businessTransaction),
                                'Description': str(hev.description),
                                'Severity': str(hev.severity),
                                'End Time': str(hev.endTime),
                                'Status': str(hev.status),
                                'Evaluation States': hev.evaluationStates["evaluationStates"]
                            }
                        )
                nodes = database_object.returnNodes('tierId', tier.tierId)
                #print "hevList"
                #print hevList
                for node in nodes:
                    if ep in node.ipAddress:
                        appd_list.append({'appId': application.appId, 'appName': str(application.appName), 'appHealth': str(
                            application.appMetrics['data'][0]['severitySummary']['performanceState']),
                                          'tierId': tier.tierId, 'tierName': str(tier.tierName),
                                          'tierHealth': str(tier.tierHealth),
                                          'nodeId': node.nodeId, 'nodeName': str(node.nodeName),
                                        'nodeHealth': str(node.nodeHealth), 'ipAddressList': node.ipAddress,
                                        'serviceEndpoints': sepList, 'tierViolations': hevList})
        return appd_list
    except Exception as e:
        logger.exception("Could not load the View. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the View. Error: "+str(e)})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for getappD: " + str(end_time - start_time))


@app.route('/details.json')  # Will take tenantname and appId as arguments
def get_details(tenant, appId):
    try:
        start_time = datetime.datetime.now()
        #time.sleep(1)
        logger.info("UI Action details.json started")
        
        setSleepVar(True)

        # To run on APIC
        aci_local_object = aci_local.ACI_Local(tenant)
        # To run anywhere other than APIC
        # aci_local_object = aci_local.ACI("192.168.130.10", "admin", "Cisco!123")

        details_list = []
        merged_data = merge_aci_appd(tenant, appId, aci_local_object)
        #getToEpgTraffic("uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord")

        for each in merged_data:
            epg_health = aci_local_object.get_epg_health(str(tenant), str(each['AppProfile']), str(each['EPG']))
            node = get_node_from_interface(each['Interfaces'][0])
            if re.match("/pathep-",each['Interfaces'][0]):
                details_list.append({
                    'IP': each['IP'],
                    'epgName': each['EPG'],
                    'epgHealth': epg_health,
                    'endPointName': each['VM-Name'],
                    'tierName': each['tierName'],
                    'tierHealth': each['tierHealth'],
                    'dn': each['dn'],
                    'mac': each['CEP-Mac'],
                    'interface': each['Interfaces'][0].split("/pathep-")[1][1:-1],
                    'node': node
                })
            else:
                logger.error("pathEp not found.")
                raise Exception("pathEp not found.")

        logger.info("UI Action details.json ended")
        details = [dict(t) for t in set([tuple(d.items()) for d in details_list])]
        return json.dumps({"instanceName":getInstanceName(),"payload": details, "status_code": "200", "message": "OK"})
    except Exception as e:
        logger.exception("Could not load the Details. Error: "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the Details. Error: "+str(e)})
    finally:
        setSleepVar(False)
        end_time =  datetime.datetime.now()
        logger.info("Time for GET_DETAILS: " + str(end_time - start_time))


def get_node_from_interface(interface):
    """This function extracts the node number from interface"""
    if (interface.find("/protpaths") != -1):
        node_number = interface.split("/protpaths-")[1].split("/")[0]
    elif(interface.find("/paths-") != -1):
        node_number = interface.split("/paths-")[1].split("/")[0]
    elif(interface.find("/pathgrp-") != -1):
        node_number = interface.split("/pathgrp-")[1].split("/")[0]
    else:
        try:
            node_number = re.search(r'\/[a-zA-Z]*path[a-zA-Z]*-(.*)',interface)
            if node_number is None:
                raise Exception("interface"+str(interface))
        except Exception as e:
            node_number = '-'
            logger.exception("Exception in get_node_from_interface:"+str(e))

    return node_number

