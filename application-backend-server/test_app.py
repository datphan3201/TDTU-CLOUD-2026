"""Auth contract tests using real RSA signatures and an HTTP JWKS server."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import os
from pathlib import Path
import tempfile
from threading import Thread
import time
import unittest
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import pymysql

spec = importlib.util.spec_from_file_location("minicloud_api", Path(__file__).with_name("app.py"))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.rotated = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.alien = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        class JWKS(BaseHTTPRequestHandler):
            def do_GET(self):
                cls.hits += 1
                self.send_response(cls.jwks_status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"keys": cls.keys}).encode())

            def log_message(self, *args):
                pass

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), JWKS)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    @staticmethod
    def jwk(key, kid):
        return {**jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key(), as_dict=True), "kid": kid, "use": "sig", "alg": "RS256"}

    def setUp(self):
        self.client = api.app.test_client()
        api.issuer = "http://issuer.invalid/auth/realms/lab"
        api.audience = "flask-app"
        type(self).hits = 0
        type(self).jwks_status = 200
        type(self).keys = [self.jwk(self.private, "initial")]
        api.jwks_client = jwt.PyJWKClient(
            f"http://127.0.0.1:{self.server.server_port}/certs",
            lifespan=300, timeout=1, cooldown_duration=0,
        )

    def token(self, updates=None, key=None, kid="initial", omit=()):
        claims = {"sub": "demo-subject", "preferred_username": "sv01", "iss": api.issuer,
                  "aud": "flask-app", "exp": int(time.time()) + 60}
        claims.update(updates or {})
        for field in omit:
            claims.pop(field)
        return jwt.encode(claims, key or self.private, algorithm="RS256", headers={"kid": kid})

    def secure(self, token):
        return self.client.get("/secure", headers={"Authorization": "Bearer " + token})

    def test_valid_token_and_cached_jwks(self):
        for _ in range(2):
            response = self.secure(self.token())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["username"], "sv01")
        self.assertEqual(type(self).hits, 1)

    def test_invalid_claims_and_signatures_are_rejected(self):
        cases = {
            "wrong issuer": self.token({"iss": "http://other.invalid"}),
            "wrong audience": self.token({"aud": "other-client"}),
            "expired": self.token({"exp": int(time.time()) - 30}),
            "future nbf": self.token({"nbf": int(time.time()) + 300}),
            "wrong signature": self.token(key=self.alien),
            "unknown kid": self.token(kid="unknown"),
            "missing exp": self.token(omit=["exp"]),
            "missing sub": self.token(omit=["sub"]),
            "malformed": "invalid-token",
            "symmetric algorithm": jwt.encode({"sub": "x"}, "x" * 32, algorithm="HS256", headers={"kid": "initial"}),
        }
        for label, token in cases.items():
            with self.subTest(label=label):
                response = self.secure(token)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["WWW-Authenticate"], "Bearer")

    def test_missing_or_invalid_authorization(self):
        for header in [None, "Basic test", "Bearer", "Bearer one two"]:
            with self.subTest(header=header):
                response = self.client.get("/secure", headers={"Authorization": header} if header else {})
                self.assertEqual(response.status_code, 401)

    def test_unknown_kid_refreshes_rotated_keys(self):
        self.assertEqual(self.secure(self.token()).status_code, 200)
        type(self).keys.append(self.jwk(self.rotated, "rotated"))
        self.assertEqual(self.secure(self.token(key=self.rotated, kid="rotated")).status_code, 200)
        self.assertEqual(type(self).hits, 2)

    def test_jwks_cache_expires(self):
        self.assertEqual(self.secure(self.token()).status_code, 200)
        with patch("jwt.jwk_set_cache.time.monotonic", return_value=time.monotonic() + 301):
            self.assertEqual(self.secure(self.token()).status_code, 200)
        self.assertEqual(type(self).hits, 2)

    def test_identity_provider_outage_is_503(self):
        type(self).jwks_status = 503
        response = self.secure(self.token())
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"error": "identity_provider_unavailable"})

    def test_database_outage_hides_driver_details(self):
        with patch.object(api.pymysql, "connect", side_effect=pymysql.OperationalError(2003, "secret-password")):
            response = self.client.get("/students-db")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {"error": "database_unavailable"})

    def test_student_file_resolves_independently_of_cwd(self):
        previous = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as folder:
                os.chdir(folder)
                response = self.client.get("/student")
        finally:
            os.chdir(previous)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 5)


if __name__ == "__main__":
    unittest.main()
