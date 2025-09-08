# Raspberry Pi 3B+ DHT 11 sensor AWS data project  

I have a couple of spare Raspberry Pi's and modules lying around and haven't used them as much as I should've, which is a shame. I've previously done some small projects with them and after that left them to collect dust for months. This time however, I intend to keep this Raspberry Pi 3B+ continuously running for a longer time, measure real-time temperature and humidity data, and then send the data to AWS DynamoDB through AWS IoT. I can then use this data to hopefully make insights using visualizations.

I successfully did a similar project previously on Azure using their Free Trial + credits. In that project, I used the same Raspberry Pi which sent data to a Serverless SQL database. I didn't do any visualizations or anything fancy like that, just wanted to dive into Azure and experience its services firsthand. This project will be fancier.

I am aware that this is a simplified way of ingesting and loading data, but this is my first touchpoint with AWS. Having used Azure quite a lot, I have to say AWS shares a lot of similarities in logic, and it's easy to get started with what feels like a more intuitive and friendlier UI.  

## The Technology Stack

#### Hardware
*   **Raspberry Pi 3B+**
*   **DHT11** Temperature and Humidity sensor

#### Software & Libraries
*   **`adafruit-circuitpython-dht`**: The modern, maintained Python driver to access the DHT11 sensor.
*   **`awsiot-mqtt5-client`**: The official AWS library for MQTT, a lightweight protocol that does the communication between the Raspberry Pi and AWS IoT Core.
*   **`systemd`**: The robust, built-in Linux service manager for orchestrating the measurement script to run 24/7.

#### AWS Cloud Services
*   **AWS IoT Core**: Acts as the secure front door and message broker for the Raspberry Pi.
*   **AWS IoT Rule**: Processes incoming messages and routes them to other services.
*   **Amazon DynamoDB**: The fully managed NoSQL database for storing the sensor data.
*   **Amazon QuickSight**: The business intelligence service for visualizing the data in a dashboard.



## The Next Level: A Scalable Data Lake

When I've got this pipeline humming, I'm keen on exploring a more industry-standard, scalable data lake approach that utilizes services like **Kinesis Data Firehose**, **Amazon S3**, **AWS Glue**, and **Amazon Athena**.



---

## Project Diary

### **6.9.2025 - Setting up the environment, configs, and sensor readings**

I started my project by creating a free tier AWS account and firing up my pre-installed Raspberry Pi 3B+. My first goal was to test that the DHT11 sensor measures data correctly and then establish a secure connection between the Pi and AWS IoT Core.

#### Setting up the AWS IoT "Thing" and Certificates
After creating the free AWS account, I proceeded to create a "Thing" (Like in *Wednesday* :D), which is the virtual representation of my Raspberry Pi. The process was user-friendly with good step-by-step instructions, which was a nice change of pace. I downloaded a Connection Kit that contained a set of essential security credentials and transferred them to the Raspberry Pi using SFTP:

*   **Device Certificate (`.cert.pem`)**: The device's unique ID card.
*   **Private Key (`.private.key`)**: The device's secret key, its password to the cloud.
*   **Root Certificate Authority (`root-CA.crt`)**: The certificate that allows my Pi to verify it's talking to a genuine AWS server and not an impostor.

With the certs in place and the sensor reading data locally, the next step was to bridge the two worlds.





## 7.9.2025 - Transmitting sensor data to AWS, automation and Lambda functions  

Today was a huge success. I managed to get the continuous measurement data flowing from the Pi, through the IoT Core hub, and landing correctly in DynamoDB.

#### Key Learnings & Impressions:
*   **The Power of `boto3` & Lambda**: I started laying the groundwork for future data processing with Lambda functions to calculate daily, weekly, and monthly averages. The AWS SDK for Python, **boto3**, is a library of MAGNIFICENCE. The code editor within the Lambda console is also a standout feature—it's lightweight, and its intelligent autocompletion makes development a breeze. It really highlights the seamless integration within AWS, which can feel more complex on other platforms.

*   **DynamoDB's Dynamic Schema**: What's really cool about DynamoDB is its dynamic approach. It just takes the JSON payload and maps it to the database. If I decide to add a new sensor for air pressure tomorrow, I just add a `pressure` field to my JSON, and DynamoDB will automatically create a new attribute (column) for it. No migrations, no downtime. Brilliant.

*   **The Debugging Journey**: The final hurdle was data formatting. At first, my data was landing in DynamoDB as a single, messy JSON string instead of the clean columns I wanted. My initial suspect was the IoT Message Routing Rule. After some fiddling, the real breakthrough came when I used the AWS MQTT Test Client to bypass the Pi and send a "perfect" message. It worked flawlessly, proving my entire cloud setup was correct. The culprit was an old version of my script still running on the Pi. A classic "turn it off and on again" moment!

#### Making it Robust: The Final `systemd` Service
To make this a true, hands-off project, the script can't just run in a PuTTY session. For it to run robustly and be fail-proof, I configured it as a `systemd` service. This is the proper way to do it on Linux. It ensures the script starts automatically when the Pi boots up and, more importantly, restarts itself if it ever crashes.

1.  **A Service File was Created**: At `/etc/systemd/system/sensor.service`, I created a configuration file.

2.  **The Configuration**: This file tells the OS exactly how to run, manage, and restart my script, using the Python interpreter from my project's dedicated virtual environment (`.venv`).

    ```ini
    [Unit]
    Description=DHT11 Sensor Data Logger for AWS IoT
    After=network.target

    [Service]
    User=testuser01
    WorkingDirectory=/home/testuser01/aws_sensor_project
    ExecStart=/home/testuser01/aws_sensor_project/.venv/bin/python3 /home/testuser01/aws_sensor_project/final_aws_sensor.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

After running `sudo systemctl enable --now sensor.service`, the job was done. The Pi is now officially on duty, 24/7. I can shut down my main computer and walk away. 

Nikolas out. 

### 8.9.2025 Creating a Public Git Repo and fixing Lambda average functions

#### Organizing files and creating placeholder values

Organized working directory and added only files which are of relevance for this AWS project. Created remote repo and pushed local files there. 

#### Lambda Weekly Average function

I unfortunately noticed that my weekly average function is not yet working but I plan to fix it tomorrow. Out of time for today...

