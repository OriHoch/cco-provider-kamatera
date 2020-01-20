from ...helpers import ssh


def initialize(server, role):
    ssh(server, [
        "if ! [ -e /srv/default/hello.txt ]; then \
            apt-get update && apt-get install -y nfs-kernel-server && \
            mkdir -p /srv/default && echo Hello from Kamatera > /srv/default/hello.txt && \
            chown -R nobody:nogroup /srv/default/ && chmod 777 /srv/default/; \
        fi && \
        echo '/srv/default 172.16.0.0/23(rw,sync,no_subtree_check,no_root_squash)' > /etc/exports && \
        exportfs -a && \
        systemctl restart nfs-kernel-server"
    ])
