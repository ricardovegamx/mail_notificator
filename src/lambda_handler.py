import json
import logging
import os

import boto3
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger()
logger.setLevel(logging.INFO)

month_names = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def lambda_handler(event, context):
    logging.info(f"event received: {event}")

    # process the incoming event
    message_body = event["Records"][0]["body"]
    account_report = json.loads(message_body)

    # set-up jinja2 to render the template
    env = Environment(loader=FileSystemLoader("./src"))
    template = env.get_template("email_template.html")
    data = {"account_report": account_report, "month_names": month_names}

    html_content = template.render(data)

    # prepare the SES client to send the email
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

    # If mail got sent, delete the sqs message as it's been processed
    sqs = boto3.client("sqs", region_name="us-west-2")
    queue_url = os.getenv("EMAIL_NOTIFICATIONS_QUEUE_URL")
    receipt_handle = event["Records"][0]["receiptHandle"]

    sqs_response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

    if sqs_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        logger.info(f"sqs message deleted successfully: {response['MessageId']}")
    else:
        logger.info(
            f"sqs msg returned HttpStatus: {sqs_response['ResponseMetadata']['HTTPStatusCode']}"
        )
