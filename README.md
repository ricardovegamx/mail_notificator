# MAIL NOTIFICATOR LAMBDA

This microservice sends and email to the user with the information of his/her account overview and transactions.

- This microservice is intended to be ran as a lambda function.
- It is triggered by a SQS queue event.
- A Makefile is provided to make deploy operations faster (when working locally).

## WORKFLOW

1. The lambda function is triggered by a SQS queue event.
2. The lambda function gets the message from the queue.
3. The lambda function uses jinja to render the email template.
4. The lambda function sends the email to the user using AWS SES.
5. The lambda function deletes the sqs message from the queue.

## ABOUT SQS QUEUE

The delivery of the messages has a 5-second delay to prevent the limits of the AWS SES service (in sandbox) and MaildropCC (public inbox service).

**IMPORTANT. MAILS WILL BE DELIVERED IN: [https://maildrop.cc/inbox/?mailbox=rick-vega-reports-inbox](https://maildrop.cc/inbox/?mailbox=rick-vega-reports-inbox)**

## REQUIREMENTS

- Python 3.11
- AWS CLI
- The following environment variables must be set:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_DEFAULT_REGION`
  - `AWS_ACCOUNT_ID`
  - `EMAIL_NOTIFICATIONS_QUEUE_URL`

## DEPLOYMENT

1. Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

2. Create the Layer that the lambda will use:

```bash
make create-layer
```

3. Create the lambda function:

```bash 
make create-lambda
```

4. Upgrate the lambda function (whenever you make changes to the code):

```bash
make update-lambda
```

5. [OPTIONAL] Delete lambda function:
   
```bash
make delete-lambda
```

## CODE STYLE

Use `make lint` to format the code style to sensible defaults.