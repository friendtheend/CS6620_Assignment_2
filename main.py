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
        print(f"✅ Table '{table_name}' is being created...")
        table.wait_until_exists()
        print(f"✅ Table '{table_name}' created successfully.")
    except ClientError as e:
        print(f"❌ Error creating table: {e}")

s3_bucket_name = 'testbucket-cs6620-lef'
dynamodb_table_name = 'S3-object-size-history'


# Create S3 bucket
#create_s3_bucket(s3_bucket_name)

# Create DynamoDB table
#create_dynamodb_table(dynamodb_table_name)

# Step 2: Attach Permissions to Roles
# Adding S3, DynamoDB permissions to driver, size-tracking, and plotting roles
policies = {
    'driver': {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::testbucket-cs6620-lef",
                    "arn:aws:s3:::testbucket-cs6620-lef/*"
                ]
            }
        ]
    },
    'size_tracking': {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::testbucket-cs6620-lef",
                    "arn:aws:s3:::testbucket-cs6620-lef/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query"
                ],
                "Resource": "arn:aws:dynamodb:us-east-2:783764596465:table/S3-object-size-history"
            }
        ]
    },
    'plotting': {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:Query"
                ],
                "Resource": [
                    "arn:aws:dynamodb:us-east-2:783764596465:table/S3-object-size-history",
                    "arn:aws:dynamodb:us-east-2:783764596465:table/S3-object-size-history/index/BucketSizeIndex"
                ]
            },
            {
                "Effect": "Allow",
                "Action": "s3:PutObject",
                "Resource": "arn:aws:s3:::testbucket-cs6620-lef/plot.png"
            }
        ]
    }
}

for role, policy in policies.items():
    try:
        iam_client.put_role_policy(
            RoleName=ROLE_ARNS[role].split('/')[-1],
            PolicyName=f'{role.capitalize()}AccessPolicy',
            PolicyDocument=json.dumps(policy)
        )
        print(f"✅ Permissions added to {role} role successfully.")
    except ClientError as e:
        print(f"❌ Error attaching policy to {role} role: {e}")

# Step 3: Enable S3 Bucket Event Notifications to Trigger Size Tracking Lambda
# def enable_s3_event_notification(bucket_name, lambda_arn):
#     notification_configuration = {
#         'LambdaFunctionConfigurations': [
#             {
#                 'LambdaFunctionArn': lambda_arn,
#                 'Events': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*', 's3:ObjectRestore:Post']
#             }
#         ]
#     }
#     try:
#         s3_client.put_bucket_notification_configuration(
#             Bucket=bucket_name,
#             NotificationConfiguration=notification_configuration
#         )
#         print(f"Event notifications configured for bucket '{bucket_name}' to trigger Lambda '{lambda_arn}'.")
#     except ClientError as e:
#         print(f"Error setting bucket notifications: {e}")
#
# # Enable event notifications
# enable_s3_event_notification('testbucket-cs6620-lef', LAMBDA_NAMES['size_tracking'])
def add_lambda_permission(lambda_name, bucket_name):
    try:
        lambda_client.add_permission(
            FunctionName=lambda_name,
            StatementId=f'AllowS3Invoke-{bucket_name}',
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=f'arn:aws:s3:::{bucket_name}'
        )
        print(f"✅ Permission is added，allow S3'{bucket_name}'use Lambda'{lambda_name}'")
    except ClientError as e:
        if 'already exists' in str(e):
            print(f"✅ Permission is added, allow S3'{bucket_name}'use Lambda'{lambda_name}'")
        else:
            print(f"❌ Something went wrong when adding permission: {e}")

def enable_s3_event_notification(bucket_name, lambda_arn, lambda_name):
    # 首先添加权限，允许S3调用Lambda
    add_lambda_permission(lambda_name, bucket_name)

    # 然后设置通知
    notification_configuration = {
        'LambdaFunctionConfigurations': [
            {
                'LambdaFunctionArn': lambda_arn,
                'Events': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*', 's3:ObjectRestore:Post']
            }
        ]
    }
    try:
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration=notification_configuration
        )
        print(f"✅ Successfully configured event notification for bucket '{bucket_name}' to trigger Lambda '{lambda_arn}'.")
    except ClientError as e:
        print(f"❌ Error occurred while setting up bucket notification: {e}")

# 启用事件通知
lambda_name = 'size_tracking'
lambda_arn = 'arn:aws:lambda:us-east-2:783764596465:function:size_tracking'


enable_s3_event_notification('testbucket-cs6620-lef', lambda_arn, lambda_name)

# Step 4: Update Lambda Timeout and Memory Settings
# def update_lambda_settings(lambda_arn, timeout=30, memory_size=512):
#     try:
#         lambda_client.update_function_configuration(
#             FunctionName=lambda_arn,
#             Timeout=timeout,
#             MemorySize=memory_size
#         )
#         print(f"Updated Lambda '{lambda_arn}' with timeout={timeout}s and memory size={memory_size}MB.")
#     except ClientError as e:
#         print(f"Error updating Lambda configuration: {e}")
#
# # Update settings for plotting Lambda
# update_lambda_settings(LAMBDA_NAMES['plotting'], timeout=30, memory_size=512)
# update_lambda_settings(LAMBDA_NAMES['driver'], timeout=15, memory_size=512)
#
# # Step 5: Add Lambda Layer for Matplotlib
#
# def add_lambda_layer(lambda_arn, layer_arn):
#     try:
#         lambda_client.update_function_configuration(
#             FunctionName=lambda_arn,
#             Layers=[layer_arn]
#         )
#         print(f"Added layer '{layer_arn}' to Lambda '{lambda_arn}'.")
#     except ClientError as e:
#         print(f"Error adding layer to Lambda: {e}")
#
# # Assume we already created a Lambda Layer for matplotlib and got the ARN
# MATPLOTLIB_LAYER_ARN = 'arn:aws:lambda:us-east-2:783764596465:layer:matplotlib-layer:1'
# REQUESTS_LAYER_ARN = 'arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p311-requests:12'
#
# # Add layer to plotting Lambda
# add_lambda_layer(LAMBDA_NAMES['plotting'], MATPLOTLIB_LAYER_ARN)
# add_lambda_layer(LAMBDA_NAMES['driver'], REQUESTS_LAYER_ARN)
import boto3
import time
from botocore.exceptions import ClientError

