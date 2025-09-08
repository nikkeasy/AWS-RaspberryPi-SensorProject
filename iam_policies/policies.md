

# AWS Service: **lambda**
    - calculateWeeklyAverages-role-sxxxx1
        - For calculating Weekly Averages of the measurements

# AWS Service: **IoT**
    - raspi-iot-to-cloudwatch-role
        - For logging
        - JSON:
        {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:eu-north-1:xxxyyy:log-group:/iot/rule-errors:*"
                ]
            }
        ]
    }


    - raspi-iot-to-dynamodb
        - For sending IoT data to DynamoDB
        - JSON: 
        {
        "Version": "2012-10-17",
        "Statement": {
            "Effect": "Allow",
            "Action": "dynamodb:PutItem",
            "Resource": "arn:aws:dynamodb:eu-north-1:xxxyyy:table/SensorData"
        }
    }