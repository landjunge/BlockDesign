"""Product-specific Whiteboard adapter, using the existing local Ollama path.

No agent spawning, tool execution, arbitrary model code, credential handling or
general-purpose scheduling. Responses are untrusted declarative data.
"""
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import re
from threading import RLock, Event, Thread
import time
from uuid import uuid4
from host import Host, PROJECT
from threaddesk.services.ollama_local import complete, default_transport, list_models
from threaddesk.services.hausmeister import Hausmeister
from threaddesk.core.secrets import reject_secrets

PATCH_KEYS={'x','y','width','height','radius','color','paletteIndex','brightness','borderColor','borderWidth','font','label','type'}
STYLE_KEYS=PATCH_KEYS-{'x','y'}
PALETTE=['#000000','#808080','#c0c0c0','#ffffff','#800000','#ff0000','#ff8000','#ffff00','#808000','#008000','#00ff00','#008080','#00ffff','#000080','#42a5f5','#800080']
HEX=re.compile(r'#[0-9a-fA-F]{6}\Z')
ID=re.compile(r'[A-Za-z0-9_-]{1,100}\Z')
class ContractError(ValueError): pass

def require(ok, code='invalidReply'):
    if not ok: raise ContractError(code)
def number(value):
    return type(value) in (float,int) and math.isfinite(value)
def exact(value, keys):
    require(isinstance(value,dict) and set(value)==set(keys))
def patch_values(value, style=False):
    require(isinstance(value,dict) and 0<len(value) and set(value)<=(STYLE_KEYS if style else PATCH_KEYS))
    for key,v in value.items():
        if key in {'x','y','width','height','radius','brightness','borderWidth'}: require(number(v))
        if key in {'color','borderColor'}:require(isinstance(v,str) and HEX.fullmatch(v))
        if key=='paletteIndex':require(v is None or (type(v)==int and 1<=v<=16))
        if key=='label':require(isinstance(v,str) and len(v)<=4000)
        if key=='type':require(isinstance(v,str) and bool(v.strip()) and len(v)<=80)
        if key=='font':
            require(isinstance(v,dict) and bool(v) and set(v)<={'family','size','color'})
            if 'family' in v:require(v['family'] in ['system-ui','sans-serif','serif','monospace'])
            if 'size' in v:require(number(v['size']) and 4<=v['size']<=200)
            if 'color' in v:require(isinstance(v['color'],str) and HEX.fullmatch(v['color']))
    for key,lo,hi in [('width',4,10000),('height',4,10000),('radius',0,1000),('brightness',-100,100),('borderWidth',0,20)]:
        if key in value:require(lo<=value[key]<=hi)
    for key in ['x','y']:
        if key in value:require(value[key]>=0)

def grid_values(grid):
    exact(grid,{'spacing','magnet','enabled'})
    require(number(grid['spacing']) and .25<=grid['spacing']<=1000 and number(grid['magnet']) and 0<=grid['magnet']<=grid['spacing']/2 and type(grid['enabled'])==bool)

def validate_snapshot(s):
    exact(s,{'version','revision','document','boxes','selection','activeLayer','grid','coordinates','zoom','language'})
    require(type(s['version'])==int and s['version']==1 and type(s['revision'])==int and s['revision']>=0 and type(s['activeLayer'])==int and s['activeLayer'] in [1,2,3])
    exact(s['document'],{'width','height'})
    require(all(number(s['document'][k]) and 50<=s['document'][k]<=10000 for k in ['width','height']))
    require(s['coordinates']=={'origin':[0,0],'x':'right','y':'down','unit':'px','pixel_scale':1})
    require(number(s['zoom']) and .25<=s['zoom']<=2 and s['language'] in ['de','en'])
    require(isinstance(s['boxes'],list) and len(s['boxes'])<=100 and isinstance(s['selection'],list) and len(s['selection'])<=100)
    grid_values(s['grid']); ids=set();numbers=set()
    for b in s['boxes']:
        exact(b,PATCH_KEYS|{'id','number','orientation','layer','parentId'})
        require(isinstance(b['id'],str) and ID.fullmatch(b['id']) and b['id'] not in ids and type(b['number'])==int and b['number']>0 and b['number'] not in numbers)
        ids.add(b['id']);numbers.add(b['number']);require(type(b['layer'])==int and b['layer'] in [1,2,3])
        require(isinstance(b['orientation'],str) and len(b['orientation'])<100)
        patch_values({k:b[k] for k in PATCH_KEYS}); exact(b['font'],{'family','size','color'})
        require(b['x']+b['width']<=s['document']['width']+1e-8 and b['y']+b['height']<=s['document']['height']+1e-8)
        if b['paletteIndex'] is not None:require(b['color'].lower()==PALETTE[b['paletteIndex']-1])
    require(len(set(s['selection']))==len(s['selection']) and all(i in ids for i in s['selection']))
    boxes={b['id']:b for b in s['boxes']}
    require(all(boxes[i]['layer']==s['activeLayer'] for i in s['selection']))
    for b in s['boxes']:
        seen={b['id']};p=b
        while p['parentId'] is not None:
            require(p['parentId'] in boxes)
            p=boxes[p['parentId']]; require(p['id'] not in seen and p['type']=='Modul' and p['layer']==b['layer'])
            seen.add(p['id'])
    return s

