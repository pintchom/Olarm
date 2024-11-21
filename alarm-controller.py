# ALARM-CONTROLLER
# alarm-controller.py
# Max Pintchouk
import board
import os
import time
import wifi
import socketpool
import supervisor
from adafruit_httpserver import Server, Request, Response
import adafruit_requests

################################################################################################################
''' Audio setup '''
from audiopwmio import PWMAudioOut as AudioOut
from audiocore import WaveFile
audio = AudioOut(board.GP15)
################################################################################################################
'''Constants'''
RECIEVER_URL = "http://10.20.69.162/"
pool = None
################################################################################################################

def send_alarm_time():
    print("Requesting alarm")
    try:
        requests = adafruit_requests.Session(pool)
        response = requests.get(RECIEVER_URL + "gather-time")
        print("Response status code:", response.status_code)
        print("Response text:", response.text)

        response.close()
        return response.text

    except Exception as e:
        print("Error making request:", str(e))
        return None

################################################################################################################
'''Function to play sound'''
def play_sound():
    print("PLAYING SOUND")
    try:
        with open("siren.wav", "rb") as wave_file:
            wave = WaveFile(wave_file)
            audio.play(wave)
            while audio.playing:
                pass
    except Exception as e:
        print(f"Error playing sound: {e}")
################################################################################################################


def connect_to_wifi():
    global pool
    max_attempts = 3
    attempt = 0
    
    # Print WiFi credentials for debugging
    print(f"Attempting to connect with SSID: {os.getenv('WIFI_SSID')}")
    
    while attempt < max_attempts:
        try:
            print(f"Connecting to WiFi (attempt {attempt + 1})...")
            wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
            print(f"Connected! IP: {wifi.radio.ipv4_address}")
            pool = socketpool.SocketPool(wifi.radio)
            # Test network connectivity
            requests = adafruit_requests.Session(pool)
            test_response = requests.get("http://google.com")
            test_response.close()
            print("Network connectivity confirmed")
            return True
        except Exception as e:
            print(f"WiFi connection failed: {str(e)}")
            attempt += 1
            time.sleep(2)
    return False

def setup_server():
    try:
        global pool  # Use the global pool instead of creating a new one
        if pool is None:
            print("Error: Socket pool not initialized")
            return None
            
        server = Server(pool, "/static", debug=True)
        print("Server object created successfully")

        @server.route("/")
        def base(request: Request):
            print("Received request to root")
            return Response(request, "Server is running!")

        @server.route("/play")
        def play_route(request: Request):
            print("Received request to play sound")
            play_sound()
            print("Finished playing sound")
            return Response(request, "Sound played!")

        print("Routes configured successfully")
        return server
    except Exception as e:
        print(f"Server setup failed: {str(e)}")
        return None

def run_server():
    print("Starting server initialization...")
    
    # Connect to WiFi
    if not connect_to_wifi():
        print("Failed to connect to WiFi after multiple attempts")
        time.sleep(5)  # Wait before reloading
        supervisor.reload()
        return

    server = setup_server()
    if not server:
        print("Failed to setup server")
        time.sleep(5)  # Wait before reloading
        supervisor.reload()
        return

    try:
        print("Starting server...")
        server.start(port=80)
        print(f"Server is running on http://{wifi.radio.ipv4_address}")
        print("Available routes:")
        print(f"  http://{wifi.radio.ipv4_address}/")
        print(f"  http://{wifi.radio.ipv4_address}/play")

        while True:
            try:
                server.poll()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in server poll: {str(e)}")
                time.sleep(1)  # Brief pause before continuing
                
    except Exception as e:
        print(f"Critical server error: {str(e)}")
        time.sleep(5)  # Wait before reloading
        supervisor.reload()

# Add startup delay to ensure board is fully initialized
time.sleep(2)
print("Starting alarm controller...")
run_server()