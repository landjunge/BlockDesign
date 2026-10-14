"""Repeatable v0.2 user acceptance in Chrome with private project/task storage.

Actual pointer/keyboard/UI paths. Live AI cases really call Whiteboard/Ollama.
Explicit negative HTTP fixtures only test refusal; storage-failure tests deny
actual filesystem writes. All artifacts remain ignored and local.
"""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
from urllib.request import urlopen
from uuid import uuid4
from playwright.sync_api import sync_playwright
import browser_acceptance as old
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/upgrade-acceptance';OUT.mkdir(parents=True,exist_ok=True)
DATA=OUT/'projects';URL='http://127.0.0.1:5192';RESULTS=[];SERVER=None

def start_server():
 global SERVER
 env={**os.environ,'BD_PROJECT_ROOT':str(DATA),'BD_TASK_ROOT':str(OUT/'tasks')}
 SERVER=subprocess.Popen(['/usr/local/bin/python3.12','scripts/server.py','--port','5192'],cwd=ROOT,env=env,stdout=(OUT/'server.log').open('a'),stderr=subprocess.STDOUT)
 for _ in range(100):
  try:
   with urlopen(URL+'/api/projects',timeout=1) as r:
    if r.status==200:return
  except Exception:time.sleep(.1)
 raise RuntimeError('test server unavailable')
def stop_server():
 global SERVER
 if SERVER:SERVER.terminate();SERVER.wait(timeout=10);SERVER=None

def state(p):return old.state(p)
def focus(p):old.focus(p)
def selected(p):return old.selected(p)
def point(p,x,y):return old.point(p,x,y)
def wait(p,expression,**args):p.wait_for_function('()=>('+expression+')',**args)
def fresh(p):
 p.goto(URL);wait(p,'!!window.blockDesigner');previous=p.evaluate('localStorage.getItem("blockdesigner.project.v1")');p.locator('#projects-panel button').click();p.wait_for_function('(old)=>localStorage.getItem("blockdesigner.project.v1")!==old',arg=previous);assert state(p)['boxes']==[];move_monitor(p,10,650)
def save_wait(p):wait(p,'document.querySelector("#save-indicator").textContent==="Lokal gesichert"',timeout=20000)
def api(p,path):return p.evaluate('async path=>{const r=await fetch(path);return await r.json();}',path)
def project_id(p):return p.evaluate('localStorage.getItem("blockdesigner.project.v1")')
def history(p):return api(p,f'/api/projects/{project_id(p)}/history')['items']
def move_monitor(p,x,y):
 r=p.locator('#monitor-handle').bounding_box();p.mouse.move(r['x']+24,r['y']+18);p.mouse.down();panel=p.locator('#monitor').bounding_box();p.mouse.move(r['x']+24+x-panel['x'],r['y']+18+y-panel['y'],steps=5);p.mouse.up()
def send_live(p,text):
 p.locator('#order').fill(text);p.locator('#send').click(timeout=30000);wait(p,'["applied","ready","question","aiPreview","failed","stale","noChange"].includes(blockDesigner.getState().tasks.at(-1)?.status)',timeout=220000)
 task=state(p)['tasks'][-1];assert task['status'] not in ['failed','stale','noChange'],task
 assert task.get('clarification',{}).get('origin')=='selection-guard' or task.get('evidence',{}).get('metrics',{}).get('eval_count',0)>0,task
 return task

def help_focus(p):
 focus(p);p.keyboard.press('b');before=state(p)['boxes'];p.keyboard.press('h');assert p.locator('#help-dialog').is_visible()
 registry=p.evaluate('async()=>{const m=await import("/src/input/shortcuts.js");return m.SHORTCUTS.map(s=>s.key)}');assert p.locator('#shortcut-list dt').all_text_contents()==registry
 p.keyboard.press('b');assert state(p)['boxes']==before;p.keyboard.press('Escape');assert p.locator('#canvas-scroll').evaluate('(e)=>e===document.activeElement')
 for selector in ['#order','#box-label','#box-type']:
  if selector!='#order' and not p.locator('#selection-panel').evaluate('(e)=>e.open'):p.locator('#selection-panel summary').click()
  p.locator(selector).fill('');p.locator(selector).press('h');p.locator(selector).press('b');p.locator(selector).press('Space');p.locator(selector).press('1');assert not p.locator('#help-dialog').is_visible();assert len(state(p)['boxes'])==1;assert state(p)['activeLayer']==1
 p.locator('#help').click();p.keyboard.press('Escape');assert p.locator('#help').evaluate('(e)=>e===document.activeElement')

