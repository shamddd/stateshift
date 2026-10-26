import paramiko, os, json, requests, tomli

key_path = os.path.expanduser('~/.ssh/id_ed25519')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('69.145.85.89', port=16644, username='root', pkey=paramiko.Ed25519Key.from_private_key_file(key_path), timeout=10)

stdin, stdout, stderr = client.exec_command('wc -l /workspace/stateshift/data/smoke_test_results.jsonl; wc -l /workspace/stateshift/data/primary_7b_results.jsonl; cat /workspace/stateshift/logs/heartbeat.json; echo ""; tail -n 1 /workspace/stateshift/data/primary_7b_results.jsonl')
print('=== POD GENERATION METRICS ===')
print(stdout.read().decode())
client.close()

with open(os.path.expanduser('~/.runpod/config.toml'), 'rb') as f:
    api_key = tomli.load(f)['default']['api_key']
headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
q = '{ myself { clientBalance } }'
r = requests.post('https://api.runpod.io/graphql', json={'query': q}, headers=headers, timeout=10)
bal = r.json().get('data', {}).get('myself', {}).get('clientBalance', 0.0)
print('=== RUNPOD ACCOUNT BALANCE ===')
print(f'Current Client Balance: ${float(bal):.4f} USD')
