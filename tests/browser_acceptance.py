"""Real Chrome user flows, synthetic documents. AI success uses live Ollama.
Negative transport/response fixtures are explicitly identified and never count as
live AI success. The application exposes only read-only state inspection.
"""
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/acceptance'
URL=os.environ.get('BD_TEST_URL','http://127.0.0.1:5190')
RESULTS=[]
def state(p):return p.evaluate('window.blockDesigner.getState()')
def focus(p):p.locator('#canvas-scroll').focus()
def selected(p):
 s=state(p);return next(b for b in s['boxes'] if b['id']==s['selection'][0])
def near(a,b):assert math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-7),(a,b)
def point(p,x,y):
 r=p.locator('#canvas').bounding_box();z=state(p)['ui']['zoom'];return r['x']+x*z,r['y']+y*z

def create_layers(p):
 focus(p);p.keyboard.press('b');p.keyboard.press('b');s=state(p)
 assert [(b['x'],b['y'],b['width'],b['height']) for b in s['boxes']]==[(475,295,50,50),(480,300,50,50)]
 assert len({b['id'] for b in s['boxes']})==2
 p.keyboard.press('2');p.keyboard.press('b');s=state(p);assert [b['layer'] for b in s['boxes']]==[1,1,2]
 assert [b['number'] for b in s['boxes']]==[1,2,3];assert p.locator('.box.locked').count()==2
 assert p.locator('.box-center').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).width==="1px"&&getComputedStyle(e).height==="1px")')
 p.keyboard.press('3');assert p.locator('.box:not(.locked)').count()==0
 p.keyboard.press('1');assert state(p)['selection']==[]
 p.locator('#canvas-scroll').focus();p.keyboard.press('Space');assert selected(p)['number']==1
 p.keyboard.press('Space')

def movement_axes(p):
 focus(p);p.keyboard.press('b');x,y=point(p,500,320);p.mouse.move(x,y);p.keyboard.press('Space')
 assert state(p)['ui']['grabbed']==selected(p)['id'];assert not p.locator('.gripper').is_hidden()
 p.mouse.move(x+75,y+60);s=selected(p);assert (s['x'],s['y'])==(575,375)
 p.keyboard.down('d');p.mouse.move(x+90,y+90);p.keyboard.up('d');s=selected(p);assert(s['width'],s['height'])==(50,90);assert(s['x'],s['y'])==(575,375)
 p.keyboard.down('f');p.mouse.move(x+120,y+110);p.keyboard.up('f');s=selected(p);assert(s['width'],s['height'])==(90,90)
 p.keyboard.down('d');p.keyboard.down('f');before=state(p)['boxes'];p.mouse.move(x+150,y+150);assert state(p)['boxes']==before;p.keyboard.up('f');p.keyboard.up('d')
 p.keyboard.press('Space');assert state(p)['ui']['grabbed'] is None
 assert 'exakt' in p.locator('#status').inner_text()

def scale_bounds(p):
 focus(p);p.keyboard.press('b');p.keyboard.press('+');near(selected(p)['width'],55);p.keyboard.press('-');near(selected(p)['width'],50)
 for _ in range(35):p.keyboard.press('+')
 s=selected(p);near(s['height'],345);near(s['width'],345);assert(s['x'],s['y'])==(475,295)
 for _ in range(75):p.keyboard.press('-')
 near(selected(p)['width'],4);near(selected(p)['height'],4)
 x,y=point(p,selected(p)['x']+2,selected(p)['y']+2);p.mouse.move(x,y);p.keyboard.press('Space');p.mouse.move(*point(p,-10,-10));s=selected(p);assert(s['x'],s['y'])==(0,0)
 p.mouse.move(*point(p,1005,645));s=selected(p);assert(s['x'],s['y'])==(996,636);p.keyboard.press('Space')


