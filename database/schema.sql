-- FinSight AI Database Schema

CREATE DATABASE IF NOT EXISTS finsight_db;
USE finsight_db;

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    INDEX idx_name (name)
);

-- Vendors table
CREATE TABLE IF NOT EXISTS vendors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL UNIQUE,
    normalized_name VARCHAR(255),
    category VARCHAR(100),
    benchmark_cost FLOAT,
    risk_score FLOAT DEFAULT 0.0,
    INDEX idx_normalized (normalized_name),
    INDEX idx_category (category)
);

-- Spend transactions table
CREATE TABLE IF NOT EXISTS spend_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    vendor_id INT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL,
    spend_type VARCHAR(50),
    payment_type VARCHAR(50),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    INDEX idx_date (date),
    INDEX idx_vendor (vendor_id),
    INDEX idx_department (department_id)
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    department_id INT NOT NULL,
    plan_tier VARCHAR(100),
    seat_count INT,
    monthly_cost FLOAT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    INDEX idx_vendor (vendor_id)
);

-- Contracts table
CREATE TABLE IF NOT EXISTS contracts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    renewal_date DATE NOT NULL,
    annual_value FLOAT NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    INDEX idx_renewal_date (renewal_date)
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_id INT NOT NULL,
    recommendation_type VARCHAR(100),
    projected_savings FLOAT,
    rationale TEXT,
    risk_level VARCHAR(20),
    alternative_vendor VARCHAR(255),
    feature_parity TEXT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    INDEX idx_type (recommendation_type),
    INDEX idx_savings (projected_savings)
);

-- Chat queries table
CREATE TABLE IF NOT EXISTS chat_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    generated_sql TEXT,
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created (created_at)
);
