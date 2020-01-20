import click
from ckan_cloud_operator import logs
from . import manager


@click.group()
def cluster():
    pass


@cluster.command()
@click.option('--values-yaml')
def create(values_yaml):
    """Create a Kamatera cluster using given values yaml file"""
    manager.create(values_yaml)


@cluster.command()
@click.argument('CLUSTER_ID')
@click.option('--skip-server-init', is_flag=True)
@click.option('--dry-run', is_flag=True)
def initialize(cluster_id, skip_server_init, dry_run):
    manager.initialize(cluster_id, skip_server_init, dry_run)
