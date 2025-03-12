# CS6620_Assignment_2

This project contains several components designed to manage and monitor the size of an S3 bucket (`testbucket-cs6620`) using AWS Lambda, S3, and DynamoDB. The implementation uses microservices, and each component has been developed to perform specific tasks related to S3 bucket monitoring and visualization.

## Components


1. **main.py**: This script automates various setup steps, including creating an S3 bucket, setting up a DynamoDB table, attaching IAM policies to roles, enabling event notifications for S3, and configuring Lambda functions.
   - **Step 1**: Create S3 bucket and DynamoDB table (`S3-object-size-history`).
   - **Step 2**: Attach IAM permissions to the Lambda roles (`driver`, `size_tracking`, and `plotting`).
   - **Step 3**: Enable S3 bucket event notifications to trigger the size-tracking Lambda for object creation, update, and deletion events.
   - **Step 4**: Update Lambda function settings (memory and timeout).
   - **Step 5**: Add Lambda layer for Matplotlib and requests library.

   If the code does not work, you can manually perform these steps using the AWS console.

2. **driver_lambda.py**: The driver Lambda function performs the following operations on the S3 bucket:
   - Creates an object (`assignment1.txt`) with specific content.
   - Updates the content of the object.
   - Deletes the object.
   - Creates another object (`assignment2.txt`) with different content.
   - This Lambda also calls the plotting Lambda after each operation to update the visual representation.

3. **size-tracking_lambda.py**: This Lambda function is triggered by S3 bucket events (create, update, delete) and calculates the total size of the bucket after each event. It records the bucket size, timestamp, and object count in the DynamoDB table.

4. **plotting_lambda.py**: This Lambda function queries the DynamoDB table to get the bucket size information over the last 10 seconds and plots the size change over time, including a line for the maximum historical size. The generated plot is saved as `plot.png` in the S3 bucket.

5. **plot.png**: The generated graph showing the bucket size changes in the last 10 seconds, along with a historical high marker.