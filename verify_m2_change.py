"""Verify that M2 changes only the U8 exposed-pad ground connection."""
from pathlib import Path
import json, collections
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import make_valid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Rectangle

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'production/M2'
OUT.mkdir(exist_ok=True)
A=json.loads((ROOT/'.audit/M2-M1-geometry.json').read_text())
B=json.loads((ROOT/'.audit/M2-M2-geometry.json').read_text())
def geom(x):
    return unary_union([make_valid(Polygon(p['outer'],p['holes'])) for p in x['polygons']])
def signature(x):
    return json.dumps({k:v for k,v in x.items() if k!='id'},sort_keys=True)
def nonzones(d):
    return collections.Counter(signature(x) for x in d['shapes'] if x['kind']!='zone' and not x['id'].startswith('U8.9:'))
assert nonzones(A)==nonzones(B),'Unrelated pad/track/via geometry or net changed'
assert A['holes']==B['holes'],'Drills changed'
epA=next(x for x in A['shapes'] if x['id'].startswith('U8.9:'))
epB=next(x for x in B['shapes'] if x['id'].startswith('U8.9:'))
assert epA['net']=='GND' and epB['net']==''
assert epA['polygons']==epB['polygons'] and epA['layer']==epB['layer']
ep=geom(epB)
cx,cy=ep.centroid.coords[0]
roi=box(cx-1.7,cy-2.2,cx+1.7,cy+2.2)
def copper(d,l):
    return unary_union([geom(x) for x in d['shapes'] if x['layer']==l])
report={'m1_board_sha256':A['board_sha256'],'m2_board_sha256':B['board_sha256'],
        'nonzone_geometry_and_nets_except_U8_EP':'identical','drills':'identical',
        'EP_shape':'identical','EP_before':'GND','EP_after':'isolated',
        'change_roi_native_mm':list(roi.bounds),'layers':{}}
for l,name in A['layers'].items():
    a,b=copper(A,int(l)),copper(B,int(l))
    delta=a.symmetric_difference(b)
    # Serialized polygon intersections can differ below the 1 nm KiCad grid.
    meaningful=a.difference(b.buffer(.000001)).union(b.difference(a.buffer(.000001)))
    assert meaningful.difference(roi).area<1e-9,('Copper changed outside U8',name,delta.bounds)
    if int(l)!=epB['layer']:
        assert delta.area<1e-9,('Other copper layer changed',name)
    report['layers'][name]={'changed_area_mm2':delta.area,'outside_roi_raw_mm2':delta.difference(roi).area,'outside_roi_above_1nm_mm2':meaningful.difference(roi).area}
near=[(ep.distance(geom(x)),x['net'],x['kind']) for x in B['shapes'] if x['layer']==epB['layer'] and not x['id'].startswith('U8.9:')]
clearance=min(x[0] for x in near)
assert clearance>=.149,('EP not isolated',clearance)
report['EP_minimum_other_copper_gap_mm']=clearance
report['pass']=True
(OUT/'U8_only_change_verification.json').write_text(json.dumps(report,indent=2))

def draw(ax,g,color,z=1):
    if g.is_empty:return
    if g.geom_type!='Polygon':
        for part in g.geoms:draw(ax,part,color,z)
        return
    vertices=[]; codes=[]
    for ring in [g.exterior,*g.interiors]:
        pts=list(ring.coords)
        vertices.extend(pts)
        codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(pts)-2)+[MPath.CLOSEPOLY])
    ax.add_patch(PathPatch(MPath(vertices,codes),facecolor=color,edgecolor='none',zorder=z))

a,b=copper(A,epA['layer']),copper(B,epB['layer'])
removed=a.difference(b)
assert b.difference(a.buffer(.000001)).area<1e-9,'Unexpected added copper'
fig,axes=plt.subplots(1,2,figsize=(12,6),layout='constrained')
fig.suptitle('Robot HAT D1-M2: U8 exposed pad 9 ONLY',fontsize=18,fontweight='bold')
for ax,g,title in zip(axes,[a,b],['M1 - superseded: EP connected to GND','M2 - use this: EP electrically isolated']):
    ax.set_facecolor('#182630')
    window=box(cx-2.2,cy-2.15,cx+2.2,cy+2.15)
    draw(ax,g.intersection(window),'#bba16d')
    if ax is axes[0]:draw(ax,removed,'#ff4545',3)
    ax.add_patch(Rectangle((ep.bounds[0]-.06,ep.bounds[1]-.06),ep.bounds[2]-ep.bounds[0]+.12,ep.bounds[3]-ep.bounds[1]+.12,fill=False,edgecolor='#00eaff',linewidth=2,zorder=5))
    ax.text(cx,cy,'9\nEP',ha='center',va='center',fontsize=14,fontweight='bold',color='#00151e',zorder=6)
    for p in B['shapes']:
        if p['kind']=='pad' and p['id'].startswith('U8.') and not p['id'].startswith('U8.9:'):
            pin=p['id'].split('.')[1].split(':')[0]
            if not pin:continue
            x,y=geom(p).centroid.coords[0]
            ax.text(x,y,pin,ha='center',va='center',fontsize=11,color='black',zorder=6)
    ax.set(xlim=(cx-2.2,cx+2.2),ylim=(cy+2.15,cy-2.15),aspect='equal',title=title)
    ax.set_xticks([]);ax.set_yticks([])
fig.supxlabel('B.Cu viewed from TOP. Red = removed GND copper. Cyan = U8 pad 9. Pin 5 stays GND.\nKeep pad, mask and paste. Components, placement and all other circuitry unchanged.',fontsize=12)
fig.savefig(OUT/'U8_only_change.png',dpi=160)
plt.close(fig)
print(json.dumps(report))
