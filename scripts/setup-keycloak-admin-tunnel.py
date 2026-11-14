#!/usr/bin/env python3
"""Point only the master realm login at the private HTTPS Admin Console."""

import json
import subprocess

from lab_common import ROOT, admin_session, configuration, request_json


def main():
    config = configuration()
    admin_url = config["services"]["authentication-identity-server"]["environment"].get("KC_HOSTNAME_ADMIN")
    if not admin_url:
        config = json.loads(subprocess.check_output([
            "docker", "compose", "-f", "docker-compose.yml",
            "-f", "api-gateway-proxy-server/compose.lb.yml",
            "-f", "monitoring-prometheus-server/compose.web-metrics.yml",
            "-f", "authentication-identity-server/compose.admin-tunnel.yml",
            "config", "--format", "json",
        ], cwd=ROOT, text=True))
        admin_url = config["services"]["authentication-identity-server"]["environment"].get("KC_HOSTNAME_ADMIN")
    if not admin_url or not admin_url.startswith("https://"):
        raise RuntimeError("Enable compose.admin-tunnel.yml with an HTTPS admin URL")
    base, token = admin_session(config)
    realm_url = base + "/admin/realms/master"
    status, realm = request_json(realm_url, token=token)
    if status != 200:
        raise RuntimeError(f"Cannot read master realm (HTTP {status})")
    attributes = realm.setdefault("attributes", {})
    if attributes.get("frontendUrl") == admin_url:
        print("PASS master realm already uses the private HTTPS admin URL")
        return
    attributes["frontendUrl"] = admin_url
    status, _ = request_json(realm_url, method="PUT", data=realm, token=token)
    if status != 204:
        raise RuntimeError(f"Cannot update master realm frontend URL (HTTP {status})")
    print("PASS master realm frontend URL set to private HTTPS admin URL")


if __name__ == "__main__":
    main()
