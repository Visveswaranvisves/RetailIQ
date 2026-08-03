# \# RetailIQ — Causal Marketing Impact \& CLV Intelligence System

# 

# \## Business Question

# Retailers spend heavily on discounts and free shipping to retain customers, but rarely

# know whether those perks \*cause\* repeat purchases or just correlate with customers who

# would have returned anyway. This project builds an end-to-end analytics system to:

# 

# 1\. Identify the most valuable customers (RFM segmentation, CLV prediction)

# 2\. Predict who's likely to churn

# 3\. Measure the \*causal\* effect of discounts/free shipping on repeat purchases

# 4\. Audit whether the models treat customers fairly across regions and price tiers

# 5\. Package findings into a business-facing dashboard and an ROI calculator

# 

# \## Dataset

# \[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

# — \~99,000 real orders across 8 relational tables (orders, payments, reviews, customers,

# products, sellers, order items, geolocation).

# 

# \## Tech Stack

# \- \*\*SQL\*\* (SQLite) — data modeling, RFM segmentation, cohort retention, window functions

# \- \*\*Python\*\* (pandas, scikit-learn, XGBoost, SHAP) — cleaning, EDA, CLV/churn models

# \- \*\*DoWhy / EconML\*\* — causal uplift modeling

# \- \*\*Power BI\*\* — executive dashboard

# \- \*\*Excel\*\* — ROI / what-if calculator

# 

# \## Repo Structure

## Week 1 Findings (Data Foundation)
- [X] unique customers, [X] delivered orders analyzed
- Repeat purchase rate: [X]% -- most customers are one-time buyers, which is the
  commercial motivation for this project: understanding what drives the small
  segment that does return.
- Cohort retention drops sharply after month 0 and stays low -- see `cohort_retention` table.
- Late deliveries show a meaningfully lower average review score than on-time
  deliveries ([X] vs [X]) -- delivery performance is a likely confounder for the
  causal model in Week 2.
- Order volume is heavily concentrated in São Paulo (SP) -- flagged for the
  fairness audit in Week 2.

## How to Run
```bash
python -m venv venv
venv\Scripts\Activate.ps1          # source venv/bin/activate on Mac/Linux
pip install pandas sqlalchemy jupyter matplotlib

python notebooks/00_load_data.py
python notebooks/03_clean_data.py
python notebooks/04_run_rfm.py
python notebooks/05_run_cohort.py
python notebooks/06_run_repeat_interval.py
python notebooks/07_run_delivery_review.py
python notebooks/08_validate_sql_outputs.py
```

## Status
🚧 In progress — Week 1 complete (data foundation, SQL layer, EDA).
Week 2: CLV/churn modeling, causal uplift, fairness audit.

## Status
🚧 In progress — Week 2 complete (CLV/churn models, causal uplift analysis,
fairness audit). See `docs/model_results_summary.md` for full results.
Week 3: Power BI dashboard + Excel ROI calculator.

## Power BI Dashboard
An interactive 4-page dashboard built on the SQL/Python outputs:

- **Overview** — headline metrics (total customers, revenue, churn rate, causal
  voucher effect)
- **Retention & Segments** — cohort retention heatmap, RFM customer segments
- **Seller Performance** — top sellers by revenue, revenue-vs-quality scatter
- **Geographic Overview** — state-level revenue distribution

![Dashboard Overview](docs/screenshots/overview.png)
![Retention Heatmap](docs/screenshots/retention_segments.png)
![Seller Performance](docs/screenshots/seller_performance.png)
![Geographic Overview](docs/screenshots/geographic.png)

File: `powerbi/RetailIQ_Dashboard.pbix`

## Excel ROI Calculator
A scenario-driven what-if tool translating the causal churn-reduction estimate
into a business ROI projection. Includes a Conservative/Moderate/Aggressive
scenario dropdown and a sensitivity table on repeat-purchase assumptions.

![Excel ROI Summary](docs/screenshots/excel_roi_summary.png)

At 30% voucher adoption (Moderate scenario), the model projects a net positive
ROI of approximately [your actual number] BRL, driven by the measured 17.48
percentage-point causal reduction in churn from voucher usage.

File: `excel/RetailIQ_ROI_Calculator.xlsx`

## Status
🚧 In progress — Week 3 complete (Power BI dashboard, Excel ROI calculator,
cross-tool reconciliation, self-review pass complete).
Week 4: final README case study, architecture diagram, walkthrough video,
resume prep.

## Author
Visveswaran