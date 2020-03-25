__author__ = 'nilayshah'

class generateD3Dict(object):
    # Put it in another file named 'generate_d3.py'
    def health_colour(self,health):
        if health == 'NORMAL':
            return 'seagreen'
        if health == 'WARNING':
            return 'orange'
        if health == 'CRITICAL':
            return 'red'


    def generate_d3_compatible_dict(self, data):
        # Get distinct app profiles
        app_profs = set()

        for node in data:
            app_profs.add(node['AppProfile'])
        app_profs_converted = []

        for app_prof in app_profs:
            # Filter out app prof nodes
            app_nodes = filter(lambda x: x['AppProfile'] == app_prof, data)

            # Top level node in Tree (Application Profile)
            app_prof_node = {}
            app_prof_node['name'] = 'AppProf'
            app_prof_node['type'] = '#581552'
            app_prof_node['label'] = "abc" # app_nodes[0]['appName']##
            app_prof_node['sub_label'] = app_nodes[0]['AppProfile']
            app_prof_node['attributes'] = {}
            app_prof_node['children'] = []

            # 2nd layer nodes in Tree (EPG)
            # distinct EPGs for current application profile
            epgs = set()
            for app_node in app_nodes:
                epgs.add(app_node['EPG'])

            # Iterating for each EPG
            epg_cnt = 1
            for epg in epgs:
                # distinct_epg_tiers = set()
                distinct_epg_ips = set()
                # Extract EPG nodes with same EPG value and get distinct tier name and ip
                epg_nodes = filter(lambda x: x['EPG'] == epg, app_nodes)
                for epg_node in epg_nodes:
                    # distinct_epg_tiers.add(epg_node['tierName'])
                    distinct_epg_ips.add(epg_node['IP'])
                epg_service_list = set()

                for epg_node in epg_nodes:
                    service_list = epg_node.get("services", {})
                    for service in service_list:
                        epg_service_list.add(service.get("serviceInstance", ""))


                epg_dict = {}
                epg_dict['name'] = "EPG"
                epg_dict['fraction'] = epg_nodes[0]['fraction']
                epg_dict['type'] = '#085A87'
                epg_dict['sub_label'] = epg_nodes[0]['EPG']
                epg_dict['label'] = epg_service_list[0] + ", ..." #",".join(epg_service_list)
                epg_dict['attributes'] = {
                    # 'VRF': epg_nodes[0]['VRF'],
                    # 'BD': epg_nodes[0]['BD'],
                    # 'Contracts': epg_nodes[0]['Contracts'],
                    # 'Nodes': list(set([x['nodeName'] for x in epg_nodes])),
                }

                # if 'Machine Agent Enabled' in epg_nodes[0]:
                #     epg_dict['attributes']['Machine Agent Enabled'] = 'True'

                epg_dict['children'] = []

                # Iterating EP nodes
                ep_cnt = 1
                # Implement NonIPs



                for epg_ip in distinct_epg_ips:
                    # distinct_ep_tiers = set()
                    ep_nodes = filter(lambda x: x['IP'] == epg_ip, epg_nodes)
                    
                    


                    # for ep_node in ep_nodes:
                    #     distinct_ep_tiers.add(ep_node['tierName'])
                    for ep_node in ep_nodes:
                        epg_service_list = [ x["serviceInstance"] for x in ep_node["services"]]

                        ep_dict = {}
                        ep_dict['name'] = "EP"
                        ep_dict['type'] = '#2DBBAD'
                        ep_dict['sub_label'] = ep_nodes[0]['VM-Name']
                        ep_dict['label'] =  ep_node["nodeName"] #",".join(epg_service_list)


                    # sep_list_dict = {}
                    # hrv_list_dict = {}
                    # for ep_node in ep_nodes:
                    #     if (ep_node.get('serviceEndpoints')):
                    #         for sep in ep_node.get('serviceEndpoints'):
                    #             if sep:
                    #                 sep_list_dict[sep['sepName']] = sep

                    #     if (ep_node.get('tierViolations')):
                    #         for hrv in ep_node.get('tierViolations'):
                    #             if hrv:#.get('Violation Id'):
                    #                 hrv_list_dict[hrv['Violation Id']] = hrv
                        ep_dict['attributes'] = {
                            # 'IP': ep_node['IP'],
                            # 'Interfaces': list(set([x['Interfaces'][0] for x in ep_nodes])),
                            # 'VMM-Domain': ep_nodes[0]['VMM-Domain']
                        }

                        ep_dict['children'] = []

                        node_dict = {}
                        node_dict['type'] = '#C5D054'
                        node_dict['label'] = ep_node['nodeName']
                        node_dict['attributes'] = {}
                        ep_dict['children'].append(node_dict)
                        epg_dict['children'].append(ep_dict)


                    # Iterating nodes
                    # node_cnt = 1
                    # for ep_node in ep_nodes:
                    #     node_dict = {}
                    #     node_dict['name'] = "Node"
                    #     node_dict['type'] = '#C5D054'
                    #     node_dict['level'] = self.health_colour(ep_node['nodeHealth'])
                    #     node_dict['label'] = ep_node['nodeName']
                    #     node_dict['attributes'] = {
                    #         'Node-Health': ep_node['nodeHealth']
                    #     }
                    #     ep_dict['children'].append(node_dict)
                    #     node_cnt += 1

                    # epg_dict['children'].append(ep_dict)
                    # ep_cnt += 1
                if epg_nodes[0]['Non_IPs']:
                    non_ep_dict={}
                    non_ep_dict['name'] = 'EP'
                    non_ep_dict['type'] = 'grey'
                    non_ep_dict['level'] = 'grey'
                    non_ep_dict['label'] = ''#'App Unmapped EPs'
                    non_ep_dict['sub_label'] = ''#'App Unmapped EPs'
                    non_ep_dict['attributes'] = epg_nodes[0]['Non_IPs']
                    non_ep_dict['fractions'] = epg_nodes[0]['fraction']
                    epg_dict['children'].append(non_ep_dict)

                # List of IPs -
                app_prof_node['children'].append(epg_dict)
                epg_cnt = epg_cnt + 1   # not used

            app_profs_converted.append(app_prof_node)
        return app_profs_converted