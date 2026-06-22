# PC-Monitor-ESP32

A real-time PC health monitor that streams live system stats (CPU, RAM, disk, temperature) from a Python script to an ESP32 microcontroller, rendered on a small OLED display.

> **Note:** The ESP32 and OLED in this project are simulated using [Wokwi](https://wokwi.com) — there's no physical hardware involved yet. The PC-side data collection is real (live `psutil` readings from an actual machine); the microcontroller and display are virtual. See [Future Work](#future-work) for the plan to move this onto real hardware.

![System Health Display](docs/demo.png)
*Live CPU/RAM/disk/temp readout on the OLED, with a HIGH MEMORY alert triggering automatically when RAM usage crosses a threshold.*

## How it works

```
┌─────────────────┐        TCP socket        ┌──────────────────┐       I2C       ┌─────────────┐
│  Python script    │  ──── JSON @ 1Hz ────►  │   ESP32 (Wokwi)    │  ─────────────► │  OLED display │
│  (psutil)          │      localhost:4000     │   sketch.ino       │                 │               │
└─────────────────┘                          └──────────────────┘                 └─────────────┘
```

1. `pc_data_sender.py` reads live system stats using `psutil` (CPU %, RAM %, disk usage, temperature where available, GPU/network if exposed by the OS).
2. The script paces output to roughly 1 reading per second and sends it as a JSON payload over a local TCP socket (`localhost:4000`).
3. An ESP32, simulated in [Wokwi](https://wokwi.com), listens on that socket, parses the JSON, and renders the values to a small OLED.
4. If RAM usage crosses a set threshold, the firmware swaps in a `!!! HIGH MEMORY !!!` warning on the display.

## Why TCP instead of serial

The first version of this project tried to bridge Python and the ESP32 simulator using a virtual serial port (`com0com`). That approach turned out to be unreliable in this setup — the VS Code Wokwi extension runs in a sandboxed environment that doesn't reliably see Windows' virtual serial drivers, and getting baud rates to agree between the Python side and the virtual port added another layer of fragility.

Switching the transport to a plain TCP socket on `localhost:4000` sidestepped the whole problem. Python opens a socket and writes JSON; the firmware reads from the socket directly. No drivers, no baud rate negotiation, no OS-level serial routing.

## Running it yourself

**1. Firmware (ESP32 + OLED)**
- Open [wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32) and paste in `sketch.ino` from this repo.
- Wokwi's web simulator compiles the sketch for you — no local toolchain (e.g. PlatformIO) required.
- Download the compiled `.bin` and place it alongside `sketch.ino` in this project's `wokwi_esp32/` folder so the local VS Code Wokwi extension can run the simulation offline.
- Open the project folder in VS Code with the [Wokwi extension](https://marketplace.visualstudio.com/items?itemName=wokwi.wokwi-vscode) installed, and start the simulator.

**2. Data collector (Python)**
```bash
cd pc_collector
pip install -r requirements.txt
python pc_data_sender.py
```

The script will start sending live PC stats over `localhost:4000`. Once both sides are running, the OLED in the simulator updates roughly once per second.

## Project structure

```
PC-Monitor-ESP32/
├── pc_collector/
│   ├── pc_data_sender.py     # reads PC stats, sends JSON over TCP
│   └── requirements.txt
└── wokwi_esp32/
    ├── sketch.ino             # ESP32 firmware: TCP listener + OLED renderer
    ├── sketch.ino.bin         # compiled binary (from wokwi.com)
    ├── diagram.json           # Wokwi wiring diagram
    └── wokwi.toml             # Wokwi simulator config
```

## What this project covers

- Reading live OS-level metrics in Python (`psutil`)
- Designing a simple JSON protocol between a host script and embedded firmware
- Debugging a transport layer when the first approach (virtual serial port) didn't hold up, and pivoting to a simpler one (TCP socket)
- Basic I2C communication and OLED rendering on an ESP32
- Rate-limiting/pacing a data stream to match what the receiving hardware can actually handle

## Future work

- **Move to physical hardware.** This project currently runs entirely on the Wokwi simulator. The next step is wiring up a real ESP32 + SSD1306 OLED per `diagram.json` and flashing `sketch.ino` directly (via Arduino IDE or PlatformIO) instead of running it in simulation.
- **Validate real I2C timing and power behavior**, which a simulator doesn't model — pull-up resistor values, voltage levels, and real-world signal noise.
- **Add Wi-Fi support** so the ESP32 can receive data over the network instead of relying on a TCP socket that only works on the same machine.

## Notes

PC stats are real, read live from the host machine with `psutil`. The microcontroller and display are currently virtual. The firmware and wiring (`diagram.json`) are written so the same code should work unchanged on a physical ESP32 + OLED once wired up per the diagram.
