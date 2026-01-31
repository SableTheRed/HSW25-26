import base64
import hashlib
import os
import secrets
import threading
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import cast
from urllib.parse import urlencode, urlparse, parse_qs

import requests

ISSUER = os.environ.get("OIDC_ISSUER")
CLIENT_ID = os.environ.get("OIDC_CLIENT_ID")
CLIENT_SECRET = os.environ.get("OIDC_CLIENT_SECRET") 

SCOPES = ["openid", "email", "profile"]

def is_wsl() -> bool:
    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except FileNotFoundError:
        return False

def open_browser(url: str):
    if is_wsl():
        subprocess.run(["wslview", url], check=False)
    else:
        webbrowser.open(url)

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def make_pkce_pair():
    code_verifier = b64url(secrets.token_bytes(32))
    challenge = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = b64url(challenge)
    return code_verifier, code_challenge

class OIDCCallbackServer(HTTPServer):
    auth_code: str | None = None
    auth_state: str | None = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        server = cast(OIDCCallbackServer, self.server)
        q = parse_qs(urlparse(self.path).query)
        server.auth_code = q.get("code", [None])[0]
        server.auth_state = q.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        # HTML with auto-close JavaScript
        html = b"""<!DOCTYPE html>
<html>
<head>
    <title>InsideOut - Signed In</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            padding: 40px;
        }
        .checkmark {
            font-size: 64px;
            color: #4ecca3;
            margin-bottom: 20px;
        }
        h1 {
            color: #4ecca3;
            margin-bottom: 10px;
        }
        p {
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="checkmark">&#10004;</div>
        <h1>Signed In Successfully</h1>
        <p>This window will close automatically...</p>
    </div>
    <script>
        setTimeout(function() {
            window.close();
        }, 1500);
    </script>
</body>
</html>"""
        self.wfile.write(html)

    def log_message(self, *args, **kwargs):
        return  # quiet

def get_openid_config(issuer: str) -> dict:
    r = requests.get(f"{issuer.rstrip('/')}/.well-known/openid-configuration", timeout=15)
    r.raise_for_status()
    return r.json()

def run_loopback_server():
    server = OIDCCallbackServer(("127.0.0.1", 0), CallbackHandler)  # 0 => pick free port
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server, thread

def login():
    """
    Prompts the user to login via OIDC in the browser.

    Returns:
        tuple: (sub, name, access_token, refresh_token, id_token, expires_in)
    """
    if not ISSUER:
        raise ValueError("OIDC_ISSUER environment variable is required")
    if not CLIENT_ID:
        raise ValueError("OIDC_CLIENT_ID environment variable is required")
    if not CLIENT_SECRET:
        raise ValueError("OIDC_CLIENT_SECRET environment variable is required")

    cfg = get_openid_config(ISSUER)
    auth_endpoint = cfg["authorization_endpoint"]
    token_endpoint = cfg["token_endpoint"]
    userinfo_endpoint = cfg["userinfo_endpoint"]

    server, thread = run_loopback_server()
    redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"

    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)  # recommended for OIDC ID token replay protection
    code_verifier, code_challenge = make_pkce_pair()

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{auth_endpoint}?{urlencode(params)}"

    print("Opening browser for sign-in…")
    open_browser(auth_url)

    # Wait for the callback to complete
    thread.join()

    if not getattr(server, "auth_code", None):
        raise RuntimeError("No authorization code received.")

    if server.auth_state != state:
        raise RuntimeError("State mismatch (possible CSRF).")

    token_resp = requests.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": server.auth_code,
            "redirect_uri": redirect_uri,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code_verifier": code_verifier,
        },
        timeout=15,
    )
    token_resp.raise_for_status()
    tokens = token_resp.json()

    userinfo_resp = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        timeout=15,
    )
    userinfo_resp.raise_for_status()
    userinfo = userinfo_resp.json()

    sub = userinfo.get("sub")
    name = userinfo.get("name")
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    id_token = tokens.get("id_token")
    expires_in = tokens.get("expires_in")

    return sub, name, access_token, refresh_token, id_token, expires_in


if __name__ == "__main__":
    sub, name, access_token, refresh_token, id_token, expires_in = login()
    print(f"Signed in as {name} (sub: {sub})")
