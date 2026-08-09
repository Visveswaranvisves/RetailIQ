\# RetailIQ Walkthrough Script (\~3 min)



\## \[0:00-0:20] Hook + Problem

"Hi, I'm Visveswaran. This is RetailIQ -- a project that answers a question

most e-commerce businesses can't actually answer: does giving customers

discounts and vouchers \*cause\* them to come back, or are we just handing

perks to customers who'd have returned anyway?"



\## \[0:20-0:50] Data + Approach

"I used Olist's real Brazilian e-commerce dataset -- about 99,000 orders

across 8 relational tables. I built this as a full analyst pipeline: SQL

for the data layer, Python for modeling, and Power BI plus Excel to turn

the results into something a business could actually use."

\[Show architecture diagram on screen -- docs/architecture\_diagram.png]



\## \[0:50-1:30] SQL + Modeling (brief)

"In SQL I built RFM segmentation and cohort retention analysis using window

functions. Then in Python I trained a CLV model and a churn classifier,

explained with SHAP -- so I'm not just predicting who'll churn, I can say why."

\[Show one SQL query briefly, then a SHAP summary plot]



\## \[1:30-2:15] The Causal Result (THE MAIN EVENT -- slow down here)

"Here's the core finding. A naive comparison shows voucher users churn less

than non-users. But that's correlation -- voucher users might just already be

more loyal customers. So I built a causal model with DoWhy, controlling for

purchase frequency, review sentiment, and delivery experience as confounders.

The real causal effect: voucher usage reduces churn probability by about

17.5 percentage points -- smaller than the naive number, but real, and

validated with three refutation tests."

\[Show the causal notebook output: naive\_diff vs. causal estimate]



\## \[2:15-2:45] Business Translation

"I turned that into something usable -- a Power BI dashboard for exploring

retention and segments, and an Excel calculator where a stakeholder can pick

a scenario and see the projected ROI. At 30% voucher adoption, that's a net

positive ROI of about \[your number] BRL."

\[Show Power BI overview page, then Excel Summary sheet]



\## \[2:45-3:00] Close

"That's RetailIQ -- full repo, all the SQL, notebooks, and dashboards, are

linked below. Thanks for watching."

