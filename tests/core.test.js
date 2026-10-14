import test from 'node:test';
import assert from 'node:assert/strict';
import { createStore } from '../src/core/store.js';
import { initialState, validateState, clone } from '../src/core/model.js';
import { nearest, center } from '../src/core/geometry.js';
const state = s => s.getState();
const box = s => state(s).boxes.find(b => b.id === state(s).selection[0]);
const run = (s, a) => { const r = s.dispatch(a); assert.equal(r.ok, true, JSON.stringify(r)); return state(s); };
function two() { const s=createStore();run(s,{type:'create'});run(s,{type:'create'});return s; }

test('creation, layer locks, offsets, identity and exhausted creation space',()=>{
 const s=two();assert.deepEqual(state(s).boxes.map(b=>[b.x,b.y,b.width,b.height]),[[475,295,50,50],[480,300,50,50]]);
 assert.equal(new Set(state(s).boxes.map(b=>b.id)).size,2);
 const id=box(s).id, original=box(s);run(s,{type:'patch',id,changes:{type:'Button'}});assert.equal(box(s).orientation,original.orientation);
 run(s,{type:'layer',layer:2});assert.equal(s.dispatch({type:'patch',id,changes:{label:'bad'}}).error,'layerLocked');run(s,{type:'create'});assert.equal(box(s).number,3);assert.equal(box(s).x,475);
 const init=initialState();init.creationCounts[0]=60;const full=createStore(init);assert.equal(full.dispatch({type:'create'}).error,'creationFull');assert.equal(state(full).boxes.length,0);
});
test('nearest centre ignores overlap area, locked layers and ties use number',()=>{
 const s=two(), [a,b]=state(s).boxes;
 assert.equal(nearest(state(s),center(a)).id,a.id);
 assert.equal(nearest(state(s),{x:502.5,y:322.5}).id,a.id);
 run(s,{type:'layer',layer:3});assert.equal(nearest(state(s),{x:500,y:320}),null);
});
test('movement snaps edges and hard boundaries; D/F lock orthogonal axis and anchor',()=>{
 const s=two(),id=box(s).id;run(s,{type:'move',id,dx:19,dy:19});assert.equal(box(s).x,500);assert.equal(box(s).y,320);
 const before=box(s);run(s,{type:'resize',id,axis:'height',delta:11});assert.equal(box(s).x,before.x);assert.equal(box(s).y,before.y);assert.equal(box(s).width,before.width);assert.equal(box(s).height,60);
 run(s,{type:'resize',id,axis:'width',delta:-9999});assert.equal(box(s).width,4);assert.equal(box(s).height,60);
 run(s,{type:'move',id,dx:9999,dy:9999});assert.equal(box(s).x,996);assert.equal(box(s).y,580);
});
test('proportional scale respects minimum and both hard limits without ratio drift',()=>{
 const s=two(),id=box(s).id;run(s,{type:'patch',id,changes:{width:100,height:40}});run(s,{type:'scale',id,factor:1.1});assert.equal(box(s).width,110.00000000000001);
 run(s,{type:'scale',id,factor:1/1.1});assert.ok(Math.abs(box(s).width-100)<1e-10);
 for(let i=0;i<50;i++)run(s,{type:'scale',id,factor:1.1});assert.ok(Math.abs(box(s).width/box(s).height-2.5)<1e-10);assert.equal(box(s).x+box(s).width,1000);
 for(let i=0;i<80;i++)run(s,{type:'scale',id,factor:1/1.1});assert.ok(Math.abs(box(s).height-4)<1e-10);assert.ok(Math.abs(box(s).width-10)<1e-10);
});
test('ordered shift selection transfers text and suitable style but preserves identity and position',()=>{
 const s=two(),[a,b]=state(s).boxes;run(s,{type:'patch',id:a.id,changes:{type:'Button',label:'Weiter',radius:8,color:'#42a5f5',font:{family:'system-ui',size:16,color:'#ffffff'}}});
 run(s,{type:'select',id:a.id});run(s,{type:'select',id:b.id,extend:true});run(s,{type:'transfer'});
 const target=state(s).boxes[1];assert.equal(target.label,'Weiter');assert.equal(target.radius,8);for(const k of ['id','number','orientation','x','y','layer','parentId'])assert.equal(target[k],b[k]);
 run(s,{type:'select',id:a.id,extend:true});assert.equal(state(s).selection[0],b.id);
});
test('nested modules move as a family, prevent cycles and keep children unscaled',()=>{
 const s=two(),[a,b]=state(s).boxes;run(s,{type:'select',id:a.id});run(s,{type:'select',id:b.id,extend:true});run(s,{type:'group'});const m=box(s);
 run(s,{type:'move',id:m.id,dx:9999,dy:9999});const moved=state(s);assert.ok(moved.boxes.every(b=>b.x+b.width<=1000&&b.y+b.height<=640));assert.equal(moved.boxes[1].x-moved.boxes[0].x,5);
 const children=clone(moved.boxes.slice(0,2));run(s,{type:'scale',id:m.id,factor:1/1.1});assert.deepEqual(state(s).boxes.slice(0,2),children);
 assert.equal(s.dispatch({type:'patch',id:m.id,changes:{type:'Button'}}).error,'parentHasChildren');assert.equal(s.dispatch({type:'parent',id:m.id,parentId:m.id}).error,'invalidParent');
});
test('atomic rejection cannot mutate a partial T batch or accept unknown attributes',()=>{
 const s=two(),[a,b]=state(s).boxes;run(s,{type:'patch',id:a.id,changes:{width:525}});run(s,{type:'select',id:a.id});run(s,{type:'select',id:b.id,extend:true});const prev=clone(state(s).boxes);
 assert.equal(s.dispatch({type:'transfer'}).ok,false);assert.deepEqual(state(s).boxes,prev);assert.equal(s.dispatch({type:'patch',id:a.id,changes:{id:'evil'}}).error,'invalidAttributes');
});
test('grid validates values, refinement and view/zoom leave document coordinates intact',()=>{
 const s=two(),before=clone(state(s).boxes);run(s,{type:'grid',spacing:10,magnet:1});assert.equal(state(s).grid.magnet,1);
 assert.equal(s.dispatch({type:'grid',spacing:0,magnet:0}).error,'invalidGrid');assert.equal(s.dispatch({type:'grid',spacing:10,magnet:8}).error,'invalidGrid');
 run(s,{type:'view',view:'design'});run(s,{type:'zoom',zoom:2});assert.deepEqual(state(s).boxes,before);
});
test('preview is transient; cancel restores original and commit increments revision once',()=>{
 const s=two(),before=box(s),revision=state(s).revision;run(s,{type:'previewStart'});run(s,{type:'previewColor',index:15});run(s,{type:'previewBrightness',delta:10});assert.deepEqual(box(s),before);assert.equal(state(s).revision,revision);run(s,{type:'previewCancel'});assert.deepEqual(box(s),before);
 run(s,{type:'previewStart'});run(s,{type:'previewColor',index:6});run(s,{type:'previewCommit'});assert.equal(box(s).color,'#ff0000');assert.equal(state(s).revision,revision+1);
});
test('AI batches bind task, target, revision; invalid duplicate stale returns never change boxes',()=>{
 const s=two(),id=box(s).id;run(s,{type:'taskAdd',task:{task_id:'task-1',revision:state(s).revision,box_ids:[id]}});
 const revision=state(s).revision;run(s,{type:'aiApply',task_id:'task-1',actions:[{type:'patch',box_id:id,changes:{label:'KI'}}]});assert.equal(box(s).label,'KI');assert.equal(state(s).revision,revision+1);
 assert.equal(s.dispatch({type:'aiApply',task_id:'task-1',actions:[]}).error,'duplicateReply');run(s,{type:'taskAdd',task:{task_id:'task-2',revision:state(s).revision,box_ids:[id]}});run(s,{type:'create'});
 assert.equal(s.dispatch({type:'aiApply',task_id:'task-2',actions:[]}).error,'staleReply');
 run(s,{type:'taskAdd',task:{task_id:'task-3',revision:state(s).revision,box_ids:[id]}});const before=clone(state(s).boxes);
 assert.equal(s.dispatch({type:'aiApply',task_id:'task-3',actions:[{type:'patch',box_id:id,changes:{label:'partial'}},{type:'patch',box_id:id,changes:{width:-10}}]}).ok,false);assert.deepEqual(state(s).boxes,before);
});