lambda_client = boto3.client('lambda', region_name='us-east-2')

def wait_for_lambda_update(lambda_name):
    """等待 Lambda 更新完成"""
    print(f"⏳ Waiting for Lambda {lambda_name} updating...")
    waiter = lambda_client.get_waiter('function_updated')
    try:
        # 使用AWS内置的waiter来等待函数更新完成
        waiter.wait(FunctionName=lambda_name)
        print(f"✅ Lambda {lambda_name} now is activated")
        return True
    except Exception as e:
        print(f"❌ Error occurred while waiting for updating Lambda configuration: {e}")
        return False

def update_lambda_settings(lambda_name, timeout, memory_size):
    """更新 Lambda 配置"""
    # 确保使用函数名而不是ARN
    function_name = lambda_name.split(":")[-1] if ":" in lambda_name else lambda_name

    try:
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Timeout=timeout,
            MemorySize=memory_size
        )
        print(f"⏳ Updating Lambda '{function_name}' : timeout={timeout}s, memory={memory_size}MB...")

        # 等待此更新完成
        if wait_for_lambda_update(function_name):
            print(f"✅ Successfully updated Lambda '{function_name}' configuration.")
        else:
            print(f"❌ Unable to confirm the update status of Lambda '{function_name}'")
    except ClientError as e:
        print(f"❌ Error occurred while updating Lambda configuration: {e}")

def wait_for_lambda_update(lambda_name, max_retries=10, delay=5):
    """
    Wait for Lambda function update to complete before making changes.
    """
    for attempt in range(max_retries):
        try:
            response = lambda_client.get_function_configuration(FunctionName=lambda_name)
            status = response.get("LastUpdateStatus")

            if status == "Successful":
                print(f"✅ Lambda '{lambda_name}' update completed. Proceeding with changes.")
                return True
            elif status == "Failed":
                print(f"❌ Lambda '{lambda_name}' last update failed. Check CloudWatch logs for details.")
                return False

            print(f"⏳ Lambda '{lambda_name}' is still updating... Waiting {delay} seconds ({attempt + 1}/{max_retries})")
            time.sleep(delay)

        except ClientError as e:
            print(f"❌ Error fetching Lambda configuration: {e}")
            return False

    print(f"❌ Lambda '{lambda_name}' did not complete updating within the expected time. Skipping changes.")
    return False


def add_lambda_layer(lambda_name, layer_arn):
    """
    Add a new layer to the Lambda function if it does not already exist.
    Wait for updates to complete before modifying configuration.
    """
    try:
        # Fetch current Lambda configuration
        response = lambda_client.get_function_configuration(FunctionName=lambda_name)

        # Get existing layers
        existing_layers = response.get("Layers", [])
        existing_layer_arns = [layer["Arn"] for layer in existing_layers]

        # Check if the layer is already present
        if layer_arn in existing_layer_arns:
            print(f"⚠️ Layer '{layer_arn}' already exists in Lambda '{lambda_name}'. Skipping...")
            return

        # Wait for Lambda to be in a modifiable state
        if not wait_for_lambda_update(lambda_name):
            print(f"❌ Lambda '{lambda_name}' is not in a modifiable state. Skipping layer addition.")
            return

        # Add the new layer
        updated_layers = existing_layer_arns + [layer_arn]

        # Update Lambda function configuration
        lambda_client.update_function_configuration(
            FunctionName=lambda_name,
            Layers=updated_layers
        )
        print(f"✅ Successfully added layer '{layer_arn}' to Lambda '{lambda_name}'.")

    except ClientError as e:
        if "ResourceConflictException" in str(e):
            print(f"⚠️ Lambda '{lambda_name}' is currently updating. Retrying in 5 seconds...")
            time.sleep(5)  # Wait and retry
            add_lambda_layer(lambda_name, layer_arn)  # Recursive retry
        else:
            print(f"❌ Error adding layer to Lambda '{lambda_name}': {e}")



# Assume we already created a Lambda Layer for matplotlib and got the ARN
# MATPLOTLIB_LAYER_ARN = 'arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p311-matplotlib:14'
REQUESTS_LAYER_ARN = 'arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p311-requests:15'
MATPLOTLIB_LAYER_ARN = 'arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p311-matplotlib:16'
NUMPY_LAYER_ARN = 'arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p311-numpy:14'

# 更新 Lambda 超时 & 内存
update_lambda_settings("plotting", timeout=30, memory_size=512)
# 等待一下确保上一个操作完成
time.sleep(5)
update_lambda_settings("driver", timeout=59, memory_size=512)
# 等待一下确保上一个操作完成
time.sleep(5)

# 添加 Layer，确保 Lambda 处于 "Active" 状态
add_lambda_layer(LAMBDA_NAMES['plotting'], MATPLOTLIB_LAYER_ARN)
add_lambda_layer(LAMBDA_NAMES['driver'], REQUESTS_LAYER_ARN)
add_lambda_layer(LAMBDA_NAMES['plotting'], NUMPY_LAYER_ARN)

#Step 6: add API Gateway to the plotting Lambda