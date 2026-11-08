"""API khởi đầu. Các endpoint TODO cố ý trả 501 đến khi được triển khai."""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health():
    """Liveness của API; chưa kiểm tra DB hay Keycloak."""
    return jsonify(status="ok", service="application-backend-server")


@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")


@app.get("/student")
def student():
    # TODO APP-01: đọc students.json bằng đường dẫn tương đối với __file__.
    return jsonify(error="not_implemented", task="APP-01"), 501


@app.get("/students-db")
def students_db():
    # TODO APP-02: dùng DB_* trong environment; truy vấn studentdb.students.
    return jsonify(error="not_implemented", task="APP-02"), 501


@app.get("/secure")
def secure():
    # TODO AUTH-01: xác minh chữ ký RS256, iss, aud, exp; đọc README auth.
    return jsonify(error="not_implemented", task="AUTH-01"), 501
