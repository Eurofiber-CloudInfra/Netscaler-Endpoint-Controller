#!/bin/bash

#check if kopf installed

docker run -e EULA=yes -dt -p 22 -p 80 -p 161/udp --ulimit core=-1 --cap-add=NET_ADMIN store/citrix/netscalercpx:12.0-56.20

kopf src/handler.py --verbose