def grid_monitor_zoom(p):
 focus(p);p.keyboard.press('b');x,y=point(p,500,320);p.mouse.move(x,y);p.keyboard.press('Space');p.mouse.move(x+4.5,y+4.5);s=selected(p);assert(s['x'],s['y'])==(480,300);p.keyboard.press('Space')
 p.locator('#refine').click();assert state(p)['grid']['spacing']==10;assert state(p)['grid']['magnet']==1
 b=selected(p);before=state(p)['boxes'];p.locator('#zoom').select_option('1.5');assert state(p)['boxes']==before
 handle=p.locator('#monitor-handle');r=handle.bounding_box();p.mouse.move(r['x']+30,r['y']+20);p.mouse.down();p.mouse.move(r['x']+110,r['y']+70,steps=5);p.mouse.up();m=state(p)['ui']['monitor'];assert m['x']>16 and m['y']>16
 handle.focus();p.keyboard.press('ArrowRight');assert state(p)['ui']['monitor']['x']==m['x']+8
 # Clear selection without selecting another box; monitor retains last values.
 cx,cy=point(p,100,300);p.mouse.click(cx,cy);assert not state(p)['selection'];assert state(p)['ui']['monitor']['last']['id']==b['id']
 values=p.locator('#monitor-values dd').evaluate_all('(es)=>es.map(e=>e.dataset.value)');assert values[1:5]==[str(b[k]) for k in ['x','y','width','height']]


def transfer_group(p):
 focus(p);p.keyboard.press('b');p.locator('#selection-panel summary').click();p.locator('#box-type').fill('Button');p.locator('#box-type').press('Tab');p.locator('#box-label').fill('Weiter');p.locator('#box-label').press('Tab');a=selected(p)
 # Move first box left to separate hit targets.
 focus(p);x,y=point(p,500,320);p.mouse.move(x,y);p.keyboard.press('Space');p.mouse.move(x-150,y);p.keyboard.press('Space');a=selected(p)
 p.keyboard.press('b');b=selected(p)
 ax,ay=point(p,a['x']+25,a['y']+25);bx,by=point(p,b['x']+25,b['y']+25);p.mouse.click(ax,ay);p.keyboard.down('Shift');p.mouse.click(bx,by);p.keyboard.up('Shift');assert state(p)['selection']==[a['id'],b['id']]
 p.keyboard.press('t');targets=state(p)['boxes'];assert targets[1]['label']=='Weiter';assert targets[1]['x']==b['x'];assert targets[1]['orientation']==b['orientation']
 p.locator('#group').click();s=state(p);module=selected(p);assert module['type']=='Modul';assert all(child['parentId']==module['id'] for child in s['boxes'][:2])
 focus(p);mx,my=point(p,module['x']+module['width']/2,module['y']+module['height']/2);p.mouse.move(mx,my);p.keyboard.press('Space');assert state(p)['ui']['grabbed']==module['id']
 before=state(p)['boxes'];p.mouse.move(mx+60,my+30);p.keyboard.press('Space');after=state(p)['boxes'];near(after[0]['x']-before[0]['x'],after[2]['x']-before[2]['x']);near(after[1]['y']-before[1]['y'],after[2]['y']-before[2]['y'])
 children=after[:2];p.keyboard.press('-');assert state(p)['boxes'][:2]==children
 p.locator('[data-view="design"]').click()
 child=state(p)['boxes'][0];cx,cy=point(p,child['x']+child['width']/2,child['y']+child['height']/2)
 hit=p.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("[data-box-id]")?.dataset.boxId',[cx,cy]);assert hit==child['id'],hit
 assert p.locator(f'[data-box-id="{child["id"]}"] .box-content').inner_text()=='Weiter'
 p.locator('#box-type').fill('Button');p.locator('#box-type').press('Tab');assert selected(p)['type']=='Modul';assert state(p)['ui']['error']


