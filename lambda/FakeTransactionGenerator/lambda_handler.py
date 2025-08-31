import json
import random
import string
import requests

API_URL = os.environ.get("API_URL")

def generate_payment_id(valid=True):
    if valid:
        return ''.join(random.choices(string.digits, k=16))
    else:
        return ''.join(random.choices(string.digits, k=random.randint(10, 20)))

def generate_transaction():
    valid = random.choice([True, False])
    return {
        "payment_id": generate_payment_id(valid),
        "user_id": "U" + str(random.randint(1000, 9999)),
        "amount": round(random.uniform(10, 1000), 2),
        "currency": random.choice(["USD", "EUR", "INR"]),
        "status": "PENDING"
    }

def lambda_handler(event, context):
    for _ in range(5):
        txn = generate_transaction()
        try:
            resp = requests.post(API_URL, json=txn)
            print("Sent:", txn, "Response:", resp.status_code)
        except Exception as e:
            print("Error sending txn:", txn, str(e))
    return {"statusCode": 200, "body": "Transactions generated"}