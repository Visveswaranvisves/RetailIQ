-- =====================================================
-- File: 03_repeat_purchase_interval.sql
-- Purpose: Calculate time interval between repeat purchases per customer
-- Output table: [your output table name]
-- Depends on: orders_clean, customers_clean
-- Author: Visveswaran
-- =====================================================

-- Repeat Purchase Interval Analysis
-- For customers with 2+ orders, calculates days between consecutive purchases
-- using LAG() — a window function that looks at the "previous row" per customer.

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        DATE(o.order_purchase_timestamp) AS order_date
    FROM orders_clean o
    JOIN customers_clean c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),

ordered_with_lag AS (
    SELECT
        customer_unique_id,
        order_id,
        order_date,
        LAG(order_date) OVER (
            PARTITION BY customer_unique_id
            ORDER BY order_date
        ) AS previous_order_date
    FROM customer_orders
),

intervals AS (
    SELECT
        customer_unique_id,
        order_id,
        order_date,
        previous_order_date,
        JULIANDAY(order_date) - JULIANDAY(previous_order_date) AS days_since_last_order
    FROM ordered_with_lag
    WHERE previous_order_date IS NOT NULL
)

SELECT
    customer_unique_id,
    COUNT(*) AS repeat_order_count,
    ROUND(AVG(days_since_last_order), 1) AS avg_days_between_orders,
    ROUND(MIN(days_since_last_order), 1) AS min_days_between_orders,
    ROUND(MAX(days_since_last_order), 1) AS max_days_between_orders
FROM intervals
GROUP BY customer_unique_id
ORDER BY repeat_order_count DESC;