def attribute_focus_views(p):
 focus(p);p.keyboard.press('b');b=selected(p);revision=state(p)['revision'];p.keyboard.down('a');assert state(p)['ui']['preview']
 p.locator('[data-palette="15"]').click();before_scroll=p.locator('#ai-space').evaluate('(e)=>e.scrollTop');p.mouse.wheel(0,-120);assert state(p)['ui']['preview']['brightness']==1;assert selected(p)['color']==b['color'];assert p.locator('#ai-space').evaluate('(e)=>e.scrollTop')==before_scroll
 p.keyboard.up('a');assert selected(p)['color']=='#42a5f5';assert selected(p)['brightness']==1;assert state(p)['revision']==revision+1
 p.locator('[data-view="design"]').click();assert p.locator('.box-visual').evaluate('(e)=>getComputedStyle(e).backgroundColor')!='rgba(0, 0, 0, 0)'
 p.locator('[data-view="structure"]').click();assert p.locator('.box-visual').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgba(0, 0, 0, 0)'
 focus(p);before=selected(p);p.keyboard.down('a');p.locator('[data-palette="6"]').click();p.keyboard.press('Escape');p.keyboard.up('a');assert selected(p)==before
 # Keys inside text input never invoke document shortcuts.
 p.locator('#order').fill('');p.locator('#order').press('b');p.locator('#order').press('1');p.locator('#order').press('Space');p.locator('#order').press('d');p.locator('#order').press('f');p.locator('#order').press('t');p.locator('#order').press('a');p.locator('#order').press('+');assert len(state(p)['boxes'])==1;assert state(p)['activeLayer']==1;assert not state(p)['ui']['preview'];assert not state(p)['ui']['grabbed']
 p.locator('#help').click();assert p.locator('#help-dialog').is_visible();assert p.evaluate('document.activeElement.closest("dialog")?.id')=='help-dialog';p.keyboard.press('b');assert len(state(p)['boxes'])==1;p.keyboard.press('Escape');assert not p.locator('#help-dialog').is_visible();assert p.locator('#help').evaluate('(e)=>e===document.activeElement')


def desktop_language_longtext(p):
 focus(p);p.keyboard.press('b');p.locator('#selection-panel summary').click();long='Sehr langer Text <script>window.bad=true</script> '+('Beschreibung '*150);p.locator('#box-label').fill(long);p.locator('#box-label').press('Tab');assert selected(p)['label']==long
 p.locator('#box-type').fill('Eigener freier Typ');p.locator('#box-type').press('Tab');identity=selected(p)['id'];assert selected(p)['type']=='Eigener freier Typ';assert not p.evaluate('window.bad || false')
 for lang in ['de','en']:
  p.locator('#language').select_option(lang);assert p.locator('html').get_attribute('lang')==lang
  for width,height in [(1440,900),(1180,760),(900,600)]:
   p.set_viewport_size({'width':width,'height':height});p.locator('#send').scroll_into_view_if_needed();assert p.locator('#send').is_visible();assert selected(p)['id']==identity;assert state(p)['document']=={'width':1000,'height':640}
   # No automatic mobile stacking; all three columns retain horizontal order.
   r=p.locator('.spaces').evaluate('(e)=>getComputedStyle(e).gridTemplateColumns');assert len(r.split())==3
   wrong=p.locator('.np-button,input,select').evaluate_all('(es)=>es.filter(e=>e.checkVisibility()&&Math.abs(e.getBoundingClientRect().height-40)>1).map(e=>e.id)');assert not wrong,wrong
 p.set_viewport_size({'width':1440,'height':900});p.locator('[data-view="design"]').click();p.locator('#canvas-scroll').scroll_into_view_if_needed();p.screenshot(path=str(OUT/'long-text-en.png'))


def send_live(p,instruction):
 p.wait_for_function('() => !document.querySelector("#send").disabled',timeout=20000)
 p.locator('#order').fill(instruction);p.locator('#send').click()
 p.wait_for_function('() => window.blockDesigner.getState().tasks.length && ["applied","ready","noChange","stale","failed","disconnected"].includes(window.blockDesigner.getState().tasks.at(-1).status)',timeout=215000)
 task=state(p)['tasks'][-1];assert task['status'] not in ['failed','disconnected'],task
 assert task.get('evidence',{}).get('metrics',{}).get('eval_count',0)>0,task
 return task

