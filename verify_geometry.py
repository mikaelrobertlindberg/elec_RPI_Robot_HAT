import pcbnew,json,subprocess,shutil
from pathlib import Path
b=pcbnew.LoadBoard('elec_RPI_Robot_HAT.kicad_pcb')
f=next(f for f in b.GetFootprints() if f.GetReference()=='U12')
result={'pads':[]}
for p in f.Pads():
 s=p.GetSize();result['pads'].append({'pin':p.GetNumber(),'size_mm':[s.x/1e6,s.y/1e6],'net':p.GetNetname(),'local_mask_margin_nm':p.GetLocalSolderMaskMargin()})
assert all(min(x['size_mm'])==0.3 for x in result['pads'])
# Deliberately restore one original-width pad: the supplier rule must detect it.
p=next(p for p in f.Pads() if p.GetNumber()=='2');s=p.GetSize();p.SetSize(pcbnew.VECTOR2I(s.x,350000))
pcbnew.SaveBoard('rule-check.kicad_pcb',b)
for suffix in ['.kicad_pro','.kicad_dru']:shutil.copyfile('elec_RPI_Robot_HAT'+suffix,'rule-check'+suffix)
subprocess.run(['C:/Program Files/KiCad/9.0/bin/kicad-cli.exe','pcb','drc','--format','json','-o','rule-check.json','rule-check.kicad_pcb'],check=True)
d=json.loads(Path('rule-check.json').read_text());result['negative_control_clearance_count']=sum(v['type']=='clearance' for v in d['violations'])
assert result['negative_control_clearance_count']>0,'Supplier clearance rule did not detect the deliberately bad pad'
Path('u12-geometry-check.json').write_text(json.dumps(result,indent=2))
