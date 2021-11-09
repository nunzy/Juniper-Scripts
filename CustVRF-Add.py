import yaml
import sys
import json
from jinja2 import Template
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config
from lxml import etree

## Read yaml
mytemplate = Template(open('template/CustVRF.j2').read())
mydata = yaml.load(open('config/CustSetup.yml').read(), Loader=yaml.BaseLoader)
custsetup = mydata["CustSetup"]
cust_name = mydata['CustSetup'][0]['CustName']
cust_crm = mydata['CustSetup'][0]['CustCRM']
cust_result = '-'.join([cust_name,cust_crm])

### Render the jinja2 template for debug
#myconfig = mytemplate.render(mydata)
#print("\n### Here's the full config:")
#print(myconfig)

## Define connection details
hostname = "pe-f-00.gwr.uk.hso-group.net"
junos_username = input("Junos OS username: ")
junos_password = getpass("Junos OS or SSH key password: ")

## Make connection
dev = Device(host=hostname, user=junos_username, passwd=junos_password)

try:
    dev.open()
except ConnectError as err:
    print ("Cannot connect to device: {0}".format(err))
    sys.exit(1)
except Exception as err:
    print (err)
    sys.exit(1)

## Check RI is created
data = dev.rpc.get_instance_information()

ri_data = data.findall('.//instance-core')

for instance in ri_data:
    name_id = instance.find('.//instance-name').text
    if name_id[:-21]==cust_result:
        print("\n### Matching VRF Found ###")
        print("\n### RI:" + name_id + " ###")
        dev.close()
        sys.exit(1)

## Apply configuration changes
with Config(dev, mode='exclusive') as cu:
    cu.load(template_path="template/CustVRF.j2", template_vars=mydata, merge=True, format="text")
    cu.pdiff()
    junos_commit = input("Commit changes: (yes|no) ")
    if junos_commit=='yes':
        cu.commit()
        print("\n### Commit complete ###")
    else:
        print("\n### Rolling back ###")
        cu.rollback()

## Tidy and close
dev.close()
