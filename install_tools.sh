#!/usr/bin/env bash

echo Install cloudcli &&\
curl -o cloudcli.tar.gz https://cloudcli.cloudwm.com/binaries/${CLOUDCLI_VERSION}/cloudcli-linux-amd64.tar.gz && \
tar -xzvf cloudcli.tar.gz && chmod +x cloudcli && mv cloudcli /usr/local/bin/ &&\
cloudcli --api-clientid _ --api-secret _ --api-server https://cloudcli.cloudwm.com version &&\
echo Install cco-provider-kamatera &&\
pip install -e /usr/local/lib/cco/${K8_PROVIDER} &&\
echo Install additional packages &&\
apt-get update && apt-get install -y sshpass &&\
( apt-get install -y ssh-tools || apt-get install -y openssh-client ) &&\
echo Install RKE &&\
curl -Lo /usr/local/bin/rke https://github.com/rancher/rke/releases/download/${RKE_VERSION}/rke_linux-amd64 &&\
chmod +x /usr/local/bin/rke &&\
rke --version &&\
curl -Lo /usr/local/lib/cco/rancher_install_docker.sh https://releases.rancher.com/install-docker/${INSTALL_DOCKER_VERSION}.sh &&\
echo ${INSTALL_DOCKER_VERSION} > /usr/local/lib/cco/rancher_install_docker_version
