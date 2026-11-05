// Isolated browser-logic tests. All API replies/storage are mocks; no real approvals.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('annotation_tool/index.html','utf8').split('<script>')[1].split('</script>')[0];
const elements = new Map(), storage = new Map(), requests=[];
const element = id => {
  if (!elements.has(id)) elements.set(id,{value:'',checked:false,textContent:'',style:{},classList:{add(){},remove(){}},getContext(){return {};},addEventListener(){},options:[]});
  return elements.get(id);
};
const context = vm.createContext({console,Image:class {},document:{getElementById:element},
  window:{addEventListener(){}},setInterval(){},setTimeout(){},
  localStorage:{getItem:key=>storage.get(key)||null,setItem:(k,v)=>storage.set(k,v),removeItem:key=>storage.delete(key)},
  fetch:async (url,options)=>{requests.push({url,payload:JSON.parse(options.body)});return {json:async()=>({success:true,work_saved_at:'2030-01-01T00:00:00Z'})};}});
vm.runInContext(source,context);
async function main() {
  vm.runInContext(`
    imagesList=[{name:'notebook_001',approved:true},{name:'notebook_002',approved:false},{name:'notebook_003',approved:true},{name:'notebook_004',approved:false}];
    currentImageIndex=1; currentRecord=imagesList[1];
    polygon=[[1,1],[9,1],[4,9]]; exclusions=[];
    globalThis.selected=-1;
    selectImage=index=>{globalThis.selected=index};
    populateImageSelector=()=>{};updateSidebarMeta=()=>{};
    nextUnapproved();
  `,context);
  assert.equal(context.selected,3,'navigation skips already approved records');
  element('inspection-confirm').checked=true;
  vm.runInContext('lastWork=null;preserveWork();',context);
  await vm.runInContext('workQueue',context);
  assert.equal(requests[0].url,'/api/autosave');
  assert.equal(requests[0].payload.inspected,undefined);
  assert.equal(requests[0].payload.status,undefined);
  assert.equal(element('inspection-confirm').checked,false,'editing invalidates checkbox');
  assert.ok(storage.has('measureit-work-notebook_002'));
  assert.equal(vm.runInContext('currentRecord.approved',context),false);
  context.fetch=async()=>({json:async()=>({success:true})});
  element('inspection-confirm').checked=true; element('reviewer-name').value='UI fixture only';
  element('status-select').value='manually_verified';context.selected=-1;
  await vm.runInContext('saveVerifiedMask()',context);
  assert.equal(vm.runInContext('imagesList[1].approved',context),true);
  assert.equal(context.selected,3,'successful explicit save advances to next unapproved');
  vm.runInContext('imagesList[1].approved=false;currentRecord=imagesList[1];',context);
  context.selected=-1;context.fetch=async()=>({json:async()=>({success:false,error:'fixture write failure'})});
  element('inspection-confirm').checked=true;
  await vm.runInContext('saveVerifiedMask()',context);
  assert.equal(context.selected,-1,'failed save does not advance');
  assert.equal(vm.runInContext('currentRecord.approved',context),false);
  storage.set('measureit-reviewer','Saved fixture name');
  vm.runInContext('setupEventListeners=()=>{};fetchImages=async()=>{};',context);
  await vm.runInContext('init()',context);
  assert.equal(element('reviewer-name').value,'Saved fixture name');
  console.log('PASS: next-unapproved, autosave separation, checkbox reset, success/error navigation, reviewer persistence');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
