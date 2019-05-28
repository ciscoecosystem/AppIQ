__author__ = 'nilayshah'
#
import requests
import json, base64
from cobra.model.pol import Uni as PolUni
from cobra.model.aaa import UserEp as AaaUserEp
from cobra.model.aaa import AppUser as AaaAppUser
from cobra.model.aaa import UserCert as AaaUserCert
import logging, pprint
from flask import current_app
#
try:
    from OpenSSL.crypto import FILETYPE_PEM, load_privatekey, sign
except:
    print "=== could not import openssl crypto ==="
#
#
def createCertSession():
    certUser = 'Cisco_TestAppIQ'  # vendor_appname
    pKeyFile = '/home/app/credentials/plugin.key'  # static generated upon install
#
    polUni = PolUni('')
    aaaUserEp = AaaUserEp(polUni)
    aaaAppUser = AaaAppUser(aaaUserEp, certUser)
#
    aaaUserCert = AaaUserCert(aaaAppUser, certUser)
#
    with open(pKeyFile, "r") as file:
        pKey = file.read()
#
    return (aaaUserCert, pKey)
#
#
class ACI_Local(object):
    def __init__(self, tenant):
        self.apic_ip = '172.17.0.1'
        self.logger = logging.getLogger('Tenant:'+str(tenant))
        self.tenant = tenant
        self.proto = 'https://'
        self.apic_token = self.login()
        if not self.apic_token:
            current_app.logger.info('Connection to APIC failed. Trying http instead...')
            self.proto = 'http://'
            self.apic_token = self.login()
        if self.apic_token:
            self.ep_url = self.proto + self.apic_ip + '/api/class/fvCEp.json'
            self.ip_url =  self.proto + self.apic_ip + '/api/class/fvIp.json'
            self.epg_url =  self.proto + self.apic_ip + '/api/class/fvAEPg.json'
            self.ep_url =  self.proto + self.apic_ip + '/api/class/fvCEp.json'
        else:

            current_app.logger.info('Could not connect to APIC. Please verify your APIC connection.')
        # self.apic_token = self.apic_login()
        #self.apic_token = self.login()
#
    # apic_ip = "172.17.0.1"
    def login(self):
        global auth_token
        global session
        global user1
        global pwd1
        global external_apic_ip
#
        user_cert, p_key_str = createCertSession()
        session = requests.session()
        uri = "/api/requestAppToken.json"
        app_token_payload = {"aaaAppToken": {"attributes": {"appName": "Cisco_TestAppIQ"}}}
        data = json.dumps(app_token_payload)
        payLoad = "POST" + uri + data
        p_key = load_privatekey(FILETYPE_PEM, p_key_str)
        signedDigest = sign(p_key, payLoad.encode(), 'sha256')
        signature = base64.b64encode(signedDigest).decode()
        user_cert_str = str(user_cert.dn)