def validate_request(packet):
    exact(packet,{'task_id','instruction','box_ids','revision','snapshot'})
    require(isinstance(packet['task_id'],str) and ID.fullmatch(packet['task_id']),'unknownTask')
    require(isinstance(packet['instruction'],str) and 0<len(packet['instruction'].strip())<=1000,'emptyOrder')
    reject_secrets(packet['instruction']);validate_snapshot(packet['snapshot'])
    require(packet['revision']==packet['snapshot']['revision'] and packet['box_ids']==packet['snapshot']['selection'],'invalidTargets')
    # The existing host has a 16k metadata contract; fail visibly rather than truncate.
    require(len(json.dumps(packet,ensure_ascii=False))<=13500,'contextTooLarge')
    # UTF-8 bytes give a conservative token upper bound; no silent context truncation.
    require(len(SYSTEM_PROMPT.encode())+len(prompt(packet).encode())+800+100<=4096,'contextTooLarge')
    return packet

def descendants(boxes, identity):
    result=[]
    for b in boxes:
        if b['parentId']==identity: result.extend([b]+descendants(boxes,b['id']))
    return result

def validate_reply(raw, packet):
    if isinstance(raw,str):
        require(len(raw)<=14000);raw=json.loads(raw)
    exact(raw,{'summary','actions','proposals'})
    require(isinstance(raw['summary'],str) and 0<len(raw['summary'])<=1500)
    require(isinstance(raw['actions'],list) and len(raw['actions'])<=100 and isinstance(raw['proposals'],list) and len(raw['proposals'])<=100)
    working=deepcopy(packet['snapshot']);boxes={b['id']:b for b in working['boxes']}
    for action in raw['actions']:
        require(isinstance(action,dict))
        kind=action.get('type')
        if kind=='grid':
            exact(action,{'type','spacing','magnet'})
            grid_values({'spacing':action['spacing'],'magnet':action['magnet'],'enabled':True});continue
        require(action.get('box_id') in packet['box_ids'],'invalidTargets')
        b=boxes[action['box_id']];require(b['layer']==working['activeLayer'],'layerLocked')
        if kind=='patch':
            exact(action,{'type','box_id','changes'});changes=action['changes'];patch_values(changes)
            family=descendants(working['boxes'],b['id'])
            if family and changes.get('type',b['type'])!='Modul':raise ContractError('parentHasChildren')
            dx=changes.get('x',b['x'])-b['x'];dy=changes.get('y',b['y'])-b['y']
            for child in family:child['x']+=dx;child['y']+=dy
            font={**b['font'],**changes.get('font',{})}
            b.update(deepcopy(changes));b['font']=font
            if changes.get('paletteIndex') is not None:b['color']=PALETTE[changes['paletteIndex']-1]
            elif 'color' in changes:
                b['color']=changes['color'].lower();b['paletteIndex']=PALETTE.index(b['color'])+1 if b['color'] in PALETTE else None
            if b['type']=='Modul':
                for child in family:
                    if 'color' in changes or 'paletteIndex' in changes:child.update(color=b['color'],paletteIndex=b['paletteIndex'])
                    if 'brightness' in changes:child['brightness']=b['brightness']
        elif kind=='scale':
            exact(action,{'type','box_id','factor'});require(number(action['factor']) and 0<action['factor']<=10)
            factor=max(max(4/b['width'],4/b['height']),min(action['factor'],(working['document']['width']-b['x'])/b['width'],(working['document']['height']-b['y'])/b['height']))
            b['width']*=factor;b['height']*=factor
        else:raise ContractError('invalidAction')
    validate_snapshot(working)
    proposals=[]
    for p in raw['proposals']:
        exact(p,{'title','description','changes'})
        require(isinstance(p['title'],str) and 0<len(p['title'])<=100 and isinstance(p['description'],str) and len(p['description'])<=500)
        patch_values(p['changes'],style=True)
        proposals.append({**deepcopy(p),'id':str(uuid4()),'source_task':packet['task_id']})
    reply={'version':1,'task_id':packet['task_id'],'revision':packet['revision'],'box_ids':packet['box_ids'],
           'summary':raw['summary'],'actions':raw['actions'],'proposals':proposals}
    require(len(json.dumps(reply,ensure_ascii=False))<=13500,'contextTooLarge')
    reject_secrets(json.dumps(reply,ensure_ascii=False));return reply

