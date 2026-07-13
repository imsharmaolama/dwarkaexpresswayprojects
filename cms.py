#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight CMS admin for dwarkaexpresswayprojects.
Local-only web UI: manage projects / developers / sectors / settings,
upload images, and Publish (build.py + git commit + push -> Vercel auto-deploys).

Launch:
    python cms.py                # serves http://127.0.0.1:8081  (password: cms123)
    CMS_PW=secret python cms.py  # custom password
"""
import json, os, re, hashlib, subprocess, cgi, urllib.parse, html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PW = os.environ.get("CMS_PW", "cms123")
TOKEN = "tk_" + hashlib.sha256(DEFAULT_PW.encode()).hexdigest()[:24]
PORT = int(os.environ.get("CMS_PORT", "8081"))
UPLOAD_DIR = os.path.join(ROOT, "assets", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_HTML = None  # loaded lazily

# ---------------- data helpers ----------------
def load_projects():
    return json.load(open(os.path.join(ROOT, "projects.json"), encoding="utf-8"))

def save_projects(data):
    json.dump(data, open(os.path.join(ROOT, "projects.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

def load_cms():
    p = os.path.join(ROOT, "cms_data.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"developers": [], "settings": {}, "sector_groups": [], "corridors": []}

def save_cms(data):
    json.dump(data, open(os.path.join(ROOT, "cms_data.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

def authed(qs):
    return qs.get("token", [""]) [0] == TOKEN

# ---------------- publish pipeline ----------------
def publish():
    """Run build.py then git add/commit/push. Returns (ok, log)."""
    log = []
    try:
        r = subprocess.run(["python", "build.py"], cwd=ROOT, capture_output=True, text=True, timeout=600)
        log.append(r.stdout.strip() or r.stderr.strip())
        if r.returncode != 0:
            return False, log + ["BUILD FAILED"]
        r = subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True, text=True, timeout=120)
        msg = "CMS publish: update content via admin"
        r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=ROOT, capture_output=True, text=True, timeout=120)
        log.append("commit: " + (r.stdout.strip() or r.stderr.strip() or "ok"))
        r = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            return False, log + ["PUSH FAILED: " + (r.stderr.strip() or r.stdout.strip())]
        log.append("pushed -> Vercel will deploy")
        return True, log
    except Exception as e:
        return False, log + ["ERROR: " + str(e)]

# ---------------- HTTP handler ----------------
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, ctype):
        data = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path, qs = url.path, urllib.parse.parse_qs(url.query)
        if path in ("/", "/index.html"):
            global ADMIN_HTML
            if ADMIN_HTML is None:
                ADMIN_HTML = open(os.path.join(ROOT, "cms_admin.html"), encoding="utf-8").read()
            self._send_file(os.path.join(ROOT, "cms_admin.html"), "text/html; charset=utf-8")
            return
        if not authed(qs):
            self._send(401, {"error": "unauthorized"})
            return
        # ---- API ----
        if path == "/api/projects":
            projs = load_projects()
            # light list for the table
            out = [{"slug": p.get("slug"), "name": p.get("name"),
                    "type": p.get("project_type"), "status": p.get("project_status"),
                    "price": p.get("starting_price"), "builder": (p.get("builder") or [{}])[0].get("name") if p.get("builder") else ""}
                   for p in projs]
            self._send(200, out)
        elif path == "/api/project":
            slug = (qs.get("slug") or [""])[0]
            projs = load_projects()
            p = next((x for x in projs if x.get("slug") == slug), None)
            self._send(200 if p else 404, p or {"error": "not found"})
        elif path == "/api/cms":
            self._send(200, load_cms())
        elif path == "/api/uploads":
            files = sorted(os.listdir(UPLOAD_DIR))
            self._send(200, [{"name": f, "url": "assets/uploads/" + f} for f in files])
        elif path == "/api/publish":
            ok, log = publish()
            self._send(200 if ok else 500, {"ok": ok, "log": log})
        else:
            self._send(404, {"error": "unknown route"})

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path, qs = url.path, urllib.parse.parse_qs(url.query)
        if path == "/api/login":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            if hashlib.sha256(data.get("pw", "").encode()).hexdigest() == hashlib.sha256(DEFAULT_PW.encode()).hexdigest():
                self._send(200, {"token": TOKEN})
            else:
                self._send(403, {"error": "bad password"})
            return
        if not authed(qs):
            self._send(401, {"error": "unauthorized"}); return
        ctype = self.headers.get("Content-Type", "")
        if "multipart/form-data" in ctype:
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST",
                              "CONTENT_TYPE": ctype, "CONTENT_LENGTH": self.headers.get("Content-Length", "0")})
            f = form["file"]
            fn = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(f.filename))
            open(os.path.join(UPLOAD_DIR, fn), "wb").write(f.file.read())
            self._send(200, {"url": "assets/uploads/" + fn, "name": fn})
            return
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        if path == "/api/project/save":
            projs = load_projects()
            slug = data.get("slug")
            idx = next((i for i, x in enumerate(projs) if x.get("slug") == slug), None)
            if idx is None:
                projs.append(data)
            else:
                projs[idx] = data
            save_projects(projs)
            self._send(200, {"ok": True, "slug": slug})
        elif path == "/api/project/delete":
            slug = data.get("slug")
            projs = [x for x in load_projects() if x.get("slug") != slug]
            save_projects(projs)
            self._send(200, {"ok": True, "remaining": len(projs)})
        elif path == "/api/cms/save":
            save_cms(data)
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": "unknown route"})

if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"CMS running at http://127.0.0.1:{PORT}  (password: {DEFAULT_PW})")
    srv.serve_forever()
