import requests
import datetime
import aci_utils
import json
from custom_logger import CustomLogger

logger = CustomLogger.get_logger("/home/app/log/app.log")


def merge_aci_consul(tenant, data_center, aci_util_obj):
    """
    Initial algo implementaion.

    Merge ACI data with Consul Data fetched from API directly
    """

    start_time = datetime.datetime.now()
    logger.info('Merging objects for Tenant:'+str(tenant)+', data_centre'+str(data_center)) # change appdid

    try:
        merge_list = []  # TODO: these should go above 946
        merged_eps = []
        total_epg_count = {}
        merged_epg_count = {}
        non_merged_ep_dict = {}

        aci_data = aci_util_obj.main(tenant)
        # mapping should come from alchemy
        # correlatoin should be part of mapping
        aci_consul_mappings = correlate_aci_consul(tenant, data_center)

        # Changing the data from the correlate_aci_consul(tenant, data_centre)
        aci_consul_mappings = get_mapping_dict_target_cluster(aci_consul_mappings)


        logger.debug("ACI Data: {}".format(str(aci_data)))
        logger.debug("Mapping Data: {}".format(str(aci_consul_mappings)))

        for aci in aci_data:
            if aci['EPG'] not in total_epg_count.keys():
                total_epg_count[aci['EPG']] = 1
            else:
                total_epg_count[aci['EPG']] += 1

            if aci_consul_mappings:
                mappings = [node for node in aci_consul_mappings if node.get('disabled') == False]
                for each in mappings:
                    mapping_key = 'ipaddress'
                    aci_key = 'IP'

                    if aci.get(aci_key) and each.get(mapping_key) and aci.get(aci_key).upper() == each.get(mapping_key).upper() and each['domainName'] == str(aci['dn']):
                        # Change based on IP and Mac
                        consul_data = get_consul_data(aci.get(aci_key).upper())
                        if consul_data:
                            for each in consul_data:
                                each.update(aci)
                                merge_list.append(each)
                                if aci[aci_key] not in merged_eps:
                                    merged_eps.append(aci[aci_key])
                                    if aci['EPG'] not in merged_epg_count:
                                        merged_epg_count[aci['EPG']] = [aci[aci_key]]
                                    else:
                                        merged_epg_count[aci['EPG']].append(aci[aci_key])

        for aci in aci_data:
            if aci['IP'] in merged_eps:
                continue
            else:
                if aci['EPG'] not in non_merged_ep_dict:
                    non_merged_ep_dict[aci['EPG']] = {aci['CEP-Mac']: str(aci['IP'])}
                
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
                logger.info('Total Unmapped Eps (Inactive):'+str(un_map_eps)+" - "+str(epg))

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
        logger.info('Merge complete. Total objects correlated: ' + str(len(final_list)))

        return final_list #updated_merged_list#,total_epg_count # TBD for returning values
    except Exception as e:
        logger.exception("Error while merge_aci_data : "+str(e))
        return json.dumps({"payload": {}, "status_code": "300", "message": "Could not load the Merge ACI and AppDynamics objects."})
    finally:
        end_time =  datetime.datetime.now()
        logger.info("Time for merge_aci_appd: " + str(end_time - start_time))


def get_consul_data(ep):
    """
    This will fetch the data from the API and return for now
    Decide the form of data neede in the merge logic and return as per that.
    """
    try:
        consul_data = []

        list_of_nodes = consul_node_list() # here data should come from db

        for node in list_of_nodes:
            if ep in node.get('NodesIPs'):
                consul_data.append({
                    'nodeId': node.get('NodeID'),
                    'nodeName': node.get('NodeName'),
                    'ipAddressList': node.get('NodesIPs'),
                    'services': consul_nodes_services(node.get('NodeName'))
                })
        return consul_data
    except Exception as e:
        logger.exception("Error while merge_aci_data : "+str(e))
        return []



def get_mapping_dict_target_cluster(mapped_objects):
    """
    return mapping dict from recommended objects
    """
    target = []
    for map_object in mapped_objects:
        for entry in map_object.get('domains'):
            if entry.get('recommended') == True:
                logger.debug("Mapping found with ipaddress for "+str(map_object))
                target.append({'domainName': entry.get('domainName'), 'ipaddress': map_object.get('ipaddress'), 'disabled': False})
    return target


