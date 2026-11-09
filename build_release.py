"""Build a traceable PCBA package from one verified native revision.

Run with standard Python3; requires KiCad9 CLI. Refuses nonzero checks.
"""
from pathlib import Path
import subprocess,json,csv,hashlib,zipfile,re,xml.etree.ElementTree as ET,shutil,sys
ROOT=Path(__file__).resolve().parent
CLI='C:/Program Files/KiCad/9.0/bin/kicad-cli.exe'
OUT=ROOT/'production'/'M1';OUT.mkdir(parents=True,exist_ok=True)
AUDIT=ROOT/'.audit';AUDIT.mkdir(exist_ok=True)
FAB=OUT/'fabrication';FAB.mkdir(exist_ok=True)
BOARD='elec_RPI_Robot_HAT.kicad_pcb';SCH='elec_RPI_Robot_HAT.kicad_sch'
def run(*args):subprocess.run([CLI,*map(str,args)],cwd=ROOT,check=True)
def export_checks():
 run('pcb','drc','--format','json','--severity-all','--schematic-parity','-o',OUT/'DRC.json',BOARD)
 run('sch','erc','--format','json','--severity-all','-o',OUT/'ERC.json',SCH)
def export_manufacturing():
 run('sch','export','netlist','--format','kicadxml','-o',OUT/'netlist.xml',SCH)
 run('pcb','export','gerbers','--layers','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts','--subtract-soldermask','--use-drill-file-origin','-o',str(FAB)+'/',BOARD)
 run('pcb','export','drill','--format','excellon','--drill-origin','plot','--excellon-separate-th','--generate-map','--map-format','pdf','-o',str(FAB)+'/',BOARD)
 run('pcb','export','gerbers','--layers','F.Paste,B.Paste','--use-drill-file-origin','-o',str(OUT/'stencil')+'/',BOARD)
 run('pcb','export','pos','--format','csv','--units','mm','--side','both','--use-drill-file-origin','--exclude-dnp','-o',AUDIT/'KiCad_positions_raw.csv',BOARD)
 run('sch','export','pdf','-o',OUT/'Robot_HAT_M1_schematic.pdf',SCH)
def export_assembly():
 plot_board=AUDIT/'Assembly_plot.kicad_pcb'
 subprocess.run(['C:/Program Files/KiCad/9.0/bin/python.exe',str(ROOT/'verify_release.py'),'--assembly-board',str(plot_board)],cwd=ROOT,check=True)
 for side,layers in [('top','F.Fab,F.SilkS,Edge.Cuts'),('bottom','B.Fab,B.SilkS,Edge.Cuts')]:
  extra=['--mirror'] if side=='bottom' else []
  run('pcb','export','svg','--layers',layers,'--sketch-pads-on-fab-layers','--crossout-DNP-footprints-on-fab-layers','--exclude-drawing-sheet','--fit-page-to-board','--black-and-white',*extra,'--page-size-mode','2','--mode-single','-o',OUT/f'Assembly_{side}.svg',plot_board)
# Keep vector artwork; render an enlarged, readable A4 landscape assembly sheet.
# Run the PDF skill's operation marker before full or --assembly-only builds.
def render_assembly():
 import fitz
 for side in ['top','bottom']:
  svg=fitz.open(stream=(OUT/f'Assembly_{side}.svg').read_bytes(),filetype='svg')
  vector=fitz.open(stream=svg.convert_to_pdf(),filetype='pdf')
  pdf=fitz.open();page=pdf.new_page(width=842,height=595)
  page.insert_text((36,35),f'Robot HAT D1-M1 - {side} assembly',fontsize=16)
  page.insert_text((36,52),'Bottom view is mirrored. DNP parts are crossed out. Use BOM/CPL as the population authority.',fontsize=9)
  # KiCad can retain a large SVG canvas even with fit-page flags. Fit the
  # actual vector artwork, never a screenshot or assumed board dimensions.
  clip=fitz.Rect()
  for drawing in vector[0].get_drawings():clip.include_rect(drawing['rect'])
  for block in vector[0].get_text('blocks'):clip.include_rect(fitz.Rect(block[:4]))
  assert not clip.is_empty and not clip.is_infinite,'Empty assembly SVG artwork'
  clip=(clip+(-4,-4,4,4)) & vector[0].rect
  page.show_pdf_page(fitz.Rect(36,65,806,559),vector,0,keep_proportion=True,clip=clip)
  pdf.save(OUT/f'Robot_HAT_M1_assembly_{side}.pdf')
  pdf.close();vector.close();svg.close()
