#!/usr/bin/env bash

echo Install cloudcli
curl -o cloudcli.tar.gz https://cloudcli.cloudwm.com/binaries/${CLOUDCLI_VERSION}/cloudcli-linux-amd64.tar.gz && \
tar -xzvf cloudcli.tar.gz && chmod +x cloudcli && mv cloudcli /usr/local/bin/ && cloudcli version
