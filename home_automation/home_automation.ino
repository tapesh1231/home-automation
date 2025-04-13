#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include "PCF8574.h"
#include "config.h"

PCF8574 relayBoard(I2C_ADDRESS);  // Relay module, initialized with I2C address

void setup() {
  Serial.begin(115200);  // Start serial communication at 115200 baud rate
  Wire.begin();  // Start I2C communication

  Serial.println("Connecting to WiFi...");  // Print a message to indicate WiFi connection attempt
  WiFi.begin(ssid, password);  // Begin WiFi connection with provided SSID and password
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);  // Wait 500 ms
    Serial.print(".");  // Print dot to indicate the connection attempt
  }
  Serial.println("\nWiFi connected");  // Print success message once connected

  relayBoard.begin();  // Initialize relay board

  // Set all relays OFF initially (assuming HIGH is OFF)
  Serial.println("Initializing relays...");  // Print message indicating relay initialization
  for (int i = 0; i < 8; i++) {
    relayBoard.write(i, HIGH);  // Set all relays to OFF (HIGH is OFF)
    Serial.print("Relay "); 
    Serial.print(i); 
    Serial.println(" set to OFF");  // Print each relay status
  }

  getRelayStateFromServer();  // Sync the relay states with the server
}

void loop() {
  static unsigned long lastSync = 0;
  if (millis() - lastSync > 60000) {  // If 60 seconds have passed
    Serial.println("Syncing relay states with the server...");  // Print a message to indicate syncing
    getRelayStateFromServer();  // Sync relay state from the server
    lastSync = millis();  // Reset the sync timer
  }

  // Additional logic (e.g., button press) can be added here
}

void getRelayStateFromServer() {
  if (WiFi.status() == WL_CONNECTED) {  // Check if WiFi is connected
    HTTPClient http;  // Initialize HTTP client
    String url = SERVER;
    url += "/device/state/";  // Append the device state endpoint
    url += DEVICE_ID;  // Append the device ID

    Serial.print("Sending GET request to: "); 
    Serial.println(url);  // Print the full URL for the GET request

    WiFiClient client;
    http.begin(client, url);  // Initialize HTTP request with the URL

    http.addHeader("Authorization", String("Bearer ") + SECRET_KEY);  // Add Authorization header

    int httpCode = http.GET();  // Send GET request to the server
    if (httpCode == 200) {  // If the response is OK (200)
      String payload = http.getString();  // Get the response payload
      Serial.println("GET Response: " + payload);  // Print the response payload

      // Parse the response and update relay states
      for (int i = 1; i <= 8; i++) {
        String key = "\"relay_" + String(i) + "\":true";
        if (payload.indexOf(key) != -1) {
          relayBoard.write(i - 1, LOW); // Set relay ON (LOW)
          Serial.print("Relay "); 
          Serial.print(i); 
          Serial.println(" turned ON");
        } else {
          relayBoard.write(i - 1, HIGH); // Set relay OFF (HIGH)
          Serial.print("Relay ");
          Serial.print(i);
          Serial.println(" turned OFF");
        }
      }

    } else {
      Serial.println("GET Failed: " + String(httpCode));  // Print failure message if GET request fails
    }

    http.end();  // End the HTTP connection
  }
}

void postRelayStateToServer() {
  if (WiFi.status() == WL_CONNECTED) {  // Check if WiFi is connected
    HTTPClient http;  // Initialize HTTP client
    String url = SERVER;
    url += "/device/state/";  // Append the device state endpoint
    url += DEVICE_ID;  // Append the device ID

    Serial.print("Sending POST request to: ");
    Serial.println(url);  // Print the full URL for the POST request

    WiFiClient client;
    http.begin(client, url);  // Initialize HTTP request with the URL

    http.addHeader("Content-Type", "application/json");  // Add content type header
    http.addHeader("Authorization", String("Bearer ") + SECRET_KEY);  // Add Authorization header

    // Construct JSON payload for the relay states
    String payload = "{\"" + String(DEVICE_ID) + "\":{";
    for (int i = 0; i < 8; i++) {
      payload += "\"relay_" + String(i + 1) + "\":" + (relayBoard.read(i) == LOW ? "true" : "false");
      if (i != 7) payload += ",";  // Add comma between relay states
    }
    payload += "}}";

    Serial.print("Payload: ");
    Serial.println(payload);  // Print the JSON payload

    int httpCode = http.POST(payload);  // Send POST request with the payload
    String response = http.getString();  // Get the response from the server
    Serial.println("POST Status: " + String(httpCode));  // Print POST status code
    Serial.println("Response: " + response);  // Print the response from the server

    http.end();  // End the HTTP connection
  }
}
