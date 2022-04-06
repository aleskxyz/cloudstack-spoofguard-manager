import requests
import json
import urllib3

urllib3.disable_warnings()

class NSXBase():

    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.auth = requests.auth.HTTPBasicAuth(username, password)
        self.eTag = ''

    def _request(self, method, command, params = None ,data = None):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'if-match': self.eTag
            }
        url = f'{self.endpoint}/api{command}'
        response = requests.request(
            method = method, 
            url = url,
            auth = self.auth,
            verify = False,
            json = data,
            params = params,
            headers = headers
            )
        response.raise_for_status()
        if ('Etag' in response.headers):
            self.eTag = response.headers['ETag']
        if not response.text:
            return True
        return json.loads(response.text)

    def get_spoofgurad_policies(self):
        return self._request('GET', '/4.0/services/spoofguard/policies/')

    def get_spoofgurad_policy_ip(self, policy_id, action = 'ACTIVE'):
        params = {'list': action}
        return self._request('GET', f'/4.0/services/spoofguard/{policy_id}', params = params)
    
    def approve_ips(self, policy_id, id, mac, ip_list):
        params = {'vnicid': id, 'action': 'approve'}
        data = {
            'spoofguardList': [
                {
                    'id': id,
                    'vnicUuid': id,
                    'approvedMacAddress': mac,
                    'approvedIpAddress': {
                        'ipAddresses': ip_list
                    },
                },
            ]
        }
        return self._request('POST', f'/4.0/services/spoofguard/{policy_id}', params = params, data = data)
   
    def publish_ips(self, policy_id):
        params = {'action':'publish'}
        return self._request('POST', f'/4.0/services/spoofguard/{policy_id}', params = params)