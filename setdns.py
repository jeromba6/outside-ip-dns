#!/usr/bin/env python3
import requests
import json
import transip_api_v6

login          = 'jvgemert'
keyfile        = 'test copy.pem'
domain         = 'gemert.net'
find_dns_entry = 'test-script'

# Get public IP
res = requests.get('https://ipinfo.io')
if res.status_code != 200:
    print('Failed to get public ip.')
    exit(1)
pub_ip=json.loads(res.text)['ip']

# Get Header for authentication against transip api V6
key_file = open(keyfile, "r")
key = key_file.read()
key_file.close()
# ph = transip_api_v6.Generic(login, key)
headers = transip_api_v6.Generic(login, key).get_headers()

# Request domains managed by this account
domains=transip_api_v6.Domains(headers)
managed_domains=domains.get()
print(json.dumps(managed_domains,indent=2))
print()

# Request DNS entries for this domain
dns_entries = domains.get_dns(domain)
print(json.dumps(dns_entries,indent=2))
print()

# Find entry
found_dns_entries = []
for dns_entry in dns_entries['dnsEntries']:
  if dns_entry['name'] == find_dns_entry and dns_entry['type'] == 'A':
    found_dns_entries.append(dns_entry)
    print (dns_entry)
print (json.dumps(found_dns_entries))
print()

# Change entry for this domain with current public IP
if len(found_dns_entries) == 0:
  data = '''{
    "dnsEntry": {
      "name": "''' + find_dns_entry + '''",
      "expire": 300,
      "type": "A",
      "content": "''' + pub_ip + '''"
    }
  }
  '''
  domains.post_dns(domain, data)
elif len(found_dns_entries) == 1:
  if found_dns_entries[0]['content'] == pub_ip:
    print('No change needed')
  else:
    print('Change dns entry')
    print('From: ' + json.dumps(found_dns_entries[0]))
    found_dns_entries[0]['content'] = pub_ip
    print('To  : ' + json.dumps(found_dns_entries[0]))
    domains.patch_dns(domain, '{"dnsEntry": ' + json.dumps(found_dns_entries[0]) +'}')
else:
  print('Multiple entries found, can\'t determine which to change (if any).')
