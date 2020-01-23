from ruamel import yaml
import os
import json
from ..kamatera import manager as kamatera_manager
from ..server import manager as server_manager
from ckan_cloud_operator import logs
import subprocess
import time
from ckan_cloud_operator.crds import manager as crds_manager
from ckan_cloud_operator import kubectl


# rke config --list-version --all
KUBERNETES_VERSION = 'v1.17.0-rancher1-2'


def get_cluster_path(cluster_id):
    return os.path.expanduser(f'~/cluster-{cluster_id}')


def get_cluster(cluster_id=None):
    if not cluster_id:
        with open(os.environ.get('KUBECONFIG')) as f:
            cluster_id = yaml.safe_load(f)['current-context']
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
    cluster['servers'] = server_manager.create_cluster_servers(cluster, skip_server_init)
    save_cluster(cluster)
    has_rke_nodes = False
    for server in cluster['servers']:
        if server.get('disabled'):
            continue
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
        subprocess.check_call(['kubectl',
                               '--kubeconfig', f'{get_cluster_path(cluster_id)}/kube_config_rke-cluster.yml',
                               'get', 'nodes'])


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


def persist(cluster_id):
    cluster = get_cluster(cluster_id)
    cluster_secrets = {
        'servers': {}
    }
    for server in cluster['servers']:
        cluster_secrets['servers'][server['name']] = server_secrets = {}
        with open(server['passwordfile']) as f:
            server_secrets['password'] = f.read()
        with open(server['keyfile']) as f:
            server_secrets['private_key'] = f.read()
        with open(server['keyfile'] + '.pub') as f:
            server_secrets['public_key'] = f.read()
    crds_manager.install_crd('kamateracluster', 'kamateraclusters', 'KamateraCluster')
    crds_manager.install_crd('kamateraserver', 'kamateraservers', 'KamateraServer')
    kubectl.apply(crds_manager.get_resource(
        'kamateracluster',
        cluster['id'],
        spec={**{k: v for k, v in cluster.items() if k != 'servers'},
              'server_names': [server['name'] for server in cluster['servers']]}
    ))
    for server in cluster['servers']:
        kubectl.apply(crds_manager.get_resource(
            'kamateraserver',
            f'{server["name"]}',
            spec=server
        ))
        crds_manager.config_set('kamateraserver', server["name"],
                                values=cluster_secrets['servers'][server['name']], is_secret=True)
    with open(f'{get_cluster_path(cluster_id)}/kube_config_rke-cluster.yml') as f:
        crds_manager.config_set('kamateracluster', cluster_id,
                                values={'kube_config_rke-cluster.yml': f.read()}, is_secret=True)


def load(cluster_id):
    cluster = crds_manager.get('kamateracluster',
                               crds_manager.get_resource_name('kamateracluster', cluster_id))['spec']
    cluster['servers'] = []
    servers_path = os.path.expanduser(f'~/cluster-{cluster_id}-servers')
    os.makedirs(servers_path, exist_ok=True)
    for server_name in cluster['server_names']:
        server = crds_manager.get('kamateraserver',
                                  crds_manager.get_resource_name('kamateraserver', server_name))['spec']
        server_secrets = crds_manager.config_get('kamateraserver', server_name, is_secret=True)
        password_filename = f'{servers_path}/server_{server_name}_password.txt'
        private_key_filename = f'{servers_path}/server_{server_name}_id_rsa'
        public_key_filename = private_key_filename + '.pub'
        with open(password_filename, 'w') as f:
            f.write(server_secrets['password'])
        with open(private_key_filename, 'w') as f:
            f.write(server_secrets['private_key'])
        with open(public_key_filename, 'w') as f:
            f.write(server_secrets['public_key'])
        server['passwordfile'] = password_filename
        server['keyfile'] = private_key_filename
        cluster['servers'].append(server)
    del cluster['server_names']
    cluster_path = get_cluster_path(cluster_id)
    os.makedirs(cluster_path, exist_ok=True)
    with open(f'{cluster_path}/cluster.json', 'w') as f:
        json.dump(cluster, f)
    cluster_secrets = crds_manager.config_get('kamateracluster', cluster_id, is_secret=True)
    with open(f'{cluster_path}/kube_config_rke-cluster.yml', 'w') as f:
        f.write(cluster_secrets['kube_config_rke-cluster.yml'])
