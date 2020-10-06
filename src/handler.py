import kopf
import pykube
import os

'''
Variables that can be set using environment
'''
NETSCALER_HOST = os.environ.get('NETSCALER_HOST', 'localhost:32768')
NETSCALER_USERNAME = os.environ.get('NETSCALER_USERNAME', 'nsroot')
NETSCALER_PASSWORD = os.environ.get('NETSCALER_PASSWORD', 'nsroot')
NETSCALER_SRVGRP = os.environ.get('NETSCALER_SRVGRP', 'acdb')

FILTER_LABEL_NAME = os.environ.get('FILTER_LABEL_NAME', 'nodegroup')
FILTER_LABEL_VALUE = os.environ.get('FILTER_LABEL_VALUE', 'mgt')

'''
Handlers for Node events in Kubernetes.
In case a node is created or deleted the Netscaler pool is updated.
To ensure only nodes added can be limited, support for nodegroup labels is added.
'''
@kopf.on.event('', 'v1', 'nodes', labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
async def my_handler(spec, **_):
    print('Node Event')
    update_netscaler()


@kopf.on.create('', 'v1', 'nodes', labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
def my_handler(spec, **_):
    print('Node Created')
    # record last created for deduplication
    update_netscaler()
    pass


@kopf.on.delete('', 'v1', 'nodes', labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
def my_handler(spec, **_):
    print('Node Deleted')
    # record last deleted for deduplication
    update_netscaler()
    pass


def update_netscaler():
    # read list of nodes from the correct
    api = pykube.HTTPClient(pykube.KubeConfig.from_env())
    k8s_nodes = pykube.Node.objects(api)
    # read list of nodes in Netscaler (servers in servicegroup)
    ns_nodes = ['']

    for node in k8s_nodes:
        print(node)
        #check if in Netscaler list
        #if not add
        pass

    for node in ns_nodes:   
        # check if in k8s_nodes list
        # if not delete
        pass

    # Adding protections against 'emptying the lb pool ??'
