import subprocess
import os
import json
from ruamel import yaml
from ckan_cloud_operator import logs


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


def get_server(cluster_id=None, server_name=None, node_name=None):
    cluster = get_cluster(cluster_id)
    if not server_name:
        server_name = f'{cluster["id"]}-{node_name}'
    for server in cluster['servers']:
        if server['name'] == server_name:
            return server
    logs.critical('server not found', cluster_id=cluster_id, server_name=server_name, node_name=node_name)
    logs.exit_catastrophic_failure(quiet=True)


def get_cluster(cluster_id=None):
    if not cluster_id:
        with open(os.environ.get('KUBECONFIG')) as f:
            cluster_id = yaml.safe_load(f)['current-context']
    cluster_path = os.path.expanduser(f'~/cluster-{cluster_id}')
    with open(f'{cluster_path}/cluster.json') as f:
        return json.load(f)