def live_ai_change(p):
 # One continuous integration journey across every editing module and the real AI adapter.
 focus(p);p.keyboard.press('2');p.keyboard.press('b');p.keyboard.press('3');p.keyboard.press('b');p.keyboard.press('1')
 movement_axes(p);p.keyboard.press('+');p.keyboard.press('-');p.locator('#refine').click();p.locator('#selection-panel summary').click();p.locator('#box-type').fill('Button');p.locator('#box-type').press('Tab');p.locator('#box-label').fill('Vorlage');p.locator('#box-label').press('Tab');a=selected(p)
 focus(p);p.keyboard.press('b');b=selected(p);p.mouse.click(*point(p,a['x']+a['width']/2,a['y']+a['height']/2));p.keyboard.down('Shift');p.mouse.click(*point(p,b['x']+25,b['y']+25));p.keyboard.up('Shift');p.keyboard.press('t');p.locator('#group').click();assert selected(p)['type']=='Modul'
 focus(p);p.keyboard.down('a');p.locator('[data-palette="15"]').click();p.keyboard.up('a');p.locator('[data-view="design"]').click();p.locator('[data-view="structure"]').click()
 child=next(box for box in state(p)['boxes'] if box['id']==b['id']);p.mouse.click(*point(p,child['x']+child['width']/2,child['y']+child['height']/2));assert selected(p)['id']==b['id']
 task=send_live(p,'Beschrifte die ausgewählte Box mit Weiter.');assert task['status']=='applied',task;assert selected(p)['label']=='Weiter';assert task['reply']['actions']
 p.locator('[data-view="design"]').click();assert 'Weiter' in p.locator('.box.primary .box-content').inner_text();p.screenshot(path=str(OUT/'live-ai.png'));(OUT/'live-ai.json').write_text(json.dumps(task,ensure_ascii=False,indent=2))

def live_ai_proposals(p):
 focus(p);p.keyboard.press('b');task=send_live(p,'Zeige mir zwei unterschiedliche Gestaltungsvorschläge für diese Box als Button. Einer blau, einer orange. Noch nicht anwenden.');assert task['reply']['proposals'],task;assert not task['reply']['actions'],task
 proposal=task['reply']['proposals'][0];card=p.locator(f'.task-card [data-proposal-id="{proposal["id"]}"]');card.locator('[data-action="retain"]').click();assert len(state(p)['myspace'])==1
 # Applying a retained proposal is immediate and uses current validated selection.
 retained=p.locator(f'#retained [data-proposal-id="{proposal["id"]}"]');retained.locator('[data-action="apply"]').click();assert selected(p)['color']==proposal['changes'].get('color',selected(p)['color']);p.locator('[data-view="design"]').click();p.screenshot(path=str(OUT/'live-proposals-myspace.png'));(OUT/'live-proposals.json').write_text(json.dumps(task,ensure_ascii=False,indent=2))


def fixture_connection(p):
 p.route('**/api/status',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({'ok':True,'busy':False,'model':'explicit-negative-fixture','version':'0.1.0'})))
 p.reload()

def negative_reply_fixtures(p):
 # No model call: injected responses are rejection fixtures only.
 fixture_connection(p)
 focus(p);p.keyboard.press('b');before=state(p)['boxes'];packet={}
 def submit(route):
  packet.update(route.request.post_data_json);route.fulfill(status=202,content_type='application/json',body=json.dumps({'task_id':packet['task_id'],'status':'waiting'}))
 def poll(route):
  reply={'version':1,'task_id':packet['task_id'],'revision':packet['revision'],'box_ids':packet['box_ids'],'summary':'Explicit invalid fixture','actions':[{'type':'patch','box_id':packet['box_ids'][0],'changes':{'id':'forbidden'}}],'proposals':[]}
  route.fulfill(status=200,content_type='application/json',body=json.dumps({'task_id':packet['task_id'],'status':'ready','reply':reply}))
 p.route('**/api/tasks',submit);p.route('**/api/tasks/*',poll);p.locator('#order').fill('Ungültige Rückgabe prüfen');p.locator('#send').click();p.wait_for_function('() => window.blockDesigner.getState().tasks[0]?.status==="failed"');assert state(p)['boxes']==before


