# CloudStack SpoofGuard Manager
## Description
This script gets all events of pending IPs and duplicated IPs from VMware NSX SpoofGuard and decides to approve or ignore the request based on VMs data on Apache CloudStack.
 It uses a caching mechanism for processing requests, so it will only call CloudStack if there is a new request from VMware NSX SpoofGuard.

## User Guide
### Installation
1. Get the script and install dependencies
```bash
git clone https://github.com/aleskxyz/cloudstack-spoofguard-manager.git
cd cloudstack-spoofguard-manager
pip install -r requirements.txt
```
1. Edit the `config.yml` file and fill it with appropriate data:
```yaml
nsx:
  url: https://nsx_url
  username: nsx_username
  password: nsx_password
  policyName: spoofguard_policy_name

cloudstack:
  url: https://cloudstack_url/client/api
  apiKey: cloudstack_api_ky
  secretKey: cloudstack_secret_key

cache:
  databasePath: './cache.sqlite'
```
1. Create a cronjob task for running the script every minute:
```bash
* * * * *    root    /path/to/main.py
```