def multi_group_bounds(p):
 focus(p);p.keyboard.press('b');a=selected(p);p.mouse.move(*point(p,500,320));p.keyboard.press('Space');p.mouse.move(*point(p,250,250));p.keyboard.press('Space');a=selected(p);p.keyboard.press('b');b=selected(p)
 p.mouse.click(*point(p,a['x']+25,a['y']+25));p.keyboard.down('Shift');p.mouse.click(*point(p,b['x']+25,b['y']+25));p.keyboard.up('Shift');before=state(p)['boxes'];p.keyboard.press('Space');assert state(p)['ui']['grabbed']==a['id'];p.mouse.move(*point(p,1100,800));p.keyboard.press('Space');after=state(p)['boxes'];assert after[0]['x']-before[0]['x']==after[1]['x']-before[1]['x'];assert after[0]['y']-before[0]['y']==after[1]['y']-before[1]['y'];assert max(b['x']+b['width'] for b in after)==1000;assert max(b['y']+b['height'] for b in after)==640
 p.locator('#selection-panel summary').click();p.locator('#group').click();parent=selected(p);child=state(p)['boxes'][0]
 # Select parent in its empty centre, then child via Shift; parent + child must
 # each move once even though the parent family already includes this child.
 p.mouse.click(*point(p,parent['x']+parent['width']/2,parent['y']+parent['height']/2));p.keyboard.down('Shift');p.mouse.click(*point(p,child['x']+25,child['y']+25));p.keyboard.up('Shift');assert state(p)['selection']==[parent['id'],child['id']]
 before=state(p)['boxes'];p.keyboard.press('Space');p.mouse.move(*point(p,-100,-100));p.keyboard.press('Space');after=state(p)['boxes'];dx=after[0]['x']-before[0]['x'];dy=after[0]['y']-before[0]['y'];assert all(b['x']-a['x']==dx and b['y']-a['y']==dy for a,b in zip(before,after));assert min(b['x'] for b in after)==0;assert min(b['y'] for b in after)==0
 focus(p);p.keyboard.press('Control+z');assert state(p)['boxes']==before;p.keyboard.press('Control+Shift+z');assert state(p)['boxes']==after

def layout_monitor_grid(p):
 widths=[]
 for selector in [None,'#toggle-myspace','#toggle-ai-space','#toggle-myspace','#toggle-ai-space']:
  if selector:p.locator(selector).click()
  widths.append(p.locator('#viewport').bounding_box()['width'])
 assert widths[1]-widths[0]==216;assert widths[2]-widths[1]==332;assert widths[4]==widths[0]
 for side in ['left','right']:
  edge=p.locator('.resize-edge.'+side);r=edge.bounding_box();p.mouse.move(r['x']+4,r['y']+60);p.mouse.down();p.mouse.move(r['x']+(60 if side=='left' else -60),r['y']+60,steps=5);p.mouse.up()
 before=p.locator('#viewport').bounding_box()['width'];assert before<widths[0]-80
 for x,y in [(20,4),(12,250),(1200,250),(1100,650)]:move_monitor(p,x,y);m=p.locator('#monitor').bounding_box();assert abs(m['x']-x)<1 and abs(m['y']-y)<1
 m=state(p)['ui']['monitor'];p.reload();wait(p,'!!window.blockDesigner');assert state(p)['ui']['monitor']['x']==m['x'];assert p.locator('#viewport').bounding_box()['width']==before
 p.set_viewport_size({'width':760,'height':500});p.wait_for_timeout(100);r=p.locator('#monitor').bounding_box();assert r['x']+r['width']<=760 and r['y']+r['height']<=500
 # Header remains available by its own scrolling, without sidebars.
 p.locator('#toggle-myspace').click();p.locator('#toggle-ai-space').click();p.locator('#help').click();p.keyboard.press('Escape');p.set_viewport_size({'width':1440,'height':900})
 for selector in ['#refine','#coarsen']:
  p.locator(selector).click();s=state(p);assert (s['grid']['spacing'],s['grid']['magnet'])==((10,1) if selector=='#refine' else (20,2))
 p.locator('#zoom').select_option('1.5');before=state(p)['document'];p.locator('#refine').click();assert state(p)['grid']['spacing']==10 and state(p)['document']==before
 for _ in range(5):p.locator('#refine').click()
 assert p.locator('#refine').is_disabled();assert state(p)['grid']['spacing']==.3125
 for _ in range(11):p.locator('#coarsen').click()
 assert state(p)['grid']['spacing']==640 and state(p)['grid']['magnet']==64;assert p.locator('#coarsen').is_disabled();assert not state(p)['ui']['error']

