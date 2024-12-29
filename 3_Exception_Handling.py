from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_configs, send_command
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.data import load_yaml
import os
from rich import print as rprint
import ipdb

nr = InitNornir (config_file="Cisco_Inventory/config.yaml")

# Clearing the Screen
os.system('clear')

'''
This program required to configure any IGP or EGP routing protocol before verification
of exception handling so please execute "2_Config_iBGP.py" which will configure iBGP
and it will populate routing table with next hope to iBGP neighbours. 

*******************
Exception Handling
*******************

after iBGP configuration we will handle error using try and except block. 
wewill parse routing table uisng nfsm, we will find all next avaiable hope of 
every router in network, we know routing tble shows only next hope for either static
or dynamic learned routes. routing table does not show next hope for directly connected 
or loopback routes so once we will try to access next hope key for directly connected
routes or loopback it will generate keyError: because value not avaiable for these routes
so we will handle this error using try and except block.

ipdb> pp nr.inventory.hosts['vIOS-R1']['routing_table']['vrf']['default']['address_family']['ipv4']['routes']
{'1.1.1.1/32': {'active': True,
                'next_hop': {'outgoing_interface': {'Loopback0': {'outgoing_interface': 'Loopback0'}}},
                'route': '1.1.1.1/32',
                'source_protocol': 'connected',
                'source_protocol_codes': 'C'},
 '10.1.6.0/24': {'active': True,
                 'next_hop': {'outgoing_interface': {'GigabitEthernet0/2': {'outgoing_interface': 'GigabitEthernet0/2'}}},
                 'route': '10.1.6.0/24',
                 'source_protocol': 'connected',
                 'source_protocol_codes': 'C'},
 '4.4.4.4/32': {'active': True,
                'metric': 5,
                'next_hop': {'next_hop_list': {1: {'index': 1,
                                                   'next_hop': '10.1.6.6',
                                                   'outgoing_interface': 'GigabitEthernet0/2',
                                                   'updated': '00:29:22'},
                                               2: {'index': 2,
                                                   'next_hop': '10.1.5.5',
                                                   'outgoing_interface': 'GigabitEthernet0/1',
                                                   'updated': '00:29:22'}}},
                'route': '4.4.4.4/32',
                'route_preference': 110,
                'source_protocol': 'ospf',
                'source_protocol_codes': 'O'},

We can iterate loop on below key and will provide each route in routing table
['routing_table']['vrf']['default']['address_family']['ipv4']['routes']

we can get all next hopes of route with below key
pp nr.inventory.hosts['vIOS-R1']['routing_table']['vrf']['default']['address_family']['ipv4']['routes']['4.4.4.4/32']['next_h
op']['next_hop_list']
{1: {'index': 1,
     'next_hop': '10.1.6.6',
     'outgoing_interface': 'GigabitEthernet0/2',
     'updated': '00:29:22'},
 2: {'index': 2,
     'next_hop': '10.1.5.5',
     'outgoing_interface': 'GigabitEthernet0/1',
     'updated': '00:29:22'}}

below key will provide exact next hope value
ipdb> pp nr.inventory.hosts['vIOS-R1']['routing_table']['vrf']['default']['address_family']['ipv4']['routes']['4.4.4.4/32']['next_h
op']['next_hop_list'][1]['next_hop']
'10.1.6.6'

if we run below code with out try & except block then we get below error

raceback (most recent call last):
  File "/home/imran/Documents/Automation/Nornir/.MyNAPALMvenv/lib/python3.12/site-packages/nornir/core/task.py", line 99, in start
    r = self.task(self, **self.params)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/imran/Documents/Automation/Nornir/Runbooks_Repositories/Python_Cisco_Lab3/3_Exception_Handling.py", line 90, in get_nexthope_info
    next_hope_list = routes[route]['next_hop']['next_hop_list']
                     ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'next_hop_list'

'''


def get_nexthope_info (task):
    show_routes = task.run (task=send_command, command="show ip route")
    task.host['routing_table'] = show_routes.scrapli_response.genie_parse_output()
    
    # below will provide us list of all routes, we can iterate it using for loop
    routes = task.host['routing_table']['vrf']['default']['address_family']['ipv4']['routes']

    for route in routes:
        # below will provide all next hopes of route of only statis or dynamic learned routes
        # but it will not provide neeext hope list for local directly connected or loopack interfaces
        # so we will use try & except block to handel the Keyerror
        # we can iterate this list as well
        try:
            next_hope_list = routes[route]['next_hop']['next_hop_list']
            for next_hope_index in next_hope_list:
                next_hope = next_hope_list[next_hope_index]['next_hop']
                rprint (f"{task.host} - Route {route} Next Hope Info: {next_hope}")
        except KeyError:
            pass

results = nr.run (task=get_nexthope_info)
#print_result (results)
#ipdb.set_trace()