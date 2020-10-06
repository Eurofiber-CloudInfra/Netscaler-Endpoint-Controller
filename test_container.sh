#!/bin/bash

if [ -z "$KUBECONFIG" ]; then
    export KUBECONFIG="~/.kube/config"
fi

docker build -t mm/netscaler .
docker run -v $KUBECONFIG:/root/.kube/config mm/netscaler
