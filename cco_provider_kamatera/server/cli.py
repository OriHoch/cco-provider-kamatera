import click
from . import manager
from .helpers import get_server, get_cluster
from ckan_cloud_operator import logs


@click.group()
def server():
    pass


@server.command()
@click.argument('NODE_NAME')
@click.argument('COMMAND', nargs=-1, required=False)
def ssh(node_name, command):
    manager.ssh(get_server(node_name=node_name), cmd=[' '.join(command)] if command else [])


@server.command()
@click.argument('NODE_NAME')
def initialize(node_name):
    manager.initialize(get_server(node_name=node_name))


@server.command('list')
def _list():
    for server in get_cluster()['servers']:
        logs.print_yaml_dump([{
            'specs': f'datacenter={server["datacenter"]},cpu={server["cpu"]},ram={server["ram"]},disk={", ".join(server["disk"])}',
            'name': server['name'],
            'private_ip': server['private_ip'],
            'public_ip': server['public_ip'],
            'rke-node-role': ', '.join(server['rke-node']['role'])
        }])
