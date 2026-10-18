"""Report a checked implementation step through the existing module facade."""
import argparse
import json
import os
from host import Host, PROJECT
p=argparse.ArgumentParser();p.add_argument('kind',choices=['claimed','progress','result','problem']);p.add_argument('step');p.add_argument('text');p.add_argument('--evidence');a=p.parse_args()
task='bd-'+a.step.split('-')[1].split('.')[0];session=os.environ.get('CODEX_THREAD_ID','01a13ae2-819a-7442-8789-a7e7c4f1cc94')
h=Host();entry=h.append(a.kind,a.text,task,a.step,run_id=session,metadata={'evidence':a.evidence} if a.evidence else {})
assert any(e['id']==entry['id'] for e in h.entries())
h.append('progress',a.step+': '+a.text,'bd-build-20261014',a.step,run_id=session)
if a.kind=='claimed':(PROJECT/'.runtime/current-step.json').write_text(json.dumps({'task':task,'step':a.step,'session':session,'next':a.text}))
print('DELIVERY_VERIFIED',a.step,a.kind,entry['id'])
