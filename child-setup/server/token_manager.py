#!/usr/bin/env python3
"""
Permanent token manager for Google APIs.
Uses service account JWT for Android Management (auto-refreshes, never expires).
Uses stored OAuth refresh token for Drive/user APIs.
"""
import json, time, base64, urllib.request, urllib.parse, os

SA_KEY_FILE = '/tmp/gcp-mdm-key.json'
REFRESH_TOKEN_FILE = '/tmp/gcp-refresh-token.json'
ENTERPRISE = 'enterprises/LC04701uaw'

def get_android_token():
    """Auto-refreshing SA token for Android Management - NEVER expires"""
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    
    with open(SA_KEY_FILE) as f:
        sa = json.load(f)
    now = int(time.time())
    h = base64.urlsafe_b64encode(json.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b'=')
    c = base64.urlsafe_b64encode(json.dumps({
        "iss": sa["client_email"],
        "scope": "https://www.googleapis.com/auth/androidmanagement",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now, "exp": now + 3600
    }).encode()).rstrip(b'=')
    k = serialization.load_pem_private_key(sa["private_key"].encode(), password=None, backend=default_backend())
    s = k.sign(h + b"." + c, padding.PKCS1v15(), hashes.SHA256())
    jwt_token = (h + b"." + c + b"." + base64.urlsafe_b64encode(s).rstrip(b'=')).decode()
    r = urllib.request.urlopen(urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=f"grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion={jwt_token}".encode()
    ), timeout=10)
    return json.loads(r.read())["access_token"]

def get_drive_token():
    """Auto-refreshing OAuth token for Drive - uses refresh token"""
    if not os.path.exists(REFRESH_TOKEN_FILE):
        return None
    with open(REFRESH_TOKEN_FILE) as f:
        creds = json.load(f)
    r = urllib.request.urlopen(urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode({
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token"
        }).encode()
    ), timeout=10)
    return json.loads(r.read())["access_token"]

# Cache
_token_cache = {}

def get_token(api='android'):
    global _token_cache
    now = time.time()
    if api in _token_cache and _token_cache[api]['expires'] > now:
        return _token_cache[api]['token']
    if api == 'android':
        token = get_android_token()
    else:
        token = get_drive_token()
    _token_cache[api] = {'token': token, 'expires': now + 3500}
    return token

if __name__ == '__main__':
    print("Android Management token:", get_android_token()[:20] + "...")
    dt = get_drive_token()
    print("Drive token:", (dt[:20] + "...") if dt else "Not configured")
