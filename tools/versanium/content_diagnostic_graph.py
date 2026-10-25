"""Independent literal Ninja graph inspection; no execution and no old helper imports."""
from pathlib import Path
import hashlib
import os
import re

class UnsupportedGraph(RuntimeError):pass
class MissingCoverage(RuntimeError):pass
def require(ok,message):
    if not ok:raise UnsupportedGraph(message)
def lines(raw):
    carry=b''
    for physical in raw.split(b'\n'):
        if physical.endswith(b'\r'):physical=physical[:-1]
        if not carry and physical.lstrip(b' \t').startswith(b'#'):
            yield physical;continue
        carry+=physical.lstrip(b' \t') if carry else physical
        if (len(carry)-len(carry.rstrip(b'$')))%2:
            carry=carry[:-1];continue
        yield carry;carry=b''
    require(not carry,'Incomplete Ninja continuation')
def lex(raw):
    parts=[];token=bytearray();i=0
    def flush():
        if token:parts.append(bytes(token));token.clear()
    while i<len(raw):
        c=raw[i]
        if c==36:
            require(i+1<len(raw) and raw[i+1] in (32,36,58),'Unsupported variable/escape in graph path: '+repr(raw[i:i+24]))
            token.append(raw[i+1]);i+=2
        elif c in (32,9):flush();i+=1
        elif c in (58,124):
            flush();operator=raw[i:i+2] if raw[i:i+2] in (b'||',b'|@') else bytes([c]);parts.append(operator.decode('ascii'));i+=len(operator)
        else:
            require(c not in (0,10,13,35),'Ambiguous graph path byte');token.append(c);i+=1
    flush();return parts
def parse_edge(raw):
    t=lex(raw);require(t.count(':')==1,'Missing/ambiguous edge separator');i=t.index(':');out=t[:i];tail=t[i+1:]
    require(out and isinstance(out[0],bytes) and tail and isinstance(tail[0],bytes),'Missing output/rule')
    require(out.count('|')<=1 and all(isinstance(x,bytes) or x=='|' for x in out) and isinstance(out[-1],bytes),'Invalid output groups')
    require(re.fullmatch(rb'[A-Za-z0-9_.-]+',tail[0]) is not None,'Invalid rule')
    explicit=[];inputs=[];group=0;empty=False
    for x in tail[1:]:
        if isinstance(x,bytes):
            inputs.append(x)
            if group==0:explicit.append(x)
            empty=False
        else:
            order={'|':1,'||':2,'|@':3}.get(x,0);require(order>group and not empty,'Invalid input groups');group=order;empty=True
    require(not empty,'Empty input group')
    return {'outputs':[x for x in out if isinstance(x,bytes)],'rule':tail[0],'explicit':explicit,'inputs':inputs,'bindings':[]}
def load(out):
    seen={};edges=[];outputs={};rules={};parents={0:None};active=set()
    def visit(name,scope):
        require(name not in active,'Recursive Ninja include');active.add(name);path=out/name
        require(path.is_file() and path.resolve().is_relative_to(out.resolve()) and not path.is_symlink(),'Missing/aliased graph: '+name)
        raw=path.read_bytes();seen[name]=hashlib.sha256(raw).hexdigest();owner=None
        for line in lines(raw):
            if not line or line.startswith(b'#'):continue
            if line[:1] in (b' ',b'\t'):
                if owner is not None:owner.append(line)
                continue
            owner=None
            if line.startswith((b'include ',b'subninja ')):
                values=lex(line.split(b' ',1)[1]);require(len(values)==1 and isinstance(values[0],bytes),'Unresolved include')
                child=scope
                if line.startswith(b'subninja '):child=len(parents);parents[child]=scope
                visit(os.fsdecode(values[0]),child);continue
            if line.startswith(b'rule '):
                rule=(scope,line[5:].strip());require(rule not in rules,'Duplicate Ninja rule in same scope');rules[rule]=[];owner=rules[rule];continue
            if not line.startswith(b'build '):continue
            edge=parse_edge(line[6:]);edge.update(ninja=name,scope=scope);owner=edge['bindings'];edges.append(edge)
            for target in edge['outputs']:
                require(target not in outputs,'Duplicate decoded Ninja output: '+os.fsdecode(target));outputs[target]=edge
        active.remove(name)
    visit('build.ninja',0)
    return {'files':seen,'edges':edges,'outputs':outputs,'rules':rules,'parents':parents}
def path_at(out,b):return (out/os.fsdecode(b)).resolve()
def recipe(graph,edge):
    rule=edge['rule'];scope=edge['scope'];body=None
    while scope is not None:
        if (scope,rule) in graph['rules']:body=graph['rules'][(scope,rule)];break
        scope=graph['parents'][scope]
    require(body is not None or rule==b'phony','Undefined Ninja rule: '+os.fsdecode(rule))
    return b'\n'.join((body or [])+edge['bindings']+edge['inputs'])
def depends_on(graph,edge,producer):
    todo=list(edge['inputs']);seen=set()
    while todo:
        n=todo.pop()
        if n in seen:continue
        seen.add(n);parent=graph['outputs'].get(n)
        if parent is producer:return True
        if parent:todo.extend(parent['inputs'])
    return False
