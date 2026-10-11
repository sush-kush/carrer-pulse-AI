# CareerPulse AI

> **Understand the Market. Predict Possibilities. Plan Your Career.**

CareerPulse AI is a complete, production-quality AI-powered career intelligence platform built on real Indian job market data. It combines data analytics, machine learning, and an intelligent AI copilot into a single, polished application.

---

## Overview

CareerPulse AI transforms the uploaded `indian-job-market-dataset-2025.xlsx` into actionable career intelligence. Every insight, chart, prediction, and recommendation is derived exclusively from this dataset — no external APIs, no fabricated data, no synthetic records.

---

## 📖 The Story Behind CareerPulse AI

### A Tale of Three People

---

**Meet Priya.**

Priya just finished her B.Tech in Computer Science from a tier-2 college in Pune. She has learned Python, some SQL, and has done a few projects on Kaggle. Placement season is around the corner and everyone around her is panicking.

She opens LinkedIn. Hundreds of job titles stare back at her — Data Analyst, Data Engineer, Business Analyst, ML Engineer, Python Developer. She doesn't know which role fits her. She doesn't know which skills she's missing. She doesn't know what salary to expect. She types into Google: *"What skills do I need for a data analyst job in India 2025?"*

She gets a blog post from 2022.

> *Priya needed answers rooted in what the market actually looks like today — not someone's opinion from three years ago.*

---

**Meet Arjun.**

Arjun is a 4-year-experienced software developer at a mid-size IT firm in Hyderabad. He's good at Java, Spring Boot, and REST APIs. But lately he's been reading about data engineering. He wonders: *"Could I switch to a Data Engineer role? How far am I? What would I need to learn?"*

He browses through job descriptions for an hour. Every posting has a different skill list. Some want Spark, some want Kafka, some want both plus Airflow. He has no way to know which skills are truly common versus which are niche asks from one employer.

> *Arjun needed a systematic way to compare his current profile against the actual patterns across hundreds of real postings — not just one JD.*

---

**Meet Rekha.**

Rekha is a recruiter at a growing Bengaluru startup. She's trying to benchmark a competitive salary for a new Data Science hire. She has no HR analyst. She googles salary surveys — most are global, some are outdated, none show her what companies similar to hers are actually offering in this city at this experience level.

> *Rekha needed a data-grounded salary view specific to her market — not a generic global range.*

---

### The Problem Was Always the Same

Priya, Arjun, and Rekha all had the same core problem: **the job market is opaque.**

There is no shortage of advice. There is a shortage of *evidence*.

- Job seekers make decisions based on anecdotes.
- Career switchers guess instead of measuring skill overlap.
- Freshers memorize roadmaps that may not reflect real hiring patterns.
- Recruiters benchmark salaries with surveys that are months or years old.

The data to answer all of these questions *existed* — hidden inside thousands of real job postings. What was missing was an intelligent layer that could make sense of it.

---

### What CareerPulse AI Does

CareerPulse AI was built to be that intelligent layer.

It takes **97,679 real Indian job postings from 2025** — covering 18,000+ companies, 54,000+ unique roles, 44,000+ skills, and 3,900+ locations — and turns raw records into a living, queryable career intelligence engine.

**For Priya**, it shows exactly which skills appear most often in Data Analyst postings in Pune — derived from real postings, not curated advice. It shows her what she already has, what she's missing, and how her profile scores against the dataset. It even simulates: *"What if I add Power BI? How many more roles does that unlock?"*

**For Arjun**, it maps the skill overlap between Software Developer and Data Engineer postings using a vectorized Jaccard similarity model. It shows him the precise skills that appear in Data Engineer postings that he hasn't listed. It ranks them by frequency — so he knows which skills are truly common across many employers, not just one.

**For Rekha**, it shows the salary distribution for Data Science roles in Bengaluru, derived from disclosed salary data in thousands of postings. It breaks it down by experience level. It shows min, median, mean, and range — all from actual postings, not a survey.

---

### The Design Philosophy

> **Understand → Analyze → Predict → Simulate**