if '--assembly-only' in sys.argv:
 export_assembly();render_assembly();sys.exit()
if '--package-only' not in sys.argv:
 subprocess.run([sys.executable,str(ROOT/'verify_connectivity.py')],cwd=ROOT,check=True)
 subprocess.run(['C:/Program Files/KiCad/9.0/bin/python.exe',str(ROOT/'verify_geometry.py')],cwd=ROOT,check=True)
 export_checks()
d=json.loads((OUT/'DRC.json').read_text(encoding='utf-8'))
assert all(not d[k] for k in ['violations','unconnected_items','schematic_parity']),'DRC/parity not clear'
d=json.loads((OUT/'ERC.json').read_text(encoding='utf-8'))
assert all(not s['violations'] for s in d['sheets']),'ERC not clear'
if '--package-only' not in sys.argv:
 export_manufacturing();export_assembly();render_assembly()
parts=json.loads((ROOT/'approved_parts.json').read_text(encoding='utf-8'))
source=list(csv.DictReader((ROOT/'sourcing.csv').open(encoding='utf-8-sig',newline='')))
assert len(source)==44,f'Expected 44 dated sourcing rows, found {len(source)}'
src={ref.strip():r for r in source for ref in r['references'].split(',')}
net=ET.parse(OUT/'netlist.xml').getroot();comps={c.attrib['ref']:c for c in net.findall('./components/comp')}
mounted={ref for ref,v in parts.items() if v['mpn'] and ref in comps}
assert all(comps[ref].find("./property[@name='dnp']") is None for ref in mounted),'Mounted BOM contains a schematic DNP component'
assert mounted==set(src),f'Sourcing mismatch {mounted.symmetric_difference(src)}'
assert all(r['sufficient_stock']=='True' for r in source)
groups={}
for ref in sorted(mounted,key=lambda x:(re.sub(r'\d','',x),int(re.search(r'\d+',x)[0]))):
 v=parts[ref];c=comps[ref];mpn=c.findtext("./fields/field[@name='Man. Ref.']")
 assert mpn==v['mpn']==src[ref]['mpn'],(ref,mpn,v['mpn'],src[ref]['mpn'])
 key=v['mpn'];g=groups.setdefault(key,dict(refs=[],part=v,source=src[ref],footprints=set(),values=set()))
 g['refs'].append(ref);g['footprints'].add(c.findtext('footprint'));g['values'].add(c.findtext('value'))
rows=[]
for i,(mpn,g) in enumerate(groups.items(),1):
 rows.append({'Item':i,'Designators':', '.join(g['refs']),'Quantity per board':len(g['refs']),'Quantity for 10 boards':10*len(g['refs']),'Manufacturer':g['part']['manufacturer'],'Manufacturer Part Number':mpn,'Value':' / '.join(sorted(g['values'])),'Footprint':' / '.join(sorted(g['footprints'])),'LCSC Part Number':g['part']['lcsc'],'Source':g['source']['selected_supplier'],'Source URL':g['source']['source_url'],'Stock checked':g['source']['checked_date'],'Observed stock':g['source']['observed_stock'],'Populate':'YES'})
