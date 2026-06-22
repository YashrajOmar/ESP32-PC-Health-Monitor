import psutil
import serial
import time
import json

try:
    import GPUtil
except ImportError:
    GPUtil = None

# --- STEP 1: OPEN THE CONNECTION ---
# Connect directly to Wokwi's internal server, bypassing Windows COM ports entirely
try:
    ser = serial.serial_for_url('rfc2217://localhost:4000', baudrate=115200, timeout=1)
    print("Successfully connected to the Wokwi network port!")
except Exception as e:
    print(f"Waiting for Wokwi Simulator... (Error: {e})")
    ser = None

# --- STEP 2: THE INFINITE LOOP ---
print("Starting PC Health Monitor... Press Ctrl+C to stop.")

# We need to remember the network bytes from the last second to calculate speed
last_net = psutil.net_io_counters()

while True:
    try:
        # 1. CPU and RAM
        # Note: interval=1 automatically pauses the script for exactly 1 second to measure load!
        cpu_usage = int(psutil.cpu_percent(interval=1)) 
        ram_usage = int(psutil.virtual_memory().percent)
        
        # 2. Disk and Battery
        disk_usage = int(psutil.disk_usage('/').percent)
        
        battery = psutil.sensors_battery()
        bat_percent = int(battery.percent) if battery else 100

        # 3. GPU Usage
        gpu_usage = 0
        if GPUtil:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = int(gpus[0].load * 100)
        
        # 4. Network Speed
        current_net = psutil.net_io_counters()
        net_down_mb = round((current_net.bytes_recv - last_net.bytes_recv) / 1_048_576, 2)
        net_up_mb = round((current_net.bytes_sent - last_net.bytes_sent) / 1_048_576, 2)
        last_net = current_net

        # 5. Temperature (Simulated based on CPU load for safety/simplicity)
        temp = int(35 + (cpu_usage * 0.55))

        # --- STEP 3: CREATE THE JSON PACKET ---
        data_dict = {
            "cpu": cpu_usage,
            "ram": ram_usage,
            "temp": temp,
            "gpu": gpu_usage,
            "disk": disk_usage,
            "bat": bat_percent,
            "net_down": net_down_mb,
            "net_up": net_up_mb
        }
        
        data_string = json.dumps(data_dict) + "\n"
        print(f"Sending -> {data_string.strip()}")

        # Send data if the connection is active
        if ser is not None and ser.is_open:
            try:
                ser.write(data_string.encode('utf-8'))
            except Exception:
                print("Network port traffic jam! Waiting for ESP32 to catch up...")
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        if ser is not None:
            ser.close()
        break