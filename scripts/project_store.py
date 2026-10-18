"""Private local projects. Immutable CAS contents + atomic checked commits.

Reuse ThreadDesk's artifact publisher, never its foreign database. Format 1 is
explicit; unknown formats are rejected rather than guessed or overwritten.
"""
from copy import deepcopy
from contextlib import contextmanager
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from threading import RLock
from uuid import uuid4
from ai_adapter import validate_snapshot, ContractError, require, patch_values, ID
from threaddesk.storage.artifacts import ContentAddressedArtifacts
from design_source import validate_design, imported, decode_upload, png_size, catalog, MAX_PNG, MAX_HTML

FORMAT=1
UUID=re.compile(r'[a-f0-9-]{36}\Z')
HASH=re.compile(r'[a-f0-9]{64}\Z')
def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sync_dir(path):
    fd=os.open(path,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    temp=path.parent/('.'+path.name+'.'+str(uuid4())+'.tmp')
    try:
        with temp.open('xb') as stream:
            os.chmod(temp,0o600);stream.write(data);stream.flush();os.fsync(stream.fileno())
        os.replace(temp,path);sync_dir(path.parent)
    finally:
        if temp.exists():temp.unlink()

def validate_body(body):
    require(isinstance(body,dict) and body.get('format')==FORMAT,'storageFormat')
    state=body.get('state');require(isinstance(state,dict),'invalidDocument')
    ui=state.get('ui',{})
    require(ui.get('view') in ['structure','design'],'invalidDocument')
    snapshot={k:deepcopy(state[k]) for k in ['version','revision','document','boxes','selection','activeLayer','grid']}
    snapshot.update(coordinates={'origin':[0,0],'x':'right','y':'down','unit':'px','pixel_scale':1},zoom=ui.get('zoom'),language=ui.get('language'))
    validate_snapshot(snapshot,max_boxes=10000)
    validate_design(state.get('design'), [box['id'] for box in state['boxes']])
    require(type(state.get('nextNumber'))==int and state['nextNumber']>max([0]+[b['number'] for b in state['boxes']]),'invalidIdentity')
    require(isinstance(state.get('creationCounts'),list) and len(state['creationCounts'])==3 and all(type(x)==int and x>=0 for x in state['creationCounts']),'invalidDocument')
    require(isinstance(state.get('tasks'),list) and isinstance(state.get('myspace'),list),'invalidDocument')
    for task in state['tasks']:
        require(isinstance(task,dict) and isinstance(task.get('task_id'),str) and ID.fullmatch(task['task_id']) and isinstance(task.get('instruction'),str) and len(task['instruction'])<=1000 and isinstance(task.get('box_ids'),list) and all(isinstance(i,str) and ID.fullmatch(i) for i in task['box_ids']),'invalidDocument')
        require(type(task.get('revision'))==int and task['revision']>=0 and task.get('activeLayer') in [1,2,3] and type(task.get('applied'))==bool and type(task.get('received'))==bool,'invalidDocument')
        require(task.get('status') in ['saving','waiting','claimed','running','ready','applied','stale','failed','disconnected','noChange','question','aiPreview','discarded'],'invalidDocument')
    for p in state['myspace']:require(isinstance(p,dict) and isinstance(p.get('id'),str));patch_values(p['changes'],style=True)
    history=body.get('history');require(isinstance(history,dict) and set(history)=={'undo','redo'},'storageFormat')
    for kind in ['undo','redo']:
        require(isinstance(history[kind],list),'storageFormat')
        for frame in history[kind]:
            require(isinstance(frame,dict) and isinstance(frame.get('state'),dict),'storageFormat')
            prior={**state,**frame['state'],'design':frame['state'].get('design')};prior_body={'format':1,'state':prior,'history':{'undo':[],'redo':[]}}
            validate_body(prior_body)
    return body

class ProjectStore:
    def __init__(self,root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.cas=ContentAddressedArtifacts(self.root);self.lock=RLock();self.depth=0;self.lock_file=None
    @contextmanager
    def transaction(self):
        with self.lock:
            if not self.depth:
                self.lock_file=(self.root/'.projects.lock').open('a+b');os.chmod(self.root/'.projects.lock',0o600);fcntl.flock(self.lock_file,fcntl.LOCK_EX)
            self.depth+=1
            try:yield
            finally:
                self.depth-=1
                if not self.depth:
                    fcntl.flock(self.lock_file,fcntl.LOCK_UN);self.lock_file.close();self.lock_file=None
    def folder(self,project_id):
        require(isinstance(project_id,str) and UUID.fullmatch(project_id),'unknownProject')
        return self.root/'projects'/project_id
    def blob(self,value):
        return self.raw_blob(encoded(value))
    def raw_blob(self,raw):
        stage=self.cas.stage(raw,self.root/'staging')
        # stage/publish is existing code; add durability around publication.
        with stage.open('rb') as stream:os.fsync(stream.fileno())
        artifact=self.cas.publish(stage);sync_dir(self.cas.root)
        if stage.exists():stage.unlink()
        return artifact.sha256
    def raw(self,digest,limit):
        require(isinstance(digest,str) and HASH.fullmatch(digest),'designInvalidSource')
        path=self.cas.root/digest
        import stat
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
            with os.fdopen(fd,'rb') as stream:
                info=os.fstat(stream.fileno());require(stat.S_ISREG(info.st_mode) and info.st_size<=limit,'designMissingArtifact')
                raw=stream.read(limit+1)
        except OSError:raise ContractError('designMissingArtifact') from None
        require(len(raw)<=limit and hashlib.sha256(raw).hexdigest()==digest,'designMissingArtifact')
        return raw
    def import_design(self,packet):
        require(isinstance(packet,dict) and set(packet)<= {'preview_base64','html_base64','reference_viewport'} and 'preview_base64' in packet,'designInvalidSource')
        with self.transaction():
            preview=decode_upload(packet['preview_base64'],MAX_PNG)
            original=decode_upload(packet['html_base64'],MAX_HTML) if packet.get('html_base64') is not None else None
            value=imported(preview,original,packet.get('reference_viewport'))
            self.raw_blob(preview)
            if original is not None:self.raw_blob(original)
        return value
    def preview(self,digest):
        raw=self.raw(digest,MAX_PNG);png_size(raw);return raw
    def check_design_artifacts(self,body):
        seen={}
        states=[body['state']]+[frame['state'] for kind in ['undo','redo'] for frame in body['history'][kind]]
        for state in states:
            design=state.get('design')
            if design is None:continue
            key=(design['source']['artifact_sha256'],design['preview']['artifact_sha256'],design['source']['media_type'])
            if key not in seen:
                preview=self.preview(key[1]);source=design['source']
                entries=[] if source['media_type']=='image/png' else catalog(self.raw(key[0],MAX_HTML))
                seen[key]=(png_size(preview),entries)
            size,entries=seen[key]
            viewport=design['source']['reference_viewport']
            require(size['width']*viewport['height']==size['height']*viewport['width'],'designViewportMismatch')
            require(entries==design['catalog'] and (design['source']['media_type']!='image/png' or key[0]==key[1]),'designInvalidSource')
    def read_blob(self,digest):
        require(isinstance(digest,str) and HASH.fullmatch(digest),'storageCorrupt')
        raw=(self.cas.root/digest).read_bytes();require(hashlib.sha256(raw).hexdigest()==digest,'storageCorrupt');return json.loads(raw)
    def pack_frame(self,frame):
        data=deepcopy(frame);boxes=data.pop('boxes');myspace=data.pop('myspace')
        return self.blob({'frame_format':1,'data':data,'boxes_ref':self.blob(boxes),'myspace_ref':self.blob(myspace)})
    def unpack_frame(self,digest):
        data=self.read_blob(digest)
        if 'frame_format' not in data:return data # earlier format-1 inline frame
        require(data['frame_format']==1,'storageFormat')
        return {**data['data'],'boxes':self.read_blob(data['boxes_ref']),'myspace':self.read_blob(data['myspace_ref'])}
    def unpack(self,commit):
        require(commit.get('format')==FORMAT,'storageFormat')
        chunks=commit['chunks'];state=self.read_blob(chunks['document']);
        if 'boxes' in chunks:state['boxes']=self.read_blob(chunks['boxes'])
        state['myspace']=self.read_blob(chunks['myspace']);state['tasks']=self.read_blob(chunks['conversation']);state['ui']=self.read_blob(chunks['ui'])
        history={k:[{'state':self.unpack_frame(f['state']),'label':f['label']} for f in chunks['history'][k]] for k in ['undo','redo']}
        body=validate_body({'format':FORMAT,'state':state,'history':history});self.check_design_artifacts(body);return body
    def commits(self,project_id):
        folder=self.folder(project_id);require(folder.exists(),'unknownProject')
        valid=[];damaged=[];highest=0
        for path in sorted((folder/'commits').glob('*.json')):
            try:
                seq=int(path.name.split('-')[0]);highest=max(highest,seq)
                record=json.loads(path.read_bytes());payload=record['commit'];require(record['sha256']==hashlib.sha256(encoded(payload)).hexdigest(),'storageCorrupt');require(payload['project_id']==project_id and payload['sequence']==seq,'storageCorrupt')
                valid.append(payload)
            except ContractError as e:
                if str(e)=='storageFormat':raise
                damaged.append(path.name)
            except Exception:damaged.append(path.name)
        return sorted(valid,key=lambda x:x['sequence']),damaged,highest
    def read(self,project_id,snapshot_id=None):
        with self.transaction():
            commits,damaged,_=self.commits(project_id);require(bool(commits),'storageCorrupt')
            candidates=[c for c in commits if c['id']==snapshot_id] if snapshot_id else list(reversed(commits))
            require(bool(candidates),'unknownSnapshot')
            chosen=None;body=None
            for candidate in candidates:
                try:body=self.unpack(candidate);chosen=candidate;break
                except ContractError as e:
                    if str(e)=='storageFormat':raise
                    damaged.append(candidate['id'])
                except Exception:damaged.append(candidate['id'])
            require(chosen is not None,'storageCorrupt')
            return {'project_id':project_id,'head':chosen['id'] if not snapshot_id else self.read(project_id)['head'],'snapshot':chosen,'body':body,'warning':'storageCorrupt' if damaged else None,'damaged':damaged}
    def list(self):
        with self.transaction():
            result=[]
            for folder in (self.root/'projects').glob('*'):
                if not folder.is_dir() or not UUID.fullmatch(folder.name):continue
                try:
                    data=self.read(folder.name);c=data['snapshot'];result.append({'id':folder.name,'name':c['name'],'updated_at':c['at'],'head':data['head'],'warning':data['warning']})
                except Exception as exc:result.append({'id':folder.name,'name':folder.name[:8],'error':'storageFormat' if str(exc)=='storageFormat' else 'storageCorrupt'})
            return sorted(result,key=lambda x:x.get('updated_at',''),reverse=True)
    def history(self,project_id):
        with self.transaction():
            commits,damaged,_=self.commits(project_id)
            return {'items':[{k:v for k,v in c.items() if k!='chunks'} for c in reversed(commits)],'damaged':damaged}
    def save(self,project_id,body,meta,base=None):
        with self.transaction():
            validate_body(body);self.check_design_artifacts(body);require(isinstance(meta,dict) and len(encoded(meta))<20000,'invalidValues')
            folder=self.folder(project_id)
            if folder.exists():
                commits,damaged,highest=self.commits(project_id);head=self.read(project_id)['head'] if commits else None
                require(bool(commits),'storageCorrupt');require(head==base,'storageConflict')
            else:
                require(base is None,'storageConflict');folder.mkdir(parents=True,mode=0o700);commits=[];highest=0
            state=deepcopy(body['state']);myspace=state.pop('myspace');tasks=state.pop('tasks');ui=state.pop('ui');boxes=state.pop('boxes')
            chunks={'boxes':self.blob(boxes),'document':self.blob(state),'myspace':self.blob(myspace),'conversation':self.blob(tasks),'ui':self.blob(ui),
                    'history':{k:[{'state':self.pack_frame(f['state']),'label':f['label']} for f in body['history'][k]] for k in ['undo','redo']}}
            commit={'format':FORMAT,'project_id':project_id,'id':str(uuid4()),'sequence':highest+1,'at':datetime.now(timezone.utc).isoformat(),
                    'revision':state['revision'],'selection':state['selection'],'name':str(meta.get('name') or (commits[-1]['name'] if commits else 'Projekt'))[:120],
                    'kind':meta.get('kind','automatic'),'parent':base,'meta':deepcopy(meta),'chunks':chunks}
            record={'commit':commit,'sha256':hashlib.sha256(encoded(commit)).hexdigest()}
            atomic(folder/'commits'/f'{commit["sequence"]:012d}-{commit["id"]}.json',encoded(record))
            # Commit publication is the durable commit point. HEAD is a hint;
            # recovery scans valid commits, including one published before crash.
            try:atomic(folder/'HEAD',encoded({'format':FORMAT,'id':commit['id']}))
            except OSError:pass
            return {'project_id':project_id,'head':commit['id'],'snapshot':{k:v for k,v in commit.items() if k!='chunks'}}
