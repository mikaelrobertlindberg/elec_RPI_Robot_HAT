"""M2 narrow ECO: restore the original floating U8 exposed pad."""
from pathlib import Path
import re, shutil, subprocess

ROOT = Path(__file__).resolve().parent

def block(s, start):
    depth = 0
    quoted = escaped = False
    for i in range(start, len(s)):
        c = s[i]
        if escaped:
            escaped = False
            continue
        if c == '\\' and quoted:
            escaped = True
            continue
        if c == '"':
            quoted = not quoted
        if not quoted:
            depth += (c == '(') - (c == ')')
            if depth == 0:
                return s[start:i+1]
    raise ValueError('unbalanced')

def main():
    import pcbnew
    audit = ROOT / '.audit' / 'M2-baseline'
    audit.mkdir(parents=True, exist_ok=True)
    for name in ['elec_RPI_Robot_HAT.kicad_pcb', 'dynamixel.kicad_sch', 'Library_Pollen.kicad_sym']:
        target = audit / name
        assert not target.exists(), 'ECO already applied; inspect instead of rerunning'
        shutil.copyfile(ROOT / name, target)
    for filename, symbol in [('dynamixel.kicad_sch','Library_Pollen:GM3088ENA'),('Library_Pollen.kicad_sym','GM3088ENA')]:
        path = ROOT / filename
        s = path.read_text(encoding='utf-8')
        old = block(s, s.index('(symbol "' + symbol + '"'))
        pins = [block(old,m.start()) for m in re.finditer(r'\(pin [a-z_]+ line',old)]
        ep = [pin for pin in pins if '(number "9"' in pin]
        assert len(ep) == 1 and '(name "EP"' in ep[0]
        s = s.replace(old, old.replace(ep[0], '', 1), 1)
        if filename.endswith('.kicad_sch'):
            start = s.index('(lib_id "Library_Pollen:GM3088ENA")')
            instance_start = s.rfind('(symbol',0,start)
            instance = block(s,instance_start)
            for match in list(re.finditer(r'\(pin "9"',instance)):
                instance = instance.replace(block(instance,match.start()),'')
            original = block(s,instance_start)
            s = s.replace(original,instance,1)
        path.write_text(s,encoding='utf-8')
    board_path = ROOT / 'elec_RPI_Robot_HAT.kicad_pcb'
    board = pcbnew.LoadBoard(str(board_path))
    pad = next(p for f in board.GetFootprints() if f.GetReference()=='U8' for p in f.Pads() if p.GetNumber()=='9')
    assert pad.GetNetname()=='GND'
    board.BuildConnectivity()
    assert len(board.GetConnectivity().GetConnectedTracks(pad))==0
    pad.SetNetCode(0)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path),board)
    print('Only U8 EP symbol pin removed and PCB EP isolated; zones refilled.')

if __name__=='__main__':
    main()