This is not a static dashboard. It is a four-stage career intelligence loop:

1. **Understand** — What does the Indian job market look like right now, according to this dataset?
2. **Analyze** — Deep-dive into roles, skills, salaries, locations, companies, and experience patterns.
3. **Predict** — Use machine learning to estimate salaries, match roles, and recommend skills — with honest confidence scores and model metrics.
4. **Simulate** — Ask "what if?" and see how your career profile changes before you invest a single hour of learning.

---

### One Rule That Never Breaks

Every number you see in CareerPulse AI — every percentage, every salary range, every skill ranking, every match score — is derived from the uploaded dataset.

Not from a blog post. Not from an AI's general knowledge. Not from a curated list. Not from a hard-coded assumption.

If the data supports the answer, CareerPulse AI shows it.
If it doesn't, it says so.

> *"The uploaded dataset does not contain enough information to answer this reliably."*

That honesty is a feature, not a limitation.

---

### From Data to Decisions

Priya uses the Career Simulator. She adds "Power BI" to her skill list. The platform shows her: **+14 new role matches, +2,341 additional relevant postings**. She decides to spend her next three weekends learning Power BI.

Arjun uses the Skill Gap Intelligence page. The top missing skill for Data Engineer roles in his experience bracket is Apache Spark, appearing in 38% of postings. He enrolls in a Spark course that weekend.

Rekha uses the Salary Lab. She filters for Data Science roles in Bengaluru with 3–5 years experience. The observed median is ₹18.4 LPA. She sets her offer range with confidence.

Three people. Three different questions. One dataset. One platform.

> *That is CareerPulse AI.*

---

The platform serves:
- **Students** — Discover what jobs match their skills
- **Freshers** — Understand what skills are commonly required for their target role
- **Career switchers** — Find roles closest to their current skill set
- **Professionals** — Compare their skill profile with real postings
- **Job seekers** — See observed salary ranges for matching roles
- **Recruiters & researchers** — Analyze market trends, locations, companies

---

## Problem Statement

Job seekers and career planners lack visibility into:
- What skills are truly in demand
- What salaries are observed for specific roles
- Which roles match their current skills
- What skills they need to learn to access new roles
- How their profile compares to real job postings

CareerPulse AI addresses these gaps using real dataset analytics and ML.

---

## Dataset

| Property | Value |
|---|---|
| File | `indian-job-market-dataset-2025.xlsx` |
| Sheet | Sheet1 |
| Total Records | 97,679 |
| Columns | 17 original + 13 derived |
| Unique Companies | ~18,623 |
| Unique Job Titles | ~54,097 |
| Unique Locations | ~3,896 |
| Unique Skills | ~44,057 |
| Salary Coverage | ~33.9% disclosed |
| Experience Coverage | ~99.4% |
| Temporal Window | ~10-day relative labels |
| Domain | Indian Job Market 2025 |

---

## Data Cleaning

1. Removed duplicate job IDs (first occurrence kept)
2. Stripped whitespace from all string columns
3. Replaced `"nan"` / `"None"` strings with proper `NaN`
4. Salary = 0 treated as undisclosed (set to `NaN`)
5. Skills parsed from comma-separated `tagsAndSkills` field, title-cased
6. Primary location extracted from multi-city strings (first city before comma)
7. Hybrid/Remote prefixes stripped from location before extraction
8. Experience parsed to numeric `minimumExperience` / `maximumExperience`
9. Role categories assigned via keyword matching on job title
10. Salary outliers >300 LPA excluded from ML salary predictor training only

---

## Feature Engineering

Derived columns added at load time:

| Feature | Description |
|---|---|
| `location_primary` | First city extracted from location field |
| `skills_list` | Parsed list of individual skills per posting |
| `skills_count` | Number of skills per posting |
| `exp_bucket` | Bucketed experience level (e.g. "2–5 Years") |
| `exp_mid` | Midpoint of experience range |
| `salary_mid` | Midpoint of min/max salary (INR) |
| `min_salary_lpa` | Minimum salary in Lakhs per Annum |
| `max_salary_lpa` | Maximum salary in Lakhs per Annum |
| `mid_salary_lpa` | Mid-point salary in LPA |
| `salary_disclosed` | Boolean: True if salary is disclosed |
| `role_category` | Broad category (e.g. "Data & Analytics") |
| `is_recent` | True if posting is within 5 days |

