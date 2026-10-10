import {loadPyodide} from './runtime/pyodide.mjs';
const out=document.querySelector('#output'),status=document.querySelector('#runtime');
const buttons=[...document.querySelectorAll('button')];
function show(x){out.textContent=JSON.stringify(x,null,2);}
function safeError(){show({status:'REJECTED',note:'Malformed or unapproved metadata. Submitted content is not echoed.'});}
async function digest(b){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');}
const buffers=new Map();
async function start(){
 const manifest=await (await fetch('asset-manifest.json')).json();
 for(const [path,record] of Object.entries(manifest.files)){
  const r=await fetch(path);if(!r.ok)throw Error('asset unavailable');const b=await r.arrayBuffer();
  if(b.byteLength!==record.bytes || await digest(b)!==record.sha256)throw Error('asset mismatch');buffers.set(path,new Uint8Array(b));
 }
 document.querySelector('#version').textContent='Build base: '+manifest.base_commit+' | Runtime: Pyodide '+manifest.runtime_version+' | All allowlisted assets hash-checked.';
 const published=JSON.parse(new TextDecoder().decode(buffers.get('assets/omm12_integrated_readiness_20261010.json')));
 const cards=document.querySelector('#summary');cards.textContent='';
 for(const [name,d] of Object.entries(published.domains)){const card=document.createElement('div');card.className='card';const title=document.createElement('strong');title.textContent=name.replace('_',' ');const tag=document.createElement('span');tag.className='tag'+(d.blocking?'':' good');tag.textContent=d.blocking?'BLOCKED / UNRESOLVED':'CONSISTENT ONLY';const p=document.createElement('p');p.textContent=d.status;card.append(title,tag,p);cards.append(card);}
 const py=await loadPyodide({indexURL:'./runtime/'});
 function mount(path,data){const parent=path.slice(0,path.lastIndexOf('/'));py.FS.mkdirTree(parent);py.FS.writeFile(path,data);}
 for(const [path,b] of buffers){if(path.startsWith('python/'))mount('/app/'+path.slice(7),b);if(path.startsWith('assets/'))mount('/public/'+path.slice(7),b);}
 await py.runPythonAsync("import sys\nsys.path.insert(0,'/app')\nfrom microtwin.source_readiness import packet\nfrom microtwin.censor_contract import load_censor_contract\nfrom microtwin.admission_demo import create_demo\nfrom microtwin.admission_evidence_bundle import create_receipt\nimport json\n");
 document.querySelector('#contract').value=new TextDecoder().decode(buffers.get('assets/omm12_censor_semantics_metadata_20261010.json'));
 async function run(code){buttons.forEach(b=>b.disabled=true);status.textContent='Running exact Python checks locally...';try{show(JSON.parse(await py.runPythonAsync(code)));status.textContent='Done. No data transmitted.';}catch{safeError();status.textContent='Rejected safely. No content echoed.';}finally{buttons.forEach(b=>b.disabled=false);}}
 document.querySelector('#omm').onclick=()=>run("json.dumps(packet('/public'))");
 document.querySelector('#synthetic').onclick=()=>run("json.dumps(packet('/synthetic'))");
 document.querySelector('#malformed').onclick=()=>{py.FS.writeFile('/malformed.json','{"raw_value":"synthetic sentinel"}');run("json.dumps(load_censor_contract('/malformed.json'))");};
 document.querySelector('#check').onclick=()=>{const t=document.querySelector('#contract').value;if(new TextEncoder().encode(t).length>10000){safeError();return;}py.FS.writeFile('/editor.json',t);run("json.dumps(load_censor_contract('/editor.json'))");};
 // Synthetic public fixtures are not source outcomes or real approval.
 for(const [path,b] of buffers)if(path.startsWith('synthetic/'))mount('/synthetic/'+path.slice(10),b);
 buttons.forEach(b=>b.disabled=false);status.textContent='Ready. Exact validators run in this browser only.';show(published);
}
start().catch(()=>{status.textContent='Runtime or asset integrity check failed. No checks executed.';safeError();});
