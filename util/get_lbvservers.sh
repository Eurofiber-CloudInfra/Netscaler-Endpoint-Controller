#!/bin/bash

echo "Retrieving Loadbalancers"
curl -H "X-NITRO-USER: nsroot" -H "X-NITRO-PASS: nsroot" -H "Content-Type:application/json"  http://localhost:32768/nitro/v1/config/