def palette_chat_language(p):
 for lang in ['en','de']:
  p.locator('[data-language="'+lang+'"]').click();assert p.locator('html').get_attribute('lang')==lang
  p.locator('#order').fill('Long instruction\n'*40);assert p.locator('#order').bounding_box()['height']==200
  p.locator('#order').fill('Short');assert p.locator('#order').bounding_box()['height']<60
 focus(p);p.keyboard.press('b');p.keyboard.down('a');palette=p.locator('#palette');assert palette.locator('button').count()==16;assert palette.bounding_box()['height']<=128
 p.locator('[data-palette="15"]').click();p.keyboard.up('a');assert selected(p)['color']=='#42a5f5';p.screenshot(path=str(OUT/'compact.png'))

def durable_restart_restore(p):
 focus(p);p.keyboard.press('b');save_wait(p);first=state(p);old_id=project_id(p);early=history(p)[0]['id']
 p.keyboard.press('b');save_wait(p);newer=state(p);ids={i['id'] for i in history(p)};assert len(newer['boxes'])==2
 p.reload();wait(p,'!!window.blockDesigner');assert state(p)['boxes']==newer['boxes'];stop_server();start_server();p.reload();wait(p,'!!window.blockDesigner');assert project_id(p)==old_id and state(p)['boxes']==newer['boxes']
 p.locator('#history').click();p.locator(f'[data-snapshot="{early}"][data-action="inspect"]').click();wait(p,'document.querySelectorAll(".history-preview .box").length===1');assert p.locator('.history-preview .box').get_attribute('title').find('475')>=0;p.locator(f'[data-snapshot="{early}"][data-action="restore"]').click();wait(p,'blockDesigner.getState().boxes.length===1');assert state(p)['boxes']==first['boxes'];assert {i['id'] for i in history(p)}>=ids;assert history(p)[0]['meta']['restore_of']==early;assert history(p)[1]['kind']=='beforeRestore';p.keyboard.press('Escape');assert p.locator('#history').evaluate('(e)=>e===document.activeElement');assert not state(p)['tasks'];previous=project_id(p);p.locator('#projects-panel button').click();p.wait_for_function('(old)=>localStorage.getItem("blockdesigner.project.v1")!==old',arg=previous);p.locator('#projects-panel select').select_option(old_id);wait(p,'blockDesigner.getState().boxes.length===1');assert project_id(p)==old_id