def stale_duplicate_disconnect_fixtures(p):
 # A stale response must be deferred, and a valid response applied once only.
 fixture_connection(p)
 focus(p);p.keyboard.press('b');packet={};mode={'name':'stale'};replies=[]
 def submit(route):
  packet.clear();packet.update(route.request.post_data_json);route.fulfill(status=202,content_type='application/json',body=json.dumps({'task_id':packet['task_id'],'status':'waiting'}))
 def poll(route):
  if mode['name']=='disconnect':route.abort('connectionreset');return
  reply={'version':1,'task_id':packet['task_id'],'revision':packet['revision'],'box_ids':packet['box_ids'],'summary':'Explicit safety fixture','actions':[{'type':'patch','box_id':packet['box_ids'][0],'changes':{'label':'Fixture permitted label'}}],'proposals':[]}
  if mode['name']=='stale':
   # Mutation through the actual UI occurs after submission, before response.
   focus(p);p.keyboard.press('b')
  data={'task_id':packet['task_id'],'status':'ready','reply':reply};replies.append(data);route.fulfill(status=200,content_type='application/json',body=json.dumps(data))
 p.route('**/api/tasks',submit);p.route('**/api/tasks/*',poll);p.locator('#order').fill('Veraltungsfall');p.locator('#send').click();p.wait_for_function('() => window.blockDesigner.getState().tasks[0]?.status==="stale"');assert state(p)['boxes'][0]['label']=='';assert p.locator('[data-status="stale"]').is_visible()
 mode['name']='disconnect';p.locator('#order').fill('Verbindungsabbruch');p.locator('#send').click();p.wait_for_function('() => window.blockDesigner.getState().tasks.at(-1)?.status==="disconnected"');before=state(p)['boxes'];assert p.locator('[data-action="reconnect"]').is_visible()
 mode['name']='duplicate';p.locator('[data-action="reconnect"]').click();p.wait_for_function('() => window.blockDesigner.getState().tasks.at(-1)?.status==="applied"');revision=state(p)['revision'];assert selected(p)['label']=='Fixture permitted label'
 # Browser bridge instance handles the repeated response via the same public module contract.
 p.evaluate('''async payload=>{const {createWhiteboardBridge}=await import('/src/bridge/whiteboard.js');const {createStore}=await import('/src/core/store.js');const s=window.blockDesigner.getState();const store=createStore(s);const bridge=createWhiteboardBridge(store);bridge.accept(payload);window.duplicateCheck={revision:store.getState().revision,boxes:store.getState().boxes};}''',replies[-1]);assert p.evaluate('window.duplicateCheck.revision')==revision;assert p.evaluate('window.duplicateCheck.boxes')==state(p)['boxes']

CASES=[('BD-02-BROWSER',create_layers),('BD-03-AXES',movement_axes),('BD-03-BOUNDS',scale_bounds),('BD-04-GRID-MONITOR-ZOOM',grid_monitor_zoom),('BD-05-TRANSFER-CHILDREN',transfer_group),('BD-06-ATTR-FOCUS-VIEWS',attribute_focus_views),('BD-08-DE-EN-DESKTOP',desktop_language_longtext),('BD-07-LIVE-CHANGE',live_ai_change),('BD-07-LIVE-PROPOSALS',live_ai_proposals),('BD-07-INVALID-FIXTURE',negative_reply_fixtures),('BD-07-STALE-DUPLICATE-DISCONNECT-FIXTURE',stale_duplicate_disconnect_fixtures)]

def main():
 OUT.mkdir(parents=True,exist_ok=True);chosen=set(sys.argv[1:]);failed=0
 with sync_playwright() as play:
  browser=play.chromium.launch(channel='chrome');version=browser.version
  for identity,fn in CASES:
   if chosen and identity not in chosen:continue
   page=browser.new_page(viewport={'width':1440,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));start=time.time()
   try:
    page.goto(URL);fn(page);assert not errors,errors
    row={'id':identity,'status':'bestanden','seconds':round(time.time()-start,2)}
   except Exception as e:
    failed+=1;row={'id':identity,'status':'fehlgeschlagen','error':traceback.format_exc(),'seconds':round(time.time()-start,2)};page.screenshot(path=str(OUT/(identity+'-failure.png')))
   page.close();RESULTS.append(row);
   with (OUT/'browser-history.jsonl').open('a') as history:history.write(json.dumps({**row,'time':time.time()},ensure_ascii=False)+'\n')
   print(json.dumps(row,ensure_ascii=False),flush=True)
   (OUT/'browser-results.json').write_text(json.dumps({'browser':'Google Chrome '+version,'url':URL,'results':RESULTS},ensure_ascii=False,indent=2))
  browser.close()
 return 1 if failed else 0
if __name__=='__main__':raise SystemExit(main())
