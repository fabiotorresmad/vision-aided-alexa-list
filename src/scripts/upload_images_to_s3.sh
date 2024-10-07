export BUCKET_NAME="minimarket-ds"
# Create a S3 bucket named pd-datasets
aws s3api create-bucket --bucket ${BUCKET_NAME} --region us-east-1
# Create two folders in the bucket named test and train
aws s3api put-object --bucket ${BUCKET_NAME} --key test/
aws s3api put-object --bucket ${BUCKET_NAME} --key train/
# sync datasets to the bucket
aws s3 sync datasets/test s3://${BUCKET_NAME}/test
aws s3 sync datasets/train s3://${BUCKET_NAME}/train
