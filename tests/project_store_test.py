"""Durability/recovery checks in an isolated temporary data directory."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from project_store import ProjectStore, ContractError
from uuid import uuid4

def body():
 return {'format':1,'state':{'version':1,'revision':0,'document':{'width':1000,'height':640},'boxes':[],'selection':[],'activeLayer':1,'grid':{'spacing':20,'magnet':2,'enabled':True},'nextNumber':1,'creationCounts':[0,0,0],'tasks':[],'myspace':[],'ui':{'zoom':.75,'language':'de','view':'structure'}},'history':{'undo':[],'redo':[]}}
class Storage(unittest.TestCase):
 def setUp(self):self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.store=ProjectStore(Path(self.tmp.name));self.id=str(uuid4())
 def test_dedup_restart_and_no_history_deletion(self):
  first=self.store.save(self.id,body(),{'kind':'preRequest','instruction':'Test'},None);count=len(list(self.store.cas.root.iterdir()));second=self.store.save(self.id,body(),{'kind':'resultSnapshot'},first['head']);self.assertEqual(len(list(self.store.cas.root.iterdir())),count)
  reopened=ProjectStore(self.store.root);self.assertEqual(reopened.read(self.id)['head'],second['head']);self.assertEqual(len(reopened.history(self.id)['items']),2)
 def test_partial_write_and_damaged_commit_recover_last_readable(self):
  first=self.store.save(self.id,body(),{},None);second=self.store.save(self.id,body(),{},first['head']);folder=self.store.folder(self.id)/'commits';last=sorted(folder.glob('*.json'))[-1];last.write_text('{interrupted');(folder/'.partial.tmp').write_text('{');loaded=ProjectStore(self.store.root).read(self.id);self.assertEqual(loaded['head'],first['head']);self.assertEqual(loaded['warning'],'storageCorrupt');self.assertTrue(last.exists())
 def test_damaged_new_content_cannot_replace_readable_project(self):
  first=self.store.save(self.id,body(),{},None);changed=body();changed['state']['revision']=1;second=self.store.save(self.id,changed,{},first['head']);commit=json.loads(sorted((self.store.folder(self.id)/'commits').glob('*.json'))[-1].read_text())['commit'];(self.store.cas.root/commit['chunks']['document']).write_bytes(b'damaged');loaded=self.store.read(self.id);self.assertEqual(loaded['head'],first['head']);self.assertEqual(loaded['warning'],'storageCorrupt')
 def test_conflicting_tab_and_invalid_future_format_rejected(self):
  first=self.store.save(self.id,body(),{},None);self.assertRaisesRegex(ContractError,'storageConflict',self.store.save,self.id,body(),{},None);future=body();future['format']=99;self.assertRaisesRegex(ContractError,'storageFormat',self.store.save,self.id,future,{},first['head'])
 def test_failed_atomic_publication_keeps_last_commit(self):
  first=self.store.save(self.id,body(),{},None)
  with patch('project_store.atomic',side_effect=OSError('disk full')):self.assertRaises(OSError,self.store.save,self.id,body(),{},first['head'])
  self.assertEqual(self.store.read(self.id)['head'],first['head']);self.assertEqual(len(self.store.history(self.id)['items']),1)
if __name__=='__main__':unittest.main(verbosity=2)
