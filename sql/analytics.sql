-- ============================================================
-- AUTOMATED ETL PIPELINE
-- ANALYTICS SQL
-- ============================================================

-- ============================================================
-- 1. OVERALL BUSINESS KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS total_revenue,
    ROUND(AVG(total_usd), 2) AS average_order_value,
    ROUND(MIN(total_usd), 2) AS minimum_order_value,
    ROUND(MAX(total_usd), 2) AS maximum_order_value
FROM orders;


-- ============================================================
-- 2. TOTAL CUSTOMERS
-- ============================================================

SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE marketing_opt_in = TRUE) AS marketing_opted_in,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE marketing_opt_in = TRUE)
        / NULLIF(COUNT(*), 0),
        2
    ) AS marketing_opt_in_percentage
FROM customers;


-- ============================================================
-- 3. TOTAL UNITS SOLD
-- ============================================================

SELECT
    SUM(quantity) AS total_units_sold,
    COUNT(*) AS total_order_lines
FROM order_items;


-- ============================================================
-- 4. REVENUE BY COUNTRY
-- ============================================================

SELECT
    country,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS total_revenue,
    ROUND(AVG(total_usd), 2) AS average_order_value
FROM orders
GROUP BY country
ORDER BY total_revenue DESC;


-- ============================================================
-- 5. REVENUE BY PRODUCT CATEGORY
-- ============================================================

SELECT
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total_usd), 2) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- ============================================================
-- 6. TOP 10 PRODUCTS BY REVENUE
-- ============================================================

SELECT
    p.product_id,
    p.name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total_usd), 2) AS revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY
    p.product_id,
    p.name,
    p.category
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================
-- 7. PRODUCT PROFITABILITY
-- ============================================================

SELECT
    p.product_id,
    p.name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * p.cost_usd), 2) AS total_cost,
    ROUND(SUM(oi.line_total_usd), 2) AS revenue,
    ROUND(
        SUM(oi.line_total_usd) -
        SUM(oi.quantity * p.cost_usd),
        2
    ) AS gross_profit
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY
    p.product_id,
    p.name,
    p.category
ORDER BY gross_profit DESC
LIMIT 20;


-- ============================================================
-- 8. MONTHLY REVENUE
-- ============================================================

SELECT
    DATE_TRUNC('month', order_time)::DATE AS month,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS revenue,
    ROUND(AVG(total_usd), 2) AS average_order_value
FROM orders
GROUP BY DATE_TRUNC('month', order_time)
ORDER BY month;


-- ============================================================
-- 9. DAILY ORDERS
-- ============================================================

SELECT
    order_time::DATE AS order_date,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS revenue
FROM orders
GROUP BY order_time::DATE
ORDER BY order_date;


-- ============================================================
-- 10. PAYMENT METHOD DISTRIBUTION
-- ============================================================

SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS revenue,
    ROUND(AVG(total_usd), 2) AS average_order_value
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;


-- ============================================================
-- 11. DEVICE PERFORMANCE
-- ============================================================

SELECT
    device,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS revenue,
    ROUND(AVG(total_usd), 2) AS average_order_value
FROM orders
GROUP BY device
ORDER BY revenue DESC;


-- ============================================================
-- 12. TRAFFIC SOURCE PERFORMANCE
-- ============================================================

SELECT
    source,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS revenue,
    ROUND(AVG(total_usd), 2) AS average_order_value
FROM orders
GROUP BY source
ORDER BY revenue DESC;


-- ============================================================
-- 13. DISCOUNT IMPACT
-- ============================================================

SELECT
    CASE
        WHEN discount_pct = 0 THEN 'No Discount'
        WHEN discount_pct < 10 THEN '1-9%'
        WHEN discount_pct < 20 THEN '10-19%'
        WHEN discount_pct < 30 THEN '20-29%'
        ELSE '30%+'
    END AS discount_bucket,

    COUNT(*) AS total_orders,
    ROUND(AVG(total_usd), 2) AS average_order_value,
    ROUND(SUM(total_usd), 2) AS revenue

FROM orders

GROUP BY
    CASE
        WHEN discount_pct = 0 THEN 'No Discount'
        WHEN discount_pct < 10 THEN '1-9%'
        WHEN discount_pct < 20 THEN '10-19%'
        WHEN discount_pct < 30 THEN '20-29%'
        ELSE '30%+'
    END

ORDER BY
    MIN(discount_pct);


-- ============================================================
-- 14. CUSTOMER PURCHASE FREQUENCY
-- ============================================================

SELECT
    customer_id,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_usd), 2) AS lifetime_value,
    ROUND(AVG(total_usd), 2) AS average_order_value
FROM orders
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 20;


-- ============================================================
-- 15. CUSTOMER LIFETIME VALUE
-- ============================================================

SELECT
    c.customer_id,
    c.name,
    c.country,
    COUNT(o.order_id) AS total_orders,
    ROUND(COALESCE(SUM(o.total_usd), 0), 2) AS lifetime_value,
    ROUND(COALESCE(AVG(o.total_usd), 0), 2) AS average_order_value
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.name,
    c.country
ORDER BY lifetime_value DESC
LIMIT 20;


-- ============================================================
-- 16. CUSTOMER SEGMENTATION
-- ============================================================

SELECT
    CASE
        WHEN order_count = 0 THEN 'No Orders'
        WHEN order_count = 1 THEN 'One-Time'
        WHEN order_count BETWEEN 2 AND 5 THEN 'Returning'
        ELSE 'Loyal'
    END AS customer_segment,
    COUNT(*) AS customers
FROM (
    SELECT
        c.customer_id,
        COUNT(o.order_id) AS order_count
    FROM customers c
    LEFT JOIN orders o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
) customer_orders
GROUP BY
    CASE
        WHEN order_count = 0 THEN 'No Orders'
        WHEN order_count = 1 THEN 'One-Time'
        WHEN order_count BETWEEN 2 AND 5 THEN 'Returning'
        ELSE 'Loyal'
    END
ORDER BY customers DESC;


-- ============================================================
-- 17. TOP CUSTOMERS BY REVENUE
-- ============================================================

SELECT
    c.customer_id,
    c.name,
    c.country,
    COUNT(o.order_id) AS orders,
    ROUND(SUM(o.total_usd), 2) AS revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.name,
    c.country
ORDER BY revenue DESC
LIMIT 10;


-- ============================================================
-- 18. ORDER VALUE DISTRIBUTION
-- ============================================================

SELECT
    CASE
        WHEN total_usd < 50 THEN '< $50'
        WHEN total_usd < 100 THEN '$50-$99'
        WHEN total_usd < 250 THEN '$100-$249'
        WHEN total_usd < 500 THEN '$250-$499'
        ELSE '$500+'
    END AS order_value_bucket,
    COUNT(*) AS orders,
    ROUND(SUM(total_usd), 2) AS revenue
FROM orders
GROUP BY
    CASE
        WHEN total_usd < 50 THEN '< $50'
        WHEN total_usd < 100 THEN '$50-$99'
        WHEN total_usd < 250 THEN '$100-$249'
        WHEN total_usd < 500 THEN '$250-$499'
        ELSE '$500+'
    END
ORDER BY MIN(total_usd);


-- ============================================================
-- END OF ANALYTICS
-- ============================================================
