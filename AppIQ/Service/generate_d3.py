__author__ = 'nilayshah'
import pprint
class generateD3Dict(object):
    # Put it in another file named 'generate_d3.py'
    def health_colour(self,health):
        if health == 'NORMAL':
            return 'seagreen'
        if health == 'WARNING':
            return 'orange'
        if health == 'CRITICAL':
            return 'red'


    def generate_d3_compatible_dict(self,data):
        #pprint.pprint(data)
        # Get distinct app profiles
        app_profs = set()
        for node in data:
            #pprint(node)  # Changed by Nilay
            app_profs.add(node['AppProfile'])
        app_profs_converted = []
        for app_prof in app_profs:
            # Filter out app prof nodes
            app_nodes = filter(lambda x: x['AppProfile'] == app_prof, data)

            app_tree = {}

            app_prof_node = {}
            stage_cnt = 0
            app_prof_node['name'] = 'AppProf'
            app_prof_node['type'] = '#581552'
            app_prof_node['level'] = self.health_colour(app_nodes[0]['appHealth'])
            app_prof_node['label'] = app_nodes[0]['appName']
            app_prof_node['sub_label'] = app_nodes[0]['AppProfile']
            app_prof_node['attributes'] = {
                # TODO
                'App-Health': str(app_nodes[0]['appHealth'])  # Changed by Nilay
            }
            app_prof_node['children'] = []

            # distinct EPGs
            epgs = set()
            for app_node in app_nodes:
                epgs.add(app_node['EPG'])

            # Iterating for each EPG
            epg_cnt = 1
            for epg in epgs:
                distinct_epg_tiers = set()
                distinct_epg_ips = set()
                epg_nodes = filter(lambda x: x['EPG'] == epg, app_nodes)
                for epg_node in epg_nodes:
                    distinct_epg_tiers.add(epg_node['tierName'])
                    distinct_epg_ips.add(epg_node['IP'])
                epg_dict = {}
                epg_dict['name'] = "EPG"
                epg_dict['fraction'] = epg_nodes[0]['fraction']
                epg_dict['type'] = '#085A87'
                epg_dict['level'] = self.health_colour(epg_nodes[0]['tierHealth'])  # Changed by Nilay
                epg_dict['sub_label'] = epg_nodes[0]['EPG']
                epg_dict['label'] = ",".join(distinct_epg_tiers)
                epg_dict['attributes'] = {
                    'VRF': epg_nodes[0]['VRF'],
                    'BD': epg_nodes[0]['BD'],
                    'VMM-Domain': epg_nodes[0]['VMM-Domain'],
                    'Contracts': epg_nodes[0]['Contracts'],
                    # 'Contracts' : list(set([x['Contracts'][0] for x in epg_nodes if len(x['Contracts']) > 0])), #if len(x['Contracts']) > 0 else ['None']
                    'Nodes': list(set([x['nodeName'] for x in epg_nodes])),
                    'Tier-Health': epg_nodes[0]['tierHealth']
                }

                if 'Machine Agent Enabled' in epg_nodes[0]:
                    epg_dict['attributes']['Machine Agent Enabled'] = 'True'

                # if (epg_dict['attributes']['Contracts']) == set(['None']):
                #    del epg_dict['attributes']['Contracts']
                # epg_dict['attributes'] = {
                #     'vrf': 'AppD-VRF',
                #     'bd': 'AppD-bd1',
                #     'nodes': ['Node1', 'Node2']
                # }

                epg_dict['children'] = []


                # Iterating EP nodes
                ep_cnt = 1
                # Implement NonIPs

                for epg_ip in distinct_epg_ips:
                    distinct_ep_tiers = set()
                    ep_nodes = filter(lambda x: x['IP'] == epg_ip, epg_nodes)
                    for ep_node in ep_nodes:
                        distinct_ep_tiers.add(ep_node['tierName'])
                    ep_dict = {}
                    ep_dict['name'] = "EP"
                    # ep_dict['x'] =
                    ep_dict['type'] = '#2DBBAD'
                    ep_dict['level'] = self.health_colour(ep_nodes[0]['tierHealth'])
                    ep_dict['sub_label'] = ep_nodes[0]['VM-Name']
                    ep_dict['label'] = ",".join(distinct_ep_tiers)


                    sep_list_dict = {}
                    for ep_node in ep_nodes:
                        if (ep_node['serviceEndpoints']):
                            for sep in ep_node['serviceEndpoints']:
                                sep_list_dict[sep['sepName']] = sep

                    hrv_list_dict = {}
                    for ep_node in ep_nodes:
                        if (ep_node['tierViolations']):
                            for hrv in ep_node['tierViolations']:
                                if hrv:#.get('Violation Id'):
                                    hrv_list_dict[hrv['Violation Id']] = hrv
                    ep_dict['attributes'] = {
                        'IP': epg_ip,
                        'Interfaces': list(set([x['Interfaces'][0] for x in ep_nodes])),
                        'ServiceEndpoints': sep_list_dict.values(),
                        # 'ServiceEndpoints': {x['serviceEndpoints'][0]['Name']: x for x in ep_nodes}.values(),
                        'HealthRuleViolations': hrv_list_dict.values(), #list(set([(x['tierViolations']) for x in ep_nodes])),  # json.loads
                        'Tier-Health': ep_nodes[0]['tierHealth']
                    }

                    # ep_dict['attributes'] = {
                    #     'IP': '10.0.9.9',
                    #     'Interfaces': ["topology/pod-1/paths-101/pathep-[eth1/15]"],
                    #     'ServiceEndpoints': [
                    #         {'Total Errors': -1, 'type': 'SERVLET', 'Errors/Min': -1, 'Error Percentage': 0.0,
                    #          'sep': '/cart/services'}]
                    # }
                    ep_dict['children'] = []

                    # Iterating nodes
                    node_cnt = 1
                    for ep_node in ep_nodes:
                        node_dict = {}
                        node_dict['name'] = "Node"
                        node_dict['type'] = '#C5D054'
                        node_dict['level'] = self.health_colour(ep_node['nodeHealth'])
                        node_dict['label'] = ep_node['nodeName']
                        node_dict['attributes'] = {
                            'Node-Health': ep_node['nodeHealth']
                        }
                        ep_dict['children'].append(node_dict)
                        node_cnt += 1

                    epg_dict['children'].append(ep_dict)
                    ep_cnt += 1
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
                epg_cnt = epg_cnt + 1

            app_profs_converted.append(app_prof_node)
        return app_profs_converted


