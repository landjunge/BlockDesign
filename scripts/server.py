"""Loopback-only browser host; static ES modules, existing ThreadDesk facade."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlparse, unquote
from host import Host, PROJECT
from ai_adapter import AIAdapter, ContractError

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if not self.local_request(): return
        if path == '/api/status':
            try:
                self.reply(self.server.adapter.status())
            except Exception:
                self.reply({'ok': False, 'error': 'host_unavailable'}, 503)
            return
        if path.startswith('/api/tasks/'):
            try: self.reply(self.server.adapter.get(path.removeprefix('/api/tasks/')))
            except ContractError as e:self.reply({'error':str(e)},404)
            return
        target=(PROJECT/path.lstrip('/')).resolve()
        if path=='/':target=PROJECT/'index.html'
        if not target.is_relative_to(PROJECT) or not (target==PROJECT/'index.html' or
          target.is_relative_to(PROJECT/'src') or target.is_relative_to(PROJECT/'styles')):
            self.send_error(404);return
        super().do_GET()
    def local_request(self):
        allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        if self.headers.get('Host') not in allowed:
            self.reply({'error':'hostRejected'},403);return False
        return True
    def do_POST(self):
        if not self.local_request():return
        origin=self.headers.get('Origin')
        if origin and origin not in {f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}:
            self.reply({'error':'originRejected'},403);return
        if urlparse(self.path).path!='/api/tasks':self.send_error(404);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=16000 or self.headers.get_content_type()!='application/json':
                self.reply({'error':'contextTooLarge'},400);return
            packet=json.loads(self.rfile.read(length))
            self.reply(self.server.adapter.submit(packet),202)
        except (ContractError,ValueError) as e:self.reply({'error':str(e) if isinstance(e,ContractError) else 'invalidReply'},400)
        except Exception:self.reply({'error':'offline'},503)
    def reply(self, data, status=200):
        raw=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
        super().end_headers()
    def log_message(self, fmt, *args):
        # No request payloads or user instructions in console logs.
        sys.stderr.write(fmt % args + '\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=5190);a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(PROJECT)))
    server.host=Host()
    server.adapter=AIAdapter(server.host)
    print(f'BLOCK_DESIGNER_READY http://127.0.0.1:{server.server_port} · {server.host.thread_id}',flush=True)
    server.serve_forever()
if __name__=='__main__':main()
