# Financial Transaction Verification Project

## Project Objective

The main goal of this project is to simulate a **Finance Transaction Verification System** on AWS using serverless architecture and free-tier services.  
I wanted to create a realistic pipeline that generates transaction data, validates it, stores it in a database, and sends notifications, just like in a real-world financial system.

---

## Use Case

In the real world, banks and fintech companies need to verify transactions quickly and automatically to detect fraud or incomplete data.  
This project demonstrates a simplified version of that:  

- **Valid transactions** are sent to the verification team.  
- **Fraudulent transactions** (like incorrect payment IDs) are flagged and notified.  
- The system is fully automated using **AWS Lambda, API Gateway, SQS, RDS, SNS, and CloudWatch**.

---

## Workflow Diagram

FakeTransactionGenerator Lambda
      --> API Gateway
     -->Validation Lambda
     ┌──────┴───────┐
     |                 |
   SQS (Valid)    SQS (Fraud)
     |              |
      \            /
        \          /
         \        /
          V      V
Insert Lambda (handles both queues)
     ┌──────┴───────┐
     |                 |
  RDS Valid       RDS Fraud
     |               |
   SNS Mail       SNS Mail



---

## How It Works

1. **Generate Fake Transactions**  
   - The `FakeTransactionGenerator` Lambda generates random transactions with fields like `payment_id`, `user_id`, `amount`, `currency`, and `status`.

2. **Send Transactions to API Gateway**  
   - The Lambda posts transactions to the API Gateway endpoint `/submitTransaction`.

3. **Validate Transactions**  
   - The `ValidationLambda` checks if `payment_id` is 16 digits.  
   - Valid transactions → SQS `valid_transactions_queue`  
   - Fraud transactions → SQS `fraud_transactions_queue`

4. **Insert into RDS**  
   - The `InsertLambda` reads messages from SQS queues and inserts transactions into **RDS MySQL/Aurora**:  
     - `valid_transactions` table  
     - `fraud_transactions` table  

5. **Send Notifications via SNS**  
   - Emails are sent to the verification team for valid transactions.  
   - Fraud alerts are sent for incorrect transactions.

6. **Monitoring**  
   - All Lambda logs are monitored with **CloudWatch**.  
   - Secrets like DB credentials are stored securely in **Secrets Manager**.

---

## How to Run

1. **Deploy RDS**  
   - Run the SQL script to create `valid_transactions` and `fraud_transactions` tables.  
   - Note the DB endpoint, username, and password for Lambda environment variables.

2. **Deploy Lambda Functions**  
   - 3 Lambdas: `FakeTransactionGenerator`, `ValidationLambda`, `InsertLambda`.  
   - Attach dependencies like `requests` and `pymysql` via Lambda layers or `requirements.txt`.

3. **Setup API Gateway**  
   - Create a POST route `/submitTransaction`.  
   - Integrate with `ValidationLambda` using Lambda Proxy Integration.

4. **Setup SQS Queues**  
   - Create `valid_transactions_queue` and `fraud_transactions_queue`.

5. **Set Environment Variables for Lambdas**  
   - `VALID_QUEUE_URL`, `FRAUD_QUEUE_URL`, `DB_SECRET_ARN`, `API_URL` (for generator).

6. **Run the Fake Transaction Generator**  
   - Either invoke the Lambda manually or run the script locally.  
   - Transactions are sent to API Gateway → Validation → SQS → RDS & SNS.

7. **Check Results**  
   - RDS tables: `valid_transactions` & `fraud_transactions`.  
   - Emails received via SNS.  
   - CloudWatch logs for debugging.

---

## Conclusion

I built this project to demonstrate a **realistic AWS serverless workflow** for transaction verification.  

- Event-driven architecture using Lambda, SQS, and API Gateway.  
- RDS used to store valid and fraudulent transactions.  
- Notifications via SNS.  
- Fully free-tier friendly.  

In interviews, I can explain **how to extend validation rules**, **monitor with CloudWatch**, or **add Step Functions** for more complex workflows.  

This project shows my ability to design and implement **end-to-end serverless pipelines** in AWS for real-world use cases.