test('grab a non-primary selected box: monitor follows it and retains exact values after drop',()=>{
 const s=two(),[a,b]=state(s).boxes;run(s,{type:'select',id:a.id});run(s,{type:'select',id:b.id,extend:true});run(s,{type:'grab',id:b.id});assert.deepEqual(state(s).selection,[a.id,b.id]);run(s,{type:'move',id:b.id,dx:100,dy:100});assert.equal(state(s).ui.monitor.last.id,b.id);assert.equal(state(s).ui.monitor.last.x,580);run(s,{type:'drop'});assert.equal(state(s).ui.monitor.last.id,b.id);run(s,{type:'select',id:null});assert.equal(state(s).ui.monitor.last.id,b.id);
});

test('module background passes to children while geometry, label and identity stay; untouched A makes no edit',()=>{
 const s=two(),[a,b]=state(s).boxes;run(s,{type:'select',id:a.id});run(s,{type:'select',id:b.id,extend:true});run(s,{type:'group'});const m=box(s);const before=clone(state(s).boxes.slice(0,2));const rev=state(s).revision;
 run(s,{type:'previewStart'});run(s,{type:'previewCommit'});assert.equal(state(s).revision,rev);assert.deepEqual(state(s).boxes.slice(0,2),before);
 run(s,{type:'patch',id:m.id,changes:{color:'#42a5f5',brightness:8}});for(let i=0;i<2;i++){const child=state(s).boxes[i];assert.equal(child.color,'#42a5f5');assert.equal(child.brightness,8);for(const k of ['id','number','orientation','x','y','width','height','label'])assert.equal(child[k],before[i][k]);}
});

