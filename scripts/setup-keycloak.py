#!/usr/bin/env python3
"""Create/update the lab realm and client without deleting existing realm data."""
import argparse
import json
import re
import secrets
from urllib.parse import quote, urlencode

from lab_common import ROOT, admin_session, configuration, environment, request_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset-demo-passwords", action="store_true", help="Explicitly reset passwords of existing sv01/sv02")
    args = parser.parse_args()
    config = configuration()
    env = environment()
    student_id = env.get("STUDENT_ID", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", student_id) or student_id == "CHANGE_ME":
        raise SystemExit("Set STUDENT_ID in .env first (letters, digits, underscore or hyphen)")
    password = env.get("KEYCLOAK_DEMO_PASSWORD")
    if not password:
        password = secrets.token_urlsafe(24)
        with (ROOT / ".env").open("a") as file:
            file.write("\n# Generated local-only password for sv01 and sv02\nKEYCLOAK_DEMO_PASSWORD=" + password + "\n")
        print("Generated KEYCLOAK_DEMO_PASSWORD in ignored .env (value not displayed)")
    realm = "realm_" + student_id
    definition = json.loads((ROOT / "authentication-identity-server/realm.template.json").read_text())
    definition["realm"] = realm
    base, token = admin_session(config)
    realm_path = base + "/admin/realms/" + quote(realm, safe="")

    def call(url, method="GET", data=None, expected=(200, 201, 204)):
        status, body = request_json(url, method, data=data, token=token)
        if status not in expected:
            raise RuntimeError(f"Keycloak setup failed: {method} HTTP {status}")
        return body

    status, _ = request_json(realm_path, token=token)
    if status == 404:
        # Create only realm settings here; create managed users separately to set passwords once.
        settings = {k: v for k, v in definition.items() if k not in ("clients", "users")}
        call(base + "/admin/realms", "POST", settings)
    elif status != 200:
        raise RuntimeError(f"Cannot inspect realm (HTTP {status})")
    for client in definition["clients"]:
        clients_url = realm_path + "/clients"
        existing = call(clients_url + "?" + urlencode({"clientId": client["clientId"]}))
        if existing:
            call(clients_url + "/" + existing[0]["id"], "PUT", client)
        else:
            call(clients_url, "POST", client)
    for user in definition["users"]:
        users_url = realm_path + "/users"
        existing = call(users_url + "?" + urlencode({"username": user["username"], "exact": "true"}))
        created = not existing
        if created:
            call(users_url, "POST", user)
            existing = call(users_url + "?" + urlencode({"username": user["username"], "exact": "true"}))
        user_url = users_url + "/" + existing[0]["id"]
        credentials = call(user_url + "/credentials")
        needs_password = not any(credential.get("type") == "password" for credential in credentials)
        if created or needs_password or args.reset_demo_passwords:
            call(user_url + "/reset-password", "PUT", {"type": "password", "temporary": False, "value": password})
        print("PASS managed lab user " + user["username"] + (" created" if created else " preserved"))
    # Declarative export contains no passwords, tokens or realm private keys.
    export_path = ROOT / "authentication-identity-server/import" / ("realm-" + student_id + ".json")
    export_path.parent.mkdir(exist_ok=True)
    export_path.write_text(json.dumps(definition, ensure_ascii=False, indent=2) + "\n")
    print("PASS AUTH-01 realm, public client and audience mapper configured; no secrets exported")


if __name__ == "__main__":
    main()
