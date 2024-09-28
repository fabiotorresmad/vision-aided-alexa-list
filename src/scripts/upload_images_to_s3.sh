# Create a S3 bucket named pd-datasets
aws s3api create-bucket --bucket products-detector-datasets --region us-east-1
# Create two folders in the bucket named test and train
aws s3api put-object --bucket products-detector-datasets --key test/
aws s3api put-object --bucket products-detector-datasets --key train/
# sync datasets to the bucket
aws s3 sync datasets/test s3://products-detector-datasets/test
aws s3 sync datasets/train s3://products-detector-datasets/train
