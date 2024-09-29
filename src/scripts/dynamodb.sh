# Create DynamoDB table
aws dynamodb create-table \
	--table-name ProductsList \
	--attribute-definitions AttributeName=ProductName,AttributeType=S \
	--key-schema AttributeName=ProductName,KeyType=HASH \
	--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Put some item
aws dynamodb put-item \
	--table-name ProductsList \
	--item '{
    	"ProductName": {"S": "milk"},
    	"Brand": {"S": "piracanjuba"},
    	"Quantity": {"N": "2"},
    	"Category": {"S": "Dairy"}
	}'

# Read items of table ProductsList in DynamoDB
aws dynamodb scan --table-name ProductsList
