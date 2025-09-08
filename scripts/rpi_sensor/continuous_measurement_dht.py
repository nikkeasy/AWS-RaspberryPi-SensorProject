import time
import board
import adafruit_dht
import json
from awscrt import mqtt5
from awsiot import mqtt5_client_builder

# --- Configuration (Plaeholder values) ---
ENDPOINT = "xxx-ats.iot.eu-north-1.amazonaws.com"
CLIENT_ID = "Raspberry_Device_1"
CERT_PATH = "../Raspberry_Device_1.cert.pem"
KEY_PATH = "../Raspberry_Device_1.private.key"
CA_PATH = "../root-CA.crt"
TOPIC = "Raspberry_Device_1/test"

# --- Sensor Setup (Using the working library) ---
# Use the pin number you used in the successful test (board.D4 is GPIO 4)
SENSOR_PIN = board.D4 
try:
    dht_device = adafruit_dht.DHT11(SENSOR_PIN)
except RuntimeError as error:
    print(f"Failed to initialize DHT11 sensor: {error.args[0]}")
    print("Please check sensor wiring and try again.")
    exit(1)
    
# --- Data Collection Setup ---
temp_readings = []
humidity_readings = []
READ_INTERVAL_SECONDS = 5
SAMPLES_PER_MINUTE = 60 // READ_INTERVAL_SECONDS # = 12 samples

# --- Main Application Logic ---
if __name__ == '__main__':
    print("Starting sensor monitoring and AWS IoT connection...")
    
    # --- AWS Connection ---
    client = mqtt5_client_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERT_PATH,
        pri_key_filepath=KEY_PATH,
        ca_filepath=CA_PATH,
        client_id=CLIENT_ID,
        on_lifecycle_connection_success=lambda event: print("Connection to AWS IoT Success!"),
        on_lifecycle_connection_failure=lambda event: print(f"Connection to AWS IoT Failure: {event.error_code}")
    )
    
    print(f"Connecting to {ENDPOINT} with client ID '{CLIENT_ID}'...")
    client.start()
    time.sleep(2) # Give a moment for the connection to establish

    # --- The Infinite Loop ---
    while True:
        try:
            # --- Read from sensor ---
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity

            if temperature_c is not None and humidity is not None:
                temp_readings.append(temperature_c)
                humidity_readings.append(humidity)
                print(f"Reading {len(temp_readings)}/{SAMPLES_PER_MINUTE}: Temp={temperature_c:.1f}C, Hum={humidity:.1f}%")

                # --- Check if we have 1 minute of data ---
                if len(temp_readings) >= SAMPLES_PER_MINUTE:
                    avg_temp = sum(temp_readings) / len(temp_readings)
                    avg_humidity = sum(humidity_readings) / len(humidity_readings)

                    message_payload = json.dumps({
                        "clientId": CLIENT_ID,
                        "timeStamp": int(time.time()),
                        "temperature": round(avg_temp, 2),
                        "humidity": round(avg_humidity, 2)
                    })

                    print("\n[PUBLISHING] Sending 1-minute average to AWS IoT...")
                    print(f"Payload: {message_payload}\n")

                    # --- Publish to AWS ---
                    client.publish(mqtt5.PublishPacket(
                        topic=TOPIC,
                        payload=message_payload,
                        qos=mqtt5.QoS.AT_LEAST_ONCE
                    ))

                    temp_readings.clear()
                    humidity_readings.clear()

            else:
                 print("Sensor returned no data. Retrying...")

        except RuntimeError as error:
            print(f"Sensor reading error: {error.args[0]}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

        time.sleep(READ_INTERVAL_SECONDS)

    print("Shutting down client.")
    client.stop()