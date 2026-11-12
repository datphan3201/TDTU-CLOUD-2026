#!/usr/bin/env python3
"""Apply the additive student migration to new or existing lab volumes."""
import re
from lab_common import ROOT, configuration, database_sql


def main():
    config = configuration()
    user = config["services"]["relational-database-server"]["environment"]["MARIADB_USER"]
    if not re.fullmatch(r"[A-Za-z0-9_]+", user) or user.lower() == "root":
        raise SystemExit("Use a non-root DB_USER consisting of letters, digits and underscores")
    migration = (ROOT / "relational-database-server/migrations/002_students.sql").read_text()
    database_sql(migration + f"\nGRANT SELECT ON studentdb.students TO '{user}'@'%';\n")
    print("PASS DB-01 migration and SELECT grant; existing rows preserved")


if __name__ == "__main__":
    main()