def correlate_aci_consul(tenant, data_center):
    """
    Initial algo imp

    This shoild go in the recommandation and not be called in mapping instead
    """
    logger.info('Finding Correlations for ACI and AppD')

    aci_util_obj = aci_utils.ACI_Utils()
    end_points = aci_util_obj.apic_fetchEPData(tenant)
    if not end_points:
        logger.error('Error: Empty end_points ' + str(end_points))
        return []

    try:
        # returns dn, ip and tenant info for each ep
        parsed_eps = aci_util_obj.parseEPs(end_points,tenant)
        if not parsed_eps:
            logger.error('Error: Empty parsed_eps ' + str(parsed_eps))
            return []
        else:
            # Example of each EP dn
            # "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test/cep-00:50:56:92:BA:4A/ip-[20.20.20.10]"
            # Example of extracted Epg dn
            # "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-test"
            for each in parsed_eps:
                each['dn'] = '/'.join(each['dn'].split('/',4)[0:4])
    except Exception as e:
        logger.exception('Exception in parsed eps list, Error: ' + str(e))
        return []

    # Get All the nodes in the data centre
    consul_nodes = get_data_centre_nodes(data_center)
    logger.info('Consul IPs: '+str(consul_nodes))
    if not consul_nodes:
        logger.exception('Error: appd_nodes is Empty!')
        return []

    ip_list = []
    for node in consul_nodes:
        ip_list.append(node)

    logger.debug('Final IP List ' + str(ip_list))

    # Extract common based on Ips
    try:
        common_eps = getCommonEPs(ip_list, parsed_eps)
        logger.debug('Common EPs:'+str(common_eps))
        if common_eps:
            extract_ap_epgs = extract_ap_and_epgs(common_eps)
        else:
            return []
    except Exception as e:
        logger.exception('Exception in common eps list, Error:'+str(e))
        return []

    try:
        rec_list = determine_recommendation(extract_ap_epgs,common_eps)
    except Exception as e:
        logger.exception('Exception while determining recommended list, Error:'+str(e))
        return []

    if rec_list:
        logger.info('Recommendation list for app:'+str(data_center)+'  rec_list= '+str(rec_list))
        fin_list = set(map(tuple,rec_list))
        final_list = map(list,fin_list)
        logger.info('Final List final_list '+str(rec_list))
    else:
        logger.info('Error: Empty rec_list ' + str(rec_list))
        return []
    
    try:
        generated_list = generatelist(final_list)
    except Exception as e:
        logger.exception('Exception in generate list, Error:'+str(e))
        return []
    
    if generated_list:
        logger.info('Generated List = '+str(generated_list))
        return generated_list
    else:
        logger.info('Error: Empty generated_list ' + str(generated_list))
        return []


def get_data_centre_nodes(data_center):
    """
    This should fetch the data from db using the dc field, not directly
    """
    
    ip_list = []
    try:
        catalog_nodes = requests.get('{}/v1/catalog/nodes'.format('http://10.23.239.14:8500'))
        nodes = json.loads(catalog_nodes.content)
        # print(nodes)
        for node in nodes:
            ip_list.append(node.get('Address', ''))
            if node.get('TaggedAddresses', {}):
                ip_list.append(node.get('TaggedAddresses', {}).get('wan_ipv4', ''))
                ip_list.append(node.get('TaggedAddresses', {}).get('wan', ''))
                ip_list.append(node.get('TaggedAddresses', {}).get('lan', ''))
                ip_list.append(node.get('TaggedAddresses', {}).get('lan_ipv4', ''))
    except Exception as e:
        print('Error ' + str(e))
    
    ip_list = [x for x in ip_list if x]
    return list(set(ip_list))


def getCommonEPs(consul_ip_list, aci_parsed_eps):
    """Map EP(ACI) to Nodes(Consul)
    
    Matches the IP of ACI fvIp with Consul Node IPs and returns a list of matched ACI fvIps dicts"""
    
    common_list = []
    for each in aci_parsed_eps:
        if each['IP'] in consul_ip_list:
            common_list.append(each)
    return common_list


def extract_ap_and_epgs(eps):
    count_dict = {}
    for ep in eps:
        ap, epg = extract(ep['dn'])
        if ap not in count_dict.keys():
            count_dict[ap] = {epg:1}
        elif epg not in count_dict[ap].keys():
            count_dict[ap][epg] = 1
        else:
            count_dict[ap][epg] += 1
    return count_dict


def extract(dn):
    """
    Extract ap and epg from given dn
    """
    ap = dn.split('/')[2].split('-',1)[1]
    epg = dn.split('/')[3].split('-',1)[1]
    return ap, epg


