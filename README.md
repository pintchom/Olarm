# OLARM
A dual micro-controller alarm clock that only shuts up when you physically lift your toothbrush from its stand 

# Parts
- 2x Raspberry pi pico W
- 1x Mono jack speaker 
- 1x Magnetic latch 

# CircuitPython Sound Server Component

A web server implementation for Raspberry Pi Pico W that plays audio files in response to HTTP requests.

## Overview

This project creates a simple web server on a Raspberry Pi Pico W that can play WAV audio files when triggered via HTTP requests. The server provides endpoints to test connectivity and trigger sound playback.

## Hardware Requirements

- Raspberry Pi Pico W
- Speaker or audio output device connected to GP16
- USB cable for programming and power

## Software Requirements

- CircuitPython 8.x or later
- Required CircuitPython libraries:
  - `adafruit_httpserver`
  - `audiocore`
  - `audiopwmio`

## Installation

1. Install CircuitPython on your Raspberry Pi Pico W
2. Copy the following files to your CIRCUITPY drive:
   - `code.py`
   - `no-id.wav` (your sound file)
   - `settings.toml` (with your WiFi credentials)

### settings.toml Configuration

Create a `settings.toml` file with your WiFi credentials:

```toml
(settings.toml)
WIFI_SSID = "your_wifi_name"
WIFI_PASSWORD = "your_wifi_password"
```


## Usage

1. Power up your Raspberry Pi Pico W
2. The device will automatically:
   - Connect to WiFi
   - Start the web server
   - Print the server's IP address to the console

### Available Endpoints

- `GET /` - Test endpoint that returns "Server is running!"
- `GET /play` - Triggers audio playback

### Example Requests

```bash
Test server connectivity
curl http://<pico-ip-address>/
Trigger sound playback
curl http://<pico-ip-address>/play
```

## Troubleshooting

If you encounter issues:
1. Check the console output for error messages
2. Verify WiFi connectivity
3. Ensure both your computer and Pico W are on the same network
4. Confirm the audio file exists and is in the correct format
5. Verify the speaker is properly connected to GP16

## Error Messages

- `ECONNREFUSED`: Server is not running or not accessible
- `ETIMEDOUT`: Network connectivity issues or wrong IP address

## Credits

Created by Max Pintchouk