def coverage(graph,out,source,toolchain):
    require(toolchain=='//build/toolchain/android:android_clang_arm64','Unexpected recorded default toolchain')
    cpp=['content/browser/renderer_host/render_frame_host_impl.cc','content/browser/web_contents/web_contents_impl.cc','content/browser/media/media_web_contents_observer.cc','content/browser/android/web_contents_observer_proxy.cc']
    objects=[];object_edges={}
    for name in cpp:
        hits=[]
        for e in graph['edges']:
            if e['rule']!=b'cxx' or len(e['explicit'])!=1 or path_at(out,e['explicit'][0])!=(source/name).resolve():continue
            hits += [(e,t) for t in e['outputs'] if t.startswith(b'obj/') and t.endswith(b'.o')]
        if len(hits)!=1:raise MissingCoverage('Native source/cxx/default-toolchain absent or ambiguous: '+name)
        e,t=hits[0];objects.append({'source':name,'target':os.fsdecode(t),'rule':'cxx','ninja':e['ninja'],'toolchain':toolchain,'recipe_sha256':hashlib.sha256(recipe(graph,e)).hexdigest()})
        object_edges[name]=e
    proxy='content/public/android/java/src/org/chromium/content/browser/webcontents/WebContentsObserverProxy.java'
    jni=[]
    for e in graph['edges']:
        if not any(path_at(out,i)==(source/proxy).resolve() for i in e['inputs']):continue
        # Android jni_zero.gni uses root_build_dir/gen/jni_headers, not root_gen_dir alone.
        header=[t for t in e['outputs'] if t==b'gen/jni_headers/content/public/android/content_jni_headers/WebContentsObserverProxy_jni.h']
        if e['ninja']!='toolchain.ninja' or e['rule']!=b'__content_public_android_content_jni_headers__action___build_toolchain_android_android_clang_arm64__rule':continue
        if header and b'jni_zero.py' in recipe(graph,e):jni.append((e,header[0]))
    if len(jni)!=1:raise MissingCoverage('JNI action input/proxy header output/generator recipe absent or ambiguous')
    e,header=jni[0]
    if not depends_on(graph,object_edges['content/browser/android/web_contents_observer_proxy.cc'],e):raise MissingCoverage('Native proxy compile edge does not prove dependency on the JNI action')
    # The bridge header must be an actual graph output, not merely a file left on disk.
    generated={'target':os.fsdecode(header),'rule':os.fsdecode(e['rule']),'ninja':e['ninja'],'inputs':[os.fsdecode(i) for i in e['inputs']],'outputs':[os.fsdecode(t) for t in e['outputs']],'recipe_sha256':hashlib.sha256(recipe(graph,e)).hexdigest()}
    java=[];analysis=[];jni_edge=e
    for name in [proxy,'content/public/android/java/src/org/chromium/content_public/browser/WebContentsObserver.java','chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java']:
        hits=[];family='chrome_java' if name.startswith('chrome/') else 'content_full_java'
        for edge in graph['edges']:
            if not any(path_at(out,i)==(source/name).resolve() for i in edge['inputs']):continue
            # GN Android library helper actions have their parent's exact family
            # name or __suffix, not similarly named unit-test target families.
            stem=Path(edge['ninja']).stem
            if stem!=family and not stem.startswith(family+'__'):continue
            jars=[t for t in edge['outputs'] if t.startswith(b'obj/') and t.endswith(b'.jar')]
            if jars and b'compile_java.py' in recipe(graph,edge):hits.append((edge,jars))
        if not hits:raise MissingCoverage('Production Java compiler action/source/.jar coverage absent or unsupported: '+name)
        for edge,jars in hits:
            java.append({'source':name,'gn_family':family,'targets':[os.fsdecode(t) for t in jars],'rule':os.fsdecode(edge['rule']),'ninja':edge['ninja'],'recipe_sha256':hashlib.sha256(recipe(graph,edge)).hexdigest()})
            if not depends_on(graph,edge,jni_edge):raise MissingCoverage('Java compiler graph does not prove dependency on content JNI: '+name)
        for candidate in graph['edges']:
            stem=Path(candidate['ninja']).stem
            if not stem.startswith(family+'__'):continue
            if not any(path_at(out,i)==(source/name).resolve() for i in candidate['inputs']):continue
            raw=recipe(graph,candidate)
            if b'errorprone.py' not in raw:continue
            require(any(depends_on(graph,edge,candidate) for edge,jars in hits),'ErrorProne action not linked to Java compile validations')
            analysis.append({'source':name,'targets':[os.fsdecode(t) for t in candidate['outputs']],'rule':os.fsdecode(candidate['rule']),'ninja':candidate['ninja'],'nullaway_flag_observed':b'--enable-nullaway' in raw,'recipe_sha256':hashlib.sha256(raw).hexdigest()})
    return {'objects':objects,'jni':generated,'java':java,'errorprone':analysis,'nullaway_status':'GRAPH_ACTIONS_REQUIRE_EXECUTION_REVIEW' if analysis else 'NOT_PROVEN_NO_ACTIONS_FOUND','gn_requirement':'NO_REGEN_INDICATED_BY_LITERAL_GRAPH_COVERAGE','limitation':'GN descriptions not newly executed; fixed target membership plus recorded default toolchain/literal graph. Ambiguous/indirect inputs require review, not guessed targets.'}
