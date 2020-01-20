from ...helpers import ssh, scp_to_server
from ckan_cloud_operator import logs


SSHD_CONFIG = """# cco-provider-kamatera managed config
Port 22
PermitRootLogin yes
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem       sftp    /usr/lib/openssh/sftp-server
AllowTcpForwarding yes
"""


def initialize(server, role):
    assert role == 'rke-node'
    try:
        ssh(server, ["""
            mkdir -p /usr/local/lib/cco &&\
            ls -lah /usr/local/lib/cco/rancher_install_docker.sh
        """])
    except Exception:
        scp_to_server(server, '/usr/local/lib/cco/rancher_install_docker.sh')
    lsmod = ssh(server, ["lsmod"], method="check_output").decode()
    lsmods = [line.split(' ')[0] for line in lsmod.split("\n") if len(line) > 0]
    missing_mods = []
    for mod in "br_netfilter ip6_udp_tunnel ip_set ip_set_hash_ip ip_set_hash_net iptable_filter iptable_nat iptable_mangle iptable_raw nf_conntrack_netlink nf_conntrack nf_conntrack_ipv4   nf_defrag_ipv4 nf_nat nf_nat_ipv4 nf_nat_masquerade_ipv4 nfnetlink udp_tunnel veth vxlan x_tables xt_addrtype xt_conntrack xt_comment xt_mark xt_multiport xt_nat xt_recent xt_set  xt_statistic xt_tcpudp".split(" "):
        if len(mod) < 1: continue
        if mod not in lsmods:
            missing_mods.append(mod)
    for missing_mod in missing_mods:
        logs.info("installing missing mod", missing_mod=missing_mod)
        ssh(server, [f"echo {missing_mod} >> /etc/modules && modprobe {missing_mod}"])
    lsmod = ssh(server, ["lsmod"], method="check_output").decode()
    lsmods = [line.split(' ')[0] for line in lsmod.split("\n") if len(line) > 0]
    missing_mods = []
    for mod in "br_netfilter ip6_udp_tunnel ip_set ip_set_hash_ip ip_set_hash_net iptable_filter iptable_nat iptable_mangle iptable_raw nf_conntrack_netlink nf_conntrack nf_conntrack_ipv4   nf_defrag_ipv4 nf_nat nf_nat_ipv4 nf_nat_masquerade_ipv4 nfnetlink udp_tunnel veth vxlan x_tables xt_addrtype xt_conntrack xt_comment xt_mark xt_multiport xt_nat xt_recent xt_set  xt_statistic xt_tcpudp".split(" "):
        if len(mod) < 1: continue
        if mod not in lsmods:
            missing_mods.append(mod)
    if missing_mods:
        logs.error(missing_mods=missing_mods)
        exit(1)
    sysctlconf = ssh(server, ["cat", "/etc/sysctl.conf"], method="check_output").decode()
    if 'net.bridge.bridge-nf-call-iptables = 1' not in sysctlconf:
        ssh(server, ["echo net.bridge.bridge-nf-call-iptables = 1 >> /etc/sysctl.conf"])
        ssh(server, ["sysctl", "-p"])
    sshdconfig = ssh(server, ["cat", "/etc/ssh/sshd_config"], method="check_output").decode()
    if 'cco-provider-kamatera managed config' not in sshdconfig:
        ssh(server, [f'echo "{SSHD_CONFIG}" > /etc/ssh/sshd_config'])
