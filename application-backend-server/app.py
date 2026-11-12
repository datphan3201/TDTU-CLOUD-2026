"""MyMiniCloud API: JSON, MariaDB and Keycloak RS256 access tokens."""

import json
import os
from pathlib import Path

import jwt
import pymysql
from flask import Flask, jsonify, request
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError, PyJWKSetError

app = Flask(__name__)
issuer = os.environ.get("OIDC_ISSUER", "")
audience = os.environ.get("OIDC_AUDIENCE", "flask-app")
jwks_url = os.environ.get("OIDC_JWKS_URL", "")
# Cache the SET with a TTL, not individual signing keys indefinitely.
jwks_client = jwt.PyJWKClient(
    jwks_url, cache_jwk_set=True, cache_keys=False, lifespan=300,
    timeout=3, cooldown_duration=0,
) if jwks_url else None


@app.get("/health")
def health():
    """Liveness only; dependency availability is tested by feature endpoints."""
    return jsonify(status="ok", service="application-backend-server")


@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")


@app.get("/student")
def student():
    try:
        data = json.loads(Path(__file__).with_name("students.json").read_text(encoding="utf-8"))
        if not isinstance(data, list) or len(data) != 5:
            raise ValueError("Expected five student objects")
        for item in data:
            if (not isinstance(item, dict)
                    or set(item) != {"id", "name", "major", "gpa"}
                    or type(item["id"]) is not int
                    or not isinstance(item["name"], str)
                    or not isinstance(item["major"], str)
                    or type(item["gpa"]) not in (int, float)):
                raise ValueError("Invalid student object")
    except (OSError, ValueError):
        app.logger.exception("Unable to read student JSON")
        return jsonify(error="student_data_unavailable"), 500
    return jsonify(data)


@app.get("/students-db")
def students_db():
    try:
        with pymysql.connect(
            host=os.environ.get("DB_HOST", "relational-database-server"),
            port=int(os.environ.get("DB_PORT", "3306")),
            user=os.environ.get("DB_USER", "minicloud_app"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("STUDENT_DB_NAME", "studentdb"),
            charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=3, read_timeout=3, write_timeout=3, autocommit=True,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, student_id, fullname, dob, major FROM students ORDER BY id")
                rows = cursor.fetchall()
        for row in rows:
            row["dob"] = row["dob"].isoformat() if row["dob"] else None
    except (pymysql.MySQLError, ValueError):
        app.logger.warning("Student database unavailable")
        return jsonify(error="database_unavailable"), 503
    return jsonify(rows)


@app.get("/secure")
def secure():
    authorization = request.headers.get("Authorization", "").split()
    if len(authorization) != 2 or authorization[0].lower() != "bearer":
        return unauthorized()
    token = authorization[1]
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str) or not header["kid"]:
            return unauthorized()
        if not jwks_client or not issuer or not audience:
            return jsonify(error="identity_provider_unavailable"), 503
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token, signing_key.key, algorithms=["RS256"],
            issuer=issuer, audience=audience,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
    except (PyJWKClientConnectionError, PyJWKSetError):
        app.logger.warning("Identity provider JWKS unavailable")
        return jsonify(error="identity_provider_unavailable"), 503
    except (jwt.InvalidTokenError, PyJWKClientError):
        return unauthorized()
    return jsonify(message="Access granted", username=claims.get("preferred_username"), sub=claims["sub"])


def unauthorized():
    return jsonify(error="invalid_or_missing_token"), 401, {"WWW-Authenticate": "Bearer"}
