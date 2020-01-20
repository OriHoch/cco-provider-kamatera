import os
import subprocess
import json
from ckan_cloud_operator import logs


def initialize(creds_id, api_client_id, api_secret, api_server):
    cloudcli_yaml = [f'apiServer: {api_server}\n',
                     f'apiClientid: "{api_client_id}"\n',
                     f'apiSecret: "{api_secret}"\n']
    if not api_client_id or not api_secret or not api_server:
        raise Exception(f"invalid args: {cloudcli_yaml}")
    with open(os.path.expanduser('~/.cloudcli.yaml'), 'w') as f:
        f.writelines(cloudcli_yaml)
    with open(os.path.expanduser(f'~/.cloudcli-{creds_id}.yaml'), 'w') as f:
        f.writelines(cloudcli_yaml)
    subprocess.check_call(['cloudcli', 'version'])


def server_list():
    return json.loads(subprocess.check_output(['cloudcli', 'server', 'list', '--format', 'json']))


def server_info(name):
    try:
        return json.loads(subprocess.check_output(['cloudcli', 'server', 'info', '--format', 'json',
                                                   '--name', name]))
    except subprocess.CalledProcessError:
        return None


def terminate_server(server_name, force=False):
    logs.info(f'terminating server (server_name={server_name} force={force})')
    subprocess.check_call(['cloudcli', 'server', 'terminate',
                           *(["--force"] if force else []),
                           "--name", server_name,
                           "--wait"])


def create_server(server, server_password):
    logs.info(f'creating server (server_name={server["name"]})')
    logs.print_yaml_dump(server)
    cmd = ['cloudcli', 'server', 'create', '--wait']
    for arg in ['billingcycle', 'cpu', 'dailybackup', 'datacenter', 'disk', 'image', 'managed', 'monthlypackage',
                'name', 'network', 'password', 'poweronaftercreate', 'quantity', 'ram']:
        if arg == 'quantity':
            val = '1'
        elif arg == 'password':
            val = server_password
        else:
            val = server[arg]
        if arg == 'disk' or arg == 'network':
            for subval in val:
                cmd += [f'--{arg}', subval]
        else:
            cmd += [f'--{arg}', val]
    subprocess.check_call(cmd)


def server_sshkey(server_sshkey_public, server_password, server_name):
    subprocess.check_call(['cloudcli', 'server', 'sshkey',
                           '--name', server_name,
                           '--password', server_password,
                           '--public-key', server_sshkey_public])


def install_server_role(role, server, server_password):
    pass
