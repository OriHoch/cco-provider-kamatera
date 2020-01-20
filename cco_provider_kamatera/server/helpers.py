import subprocess
import os
import json


def ssh(server, cmd, method='check_call', **kwargs):
    return getattr(subprocess, method)([
        'ssh', '-i', server['keyfile'], f'root@{server["public_ip"]}',
        '-o', 'StrictHostKeyChecking=no',
        *cmd
    ], **kwargs)


def scp_to_server(server, local_filename, remote_filename=None):
    if not remote_filename:
        remote_filename = local_filename
    subprocess.check_call([
        'scp', '-i', server['keyfile'], '-o', 'StrictHostKeyChecking=no',
        local_filename, f'root@{server["public_ip"]}:{remote_filename}',
    ])


def get_server(cluster_id, server_name):
    cluster_path = os.path.expanduser(f'~/cluster-{cluster_id}')
    with open(f'{cluster_path}/cluster.json') as f:
        cluster = json.load(f)
    for server in cluster['servers']:
        if server['name'] == server_name:
            return server
    return None
