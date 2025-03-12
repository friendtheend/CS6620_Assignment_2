#driver

import json
import boto3
import time
import requests
from botocore.exceptions import ClientError


# Initialize S3 client
s3_client = boto3.client('s3', region_name='us-east-2')

# Environment variables
BUCKET_NAME = 'testbucket-cs6620-lef'
PLOTTING_API_URL = 'https://ftyoin29f1.execute-api.us-east-2.amazonaws.com/dev'
def lambda_handler(event, context):
    try:
        # Step 1: Create object 'assignment1.txt' with initial content
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key='assignment1.txt',
            Body='Empty Assignment 1'
        )
        print("Created 'assignment1.txt' with content: 'Empty Assignment 1'")

        # Wait
        time.sleep(1.5)

        # Step 2: Update 'assignment1.txt' with new content
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key='assignment1.txt',
            Body='Empty Assignment 2222222222'
        )
        print("Updated 'assignment1.txt' with content: 'Empty Assignment 2222222222'")

        # Wait
        time.sleep(1.5)

        # Step 3: Delete 'assignment1.txt'
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key='assignment1.txt'
        )
        print("Deleted 'assignment1.txt'")

        # Wait
        time.sleep(1.5)

        # Step 4: Create object 'assignment2.txt' with content "33"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key='assignment2.txt',
            Body='33'
        )
        print("Created 'assignment2.txt' with content: '33'")

        # Step 5: Wait and then call the plotting API
        time.sleep(1.5)
        response = requests.get(PLOTTING_API_URL)

        # Check if the plotting API call was successful
        if response.status_code == 200:
            print("Plotting API called successfully.")
        else:
            print(f"Plotting API call failed. Status Code: {response.status_code}, Response: {response.text}")

        return {
            'statusCode': 200,
            'body': json.dumps('Driver lambda executed successfully')
        }

    except ClientError as e:
        print(f"Error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {e}")
        }
    except requests.RequestException as e:
        print(f"Request error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error calling plotting API: {e}")
        }
