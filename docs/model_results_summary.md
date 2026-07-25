\# Model Results Summary — RetailIQ (Week 2)



\## 1. CLV Prediction (Random Forest Regressor)

\- \*\*Target:\*\* total historical spend (monetary, from RFM)

\- \*\*Tuned MAE:\*\* \[X] | \*\*R²:\*\* \[X]

\- \*\*Improvement over mean-baseline:\*\* \[X]%

\- \*\*Top drivers (SHAP):\*\* \[list top 3 from your summary plot, e.g. frequency, avg\_review\_score, repeat\_order\_count]

\- See: `notebooks/15\_clv\_model\_tuning.ipynb`, `notebooks/17\_shap\_clv\_model.ipynb`



\## 2. Churn Prediction (XGBoost Classifier)

\- \*\*Target:\*\* churned (no purchase in 90+ days)

\- \*\*Tuned ROC-AUC:\*\* \[X]

\- \*\*Class handling:\*\* scale\_pos\_weight applied for imbalance (\[X]% churn rate in data)

\- \*\*Top drivers (SHAP):\*\* \[list top 3]

\- See: `notebooks/16\_churn\_model\_tuning.ipynb`, `notebooks/18\_shap\_churn\_model.ipynb`



\## 3. Causal Analysis — Does Voucher Usage Reduce Churn?

\- \*\*Method:\*\* DoWhy, backdoor adjustment via propensity score matching

\- \*\*Confounders controlled for:\*\* frequency, avg\_review\_score, avg\_delivery\_days, avg\_delay\_days

\- \*\*Naive (correlational) difference in churn rate:\*\* \[X]

\- \*\*Causal estimate:\*\* \[X]

\- \*\*Interpretation:\*\* \[X]% of the naive difference was explained by confounding

&#x20; (i.e., voucher users already being more loyal customers) rather than the

&#x20; voucher itself.

\- \*\*Refutation tests:\*\* \[summarize — e.g. "stable under random common cause and

&#x20; data subset tests; placebo test showed effect shrinking toward zero as expected"]

\- See: `notebooks/19\_causal\_model\_dowhy.ipynb`



\## 4. Fairness Audit

\- \*\*Regional:\*\* \[state] showed the largest prediction gap (\[X] on CLV / \[X] on

&#x20; churn probability), attributable to lower sample volume in the training data

&#x20; rather than a modeling flaw. Predictions for lower-volume regions should be

&#x20; treated with reduced confidence.

\- \*\*Price tier:\*\* the model \[over/under]-predicts churn for \[tier] customers by

&#x20; \[X] percentage points.

\- \*\*Business implication:\*\* \[1-2 sentences]

\- See: `notebooks/20\_fairness\_audit\_region.ipynb`, `notebooks/21\_fairness\_audit\_price\_tier.ipynb`



\## Key Takeaway

This project doesn't just predict outcomes — it distinguishes correlation from

causation for a real business lever (vouchers), and audits whether the models

that inform that lever are being applied fairly across customer segments. The

gap between the naive \[X] and causal \[X] estimate is the single most important

number in this project: it's the difference between a business overspending on

discounts for customers who didn't need them, versus targeting the customers

who actually respond.

