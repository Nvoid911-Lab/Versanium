"""Review repository rename/metadata plan. --apply requires synchronized migration branch and unchanged main and original assets.
Never changes Secrets, signing settings, topics by subtraction, releases, tags, or default branches.
"""
from pathlib import Path
import argparse,json,re,subprocess
from apply import check_assets

REPO=Path(__file__).resolve().parents[2]
OWNERS=('Nvoid911','Nvoid911-Lab')
DESCRIPTION='An Android browser focused on providing a comfortable and consistent browsing experience across smartphones and desktop-style environments.'
TOPICS=['android','browser','chromium','titanium','samsung-dex','desktop-mode','android-browser','chromium-browser']

def api(method,path,body=None):
    command=['gh','api','--method',method,path]
    if body is not None:command+=['--input','-']
    result=subprocess.run(command,input=None if body is None else json.dumps(body),text=True,capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)


def apply(expected):
    if not re.fullmatch('[0-9a-f]{40}',expected):raise ValueError('Expected exact reviewed SHA')
    check_assets(REPO)
    readme=subprocess.check_output(['git','show',expected+':README.md'],cwd=REPO,text=True)
    if not readme.startswith('# Versanium\n'):raise RuntimeError('Expected branded migration commit')
    # Read both current states before the first mutation. Preserve unknown existing topics.
    states=[]
    for owner in OWNERS:
        state=api('GET',f'repos/{owner}/android-titanium-browser')
        if state['owner']['login'].lower()!=owner.lower() or state['name'] not in ('android-titanium-browser','Versanium'):
            raise RuntimeError('Unexpected repository identity')
        if state['default_branch']!='main':raise RuntimeError('Review non-main default branch before migration')
        head=api('GET',f'repos/{state["full_name"]}/git/ref/heads/main')['object']['sha']
        if head!='6755ccfd5d5c8a5e8fa3620be6da9ccd4a399aa7':raise RuntimeError('Main changed: review before metadata changes')
        migration=api('GET',f'repos/{state["full_name"]}/git/ref/heads/migration/versanium')['object']['sha']
        if migration!=expected:raise RuntimeError('Both migration branches must match the reviewed commit')
        if not state.get('permissions',{}).get('admin'):raise RuntimeError('Repository administration permission required')
        states.append(state)
    for state in states:
        renamed=api('PATCH','repos/'+state['full_name'],{'name':'Versanium','description':DESCRIPTION})
        name=renamed['full_name']
        topics=sorted(set(state.get('topics',[]))|set(TOPICS))
        api('PUT','repos/'+name+'/topics',{'names':topics})
        confirmed=api('GET','repos/'+name)
        if confirmed['name']!='Versanium' or confirmed['description']!=DESCRIPTION or not set(topics)<=set(confirmed['topics']):
            raise RuntimeError('Repository metadata verification failed; inspect the reported current state before retrying')
        print('Verified:',confirmed['html_url'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--expected-sha');a=p.parse_args()
    if a.apply:
        if not a.expected_sha:p.error('--apply requires --expected-sha')
        apply(a.expected_sha)
    else:
        print(json.dumps({'primary':'https://github.com/Nvoid911/Versanium','secondary':'https://github.com/Nvoid911-Lab/Versanium','description':DESCRIPTION,'topics_to_add_without_removing_existing':TOPICS,'apply_requires':'Reviewed branded SHA on both migration/versanium branches; unchanged main, original assets, and working GitHub API access'},indent=2))
