from .roles import manager as roles_manager
from . import helpers
import os
import binascii
import subprocess
from ..kamatera import manager as kamatera_manager
from ckan_cloud_operator import logs


def get_cluster_servers_path(cluster_id):
    return os.path.expanduser(f'~/cluster-{cluster_id}-servers')


def get_server_password(cluster_id, server_name):
    password_filename = f'{get_cluster_servers_path(cluster_id)}/server_{server_name}_password.txt'
    if os.path.exists(password_filename):
        with open(password_filename) as f:
            server_password = f.read()
    else:
        server_password = 'Aa' + \
                          binascii.hexlify(os.urandom(8)).decode() + '!'
        with open(password_filename, 'w') as f:
            f.write(server_password)
    return server_password, password_filename


def get_server_sshkey(cluster_id, server_name):
    keyfile = f'{get_cluster_servers_path(cluster_id)}/server_{server_name}_id_rsa'
    if not os.path.exists(keyfile):
        subprocess.check_call(['ssh-keygen', '-t', 'rsa', '-b', '4096',
                               '-N', "",
                               '-f', keyfile,
                               '-C', server_name])
    return f'{keyfile}.pub', keyfile


def ssh(server, **ssh_kwargs):
    helpers.ssh(server, **ssh_kwargs)


def initialize(server, create=False):
    if create:
        set_ssh_key(server)
    roles_manager.initialize(server)


def set_ssh_key(server):
    try:
        authorized_keys = subprocess.check_output([
            'sshpass', '-f', server['passwordfile'],
            'ssh', f'root@{server["public_ip"]}',
            '-o', 'StrictHostKeyChecking=no',
            '--',
            'cat', '.ssh/authorized_keys'
        ]).decode()
    except subprocess.CalledProcessError:
        authorized_keys = None
    if not authorized_keys or server['name'] not in authorized_keys:
        logs.info(f"Adding authorized key for server", server_name=server['name'])
        with open(server['keyfile'] + '.pub') as f:
            public_key = f.read()
        subprocess.check_call([
            'sshpass', '-f', server['passwordfile'], 'ssh', f'root@{server["public_ip"]}',
            '-o', 'StrictHostKeyChecking=no',
            '--',
            'mkdir', '-p', ".ssh"
        ])
        subprocess.check_call(['sshpass', '-f', server['passwordfile'], 'ssh', f'root@{server["public_ip"]}',
                               '-o', 'StrictHostKeyChecking=no',
                               f'echo "{public_key}" > .ssh/authorized_keys'])
        helpers.ssh(server, ["echo successfull ssh connection using key"])


def create_cluster_servers(cluster):
    cluster_id = cluster['id']
    cluster_servers_path = get_cluster_servers_path(cluster_id)
    if not os.path.exists(cluster_servers_path):
        os.mkdir(cluster_servers_path)
    server_defaults = cluster['server_defaults']
    servers = []
    for server in cluster['servers']:
        server['cluster_id'] = cluster_id
        name_template = server.get('name_template', server_defaults['name_template'])
        server_name = server.get('name')
        if not server_name:
            server_name = server['name'] = name_template.format(cluster_id=cluster_id, server_num=server['server_num'])
        for k, v in server_defaults.items():
            if server.get(k) is None:
                server[k] = v
        server_password, server['passwordfile'] = get_server_password(cluster_id, server_name)
        server_info = kamatera_manager.server_info(server_name)
        if not server_info:
            kamatera_manager.create_server(server, server_password)
            server_info = kamatera_manager.server_info(server_name)
        assert len(server_info) == 1
        _, server['keyfile'] = get_server_sshkey(cluster_id, server_name)
        server['public_ip'] = None
        server['private_ip'] = None
        for network in server_info[0]['networks']:
            if network['network'].startswith('wan'):
                assert len(network['ips']) == 1, logs.yaml_dump(server_info)
                assert server['public_ip'] is None
                server['public_ip'] = network['ips'][0]
            else:
                assert len(network['ips']) == 1, logs.yaml_dump(server_info)
                assert server['private_ip'] is None
                server['private_ip'] = network['ips'][0]
        servers.append(server)
        initialize(server, create=True)
    return servers
