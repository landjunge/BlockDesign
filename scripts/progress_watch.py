"""Bounded factual operating pings, not an agent or an execution dispatcher."""
import json
import time
from urllib.request import urlopen
from host import Host, PROJECT

if __name__=='__main__':
    host=Host();end=time.monotonic()+14400
    while time.monotonic()<end:
        time.sleep(40)
        path=PROJECT/'.runtime/current-step.json'
        if not path.exists(): continue
        current=json.loads(path.read_text())
        if current.get('finished'): break
        files=sorted((p for area in ['src','scripts','tests'] for p in (PROJECT/area).rglob('*') if p.is_file() and '__pycache__' not in str(p)),key=lambda p:p.stat().st_mtime,reverse=True)[:3]
        try:
            with urlopen('http://127.0.0.1:5190/api/status',timeout=2) as r: online=r.status==200
        except Exception: online=False
        text='Betriebscheck: Browserhost '+('erreichbar' if online else 'nicht erreichbar')+'. Aktiver Schritt '+current['step']+'. Zuletzt bearbeitet: '+', '.join(str(p.relative_to(PROJECT)) for p in files)+'. Abschluss noch nicht bestätigt; nächste Handlung: '+current['next']
        host.append('progress',text,'bd-build-20261014',current['step'],run_id=current['session'],metadata={'operating_check':True,'server_reachable':online})
        host.append('progress',text,current['task'],current['step'],run_id=current['session'],metadata={'operating_check':True})
