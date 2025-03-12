import boto3
from botocore.exceptions import ClientError
import json
import time

# Initialize clients for IAM, Lambda, S3, and DynamoDB
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda', region_name='us-east-2')
s3_client = boto3.client('s3', region_name='us-east-2')
dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-2')

# Role and Lambda details
ROLE_ARNS = {
    'driver': 'arn:aws:iam::783764596465:role/driver-role',
    'size_tracking': 'arn:aws:iam::783764596465:role/size-tracking-role',
    'plotting': 'arn:aws:iam::783764596465:role/plotting-role'
}
LAMBDA_NAMES = {
    'driver': 'arn:aws:lambda:us-east-2:783764596465:function:driver',
    'size_tracking': 'arn:aws:lambda:us-east-2:783764596465:function:size-tracking',
    'plotting': 'arn:aws:lambda:us-east-2:783764596465:function:plotting'
}

# Step 1: Create S3 Bucket and DynamoDB Table
# Create an S3 bucket
def create_s3_bucket(bucket_name):
    try:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
        print(f"✅ Bucket '{bucket_name}' created successfully.")
    except ClientError as e:
        print(f"❌ Error creating bucket: {e}")

# Create a DynamoDB table named 'S3-object-size-history'
def create_dynamodb_table(table_name):
    try:
        table = dynamodb_resource.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'bucket_name',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'bucket_name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'size',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'BucketSizeIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'bucket_name',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'size',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ]
        )
        print(f"✅ Table '{table_name}' is creating...")
        table.wait_until_exists()
        print(f"✅ Table '{table_name}' created successfully.")
    except ClientError as e:
        print(f"❌ Error creating table: {e}")

s3_bucket_name = 'testbucket-cs6620-lef'
dynamodb_table_name = 'S3-object-size-history'


# Create S3 bucket
create_s3_bucket(s3_bucket_name)

# Create DynamoDB table
create_dynamodb_table(dynamodb_table_name)


# import boto3
# from botocore.exceptions import ClientError
#
#
#
# # Initialize clients for IAM, Lambda, S3, and DynamoDB
# iam_client = boto3.client('iam')
# lambda_client = boto3.client('lambda', region_name='us-east-2')
# s3_client = boto3.client('s3', region_name='us-east-2')
# dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-2')
#
# # Role and Lambda details
# ROLE_ARNS = {
#     'driver': 'arn:aws:iam::783764596465:role/driver-role',
#     'size_tracking': 'arn:aws:iam::783764596465:role/size-tracking-role',
#     'plotting': 'arn:aws:iam::783764596465:role/plotting-role'
# }
# LAMBDA_NAMES = {
#     'driver': 'arn:aws:lambda:us-east-2:783764596465:function:driver',
#     'size_tracking': 'arn:aws:lambda:us-east-2:783764596465:function:size-tracking',
#     'plotting': 'arn:aws:lambda:us-east-2:783764596465:function:plotting'
# }
#
# # Step 1: Create S3 Bucket and DynamoDB Table
# # Create an S3 bucket named 'testbucket-cs6620'
# def create_s3_bucket(bucket_name):
#     try:
#         s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
#         print(f"Bucket '{bucket_name}' created successfully.")
#     except ClientError as e:
#         print(f"Error creating bucket: {e}")
#
# # Create a DynamoDB table named 'S3-object-size-history'
# def create_dynamodb_table(table_name):
#     try:
#         table = dynamodb_resource.create_table(
#             TableName=table_name,
#             KeySchema=[
#                 {
#                     'AttributeName': 'bucket_name',
#                     'KeyType': 'HASH'  # Partition key
#                 },
#                 {
#                     'AttributeName': 'timestamp',
#                     'KeyType': 'RANGE'  # Sort key
#                 }
#             ],
#             AttributeDefinitions=[
#                 {
#                     'AttributeName': 'bucket_name',
#                     'AttributeType': 'S'
#                 },
#                 {
#                     'AttributeName': 'timestamp',
#                     'AttributeType': 'N'
#                 },
#                 {
#                     'AttributeName': 'size',
#                     'AttributeType': 'N'
#                 }
#             ],
#             ProvisionedThroughput={
#                 'ReadCapacityUnits': 5,
#                 'WriteCapacityUnits': 5
#             },
#             GlobalSecondaryIndexes=[
#                 {
#                     'IndexName': 'BucketSizeIndex',
#                     'KeySchema': [
#                         {
#                             'AttributeName': 'bucket_name',
#                             'KeyType': 'HASH'
#                         },
#                         {
#                             'AttributeName': 'size',
#                             'KeyType': 'RANGE'
#                         }
#                     ],
#                     'Projection': {
#                         'ProjectionType': 'ALL'
#                     },
#                     'ProvisionedThroughput': {
#                         'ReadCapacityUnits': 5,
#                         'WriteCapacityUnits': 5
#                     }
#                 }
#             ]
#         )
#         print(f"Table '{table_name}' is being created...")
#         table.wait_until_exists()
#         print(f"Table '{table_name}' created successfully.")
#     except ClientError as e:
#         print(f"Error creating table: {e}")
#
# s3_bucket_name = 'testbucket-cs6620-lef'
# dynamodb_table_name = 'S3-object-size-history'
#
# # Create S3 bucket
# create_s3_bucket(s3_bucket_name)
#
# # Create DynamoDB table
# create_dynamodb_table(dynamodb_table_name)