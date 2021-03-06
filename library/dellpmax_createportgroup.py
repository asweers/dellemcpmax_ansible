#!/usr/bin/python


from __future__ import absolute_import, division, print_function
import PyU4V
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'VMAX REST API Community '
                                    'https://community.emc.com/docs/DOC-56447'
                    }
DOCUMENTATION = r'''
---
module: dellpmax_createsg

Author: Paul Martin @rawstorage

Contributors: Rob Mortell @robmortell

software versions=ansible 2.6.2
                  python version = 2.7.15rc1 (default, Apr 15 2018,

short_description: 
    module to create a portgroup, Port Groups are sets of Front End 
    ports on VMAX and PowerMAX arrays where Host HBAs are zoned.   Port 
    Group name needs to be unique and not already exist.  You can't mix 
    emulations in a port group, transport protocol must me same on all ports 
    added 
    
notes:
    - This module has been tested against UNI 9.0.  Every effort has been 
    made to verify the scripts run with valid input.  These modules 
    are a tech preview.  Additional error handling will be added at a later 
    date, base functionality only right now.



Requirements:
    - Ansible, Python 2.7, Unisphere for PowerMax version 9.0 or higher. 
    VMAX All Flash, VMAX3, or PowerMax storage Array
    Python module PyU4V also needs to be installed from pip or PyPi


playbook options:
    unispherehost:
        description:
            - Full Qualified Domain Name or IP address of Unisphere for 
            PowerMax host.
        required:True

    universion:
        -description:
            - Integer, version of unipshere software 
            https://{HostName|IP}:8443/univmax/restapi/{version}/{resource}
            90 is the release at time of writing module.
        -required:True
    verifycert:
        description: 
            -Boolean, securitly check on ssl certificates
        required:True             

        required: True
    array_id:
        description:
            - Integer 12 Digit Serial Number of PowerMAX or VMAX array.
        required:True
    portgroup_id:
         description:
            -  String value to denote name of portgroup, No  Special Character 
            support except for _.  Case sensistive for REST Calls.
        required:True
    Port List:
        description:
            - List of Directors and Ports to be added to the Port Group in 
            the format 
              {
      "directorId": "FA-1D",
      "portId": "4"
                },
                  {
      "directorId": "FA-2D",
      "portId": "4"
                }
            
        required:True
    consistent_lun:
        description:
            - Boolean Value, specifying consistent_lun ensures LUN address 
            consistency across ports, this is not required on most modern 
            operating systems as WWN or UUID is used to Uniqely identify luns
        required:True    
    async:
        Optional Parameter to set REST call to run Asyncronously, job will 
        be submitted to job queue and executed.  Task Id will be returned in 
        JSON for lookup purposed to check job completion status. 

'''

EXAMPLES = r'''
- name: Create Port Group
  hosts: localhost
  connection: local
  vars:
        unispherehost: '10.60.156.63'
        uniport: 8443
        universion: "90"
        verifycert: False
        user: 'smc'
        password: 'smc'
        array_id: "000197600156"
  tasks:
      dellpmax_createportgroup:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             port_list:
                     -
                      directorId: "FA-1D"
                      portId: "4"
                     -
                      directorId: "FA-2D"
                      portId: "4"
             portgroup_id: "Ansible_PG"
'''
RETURN = r'''
'''


def main():
    changed = False
    # print (changed)
    module = AnsibleModule(
        argument_spec=dict(
            unispherehost=dict(required=True),
            universion=dict(type='int', required=False),
            verifycert=dict(type='bool', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            array_id=dict(type='str', required=True),
            portgroup_id=dict(type='str', required=True),
            port_list=dict(type='list', required=True),

        )
    )
    # Make REST call to Unisphere Server and execute create Host

    payload = (
        {
            "portGroupId": module.params['portgroup_id'],
            "symmetrixPortKey": module.params['port_list']
        }
    )

    headers = ({

        'Content-Type': 'application/json'

    })

    conn = PyU4V.U4VConn(server_ip=module.params['unispherehost'], port=8443,
                         array_id=module.params['array_id'],
                         verify=module.params['verifycert'],
                         username=module.params['user'],
                         password=module.params['password'],
                         u4v_version=module.params['universion'])

    # Setting connection shortcut to Provisioning modules to simplify code

    dellemc = conn.provisioning

    changed = False


    pglist = dellemc.get_portgroup_list()

    if module.params['portgroup_id'] in pglist:
        module.fail_json(msg='Portgroup already exists, failing task')

    else:
        dellemc.create_multiport_portgroup(portgroup_id=module.params['portgroup_id'],
                                           ports=module.params['port_list'])
        changed = True

    module.exit_json(changed=changed)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()


