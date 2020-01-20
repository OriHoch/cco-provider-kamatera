import click
from . import manager
from .helpers import get_server


@click.group()
def server():
    pass


@server.command()
@click.argument('CLUSTER_ID')
@click.argument('SERVER_NAME')
@click.argument('COMMAND', nargs=-1, required=False)
def ssh(cluster_id, server_name, command):
    manager.ssh(get_server(cluster_id, server_name), cmd=[' '.join(command)] if command else [])


@server.command()
@click.argument('CLUSTER_ID')
@click.argument('SERVER_NAME')
def initialize(cluster_id, server_name):
    manager.initialize(get_server(cluster_id, server_name))
