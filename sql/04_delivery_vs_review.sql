-- Delivery Time vs Review Score
-- Compares actual delivery duration and delivery delay (vs estimate)
-- against the review score customers left.

WITH delivery_data AS (
    SELECT
        o.order_id,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp) AS delivery_days,
        JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date) AS delay_days
    FROM orders_clean o
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
),

joined_reviews AS (
    SELECT
        d.order_id,
        d.delivery_days,
        d.delay_days,
        CASE WHEN d.delay_days > 0 THEN 'Late' ELSE 'On Time / Early' END AS delivery_status,
        r.review_score
    FROM delivery_data d
    JOIN reviews_clean r ON d.order_id = r.order_id
)

SELECT
    delivery_status,
    COUNT(*) AS order_count,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(delay_days), 1) AS avg_delay_days
FROM joined_reviews
GROUP BY delivery_status
ORDER BY avg_review_score DESC;