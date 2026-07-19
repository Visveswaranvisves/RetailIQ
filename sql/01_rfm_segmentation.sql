-- RFM Segmentation
-- Recency: days since last purchase (as of the most recent date in the dataset)
-- Frequency: number of distinct orders per unique customer
-- Monetary: total amount spent per unique customer

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        p.payment_value
    FROM orders_clean o
    JOIN customers_clean c ON o.customer_id = c.customer_id
    JOIN payments_clean p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
),

max_date AS (
    SELECT MAX(order_purchase_timestamp) AS ref_date FROM customer_orders
),

rfm_base AS (
    SELECT
        co.customer_unique_id,
        JULIANDAY((SELECT ref_date FROM max_date)) - JULIANDAY(MAX(co.order_purchase_timestamp)) AS recency_days,
        COUNT(DISTINCT co.order_id) AS frequency,
        SUM(co.payment_value) AS monetary
    FROM customer_orders co
    GROUP BY co.customer_unique_id
),

rfm_scored AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_base
)

SELECT
    customer_unique_id,
    ROUND(recency_days, 0) AS recency_days,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score, f_score, m_score,
    (r_score + f_score + m_score) AS rfm_total,
    CASE
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 2 THEN 'Loyal Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk (High Value)'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost / Churned'
        ELSE 'Needs Attention'
    END AS segment
FROM rfm_scored
ORDER BY rfm_total DESC;