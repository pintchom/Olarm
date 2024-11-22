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
import rtc
import circuitpython_schedule as schedule
import ssl

################################################################################################################
'''Constants'''
RECIEVER_URL = "http://10.20.69.162/"
pool = None
requests = None
server = None
################################################################################################################
''' TIMER setup '''
alarm_times = ["10:48:00"]  # Added seconds for more precise timing
clock = rtc.RTC()
url = "http://worldtimeapi.org/api/timezone/"  # Changed to http instead of https
timezone = "America/New_York"
url = url + timezone
alarm_active = False
last_alarm_time = None  # Track when the last alarm was triggered

def get_time():
    print(f"Accessing url: {url}")
    response = requests.get(url)

    # convert response into json
    json = response.json()

    # parse out values that we want
    unixtime = json["unixtime"]
    raw_offset = json["raw_offset"]

    # create the local time in seconds
    location_time = unixtime + raw_offset

    # turn seconds into time components
    current_time = time.localtime(location_time)

    # format and print time & date
    printable_time = f"{current_time.tm_hour:d}:{current_time.tm_min:02d}:{current_time.tm_sec:02d}"
    printable_date = f"{current_time.tm_mon:d}/{current_time.tm_mday:d}/{current_time.tm_year:02d}"
    print(f"printable_time: {printable_time}")
    print(f"printable_date: {printable_date}")

    # set the rtc with the component time in current_time
    clock.datetime = time.struct_time(current_time)

def check_alarm():
    global last_alarm_time
    current = time.localtime()
    current_time = f"{current.tm_hour}:{current.tm_min:02d}:{current.tm_sec:02d}"
    
    if (current_time in alarm_times and 
        not alarm_active and 
        last_alarm_time != current_time):
        last_alarm_time = current_time
        play_sound()

################################################################################################################
''' Audio setup '''
from audiopwmio import PWMAudioOut as AudioOut
from audiocore import WaveFile
audio = AudioOut(board.GP15)


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
    global alarm_active
    print("PLAYING SOUND")
    try:
        alarm_active = True
        with open("siren.wav", "rb") as wave_file:
            wave = WaveFile(wave_file)
            while True:
                if not alarm_active:
                    break
                audio.play(wave)
                while audio.playing:
                    server.poll()
                    if not alarm_active:
                        break
                    time.sleep(0.1)  # Small delay to prevent CPU hogging
                audio.stop()
    except Exception as e:
        print(f"Error playing sound: {e}")
        alarm_active = False

def stop_sound():
    global alarm_active
    print("Stopping alarm...")
    alarm_active = False  # Set flag first
    if audio.playing:
        audio.stop()
    print("Alarm stopped")
    time.sleep(1)  # Reduced sleep time
################################################################################################################

def connect_to_wifi():
    global pool
    global requests
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
    global server
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

        @server.route("/stop-alarm")
        def stop_route(request: Request):
            print("Received request to stop alarm")
            stop_sound()
            return Response(request, "Alarm stopped!")

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
        print(f"  http://{wifi.radio.ipv4_address}/stop-alarm")

        # Get initial time
        get_time()

        while True:
            try:
                server.poll()
                check_alarm()  # Check if it's time for alarm
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