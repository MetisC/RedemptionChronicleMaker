"""Join the 58 authoring routes to executed tests and real build receipts.

This is an integration index, not a gameplay or line-coverage certificate.
Multiple capabilities intentionally share the same existing implementation.
"""
import ast,collections,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def group(ui,engine,tests):
    return dict(ui=['src/rcm/editor/'+s+'.py' for s in ui.split()],
                implementation=['src/rcm/'+s+'.py' for s in engine.split()],
                test_modules=['test_'+s for s in tests.split()])


GROUPS={
    'placement':group('inspector window viewport','model campaign generator campaign_generator campaign_document','core editor spatial'),
    'templates':group('resource_panel instance_overrides inspector','project_resources instance_overrides formats','strict_authoring strict_editor phase5_resources'),
    'native':group('native_scripts inspector','native_scripts script_parameters native_regions formats campaign','strict_authoring strict_editor authoring_completion'),
    'environment':group('environment inspector','environment_fields scene_profiles formats campaign','strict_authoring strict_editor'),
    'zones':group('zones inspector','scene_zones audio world_effects campaign campaign_document','final_closure authoring_completion director'),
    'arrival':group('inspector campaign_panel','native_arrivals campaign campaign_generator formats','native_arrivals phase9 phase9_gui round0'),
    'interest':group('inspector resource_panel','interest_spots project_resources formats','strict_authoring strict_editor'),
    'movement':group('campaign_panel inspector','campaign campaign_generator dynamic_targets','phase9 phase9_gui authoring_completion'),
    'director':group('director click_actions inspector','cinematics audio world_effects camera_paths campaign_generator','director director_ui director_packages camera_paths'),
    'click':group('click_actions original_objects viewport','click_interactions original_objects campaign campaign_generator','click_interactions original_picking phase9_gui'),
    'libraries':group('content_libraries browser','content_libraries project_resources service packages','content_libraries final_closure'),
    'editor':group('window theme product_ui','app_settings campaign_document safe_edit','usability editor_fixes delete_flow round0'),
    'maps':group('maps campaign_panel','original_maps chronicle_maps campaign campaign_generator campaign_document','authoring_completion original_maps'),
    'dynamic_targets':group('inspector zones click_actions','dynamic_targets campaign campaign_generator dynamic_runtime','authoring_completion final_closure'),
    'inventory':group('inspector click_actions','campaign campaign_generator profile_compatibility','campaign round0 profile_startup lan_startup'),
    'traits':group('wtd inspector click_actions','actor_traits wtd campaign campaign_generator','wtd authoring_completion'),
    'dialogue':group('graph_panel inspector click_actions','campaign campaign_generator generator','dialogue_lifecycle campaign_callbacks round0 director'),
    'notes':group('click_actions inspector recipe_wizard','notes campaign campaign_generator','notes_motion click_interactions'),
    'quests':group('campaign_panel inspector recipe_wizard','campaign campaign_generator campaign_document','campaign campaign_editor campaign_callbacks'),
    'scenes':group('campaign_panel inspector','campaign campaign_generator campaign_document native_arrivals','campaign phase7_scenes round0 phase9'),
    'state':group('inspector graph_panel campaign_panel','campaign campaign_generator campaign_document safe_edit','campaign campaign_callbacks final_closure'),
    'encounters':group('dynamic_wizard campaign_panel inspector','dynamic_encounters dynamic_runtime combat_difficulty campaign','dynamic_encounters dynamic_gui combat_difficulty'),
    'packaging':group('browser package_panel product_ui','catalogue service packages generator content_libraries','core content_libraries shared_content release10'),
}
# Stable row numbers of the existing matrix. No new capability or subsystem.
ROUTES={
    'placement':[1,45], 'templates':[2,4,5,6,7,8,9,38], 'native':[3,21,27,28,29,56],
    'environment':[11,12,14,15,16], 'zones':[13,22,23,24,25,57],
    'arrival':[17,18], 'interest':[19], 'movement':[20,35,46],
    'director':[30,31,32,33,34,36,58], 'click':[26], 'libraries':[37,39],
    'editor':[40], 'maps':[41,42], 'dynamic_targets':[43,44], 'inventory':[47],
    'traits':[48], 'dialogue':[49], 'notes':[50], 'quests':[51], 'scenes':[10,52],
    'state':[53], 'encounters':[54], 'packaging':[55],
}


def main():
    rows=[line.split('|')[1:-1] for line in (ROOT/'docs/EMBRACE_AUTHORING_PARITY.md').read_text(encoding='utf8').splitlines() if line.startswith('| ')][1:]
    if len(rows)!=58:raise ValueError('Expected the existing 58 capabilities')
    owners={i:name for name,indices in ROUTES.items() for i in indices}
    if len(owners)!=sum(map(len,ROUTES.values())) or set(owners)!=set(range(1,59)):raise ValueError('Missing or repeated route')
    report=json.loads((ROOT/'build/tests/test_report.json').read_text())
    quality=json.loads((ROOT/'build/tests/quality_report.json').read_text())
    if not report['successful'] or report['skipped'] or not quality['successful']:raise ValueError('Full gate must pass without skips')
    log=(ROOT/'build/tests/tests.log').read_text(encoding='utf8')
    passed=set(re.findall(r'^(test_\w+) \((test_\w+\.\w+)\) \.\.\. ok$',log,re.M))
    builds=json.loads((ROOT/'research/authoring_completion/builds.json').read_text())
    if len(builds)!=7 or not all(r['successful'] and r['class_versions']==['45.3'] and not r['geometry_included'] for r in builds):raise ValueError('Seven actual Codex builds required')
    groups={}
    for name,route in GROUPS.items():
        files=route['ui']+route['implementation']+['src/rcm/campaign_document.py','src/rcm/service.py']
        for path in files:
            if not (ROOT/path).is_file():raise ValueError('Missing route source: '+path)
        tests=[]
        for module in route['test_modules']:
            tree=ast.parse((ROOT/'tests'/(module+'.py')).read_text(encoding='utf8'))
            for cls in (c for c in tree.body if isinstance(c,ast.ClassDef)):
                for method in (m for m in cls.body if isinstance(m,ast.FunctionDef) and m.name.startswith('test_')):
                    if (method.name,module+'.'+cls.name) not in passed:raise ValueError('Test not passed in full gate: '+module+'.'+method.name)
                    tests.append(module+'.'+cls.name+'.'+method.name)
        groups[name]=dict(**route,passed_tests=tests,save_model='src/rcm/campaign_document.py',real_compilation='src/rcm/service.py',
                          native_acceptance=False)
    result=dict(capabilities=[dict(number=i,name=row[0].strip(),status=row[5].strip(),route=owners[i],
                                  normal_ui=row[4].strip(),native_contract=row[2].strip(),manual_check=row[7].strip()) for i,row in enumerate(rows,1)],
                routes=groups,counts=dict(collections.Counter(r[5].strip() for r in rows)),
                full_gate=report,builds=builds,tests_log_sha256=hashlib.sha256(log.encode()).hexdigest(),
                source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted({p for g in groups.values() for p in g['ui']+g['implementation']})},
                note='Executed integration routes; no assertion of native rendering, audio, network or gameplay acceptance.',native_engine_test=False)
    (ROOT/'research/authoring_completion/final_routes.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(dict(capabilities=58,counts=result['counts'],tests=report['tests'],real_codex_builds=7,native_engine_test=False)))


if __name__=='__main__':main()
