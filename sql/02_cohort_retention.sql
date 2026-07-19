-- Cohort Retention Analysis
-- Groups customers by the month of their first purchase (cohort),
-- then tracks how many of that cohort purchased again in subsequent months.

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        DATE(o.order_purchase_timestamp) AS order_date
    FROM orders_clean o
    JOIN customers_clean c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),

first_purchase AS (
    SELECT
        customer_unique_id,
        MIN(strftime('%Y-%m', order_date)) AS cohort_month
    FROM customer_orders
    GROUP BY customer_unique_id
),

orders_with_cohort AS (
    SELECT
        co.customer_unique_id,
        fp.cohort_month,
        strftime('%Y-%m', co.order_date) AS order_month
    FROM customer_orders co
    JOIN first_purchase fp ON co.customer_unique_id = fp.customer_unique_id
),

cohort_activity AS (
    SELECT
        cohort_month,
        order_month,
        -- month index: how many months after first purchase this activity happened
        (CAST(strftime('%Y', order_month || '-01') AS INTEGER) * 12 + CAST(strftime('%m', order_month || '-01') AS INTEGER))
        - (CAST(strftime('%Y', cohort_month || '-01') AS INTEGER) * 12 + CAST(strftime('%m', cohort_month || '-01') AS INTEGER))
        AS month_index,
        COUNT(DISTINCT customer_unique_id) AS active_customers
    FROM orders_with_cohort
    GROUP BY cohort_month, order_month
),

cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT customer_unique_id) AS cohort_customers
    FROM first_purchase
    GROUP BY cohort_month
)

SELECT
    ca.cohort_month,
    ca.month_index,
    ca.active_customers,
    cs.cohort_customers,
    ROUND(100.0 * ca.active_customers / cs.cohort_customers, 1) AS retention_pct
FROM cohort_activity ca
JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.month_index;