---

## Analytics

All analytics are computed dynamically from the loaded dataset:

- **Market KPIs**: Total postings, companies, roles, locations, skills, salary coverage
- **Role Demand**: Most posted job titles by volume and frequency
- **Skill Demand**: Most frequent skills, skill coverage %, skills by role/location/experience
- **Salary Analytics**: Distribution, mean, median, by role/location/experience
- **Location Analytics**: City-level posting volume, salary, skills, comparison
- **Company Analytics**: Posting volume, roles, locations, ratings, salary per company
- **Experience Analytics**: Distribution across experience buckets
- **Skill Co-occurrence**: Network graph of skills that appear together
- **Role Similarity**: Jaccard overlap between role skill sets

---

## AI Features

### AI Career Copilot
- Rule-based NL query engine
- 11 intent classifiers (regex-based)
- Answers strictly from dataset analytics
- No external LLM API calls
- Handles: skill demand, salary stats, role matching, skill gap, location analysis, company info, what-if scenarios, market overview

### Career Simulator
- Simulates "What if I learn X?" scenarios
- Compares match scores before/after adding skills
- Shows new role matches unlocked
- Displays before/after bar chart comparison

### Skill Gap Intelligence
- Compares user skills vs. observed skills in target role postings
- Ranks missing skills by frequency in dataset
- Shows match percentage against dataset skill patterns

---

## Machine Learning Models

### Salary Predictor
| Property | Value |
|---|---|
| Algorithm | Gradient Boosting Regressor |
| Features | Job Role, Location, Experience (mid), Skills Count |
| Target | Mid-point salary in LPA |
| Train/Test Split | 80/20 |
| Metrics | MAE, RMSE, R² |
| Outlier Filter | Salaries >300 LPA excluded |
| Training Records | ~33,135 disclosed salary observations |
| Note | Predictions are estimates, not compensation guarantees |

### Role Matching (Vectorized Jaccard)
- Computes Jaccard similarity between user skills and each job posting
- Groups by role title, averages scores
- Returns top matching roles with match score, postings count, matched/missing skills
- Fully vectorized — no `.iterrows()` — performant on 97k rows

### Market Alignment Score
- Composite score (0–100): Skill Match (60%) + Location Fit (20%) + Experience Fit (20%)
- Vectorized computation using list comprehension over skills column
- Used in: My Career, Career Simulator

### Role Similarity Matrix
- Jaccard similarity over top N roles
- Based on top 20 skills per role
- Used in: Career Path Explorer

---

## Career Matching

### Career Role Matcher
Users enter skills → system finds matching roles with:
- Jaccard match score per role
- Number of relevant postings
- Skills already matched
- Top missing frequently observed skills
- Average observed salary

### Skill Gap Analysis
Users enter skills + target role → system shows:
- Skills present in role postings that user has
- Skills present in role postings that user lacks (ranked by frequency)
- Skill coverage percentage

---

## Skill Intelligence

- **Global Demand**: Top N skills by posting frequency
- **By Role**: Skills breakdown for any selected job title
- **By Location**: Skills breakdown for any selected city
- **By Experience**: Skills breakdown per experience bucket
- **Co-occurrence Network**: NetworkX + Plotly graph of skill pairs that appear together in postings

---

## Career Simulator

Signature feature — "What if I add Power BI to my skills?"

1. User enters current skills
2. User enters skills they want to add
3. System computes match scores before and after
4. Displays: score change, new roles unlocked, before/after bar chart

All framed as dataset-based scenario analysis, not hiring guarantees.

---

## Forecasting

