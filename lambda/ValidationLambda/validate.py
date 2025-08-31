import json
import boto3
import os

# Initialize SQS client
sqs = boto3.client("sqs")

# Replace with your SQS URLs
VALID_QUEUE_URL = os.environ["valid_url"]
FRAUD_QUEUE_URL = os.environ["fraud_url"]



def lambda_handler(event, context):
    # Get JSON body from API Gateway
    print("Received event:", event)

    try:
        body = json.loads(event["body"])
    except KeyError:
        # If body is missing (direct test invoke)
        body = event

    payment_id = body.get("payment_id")
    print("Payment ID:", payment_id)

    if payment_id and len(payment_id) == 16:
        body["status"] = "sending to verification" 
        print(body)
        sqs.send_message(QueueUrl=VALID_QUEUE_URL, MessageBody=json.dumps(body))
        status1 = "VALID"
    else:
        body["status"] = "failed"  
        body["reason"] = "Invalid Payment ID"
        print(body)
        sqs.send_message(QueueUrl=FRAUD_QUEUE_URL, MessageBody=json.dumps(body))
        status1 = "FRAUD"

    return {
        "statusCode": 200,
        "body": json.dumps({"status1": status1})
    }
