#!/usr/bin/env python3
"""Read-only API/DB/auth integration checks; tokens and passwords are never printed."""
from datetime import date
import json
from urllib.parse import quote

from lab_common import admin_session, compose, configuration, environment, gateway_url, request_json


def check(label, condition):
    if not condition:
        raise RuntimeError("FAIL " + label)
    print("PASS " + label)


def main():
    config = configuration()
    base = gateway_url(config)
    env = environment()
    print("Newton local acceptance: " + base)
    status, students = request_json(base + "/api/student")
    check("APP-01 five typed students, GPA scale 0-4", status == 200 and isinstance(students, list) and len(students) == 5
          and all(set(s) == {"id", "name", "major", "gpa"} and type(s["id"]) is int
                  and isinstance(s["name"], str) and isinstance(s["major"], str)
                  and type(s["gpa"]) in (float, int) and 0 <= s["gpa"] <= 4 for s in students))
    app_port = config["services"]["application-backend-server"]["ports"][0]["published"]
    status, direct = request_json(f"http://127.0.0.1:{app_port}/student")
    check("APP-01 direct API equals gateway", status == 200 and direct == students)
    status, alias = request_json(base + "/student/?source=acceptance")
    check("GW-01 /student/ equals /api/student including query string", status == 200 and alias == students)
    status, rows = request_json(base + "/api/students-db")
    check("APP-02 database API has at least three rows", status == 200 and isinstance(rows, list) and len(rows) >= 3)
    for row in rows:
        check("APP-02 row schema and ISO date", set(row) == {"id", "student_id", "fullname", "dob", "major"}
              and (row["dob"] is None or date.fromisoformat(row["dob"]).isoformat() == row["dob"]))
    sql_rows = compose("exec", "-T", "relational-database-server", "sh", "-lc",
                       'mariadb --batch --skip-column-names --default-character-set=utf8mb4 '
                       '-u"$MARIADB_USER" -p"$MARIADB_PASSWORD" -e '
                       '\'SELECT JSON_OBJECT("id",id,"student_id",student_id,"fullname",fullname,"dob",DATE_FORMAT(dob,"%Y-%m-%d"),"major",major) FROM studentdb.students ORDER BY id;\'')
    check("DB-01 application user SELECT matches API data", [json.loads(line) for line in sql_rows.splitlines()] == rows)
    status, _ = request_json(base + "/api/secure")
    check("AUTH-01 missing token returns 401", status == 401)
    status, _ = request_json(base + "/api/secure", token="invalid-token")
    check("AUTH-01 malformed token returns 401", status == 401)
    realm = "realm_" + env["STUDENT_ID"]
    status, discovery = request_json(base + "/auth/realms/" + quote(realm, safe="") + "/.well-known/openid-configuration")
    check("AUTH-01 public issuer matches gateway", status == 200 and discovery["issuer"] == base + "/auth/realms/" + realm)
    admin_base, admin_token = admin_session(config)
    status, clients = request_json(admin_base + "/admin/realms/" + quote(realm, safe="") + "/clients?clientId=flask-app", token=admin_token)
    check("AUTH-01 public client and direct grants", status == 200 and len(clients) == 1
          and clients[0]["publicClient"] and clients[0]["directAccessGrantsEnabled"])
    for user in ("sv01", "sv02"):
        status, result = request_json(discovery["token_endpoint"], method="POST", form={
            "grant_type": "password", "client_id": "flask-app", "username": user,
            "password": env.get("KEYCLOAK_DEMO_PASSWORD", ""),
        })
        check("AUTH-01 login " + user, status == 200 and "access_token" in result)
        status, body = request_json(base + "/api/secure", token=result["access_token"])
        check("AUTH-01 valid token for " + user + " returns 200", status == 200 and body["username"] == user)
        parts = result["access_token"].split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        status, _ = request_json(base + "/api/secure", token=".".join(parts))
        check("AUTH-01 tampered real token signature returns 401", status == 401)
    print("All Newton integration checks passed (no credentials or tokens logged).")


if __name__ == "__main__":
    main()
