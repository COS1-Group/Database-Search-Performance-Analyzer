-- Create the table (if not already created
CREATE TABLE  IF NOT EXISTS customer_purchases (
    customer_id VARCHAR(20) PRIMARY KEY,  -- Primary index automatically created
    customer_name VARCHAR(255),
    purchase_date DATE,
    product_id VARCHAR(50),
    product_category VARCHAR(100),
    amount DECIMAL(10,2)
);

-- Import CSV data (using \copy for file permissions and use/update data path)
\copy customer_purchases FROM 'purchases_data.csv' DELIMITER ',' CSV HEADER;

-- Create secondary index on product_category
CREATE INDEX idx_product_category ON customer_purchases(product_category);

-- Create non-clustered index on purchase_date
CREATE INDEX idx_purchase_date ON customer_purchases(purchase_date);

-- Verify all indexes were created
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'customer_purchases';

-- =====================================================
-- ASSIGNMENT QUERY EXAMPLES
-- =====================================================

-- Query 1: Retrieve all purchases in a date range
SELECT 
    customer_id,
    customer_name,
    purchase_date,
    product_id,
    product_category,
    amount
FROM customer_purchases 
WHERE purchase_date BETWEEN '2024-01-20' AND '2024-02-10'
ORDER BY purchase_date;

-- Query 2: Retrieve all purchases in a given category
SELECT 
    customer_id,
    customer_name,
    purchase_date,
    product_id,
    amount
FROM customer_purchases 
WHERE product_category = 'Electronics'
ORDER BY amount DESC;