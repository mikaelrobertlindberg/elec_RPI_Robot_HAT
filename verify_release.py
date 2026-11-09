"""Independent Gerber/Excellon geometry and assembly-file checks.

Uses gerbonara to interpret actual exported primitives and shapely to build copper
islands. Native pad centres supply net labels; native through holes supply only
the plated-layer association. No KiCad DRC results are used by these checks.
"""
from pathlib import Path
import sys,json,subprocess,csv,math,collections,re,hashlib

ROOT=Path(__file__).resolve().parent
KPY='C:/Program Files/KiCad/9.0/bin/python.exe'

if '--assembly-board' in sys.argv:
 import pcbnew
 b=pcbnew.LoadBoard(str(ROOT/'elec_RPI_Robot_HAT.kicad_pcb'))
 for f in b.GetFootprints():
  f.Value().SetVisible(False)
  f.Reference().SetVisible(True)
 pcbnew.SaveBoard(sys.argv[sys.argv.index('--assembly-board')+1],b)
 sys.exit()

if '--native-facts' in sys.argv:
 import pcbnew
 b=pcbnew.LoadBoard(str(ROOT/'elec_RPI_Robot_HAT.kicad_pcb'))
 origin=b.GetDesignSettings().GetAuxOrigin()
 def xy(p):return [(p.x-origin.x)/1e6,(origin.y-p.y)/1e6]
 layer_ids=[pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.B_Cu]
 pads=[];holes=[];parts=[];tracks=[]
 for f in b.GetFootprints():
  parts.append({'ref':f.GetReference(),'xy':xy(f.GetPosition()),'angle':f.GetOrientationDegrees(),'side':'Bottom' if f.IsFlipped() else 'Top'})
  for p in f.Pads():
   pad={'ref':f.GetReference(),'pin':p.GetNumber(),'net':p.GetNetname(),'xy':xy(p.GetPosition()),'layers':[i for i,l in enumerate(layer_ids) if p.IsOnLayer(l)],'size_mm':[p.GetSize().x/1e6,p.GetSize().y/1e6]}
   pads.append(pad)
   drill=p.GetDrillSize()
   if drill.x:
    holes.append({'xy':pad['xy'],'size':[drill.x/1e6,drill.y/1e6],'plated':p.GetAttribute()!=pcbnew.PAD_ATTRIB_NPTH,'layers':pad['layers']})
 for t in b.GetTracks():
  if isinstance(t,pcbnew.PCB_VIA):
   holes.append({'xy':xy(t.GetPosition()),'size':[t.GetDrillValue()/1e6]*2,'plated':True,'layers':[i for i,l in enumerate(layer_ids) if t.IsOnLayer(l)]})
  else:
   tracks.append({'start':xy(t.GetStart()),'end':xy(t.GetEnd()),'width':t.GetWidth()/1e6,'net':t.GetNetname(),'layer':layer_ids.index(t.GetLayer()),'arc':isinstance(t,pcbnew.PCB_ARC)})
 box=b.GetBoardEdgesBoundingBox();p1=xy(box.GetPosition());p2=xy(pcbnew.VECTOR2I(box.GetRight(),box.GetBottom()))
 print(json.dumps({'origin_mm':[origin.x/1e6,origin.y/1e6],'outline_bounds':[min(p1[0],p2[0]),min(p1[1],p2[1]),max(p1[0],p2[0]),max(p1[1],p2[1])],'pads':pads,'holes':holes,'parts':parts,'tracks':tracks}))
 sys.exit()

from gerbonara.rs274x import GerberFile
from gerbonara.excellon import ExcellonFile
from gerbonara.graphic_objects import Flash
from gerbonara.utils import MM
from shapely.geometry import Point,LineString,Polygon,box
from shapely.ops import unary_union
from shapely.strtree import STRtree

def primitive_polygon(p):
 ap=p.to_arc_poly().approximate_arcs(max_error=.0005)
 if len(ap.outline)<3:return Polygon()
 g=Polygon(ap.outline)
 return g if g.is_valid else g.buffer(0)

def material(file):
 """Respect dark/clear draw order, including clear macro primitives."""
 result=Polygon();batch=[];dark=True
 def flush(result,batch,dark):
  if not batch:return result
  merged=unary_union(batch)
  return result.union(merged) if dark else result.difference(merged)
 for obj in file.objects:
  for p in obj.to_primitives(unit=MM):
   g=primitive_polygon(p)
   if g.is_empty:continue
   if p.polarity_dark!=dark:
    result=flush(result,batch,dark);batch=[];dark=p.polarity_dark
   batch.append(g)
 return flush(result,batch,dark)

def one_file(directory,suffixes):
 candidates=[p for p in directory.iterdir() if any(p.name.endswith(s) for s in suffixes)]
 assert len(candidates)==1,(directory,suffixes,[p.name for p in candidates])
 return candidates[0]

