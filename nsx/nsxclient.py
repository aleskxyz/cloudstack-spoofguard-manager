from nsx.nsxbase import NSXBase
import re

class NSXClient(NSXBase):
    
    def __init__(self, endpoint, username, password):
        super().__init__(endpoint, username, password)
    
    def find_spoofguard_policy_id_by_name(self, policy_name):
        policies = self.get_spoofgurad_policies()
        for policy in policies['policies']:
            if policy['name'] == policy_name:
                return policy['policyId']
    
    def get_spoofguard_ip_list(self, policy_id, list_name):
        nics = self.get_spoofgurad_policy_ip(policy_id,list_name)
        output = []
        vm_name_regex = re.compile('^(.*) - Network adapter \d*$')
        for nic in nics['spoofguardList']:
            vm_name = vm_name_regex.match(nic['nicName']).group(1)
            output.append({
                'id': nic['id'],
                'vmName': vm_name,
                'mac': nic['detectedMacAddress'],
                'approvedIps': nic['approvedIpAddress']['ipAddresses'],
                'detectedIps': nic['detectedIpAddress']['ipAddresses'],
            })
        return output

