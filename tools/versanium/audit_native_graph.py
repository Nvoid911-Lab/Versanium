"""Read-only post-GN audit. Never runs GN/Ninja/Siso/compiler or edits saved files."""
from pathlib import Path
import argparse
import json
import os
import shutil
import prepare_native_diagnostic as p

SOURCES={
 'chrome/browser/ui/android/exclusive_access/exclusive_access_context_android.cc':'//chrome/browser/ui/android/exclusive_access:exclusive_access',
 'chrome/browser/ui/android/exclusive_access/exclusive_access_manager_android.cc':'//chrome/browser/ui/android/exclusive_access:exclusive_access',
 'chrome/browser/ui/exclusive_access/fullscreen_controller.cc':'//chrome/browser/ui/exclusive_access:exclusive_access',
}
def logical_lines(data):
    pending=b''
    for line in data.splitlines():
        pending+=line.lstrip() if pending else line
        trailing=len(pending)-len(pending.rstrip(b'$'))
        if trailing%2:pending=pending[:-1];continue
        yield pending;pending=b''
    p.require(not pending,'Incomplete Ninja continuation')
def objects(out,source,descriptions,toolchain,edge_base=None):
    nodes={}
    for doc in descriptions:
        for k,v in doc.items():
            p.require(k not in nodes,'Duplicate GN description target: '+k)
            nodes[k]=v
    for name,label in SOURCES.items():
        matches=[v for k,v in nodes.items() if k.split('(')[0]==label and '//'+name in v.get('sources',[]) and v.get('toolchain')==toolchain]
        p.require(len(matches)==1,'GN source/target/toolchain missing or duplicate: '+name)
    pending=['build.ninja'];seen=set();definitions={};found={n:[] for n in SOURCES}
    while pending:
        n=pending.pop()
        if n in seen:continue
        seen.add(n);path=out/n
        p.require(path.is_file() and path.resolve().is_relative_to(out.resolve()) and not path.is_symlink(),'Missing/aliased graph include: '+n)
        for line in logical_lines(path.read_bytes()):
            if line.startswith((b'include ',b'subninja ')):
                value=line.split(b' ',1)[1].strip()
                p.require(b'$' not in value,'Unresolved/escaped graph include; review required')
                pending.append(os.fsdecode(value));continue
            if not line.startswith(b'build '):continue
            lhs,sep,rhs=line[6:].partition(b':')
            p.require(bool(sep),'Malformed Ninja build edge')
            tokens=rhs.split()
            if not tokens:continue
            outputs=lhs.split()
            for output in outputs:
                if output==b'|':break
                p.require(output not in definitions,'Duplicate Ninja output definition: '+os.fsdecode(output))
                definitions[output]=n
            if tokens[0]!=b'cxx' or len(tokens)<2:continue
            src=tokens[1]
            if b'$' in src:continue  # Never silently de-escape; unresolved edges cannot match.
            actual=((edge_base or out)/os.fsdecode(src)).resolve()
            for name in found:
                if actual!=(source/name).resolve():continue
                for output in outputs:
                    if output.startswith(b'obj/') and output.endswith(b'.o'):
                        p.require(b'$' not in output,'Escaped object output requires review')
                        found[name].append({'target':os.fsdecode(output),'rule':'cxx','source':name,'ninja':n,'toolchain':toolchain})
    for name,values in found.items():p.require(len(values)==1,'Default-toolchain object absent/duplicate: '+name)
    return {'objects':[v[0] for v in found.values()],'loaded_graphs':{n:p.file_hash(out/n) for n in sorted(seen)}}
def graph_delta(before,after):
    delta=[]
    for n in set(before)|set(after):
        if before.get(n)!=after.get(n):
            p.require(p.graph_file(n),'Non-graph output changed during GN: '+n);delta.append(n)
    return sorted(delta)
def run(a):
    prior,baseline=p.baseline(a);record=json.loads(a.source_record.read_text())
    p.require(record.get('source_applied') is True and record.get('phase')=='SOURCE_ONLY_GRAPH_UNCHANGED','Need source-only completed record')
    p.require(record['controller']==p.git(a.control,'rev-parse','HEAD').decode().strip() and record['baseline']==baseline,'Controller/baseline changed')
    for key,path in [('forward_applied',a.forward_applied),('after_apk',a.after_apk),('forward_apk',a.forward_apk)]:p.require(record['baseline_hashes'][key]==p.file_hash(path),'Baseline evidence changed')
    s,out,data,changed,mhash,mod,tools,signing=p.environment(a,p.AFTER,record['updated_provenance'])
    p.require(record['manifest']==mhash and record['tools']==tools and record['signing']==signing and record['paths']==[str(a.workspace),str(s),str(out)],'Paths/manifest/tools/config drift')
    p.require(p.nonselected_diff(s,record['changed'])==record['other_diff'],'Other source changed')
    now=p.inventory(out);delta=graph_delta(record['output'],now)
    p.require(a.gn_status.read_text().strip()=='0','GN did not report success')
    descriptions=[json.loads(f.read_text()) for f in a.gn_desc]
    graph=objects(out,s,descriptions,a.toolchain)
    old_graph=objects(Path(record['backup'])/'output',s,descriptions,a.toolchain,edge_base=out)
    p.require(old_graph['objects']==graph['objects'],'Object edge identities changed; explicit review required')
    result={'configuration':p.AFTER,'phase':'GRAPH_AUDITED_NOT_COMPILED','source_record_sha256':p.file_hash(a.source_record),'gn_log_sha256':p.file_hash(a.gn_log),'gn_status_sha256':p.file_hash(a.gn_status),'gn_descriptions':{str(f):p.file_hash(f) for f in a.gn_desc},'graph_delta':sorted(delta),'graph':graph,'old_graph':old_graph,'output':now,'provenance':record['updated_provenance'],'tools':tools}
    evidence=a.evidence.parent.resolve()/a.evidence.name
    p.require(a.workspace not in evidence.parents,'Evidence must be external')
    p.require(not evidence.exists(),'Never overwrite graph evidence')
    saved=evidence.with_suffix('.graphs');saved.mkdir()
    for n in set(graph['loaded_graphs'])|{n for n in delta if n in now}:
        q=saved/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(out/n,q)
        p.require(p.file_hash(q)==now[n]['sha256'],'Graph moved while backing up: '+n)
    result['updated_graph_backup']=str(saved)
    p.write_json(evidence,result)
    p.require(p.inventory(out)==now,'Output moved during read-only graph audit')
    print('Post-GN read-only audit PASS; actual object targets saved in evidence, compilation NOT RUN')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ['workspace','control','forward-applied','after-apk','forward-apk','source-record','gn-log','gn-status','evidence']:parser.add_argument('--'+n,type=Path,required=True)
    parser.add_argument('--gn-desc',type=Path,action='append',required=True)
    parser.add_argument('--toolchain',required=True)
    a=parser.parse_args();a.workspace=a.workspace.absolute();a.control=a.control.resolve();run(a)