def verify_release(out):
 out=Path(out);fab=out/'fabrication';report={'method':'gerbonara interpreted primitives + shapely copper-island graph','arc_approximation_max_error_mm':.0005}
 facts=json.loads(subprocess.check_output([KPY,str(Path(__file__).resolve()),'--native-facts'],cwd=ROOT,text=True,encoding='utf-8'))
 report['native_plot_origin_mm']=facts['origin_mm'];bounds=facts['outline_bounds'];report['native_outline_bounds_mm']=bounds
 names=['F_Cu','In1_Cu','In2_Cu','B_Cu','F_Mask','B_Mask','Edge_Cuts']
 extensions={'F_Cu':'.gtl','In1_Cu':'.g1','In2_Cu':'.g2','B_Cu':'.gbl','F_Mask':'.gts','B_Mask':'.gbs','Edge_Cuts':'.gm1'}
 files={n:GerberFile.open(one_file(fab,[f'-{n}.gbr',f'-{n}'+extensions[n]])) for n in names}
 report['gerber_object_counts']={n:len(f.objects) for n,f in files.items()}
 assert all(not f.is_empty for f in files.values()),'Empty required fabrication layer'
 edgebox=files['Edge_Cuts'].bounding_box(MM);flat=[*edgebox[0],*edgebox[1]]
 assert max(abs(a-b) for a,b in zip(bounds,flat))<.11,('Gerber/board outline or origin mismatch',bounds,flat)
 copper=[material(files[n]) for n in names[:4]];masks=[material(files[n]) for n in names[4:6]]
 for i,g in enumerate(copper):
  assert g.is_valid and not g.is_empty,('Unreadable copper',names[i])
  assert box(*bounds).buffer(.11).covers(g),('Copper outside board bounds',names[i],g.bounds)
 drills=[];drill_plating=[]
 for p in sorted(fab.glob('*.drl')):
  # gerbonara does not consume KiCad's X2 comment attributes itself. Read the
  # actual file's FileFunction attribute, never infer plating from the filename.
  plating=re.search(r'TF\.FileFunction,(NonPlated|Plated),',p.read_text())
  assert plating,('Missing drill plating FileFunction',p.name)
  d=ExcellonFile.open(p,plated=plating[1]=='Plated');prims=[q for o in d.objects for q in o.to_primitives(unit=MM)]
  for q in prims:
   g=primitive_polygon(q)
   assert box(*bounds).buffer(.15).covers(g),('Drill outside outline bounds',p.name,g.bounds)
   drills.append(g);drill_plating.append(plating[1]=='Plated')
 assert drills,'No drills in exported package'
 # Every native hole must have a centre-aligned tool hit/slot in the actual file.
 for h in facts['holes']:
  pt=Point(h['xy']);matches=[g for g in drills if g.buffer(.003).covers(pt)]
  assert matches,('Missing or shifted drill',h)
  assert any(abs(min(g.bounds[2]-g.bounds[0],g.bounds[3]-g.bounds[1])-min(h['size']))<.015 for g in matches),('Drill tool size mismatch',h)
 for g,plated in zip(drills,drill_plating):
  matches=[h for h in facts['holes'] if Point(h['xy']).distance(g.centroid)<.005 and abs(min(g.bounds[2]-g.bounds[0],g.bounds[3]-g.bounds[1])-min(h['size']))<.015]
  assert matches,('Unexpected exported hole/slot',g.bounds)
  if plated is not None:assert any(h['plated']==plated for h in matches),('Plated/nonplated classification mismatch',g.bounds,plated)
 report['drill_primitives']=len(drills);report['native_holes_matched']=len(facts['holes']);report['drills_with_unknown_plating']=sum(p is None for p in drill_plating)

 # Identify actual U12 pad flashes, independently of native pad-size assertions.
 u12=[p for p in facts['pads'] if p['ref']=='U12'];assert len(u12)==14
 flash_shapes=[]
 for obj in files['F_Cu'].objects:
  if isinstance(obj,Flash):
   gs=[primitive_polygon(q) for q in obj.to_primitives(unit=MM)]
   if gs:flash_shapes.append(unary_union(gs))
 pads=[];mask_pads=[]
 mask_islands=list(masks[0].geoms) if hasattr(masks[0],'geoms') else [masks[0]]
 for p in u12:
  pt=Point(p['xy']);candidates=[g for g in flash_shapes if g.centroid.distance(pt)<.003]
  assert len(candidates)==1,('U12 flash not unique/missing',p,len(candidates))
  pads.append(candidates[0]);candidates=[g for g in mask_islands if g.buffer(.001).covers(pt)]
  assert len(candidates)==1,('U12 mask aperture missing',p)
  mask_pads.append(candidates[0])
 cu_gap=min(a.distance(b) for i,a in enumerate(pads) for b in pads[i+1:])
 mask_gap=min(a.distance(b) for i,a in enumerate(mask_pads) for b in mask_pads[i+1:])
 assert .199<=cu_gap<=.201,('Actual U12 Gerber copper gap',cu_gap)
 assert mask_gap>=.189,('Actual U12 Gerber mask bridge below PCBWay0.19',mask_gap)
 report['u12_exported_min_copper_gap_mm']=cu_gap;report['u12_exported_min_mask_bridge_mm']=mask_gap

 # Actual copper islands, connected across only native plated through holes.
 islands=[];layer_indices=[]
 for layer,g in enumerate(copper):
  polys=list(g.geoms) if hasattr(g,'geoms') else [g]
  ids=[]
  for poly in polys:
   if poly.area<1e-10:continue
   ids.append(len(islands));islands.append(poly)
  layer_indices.append(ids)
 tree=STRtree(islands);parents=list(range(len(islands)))
 def find(x):
  while parents[x]!=x:parents[x]=parents[parents[x]];x=parents[x]
  return x
 def join(a,b):parents[find(a)]=find(b)
 def hits(pt,allowed):
  area=Point(pt).buffer(.001);return [int(i) for i in tree.query(area) if int(i) in allowed and islands[int(i)].intersects(area)]
 for h in facts['holes']:
  if not h['plated']:continue
  ids=hits(h['xy'],set(i for l in h['layers'] for i in layer_indices[l]))
  for i in ids[1:]:join(ids[0],i)
 net_components=collections.defaultdict(set);component_nets=collections.defaultdict(set)
 for p in facts['pads']:
  if not p['layers'] or not p['net'] or p['net'].startswith('unconnected-'):continue
  ids=hits(p['xy'],set(i for l in p['layers'] for i in layer_indices[l]))
  assert ids,('Pad centre missing copper in exported files',p)
  for i in ids:net_components[p['net']].add(find(i));component_nets[find(i)].add(p['net'])
 shorts={str(k):sorted(v) for k,v in component_nets.items() if len(v)>1}
 assert not shorts,('Physical exported copper joins different named nets',shorts)
 critical=[n for n in net_components if any(t in n for t in ['5V','BATT','GND','U10','Q2','D1-K'])]
 disconnected={n:len(net_components[n]) for n in critical if len(net_components[n])!=1}
 assert not disconnected,('Changed/critical power net has multiple copper islands',disconnected)
 report['physical_connectivity']={'all_pad_net_short_check':'passed','critical_net_island_counts':{n:len(net_components[n]) for n in sorted(critical)},'copper_islands':len(islands),'limits':'Net identity from native pads; plated associations from native layer span with all drill centres/sizes matched to Excellon. No impedance, current-temperature, electromagnetic or solder-joint model.'}
 checked_tracks=[]
 for t in facts['tracks']:
  if t['net'] not in critical or t['arc']:continue
  shape=LineString([t['start'],t['end']]).buffer(t['width']/2-.002,cap_style=1)
  assert copper[t['layer']].buffer(.003).covers(shape),('Power track missing/narrowed in exported copper',t)
  checked_tracks.append(t)
 report['power_track_count_checked']=len(checked_tracks)
 report['power_track_min_native_width_mm']=min((t['width'] for t in checked_tracks),default=None)

 # BOM/CPL both parsed afresh, compared with native component position/side.
 bom=list(csv.DictReader((out/'BOM_PCBA_10.csv').open(encoding='utf-8-sig')))
 refs=[]
 for r in bom:
  rr=[s.strip() for s in r['Designators'].split(',')];refs.extend(rr)
  assert len(rr)==int(r['Quantity per board']) and 10*len(rr)==int(r['Quantity for 10 boards'])
 assert len(refs)==len(set(refs)),'Duplicate BOM designator'
 cpl=list(csv.DictReader((out/'CPL_PCBA_10.csv').open(encoding='utf-8-sig')))
 assert set(refs)=={r['Designator'] for r in cpl} and len(cpl)==len(refs),'BOM/CPL coverage mismatch'
 parts={p['ref']:p for p in facts['parts']}
 for r in cpl:
  p=parts[r['Designator']];assert math.dist(p['xy'],[float(r['Mid X']),float(r['Mid Y'])])<.002,('CPL origin/coordinate mismatch',r,p)
  assert p['side']==r['Layer'],('CPL side mismatch',r,p)
  assert abs((float(r['Rotation'])-p['angle']+180)%360-180)<.01,('CPL rotation mismatch',r,p)
 report['assembly_files']={'bom_rows':len(bom),'populated_designators':len(refs),'cpl_origin_side_rotation_check':'passed; native KiCad footprint rotation convention'}
 report['input_sha256']={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(fab.iterdir()) if p.suffix.lower()!='.pdf'}
 report['native_board_sha256']=hashlib.sha256((ROOT/'elec_RPI_Robot_HAT.kicad_pcb').read_bytes()).hexdigest()
 (out/'Independent_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 return report

if __name__=='__main__':
 print(json.dumps(verify_release(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'production'/'M1'),indent=2))
