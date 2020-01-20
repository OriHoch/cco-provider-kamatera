import click
import os
from .cluster import cli as cluster_cli
from .server import cli as server_cli


CLICK_CLI_MAX_CONTENT_WIDTH = 200


@click.group(context_settings={'max_content_width': CLICK_CLI_MAX_CONTENT_WIDTH})
@click.option('--debug', is_flag=True)
def main(debug):
    """Ckan Cloud Operator provider for Kamatera"""
    if debug:
        os.environ.setdefault('CKAN_CLOUD_OPERATOR_DEBUG', 'y')
    pass


main.add_command(cluster_cli.cluster)
main.add_command(server_cli.server)


if __name__ == '__main__':
    main()
