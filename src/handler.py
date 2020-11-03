import os
import kopf
import pykube
import logging
import requests

from pyfiglet import Figlet

'''
Variables that can be set using environment and default
'''
NETSCALER_HOST      = os.environ.get('NETSCALER_HOST',      'http://localhost:32768')
NETSCALER_USERNAME  = os.environ.get('NETSCALER_USERNAME',  'nsroot')
NETSCALER_PASSWORD  = os.environ.get('NETSCALER_PASSWORD',  'nsroot')
NETSCALER_SVC_GRP   = os.environ.get('NETSCALER_SVC_GRP',   'acdb')
NETSCALER_SVC_PORT  = int(os.environ.get('NETSCALER_SVC_PORT', '80'))
K8S_SSL_VERIFY      = bool(os.environ.get('K8S_SSL_VERIFY', 'False'))
FILTER_LABEL_NAME   = os.environ.get('FILTER_LABEL_NAME',   'nodepool')
FILTER_LABEL_VALUE  = os.environ.get('FILTER_LABEL_VALUE',  'frontend')
DEVELOPMENT = os.environ.get('DEVELOPMENT', 'False').lower() == 'true'

'''
Default logger scope
'''
logger = logging.getLogger('mm.netscaler.controller')

'''
Handlers for Node events in Kubernetes.
In case a node is created or deleted the Netscaler pool is updated.
To ensure only nodes added can be limited, support for nodegroup labels is added.
'''
@kopf.on.event('', 'v1', 'nodes', labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
async def my_handler(spec, **_):
    logger.info('Generic node event detected')
    if DEVELOPMENT:
        logger.info(
            'Handling generic event because of development testing without new nodes needed')
        update_netscaler()


@kopf.on.create('', 'v1', 'nodes', labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
def my_handler(spec, **_):
    logger.info('Create node detected')
    update_netscaler()


@kopf.on.delete('', 'v1', 'nodes', labels={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})
def my_handler(spec, **_):
    logger.info('Delete node detected')
    update_netscaler()

'''
Function to update Netscaler setup
Works independently of the event that starts it so retrieves all the information needed.
'''
def update_netscaler():

    api = pykube.HTTPClient(
        pykube.KubeConfig.from_env(), verify=K8S_SSL_VERIFY)
    k8s_nodes = pykube.Node.objects(api).filter(selector={FILTER_LABEL_NAME: FILTER_LABEL_VALUE})

    ns_nodes = []
    headers = {'Content-Type' : 'application/json'}
    r = requests.get(NETSCALER_HOST+'/nitro/v1/config/servicegroup_servicegroupmember_binding/'+NETSCALER_SVC_GRP,
                     headers=headers, auth=(NETSCALER_USERNAME, NETSCALER_PASSWORD))

    if (r.status_code < 300):
        response = r.json()
        bindings = response["servicegroup_servicegroupmember_binding"]
        for binding in bindings:
            ns_nodes.append(binding["ip"])
            logger.debug("Adding "+binding["ip"])
    else:
        logger.error("Failed to load existing bindings")
        logger.error(r.text)

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
                    data = {
                        'servicegroup_servicegroupmember_binding': {
                            'servicegroupname': NETSCALER_SVC_GRP,
                            'ip': external_ip,
                            'port': NETSCALER_SVC_PORT
                        }
                    }
                    r = requests.put(NETSCALER_HOST+'/nitro/v1/config/servicegroup_servicegroupmember_binding',
                                     json = data, 
                                     headers = headers, 
                                     auth = (NETSCALER_USERNAME, NETSCALER_PASSWORD))
                    
                    logger.debug(r.request.body)
                    logger.debug(r.status_code)
                    logger.debug(r.text)

    for node in ns_nodes:   
        if node not in k8s_ips and len(ns_nodes) > 1:
            logger.info(node+" not found in K8S Nodes, Can be deleted")
            params={'args': "ip:"+node}
            r = requests.delete(NETSCALER_HOST+'/nitro/v1/config/servicegroup_servicegroupmember_binding/'+\
                                NETSCALER_SVC_GRP+"?args=ip:"+node+",port:"+str(NETSCALER_SVC_PORT),
                             headers=headers,
                             auth=(NETSCALER_USERNAME, NETSCALER_PASSWORD))
            if r.status_code > 300:
                logger.error("Could not delete the node")
                logger.error(r.text)
            logger.info("Node deleted")


'''
Nice initialization header
'''
print('')
custom_fig = Figlet(font='graffiti')
print(custom_fig.renderText('Matrixmind'))
print("Project: Netscaler Endpoint Controller")
print("--------------------------------------")
