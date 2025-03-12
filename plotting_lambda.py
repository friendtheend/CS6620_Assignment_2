#plotting

import json
import boto3
import os
import io
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

# Initialize DynamoDB and S3 clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
s3_client = boto3.client('s3', region_name='us-east-2')

# Environment variables for Lambda
DYNAMODB_TABLE_NAME = 'S3-object-size-history'
BUCKET_NAME = 'testbucket-cs6620-lef'

def lambda_handler(event, context):
    try:
        # 获取当前时间戳（毫秒级）
        current_timestamp = int(datetime.now().timestamp() * 1000)
        start_timestamp = current_timestamp - (10 * 1000)  # 10 秒前

        print(f"Current timestamp (ms): {current_timestamp}")
        print(f"Start timestamp (ms): {start_timestamp}")

        # 查询 DynamoDB 过去 10 秒的数据
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        response = table.scan(
            FilterExpression=Attr('bucket_name').eq(BUCKET_NAME) & Attr('timestamp').between(start_timestamp, current_timestamp)
        )

        items = response.get('Items', [])
        print(f"Queried {len(items)} items from DynamoDB.")

        if not items:
            print("No data available in the last 10 seconds.")
            return {
                'statusCode': 404,
                'body': json.dumps('No data available in the last 10 seconds.')
            }

        # 提取时间戳和 S3 Bucket 大小
        timestamps = [int(item['timestamp']) for item in items]
        sizes = [float(item['size']) for item in items]

        # 计算相对时间（转换为秒）
        relative_times = [-(current_timestamp - ts) / 1000 for ts in timestamps]

        # **打印数据，检查是否为空**
        print("Timestamps:", timestamps)
        print("Relative times:", relative_times)
        print("Sizes:", sizes)

        # 查询历史最大值
        response_max = table.scan(
            FilterExpression=Key('bucket_name').eq(BUCKET_NAME)
        )
        max_size = max(float(item['size']) for item in response_max.get('Items', [])) if response_max.get('Items') else 0

        print(f"Historical max size: {max_size}")

        # 创建图表
        plt.figure(figsize=(10, 6))
        plt.plot(relative_times, sizes, label='Bucket Size (Last 10 seconds)', color='b')
        plt.axhline(y=max_size, color='r', linestyle='--', label='Historical High')
        plt.xlim(-10, 0)
        plt.xlabel('Relative Time (seconds)')
        plt.ylabel('Size (Bytes)')
        plt.title('S3 Bucket Size Change in Last 10 Seconds')
        plt.xticks(rotation=45)
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()

        # 保存图表到 buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # 上传图表到 S3
        s3_key = 'plot.png'
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=buffer, ContentType='image/png')

        print(f"Plot successfully generated and stored in s3://{BUCKET_NAME}/{s3_key}")

        return {
            'statusCode': 200,
            'body': json.dumps(f'Plot successfully generated and stored in s3://{BUCKET_NAME}/{s3_key}')
        }

    except ClientError as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {e}")
        }
