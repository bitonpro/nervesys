#!/usr/bin/env python3
"""
BitOn.Pro Family Safety Platform - Central Control Server
Connects: Google MDM + Aster + OpenClaw + Tailscale + Cloudflare
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import json, os, urllib.request, urllib.parse, time, base64, hashlib, threading, subprocess

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# ===== CONFIG =====
PORT = 9098
ENT = 'enterprises/LC04701uaw'
SA_KEY = '/tmp/gcp-mdm-key.json'
TS_KEY_FILE = '/tmp/tailscale-api-key'
PG_HOST = '172.22.0.2'
PG_DB = 'biton_family'
PG_USER = 'cloudmgmt'
ASTER_URL = 'http://127.0.0.1:5989'
OPENCLAW_URL = 'http://127.0.0.1:18789'
OLLAMA_URL = 'http://100.122.148.62:11434'

USERS = {"admin": "Biton24680", "meni": "Biton24680", "bar": "Biton24680"}

# ===== AUTH =====
def check_auth(headers):
    auth = headers.get('Authorization', '')
    if not auth.startswith('Basic '): return False
    try:
        decoded = base64.b64decode(auth[6:]).decode()
        user, pwd = decoded.split(':', 1)
        return USERS.get(user) == pwd
    except: return False

# ===== GOOGLE TOKEN (auto-refresh via JWT) =====
_google_token_cache = {'token': '', 'expires': 0}

def get_google_token():
    now = time.time()
    if _google_token_cache['expires'] > now:
        return _google_token_cache['token']
    try:
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.backends import default_backend
        with open(SA_KEY) as f: sa = json.load(f)
        n = int(time.time())
        h = base64.urlsafe_b64encode(json.dumps({"alg":"RS256","typ":"JWT"}).encode()).rstrip(b'=')
        c = base64.urlsafe_b64encode(json.dumps({"iss":sa["client_email"],"scope":"https://www.googleapis.com/auth/androidmanagement","aud":"https://oauth2.googleapis.com/token","iat":n,"exp":n+3600}).encode()).rstrip(b'=')
        k = serialization.load_pem_private_key(sa["private_key"].encode(), password=None, backend=default_backend())
        s = k.sign(h+b"."+c, padding.PKCS1v15(), hashes.SHA256())
        jwt = (h+b"."+c+b"."+base64.urlsafe_b64encode(s).rstrip(b'=')).decode()
        r = urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=f"grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion={jwt}".encode()), timeout=10)
        token = json.loads(r.read())["access_token"]
        _google_token_cache['token'] = token
        _google_token_cache['expires'] = now + 3500
        return token
    except Exception as e:
        print(f"Google token error: {e}")
        return ''

# ===== TAILSCALE =====
def get_ts_key():
    try:
        with open(TS_KEY_FILE) as f: return f.read().strip()
    except: return ''

def ts_api(path):
    key = get_ts_key()
    if not key: return {}
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            f'https://api.tailscale.com/api/v2/{path}',
            headers={'Authorization': f'Basic {base64.b64encode((key+":").encode()).decode()}'}
        ), timeout=15)
        return json.loads(r.read())
    except: return {}

# ===== ASTER =====
def aster_call(method, params=None):
    try:
        payload = json.dumps({"method": "tools/call", "params": {"name": method, "arguments": params or {}}})
        r = urllib.request.urlopen(urllib.request.Request(
            f'{ASTER_URL}/api/mcp', data=payload.encode(),
            headers={'Content-Type': 'application/json'}, method='POST'), timeout=30)
        return json.loads(r.read())
    except Exception as e:
        return {'error': str(e)}

def aster_devices():
    try:
        r = urllib.request.urlopen(urllib.request.Request(f'{ASTER_URL}/api/devices'), timeout=5)
        return json.loads(r.read())
    except: return []

def aster_health():
    try:
        r = urllib.request.urlopen(urllib.request.Request(f'{ASTER_URL}/api/health'), timeout=5)
        return json.loads(r.read())
    except: return {'status': 'offline'}

# ===== OLLAMA (local AI) =====
def ai_analyze(text, system_prompt="You are a child safety analyst. Respond in Hebrew."):
    try:
        payload = json.dumps({
            "model": "llama3.1", "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        })
        r = urllib.request.urlopen(urllib.request.Request(
            f'{OLLAMA_URL}/api/chat', data=payload.encode(),
            headers={'Content-Type': 'application/json'}, method='POST'), timeout=60)
        return json.loads(r.read()).get('message', {}).get('content', '')
    except Exception as e:
        return f'AI offline: {e}'

# ===== DB =====
def db_query(sql, params=None):
    """Simple DB query via docker exec"""
    try:
        escaped_sql = sql.replace("'", "'\\''")
        cmd = f"sudo docker exec cloudmgmt-postgres psql -U {PG_USER} -d {PG_DB} -t -A -c '{escaped_sql}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except: return ''

# ===== MAIN SERVER =====
class BitonHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not check_auth(self.headers):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="BitOn.Pro"')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Unauthorized</h1>')
            return

        path = self.path.split('?')[0]

        # ===== DASHBOARD =====
        if path == '/api/status':
            aster = aster_health()
            aster_devs = aster_devices()
            ts = ts_api('tailnet/-/devices')
            ts_online = len([d for d in ts.get('devices', []) if d.get('connectedToControl')])
            ts_total = len(ts.get('devices', []))
            g = get_google_token()
            self._j({
                'server': 'gama-2',
                'uptime': subprocess.run('uptime -p', shell=True, capture_output=True, text=True).stdout.strip(),
                'aster': {'status': aster.get('status', 'offline'), 'devices': len(aster_devs)},
                'tailscale': {'online': ts_online, 'total': ts_total},
                'google_mdm': {'connected': bool(g), 'enterprise': ENT},
                'openclaw': self._check_service(OPENCLAW_URL),
                'ollama': self._check_service(OLLAMA_URL),
            })

        # ===== DEVICES =====
        elif path == '/api/devices':
            devices = []
            # Aster devices
            for d in aster_devices():
                devices.append({**d, 'source': 'aster'})
            # Google MDM devices
            g = get_google_token()
            if g:
                try:
                    r = urllib.request.urlopen(urllib.request.Request(
                        f'https://androidmanagement.googleapis.com/v1/{ENT}/devices',
                        headers={'Authorization': f'Bearer {g}'}), timeout=10)
                    for d in json.loads(r.read()).get('devices', []):
                        hi = d.get('hardwareInfo', {})
                        devices.append({
                            'device_name': d.get('name', '').split('/')[-1],
                            'model': hi.get('model', ''),
                            'os_version': d.get('softwareInfo', {}).get('androidVersion', ''),
                            'source': 'google_mdm',
                            'state': d.get('state', ''),
                            **d
                        })
                except: pass
            self._j({'devices': devices, 'count': len(devices)})

        # ===== TAILSCALE NETWORK =====
        elif path == '/api/network':
            ts = ts_api('tailnet/-/devices')
            devices = []
            for d in ts.get('devices', []):
                devices.append({
                    'name': d.get('hostname', ''),
                    'ip': d.get('addresses', [''])[0],
                    'os': d.get('os', ''),
                    'online': d.get('connectedToControl', False),
                    'last_seen': d.get('lastSeen', ''),
                    'tags': d.get('tags', []),
                })
            online = [d for d in devices if d['online']]
            offline = [d for d in devices if not d['online']]
            self._j({'online': online, 'offline': offline, 'total': len(devices)})

        # ===== ENROLLMENT =====
        elif path == '/api/enrollment/new':
            g = get_google_token()
            if g:
                try:
                    r = urllib.request.urlopen(urllib.request.Request(
                        f'https://androidmanagement.googleapis.com/v1/{ENT}/enrollmentTokens',
                        data=json.dumps({"policyName": f"{ENT}/policies/ai-compute", "duration": "604800s"}).encode(),
                        headers={'Authorization': f'Bearer {g}', 'Content-Type': 'application/json'},
                        method='POST'), timeout=10)
                    self._j(json.loads(r.read()))
                except Exception as e: self._j({'error': str(e)})
            else: self._j({'error': 'no google token'})

        # ===== POLICIES =====
        elif path == '/api/policies':
            g = get_google_token()
            if g:
                try:
                    r = urllib.request.urlopen(urllib.request.Request(
                        f'https://androidmanagement.googleapis.com/v1/{ENT}/policies',
                        headers={'Authorization': f'Bearer {g}'}), timeout=10)
                    self._j(json.loads(r.read()))
                except Exception as e: self._j({'error': str(e)})

        # ===== ASTER =====
        elif path == '/api/aster/status':
            health = aster_health()
            devs = aster_devices()
            self._j({'status': health.get('status', 'offline'), 'devices': len(devs), 'devices_list': devs})

        elif path.startswith('/api/aster/device/') and path.endswith('/info'):
            device_id = path.split('/')[4]
            result = aster_call('get_device_info', {'deviceId': device_id})
            self._j(result)

        elif path.startswith('/api/aster/device/') and path.endswith('/location'):
            device_id = path.split('/')[4]
            result = aster_call('get_location', {'deviceId': device_id})
            self._j(result)

        elif path.startswith('/api/aster/device/') and path.endswith('/screenshot'):
            device_id = path.split('/')[4]
            result = aster_call('take_screenshot', {'deviceId': device_id})
            self._j(result)

        # ===== AI =====
        elif path == '/api/ai/models':
            try:
                r = urllib.request.urlopen(urllib.request.Request(f'{OLLAMA_URL}/api/tags'), timeout=5)
                self._j(json.loads(r.read()))
            except: self._j({'models': []})

        # ===== FAMILY =====
        elif path == '/api/family':
            result = db_query("SELECT row_to_json(f) FROM families f WHERE parent_email='bar@yohay.ai'")
            self._j(json.loads(result) if result else {'error': 'not found'})

        elif path == '/api/events':
            result = db_query("SELECT json_agg(e) FROM (SELECT * FROM events ORDER BY created_at DESC LIMIT 50) e")
            self._j(json.loads(result) if result and result != '' else [])

        # ===== SOS STATUS =====
        elif path == '/api/sos/active':
            result = db_query("SELECT json_agg(s) FROM sos_alerts s WHERE resolved=false")
            self._j(json.loads(result) if result and result != '' else [])

        # ===== STATIC FILES =====
        else:
            super().do_GET()

    def do_POST(self):
        if not check_auth(self.headers):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="BitOn.Pro"')
            self.end_headers()
            return

        cl = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(cl)) if cl > 0 else {}
        path = self.path.split('?')[0]

        # ===== SOS TRIGGER =====
        if path == '/api/sos/trigger':
            device_id = body.get('device_id', '')
            trigger = body.get('trigger_type', 'manual')
            # Get location
            loc = aster_call('get_location', {'deviceId': device_id})
            # Save to DB
            db_query(f"INSERT INTO sos_alerts (device_id, trigger_type, location) VALUES ('{device_id}', '{trigger}', '{json.dumps(loc)}')")
            db_query(f"INSERT INTO events (type, severity, payload, risk_score) VALUES ('sos', 'critical', '{json.dumps(body)}', 100)")
            # TODO: Call PBX to phone parent, send WhatsApp
            self._j({'status': 'SOS_ACTIVATED', 'location': loc})

        # ===== ASTER COMMANDS =====
        elif path == '/api/aster/command':
            cmd = body.get('command', '')
            args = body.get('arguments', {})
            result = aster_call(cmd, args)
            self._j(result)

        # ===== AI ANALYZE =====
        elif path == '/api/ai/analyze':
            text = body.get('text', '')
            prompt = body.get('prompt', 'Analyze this for child safety risks. Respond in Hebrew.')
            analysis = ai_analyze(text, prompt)
            risk = 0
            for word in ['danger', 'risk', 'alert', 'סכנה', 'חשוד', 'פדופיל', 'בריונות']:
                if word in analysis.lower(): risk += 20
            risk = min(risk, 100)
            db_query(f"INSERT INTO events (type, severity, ai_analysis, risk_score) VALUES ('ai_scan', '{'critical' if risk > 60 else 'info'}', '{analysis[:500]}', {risk})")
            self._j({'analysis': analysis, 'risk_score': risk})

        # ===== EVENT WEBHOOK (from Aster/OpenClaw) =====
        elif path == '/api/webhook/event':
            event_type = body.get('type', 'unknown')
            device_id = body.get('device_id', '')
            payload = body
            severity = 'info'
            risk = 0
            # Check for SOS keywords
            text = json.dumps(payload)
            sos_keywords = ['הצילו', 'במבה עם טונה', 'עזרה', 'help', 'sos']
            for kw in sos_keywords:
                if kw in text.lower():
                    severity = 'critical'
                    risk = 100
                    # Auto-trigger SOS
                    loc = aster_call('get_location', {'deviceId': device_id})
                    db_query(f"INSERT INTO sos_alerts (trigger_type, location) VALUES ('keyword:{kw}', '{json.dumps(loc)}')")
                    break
            # Check for grooming patterns
            grooming_words = ['סודי', 'אל תספר', 'נפגש', 'תשלח תמונה', 'secret', 'dont tell']
            for gw in grooming_words:
                if gw in text.lower():
                    severity = 'warning'
                    risk = max(risk, 70)
                    break
            db_query(f"INSERT INTO events (type, severity, payload, risk_score) VALUES ('{event_type}', '{severity}', '{json.dumps(payload)[:1000]}', {risk})")
            self._j({'received': True, 'severity': severity, 'risk_score': risk})

        # ===== MDM ACTIONS =====
        elif path == '/api/mdm/lock':
            device = body.get('device_name', '')
            g = get_google_token()
            if g and device:
                try:
                    urllib.request.urlopen(urllib.request.Request(
                        f'https://androidmanagement.googleapis.com/v1/{ENT}/devices/{device}:issueCommand',
                        data=json.dumps({"type": "LOCK"}).encode(),
                        headers={'Authorization': f'Bearer {g}', 'Content-Type': 'application/json'},
                        method='POST'), timeout=10)
                    self._j({'status': 'locked', 'device': device})
                except Exception as e: self._j({'error': str(e)})

        elif path == '/api/mdm/wipe':
            device = body.get('device_name', '')
            g = get_google_token()
            if g and device:
                try:
                    urllib.request.urlopen(urllib.request.Request(
                        f'https://androidmanagement.googleapis.com/v1/{ENT}/devices/{device}:issueCommand',
                        data=json.dumps({"type": "RESET_PASSWORD"}).encode(),
                        headers={'Authorization': f'Bearer {g}', 'Content-Type': 'application/json'},
                        method='POST'), timeout=10)
                    self._j({'status': 'wipe_initiated', 'device': device})
                except Exception as e: self._j({'error': str(e)})

        # ===== ENROLLMENT =====
        elif path == '/api/family/register':
            name = body.get('name', '')
            email = body.get('email', '')
            phone = body.get('phone', '')
            if name and email:
                db_query(f"INSERT INTO families (name, parent_email, parent_phone) VALUES ('{name}', '{email}', '{phone}') ON CONFLICT DO NOTHING")
                # Create enrollment token
                g = get_google_token()
                token_data = {}
                if g:
                    try:
                        r = urllib.request.urlopen(urllib.request.Request(
                            f'https://androidmanagement.googleapis.com/v1/{ENT}/enrollmentTokens',
                            data=json.dumps({"policyName": f"{ENT}/policies/ai-compute", "duration": "604800s"}).encode(),
                            headers={'Authorization': f'Bearer {g}', 'Content-Type': 'application/json'},
                            method='POST'), timeout=10)
                        token_data = json.loads(r.read())
                    except: pass
                self._j({'status': 'registered', 'family': name, 'enrollment': token_data})
            else:
                self._j({'error': 'name and email required'})

        else:
            self._j({'error': 'not found'})

    def _check_service(self, url):
        try:
            urllib.request.urlopen(urllib.request.Request(url), timeout=3)
            return 'online'
        except: return 'offline'

    def _j(self, d):
        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, ensure_ascii=False, default=str).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')

    def log_message(self, f, *a): pass

if __name__ == '__main__':
    os.chdir('/tmp/enroll')
    print(f"BitOn.Pro Family Safety Platform on port {PORT}")
    print(f"Enterprise: {ENT}")
    print(f"Aster: {ASTER_URL}")
    print(f"OpenClaw: {OPENCLAW_URL}")
    print(f"Ollama: {OLLAMA_URL}")
    ThreadedHTTPServer(('0.0.0.0', PORT), BitonHandler).serve_forever()
