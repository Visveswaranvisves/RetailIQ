# Deploy RetailIQ for free

Upload the entire `dashboard` folder into the root of your existing RetailIQ GitHub repository. Keep `data/archive (4).zip` and the existing `docs` folder unchanged.

In Streamlit Community Cloud, choose Create app:

- Repository: Visveswaranvisves/RetailIQ
- Branch: main
- Main file: dashboard/app.py
- Advanced settings: Python 3.11
- Suggested subdomain: visves-retailiq (subject to availability)

Streamlit uses the requirements.txt next to the entry point. Keep this dependency file inside dashboard; the original root requirements.txt is for the research environment and is not needed by the dashboard.

The first run reads selected CSVs from the existing ZIP. Data is cached for later interactions. No API keys, database or paid AI service are required.

## What is included

- Sales overview with date/state filters and CSV export
- Customer frequency/inactivity segments and monthly retention cohorts
- Seller sales and delivery/review analysis
- Retention intervention scenario calculator with contribution margin
- Saved research results and SHAP/fairness figures

## Definitions

Analytics include delivered orders only. Order payments are aggregated before joining customer/review records to avoid double counting. Revenue refers to collected payments including freight; seller item sales exclude freight. Customer retention and inactivity are computed inside the selected period, not over unseen future activity. Cohort cells beyond the observation horizon remain blank.

ROI is a user-controlled scenario, not a forecast. Its initial target count and revenue at risk are sourced from docs/model_results_summary.md. Research metrics are saved results, not live predictions or independent reproductions. No trained ML artifacts are present for deployment. The original Power BI report and Excel workbook remain unchanged.

## Local run

From the repository root:

    python -m pip install -r dashboard/requirements.txt
    python -m streamlit run dashboard/app.py