SYSTEM_PROMPT = """You are a box design editor. Fulfill the user instruction by returning actual edits or design proposals as JSON.
Reply with exactly 3 keys: summary (brief text), actions (array of edits), proposals (array of suggestions).
Do not merely describe edits: a requested change MUST appear in actions.
Patch example: {"type":"patch","box_id":"exact selected id","changes":{"label":"requested text"}}.
Other patch attributes: type, x,y,width,height,radius,color (#RRGGBB design fill), borderColor,borderWidth,brightness,font (family,size,color).
Scale edit: {"type":"scale","box_id":"exact selected id","factor":1.1}; smaller factor 0.9090909090909091.
Grid edit: {"type":"grid","spacing":10,"magnet":1}; finer halves both existing values.
A proposal has title,description,changes (style attributes without x/y). For requested suggestions return proposals, no immediate actions. Give useful different designs.
Only edit selected_ids, only active layer; preserve other attributes and identity. Min size 4px; stay within document bounds. Never execute code or add functions. Types are labels.
"""
def prompt(packet):
    snapshot=packet['snapshot'];selected=set(packet['box_ids'])
    targets=[b for b in snapshot['boxes'] if b['id'] in selected]
    children=[{k:b[k] for k in ['x','y','width','height','layer']} for target in targets for b in descendants(snapshot['boxes'],target['id'])]
    return json.dumps({'instruction':packet['instruction'],'selected_ids':packet['box_ids'],'revision':packet['revision'],
        'targets':targets,'children':children,'document':snapshot['document'],'activeLayer':snapshot['activeLayer'],
        'grid':snapshot['grid'],'coordinates':snapshot['coordinates'],'zoom':snapshot['zoom'],'language':snapshot['language']},ensure_ascii=False)


