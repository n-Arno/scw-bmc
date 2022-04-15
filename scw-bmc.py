#!/usr/bin/python3

import sys, os, requests, json


def myip():
    return requests.get("https://api.ipify.org?format=json").json()


def do(method, endpoint, body=None):
    scw_url = "https://api.scaleway.com"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Auth-Token": os.environ.get("SCW_SECRET_KEY"),
    }
    response = requests.request(
        method,
        "/".join([scw_url, endpoint]),
        json=body,
        headers=headers,
    )
    if not str(response.status_code).startswith("2"):
        print(f"ERROR {response.status_code}: {response.text} on {method} {endpoint}")
        sys.exit(1)
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        return response.text


def _status(id):
    r = do("GET", f"baremetal/v1/zones/fr-par-2/servers/{id}")
    offer_id = r["offer_id"]
    activated = [o for o in r["options"] if o["name"] == "Remote Access"]
    r = do("GET", f"baremetal/v1/zones/fr-par-2/offers/{offer_id}")
    possible = [o for o in r["options"] if o["name"] == "Remote Access"]
    if possible:
        return True if activated else False
    else:
        return None


def status(id):
    s = _status(id)
    if s is not None:
        print(f'Remote Access option is { "" if s else "not " }activated')
    else:
        print("Remote Access is not possible for this server")


def stop(id, verbose=True):
    s = _status(id)
    if s:
        do("DELETE", f"baremetal/v1/zones/fr-par-2/servers/{id}/bmc-access")
        r = do("GET", f"baremetal/v1/zones/fr-par-2/servers/{id}")
        offer_id = r["offer_id"]
        r = do("GET", f"baremetal/v1/zones/fr-par-2/offers/{offer_id}")
        option_id = [o for o in r["options"] if o["name"] == "Remote Access"][0]["id"]
        do("DELETE", f"baremetal/v1/zones/fr-par-2/servers/{id}/options/{option_id}")
        if verbose:
            print("Done")


def start(id):
    s = _status(id)
    if s is None:
        print("Remote Access is not possible for this server")
        sys.exit(1)
    if s:
        stop(id, verbose=False)
    r = do("GET", f"baremetal/v1/zones/fr-par-2/servers/{id}")
    offer_id = r["offer_id"]
    r = do("GET", f"baremetal/v1/zones/fr-par-2/offers/{offer_id}")
    option_id = [o for o in r["options"] if o["name"] == "Remote Access"][0]["id"]
    do("POST", f"baremetal/v1/zones/fr-par-2/servers/{id}/options/{option_id}", body={})
    r = do("POST", f"baremetal/v1/zones/fr-par-2/servers/{id}/bmc-access", body=myip())
    print(
        f"URL: {r['url']}\nLOGIN: {r['login']}\nPASSWORD: {r['password']}\nEXPIRATION: {r['expires_at']}"
    )


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ["start", "stop", "status"]:
        print(f"Usage: {sys.argv[0]} <start|stop|status> <id>")
        sys.exit(1)
    if not os.environ.get("SCW_SECRET_KEY"):
        print("Please set the SCW_SECRET_KEY environment variable")
        sys.exit(1)
    if sys.argv[1] == "start":
        start(sys.argv[2])
    elif sys.argv[1] == "stop":
        stop(sys.argv[2])
    else:
        status(sys.argv[2])
    sys.exit(0)


if __name__ == "__main__":
    main()
