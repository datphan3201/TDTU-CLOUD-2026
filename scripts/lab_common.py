"""Host-side lab helpers. Never print Compose output containing credentials."""
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent


def compose(*args, input=None):
    return subprocess.check_output(
        ["docker", "compose", *args], cwd=ROOT, input=input, text=True,
    )


def configuration():
    return json.loads(compose("config", "--format", "json"))


def environment():
    return dict(line.split("=", 1) for line in compose("config", "--environment").splitlines() if "=" in line)


def gateway_url(config):
    return config["services"]["authentication-identity-server"]["environment"]["KC_HOSTNAME"].removesuffix("/auth").rstrip("/")


def request_json(url, method="GET", data=None, token=None, form=None):
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    if form is not None:
        from urllib.parse import urlencode
        body = urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            return response.status, json.loads(content) if content else None
    except urllib.error.HTTPError as exc:
        # Keep parsed errors for assertions; callers must not log raw auth bodies.
        try:
            body = json.loads(exc.read(1048576))
        except (ValueError, OSError):
            body = None
        return exc.code, body


def admin_session(config):
    auth = config["services"]["authentication-identity-server"]
    port = auth["ports"][0]["published"]
    base = os.environ.get("KEYCLOAK_ADMIN_URL", f"http://127.0.0.1:{port}/auth").rstrip("/")
    env = auth["environment"]
    status, data = request_json(base + "/realms/master/protocol/openid-connect/token", method="POST", form={
        "client_id": "admin-cli", "grant_type": "password",
        "username": env["KC_BOOTSTRAP_ADMIN_USERNAME"],
        "password": env["KC_BOOTSTRAP_ADMIN_PASSWORD"],
    })
    if status != 200:
        raise RuntimeError(f"Keycloak admin login failed (HTTP {status}); check the password stored in its volume")
    return base, data["access_token"]


def database_sql(sql):
    return compose("exec", "-T", "relational-database-server", "sh", "-lc",
                   'mariadb --default-character-set=utf8mb4 -uroot -p"$MARIADB_ROOT_PASSWORD"', input=sql)
