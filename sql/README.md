\# SQL Queries — RetailIQ



All queries run against `retailiq.db` (SQLite), built from the cleaned `\*\_clean` tables.



| File | Output Table | Business Question |

|---|---|---|

| 01\_rfm\_segmentation.sql | rfm\_segments | Who are our most valuable customers? |

| 02\_cohort\_retention.sql | cohort\_retention | How well do we retain customers over time? |

| 03\_repeat\_purchase\_interval.sql | repeat\_purchase\_intervals | How often do customers come back? |

| 04\_delivery\_vs\_review.sql | delivery\_vs\_review | Does delivery speed drive satisfaction? |



\## How to run

Each query has a matching runner script in `/notebooks` (e.g. `04\_run\_rfm.py` for

`01\_rfm\_segmentation.sql`) that executes it and saves the result as a table in `retailiq.db`.



\## Validation

See `notebooks/08\_validate\_sql\_outputs.py` for cross-checks confirming these outputs

are internally consistent with the raw cleaned data.

