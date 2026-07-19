\# Data Dictionary — RetailIQ



\## orders (\~99,441 rows)

\- \*\*Primary key:\*\* order\_id

\- \*\*Foreign key:\*\* customer\_id → customers.customer\_id

\- Key columns: order\_status, order\_purchase\_timestamp, order\_delivered\_customer\_date, order\_estimated\_delivery\_date

\- Notes: order\_delivered\_customer\_date is null for undelivered orders — expected, not a data error.



\## order\_items

\- \*\*Primary key:\*\* order\_id + order\_item\_id (composite)

\- \*\*Foreign keys:\*\* order\_id → orders.order\_id, product\_id → products.product\_id, seller\_id → sellers.seller\_id

\- Key columns: price, freight\_value

\- Notes: one row per item per order — an order with 3 items has 3 rows here.



\## customers

\- \*\*Primary key:\*\* customer\_id

\- Key columns: customer\_unique\_id, customer\_city, customer\_state

\- Notes: customer\_id is order-specific; customer\_unique\_id is the true unique person — use customer\_unique\_id for repeat-purchase / CLV analysis, not customer\_id.



\## payments

\- \*\*Foreign key:\*\* order\_id → orders.order\_id

\- Key columns: payment\_type, payment\_installments, payment\_value

\- Notes: an order can have multiple payment rows (e.g. voucher + credit card combined).



\## reviews

\- \*\*Foreign key:\*\* order\_id → orders.order\_id

\- Key columns: review\_score (1-5), review\_comment\_title, review\_comment\_message

\- Notes: comment fields are frequently null — customers rate without writing text.



\## products

\- \*\*Primary key:\*\* product\_id

\- Key columns: product\_category\_name, product\_weight\_g



\## sellers

\- \*\*Primary key:\*\* seller\_id

\- Key columns: seller\_city, seller\_state



\## geolocation

\- Key columns: geolocation\_zip\_code\_prefix, geolocation\_lat, geolocation\_lng

\- Notes: many-to-one with zip prefix — will need aggregation (e.g. mean lat/lng per prefix) before joining.



\## Critical join path for analysis

orders → order\_items → products / sellers

orders → payments

orders → reviews

orders → customers (via customer\_id) → dedupe on customer\_unique\_id for CLV

