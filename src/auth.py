import base64
import hashlib
import json
import os
import secrets
import threading
import subprocess
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests

ISSUER = os.environ["OIDC_ISSUER"] 
CLIENT_ID = os.environ["OIDC_CLIENT_ID"] 

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

class CallbackHandler(BaseHTTPRequestHandler):
    # Store results on the server object
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        self.server.auth_code = q.get("code", [None])[0]
        self.server.auth_state = q.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Signed in</h1>You can close this window.")

    def log_message(self, *args, **kwargs):
        return  # quiet

def get_openid_config(issuer: str) -> dict:
    r = requests.get(f"{issuer.rstrip('/')}/.well-known/openid-configuration", timeout=15)
    r.raise_for_status()
    return r.json()

def run_loopback_server():
    server = HTTPServer(("127.0.0.1", 0), CallbackHandler)  # 0 => pick free port
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    return server, thread

def main():
    cfg = get_openid_config(ISSUER)
    auth_endpoint = cfg["authorization_endpoint"]
    token_endpoint = cfg["token_endpoint"]

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
            "code_verifier": code_verifier,
        },
        timeout=15,
    )
    token_resp.raise_for_status()
    tokens = token_resp.json()

    # If OIDC, you typically get an id_token (JWT) + access_token (+ maybe refresh_token)
    print(json.dumps({k: ("<redacted>" if "token" in k else v) for k, v in tokens.items()}, indent=2))

    # Next steps:
    # 1) Validate id_token (issuer, audience, signature via JWKS) before trusting identity
    # 2) Create your local app session/user record
    # 3) Store refresh_token securely (keyring, encrypted file, etc.)

if __name__ == "__main__":
    main()
