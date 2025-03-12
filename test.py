import boto3
import time
from datetime import datetime

# 连接 DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('S3-object-size-history')

# 插入 5 条数据
for i in range(5):
    timestamp = int(datetime.now().timestamp() * 1000)  # 毫秒级时间戳
    size = 100000 + (i * 50000)  # 递增大小
    table.put_item(
        Item={
            'bucket_name': 'testbucket-cs6620-lef',
            'timestamp': timestamp,
            'size': size
        }
    )
    print(f"Inserted: {timestamp}, size: {size}")
    time.sleep(2)  # 间隔 2 秒

# driver-role plotting-role size-tracking-role
#AmazonAPIGatewayInvokeFullAccess
#AmazonDynamoDBFullAccess
#AmazonS3FullAccess
#AWSLambdaBasicExecutionRole