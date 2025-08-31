USE finance_db;
CREATE TABLE valid_transactions (
    transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payment_id CHAR(16) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency CHAR(3) NOT NULL,
    status VARCHAR(20) DEFAULT 'VALID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE fraud_transactions (
    fraud_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payment_id VARCHAR(30), -- can be longer/shorter
    user_id VARCHAR(50),
    amount DECIMAL(10,2),
    currency CHAR(3),
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SHOW TABLES;

SELECT * FROM fraud_transactions;
SELECT * FROM valid_transactions;

ALTER TABLE valid_transactions
MODIFY COLUMN status VARCHAR(50) DEFAULT 'sending to verification';
ALTER TABLE fraud_transactions
MODIFY COLUMN status VARCHAR(50) DEFAULT 'failed';

DESCRIBE valid_transactions;