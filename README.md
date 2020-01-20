# cco-provider-kamatera

ckan-cloud-operator custom provider for Kamatera

Check [ckan-cloud-operator docs](https://github.com/datopian/ckan-cloud-operator/blob/master/README.md) for details.

## Create the custom provider values file:

```
kamatera:
  api_client_id: ""
  api_secret: ""
  api_server: "https://cloudcli.cloudwm.com"
  cluster:
    id: "mycluster"
    server_defaults:
      name_template: "{cluster_id}-node-{server_num}"
      billingcycle: "hourly"
      cpu: "4T"
      ram: "8192"
      dailybackup: "no"
      datacenter: "IL"
      disk:
        - "size=100"
      image: "IL:6000C2904fc6d8295d2b6d9687ed955e"
      managed: "no"
      poweronaftercreate: "yes"
      monthlypackage: ""
      network:
        - "name=wan,ip=auto"
        - "name=lan-82145-mylan,ip=auto"
    servers:
      - server_num: 1
        roles: ["nfs", "rke-node"]
        cpu: "1D"
        ram: "1024"
        rke-node:
          role: ["controlplane", "etcd"]
      - server_num: 2
        roles: ["rke-node"]
        rke-node:
          role: ["worker"]
```

Save it under `.cco/interactive.yaml` (so it is available inside the ckan-cloud-operator under /root)

Start a Bash shell inside the ckan-cloud-operator Docker image (see the docs)

Run the following inside this Bash shell:

```
cco-provider-kamatera cluster create
```
