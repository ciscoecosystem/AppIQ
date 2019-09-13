__author__ = 'nilayshah'
#import ACI_Info as ACI_EPs
import AppD_Alchemy as database
import json, pprint
# import ACI_Info as aci_local
import ACI_Local as aci_local
db_object = database.Database()
from flask import current_app
# aci_object = ACI_EPs.ACI('192.168.130.10', 'admin', 'Cisco!123')  # Change it later to ACI_Local
from custom_logger import CustomLogger

logger = CustomLogger.get_logger("/home/app/log/app.log")

class Recommend(object):

    # Matches the IP of ACI fvIp with AppD Node IPs and returns a list of matched ACI fvIps dicts
    def getCommonEPs(self, appd_ip_list, aci_parsed_eps):
        common_list = []
        for each in aci_parsed_eps:
            if each['IP'] in appd_ip_list:
                common_list.append(each)
        return common_list

    def extract(self,dn):
        ap = dn.split('/')[2].split('-',1)[1]
        epg = dn.split('/')[3].split('-',1)[1]
        return ap,epg

    # count_dict Example
    # count_dict = 
    # {
    #     "ap1": {
    #         "epg11":2,
    #         "epg12":3
    #     },
    #     "ap2": {
    #         "epg21":3,
    #         "epg22":1
    #     }
    # }
    def extract_ap_and_epgs(self,eps):
        count_dict = {}
        for ep in eps:
            ap,epg = self.extract(ep['dn'])
            if ap not in count_dict.keys():
                count_dict[ap] = {epg:1}
            elif epg not in count_dict[ap].keys():
                count_dict[ap][epg] = 1
            else:# epg in count_dict[ap].keys():
                count_dict[ap][epg] += 1
        return count_dict

    # returns a list of list
    def determine_recommendation(self,extract_ap_epgs,common_eps):
        ip2_list = []
        for each in common_eps:
            accounted = 0
            for duplicate in common_eps:
                # For different elements, if IP is same and 'dn' is different
                if each['IP'] == duplicate['IP'] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate):
                    ap_main,epg_main = self.extract(each['dn'])
                    ap_dup,epg_dup = self.extract(duplicate['dn'])
                    
                    # Compare count of 'EPG' for an 'AP'
                    main_count = extract_ap_epgs[ap_main][epg_main]
                    dup_count = extract_ap_epgs[ap_dup][epg_dup]
                    
                    if main_count > dup_count:
                        ip2_list.append([each['IP'],each['dn'],'Yes'])
                        break
                    elif main_count == dup_count:
                        ap_main_c = len(extract_ap_epgs[ap_main])
                        ap_dup_c = len(extract_ap_epgs[ap_dup])
                        # Add one with more number of Epgs
                        if ap_main_c > ap_dup_c:
                            ip2_list.append([each['IP'],each['dn'],'Yes'])
                            break
                        elif ap_main_c < ap_dup_c:
                            ip2_list.append([each['IP'],each['dn'],'No'])
                            break
                        else:
                            ip2_list.append([each['IP'],each['dn'],'None'])
                    else:
                        ip2_list.append([each['IP'],each['dn'],'No'])
                elif each['IP'] != duplicate['IP'] and common_eps.index(each) != common_eps.index(duplicate) and each['dn'] != duplicate['dn'] and any(each['IP'] in d for d in ip2_list) != True:
                    ip2_list.append([each['IP'],each['dn'],'None'])
                elif accounted == 0:
                    ip2_list.append([each['IP'],each['dn'],'None'])
                    accounted = 1

        for a in ip2_list:
            for b in ip2_list:
                if a[0] == b[0] and a[1] == b[1] and (a[2] == 'Yes' or a[2] == 'No') and b[2] == 'None':
                    ip2_list.remove(b)
        return ip2_list

    # Sample Return Value
    # [
    #     {
    #         "ipaddress": "1.1.1.1",
    #         "domains": [
    #             {
    #                 "domainName": "dn of epg1",
    #                 "recommended": True
    #             },
    #             {
    #                 "domainName": "dn of epg2",
    #                 "recommended": False
    #             }
    #         ]
    #     },
    #     {
    #         "ipaddress": "2.2.2.2",
    #         "domains": [
    #             {
    #                 "domainName": "dn of epg3",
    #                 "recommended": True
    #             },
    #             {
    #                 "domainName": "dn of epg4",
    #                 "recommended": False
    #             }
    #         ]
    #     }
    # ]
    def generatelist(self,ipList):
        src_clus_list = []
        ips = []
        for each in ipList:
            ips.append(each[0])
        ips = list(set(ips))
        new_dict = dict((el,[]) for el in ips)
        for each in ipList:
            if each[2] == 'No':
                each[2] = False
            if each[2] == 'Yes' or each[2] == 'None':
                each[2] = True
            new_dict[each[0]].append({'domainName':each[1],'recommended':each[2]})
        for key,value in new_dict.iteritems():
            entry = {'ipaddress':key,'domains':value}
            src_clus_list.append(entry)

        return src_clus_list



    def correlate_ACI_AppD(self, tenant, appId):
        logger.info('Finding Correlations for ACI and AppD')
        appd_ips = list(set(db_object.ipsforapp(appId)))
        logger.info('AppD IPs: '+str(appd_ips))
        ip_list = []
        if not appd_ips:
            return []
        for each in appd_ips:
            ip_list += each.ipAddress
        # aci_local_object = aci_local.ACI('10.23.239.23','admin','cisco123')
        # aci_local_object = aci_local.ACI('192.168.130.10','admin','Cisco!123')
        aci_local_object = aci_local.ACI_Local(tenant)
        end_points = aci_local_object.apic_fetchEPData(tenant)
        if not end_points:
            return []
        #logger.info('ACI EPs found:'+str(end_points))
        try:
            parsed_eps = aci_local_object.parseEPsforTemp(end_points,tenant)
        except Exception as e:
            logger.exception('Exception in parsed eps list, Error:'+str(e))
            return []
        # end_points = aci_object.apic_fetchEPData(tenant)
        # parsed_eps = aci_object.parseEPsforTemp(end_points, tenant)
        
        # "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test/cep-00:50:56:92:BA:4A/ip-[20.20.20.10]"
        if not parsed_eps:
            return []
        for each in parsed_eps:
            splitdn = '/'.join(each['dn'].split('/',4)[0:4])
            # Example of extracted Epg dn
            # uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test
            each['dn'] = splitdn
        try:
            common_eps = self.getCommonEPs(ip_list, parsed_eps)
            logger.info('Common EPs:'+str(common_eps))
        except Exception as e:
            logger.exception('Exception in common eps list, Error:'+str(e))
            return []

        if common_eps:
            extract_ap_epgs = self.extract_ap_and_epgs(common_eps)
        else:
            return []
        try:
            rec_list = self.determine_recommendation(extract_ap_epgs,common_eps)
        except Exception as e:
            logger.exception('Exception in rec list, Error:'+str(e))
            return []
        if rec_list:
            logger.info('Recommendation list for app:'+str(appId)+'  rec_list= '+str(rec_list))
            fin_list = set(map(tuple,rec_list))
            final_list = map(list,fin_list)
        else:
            return []
        try:
            generated_list = self.generatelist(final_list)
        except Exception as e:
            logger.exception('Exception in generate list, Error:'+str(e))
            return []
        if generated_list:
            logger.info('Generated List = '+str(generated_list))
            return generated_list
        else:
            return []


# rec = Recommend()
# pprint.pprint(rec.correlate_ACI_AppD('AppDControllerTenant', 7))

