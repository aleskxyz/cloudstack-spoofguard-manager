from nsx.nsxclient import NSXClient
from cloudstack.cloudstackclient import CloudStackClient
import ipaddress
from simplecache.simplecache import SimpleCache
import yaml

with open("config.yml", "r") as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

nsx_endpoint = config['nsx']['url']
nsx_username = config['nsx']['username']
nsx_password = config['nsx']['password']
nsx_policy_name = config['nsx']['policyName']
cloudstack_url = config['cloudstack']['url']
cloudstack_api_key = config['cloudstack']['apiKey']
cloudstack_secret_key = config['cloudstack']['secretKey']
cache_database_path = config['cache']['databasePath']

nsx = NSXClient(nsx_endpoint,nsx_username,nsx_password)
policy_id = nsx.find_spoofguard_policy_id_by_name(nsx_policy_name)
cache = SimpleCache(cache_database_path)

def find_allowed_ips(cloudstack_url,cloudstack_api_key,cloudstack_secret_key,vm_name, mac):
    cloudstack = CloudStackClient(cloudstack_url,cloudstack_api_key,cloudstack_secret_key)
    vm_list = cloudstack.listVirtualMachines({'keyword':vm_name,'listall':'true'})
    vm_info = None
    allowed_ips = []
    if vm_list:
        for vm in vm_list['virtualmachine']:
            if vm['instancename'] == vm_name:
                vm_info = vm
                break
    if vm_info:
        for nic in vm_info['nic']:
            if nic['macaddress'] == mac:
                allowed_ips.append(nic['ipaddress'])
                for secondary_ip in nic['secondaryip']:
                    allowed_ips.append(secondary_ip['ipaddress'])
    return allowed_ips

try:
    duplicated_ips = nsx.get_spoofguard_ip_list(policy_id,'DUPLICATE')
    for item in duplicated_ips:
        if not cache.lookup({'duplicated': item}):
            allowed_ips = find_allowed_ips(cloudstack_url,cloudstack_api_key,cloudstack_secret_key,item['vmName'], item['mac'])
            for ip in item['detectedIps']:
                if ipaddress.ip_address(ip).is_link_local:
                    allowed_ips.append(ip)
            if list(set(item['detectedIps']) - set(allowed_ips)):
                nsx.approve_ips(policy_id,item['id'],item['mac'],[])
                nsx.publish_ips(policy_id)
            cache.add({'duplicated': item})
        else:
            cache.update_last_access({'duplicated': item})

    pending_ips = nsx.get_spoofguard_ip_list(policy_id,'REVIEW_PENDING')
    for item in pending_ips:
        if not cache.lookup({'pending': item}):
            allowed_ips = find_allowed_ips(cloudstack_url,cloudstack_api_key,cloudstack_secret_key,item['vmName'], item['mac'])
            for ip in item['detectedIps']:
                if ipaddress.ip_address(ip).is_link_local:
                    allowed_ips.append(ip)
            if allowed_ips:
                nsx.approve_ips(policy_id,item['id'],item['mac'],allowed_ips)
                nsx.publish_ips(policy_id)
            cache.add({'pending': item})
        else:
            cache.update_last_access({'pending': item})
except Exception as error:
    print(error)