lint:
	autoflake --in-place --recursive --imports=missing ./src
	autoflake --in-place --remove-all-unused-imports --recursive ./src
	isort --profile black ./src
	black --line-length 100 --target-version py311 ./src
	flake8 ./src --max-line-length=100

deploy-layer:
	mkdir -p layer/python
	pip install -r requirements.txt -t layer/python
	cd layer && zip -r ../layer.zip .
	aws lambda publish-layer-version --layer-name mail_notificator_dependencies --zip-file fileb://layer.zip --compatible-runtimes python3.11
	rm -rf layer/python
	rm layer.zip

create-lambda:
	zip -r lambda_handler.zip src/lambda_handler.py src/email_template.html
	aws lambda create-function --function-name mail_notificator --runtime python3.11 --role arn:aws:iam::012656771503:role/lambda-ex --handler src.lambda_handler.lambda_handler --layers arn:aws:lambda:us-west-2:012656771503:layer:mail_notificator_dependencies:1 --zip-file fileb://lambda_handler.zip \
	--memory-size 512 --timeout 30 \
	--environment Variables="{EMAIL_NOTIFICATIONS_QUEUE_URL=${EMAIL_NOTIFICATIONS_QUEUE_URL}}"
	rm lambda_handler.zip

update-lambda:
	zip -r lambda_handler.zip src/lambda_handler.py src/email_template.html
	aws lambda update-function-code --function-name mail_notificator --zip-file fileb://lambda_handler.zip
	rm lambda_handler.zip

delete-lambda:
	aws lambda delete-function --function-name mail_notificator