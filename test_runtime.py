"""CareerPulse AI — Runtime Integration Test"""
import sys
sys.path.insert(0, '.')

from modules.data_loader import load_data
df = load_data('../indian-job-market-dataset-2025.xlsx')
print(f'Dataset loaded: {len(df)} rows, {len(df.columns)} cols')

from modules.feature_engineering import (
    get_kpis, get_role_demand, get_location_demand,
    get_skill_frequency, get_salary_distribution,
    get_skills_by_role, get_skill_cooccurrence,
    get_salary_by_exp, get_exp_distribution,
    get_company_stats, get_role_salary_stats,
    get_related_roles, match_roles_to_skills,
    compute_skill_gap, simulate_skill_addition,
    get_role_category_demand, get_location_salary_stats,
)

kpis = get_kpis(df)
assert kpis['total_postings'] > 90000, "KPI total_postings wrong"
print(f'KPIs OK: {kpis["total_postings"]:,} postings')

roles = get_role_demand(df, 5)
assert len(roles) == 5
print(f'Role demand OK: {roles["role"].tolist()}')

skills = get_skill_frequency(df, 10)
assert len(skills) == 10
print(f'Skill freq OK: {skills["skill"].tolist()}')

sal = get_salary_distribution(df)
assert len(sal) > 0
print(f'Salary dist OK: {len(sal)} buckets')

from modules.ml_engine import SalaryPredictor, compute_market_alignment, find_opportunities
p = SalaryPredictor()
p.train(df)
print(f'Salary predictor: trained={p.trained}, n_train={p.n_train}')
if p.trained:
    print(f'  metrics={p.metrics}')
    res = p.predict('Data Analyst', 'Bengaluru', 3.0, 6)
    assert 'predicted_lpa' in res
    print(f'  prediction={res["predicted_lpa"]} LPA, confidence={res["confidence"]}')

user_skills = ['Python', 'Sql', 'Pandas']
al = compute_market_alignment(df, user_skills, 'Data Analyst', 2.0, 'Bengaluru')
score = al['score']
print(f'Alignment score: {score}%')

opps = find_opportunities(df, user_skills, 'Data Analyst', 'Bengaluru', 2.0, top_n=5)
print(f'Opportunities: {len(opps)} results')

from modules.ai_copilot import answer
tests = [
    ('What skills are most demanded?', 'skill_demand'),
    ('Which roles match Python and SQL?', 'role_match'),
    ('What salary is observed for Data Analyst?', 'salary_stats'),
    ('Show me the job market overview', 'general_market'),
    ('Compare Data Analyst vs Business Analyst', 'compare_roles'),
    ('What if I learn Power BI?', 'what_if'),
]
for q, label in tests:
    r = answer(df, q)
    assert len(r) > 50, f"Answer too short for {label}"
    print(f'AI Copilot [{label}]: OK ({len(r)} chars)')

print('\nALL RUNTIME TESTS PASSED')
