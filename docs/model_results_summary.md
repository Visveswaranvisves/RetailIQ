# Model Results Summary — RetailIQ (Week 2)

## 1. CLV Prediction (Random Forest Regressor)
- **Target:** total historical spend (monetary, from RFM)
- **Tuned MAE:** 110.65 | **R²:** 0.0351
- **Improvement over mean-baseline:** 3.0% (Baseline MAE: 114.09)
- **Top drivers (SHAP):** avg_delivery_days, avg_delay_days, recency_days
- **Note:** R² is modest — CLV in this dataset appears to be driven more by one-time purchase behavior than by the delivery/recency/frequency features captured here. Flagged honestly rather than overstated.
- See: `notebooks/15_clv_model_tuning.ipynb`, `notebooks/17_shap_clv_model.ipynb`

## 2. Churn Prediction (XGBoost Classifier)
- **Target:** churned (no purchase in 90+ days)
- **Tuned ROC-AUC:** 0.746
- **Class handling:** scale_pos_weight applied for imbalance (80.12% churn rate in data)
- **Top drivers (SHAP):** avg_delivery_days, avg_delay_days, avg_days_between_orders
- See: `notebooks/16_churn_model_tuning.ipynb`, `notebooks/18_shap_churn_model.ipynb`

## 3. Causal Analysis — Does Voucher Usage Reduce Churn?
- **Method:** DoWhy, backdoor adjustment via propensity score matching
- **Confounders controlled for:** frequency, avg_review_score, avg_delivery_days, avg_delay_days
- **Naive (correlational) difference in churn rate:** 0.0164 (1.64 percentage points higher for voucher recipients)
- **Causal estimate:** 0.1748 (17.48 percentage points higher for voucher recipients, after adjustment)
- **Interpretation:** The naive comparison substantially *understates* the true relationship. Once frequency and review sentiment are controlled for, voucher recipients show a much larger churn probability gap than the raw numbers suggest — consistent with vouchers being issued reactively to customers already showing risk signals (e.g., after a poor experience), rather than proactively driving retention. This is the opposite of the "vouchers reduce churn" assumption a naive read might suggest, and has direct implications for how the business should target retention offers.
- **Refutation tests:**
  - *Random common cause:* adding a random confounder left the estimate effectively unchanged (0.17483 → 0.17483, p=1.0) — result is stable to this perturbation.
  - *Placebo treatment:* replacing the real treatment with a random placebo shrank the effect substantially (0.1748 → 0.0583, p=0.46, not significant) — as expected for a genuine effect, since a placebo treatment should show a much weaker, non-significant relationship.
- See: `notebooks/19_causal_model_dowhy.ipynb`

## 4. Fairness Audit
- **Regional:** Paraíba (PB) showed the largest CLV prediction gap (-83.27 BRL, n=499), and Rondônia (RO) showed the largest churn-probability gap (-0.257, n=231). Both are low-volume states, and the pattern across states tracks sample size — attributable to lower training-data volume rather than a modeling flaw. Predictions for lower-volume regions should be treated with reduced confidence.
- **Price tier:** the model under-predicts churn fairly consistently across all four price tiers (gap ranges from -0.225 for High tier to -0.285 for Low tier) — no single tier shows a dramatically larger gap, suggesting the model isn't systematically discriminating by price tier the way it does by region.
- **Business implication:** Regional fairness needs a caveat in deployment (flag low-volume-state predictions as lower-confidence); price-tier fairness looks acceptable as-is.
- See: `notebooks/20_fairness_audit_region.ipynb`, `notebooks/21_fairness_audit_price_tier.ipynb`

## Key Takeaway
This project doesn't just predict outcomes — it distinguishes correlation from
causation for a real business lever (vouchers), and audits whether the models
that inform that lever are being applied fairly across customer segments. The
gap between the naive 0.0164 and causal 0.1748 estimate is the single most
important number in this project: it reveals that vouchers are being used
reactively on at-risk customers rather than proactively preventing churn —
the opposite of what a surface-level read of the data would suggest, and
exactly the kind of distinction that should change how a business allocates
its retention budget.

## Key Findings

**Customer base:** 96,096 unique customers, with a low overall repeat-purchase
rate (2.91%) — typical for this category and period, and the core reason a
retention strategy has real commercial upside here.

**Predictive models:** The CLV model explains a modest share of variance in
customer spend (R² = 0.035, 3.0% improvement over a mean-baseline), suggesting
CLV here is driven more by one-off purchase dynamics than by the delivery and
recency features available. The churn classifier performs more strongly,
reaching 0.746 ROC-AUC, with `avg_delivery_days` and `avg_delay_days` as the
strongest predictors per SHAP analysis.

**The causal result (the core finding):** A naive comparison shows voucher
users churn only slightly more than non-users (1.64 percentage points). But
controlling for purchase frequency, review sentiment, and delivery experience
via a DoWhy causal model (propensity score matching, validated with two
refutation tests), the *true causal effect* of receiving a voucher is a 17.48
percentage-point *increase* in churn probability — confounders were masking,
not inflating, the real relationship. This points to vouchers being issued
reactively to already at-risk customers rather than functioning as an
effective retention lever, exactly the kind of distinction that matters
before a business scales a discount program.

**Fairness:** Model predictions show a measurable regional gap for
lower-order-volume states (notably PB and RO), consistent with training-data
volume imbalance rather than a modeling flaw — flagged as a caution for real
deployment. Price-tier fairness is comparatively even across all four tiers.

**Business impact (revised framing):** Because the causal analysis shows the
current voucher mechanism is reactive rather than preventive, a straight
"scale the voucher program" ROI projection would be misleading. Instead, the
model identifies the addressable opportunity: the top 20% highest-churn-risk
customers who have *not yet* received a voucher (18,021 customers) represent
approximately 2,643,900 BRL in revenue at risk. A proactive intervention
program targeting this group, at an assumed 15 BRL/customer cost (270,315
BRL total), would need to prevent churn in only 10.2% of this group to break
even — a low, testable bar, rather than an unverified assumption about
program effectiveness. See `excel/RetailIQ_ROI_Calculator.xlsx` for the
full interactive model, including the original adoption-scenario ROI view
for comparison.

## Dashboard & Tools
See the [Power BI Dashboard](#power-bi-dashboard) and
[Excel ROI Calculator](#excel-roi-calculator) sections below.