def real_conversation_preview_undo(p):
 focus(p);p.keyboard.press('b');task=send_live(p,'Beschrifte die ausgewählte Box mit Start.');assert task['status']=='applied' and selected(p)['label']=='Start'
 before=selected(p);follow=send_live(p,'Etwas schmaler.');assert follow['status'] in ['applied','aiPreview'],follow;
 if follow['status']=='aiPreview':p.locator('[data-action="commit"]').click();wait(p,'blockDesigner.getState().tasks.at(-1).status==="applied"')
 assert selected(p)['width']<before['width'];assert selected(p)['height']==before['height'];assert follow['parent_task_id']==task['task_id']
 # A compound change is necessarily previewed. Reject first, then explicitly
 # apply a new real request and undo the complete multi-attribute change.
 baseline=state(p)['boxes'];large=send_live(p,'Setze Breite auf 180 Pixel, Höhe auf 80 Pixel und Beschriftung auf Weiter.');assert large['status']=='aiPreview',large;assert state(p)['boxes']==baseline;assert state(p)['ui']['aiPreview'];p.locator('[data-action="discard"]').click();wait(p,'blockDesigner.getState().tasks.at(-1).status==="discarded"');assert state(p)['boxes']==baseline
 large2=send_live(p,'Setze Breite auf 180 Pixel, Höhe auf 80 Pixel und Beschriftung auf Weiter.');assert large2['status']=='aiPreview',large2;p.locator('[data-action="commit"]').click();wait(p,'blockDesigner.getState().tasks.at(-1).status==="applied"');applied=state(p)['boxes'];assert(selected(p)['width'],selected(p)['height'],selected(p)['label'])==(180,80,'Weiter')
 p.locator('#undo').click();assert state(p)['boxes']==baseline;p.locator('#redo').click();assert state(p)['boxes']==applied;save_wait(p)
 items=history(p);pre=[i for i in items if i['kind']=='preRequest'];assert len(pre)==4
 for task in state(p)['tasks']:
  assert any(i['id']==task['pre_snapshot'] and i['meta']['task_id']==task['task_id'] for i in pre)
 assert any(i['kind']=='resultSnapshot' and i['meta'].get('task_id')==large2['task_id'] for i in items);assert any(i['kind']=='discarded' for i in items)
 p.reload();wait(p,'!!window.blockDesigner');assert state(p)['boxes']==applied and len(state(p)['tasks'])==4;assert not state(p)['ui'].get('aiPreview');p.screenshot(path=str(OUT/'live-conversation.png'));sent=[];p.on('request',lambda r:sent.append(r.url) if r.url.endswith('/api/tasks') and r.method=='POST' else None);chosen=pre[0]['id'];p.locator('#history').click();p.locator(f'[data-snapshot="{chosen}"][data-action="restore"]').click();wait(p,'blockDesigner.getState().tasks.some(t=>t.archived)');p.wait_for_timeout(1200);assert not sent;assert all(t.get('archived') for t in state(p)['tasks']);assert {i['id'] for i in history(p)}>={i['id'] for i in items};p.keyboard.press('Escape')

def real_question_selection(p):
 # No selected object: an ambiguous object-specific command must ask, not edit.
 question=send_live(p,'Mach es passend.');assert question['status']=='question' and question['clarification']['question'],question;assert state(p)['boxes']==[];p.locator('[data-action="answer"]').click();assert p.locator('#order').evaluate('(e)=>e===document.activeElement')
 focus(p);p.keyboard.press('b');task=send_live(p,'Beschrifte die aktuell ausgewählte Box mit Eins.');assert task['status']=='applied';a=selected(p);focus(p);p.keyboard.press('b');b=selected(p)
 follow=send_live(p,'Etwas schmaler.');assert follow['selection_changed'] and follow['box_ids']==[b['id']];assert next(x for x in state(p)['boxes'] if x['id']==a['id'])==a;
 if follow['status']=='aiPreview':p.locator('[data-action="commit"]').click();wait(p,'blockDesigner.getState().tasks.at(-1).status==="applied"')
 assert selected(p)['width']<b['width'];assert p.locator('.task-card').first.get_by_text('Auswahl geändert;',exact=False).is_visible()

def real_model_clarification(p):
 focus(p);p.keyboard.press('b');before=state(p)['boxes'];task=send_live(p,'Ich bin unentschieden zwischen breiter und höher. Frage mich zuerst, welche Achse ich ändern möchte. Jetzt nichts ändern.');assert task['status']=='question' and task['reply'].get('question'),task;assert not task.get('clarification');assert state(p)['boxes']==before
 p.locator('[data-action="answer"]').click();assert p.locator('#reply-context').is_visible();answer=send_live(p,'Beschrifte die ausgewählte Box mit Geklärt.');assert answer['status']=='applied' and selected(p)['label']=='Geklärt';assert answer['parent_task_id']==task['task_id']

