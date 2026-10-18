"""Automatic own-manifest upgrades preserve the existing host's access gates."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from host import Host, ModuleRegistry, ModuleManifest, JsonStore, ThreadService, PROJECT
class HostContract(unittest.TestCase):
 def setup_host(self,enabled):
  temp=TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name);store=JsonStore(root);registry=ModuleRegistry(store)
  old=json.loads((PROJECT/'module.json').read_text());old['version']='0.1.0';old['write_actions']=['whiteboard:append'];registry.install(ModuleManifest.from_dict(old));registry.set_enabled(old['id'],enabled)
  thread=ThreadService(store=store).create('Synthetic contract check');binding=root/'binding.json';binding.write_text(json.dumps({'thread_id':thread.id}));return Host(root=root,binding=binding)
 def test_own_upgrade_uses_existing_context_and_keeps_data(self):
  host=self.setup_host(True);host.context(lambda c:c.write_own_record('projects:write','test-record',{'format':1}),'projects:write');self.assertEqual(host.context(lambda c:c.read_own_data(),'projects:write')['records']['test-record'],{'format':1});self.assertTrue(host.registry.get(host.manifest.id).enabled)
 def test_disabled_module_is_not_silently_enabled(self):
  host=self.setup_host(False);self.assertFalse(host.registry.get(host.manifest.id).enabled)
  with self.assertRaises(RuntimeError):host.context(lambda c:c.read_own_data(),'projects:write')
if __name__=='__main__':unittest.main(verbosity=2)
