import json
import logging
import os

import boto3
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger()
logger.setLevel(logging.INFO)

month_names = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December',
}

def lambda_handler(event, context):
    logging.info(f"event received: {event}")

    message_body = event["Records"][0]["body"]
    account_report = json.loads(message_body)
    

    env = Environment(loader=FileSystemLoader("./src"))
    template = env.get_template("email_template.html")
    data = {
        "account_report": account_report,
        "month_names": month_names
    }

    html_content = template.render(data)

    # send the email
    ses = boto3.client("ses", region_name="us-west-2")
    subject = f"Financial Report for Account {account_report['account_number']}"
    recipient = "rick-vega-reports-inbox@maildrop.cc"
    sender = "dev.ricardo.vega@gmail.com"

    response = ses.send_email(
        Destination={"ToAddresses": [recipient]},
        Message={
            "Body": {"Html": {"Charset": "UTF-8", "Data": html_content}},
            "Subject": {"Charset": "UTF-8", "Data": subject},
        },
        Source=sender,
    )

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        logger.info(f"email sent with id: {response['MessageId']}")

    sqs = boto3.client("sqs", region_name="us-west-2")
    queue_url = os.getenv("EMAIL_NOTIFICATIONS_QUEUE_URL")
    receipt_handle = event["Records"][0]["receiptHandle"]

    sqs_response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    
    if sqs_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        logger.info(f"sqs message deleted successfully: {response['MessageId']}")


if __name__ == "__main__":
    event = {
        "Records": [
            {
                "messageId": "aeb997d3-e1a0-4964-b9c9-cc64ed0c60de",
                "receiptHandle": "AQEBu+rXZoBSb4TWvgULeZBnFVFOxEQma6T8Z+AJCrrYE+ia+sL4g+GFxX6YyD46YGoTz9Zhx0eRW8+1LYeIYE7jdTOa3kCZNceWlOG9DstRDuiLmzZv05ccGW2+Mq7b/LlSBELP1f1wxToA8vbAN4xBTRGJaTjokV9VzMz4ngI7pmJfOCAd/R56UIQneOBMKhL3iHX0RfpG9d2JBrPFqgmDrScqnK/tqPvTxHL5frb6LM7AT5HqKG+3K2xp8OVDM3SycV3Z0Ysm3wF8QGMCodSALkSUNMNT6K1jkWefzU0iIyhGqbUKgzjSHL/sR6ddDCT6C98KKhWnzQdlJDO53ZHvDLpD2Ftp9IoS2mAIH/iUdq4cq6BM4hiMmnBMDmHtzeWZ39791RBm+w2ax95GfirnOFHWN1PimqiwTwn3ss+s5ds=",
                "body": '{"account_number": "424236340", "total_balance": 3807.6599999999944, "average_debit_amount": -8930.06, "average_credit_amount": 9691.59, "monthly_transactions": {"2023": {"3": {"month_transactions_count": 3, "debit_transactions_count": 2, "debit_transaction_month_avg": -9069.2, "credit_transactions_count": 1, "credit_transaction_month_avg": 7179.28}, "7": {"month_transactions_count": 2, "debit_transactions_count": 1, "debit_transaction_month_avg": -16967.9, "credit_transactions_count": 1, "credit_transaction_month_avg": 10493.08}, "6": {"month_transactions_count": 1, "debit_transactions_count": 0, "debit_transaction_month_avg": 0.0, "credit_transactions_count": 1, "credit_transaction_month_avg": 11613.07}, "5": {"month_transactions_count": 1, "debit_transactions_count": 0, "debit_transaction_month_avg": 0.0, "credit_transactions_count": 1, "credit_transaction_month_avg": 16192.81}, "2": {"month_transactions_count": 2, "debit_transactions_count": 2, "debit_transaction_month_avg": -4772.01, "credit_transactions_count": 0, "credit_transaction_month_avg": 0.0}, "8": {"month_transactions_count": 1, "debit_transactions_count": 0, "debit_transaction_month_avg": 0.0, "credit_transactions_count": 1, "credit_transaction_month_avg": 2979.73}}}}',
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "AWSTraceHeader": "Root=1-6524701c-52810e8e6639a1110b0c1312;Parent=21029c1e3bbac5f1;Sampled=0;Lineage=b07fc553:0",
                    "SentTimestamp": "1696886817196",
                    "SenderId": "AROAQF4THAGX3D2QFVPOZ:transactions_processor",
                    "ApproximateFirstReceiveTimestamp": "1696886822196",
                },
                "messageAttributes": {},
                "md5OfBody": "8525ff5751fe67faaa53bd8feeba980d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-west-2:012656771503:demo-email-notifications-queue",
                "awsRegion": "us-west-2",
            }
        ]
    }

    lambda_handler(event, {})
