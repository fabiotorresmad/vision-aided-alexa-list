LAMBDA_FN="minimarket-alexa"

# Add alexa permissions to lambda function
aws lambda add-permission \
	--function-name ${LAMBDA_FN} \
	--statement-id alexa-permission \
	--action lambda:InvokeFunction \
	--principal alexa-appkit.amazon.com

# Pack lambda content
mkdir package
pip install --target ./package "ask-sdk-core>=1.10.2"
cd package
zip -r ../lambda.zip .
cd ..
zip lambda.zip hello_world.py

# Update lambda content
aws lambda update-function-code \
   --function-name ${LAMBDA_FN} \
   --zip-file fileb://lambda.zip
