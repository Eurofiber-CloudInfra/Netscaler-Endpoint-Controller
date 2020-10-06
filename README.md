# Netscaler Endpoint Controller

A Kubernetes controller that registers nodes with predefined labels with the Netscaler to ensure transparent registration.

## Run on Kubernetes

In order to run it on Kubernetes ensure you have the correct ServiceAccount created.

## Manual Actions

Commands below can be tested on a local test environment. For remote replace hostname, port, username and password.

On the Netscaler you have a virtual server (lbvserver), services and servicegroups.

In order to test integration and for troubleshooting the following manual commands can be used:

```bash
curl -H "X-NITRO-USER: nsroot" -H "X-NITRO-PASS: nsroot" -H "Content-Type:application/json"  http://localhost:32768/nitro/v1/config/
```

This lists a set of possible configuration items that can be traversed.

### Create a loadbalancer configuration

```bash
curl -d '{ "lbvserver": { "name":"Test123", "servicetype":"http" }}' -H "X-NITRO-USER: nsroot" -H "X-NITRO-PASS: nsroot" -H "Content-Type:application/json"  http://localhost:32768/nitro/v1/config/lbvserver
```

No response if ok, only 200 HTTP response. Remember that it is not enabled yet.
Enabling works through adding ?enable=true

```bash
curl -H "X-NITRO-USER: nsroot" -H "X-NITRO-PASS: nsroot" -H "Content-Type:application/json" "http://localhost:32768/nitro/v1/config/lbvserver/Test123?action=enable
```

### List All Loadbalancers

```bash
curl -H "X-NITRO-USER: nsroot" -H "X-NITRO-PASS: nsroot" -H "Content-Type:application/json"  http://localhost:32768/nitro/v1/config/lbvserver 
```

output:

```json
{
	"errorcode": 0,
	"message": "Done",
	"severity": "NONE",
	"lbvserver": [{
		"name": "Test123",
		"insertvserveripport": "OFF",
		"ipv46": "0.0.0.0",
		"ippattern": "0.0.0.0",
		"ipmask": "*",
		"listenpolicy": "NONE",
		"ipmapping": "0.0.0.0",
		"port": 0,
		"range": "1",
		"servicetype": "HTTP",
		"type": "ADDRESS",
		"curstate": "DOWN",
		"effectivestate": "DOWN",
		"status": 0,
		"lbrrreason": 0,
		"cachetype": "SERVER",
		"authentication": "OFF",
		"authn401": "OFF",
		"dynamicweight": "0",
		"priority": "0",
		"clttimeout": "180",
		"somethod": "NONE",
		"sopersistence": "DISABLED",
		"sopersistencetimeout": "2",
		"healththreshold": "0",
		"lbmethod": "LEASTCONNECTION",
		"backuplbmethod": "ROUNDROBIN",
		"dataoffset": "0",
		"health": "0",
		"datalength": "0",
		"ruletype": "0",
		"m": "IP",
		"persistencetype": "NONE",
		"timeout": 2,
		"persistmask": "255.255.255.255",
		"v6persistmasklen": "128",
		"persistencebackup": "NONE",
		"cacheable": "NO",
		"rtspnat": "OFF",
		"sessionless": "DISABLED",
		"trofspersistence": "ENABLED",
		"map": "OFF",
		"connfailover": "DISABLED",
		"redirectportrewrite": "DISABLED",
		"downstateflush": "ENABLED",
		"disableprimaryondown": "DISABLED",
		"gt2gb": "DISABLED",
		"consolidatedlconn": "GLOBAL",
		"consolidatedlconngbl": "YES",
		"thresholdvalue": 0,
		"invoke": false,
		"version": 0,
		"totalservices": "0",
		"activeservices": "0",
		"statechangetimesec": "Tue Oct  6 12:51:41 2020",
		"statechangetimeseconds": "1601988701",
		"statechangetimemsec": "90",
		"tickssincelaststatechange": "5691",
		"hits": "0",
		"pipolicyhits": "0",
		"push": "DISABLED",
		"pushlabel": "none",
		"pushmulticlients": "NO",
		"policysubtype": "0",
		"l2conn": "OFF",
		"appflowlog": "ENABLED",
		"isgslb": false,
		"icmpvsrresponse": "PASSIVE",
		"rhistate": "PASSIVE",
		"newservicerequestunit": "PER_SECOND",
		"vsvrbindsvcip": "0.0.0.0",
		"vsvrbindsvcport": 0,
		"skippersistency": "None",
		"td": "0",
		"minautoscalemembers": "0",
		"maxautoscalemembers": "0",
		"macmoderetainvlan": "DISABLED",
		"dns64": "DISABLED",
		"bypassaaaa": "NO",
		"processlocal": "DISABLED",
		"vsvrdynconnsothreshold": "0",
		"retainconnectionsoncluster": "NO"
	}]
}
```

### Checking statistics on a Loadbalancer

```bash
curl -H "X-NITRO-USER: nsroot" -H "X-NITRO-PASS: nsroot" -H "Content-Type:application/json" "http://localhost:32768/nitro/v1/stat/lbvserver/Test123?statbindings=yes
```

