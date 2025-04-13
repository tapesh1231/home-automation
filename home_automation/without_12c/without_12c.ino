#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>  // Add this include
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "JIET@JOD";
const char* password = "2912868152";

// Server details
#define SERVER "http://192.168.24.82:5000"
#define DEVICE_ID "AP0011"
#define SECRET_KEY "Tapesh@123"

// Relay pins (adjust according to your wiring)
const int relayPins[] = {5, 4, 0, 2, 14, 12, 13, 15};
bool currentStates[8] = {false}; // Track current relay states

WiFiClient client;  // Create WiFiClient instance

void setup() {
  Serial.begin(115200);
  while (!Serial); // Wait for serial connection
  
  Serial.println("\nStarting Relay Controller");
  setupRelays();
  connectWiFi();
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    syncRelayStates();
  } else {
    Serial.println("WiFi disconnected! Attempting to reconnect...");
    connectWiFi();
  }
  delay(5000); // Sync every 5 seconds
}

void setupRelays() {
  Serial.println("Initializing relay pins:");
  for (int i = 0; i < 8; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH); // Default to OFF
    Serial.printf("  Relay %d: GPIO %d (Initial State: OFF)\n", i+1, relayPins[i]);
  }
}

void connectWiFi() {
  Serial.printf("Connecting to %s", ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void syncRelayStates() {
  Serial.println("\nSyncing relay states with server...");
  String url = String(SERVER) + "/api/v1/device/state/" + String(DEVICE_ID);
  Serial.printf("Requesting: %s\n", url.c_str());
  
  HTTPClient http;
  http.begin(client, url);  // Updated API usage
  http.addHeader("Authorization", "Bearer " + String(SECRET_KEY));
  
  int httpCode = http.GET();
  
  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    Serial.println("Server Response:");
    Serial.println(payload);
    
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, payload);
    
    JsonObject device = doc[DEVICE_ID];
    if (!device.isNull()) {
      Serial.println("\nParsed Relay States:");
      for (int i = 1; i <= 8; i++) {
        String relayKey = "relay_" + String(i);
        bool newState = device[relayKey];
        
        Serial.printf("  %s: %s", relayKey.c_str(), newState ? "ON" : "OFF");
        
        if (newState != currentStates[i-1]) {
          setRelayState(i, newState);
          currentStates[i-1] = newState;
          Serial.println(" (CHANGED)");
        } else {
          Serial.println(" (no change)");
        }
      }
    } else {
      Serial.println("Error: No device data in response");
    }
  } else {
    Serial.printf("Error: HTTP code %d\n", httpCode);
  }
  http.end();
}

void setRelayState(int relayNum, bool state) {
  if (relayNum < 1 || relayNum > 8) return;
  
  int pin = relayPins[relayNum - 1];
  digitalWrite(pin, state ? LOW : HIGH); // LOW activates most relay modules
  
  Serial.printf("  -> PHYSICALLY SET Relay %d to %s\n", 
                relayNum, state ? "ON" : "OFF");
}