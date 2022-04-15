Scaleway BMC access
===================

Quick python helper to access Elastic Metal BMC until Scaleway CLI and console are available to do so.

IMPORTANT: Please note this start a paid option on your Elastic Metal server (0,99€ per hour) which needs to be stopped to avoid extra billing.

Usage:
```
$ export SCW_SECRET_KEY=<scaleway api key>
$ ./scw-bmc.py status <EM server id>
Remote Access option is not activated

$ ./scw-bmc.py start <EM server id>
URL: https://<bmc url>/
LOGIN: <username>
PASSWORD: <password>
EXPIRATION: <access expire 30 minutes after start>

$ ./scw-bmc.py status <EM server id>
Remote Access option is activated

$ ./scw-bmc.py stop <EM server id>
Done
```

