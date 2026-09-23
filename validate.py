import sys, os
sys.path.insert(0, '.')

print('=== Testing data_loader ===')
from modules import data_loader as dl
import pandas as pd
import numpy as np

df = pd.read_excel(dl.DEFAULT_PATH, sheet_name='Sheet1', engine='openpyxl')
print(f'Raw rows: {len(df)}')

df = dl._validate_columns(df)
df = dl._clean(df)
print(f'After clean: {len(df)} rows, {len(df.columns)} columns')
print(f'skills_list sample: {df["skills_list"].iloc[0]}')
print(f'exp_bucket counts: {df["exp_bucket"].value_counts().head(3).to_dict()}')
print(f'salary_disclosed: {df["salary_disclosed"].sum()}')

qr = dl.get_quality_report(df)
print(f'Quality: {qr}')

print()
print('=== Testing feature_engineering ===')
from modules import feature_engineering as fe

kpis = fe.get_kpis(df)
print(f'KPIs: {kpis}')

skill_freq = fe.get_skill_frequency(df, top_n=5)
print(f'Top 5 skills: {skill_freq.to_dict("records")}')

role_dem = fe.get_role_demand(df, top_n=3)
print(f'Top 3 roles: {role_dem.to_dict("records")}')

loc_dem = fe.get_location_demand(df, top_n=3)
print(f'Top 3 locs: {loc_dem.to_dict("records")}')

sal_dist = fe.get_salary_distribution(df)
print(f'Salary dist: {sal_dist.head(3).to_dict("records")}')

match = fe.match_roles_to_skills(df, ["Python", "SQL", "Pandas"], top_n=3)
print(f'Role match: {match[["role","match_score","postings"]].to_dict("records")}')

gap = fe.compute_skill_gap(df, ["Python", "SQL"], "Data Analyst")
print(f'Skill gap: match_pct={gap.get("match_pct")}, missing={list(gap.get("missing_skills",{}).keys())[:3]}')

sim = fe.simulate_skill_addition(df, ["Python"], ["Power BI"])
print(f'Simulation: score_delta={sim["score_delta"]}, new_roles={sim["new_roles"][:2]}')

print()
print('=== Testing ml_engine ===')
from modules.ml_engine import SalaryPredictor, SkillRecommender, compute_market_alignment, find_opportunities

p = SalaryPredictor()
p.n_train = 0  # just test predict without training
result = p.predict("Data Analyst", "Bengaluru", 3.0, 5)
print(f'Predictor (untrained): {result}')

rec = SkillRecommender()
recs = rec.recommend(df, ["Python"], "Data Analyst", top_n=5)
print(f'Skill recommendations: {recs[:3]}')

alignment = compute_market_alignment(df, ["Python","SQL"], "Data Analyst", 3.0, "Bengaluru")
print(f'Alignment score: {alignment["score"]}')

opps = find_opportunities(df, ["Python","SQL"], "Data Analyst", "Bengaluru", 2.0, top_n=3)
print(f'Opportunities found: {len(opps)}')

print()
print('=== Testing ai_copilot ===')
from modules.ai_copilot import answer, classify_intent

intents_to_test = [
    "What skills are most demanded?",
    "What salary for Data Analyst?",
    "Which roles match Python and SQL?",
    "What if I learn Power BI?",
    "Which cities have the most jobs?",
]
for q in intents_to_test:
    intent = classify_intent(q)
    print(f'Q: "{q}" -> Intent: {intent}')

resp = answer(df, "What skills are most demanded?")
print(f'Copilot response (truncated): {resp[:200]}')

print()
print('=== ALL TESTS PASSED ===')
