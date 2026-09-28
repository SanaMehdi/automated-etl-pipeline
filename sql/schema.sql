-- ============================================================
-- Automated ETL Pipeline
-- PostgreSQL Database Schema
-- ============================================================

-- Drop tables in dependency order
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;


-- ============================================================
-- CUSTOMERS
-- ============================================================

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    country VARCHAR(10) NOT NULL,
    age INTEGER NOT NULL,
    signup_date DATE NOT NULL,
    marketing_opt_in BOOLEAN NOT NULL,

    CONSTRAINT customers_age_check
        CHECK (age >= 0 AND age <= 120)
);


-- ============================================================
-- PRODUCTS
-- ============================================================

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    price_usd NUMERIC(12, 2) NOT NULL,
    cost_usd NUMERIC(12, 2) NOT NULL,
    margin_usd NUMERIC(12, 2) NOT NULL,

    CONSTRAINT products_price_check
        CHECK (price_usd >= 0),

    CONSTRAINT products_cost_check
        CHECK (cost_usd >= 0),

    CONSTRAINT products_margin_check
        CHECK (margin_usd >= 0)
);


-- ============================================================
-- ORDERS
-- ============================================================

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_time TIMESTAMP NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    discount_pct NUMERIC(5, 2) NOT NULL,
    subtotal_usd NUMERIC(12, 2) NOT NULL,
    total_usd NUMERIC(12, 2) NOT NULL,
    country VARCHAR(10) NOT NULL,
    device VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,

    CONSTRAINT orders_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT orders_discount_check
        CHECK (discount_pct >= 0 AND discount_pct <= 100),

    CONSTRAINT orders_subtotal_check
        CHECK (subtotal_usd >= 0),

    CONSTRAINT orders_total_check
        CHECK (total_usd >= 0)
);


-- ============================================================
-- ORDER ITEMS
-- ============================================================

CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    unit_price_usd NUMERIC(12, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    line_total_usd NUMERIC(12, 2) NOT NULL,

    PRIMARY KEY (order_id, product_id),

    CONSTRAINT order_items_order_fk
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT order_items_product_fk
        FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    CONSTRAINT order_items_quantity_check
        CHECK (quantity > 0),

    CONSTRAINT order_items_unit_price_check
        CHECK (unit_price_usd >= 0),

    CONSTRAINT order_items_line_total_check
        CHECK (line_total_usd >= 0)
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_orders_customer_id
    ON orders(customer_id);

CREATE INDEX idx_orders_order_time
    ON orders(order_time);

CREATE INDEX idx_orders_country
    ON orders(country);

CREATE INDEX idx_order_items_product_id
    ON order_items(product_id);


-- ============================================================
-- COMPLETE
-- ============================================================
