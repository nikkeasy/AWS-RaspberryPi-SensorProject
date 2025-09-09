import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SensorData')

def lambda_handler(event, context):
    """ 
    This lambda function calculates the weekly averages for temperature and humidity
    measured with Raspberry Pi 3B+ DHT 11 temp and humidity sensor and writes the 
    results back to the DynamoDB table.
    """ 

    # Configuration
    client_id_to_process = 'Raspberry_Device_1' # Raspberry Pi measuring device

    # 1. Calculate time range
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    # Convert days to epoch timestamps
    start_ts = int(seven_days_ago.timestamp())
    end_ts = int(now.timestamp())

    print(f"Fetching data for '{client_id_to_process}' from {seven_days_ago} to {now}")

    # 2. Query DynamoDB for RAW data 
    try:
        response = table.query(
            KeyConditionExpression='clientId = :cid AND #ts BETWEEN :start AND :end',
            ExpressionAttributeNames={'#ts': 'timeStamp'},
            ExpressionAttributeValues={':cid': client_id_to_process, ':start': start_ts, ':end': end_ts}
        )
        items = response.get('Items', [])

        if not items:
            print("No data found for the specified time range.")
            return {
                'statusCode': 200,
                'body': json.dumps('No data to process.')
            }

        # 3. Transform RAW data to weekly averages
        total_temp = sum(item['temperature'] for item in items)
        total_humidity = sum(item['humidity'] for item in items)
        item_count = len(items)

        avg_temp = total_temp / item_count
        avg_humidity = total_humidity / item_count

        print(f"Processed {item_count} items. Avg Temp: {avg_temp:.2f}, Avg Humidity: {avg_humidity:.2f}")

        # 4. Load transformed data into DynamoDB 
        table.put_item(
            Item={
                'clientId': f'{client_id_to_process}#WEEKLY_AVG',
                'timestamp': end_ts,
                'avg_temperature': Decimal(f'{avg_temp:.2f}'),
                'avg_humidity': Decimal(f'{avg_humidity:.2f}'),
                'processed_item_count': item_count
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Weekly averages calculated and stored successfully.')
        }

    except Exception as e:
        print(f"Error processing data: {e}")
        raise e