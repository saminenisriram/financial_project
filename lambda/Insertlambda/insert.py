import os
import json
import boto3
import pymysql
import logging
from pymysql.err import OperationalError, IntegrityError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# env
SECRET_NAME = os.environ['SECRET_NAME']
VALID_SNS_TOPIC_ARN = os.environ['VALID_SNS_TOPIC_ARN']
FRAUD_SNS_TOPIC_ARN = os.environ['FRAUD_SNS_TOPIC_ARN']
VALID_QUEUE_INDICATOR = os.environ.get('VALID_QUEUE_INDICATOR', 'valid-transactions-queue')

sm = boto3.client('secretsmanager')
sns = boto3.client('sns')

_cached_secret = None

def get_db_creds():
    global _cached_secret
    if _cached_secret:
        return _cached_secret
    resp = sm.get_secret_value(SecretId=SECRET_NAME)
    secret = json.loads(resp['SecretString'])
    _cached_secret = secret
    return secret

def get_conn():
    creds = get_db_creds()
    conn = pymysql.connect(
        host=creds['host'],
        user=creds['username'],
        password=creds['password'],
        database=creds['database'],
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
    return conn

def insert_valid(cursor, txn):
    
    sql = """
      INSERT INTO valid_transactions (payment_id, user_id, amount, currency)
      VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (txn.get('payment_id'), txn.get('user_id'), txn.get('amount'), txn.get('currency')))

def insert_fraud(cursor, txn):
    
    sql = """
      INSERT INTO fraud_transactions (payment_id, user_id, amount, currency, reason)
      VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (txn.get('payment_id'), txn.get('user_id'), txn.get('amount'), txn.get('currency'), txn.get('reason', 'Invalid Payment ID')))

def publish(topic_arn, message, subject):
    sns.publish(TopicArn=topic_arn, Message=message, Subject=subject)

def lambda_handler(event, context):
    logger.info("Received SQS event with %d records", len(event.get('Records', [])))
    try:
        conn = get_conn()
        cursor = conn.cursor()
    except Exception as e:
        logger.exception("DB connection failed")
        raise

    processed = 0
    try:
        for record in event['Records']:
            try:
                body = json.loads(record['body'])
                print(body)
            except Exception:
                logger.exception("Invalid JSON in record body")
                # choose to raise to retry entire batch, or continue to skip:
                raise

            queue_arn = record.get('eventSourceARN','')
            is_valid_queue = VALID_QUEUE_INDICATOR in queue_arn

            if is_valid_queue:
                insert_valid(cursor, body)
                publish(VALID_SNS_TOPIC_ARN, f"Valid Transaction: {body}", "Valid Transaction")
            else:
                # store reason if it exists; otherwise default
                if 'reason' not in body:
                    body['reason'] = body.get('reason','Invalid Payment ID')
                insert_fraud(cursor, body)
                publish(FRAUD_SNS_TOPIC_ARN, f"Fraud Transaction: {body}", "Fraud Transaction")

            processed += 1

        conn.commit()
        logger.info("Committed %d records to DB", processed)
    except Exception:
        logger.exception("Error processing batch, letting Lambda fail so SQS retries")
        conn.rollback()
        raise    # re-raise to signal Lambda/SQS to retry the batch
    finally:
        cursor.close()
        conn.close()

    return {"statusCode": 200, "processed": processed}
