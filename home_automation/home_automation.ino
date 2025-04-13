#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "5g";
const char* password = "12341234";

// Flask server details
const char* serverUrl = "http://192.168.181.130:5000";
const String deviceId = "AP1001"; // Must match what's registered in Flask
const String secretKey = "tapesh@143";

// I2C addresses for PCF8574 expanders
#define I2C_EXPANDER_1 0x20
#define I2C_EXPANDER_2 0x21

// Pins for status LED
#define STATUS_LED 2

// Variables for device state
bool currentStates[8] = {false};
unsigned long lastUpdateTime = 0;
const long updateInterval = 5000; // Check for updates every 5 seconds

void setup() {
  Serial.begin(115200);
  Serial.println("Starting setup...");
  
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(STATUS_LED, LOW); // Start with LED off
  Serial.println("Status LED configured.");
  
  // Start I2C bus with explicit pin definitions for NodeMCU
  Serial.println("Initializing I2C bus...");
  Wire.begin(4, 5); // SDA=D2, SCL=D1 for NodeMCU
  Serial.println("I2C bus initialized.");
  
  // Initialize I2C expanders
  Serial.println("Initializing I2C expanders...");
  initializeExpanders();
  Serial.println("I2C expanders initialized.");
  
  // Connect to WiFi
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    blinkLED(1, 200);
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Initial state fetch
  Serial.println("Fetching initial device state from server...");
  fetchDeviceStates();
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Attempting to reconnect...");
    reconnectWiFi();
    return;
  }
  
  // Regular state updates
  if (millis() - lastUpdateTime >= updateInterval) {
    Serial.println("Time for scheduled state update...");
    fetchDeviceStates();
    lastUpdateTime = millis();
  }
  
  // Blink LED to show activity
  digitalWrite(STATUS_LED, HIGH);
  delay(50);
  digitalWrite(STATUS_LED, LOW);
  
  delay(1000);
}

void initializeExpanders() {
  Serial.println("Setting all pins as outputs for expander 1...");
  // Set all pins as outputs and turn off initially (active-low relays)
  Wire.beginTransmission(I2C_EXPANDER_1);
  Wire.write(0xFF); // All pins high (off)
  Wire.endTransmission();
  Serial.println("Expander 1 initialized.");
  
  Serial.println("Setting all pins as outputs for expander 2...");
  Wire.beginTransmission(I2C_EXPANDER_2);
  Wire.write(0xFF); // All pins high
  Wire.endTransmission();
  Serial.println("Expander 2 initialized.");
}

void fetchDeviceStates() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Cannot fetch state: WiFi not connected");
    return;
  }
  
  Serial.println("Creating HTTP client...");
  WiFiClient client;
  HTTPClient http;
  
  String url = String(serverUrl) + "/api/device/control/" + deviceId;
  Serial.print("Fetching device state from URL: ");
  Serial.println(url);
  
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + secretKey);
  
  int httpCode = http.GET();
  
  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    Serial.print("Received payload: ");
    Serial.println(payload);
    
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, payload);
    if (error) {
      Serial.print("JSON deserialization failed: ");
      Serial.println(error.c_str());
    } else {
      // Update all 8 appliances
      for (int i = 0; i < 8; i++) {
        String key = "appliance_" + String(i+1);
        bool newState = doc[key];
        
        Serial.print("Appliance ");
        Serial.print(i+1);
        Serial.print(" current state: ");
        Serial.print(currentStates[i] ? "ON" : "OFF");
        Serial.print(", new state: ");
        Serial.println(newState ? "ON" : "OFF");
        
        if (newState != currentStates[i]) {
          currentStates[i] = newState;
          setApplianceState(i+1, newState); // Appliances numbered 1-8
        }
      }
      
      Serial.println("States updated successfully.");
    }
  } else {
    Serial.print("Error fetching states: ");
    Serial.println(http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void setApplianceState(int applianceNum, bool state) {
  Serial.print("Setting appliance ");
  Serial.print(applianceNum);
  Serial.print(" to ");
  Serial.println(state ? "ON" : "OFF");
  
  // Determine which expander controls this appliance
  uint8_t expanderAddress;
  uint8_t pin;
  
  if (applianceNum <= 4) {
    expanderAddress = I2C_EXPANDER_1;
    pin = applianceNum - 1; // Pins 0-3
    Serial.println("Using expander 1.");
  } else {
    expanderAddress = I2C_EXPANDER_2;
    pin = applianceNum - 5; // Pins 0-3
    Serial.println("Using expander 2.");
  }
  
  // Read current state of all pins
  Serial.print("Requesting current pin states from expander at address 0x");
  Serial.println(expanderAddress, HEX);
  Wire.requestFrom(expanderAddress, 1);
  uint8_t currentPins = Wire.read();
  Serial.print("Current pins state: 0x");
  Serial.println(currentPins, HEX);
  
  // Modify the specific pin
  if (state) {
    currentPins &= ~(1 << pin); // Set pin LOW to turn ON (active-low)
  } else {
    currentPins |= (1 << pin); // Set pin HIGH to turn OFF
  }
  
  // Write back to expander
  Wire.beginTransmission(expanderAddress);
  Wire.write(currentPins);
  Wire.endTransmission();
  
  Serial.print("New pins state written: 0x");
  Serial.println(currentPins, HEX);
}

void reconnectWiFi() {
  Serial.println("Attempting to reconnect to WiFi...");
  WiFi.disconnect();
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 10) {
    delay(500);
    Serial.print(".");
    blinkLED(2, 100);
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi reconnected.");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to reconnect to WiFi.");
  }
}

void blinkLED(int count, int duration) {
  Serial.print("Blinking LED ");
  Serial.print(count);
  Serial.print(" times with ");
  Serial.print(duration);
  Serial.println("ms duration each.");
  for (int i = 0; i < count; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(duration);
    digitalWrite(STATUS_LED, LOW);
    if (i < count - 1)
      delay(duration);
  }
}
