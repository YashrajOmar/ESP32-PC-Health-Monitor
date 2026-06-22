#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  // 1. Start the serial connection at the correct speed
  Serial.begin(115200);
  
  // 2. Prove the ESP32 is actually turning on
  Serial.println("ESP32 is awake!"); 

  // 3. Try to start the screen, but DO NOT FREEZE if it fails!
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println("WARNING: OLED NOT FOUND! Check diagram.json wiring.");
  } else {
    Serial.println("OLED initialized successfully!");
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(10, 20);
    display.println("Waiting for JSON...");
    display.display();
  }
}

void loop() {
  if (Serial.available() > 0) {
    String jsonString = Serial.readStringUntil('\n');
    delay(50);
    jsonString.trim();
    
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, jsonString);
    
    if (!error) {
      int cpu = doc["cpu"];
      int ram = doc["ram"];
      int temp = doc["temp"];
      int gpu = doc["gpu"];
      int disk = doc["disk"];
      
      display.clearDisplay();
      display.setCursor(0, 0); display.println("--- SYSTEM HEALTH ---");
      display.setCursor(0, 16); display.print("CPU: "); display.print(cpu); display.print("%  ");
                                display.print("TMP: "); display.print(temp); display.println("C");
      display.setCursor(0, 28); display.print("RAM: "); display.print(ram); display.print("%  ");
                                display.print("DSK: "); display.print(disk); display.println("%");
      display.setCursor(0, 40); display.print("GPU: "); display.print(gpu); display.println("%");
      
      display.setCursor(0, 56);
      if (temp > 85 || cpu > 95) display.println("!!! OVERHEATING !!!");
      else if (ram > 90) display.println("!!! HIGH MEMORY !!!");
      else display.println("System OK");
      
      display.display();
    }
  }
}