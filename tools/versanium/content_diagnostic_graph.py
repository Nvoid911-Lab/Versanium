"""Independent literal Ninja graph inspection; no execution and no old helper imports."""
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
    # GN android_library creates __compile_java and optional __errorprone[_shardN]
    # actions. Their rules encode target + toolchain; the .ninja filename does not.
    specs=[('content/public/android','content_full_java',[proxy,'content/public/android/java/src/org/chromium/content_public/browser/WebContentsObserver.java']),
           ('chrome/android','chrome_java',['chrome/android/java/src/org/chromium/chrome/browser/media/FullscreenVideoPictureInPictureController.java'])]
    for directory,family,names in specs:
        prefix=('__'+directory.replace('/','_')+'_'+family).encode()
        suffix=b'___build_toolchain_android_android_clang_arm64__rule'
        compile_rule=prefix+b'__compile_java'+suffix
        output=('obj/'+directory+'/'+family).encode()
        jar=output+b'.javac.jar'
        required={jar,jar+b'.info'};allowed=required|{output+b'.compliment.jar'}
        hits=[edge for edge in graph['edges'] if edge['rule']==compile_rule]
        if len(hits)!=1:raise MissingCoverage('Production Java compiler action absent or ambiguous: '+family)
        edge=hits[0];raw=recipe(graph,edge)
        require(required<=set(edge['outputs'])<=allowed,'Unexpected exact Java compiler outputs: '+family)
        require(b'compile_java.py' in raw and b'errorprone.py' not in raw and b'turbine.py' not in raw,'Wrong Java compiler recipe: '+family)
        if not depends_on(graph,edge,jni_edge):raise MissingCoverage('Java compiler graph does not prove dependency on content JNI: '+family)
        for name in names:
            if not any(path_at(out,i)==(source/name).resolve() for i in edge['inputs']):raise MissingCoverage('Production Java compiler direct source absent: '+name)
            java.append({'source':name,'gn_family':family,'compiler_nullaway_flag_observed':b'--enable-nullaway' in raw,'targets':[os.fsdecode(jar)],'outputs':[os.fsdecode(t) for t in edge['outputs']],'rule':os.fsdecode(edge['rule']),'ninja':edge['ninja'],'recipe_sha256':hashlib.sha256(raw).hexdigest()})
        pattern=re.compile(re.escape(prefix)+rb'__errorprone(_shard[0-9]+)?'+re.escape(suffix))
        found=[];seen_ep_rules=set()
        for candidate in graph['edges']:
            match=pattern.fullmatch(candidate['rule'])
            if not match:continue
            require(candidate['rule'] not in seen_ep_rules,'Ambiguous duplicate ErrorProne rule: '+family)
            seen_ep_rules.add(candidate['rule'])
            label=family+'__errorprone'+(match.group(1).decode() if match.group(1) else '')
            stamp=('obj/'+directory+'/'+label+'.stamp').encode()
            require(candidate['outputs']==[stamp],'Unexpected exact ErrorProne output: '+label)
            ep_raw=recipe(graph,candidate)
            require(b'errorprone.py' in ep_raw and b'compile_java.py' not in ep_raw and b'turbine.py' not in ep_raw,'Wrong ErrorProne recipe: '+label)
            require(depends_on(graph,edge,candidate),'ErrorProne action not linked to Java compile validations: '+label)
            found.append((candidate,ep_raw,match.group(1)))
        require(not (any(shard is None for _,_,shard in found) and len(found)>1),'Ambiguous sharded/unsharded ErrorProne actions: '+family)
        for name in names:
            matches=[(candidate,ep_raw) for candidate,ep_raw,_ in found if any(path_at(out,i)==(source/name).resolve() for i in candidate['inputs'])]
            require(len(matches)<=1,'Ambiguous ErrorProne source membership: '+name)
            require(not found or matches,'ErrorProne family exists but direct source membership unproven: '+name)
            for candidate,ep_raw in matches:
                analysis.append({'source':name,'targets':[os.fsdecode(t) for t in candidate['outputs']],'rule':os.fsdecode(candidate['rule']),'ninja':candidate['ninja'],'nullaway_flag_observed':b'--enable-nullaway' in ep_raw,'recipe_sha256':hashlib.sha256(ep_raw).hexdigest()})
    return {'objects':objects,'jni':generated,'java':java,'errorprone':analysis,'nullaway_status':'GRAPH_ACTIONS_REQUIRE_EXECUTION_REVIEW' if analysis else 'NOT_PROVEN_NO_ACTIONS_FOUND','gn_requirement':'NO_REGEN_INDICATED_BY_LITERAL_GRAPH_COVERAGE','limitation':'GN descriptions not newly executed; fixed target membership plus recorded default toolchain/literal graph. Ambiguous/indirect inputs require review, not guessed targets.'}
