"""Loopback-only browser host; static ES modules, existing ThreadDesk facade."""
import argparse
import asyncio
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from project_store import ProjectStore, FORMAT
from pathlib import Path
import sys
from urllib.parse import urlparse, unquote
from host import Host, PROJECT
from ai_adapter import AIAdapter, ContractError
from design_workflow import DesignWorkflow
from workflow_profile import load_workflow_profile, WorkflowProfileError
from static_assets import read_asset, AssetUnavailable

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if not self.local_request(): return
        if path.startswith('/api/design/workflows/'):
            parts=path.split('/')
            try:
                if len(parts)!=6:raise ContractError('unknownTask')
                with self.server.projects.transaction():
                    value=self.server.design_workflow.load(parts[4],parts[5])
                    public=self.server.design_workflow.public(value)
                    public['stale']=self.server.projects.read(parts[4])['head']!=value['snapshot_id']
                    self.reply(public)
            except (ContractError,ValueError) as e:self.reply({'error':str(e)},400)
            except Exception:self.reply({'error':'designBridgeUnknown'},503)
            return
        if path.startswith('/api/design/preview/'):
            try:
                raw=self.server.projects.preview(path.removeprefix('/api/design/preview/'))
                self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','private, max-age=31536000, immutable');self.end_headers();self.wfile.write(raw)
            except (ContractError,OSError):self.reply({'error':'designMissingArtifact'},404)
            return
        if path=='/api/projects':
            try:self.reply({'format':FORMAT,'projects':self.server.projects.list()})
            except Exception:self.reply({'error':'saveFailed'},503)
            return
        if path.startswith('/api/projects/'):
            parts=path.split('/')
            try:
                if len(parts)==4:self.reply(self.server.projects.read(parts[3]))
                elif len(parts)==5 and parts[4]=='history':self.reply(self.server.projects.history(parts[3]))
                elif len(parts)==6 and parts[4]=='snapshots':self.reply(self.server.projects.read(parts[3],parts[5]))
                else:self.send_error(404)
            except ContractError as e:self.reply({'error':str(e)},400)
            except Exception:self.reply({'error':'saveFailed'},503)
            return
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
        self.static_response(path)
    def do_HEAD(self):
        if not self.local_request():return
        self.static_response(unquote(urlparse(self.path).path), head_only=True)
    def static_response(self, path, head_only=False):
        try:raw, modified=read_asset(PROJECT,path)
        except AssetUnavailable:self.send_error(404);return
        self.send_response(200)
        self.send_header('Content-Type',self.guess_type('index.html' if path=='/' else path))
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Last-Modified',self.date_time_string(modified))
        self.end_headers()
        if not head_only:self.wfile.write(raw)
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
        path=urlparse(self.path).path
        if path=='/api/design/workflows':
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=8000 or self.headers.get_content_type()!='application/json':raise ContractError('contextTooLarge')
                packet=json.loads(self.rfile.read(length))
                if set(packet)=={'project_id','snapshot_id','instruction'}:
                    self.reply(self.server.design_workflow.prepare(packet['project_id'],packet['snapshot_id'],packet['instruction']))
                elif set(packet)=={'project_id','id','action','data'}:
                    self.reply(asyncio.run(self.server.design_workflow.action(packet['project_id'],packet['id'],packet['action'],packet['data'])))
                else:raise ContractError('invalidAction')
            except (ContractError,ValueError) as e:self.reply({'error':str(e) if isinstance(e,ContractError) else 'invalidAction'},400)
            except Exception:self.reply({'error':'designBridgeUnknown'},503)
            return
        if path=='/api/design/import':
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=1800000 or self.headers.get_content_type()!='application/json':raise ContractError('designSourceLimit')
                self.reply(self.server.projects.import_design(json.loads(self.rfile.read(length))))
            except (ContractError,ValueError) as e:self.reply({'error':str(e) if isinstance(e,ContractError) else 'designInvalidSource'},400)
            except Exception:self.reply({'error':'saveFailed'},503)
            return
        if path.startswith('/api/projects/'):
            try:
                parts=path.split('/');length=int(self.headers.get('Content-Length','0'))
                if len(parts)!=4 or not 0<length<=16000000 or self.headers.get_content_type()!='application/json':raise ContractError('invalidValues')
                packet=json.loads(self.rfile.read(length));self.reply(self.server.projects.save(parts[3],packet['body'],packet['meta'],packet.get('base')))
            except ContractError as e:self.reply({'error':str(e)},409 if str(e)=='storageConflict' else 400)
            except Exception:self.reply({'error':'saveFailed'},503)
            return
        if path!='/api/tasks':self.send_error(404);return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=16000 or self.headers.get_content_type()!='application/json':
                self.reply({'error':'contextTooLarge'},400);return
            packet=json.loads(self.rfile.read(length))
            if 'conversation' in packet:
                c=packet['conversation'];saved=self.server.projects.read(c['project_id'],c['snapshot_id']);meta=saved['snapshot']['meta']
                state=saved['body']['state'];snapshot={k:state[k] for k in ['version','revision','document','boxes','selection','activeLayer','grid']}
                snapshot.update(coordinates={'origin':[0,0],'x':'right','y':'down','unit':'px','pixel_scale':1},zoom=state['ui']['zoom'],language=state['ui']['language'])
                if meta.get('task_id')!=packet['task_id'] or meta.get('instruction')!=packet['instruction'] or snapshot!=packet['snapshot']:raise ContractError('taskConflict')
                previous=[t for t in state['tasks'] if t['task_id']!=packet['task_id']]
                parent=next((t for t in previous if t['task_id']==c['parent_task_id']),None)
                if c['parent_task_id'] is not None and parent is None:raise ContractError('taskConflict')
                relevant=([t for t in previous if t['task_id']!=parent['task_id']][-1:]+[parent]) if parent else previous[-2:]
                turns=[{'task_id':t['task_id'],'instruction':t['instruction'],'summary':t.get('reply',{}).get('summary',''),'question':t.get('clarification',{}).get('question') or t.get('reply',{}).get('question',''),'box_ids':t['box_ids'],'status':t['status'],'actions':t.get('reply',{}).get('actions',[]),**({'proposals':t.get('reply',{}).get('proposals',[])} if any('proposals' in turn for turn in c['turns']) else {})} for t in relevant]
                if turns!=c['turns'] or c['selection_changed']!=(bool(parent) and parent['box_ids']!=packet['box_ids']):raise ContractError('taskConflict')
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

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=5190)
    p.add_argument('--workflow-profile', help='Private operator JSON or BD_WORKFLOW_PROFILE')
    a=p.parse_args(argv)
    try:workflow_profile=load_workflow_profile(a.workflow_profile)
    except WorkflowProfileError as exc:p.exit(2,f'[{exc.code}] {exc}\n')
    server=ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(PROJECT)))
    server.host=Host()
    server.adapter=AIAdapter(server.host)
    project_root=Path(os.environ.get('BD_PROJECT_ROOT',str(Path.home()/'Library/Application Support/BlockDesigner')))
    if 'BD_PROJECT_ROOT' not in os.environ:
        server.host.context(lambda c:c.write_own_record('projects:write','project-storage',{'format':FORMAT,'root':str(project_root)}),'projects:write')
    else:server.host.context(lambda c:c.read_own_data(),'projects:write')
    server.projects=ProjectStore(project_root)
    # Only trusted startup may select the existing fixed client/profile.
    # No browser input configures a peer, path, principal or credential.
    server.design_workflow=DesignWorkflow(server.projects, *(workflow_profile or (None, None)))
    print(f'BlockDesigner bereit http://127.0.0.1:{server.server_port} · {server.host.thread_id}',flush=True)
    server.serve_forever()
if __name__=='__main__':main()
