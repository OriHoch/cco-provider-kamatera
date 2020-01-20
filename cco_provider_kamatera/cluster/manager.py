from ruamel import yaml
import os
import json
from ..kamatera import manager as kamatera_manager
from ..server import manager as server_manager
from ckan_cloud_operator import logs
import subprocess
import time


# rke config --list-version --all
KUBERNETES_VERSION = 'v1.17.0-rancher1-2'


def get_cluster_path(cluster_id):
    return os.path.expanduser(f'~/cluster-{cluster_id}')


def get_cluster(cluster_id):
    cluster_path = get_cluster_path(cluster_id)
    with open(f'{cluster_path}/cluster.json') as f:
        return json.load(f)


def save_cluster(cluster):
    cluster_path = get_cluster_path(cluster['id'])
    with open(f'{cluster_path}/cluster.json', 'w') as f:
        json.dump(cluster, f)


def create(values_yaml):
    if not values_yaml:
        values_yaml = '~/interactive.yaml'
    values_yaml = os.path.expanduser(values_yaml)
    with open(values_yaml) as f:
        values = yaml.safe_load(f.read())
    cluster_id = values['kamatera']['cluster']['id']
    kamatera_manager.initialize(
        f'cluster-{cluster_id}',
        values['kamatera']['api_client_id'],
        values['kamatera']['api_secret'],
        values['kamatera']['api_server']
    )
    cluster_path = os.path.expanduser('~/cluster-hasadna')
    if os.path.exists(f'{cluster_path}/cluster.json'):
        logs.info("Cluster already exists, ignoring the values_yaml and using existing cluster.json")
    else:
        if not os.path.exists(cluster_path):
            os.mkdir(cluster_path)
        with open(f'{cluster_path}/cluster.json', 'w') as f:
            json.dump(values['kamatera']['cluster'], f)
    initialize(cluster_id)


def initialize(cluster_id, skip_server_init=False, dry_run=False):
    cluster = get_cluster(cluster_id)
    cluster['servers'] = server_manager.create_cluster_servers(cluster)
    save_cluster(cluster)
    has_rke_nodes = False
    for server in cluster['servers']:
        if server.get('disabled'):
            continue
        server_name = server['name']
        if not skip_server_init:
            if dry_run:
                logs.info('skipping server_manage.initialize', cluster_id=cluster_id, server_name=server_name)
            else:
                server_manager.initialize(server)
        if 'rke-node' in server['roles']:
            has_rke_nodes = True
    if has_rke_nodes:
        rke_cluster_config = get_rke_cluster_config(cluster)
        rke_config_filename = f'{get_cluster_path(cluster_id)}/rke-cluster.yml'
        with open(rke_config_filename, 'w') as f:
            f.write(logs.yaml_dump(rke_cluster_config))
        if dry_run:
            logs.info('skipping rke command', rke_config_filename=rke_config_filename)
        else:
            i = 0
            while True:
                i += 1
                logs.info('rke up', i=i)
                err = None
                try:
                    subprocess.check_call(['rke', 'up', '--config', rke_config_filename])
                except subprocess.CalledProcessError as e:
                    logs.error(f'{e}')
                    err = e
                if err:
                    if i > 4:
                        raise Exception('Too many iterations')
                    logs.info('sleeping 60 seconds before retrying...')
                    time.sleep(60)
                else:
                    break


def get_rke_cluster_config(cluster):
    nodes = []
    for server in cluster['servers']:
        if server.get('disabled'):
            continue
        if 'rke-node' in server['roles']:
            node = server['rke-node']
            nodes.append(node)
            node['address'] = server['public_ip']
            node['user'] = 'root'
            node['ssh_key_path'] = server['keyfile']
    return {
        'cluster_name': cluster['id'],
        'kubernetes_version': KUBERNETES_VERSION,
        'nodes': nodes,
    }