class AIAdapter:
    def __init__(self,host,executor=None):
        self.host=host;self.jobs={};self.lock=RLock();self.pool=ThreadPoolExecutor(max_workers=1);self.executor=executor
        self.config=json.loads((PROJECT/'ai-config.json').read_text())
        self.folder=PROJECT/'.runtime/tasks';self.folder.mkdir(parents=True,exist_ok=True)
        for p in self.folder.glob('*.json'):
            data=json.loads(p.read_text());self.jobs[data['task_id']]=data
            if data['status'] not in ['ready','failed']:
                data.update(status='failed',error='disconnected');self.save(data)
    def status(self):
        status=Hausmeister(self.host.store).status()
        selected=self.config['model']
        status['model']=selected
        self.host.context(lambda c:c.read_whiteboard(self.host.thread_id))
        return {'ok':status['enabled'] and status['ollama_ok'] and status['model'] in status['models'],
                'model':status['model'],'thread_id':self.host.thread_id,'version':'0.1.0','busy':any(j['status'] in ['waiting','claimed','running'] for j in self.jobs.values())}
    def save(self,job):
        path=self.folder/(job['task_id']+'.json');temp=path.with_suffix('.tmp');temp.write_text(json.dumps(job,ensure_ascii=False));temp.chmod(0o600);temp.replace(path)
    def public(self,job):return {k:deepcopy(v) for k,v in job.items() if k not in {'packet','raw_response'}}
    def submit(self,packet):
        validate_request(packet)
        with self.lock:
            task=packet['task_id']
            if task in self.jobs:
                require(self.jobs[task]['packet']==packet,'taskConflict');return self.public(self.jobs[task])
            require(not any(j['status'] in ['waiting','claimed','running'] for j in self.jobs.values()),'busy')
            require(self.status()['ok'],'offline')
            entry=self.host.append('task',packet['instruction'],task,'BD-AI.1',actor_type='human',metadata={'role':'box-task','request':packet},key='bd-task-'+task)
            job={'task_id':task,'status':'waiting','entry_id':entry['id'],'packet':deepcopy(packet),'created_at':time.time()}
            self.jobs[task]=job;self.save(job);self.pool.submit(self.work,task);return self.public(job)
    def get(self,task):
        with self.lock:
            require(task in self.jobs,'unknownTask');return self.public(self.jobs[task])
    def update(self,task,**changes):
        with self.lock:self.jobs[task].update(changes);self.save(self.jobs[task])
    def work(self,task):
        job=self.jobs[task];run_id='bd-local-'+str(uuid4());stop=Event()
        try:
            # Actual delivery: retrieve the exact immutable request through the host.
            entry=next(e for e in self.host.entries() if e['id']==job['entry_id'])
            packet=validate_request(entry['metadata']['request'])
            require(packet==job['packet'],'taskConflict')
            model=self.status()['model']
            self.host.append('claimed','Auftrag tatsächlich vom Whiteboard gelesen; lokale KI übernimmt die ausgewählten Boxen.',task,'BD-AI.1',actor_type='local-assistant',run_id=run_id,
                             metadata={'request_entry_id':entry['id'],'revision':packet['revision'],'box_ids':packet['box_ids'],'model':model,'choice_reason':self.config['reason']},key='bd-claimed-'+task)
            self.update(task,status='running',run_id=run_id,model=model)
            def heartbeat():
                while not stop.wait(30):
                    self.host.append('progress','Lokaler Modellaufruf läuft; noch keine Antwort oder Änderung bestätigt.',task,'BD-AI.1',actor_type='local-assistant',run_id=run_id)
            Thread(target=heartbeat,daemon=True).start()
            metrics={}
            def transport(url,body,timeout):
                body={**body,'messages':[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':prompt(packet)}],'format':'json','options':{'temperature':0,'num_predict':800,'num_ctx':4096}}
                response=default_transport(url,body,timeout)
                metrics.update({k:response.get(k) for k in ['model','eval_count','prompt_eval_count','total_duration']})
                return response
            raw=self.executor(packet) if self.executor else complete(model,prompt(packet),transport=transport,timeout=180)
            self.update(task,raw_response=reject_secrets(raw))
            reply=validate_reply(raw,packet)
            evidence={'model':model,'response_sha256':hashlib.sha256(raw.encode()).hexdigest(),'metrics':metrics}
            result=self.host.append('result',reply['summary'],task,'BD-AI.2',actor_type='local-assistant',run_id=run_id,
                                    metadata={'role':'box-result','reply':reply,'evidence':evidence},key='bd-result-'+task)
            returned=next(e for e in self.host.entries() if e['id']==result['id'])
            require(returned['metadata']['reply']==reply)
            self.update(task,status='ready',reply=reply,result_entry_id=result['id'],evidence=evidence)
        except Exception as exc:
            code=str(exc) if isinstance(exc,ContractError) else 'offline' if 'ollama' in str(exc) else 'invalidReply'
            self.update(task,status='failed',error=code)
            try:self.host.append('problem','KI-Auftrag fehlgeschlagen: '+code+'. Keine Änderung übernommen.',task,'BD-AI.2',actor_type='local-assistant',run_id=run_id,key='bd-problem-'+task)
            except Exception:pass
        finally:stop.set()
