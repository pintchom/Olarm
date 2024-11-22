# TOOTHBRUSH - CONTROLLER
# toothbrush-controller.py
# Max Pintchouk
import board, time, digitalio
from adafruit_debouncer import Button
import wifi
import socketpool
import adafruit_requests
import os
import wifi
from adafruit_httpserver import Server, Request, Response
import supervisor

door_sensor = digitalio.DigitalInOut(board.GP14)
door_sensor.switch_to_input(pull=digitalio.Pull.UP)

HOST_URL = "http://10.20.81.170/"
def request_stop_alarm():
    print("Requesting stop alarm")
    try:
        requests = adafruit_requests.Session(pool)
        response = requests.get(HOST_URL + "stop-alarm")

        print("Response status code:", response.status_code)
        print("Response text:", response.text)

        response.close()
        return response.text

    except Exception as e:
        print("Error making request:", str(e))
        return None


pool = None
time_to_detonate = None
def connect_to_wifi():
    global pool
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        try:
            print(f"Connecting to WiFi (attempt {attempt + 1})...")
            wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
            print(f"Connected! IP: {wifi.radio.ipv4_address}")
            pool = socketpool.SocketPool(wifi.radio)
            return True
        except Exception as e:
            print(f"WiFi connection failed: {e}")
            attempt += 1
            time.sleep(2)
    return False

connect_to_wifi()
while True:
    if door_sensor.value:
        print("Detected magnet")
        request_stop_alarm()
