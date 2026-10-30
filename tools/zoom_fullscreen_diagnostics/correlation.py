"""Fail-closed, explicit-unit checks for normalized matched diagnostic records.

Normalization must explicitly resolve raw browser/widget/frame joins; this module
does not infer identity from timestamps or infer correction from a zero value.
"""
import math

IDENTITY=('trial','wc','frame','document','widget','grant')
def same_identity(records):
    if not records:raise ValueError('No records')
    reference=tuple(records[0].get(k) for k in IDENTITY)
    if any(v is None or v=='unknown' or v=='' for v in reference):raise ValueError('Missing identity')
    for r in records:
        if tuple(r.get(k) for k in IDENTITY)!=reference:raise ValueError('Mismatched identity')
    return reference

def geometry_ratio(video,viewport):
    if video.get('unit')!=viewport.get('unit') or video.get('space')!=viewport.get('space'):
        raise ValueError('Coordinate mismatch')
    if video.get('unit') not in ('css_px','root_paint_px','device_px','dip'):
        raise ValueError('Unknown unit')
    if video.get('space') in (None, '', 'unknown'):
        raise ValueError('Unknown coordinate space')
    for r in (video,viewport):
        if not all(math.isfinite(r[k]) and r[k]>0 for k in ('w','h')):raise ValueError('Invalid geometry')
    return video['w']/viewport['w'],video['h']/viewport['h']

def validate_chain(records):
    same_identity(records)
    kinds=[r['event'] for r in records]
    required=('VISUAL_PROPERTIES_SEND','VISUAL_PROPERTIES_RECEIVED','RENDERER_ZOOM_ADOPTED')
    if any(kinds.count(k)!=1 for k in required):raise ValueError('Missing/ambiguous stage')
    stages=[records[kinds.index(k)] for k in required]
    if not kinds.index(required[0])<kinds.index(required[1])<kinds.index(required[2]):raise ValueError('Wrong stage order')
    if not all(math.isfinite(r['zoom_exp']) for r in stages):raise ValueError('Invalid zoom')
    if stages[0]['zoom_exp']!=stages[1]['zoom_exp']:raise ValueError('Transport mismatch')
    if stages[2]['zoom_exp']!=stages[1]['zoom_exp'] and not stages[2].get('clamp_documented'):
        raise ValueError('Unexplained adoption')
    selected=[i for i,k in enumerate(kinds) if k=='FULLSCREEN_CORRECTION_SELECTED']
    if len(selected)>1:raise ValueError('Ambiguous selection')
    if selected and (selected[0]>=kinds.index(required[0]) or 'FULLSCREEN_CORRECTION_SKIP' in kinds):
        raise ValueError('Ambiguous selection path')
    if selected:
        value=records[selected[0]].get('selected_exp')
        if value is None or not math.isfinite(value) or value!=stages[0]['zoom_exp']:
            raise ValueError('Selection did not reach this send')
    layouts=[r for i,r in enumerate(records) if r['event']=='FULLSCREEN_LAYOUT'
             and i>kinds.index(required[2]) and r.get('valid')]
    for r in layouts:geometry_ratio(r['video'],r['viewport'])
    return {'transport_and_adoption':True,'correction_applied':
            bool(selected) and stages[0]['zoom_exp']==0 and stages[2]['zoom_exp']==0 and bool(layouts)}