# returns a list of list
def determine_recommendation(extract_ap_epgs, common_eps):
    recommendation_list = []
    for each in common_eps:
        accounted = 0
        for duplicate in common_eps:

            # For different elements, if IP/Mac is same and 'dn' is different
            if each['IP'] == duplicate['IP'] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate):
                ap_main,epg_main = extract(each['dn'])
                ap_dup,epg_dup = extract(duplicate['dn'])
                
                # Compare count of 'EPG' for an 'AP'
                main_count = extract_ap_epgs[ap_main][epg_main]
                dup_count = extract_ap_epgs[ap_dup][epg_dup]
                
                if main_count > dup_count:
                    recommendation_list.append([each['IP'],each['dn'],'Yes','IP'])
                    break
                elif main_count == dup_count:
                    ap_main_c = len(extract_ap_epgs[ap_main])
                    ap_dup_c = len(extract_ap_epgs[ap_dup])
                    # Add one with more number of Epgs
                    if ap_main_c > ap_dup_c:
                        recommendation_list.append([each['IP'],each['dn'],'Yes','IP'])
                        break
                    elif ap_main_c < ap_dup_c:
                        recommendation_list.append([each['IP'],each['dn'],'No','IP'])
                        break
                    else:
                        recommendation_list.append([each['IP'],each['dn'],'None','IP'])
                else:
                    recommendation_list.append([each['IP'],each['dn'],'No','IP'])
            elif each['IP'] != duplicate['IP'] and each['dn'] != duplicate['dn'] and common_eps.index(each) != common_eps.index(duplicate) and any(each['IP'] in d for d in recommendation_list) != True:
                recommendation_list.append([each['IP'],each['dn'],'None','IP'])
            elif accounted == 0:
                recommendation_list.append([each['IP'],each['dn'],'None','IP'])
                accounted = 1

    for a in recommendation_list:
        for b in recommendation_list:
            # If same recommendation already exist with b[2] == 'None' than remove it.
            if a[0] == b[0] and a[1] == b[1] and (a[2] == 'Yes' or a[2] == 'No') and b[2] == 'None':
                recommendation_list.remove(b)
    return recommendation_list


def generatelist(ipList):
    """
    Generate list based on the IP or Mac.
    """
    src_clus_list = []
    # logger.info("ip_list" + type + ipList)
    ips = list(set([x[0] for x in ipList]))
    ip_dict = dict((el,[]) for el in ips)
    for each in ipList:
        if each[2] == 'No':
            each[2] = False
        if each[2] == 'Yes' or each[2] == 'None':
            each[2] = True

        ip_dict[each[0]].append({'domainName':each[1],'recommended':each[2]})

    for key,value in ip_dict.iteritems():
        src_clus_list.append({'ipaddress':key,'domains':value})

    return src_clus_list


def consul_node_list():
    """
    This should fetch the data from db using the dc field, not directly
    
    For now fetching nodes and returning [{name: '', iplist: []},..]
    """
    
    node_list = []
    try:
        catalog_nodes = requests.get('{}/v1/catalog/nodes'.format('http://10.23.239.14:8500'))
        nodes = json.loads(catalog_nodes.content)
        logger.debug(str(nodes))
        for node in nodes:
            ip_list = []
            ip_list.append(node.get('Address', ''))
            if node.get('TaggedAddresses', {}):
                ip_list.append(node.get('TaggedAddresses', {}).get('wan_ipv4', ''))
                ip_list.append(node.get('TaggedAddresses', {}).get('wan', ''))
                ip_list.append(node.get('TaggedAddresses', {}).get('lan', ''))
                ip_list.append(node.get('TaggedAddresses', {}).get('lan_ipv4', ''))

            node_list.append({
                'NodeID': node.get('ID', ''),
                'NodeName': node.get('Node', ''),
                'NodesIPs': list(set(ip_list)),
            })

        return node_list
        
    except Exception as e:
        logger.error('Error ' + str(e))


def consul_nodes_services(node_name):
    """This will return all the services of a node"""

    # API works for node id also, ask and decide
    services_resp = requests.get('{}/v1/catalog/node-services/{}'.format('http://10.23.239.14:8500', node_name))
    services_resp = json.loads(services_resp.content)

    service_list = []
    for service in services_resp.get('Services'):
        service_list.append({
            'ServiceID': service.get('ID', ''),
            'ServiceName': service.get('Service', ''),
            'ServiceIP': service.get('Address', ''),
            'ServicePort': service.get('Port', ''),
        })

    return service_list