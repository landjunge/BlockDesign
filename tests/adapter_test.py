"""Trust-boundary tests with explicit synthetic JSON, no simulated AI success."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from ai_adapter import ContractError, validate_request, validate_reply, validate_snapshot

BOX={'id':'synthetic-box-1','number':1,'orientation':'hsl(137.508 80% 76%)','layer':1,'type':'Box','x':475,'y':295,'width':50,'height':50,'radius':0,'color':'#ffffff','paletteIndex':4,'brightness':0,'borderColor':'#808080','borderWidth':1,'font':{'family':'system-ui','size':14,'color':'#000000'},'label':'','parentId':None}
SNAPSHOT={'version':1,'revision':4,'document':{'width':1000,'height':640},'boxes':[BOX],'selection':[BOX['id']],'activeLayer':1,'grid':{'spacing':20,'magnet':2,'enabled':True},'coordinates':{'origin':[0,0],'x':'right','y':'down','unit':'px','pixel_scale':1},'zoom':.75,'language':'de'}
PACKET={'task_id':'synthetic-task','instruction':'Beschrifte die Box','box_ids':[BOX['id']],'revision':4,'snapshot':SNAPSHOT}
def raw(changes=None):return {'summary':'Synthetic validator fixture','actions':[{'type':'patch','box_id':BOX['id'],'changes':changes or {'label':'Weiter'}}],'proposals':[]}
class AdapterSafety(unittest.TestCase):
 def setUp(self):self.packet=copy.deepcopy(PACKET)
 def reject(self,data):
  with self.assertRaises((ContractError,ValueError,TypeError)):validate_reply(data,self.packet)
 def test_real_request_contract(self):
  self.assertEqual(validate_request(self.packet),self.packet)
  self.assertEqual(validate_reply(raw(),self.packet)['revision'],4)
 def test_unknown_or_locked_targets(self):
  data=raw();data['actions'][0]['box_id']='foreign-box';self.reject(data)
  self.packet['snapshot']['activeLayer']=2
  with self.assertRaises(ContractError):validate_request(self.packet)
 def test_identity_code_css_and_nonfinite_rejected(self):
  for changes in [{'id':'forbidden'},{'number':9},{'orientation':'#ff0000'},{'layer':3},{'parentId':None},{'onclick':'execute code'},{'color':'url(https://x.invalid)'},{'x':float('nan')},{'width':True}]:self.reject(raw(changes))
 def test_dimensions_font_and_grid_limits(self):
  for changes in [{'width':3},{'height':-1},{'x':999},{'y':639},{'radius':-1},{'brightness':101},{'borderWidth':21},{'font':{'family':'url(evil)','size':14,'color':'#000000'}}]:self.reject(raw(changes))
  for spacing,magnet in [(0,0),(10,8),(-5,1),(float('inf'),2)]:self.reject({'summary':'fixture','actions':[{'type':'grid','spacing':spacing,'magnet':magnet}],'proposals':[]})
 def test_parent_cycle_and_moving_children_bounds(self):
  module=copy.deepcopy(BOX);module.update(id='module-1',number=2,type='Modul',x=470,y=290,width=60,height=60)
  self.packet['snapshot']['boxes'].append(module);self.packet['snapshot']['boxes'][0]['parentId']=module['id'];self.packet['box_ids']=['module-1'];self.packet['snapshot']['selection']=['module-1']
  data=raw({'x':950});data['actions'][0]['box_id']='module-1';self.reject(data)
  module['parentId']=module['id']
  with self.assertRaises(ContractError):validate_snapshot(self.packet['snapshot'])
 def test_proposals_have_no_positions_or_executable_values(self):
  data={'summary':'fixture','actions':[],'proposals':[{'title':'Blue','description':'fixture','changes':{'color':'#42a5f5','radius':8}}]}
  reply=validate_reply(data,self.packet);self.assertEqual(reply['proposals'][0]['source_task'],self.packet['task_id'])
  data['proposals'][0]['changes']['x']=10;self.reject(data)
 def test_packet_revision_targets_coordinate_contract_and_context_bound(self):
  for change in ['revision','box_ids','coordinates','context']:
   packet=copy.deepcopy(self.packet)
   if change=='revision':packet['revision']=3
   elif change=='box_ids':packet['box_ids']=[]
   elif change=='coordinates':packet['snapshot']['coordinates']['x']='left'
   else:packet['snapshot']['boxes'][0]['label']='large'*4000
   with self.assertRaises(ContractError):validate_request(packet)
 def test_reply_extra_fields_wrong_structure_and_large_values(self):
  data=raw();data['code']='arbitrary';self.reject(data)
  self.reject('not JSON');self.reject(raw({'label':'x'*4001}))
if __name__=='__main__':unittest.main(verbosity=2)
