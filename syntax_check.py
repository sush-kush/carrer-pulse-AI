import sys, ast, os
sys.path.insert(0, '.')

# Check home.py syntax
src = open('pages/home.py', encoding='utf-8').read()
try:
    ast.parse(src)
    print('home.py syntax: OK')
except SyntaxError as e:
    print('home.py SYNTAX ERROR:', e)
    sys.exit(1)

# The old bug: {example_chips()} inside a plain """ string (not f-string)
assert '{example_chips()}' not in src, 'OLD BUG STILL PRESENT: unresolved example_chips()'
print('f-string bug fixed: OK')

# chips_html variable exists and is used in an f-string
assert 'chips_html = _example_chips()' in src, 'chips_html assignment missing'
assert '{chips_html}' in src, 'chips_html interpolation missing'
print('chips_html interpolation: OK')

# All pages parse cleanly
pages = ['home','market_pulse','skill_intelligence','salary_lab','role_explorer',
         'my_career','career_simulator','career_path','opportunity_explorer',
         'location_intelligence','company_intelligence','forecast_lab',
         'ai_copilot_page','data_explorer','data_quality','about_dataset']
for p in pages:
    try:
        psrc = open(f'pages/{p}.py', encoding='utf-8').read()
        ast.parse(psrc)
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {p}: {e}')
        sys.exit(1)
print('All 16 pages parse without syntax errors: OK')
print()
print('=== ALL CHECKS PASSED ===')
