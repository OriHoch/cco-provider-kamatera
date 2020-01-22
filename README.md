# cco-provider-kamatera

ckan-cloud-operator custom provider for Kamatera

See [ckan-cloud-operator docs](https://github.com/datopian/ckan-cloud-operator/blob/master/README.md) for more details.

## Creating a cluster

Create a directory to hold cluster values and secrets under current working directory:

```
mkdir .cco
```

Create the following file at `.cco/interactive.yaml`

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
default:
  config:
    cluster-init:
      ckan-cloud-operator-image: orihoch/ckan-cloud-operator:kamatera-latest
      components:
        - labels
        - cluster
        - crds
```

Start the working environment

```
docker run -it -v $PWD/.cco:/root/ orihoch/ckan-cloud-operator:kamatera-latest
```

This starts a Bash shell where you can run ckan cloud operator commands

Create the cluster:
 
```
cco-provider-kamatera cluster create
```

You can run this command multiple times in case of failures.

Once it's done, edit `interactive.yaml` and remove the cluster key

All the cluster settings now reside in `.cco/cluster-MYCLUSTER/cluster.json`

Connect to the Kubernetes cluster (from inside the cco working environment):

```
export KUBECONFIG=$HOME/cluster-MYCLUSTER/kube_config_rke-cluster.yml
kubectl get nodes
```

list servers:

```
cco-provider-kamatera server list
```

ssh to a server:

```
cco-provider-kamatera server ssh node-1
```

## Initializing ckan-cloud-operator

```
CCO_INTERACTIVE_CI=$HOME/interactive.yaml ckan-cloud-operator cluster initialize --cluster-provider=custom-kamatera 
```
