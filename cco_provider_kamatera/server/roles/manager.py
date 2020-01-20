from .nfs import manager as nfs_manager
from .rke import manager as rke_manager


def initialize(server):
    for role in server['roles']:
        {
            'nfs': nfs_manager,
            'rke-node': rke_manager
        }[role].initialize(server, role)
