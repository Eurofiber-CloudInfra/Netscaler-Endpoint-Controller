import os
import kopf
import pykube
import logging
import requests

from pyfiglet import Figlet

'''
Variables that can be set using environment and defaults
'''
K8S_SSL_VERIFY = bool(os.environ.get('K8S_SSL_VERIFY', 'False'))
FILTER_LABEL_NAME = os.environ.get('FILTER_LABEL_NAME',   'nodepool')
FILTER_LABEL_VALUE = os.environ.get('FILTER_LABEL_VALUE',  'frontend')
DEVELOPMENT = os.environ.get('DEVELOPMENT', 'False').lower() == 'true'
NS_HOST = os.environ.get('NETSCALER_HOST', 'http://localhost:32768')
NS_USERNAME = os.environ.get('NETSCALER_USERNAME',  'nsroot')
NS_PASSWORD = os.environ.get('NETSCALER_PASSWORD',  'nsroot')
NS_SVC_GRP = os.environ.get('NETSCALER_SVC_GRP',   'acdb,ghj').split(',')
NS_SVC_PORT = int(os.environ.get('NETSCALER_SVC_PORT', '80'))
NS_DEFAULT_HEADERS = {'Content-Type': 'application/json'}
NS_FULL_URL = NS_HOST + \
    '/nitro/v1/config/servicegroup_servicegroupmember_binding/'

'''
Default logger scope
'''
logger = logging.getLogger('mm.netscaler.controller')


@kopf.on.event('', 'v1', 'nodes',
               labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
async def my_handler(spec, **_):
    '''
    Handlers for Node events in Kubernetes.
    In case a node is created or deleted the Netscaler pool is updated.
    Support for nodegroup labels is added, to limit nodes.
    '''
    logger.info('Generic node event detected')
    if DEVELOPMENT:
        logger.info(
            'Handling event because of testing without new nodes')
        update_netscaler()


@kopf.on.create('', 'v1', 'nodes',
                labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
def my_update_handler(spec, **_):
    logger.info('Create node detected')
    update_netscaler()


@kopf.on.delete('', 'v1', 'nodes',
                labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
def my_delete_handler(spec, **_):
    logger.info('Delete node detected')
    update_netscaler()


def update_netscaler():
    '''
    Function to update Netscaler setup
    Works independently of the event that starts it so retrieval.
    '''
    api = pykube.HTTPClient(
        pykube.KubeConfig.from_env(), verify=K8S_SSL_VERIFY)
    k8s_nodes = pykube.Node.objects(api).filter(
        selector={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})

    ns_nodes = []
    for servicegroup in NS_SVC_GRP:
        ns_nodes = list(set(ns_nodes+get_from_servicegroup(servicegroup)))

    logger.info("Found "+str(len(ns_nodes))+" bindings on Netscaler")
    logger.debug(ns_nodes)

    k8s_ips = []

    for node in k8s_nodes:
        for address in node.obj["status"]["addresses"]:
            if address["type"] == "ExternalIP":
                external_ip = (address["address"])
                k8s_ips.append(external_ip)
                if external_ip not in ns_nodes:
                    logging.info("Found a new node "+external_ip)
                    for servicegroup in NS_SVC_GRP:
                        logging.info("Adding to servicegroup "+servicegroup)
                        delete_from_servicegroup(servicegroup, external_ip)

    for node in ns_nodes:
        if node not in k8s_ips and len(ns_nodes) > 1:
            logger.info(node+" not found in K8S Nodes, Can be deleted")
            for servicegroup in NS_SVC_GRP:
                delete_from_servicegroup(servicegroup, node)
            logger.info("Nodes deleted")


def get_from_servicegroup(servicegroup):
    r = requests.get(NS_FULL_URL + NS_SVC_GRP,
                     headers=NS_DEFAULT_HEADERS,
                     auth=(NS_USERNAME, NS_PASSWORD))
    ns_nodes = []
    if (r.status_code < 300):
        response = r.json()
        bindings = response["servicegroup_servicegroupmember_binding"]
        for binding in bindings:
            ns_nodes.append(binding["ip"])
            logger.debug("Adding "+binding["ip"])
    else:
        logger.error("Failed to load existing bindings")
        logger.error(r.text)
    return ns_nodes


def add_to_servicegroup(servicegroup, node):
    data = {
        'servicegroup_servicegroupmember_binding': {
            'servicegroupname': NS_SVC_GRP,
            'ip': node,
            'port': NS_SVC_PORT
        }
    }
    r = requests.put(NS_FULL_URL,
                     json=data,
                     headers=NS_DEFAULT_HEADERS,
                     auth=(NS_USERNAME, NS_PASSWORD))
    logger.debug(r.request.body)
    logger.debug(r.status_code)
    logger.debug(r.text)


def delete_from_servicegroup(servicegroup, node):
    r = requests.delete(NS_FULL_URL + servicegroup + "?args=ip:"+node +
                        ",port:"+str(NS_SVC_PORT),
                        headers=NS_DEFAULT_HEADERS,
                        auth=(NS_USERNAME, NS_PASSWORD))
    if r.status_code > 300:
        logger.error("Could not delete the node")
        logger.error(r.text)


'''
Nice initialization header
'''
print('')
custom_fig = Figlet(font='graffiti')
print(custom_fig.renderText('Matrixmind'))
print("Project: Netscaler Endpoint Controller")
print("--------------------------------------")
