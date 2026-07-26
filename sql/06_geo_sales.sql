-- =====================================================
-- File: 06_geo_sales.sql
-- Purpose: Aggregate order volume and revenue by customer state
-- Output table: geo_sales
-- Depends on: orders_clean, customers_clean, order_items_clean
-- Author: Visveswaran
-- =====================================================

DROP TABLE IF EXISTS geo_sales;

CREATE TABLE geo_sales AS
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    AVG(oi.price) AS avg_order_value
FROM orders_clean o
JOIN customers_clean c ON o.customer_id = c.customer_id
JOIN order_items_clean oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC;