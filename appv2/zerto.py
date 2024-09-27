import requests
from config import settings

requests.packages.urllib3.disable_warnings()

class _ZertoAuth():
    def __init__(self):
        pass

    def auth(self, location):
        if location == 'sgu prod':
            self.base_url = settings.sgu_prod_zvm_url
            secret = settings.sgu_prod_secret
            self.zvm_name = 'SGU Prod'
        elif location == 'boi prod':
            self.base_url = settings.boi_prod_zvm_url
            secret = settings.boi_prod_secret
            self.zvm_name = 'BOI Prod'
        elif location == 'fb prod':
            self.base_url = settings.fb_prod_zvm_url
            secret = settings.fb_prod_secret
            self.zvm_name = 'FB Prod'
        elif location == 'sgu inf':
            self.base_url = settings.sgu_inf_zvm_url
            secret = settings.sgu_inf_secret
            self.zvm_name = 'SGU Inf'
        elif location == 'boi inf':
            self.base_url = settings.boi_inf_zvm_url
            secret = settings.boi_inf_secret
            self.zvm_name = 'BOI Inf'
        elif location == 'okc inf':
            self.base_url = settings.okc_inf_zvm_url
            secret = settings.okc_inf_secret
            self.zvm_name = 'OKC Inf'
        else:
            print("Invalid location...")
            return None
        #print(base_url)
        #base_url = '10.103.83.190'
        #print(self.base_url)
        auth_url = f'https://{self.base_url}/auth/realms/zerto/protocol/openid-connect/token'
        print("Attempting to authenticate...")

        response = requests.post(auth_url, 
                                data={"grant_type": "client_credentials", 
                                        "client_id": settings.keycloak_client_id, 
                                        "client_secret": secret}, 
                                timeout=10, 
                                verify=False)

        if response.status_code == 200:
            print(f"Authentication successful against {self.base_url}!")
            return response.json()['access_token']
        else:
            print(f'Failed to authenticate: {response.status_code} - {response.text}')
            return None
        

class ZertoGet():
    def __init__(self, location):
        self.location = location
        self.zerto_auth = _ZertoAuth()
        self.auth_token = self.zerto_auth.auth(location)
        self.zvm_name = self.zerto_auth.zvm_name
        self.subs_naughty_list = [8, 24, 27, 30, 31, 32, 33] # List of substatuses that are not good and will cause a VPG to be considered down
        #print(self.auth_token)
        self.base_url = self.zerto_auth.base_url
        #print(location)
        if not self.auth_token:
            print("There was a problem getting the auth token...")
            return None

    def get_vpgs(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        url = f'https://{self.base_url}/v1/vpgs'
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            list_of_vpgs = response.json()
            return list_of_vpgs
        else:
            print("Failed to get VPGs...")
            print(f'Error: {response.status_code} - {response.text} for endpoint')
            return None
    
    def get_sites(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        url = f'https://{self.base_url}/v1/peersites'
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            list_of_sites = response.json()
            return list_of_sites
        else:
            print("Failed to get sites...")
            print(f'Error: {response.status_code} - {response.text} for endpoint')
            return None

    def get_vras(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.auth_token}'
        }
        url = f'https://{self.base_url}/v1/vras'
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            list_of_vras = response.json()
            return list_of_vras
        else:
            print("Failed to get VRAs...")
            print(f'Error: {response.status_code} - {response.text} for endpoint')
            return None
        
    def get_status(self, status=None) -> str:
        '''
        Returns the status of a VPG if a status number is provided. If no status number is provided, it returns a list of all possible statuses.
        '''
        headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.auth_token}'
            }
        url = f'https://{self.base_url}/v1/vpgs/statuses'
        if status == None:
            response = requests.get(url, headers=headers, verify=False)
            list_of_statuses = response.json()
            print(list_of_statuses)
        else:
            response = requests.get(url, headers=headers, verify=False)
            list_of_statuses = response.json()
            if status > 2:
                print("This status is not good... VPG Considered DOWN...")
            return list_of_statuses[status]
    
    def get_substatus(self, substatus=None):
        '''
        Returns the substatus of a VPG if a substatus number is provided. If no substatus number is provided, it returns a list of all possible substatuses.
        '''
        headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {self.auth_token}'
            }
        url = f'https://{self.base_url}/v1/vpgs/substatuses'
        if substatus == None:
            response = requests.get(url, headers=headers, verify=False)
            list_of_substatuses = response.json()
            return list_of_substatuses
            #print(list_of_substatuses)
        else:
            response = requests.get(url, headers=headers, verify=False)
            list_of_substatuses = response.json()
            return list_of_substatuses[substatus]

    
    def get_throughput_zvm(self) -> int:
        '''
        Returns the total throughput of all VPGs on a ZVM
        '''
        list_of_vpgs = self.get_vpgs()
        throughput = 0
        for vpg in list_of_vpgs:
            throughput += vpg['ThroughputInMB']
        
        #print(f'Total throughput on {self.zvm_name} is {throughput} MB')
        return throughput
    
    def get_throughput_sites(self) -> list:
        '''
        Returns a list with the total throughput of all VPGs on each site

        [{'site1': 'throughput1'}, ...]
        '''
        list_of_sites = []
        vpgs = self.get_vpgs()
        for vpg in vpgs:
            site = vpg['ProtectedSiteName']
            if site not in list_of_sites:
                list_of_sites.append(site)
        #print(list_of_sites)
        all_sites_with_throughput = []
        for site in list_of_sites:
            throughput = 0
            for vpg in vpgs:
                if vpg['ProtectedSiteName'] == site:
                    throughput += vpg['ThroughputInMB']
            #print(f'Total throughput on {site} is {throughput} MB')
                one_site_with_throughput = {site: throughput}
                
            all_sites_with_throughput.append(one_site_with_throughput)
        #print(all_sites_with_throughput)
        return all_sites_with_throughput
    
    def get_percent_vpgs_up(self):
        vpg_list = self.get_vpgs()
        list_of_sites = []
        percent_vpgs_per_site = []
        for vpg in vpg_list:
            site = vpg['ProtectedSiteName']
            if site not in list_of_sites:
                list_of_sites.append(site)
        for site in list_of_sites:
            total_vpgs = 0
            up_vpgs = 0
            for vpg in vpg_list:
                if vpg['ProtectedSiteName'] == site:
                    total_vpgs += 1
                    if vpg['Status'] == 0 or 1:
                        up_vpgs += 1
            percent = (up_vpgs / total_vpgs) * 100
            percent_vpgs_per_site.append({site: percent})
        #print(percent_vpgs_per_site)
        return percent_vpgs_per_site

        





#zerto = ZertoGet('sgu inf')

# site_percent = zerto.get_percent_vpgs_up()
#zvm_throughput = zerto.get_throughput_zvm()
#print(zvm_throughput)
# site_throughput = zerto.get_throughput_sites()

# alert_sites = []

# for site in site_percent:
#     for key, value in site.items():
#         if value == 80:
#             alert_sites.append(key)
# if alert_sites == []:
#     pass
# else:
#     print(f"The following sites have less than 80% of their VPGs up: {alert_sites}")


