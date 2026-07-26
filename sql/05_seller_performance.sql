-- =====================================================
-- File: 05_seller_performance.sql
-- Purpose: Aggregate seller-level performance metrics (orders, revenue, delivery speed, review score)
-- Output table: seller_performance
-- Depends on: order_items_clean, orders_clean, reviews_clean
-- Author: Visveswaran
-- =====================================================

DROP TABLE IF EXISTS seller_performance;

CREATE TABLE seller_performance AS
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    AVG(julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)) AS avg_delivery_days,
    AVG(r.review_score) AS avg_review_score
FROM order_items_clean oi
JOIN orders_clean o ON oi.order_id = o.order_id
LEFT JOIN reviews_clean r ON oi.order_id = r.order_id
GROUP BY oi.seller_id;