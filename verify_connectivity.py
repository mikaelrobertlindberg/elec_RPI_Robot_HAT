"""Read-only geometric copper connectivity check, independent of KiCad DRC.

Run with ordinary Python (Shapely installed). A KiCad-Python subprocess exports
native pad/track/via polygons and SAVED filled-zone polygons. GEOS unions those
polygons per net/layer and joins layers only through plated pads and vias.
No native connectivity graph or DRC result is consulted. No board is written.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from collections import defaultdict
from pathlib import Path

DEFAULT_KICAD = 'C:/Program Files/KiCad/9.0/bin/python.exe'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def native_export(board_path):
    import pcbnew
    before = sha(board_path)
    board = pcbnew.LoadBoard(str(Path(board_path).resolve()))
    layers = list(board.GetEnabledLayers().CuStack())
    def chain_points(chain):
        return [[chain.CPoint(i).x / 1e6, chain.CPoint(i).y / 1e6]
                for i in range(chain.PointCount())]
    def polygons(polyset):
        return [{'outer': chain_points(polyset.COutline(i)),
                 'holes': [chain_points(polyset.CHole(i, h))
                           for h in range(polyset.HoleCount(i))]}
                for i in range(polyset.OutlineCount())]
    def shape(item, layer):
        polyset = pcbnew.SHAPE_POLY_SET()
        item.TransformShapeToPolygon(polyset, layer, 0, 1000,
                                     pcbnew.ERROR_INSIDE)
        return polygons(polyset)
    data = {'board_sha256': before, 'layers': {str(x): board.GetLayerName(x)
             for x in layers}, 'shapes': [], 'pads': [], 'bridges': [], 'holes': []}
    def add(item, kind, identifier, plated=False):
        net = item.GetNetname()
        active = [layer for layer in layers if item.IsOnLayer(layer)]
        pad_shapes = {}
        for layer in active:
            p = shape(item, layer)
            if p:
                record = {'id': identifier, 'kind': kind, 'net': net,
                          'layer': layer, 'polygons': p}
                data['shapes'].append(record)
                pad_shapes[str(layer)] = p
        if kind == 'pad' and net:
            data['pads'].append({'id': identifier, 'net': net,
                                 'layers': pad_shapes})
        if plated and net:
            data['bridges'].append({'id': identifier, 'net': net,
                                    'layers': pad_shapes})
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            identifier = footprint.GetReference() + '.' + pad.GetNumber() + ':' + str(pad.m_Uuid)
            add(pad, 'pad', identifier, pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH)
            hole = pcbnew.SHAPE_POLY_SET()
            if pad.TransformHoleToPolygon(hole, 0, 1000, pcbnew.ERROR_OUTSIDE):
                data['holes'].append({'layers': layers, 'polygons': polygons(hole)})
    for track in board.GetTracks():
        is_via = track.GetClass() == 'PCB_VIA'
        identifier = str(track.m_Uuid)
        add(track, 'via' if is_via else 'track', identifier, is_via)
        if is_via:
            pos = track.GetPosition()
            data['holes'].append({'layers': [layer for layer in layers if track.IsOnLayer(layer)],
                                  'circle': [pos.x / 1e6, pos.y / 1e6,
                                             track.GetDrillValue() / 2e6]})
    for index, zone in enumerate(board.Zones()):
        if zone.GetIsRuleArea():
            continue
        for layer in layers:
            if zone.IsOnLayer(layer) and zone.HasFilledPolysForLayer(layer):
                p = polygons(zone.GetFilledPolysList(layer))
                if p:
                    data['shapes'].append({'id': 'zone:' + str(index), 'kind': 'zone',
                       'net': zone.GetNetname(), 'layer': layer, 'polygons': p})
    after = sha(board_path)
    if before != after:
        raise RuntimeError('Board changed while native geometry was being exported')
    print(json.dumps(data, separators=(',', ':')))

def analyse(data):
    import shapely
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    from shapely.strtree import STRtree
    from shapely.validation import explain_validity
    invalid = []
    def geometry(polys, identifier):
        converted = []
        for p in polys:
            if len(p['outer']) < 3:
                continue
            g = Polygon(p['outer'], [h for h in p['holes'] if len(h) >= 3])
            if not g.is_valid:
                before_area = g.area
                reason = explain_validity(g)
                g = shapely.make_valid(g)
                invalid.append({'id': identifier, 'reason': reason,
                                'area_change_mm2': abs(g.area - before_area),
                                'valid_after': bool(g.is_valid)})
            converted.append(g)
        return unary_union(converted)
    cuts = defaultdict(list)
    for h in data['holes']:
        g = Point(h['circle'][:2]).buffer(h['circle'][2], quad_segs=64) if 'circle' in h else geometry(h['polygons'], 'drill')
        for layer in h['layers']:
            cuts[layer].append(g)
    cuts = {layer: unary_union(gs) for layer, gs in cuts.items()}
    grouped = defaultdict(list)
    for item in data['shapes']:
        if not item['net']:
            continue
        g = geometry(item['polygons'], item['id'])
        if item['layer'] in cuts:
            g = g.difference(cuts[item['layer']])
        grouped[(item['net'], item['layer'])].append(g)
    components = []
    lookup = defaultdict(list)
    unions = {}
    def polygons_only(g):
        if g.geom_type == 'Polygon':
            yield g
        elif hasattr(g, 'geoms'):
            for item in g.geoms:
                yield from polygons_only(item)
    for key, gs in grouped.items():
        combined = unary_union(gs)
        unions[key] = combined
        for g in polygons_only(combined):
            if g.area > 1e-12:
                index = len(components)
                components.append(g)
                lookup[key].append(index)
    parent = list(range(len(components)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def join(ids):
        if ids:
            first = find(ids[0])
            for i in ids[1:]:
                parent[find(i)] = first
    def memberships(record):
        ids = []
        for layer, polys in record['layers'].items():
            layer = int(layer)
            g = geometry(polys, record['id'])
            if layer in cuts:
                g = g.difference(cuts[layer])
            ids.extend(i for i in lookup[(record['net'], layer)]
                       if g.intersects(components[i]) and g.intersection(components[i]).area > 1e-12)
        return sorted(set(ids))
    for bridge in data['bridges']:
        join(memberships(bridge))
    net_pads = defaultdict(list)
    unrepresented = []
    for pad in data['pads']:
        if pad['net'].startswith('unconnected-'):
            continue
        ids = memberships(pad)
        if not ids:
            unrepresented.append(pad['id'])
        net_pads[pad['net']].append({'pad': pad['id'],
                                    'components': sorted(set(find(i) for i in ids))})
    failures = []
    summary = {}
    for net, pads in net_pads.items():
        groups = sorted(set(i for p in pads for i in p['components']))
        if len(pads) > 1 and len(groups) != 1:
            failures.append({'net': net, 'physical_components': groups, 'pads': pads})
        summary[net] = {'pad_count': len(pads), 'physical_component_count': len(groups)}
    shorts = []
    for layer in sorted({layer for net, layer in unions}):
        keys = [key for key in unions if key[1] == layer]
        gs = [unions[key] for key in keys]
        tree = STRtree(gs)
        for i, g in enumerate(gs):
            for j in tree.query(g, predicate='intersects'):
                j = int(j)
                if j > i:
                    shorts.append({'layer': data['layers'][str(layer)],
                                   'nets': [keys[i][0], keys[j][0]],
                                   'intersection_area_mm2': g.intersection(gs[j]).area})
    return {'method': 'Native copper polygons + saved zone fills; independent Shapely/GEOS union and plated-barrel graph',
            'board_sha256': data['board_sha256'], 'polygon_approximation_nm': 1000,
            'shapely_version': shapely.__version__, 'copper_shape_count': len(data['shapes']),
            'plated_bridge_count': len(data['bridges']), 'pad_count': len(data['pads']),
            # KiCad filled zones may encode a weakly-simple boundary with
            # zero-width bridges. GEOS normalization is accepted only when it
            # yields valid geometry without changing copper area.
            'invalid_polygon_repairs': invalid,
            'unrepresented_pads': unrepresented, 'disconnected_nets': failures,
            'cross_net_copper_intersections': shorts, 'nets': summary,
            'pass': not (unrepresented or failures or shorts or any(
                not x['valid_after'] or x['area_change_mm2'] > 1e-10 for x in invalid)),
            'limits': 'Checks saved copper geometry only; does not prove fabrication, plating integrity, thermal/current capability, RF return quality or measured function.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('board', nargs='?', default='elec_RPI_Robot_HAT.kicad_pcb')
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--kicad-python', default=DEFAULT_KICAD)
    parser.add_argument('--output', default='.audit/native-connectivity.json')
    args = parser.parse_args()
    if args.export:
        native_export(args.board)
        return
    proc = subprocess.run([args.kicad_python, str(Path(__file__).resolve()),
                           '--export', str(Path(args.board).resolve())],
                          capture_output=True, text=True, encoding='utf-8', check=True)
    data = json.loads(proc.stdout)
    report = analyse(data)
    # Exercise the independent graph on an actual changed net: opening its
    # trace must disconnect its pads, while copper from another net laid over
    # one of its pads must be detected as a short. These alter only in-memory
    # exported geometry, never the native board.
    import copy
    target = next(p['net'] for p in data['pads'] if 'VCAP' in p['net'])
    subset = {**data, 'shapes': [x for x in data['shapes'] if x['net'] == target],
              'pads': [x for x in data['pads'] if x['net'] == target],
              'bridges': [x for x in data['bridges'] if x['net'] == target]}
    control_baseline = analyse(subset)
    opened = {**subset, 'shapes': [x for x in subset['shapes'] if x['kind'] != 'track']}
    open_result = analyse(opened)
    shorted = copy.deepcopy(subset)
    extra = copy.deepcopy(next(x for x in shorted['shapes'] if x['kind'] == 'pad'))
    extra['net'] = '__DELIBERATE_SHORT_CONTROL__'
    shorted['shapes'].append(extra)
    short_result = analyse(shorted)
    controls = {'target_net': target, 'unchanged_subset_pass': control_baseline['pass'],
                'deliberate_open_detected': bool(open_result['disconnected_nets']),
                'deliberate_short_detected': bool(short_result['cross_net_copper_intersections'])}
    report['negative_controls'] = controls
    report['pass'] = report['pass'] and all(controls[k] for k in (
        'unchanged_subset_pass', 'deliberate_open_detected', 'deliberate_short_detected'))
    if sha(args.board) != report['board_sha256']:
        raise RuntimeError('Board changed during analysis; rerun against stable saved board')
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['pass', 'board_sha256',
           'copper_shape_count', 'pad_count']}))
    if not report['pass']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