test('partial font edits validate known fields and preserve all unrequested font attributes',()=>{
 const s=two(),id=box(s).id;run(s,{type:'patch',id,changes:{font:{color:'#ffffff'}}});assert.deepEqual(box(s).font,{family:'system-ui',size:14,color:'#ffffff'});assert.equal(s.dispatch({type:'patch',id,changes:{font:{weight:'bold'}}}).error,'invalidValues');
});

test('selection families share one snapped/clamped displacement and parent child move once',()=>{
 const s=two(),[a,b]=state(s).boxes;run(s,{type:'patch',id:b.id,changes:{x:700,y:500}});run(s,{type:'select',id:a.id});run(s,{type:'select',id:b.id,extend:true});
 const before=state(s).boxes;run(s,{type:'moveSelection',dx:1000,dy:1000});const after=state(s).boxes;
 assert.equal(after[0].x-before[0].x,after[1].x-before[1].x);assert.equal(after[0].y-before[0].y,after[1].y-before[1].y);assert.equal(after[1].x,950);assert.equal(after[1].y,590);
 run(s,{type:'group'});const parent=box(s);run(s,{type:'select',id:parent.id});run(s,{type:'select',id:a.id,extend:true});const family=state(s).boxes;run(s,{type:'moveSelection',dx:-100,dy:-100});assert.ok(state(s).boxes.every((b,i)=>b.x===family[i].x-100&&b.y===family[i].y-100));
});
test('undo redo gestures and AI batches are single steps with monotonically increasing revisions',()=>{
 const s=two(),id=box(s).id;s.begin('move');run(s,{type:'grab',id});run(s,{type:'moveSelection',dx:30,dy:30});run(s,{type:'moveSelection',dx:10,dy:10});run(s,{type:'drop'});s.end();const moved=box(s),rev=state(s).revision;run(s,{type:'undo'});assert.equal(box(s).x,480);assert.equal(state(s).revision,rev+1);run(s,{type:'redo'});assert.equal(box(s).x,moved.x);
 const task={task_id:'undo-ai',box_ids:[id],revision:state(s).revision,activeLayer:1,applied:false};run(s,{type:'taskAdd',task});run(s,{type:'aiApply',task_id:task.task_id,actions:[{type:'patch',box_id:id,changes:{label:'AI'}},{type:'patch',box_id:id,changes:{width:70}}]});run(s,{type:'undo'});assert.equal(box(s).label,'');assert.equal(box(s).width,50);assert.equal(state(s).tasks.at(-1).applied,true);run(s,{type:'redo'});assert.equal(box(s).label,'AI');assert.equal(box(s).width,70);
});

test('prospective durable commit shares the same undo calculation and retains transient UI',()=>{
 const s=two(),id=box(s).id,before=state(s);const action={type:'patch',id,changes:{label:'Durable'}};const prepared=s.prepare(action);assert.equal(state(s).boxes[1].label,'');assert.equal(prepared.history.undo.length,s.history().undo+1);
 run(s,{type:'monitor',x:40,y:60});s.commitCandidate(prepared.state,action);assert.equal(box(s).label,'Durable');assert.equal(state(s).ui.monitor.x,40);assert.deepEqual(s.exportHistory(),prepared.history);
 const noChange=s.prepare({type:'patch',id,changes:{label:'Durable'}});assert.equal(noChange.history.undo.length,s.history().undo);
});

test('changing layer during a gesture closes it before subsequent creations',()=>{
 const s=createStore();run(s,{type:'create'});const original=box(s);s.begin('move');run(s,{type:'grab',id:original.id});run(s,{type:'moveSelection',dx:40,dy:40});run(s,{type:'layer',layer:2});run(s,{type:'create'});assert.equal(state(s).boxes.length,2);run(s,{type:'undo'});assert.equal(state(s).boxes.length,1);assert.equal(state(s).boxes[0].x,515);run(s,{type:'undo'});assert.equal(state(s).boxes[0].x,original.x);
});

test('archived restored instructions cannot replay even with a matching revision',()=>{
 const s=two(),id=box(s).id;run(s,{type:'taskAdd',task:{task_id:'archived',box_ids:[id],revision:state(s).revision,activeLayer:1,applied:false,archived:true}});const before=state(s).boxes;assert.equal(s.dispatch({type:'aiApply',task_id:'archived',actions:[{type:'patch',box_id:id,changes:{label:'Replay'}}]}).error,'staleReply');assert.deepEqual(state(s).boxes,before);
});
