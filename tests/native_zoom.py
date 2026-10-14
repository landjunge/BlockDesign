"""Actual Chrome page zoom through its native settings, fresh temporary profile."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
URL=os.environ.get('BD_TEST_URL','http://127.0.0.1:5191');OUT=ROOT/'.runtime/acceptance-v02';OUT.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as p:
 context=p.chromium.launch_persistent_context('',channel='chrome',headless=False,no_viewport=True)
 settings=context.new_page();settings.goto('chrome://settings/appearance')
 settings.locator('select#zoomLevel').select_option('1')
 baseline=context.new_page();baseline.goto(URL);base_ratio=baseline.evaluate('devicePixelRatio');baseline.close()
 for zoom in [1.25,1.5,2.0]:
  settings.locator('select#zoomLevel').select_option(str(zoom).removesuffix('.0'))
  page=context.new_page();page.goto(URL);page.wait_for_function('()=>!!window.blockDesigner');old=page.evaluate('localStorage.getItem("blockdesigner.project.v1")');page.locator('#projects-panel button').click();page.wait_for_function('(old)=>localStorage.getItem("blockdesigner.project.v1")!==old',arg=old);page.locator('#canvas-scroll').focus();page.keyboard.press('b')
  observed=page.evaluate('({ratio:devicePixelRatio,width:innerWidth,height:innerHeight})')
  assert abs(observed['ratio']/base_ratio-zoom)<.01,observed
  handle=page.locator('#monitor-handle').bounding_box();panel=page.locator('#monitor').bounding_box();page.mouse.move(handle['x']+20,handle['y']+18);page.mouse.down();page.mouse.move(handle['x']+20-panel['x'],handle['y']+18-panel['y'],steps=4);page.mouse.up()
  before=page.evaluate('window.blockDesigner.getState()');page.locator('.box').scroll_into_view_if_needed();r=page.locator('#canvas').bounding_box();x=r['x']+500*.75;y=r['y']+320*.75
  page.mouse.move(x,y);page.keyboard.press('Space');page.mouse.move(x+15,y+15);page.keyboard.press('Space');after=page.evaluate('window.blockDesigner.getState()')
  box=after['boxes'][0];assert abs(box['x']-495)<1e-7 and abs(box['y']-315)<1e-7,box
  assert after['document']==before['document'];assert(box['width'],box['height'])==(50,50)
  for selector in ['#help','#send','#zoom']:
   page.locator(selector).scroll_into_view_if_needed();assert page.locator(selector).is_visible()
  results.append({'zoom':zoom,'observed':observed,'status':'bestanden','position':[box['x'],box['y']]})
  page.close()
 context.close()
(OUT/'native-zoom.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False))