#
        token = "APIC-Request-Signature=" + signature + ";"
        token += "APIC-Certificate-Algorithm=v1.0;"
        token += "APIC-Certificate-Fingerprint=fingerprint;"
        token += "APIC-Certificate-DN=" + user_cert_str
        try:
            r = session.post(self.proto + self.apic_ip+"/api/requestAppToken.json", data=data, headers={'Cookie': token},timeout=10, verify=False)
            if r.status_code == 200 or r.status_code == 201:
                auth = json.loads(r.text)
                #print auth['imdata'][0]
                auth_token = auth['imdata'][0]['aaaLogin']['attributes']['token']
                #self.logger.info(auth_token)
                #current_app.logger.info('Auth token generated for APIC')
                return auth_token
            else:
                return None
        except:
            current_app.logger.info('Could not communicate with APIC')
            return None

    def ACI_get(self, url,cookie=None):
        try:
            response = requests.get(url,cookies=cookie, verify=False)
            #current_app.logger.info('API call for APIC: '+str(url))
            if response.status_code == 200 or response.status_code == 201:
                current_app.logger.info('API call success: '+str(url))
                return response
            else:
                apic_token = self.login()
                response = requests.get(url,cookies={'APIC-Cookie': apic_token}, verify=False)
                if response.status_code == 200 or response.status_code == 201:
                    current_app.logger.info('API call success: '+str(url))
                    return response
        except Exception as e:
            current_app.logger.info('ACI call Exception:'+str(e)+', URL:'+str(url))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: Could not connect to APIC database. Error: "+str(e)})


    def get_mo_related_item(self, mo_dn, item_query_string, item_type):
        try:
            if item_type == "":
                mo_related_item_url = self.proto + self.apic_ip + "/api/node/mo/" + mo_dn + ".json?" + item_query_string
            elif item_type == "HealthRecords":
                mo_related_item_url = self.proto + self.apic_ip + "/api/node/class/healthRecord.json?query-target-filter=eq(healthRecord.affected,\"" + mo_dn + "\")"
            elif item_type == "ifConnRecords":
                mo_related_item_url = self.proto + self.apic_ip + "/api/node/mo/uni/epp/fv-[" + mo_dn + "].json?" + item_query_string
            
            mo_related_item_resp = self.ACI_get(mo_related_item_url, cookie = {'APIC-Cookie': self.apic_token})
            mo_related_item_list = ((json.loads(mo_related_item_resp.text)['imdata']))
            return mo_related_item_list
            # return {"status": True, "payload": mo_related_item_list}
        except Exception as ex:
            current_app.logger.info('Exception while fetching EPG item with query string: ' + item_query_string + ',\nError:' + str(ex))
            current_app.logger.info('Epg Item Url : =>' + mo_related_item_url)
            return []
            # return {"status": False, "payload": []}

    def get_all_mo_instances(self, mo_class):
        try:
            mo_url = self.proto + self.apic_ip + "/api/node/class/" + mo_class + ".json"
            mo_resp = self.ACI_get(mo_url, cookie = {'APIC-Cookie': self.apic_token})
            mo_instance_list = ((json.loads(mo_resp.text)['imdata']))
            return {"status": True, "payload": mo_instance_list}
        except Exception as ex:
            current_app.logger.info('Exception while fetching MO: ' + mo_class + ', Error:' + str(ex))
            return {"status": False, "payload": []}

    def get_epg_health(self,tenant,app_profile,epg_name,apic_token=None):
        try:
            epg_health_url = self.proto+self.apic_ip +"/api/node/mo/uni/tn-"+str(tenant)+"/ap-"+app_profile+"/epg-"+epg_name+".json?rsp-subtree-include=health,no-scoped"
            # epg_heath = requests.get(epg_health_url, cookies={'APIC-Cookie': apic_token}, verify=False)
            epg_health = self.ACI_get(epg_health_url,cookie={'APIC-Cookie': apic_token})
            health = ((json.loads(epg_health.text)['imdata']))
            for each in health:
                for key,value in each.iteritems():
                    if str(key) == 'healthInst':
                        return value['attributes']['cur']
        except Exception as e:
            current_app.logger.info('Exception in EPG health API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve EPG Health. Error: "+str(e)})


    def apic_fetchEPData(self, tenant,apic_token=None):
        try:
            # ep_url = "https://"+self.apic+"/api/class/fvCEp.json?query-target-filter=wcard(fvCEp.dn,"AppDynamics/")"
            url = self.ip_url + '?query-target-filter=wcard(fvIp.dn,"' + str(tenant) + '/")'
            # ep_response = requests.get(url, cookies={'APIC-Cookie': apic_token}, verify=False)
            ep_response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            if json.loads(ep_response.text)['imdata']:
                current_app.logger.info('Total EPs fetched for Tenant: '+str(tenant)+' - '+str(len(json.loads(ep_response.text)['imdata']))+ 'EPs')
                return json.loads(ep_response.text)['imdata']
            else:
                return []
        except Exception as e:
            current_app.logger.info('Exception in EP/IP Data API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve EP data. Error: "+str(e)})

#
#
    def apic_fetchEPGData(self, tenant,apic_token=None):
        try:
            url = self.epg_url + '?query-target-filter=wcard(fvCEp.dn,"tn-' + str(
                tenant) + '/")&query-target=children&target-subtree-class=fvCEp&rsp-subtree=children&rsp-subtree-class=fvRsToVm,fvRsCEpToPathEp,fvIp'
            #epg_response = requests.get(url, cookies={'APIC-Cookie': apic_token}, verify=False)
            epg_response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            if json.loads(epg_response.text)['imdata']:
                current_app.logger.info('Total EPGs fetched for Tenant: '+str(tenant)+' - '+str(len(json.loads(epg_response.text)['imdata']))+ 'EPGs')
                return json.loads(epg_response.text)['imdata']
            else:
                return []
        except Exception as e:
            current_app.logger.info('Exception in EPG Data API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve EPG data. Error: "+str(e)})

#
    def apic_fetchBD(self, dn,apic_token=None):
        try:
            # apic_token = self.login()
            url = self.proto + self.apic_ip + '/api/node/mo/' + dn + '.json?query-target=children&target-subtree-class=fvRsBd'
            # bd_response = requests.get(url, cookies={'APIC-Cookie': apic_token})
            bd_response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            if json.loads(bd_response.text)['imdata']:
                bd_data = (json.loads(bd_response.text)['imdata'])[0]['fvRsBd']['attributes']['tnFvBDName']
                #current_app.logger.info('BDs fetched!')
                return bd_data
            else:
                return ""
        except Exception as e:
            current_app.logger.info('Exception in BD API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could retrieve BD data. Error: "+str(e)})

#
    def apic_fetchVRF(self,dn,apic_token=None):
        try:
            # apic_token = self.login()
            # url: https://192.168.130.10/api/node/mo/uni/tn-AppDynamics/BD-AppD-bd1.json?query-target=children&target-subtree-class=fvRsCtx&subscription=yes
            url = self.proto + self.apic_ip + '/api/node/mo/' + dn + '.json?query-target=children&target-subtree-class=fvRsCtx'
            # vrf_response = requests.get(url, cookies={'APIC-Cookie': apic_token})
            vrf_response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            if json.loads(vrf_response.text)['imdata']:
                vrf_data = (json.loads(vrf_response.text)['imdata'])[0]['fvRsCtx']['attributes']['tnFvCtxName']
                #current_app.logger.info('VRFs fetched!')
                return vrf_data
            else:
                return ""
        except Exception as e:
            current_app.logger.info('Exception in VRF API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve VRF data. Error: "+str(e)})

#
#
    def extractCtxName(self, dn):
        splitdn = dn.split("/", 4)[4].split("-")[1]
        return splitdn
#
    def apic_fetchContract(self, dn,apic_token=None):
        try:
            url = self.proto + self.apic_ip + '/api/node/mo/' + dn + '.json?query-target=children&target-subtree-class=fvRsCons,fvRsProv,fvRsConsIf,fvRsProtBy,fvRsConsIf'
            # bd_response = requests.get(url, cookies={'APIC-Cookie': apic_token})
            bd_response = self.ACI_get(url,cookie={'APIC-Cookie': apic_token})
            contract_list = []
            if json.loads(bd_response.text)['imdata']:
                #current_app.logger.info('Contracts fetched!')
                ctx = json.loads(bd_response.text)['imdata']
            else:
                ctx = {}
            for child in ctx:
                if str(child.keys()[0]) == 'fvRsCons':
                    ct_name = str(self.extractCtxName(child['fvRsCons']['attributes']['dn']))
                    contract_list.append({'Consumer': ct_name})

                if str(child.keys()[0]) == 'fvRsIntraEpg':
                    ct_name = str(self.extractCtxName(child['fvRsIntraEpg']['attributes']['dn']))
                    contract_list.append({'IntraEpg': ct_name})

                if str(child.keys()[0]) == 'fvRsProv':
                    ct_name = str(self.extractCtxName(child['fvRsProv']['attributes']['dn']))
                    contract_list.append({'Provider': ct_name})

                if str(child.keys()[0]) == 'fvRsConsIf':
                    ct_name = str(self.extractCtxName(child['fvRsConsIf']['attributes']['dn']))
                    contract_list.append({'Consumer Interface': ct_name})

                if str(child.keys()[0]) == 'fvRsProtBy':
                    ct_name = str(self.extractCtxName(child['fvRsProtBy']['attributes']['dn']))
                    contract_list.append({'Taboo': ct_name})
            return contract_list
        except Exception as e:
            current_app.logger.info('Exception in Contracts API call, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve Contracts. Error: "+str(e)})


    # Reads dn, ip and tenant for an fvIp and returns a list of those dictionaries
    def parseEPsforTemp(self, data, tenant):
        resp = []
        for each in data:
            val = {'dn': str(each['fvIp']['attributes']['dn']), 'IP': str(each['fvIp']['attributes']['addr']),
                   'tenant': str(tenant)}
            resp.append(val)
        return resp


    def apic_parseData(self, ep_resp,apic_token=None):
        try:
            current_app.logger.info('Parsing APIC Data!')
            ep_list = []
            
            current_app.logger.info("")

            for ep in ep_resp:
                #current_app.logger.info('EP Name:'+str(ep['fvCEp']['attributes']['name']))
                ep_attr = ep['fvCEp']['attributes']
                fviplist = []
                for eachip in ep['fvCEp']['children']:
                    if eachip.keys()[0] == 'fvIp':
                        fviplist.append(str(eachip['fvIp']['attributes']['addr']))
                #print fviplist
                for ip in fviplist:
                    
                    # ep_dict = {'Tenant': '', "AppProfile": '', 'EPG': '', 'CEP-Mac': '', 'IP': ''}
                    ep_dict = {"AppProfile": '', 'EPG': '', 'CEP-Mac': '', 'IP': '', 'Interfaces': [], 'VM-Name': '', 'BD': '',
                           'VMM-Domain': '', 'Contracts': [], 'VRF':'','dn': '/'.join((ep_attr['dn'].split('/', 4)[0:4]))}

                    string = str(ep_attr['dn'])
                    bdString = string.split("/", 5)

                    newbdString = bdString[0] + '/' + bdString[1] + '/' + bdString[2] + '/' + bdString[3]
                    bd_data = self.apic_fetchBD(newbdString,apic_token=apic_token)
                    newvrfString = bdString[0] + '/' + bdString[1] + '/BD-' + bd_data
                    vrf_data = self.apic_fetchVRF(newvrfString,apic_token=apic_token)
                    vrf_name =  bdString[1].split('-')[1] + "/" + vrf_data
                    ct_data_list = self.apic_fetchContract(newbdString,apic_token=apic_token)
                    ep_dict.update({'VRF': str(vrf_name)})
                    ep_dict.update({'Contracts': ct_data_list})
                    ep_dict.update({'BD': str(bd_data)})
                    splitString = string.split("/")
                    ep_dict.update({"IP": str(ip)})
                    for eachSplit in splitString:
                        if "-" in eachSplit:
                            epSplit = eachSplit.split("-", 1)
                            if epSplit[0] == "ap":
                                ep_dict.update({"AppProfile": str(epSplit[1])})
                            if epSplit[0] == "epg":
                                ep_dict.update({"EPG": str(epSplit[1])})
                            if epSplit[0] == "cep":
                                ep_dict.update({"CEP-Mac": str(epSplit[1])})
                    # ep_dict.update({'IP': str(ep_attr['ip'])})
                    ep_child_attr = ep['fvCEp']['children']
                    path_list = []
                    for child in ep_child_attr:
                        if str(child.keys()[0]) == 'fvRsCEpToPathEp':
                            path_list.append(str(child['fvRsCEpToPathEp']['attributes']['tDn']))
                        if str(child.keys()[0]) == 'fvRsToVm':
                            tDn_dom = str(child['fvRsToVm']['attributes']['tDn'])
                            
                            vmmDom = str(tDn_dom.split("ctrlr-[")[1].split(']-')[0])
                            
                            # vmmDom = str(tDn_dom.split("/")[1].split("-")[1]) + "/" + str(tDn_dom.split("/")[2].split("-")[2])
                            ep_dict.update({'VMM-Domain': vmmDom})
                            tDn = str(child['fvRsToVm']['attributes']['tDn'])
                            vm_url = self.proto + self.apic_ip + '/api/mo/' + tDn + '.json'
                            # vm_response = requests.get(vm_url, cookies={'APIC-Cookie': token})
                            vm_response = self.ACI_get(vm_url,cookie={'APIC-Cookie': apic_token})

                            vm_name = json.loads(vm_response.text)['imdata'][0]['compVm']['attributes']['name']

                            if not vm_name:
                                vm_name = 'EP-'+str(ep['fvCEp']['attributes']['name'])
                            ep_dict.update({'VM-Name': str(vm_name)})
                        else:
                            ep_dict.update({'VMM-Domain':'None'})
                            ep_dict.update({'VM-Name':'EP-'+str(ep['fvCEp']['attributes']['name'])})
                        ep_dict.update({'Interfaces': path_list})
                    #current_app.logger.info('EP Dict:')
                    #current_app.logger.info(ep_dict)
                    ep_list.append(ep_dict)
            return ep_list
        except Exception as e:
            current_app.logger.info('Exeption in ACI Parsing Data, Error: '+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not parse APIC data. Error: "+str(e)})


    def main(self):
        try:
            auth_token = self.login()
            current_app.logger.info('APIC Login success!')
            # ep_data = self.apic_fetchEPData(auth_token,self.tenant)
            # ep_data = self.apic_fetchEPData(self.tenant,apic_token=auth_token)
            epg_data = self.apic_fetchEPGData(self.tenant,apic_token=auth_token)
            #current_app.logger.info('EPG data in main:'+str(epg_data))
            parse_data = self.apic_parseData(epg_data,apic_token=auth_token)
            #current_app.logger.info('Parse data in main'+str(parse_data))
            return parse_data
        except Exception as e:
            current_app.logger.info('Exception in ACI Local Main, Error:'+str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not retrieve ACI objects. Error: "+str(e)})




# ==============================================================================================================================
#         # cookies = {}
#         # cookies['APIC-Cookie'] = auth_token
#     # uses REST API to subscribe to tenants
#         tenant_url = 'https://' + self.apic_ip + '/api//class/fvCEp.json?query-target-filter=wcard(fvCEp.dn,"' + str(
#         self.tenant) + '")'
#         tenant_response = requests.get(tenant_url, cookies=cookies, verify=False)
#         ep_resp = json.loads(tenant_response.text)['imdata']
#         ep_list = []
#         for ep in ep_resp:
#             ep_attr = ep['fvCEp']['attributes']
#             # ep_dict = {'Tenant': '', "AppProfile": '', 'EPG': '', 'CEP-Mac': '', 'IP': ''}
#             ep_dict = {"AppProfile": '', 'EPG': '', 'CEP-Mac': '', 'IP': ''}
#             string = str(ep_attr['dn'])
#             splitString = string.split("/")
#             for eachSplit in splitString:
#                 if "-" in eachSplit:
#                     epSplit = eachSplit.split("-", 1)
#                     # if epSplit[0] == "tn":
#                     #     ep_dict.update({"Tenant": str(epSplit[1])})
#                     if epSplit[0] == "ap":
#                         ep_dict.update({"AppProfile": str(epSplit[1])})
#                     if epSplit[0] == "epg":
#                         ep_dict.update({"EPG": str(epSplit[1])})
#                     if epSplit[0] == "cep":
#                         ep_dict.update({"CEP-Mac": str(epSplit[1])})
#             ep_dict.update({'IP': str(ep_attr['ip'])})
#             ep_list.append(ep_dict)
#         return ep_list
#


