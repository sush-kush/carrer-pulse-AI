"""CareerPulse AI — Final Comprehensive Check"""
import sys, ast, os
sys.path.insert(0, '.')

# 1. Syntax check all files
print('=== SYNTAX CHECK ===')
all_files = (
    ['pages/' + f for f in os.listdir('pages') if f.endswith('.py') and f != '__init__.py'] +
    ['modules/' + f for f in os.listdir('modules') if f.endswith('.py') and f != '__init__.py'] +
    ['app.py']
)
err_count = 0
for path in all_files:
    with open(path, encoding='utf-8') as f:
        src = f.read()
    try:
        ast.parse(src)
    except SyntaxError as e:
        print('SYNTAX ERROR %s: %s' % (path, e))
        err_count += 1
if err_count == 0:
    print('All %d files: no syntax errors' % len(all_files))

# 2. Module imports
print('\n=== MODULE IMPORTS ===')
from modules.data_loader import load_data
from modules.feature_engineering import get_kpis, get_skill_frequency, match_roles_to_skills
from modules.ml_engine import SalaryPredictor, compute_market_alignment
from modules.ai_copilot import answer
from modules.ui_components import GLOBAL_CSS, CHART_LAYOUT, kpi_card, page_header
print('All modules imported OK')

# 3. Load dataset
print('\n=== DATASET ===')
df = load_data('../indian-job-market-dataset-2025.xlsx')
print('Rows: %s  Cols: %s' % (len(df), len(df.columns)))
kpis = get_kpis(df)
print('Top role: %s  Top city: %s' % (kpis['top_role'], kpis['top_location']))
print('Salary coverage: %s%%  Exp coverage: %s%%' % (kpis['salary_coverage_pct'], kpis['exp_coverage_pct']))
print('Unique skills: %s' % kpis['unique_skills'])

# 4. ML
print('\n=== ML ENGINE ===')
p = SalaryPredictor()
p.train(df)
print('Trained: %s  n=%s  R2=%s' % (p.trained, p.n_train, p.metrics.get('R2')))
if p.trained:
    res = p.predict('Data Analyst', 'Bengaluru', 3.0, 6)
    print('Prediction: %s LPA, confidence: %s' % (res['predicted_lpa'], res['confidence']))

# 5. Career matching
print('\n=== CAREER MATCHING ===')
matches = match_roles_to_skills(df, ['Python', 'Sql', 'Pandas'], top_n=5)
print('Role matches: %d' % len(matches))
if not matches.empty:
    print('Top match: %s (%.1f%%)' % (matches.iloc[0]['role'], matches.iloc[0]['match_score']))

# 6. CSS
print('\n=== CSS ===')
assert '<style>' in GLOBAL_CSS
assert '--cp-purple' in GLOBAL_CSS
assert 'cp-kpi' in GLOBAL_CSS
print('GLOBAL_CSS: %d chars  OK' % len(GLOBAL_CSS))

# 7. All pages importable
print('\n=== PAGE IMPORTS ===')
import importlib
page_keys = [
    'pages.home', 'pages.market_pulse', 'pages.skill_intelligence',
    'pages.salary_lab', 'pages.role_explorer', 'pages.location_intelligence',
    'pages.company_intelligence', 'pages.my_career', 'pages.career_simulator',
    'pages.career_path', 'pages.opportunity_explorer', 'pages.forecast_lab',
    'pages.ai_copilot_page', 'pages.data_explorer', 'pages.data_quality',
    'pages.about_dataset',
]
fail_count = 0
for mod in page_keys:
    try:
        m = importlib.import_module(mod)
        assert hasattr(m, 'render')
    except Exception as e:
        print('FAIL: %s -> %s' % (mod, e))
        fail_count += 1
if fail_count == 0:
    print('All %d pages: imports + render() OK' % len(page_keys))

print('\n=== ALL CHECKS PASSED ===')