def writecsv(path,rows,fields=None):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
writecsv(OUT/'BOM_PCBA_10.csv',rows)
positions=list(csv.DictReader((AUDIT/'KiCad_positions_raw.csv').open(encoding='utf-8-sig',newline='')))
selected=[r for r in positions if r['Ref'] in mounted]
assert {r['Ref'] for r in selected}==mounted,'Placement coverage incomplete'
assert len(selected)==len(mounted),'Duplicate placement reference'
standard=[{'Designator':r['Ref'],'Mid X':r['PosX'],'Mid Y':r['PosY'],'Layer':{'top':'Top','bottom':'Bottom'}[r['Side']],'Rotation':r['Rot']} for r in selected]
writecsv(OUT/'CPL_PCBA_10.csv',standard)
other=[{'Designator':ref,'Value':c.findtext('value'),'Populate':'NO','Reason':'DNP or non-component artwork/fiducial/mechanical item'} for ref,c in comps.items() if ref not in mounted]
writecsv(OUT/'Do_not_populate.csv',other)
shutil.copyfile(ROOT/'sourcing.csv',OUT/'Sourcing_2026-11-09.csv')
shutil.copyfile(ROOT/'ORDERING.md',OUT/'READ_ME_FIRST.txt')
docs=OUT/'docs';docs.mkdir(exist_ok=True)
for name in ['QUALIFICATION.md','ORDERING.md','CIRCUIT_REVIEW.md','circuit_review.md','COMPONENT_REVIEW.md','POWER_POST_REVIEW.md','C39_QUALIFICATION.md','PINOUT_REVIEW.md','D5_ROUTING_REVIEW.md','ROUTING_REPAIR.md']:
 if (ROOT/name).exists():shutil.copyfile(ROOT/name,docs/name)
for name in ['u12-geometry-check.json','physical_connectivity.json','native-connectivity.json','connectivity-report.json']:
 if (ROOT/name).exists():shutil.copyfile(ROOT/name,docs/name)
native_report=json.loads((AUDIT/'native-connectivity.json').read_text(encoding='utf-8'))
assert native_report.get('pass') is True,'Independent native connectivity not clear'
assert native_report['board_sha256']==hashlib.sha256((ROOT/BOARD).read_bytes()).hexdigest(),'Independent native connectivity report is stale'
shutil.copyfile(AUDIT/'native-connectivity.json',OUT/'Native_connectivity.json')
# These checks interpret the exported manufacturing data independently of KiCad.
from verify_release import verify_release
verify_release(OUT)
with zipfile.ZipFile(OUT/'Robot_HAT_M1_Gerber.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(FAB.iterdir()):
  if p.suffix.lower()!='.pdf':z.write(p,p.name)
manifest={'revision':'D1-M1','quantity_boards':10,'populated_parts_per_board':len(mounted),'bom_rows':len(rows),'source_hash_convention':'Text sources normalized CRLF to LF for Git portability; exported files hashed byte-for-byte. Native_connectivity.json separately binds raw board bytes.','source_sha256':{},'files':{}}
source_paths=[ROOT/BOARD,ROOT/SCH,*ROOT.glob('*.kicad_sch'),ROOT/'elec_RPI_Robot_HAT.kicad_pro',ROOT/'elec_RPI_Robot_HAT.kicad_dru',
 ROOT/'approved_parts.json',ROOT/'sourcing.csv',ROOT/'fp-lib-table',ROOT/'sym-lib-table',ROOT/'Library_Pollen.kicad_sym',
 ROOT/'ORDERING.md',ROOT/'QUALIFICATION.md',ROOT/'build_release.py',ROOT/'verify_release.py',ROOT/'verify_connectivity.py',ROOT/'verify_geometry.py',
 *ROOT.glob('RobotHAT.pretty/*.kicad_mod')]
for p in source_paths:
 if p.exists():manifest['source_sha256'][p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
for p in sorted(OUT.rglob('*')):
 if p.is_file() and p.name not in ['manifest.json','Robot_HAT_M1_PCBA_10.zip']:
  manifest['files'][p.relative_to(OUT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(OUT/'Robot_HAT_M1_PCBA_10.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file() and p.name!='Robot_HAT_M1_PCBA_10.zip':z.write(p,p.relative_to(OUT))
print(json.dumps({'mounted':len(mounted),'bom_rows':len(rows),'zip':str(OUT/'Robot_HAT_M1_PCBA_10.zip')}))