The dataset uses relative time labels (~10-day window), not calendar dates. Forecast Lab:
- Plots posting activity trend over the ~10-day window
- Applies linear extrapolation (illustrative only)
- Clearly communicates limitation: not suitable for long-term forecasting
- Shows skill and role demand trends within the window

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| UI Framework | Streamlit 1.60+ |
| Data Processing | Pandas 2+, NumPy 2+ |
| Machine Learning | Scikit-learn 1.3+ |
| Visualization | Plotly 5+ |
| Graph/Network | NetworkX 3+ |
| Excel Reading | openpyxl 3+ |
| Design System | Custom CSS (Inter + Plus Jakarta Sans) |

---

## Architecture

```
indian-job-market-dataset-2025.xlsx
            │
            ▼
    data_loader.py
    (load, validate, clean, derive features)
            │
            ▼
    feature_engineering.py
    (KPIs, skill/role/salary/location/company analytics)
            │
    ┌───────┼───────────────┐
    ▼       ▼               ▼
ml_engine  ai_copilot    ui_components
(ML models)(NL Q&A)      (CSS design system)
    │       │               │
    └───────┼───────────────┘
            ▼
        app.py
    (routing, sidebar navigation)
            │
        pages/
    (16 page modules, each with render(df))
```

---

## Installation

```bash
# 1. Clone or download project
cd careerpulse

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place dataset file
# Ensure indian-job-market-dataset-2025.xlsx is one level up from careerpulse/
# i.e. at the same level as the careerpulse/ folder

# 4. Run the application
streamlit run app.py
```

---

## Usage

1. Navigate to `http://localhost:8501`
2. The app loads and caches the dataset on first run (~10-15 seconds)
3. Use the sidebar to navigate between modules:
   - **Home** — Market snapshot and feature overview
   - **Market Pulse** — KPI dashboard with global filters
   - **Skill Intelligence** — Skill demand, network, co-occurrence
   - **Role Explorer** — Deep-dive into any job role
   - **Career Path** — Skill-overlap role transitions
   - **Career Simulator** — "What if I learn X?"
   - **My Career** — Personalized market alignment
   - **Opportunity Explorer** — Find matching postings
   - **Company Intelligence** — Company profiles
   - **Location Intelligence** — City-level analytics
   - **Salary Lab** — Salary analytics + ML predictor
   - **Forecast Lab** — Posting activity trends
   - **Data Explorer** — Search and filter dataset
   - **AI Career Copilot** — Natural language Q&A
   - **Data Quality** — Missing values, coverage stats
   - **About Dataset** — Transparency and limitations

---

## Limitations

1. **Salary coverage**: Only ~34% of postings disclose salary. Salary analytics cover disclosed postings only.
2. **Temporal data**: "jobUploaded" uses relative labels (~10-day window). Long-term trend forecasting is not reliable.
3. **Location parsing**: Multi-city postings reduced to primary city — some nuance is lost.
4. **Skill normalization**: Skills are title-cased; minor spelling variants may appear as separate skills.
5. **ML predictions**: All predictions are estimates from dataset patterns — not hiring guarantees.
6. **Dataset snapshot**: Represents a point-in-time snapshot, not the full live Indian job market.
7. **Salary predictor R²**: ~0.43 — predictions are directional, not precise. Confidence level displayed.

---

## Future Improvements

- Resume text parsing for automatic skill extraction
- Multi-dataset support (multiple time windows for trend analysis)
- Transformer-based skill extraction from job descriptions
- Integration with live job APIs for real-time data
- User account system for persistent career profiles
- Salary negotiation benchmarking feature
- Enhanced NL understanding with open-source LLM integration
- Mobile-optimized layout improvements

---

## Disclaimer

All predictions, match scores, salary estimates, and skill recommendations are derived from patterns in the uploaded dataset. They are statistical estimates and should not be interpreted as:
- Guaranteed future employment outcomes
- Guaranteed compensation figures
- Career advice from qualified professionals

CareerPulse AI uses **indian-job-market-dataset-2025.xlsx** as its sole data source.
No external job-market APIs, fabricated data, or synthetic records are used anywhere in this application.
