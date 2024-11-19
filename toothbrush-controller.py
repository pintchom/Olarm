# TOOTHBRUSH - CONTROLLER
# toothbrush-controller.py
# Max Pintchouk
import board, time
import wifi
import socketpool
import adafruit_requests
import os
import wifi
from adafruit_httpserver import Server, Request, Response
import supervisor

HOST_URL = "http://10.20.77.240/"
def request_alarm():
    print("Requesting alarm")
    try:
        requests = adafruit_requests.Session(pool)
        response = requests.get(HOST_URL + "play")

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

def setup_server():
    try:
        pool = socketpool.SocketPool(wifi.radio)
        server = Server(pool, "/static", debug=True)

        @server.route("/")
        def base(request: Request):
            print("Received request to root")
            return Response(request, "Server is running!")

        @server.route("/gather-time")
        def play_route(request: Request, methods=["GET"]):
            print("Recieving time")
            return Response(request, "Sound played!")
        return server
    except Exception as e:
        print(f"Server setup failed: {e}")
        return None

def run_server():
    if not connect_to_wifi():
        print("Failed to connect to WiFi after multiple attempts")
        supervisor.reload()
        return

    server = setup_server()
    if not server:
        print("Failed to setup server")
        supervisor.reload()
        return

    try:
        print("Starting server...")
        server.start(port=80)
        print(f"Server is running on http://{wifi.radio.ipv4_address}")
        print("Available routes:")
        print(f"  http://{wifi.radio.ipv4_address}/")
        print(f"  http://{wifi.radio.ipv4_address}/gather-time")

        while True:
            server.poll()
            time.sleep(0.1)
    except Exception as e:
        print(f"Server error: {e}")
        supervisor.reload()

run_server()
