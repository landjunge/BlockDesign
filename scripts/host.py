"""Existing ThreadDesk module facade. No foreign database/file writes."""
import json
import os
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('BD_THREADDESK_SOURCE', str(Path.home()/'threaddesk-worktrees/ordinal-lock/src'))).expanduser()
sys.path.insert(0, str(SOURCE))
from threaddesk.services.modules import ModuleManifest, ModuleRegistry, ModuleRuntime
from threaddesk.services.actors import ActorRegistry
from threaddesk.storage.json_store import JsonStore
from threaddesk.api.service import ThreadService
from threaddesk.core.errors import NotFound
from threaddesk.services.hausmeister import Hausmeister

class Host:
    def __init__(self, root=None, binding=None):
        self.store = JsonStore(Path(root or os.environ.get('BD_WHITEBOARD_ROOT', str(Path.home()/'.threaddesk'))))
        self.registry = ModuleRegistry(self.store)
        self.runtime = ModuleRuntime(self.store, self.registry)
        self.manifest = ModuleManifest.from_dict(json.loads((PROJECT/'module.json').read_text()))
        try: installed=self.registry.get(self.manifest.id)
        except NotFound:raise RuntimeError('Modulanschluss fehlt: ./start.command --setup ausführen.') from None
        if installed.manifest.to_dict()!=self.manifest.to_dict():
            # Registry preserves disabled state and enforces new approvals.
            self.registry.update(self.manifest)
        self.binding = binding or PROJECT/'.runtime/binding.json'
        if not self.binding.exists():
            raise RuntimeError('Hostanschluss fehlt: ./start.command --setup ausführen.')
        data = json.loads(self.binding.read_text())
        self.thread_id = data['thread_id']
        self.store.get_thread(self.thread_id)
    def context(self, fn, action='whiteboard:append'):
        result = self.runtime.run(self.manifest.id, action, fn)
        if not result.ok:
            raise RuntimeError(result.error)
        return result.value
    def entries(self):
        return self.context(lambda c: c.read_whiteboard(self.thread_id))
    def append(self, kind, text, task_id, step_id=None, actor_type='codex', run_id=None, metadata=None, key=None):
        fields = dict(actor='BlockDesigner' if actor_type=='human' else 'Codex' if actor_type=='codex' else 'lokale KI',
                      actor_type=actor_type, entry_type=kind, content=text, task_id=task_id,
                      run_id=run_id, metadata={**(metadata or {}), 'step_id':step_id}, external_key=key)
        if actor_type=='local-assistant':
            fields['actor_id']=Hausmeister(self.store).ensure_actor()['id']
        return self.context(lambda c: c.append_whiteboard(self.thread_id, **fields))['entry']


def setup():
    store = JsonStore(Path(os.environ.get('BD_WHITEBOARD_ROOT', str(Path.home()/'.threaddesk'))))
    registry = ModuleRegistry(store)
    manifest = ModuleManifest.from_dict(json.loads((PROJECT/'module.json').read_text()))
    try: installed = registry.get(manifest.id)
    except NotFound:
        installed = registry.install(manifest)
        registry.set_enabled(manifest.id, True)
    if installed.manifest.to_dict()!=manifest.to_dict():
        registry.update(manifest)
    if not registry.get(manifest.id).enabled:
        raise RuntimeError('Modul ist deaktiviert / module disabled; bestehende Modulfreigabe explizit ändern, Setup reaktiviert sie nicht.')
    binding = PROJECT/'.runtime/binding.json'
    binding.parent.mkdir(exist_ok=True)
    if not binding.exists():
        service = ThreadService(store=store)
        previous = store.get_current_id()
        thread = next((t for t in service.list() if t.title in ['BlockDesigner','Block Designer']), None)
        if thread is None:
            thread = service.create('BlockDesigner','Modulares Browser-Prototyp-Modul; Konzept in Zukunftsvisionen/Ideen/Block Designer.')
            store.set_current_id(previous)
        binding.write_text(json.dumps({'thread_id':thread.id,'root':str(store.root),'source':str(SOURCE)},indent=2)+'\n')
    print('HOST_BOUND', binding.read_text().strip())

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('command',choices=['setup','ping','entries'])
    p.add_argument('--task',default='bd-build-20261014');p.add_argument('--step');p.add_argument('--kind',default='progress');p.add_argument('--text',default='');p.add_argument('--actor',default='codex');p.add_argument('--evidence')
    a=p.parse_args()
    if a.command=='setup':setup()
    elif a.command=='entries': print(json.dumps(Host().entries(),ensure_ascii=False))
    else:
        h=Host(); entry=h.append(a.kind,a.text,a.task,a.step,actor_type=a.actor,run_id=os.environ.get('CODEX_THREAD_ID'),metadata={'evidence':a.evidence} if a.evidence else {})
        assert any(e['id']==entry['id'] for e in h.entries())
        print('DELIVERY_VERIFIED',entry['id'],entry['task_id'],entry['metadata'].get('step_id'))