def disk_failure(p):
 focus(p);p.keyboard.press('b');save_wait(p);pid=project_id(p);commits=DATA/'projects'/pid/'commits';before=state(p)['boxes'];submitted=[]
 p.on('request',lambda r:submitted.append(r.url) if r.url.endswith('/api/tasks') and r.method=='POST' else None)
 commits.chmod(0o500)
 try:
  p.locator('#order').fill('Beschrifte mit Ungesichert.');p.locator('#send').click();wait(p,'blockDesigner.getState().tasks.at(-1)?.status==="failed"');assert not submitted;assert state(p)['boxes']==before;assert 'Sicherung fehlgeschlagen' in p.locator('#save-indicator').inner_text()
 finally:commits.chmod(0o700)
 # Let a genuine KI produce a preview, then deny the result commit. No model
 # fixture counts as AI here; actual disk permissions cause the save failure.
 task=send_live(p,'Setze Breite auf 150 Pixel und Höhe auf 90 Pixel.');assert task['status']=='aiPreview',task;commits.chmod(0o500)
 try:
  p.locator('[data-action="commit"]').click();wait(p,'blockDesigner.getState().tasks.at(-1).error==="saveFailed"');assert state(p)['boxes']==before;assert not state(p)['tasks'][-1]['applied'];assert 'Sicherung fehlgeschlagen' in p.locator('#save-indicator').inner_text()
 finally:commits.chmod(0o700)
 p.locator('[data-action="discard"]').click();wait(p,'blockDesigner.getState().tasks.at(-1).status==="discarded"');save_wait(p)

def competing_tabs(p):
 focus(p);p.keyboard.press('b');save_wait(p);q=p.context.browser.new_page(viewport={'width':1440,'height':900})
 try:
  q.goto(URL);wait(q,'!!window.blockDesigner');assert project_id(q)==project_id(p);focus(p);p.keyboard.press('b');save_wait(p);winner=state(p)['boxes'];focus(q);q.keyboard.press('b');wait(q,'document.querySelector("#save-indicator").textContent.includes("anderer Tab")');assert state(q)['boxes']!=winner;assert api(p,f'/api/projects/{project_id(p)}')['body']['state']['boxes']==winner
 finally:q.close()

def browser_corrupt_recovery(p):
 focus(p);p.keyboard.press('b');save_wait(p);good=state(p)['boxes'];p.keyboard.press('b');save_wait(p);pid=project_id(p);files=sorted((DATA/'projects'/pid/'commits').glob('*.json'));damaged=files[-1];damaged.write_text('{interrupted write');(damaged.parent/'.interrupted.tmp').write_text('{')
 p.reload();wait(p,'!!window.blockDesigner');assert state(p)['boxes']==good;assert 'storageCorrupt'==state(p)['ui']['notice'];assert damaged.exists();assert 'Beschädigter Stand' in p.locator('#status').inner_text()

CASES=[('BU-HELP-FOCUS',help_focus),('BU-MULTI-FAMILY-BOUNDS',multi_group_bounds),('BU-SIDEBARS-MONITOR-GRID',layout_monitor_grid),('BU-PALETTE-CHAT-DE-EN',palette_chat_language),('BU-DURABLE-RESTART-RESTORE',durable_restart_restore),('BU-REAL-CONVERSATION-PREVIEW-UNDO',real_conversation_preview_undo),('BU-REAL-QUESTION-SELECTION',real_question_selection),('BU-REAL-MODEL-CLARIFICATION',real_model_clarification),('BU-DISK-FAILURE',disk_failure),('BU-COMPETING-TABS',competing_tabs),('BU-CORRUPTION-RECOVERY',browser_corrupt_recovery)]
def main():
 chosen=set(sys.argv[1:]);start_server();failed=0
 try:
  with sync_playwright() as play:
   browser=play.chromium.launch(channel='chrome')
   for identity,fn in CASES:
    if chosen and identity not in chosen:continue
    page=browser.new_page(viewport={'width':1440,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));started=time.time()
    try:fresh(page);fn(page);assert not errors,errors;row={'id':identity,'status':'bestanden','seconds':round(time.time()-started,2)}
    except Exception:failed+=1;row={'id':identity,'status':'fehlgeschlagen','seconds':round(time.time()-started,2),'error':traceback.format_exc()};page.screenshot(path=str(OUT/(identity+'-failure.png')))
    RESULTS.append(row);print(json.dumps(row,ensure_ascii=False),flush=True);(OUT/'results.json').write_text(json.dumps({'browser':browser.version,'results':RESULTS},ensure_ascii=False,indent=2));
    with (OUT/'history.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    page.close()
   browser.close()
 finally:stop_server()
 return int(bool(failed))
if __name__=='__main__':raise SystemExit(main())
