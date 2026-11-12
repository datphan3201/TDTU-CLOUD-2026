#!/usr/bin/env python3
"""Explicit lab tests: temporary row change, DB interruption and DB/auth recreate.

Run only against the local demonstration stack. Keeps named volumes and restores
the test row and stopped DB in finally blocks. May briefly interrupt requests.
"""
import time
from urllib.parse import quote

from lab_common import compose, configuration, database_sql, environment, gateway_url, request_json


def wait_for(url, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            status, body = request_json(url)
            if status == 200:
                return body
        except OSError:
            pass
        time.sleep(2)
    raise RuntimeError("Service did not recover before timeout")


def main():
    base = gateway_url(configuration())
    url = base + "/api/students-db"
    before = wait_for(url)
    row = next(item for item in before if item["student_id"] == "DEMO001")
    row_id = int(row["id"])
    original = row["fullname"].encode().hex()
    changed_name = row["fullname"] + " [live-check]"
    changed = changed_name.encode().hex()
    try:
        database_sql(f"UPDATE studentdb.students SET fullname=CONVERT(0x{changed} USING utf8mb4) WHERE id={row_id};")
        status, live = request_json(url)
        assert status == 200 and next(r for r in live if r["id"] == row_id)["fullname"] == changed_name
        print("PASS APP-02 API reflects a committed database UPDATE", flush=True)
    finally:
        database_sql(f"UPDATE studentdb.students SET fullname=CONVERT(0x{original} USING utf8mb4) WHERE id={row_id};")
    try:
        compose("stop", "relational-database-server")
        status, body = request_json(url)
        assert status == 503 and body == {"error": "database_unavailable"}
        print("PASS APP-02 actual DB outage returns sanitized 503", flush=True)
    finally:
        compose("start", "relational-database-server")
    assert wait_for(url) == before
    print("PASS APP-02 recovers automatically after DB restart", flush=True)
    compose("up", "-d", "--force-recreate", "--no-deps", "relational-database-server", "authentication-identity-server")
    assert wait_for(url) == before
    print("PASS DB-01 data persists after database recreate", flush=True)
    realm = "realm_" + environment()["STUDENT_ID"]
    discovery = wait_for(base + "/auth/realms/" + quote(realm, safe="") + "/.well-known/openid-configuration")
    for user in ("sv01", "sv02"):
        status, token = request_json(discovery["token_endpoint"], method="POST", form={
            "client_id": "flask-app", "grant_type": "password", "username": user,
            "password": environment()["KEYCLOAK_DEMO_PASSWORD"],
        })
        assert status == 200
        status, body = request_json(base + "/api/secure", token=token["access_token"])
        assert status == 200 and body["username"] == user
    print("PASS AUTH-01 realm, client and both user credentials persist after recreate", flush=True)


if __name__ == "__main__":
    main()
