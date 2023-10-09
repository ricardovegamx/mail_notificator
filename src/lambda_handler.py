import json
import logging

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logging.info(f"event received: {event}")

    message_body = event["Records"][0]["body"]
    message_data = json.loads(message_body)

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("email_template.html")

    html_content = template.render(message_data)
    print(html_content)

    # send the email

    # if sent email, delete the message from the queue
