import os
from ruamel import yaml
from ckan_cloud_operator.providers import helpers as providers_helpers
from .constants import PROVIDER_SUBMODULE, PROVIDER_ID
(
    _config_interactive_set, _config_get, _config_set, _set_provider, _get_resource_annotations,
    _get_resource_labels, _get_resource_name
) = providers_helpers.get_provider_functions(PROVIDER_SUBMODULE, PROVIDER_ID)
from .cluster import manager as cluster_manager
from .kamatera import manager as kamatera_manager


def initialize(interactive=False):
    _set_provider()
    interactive_file = os.environ.get('CCO_INTERACTIVE_CI')
    assert interactive_file
    answers = yaml.safe_load(open(interactive_file))
    _config_set(values={
        'kamatera_api_client_id': answers['kamatera']['api_client_id'],
        'kamatera_api_secret': answers['kamatera']['api_secret'],
        'kamatera_api_server': answers['kamatera']['api_server'],
    }, is_secret=True)
    print(yaml.dump(get_info(), default_flow_style=False))


def get_info(debug=False):
    cluster = cluster_manager.get_cluster()
    servers_info = []
    for server in cluster['servers']:
        servers_info.append(kamatera_manager.server_info(server['name'])[0])
    return {
        'cluster': cluster,
        'servers': servers_info
    }
