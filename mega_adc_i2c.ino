#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <SPI.h>
#include <RF24.h>

#define NUM_ELECTRODES 12
Adafruit_ADS1115 ads1;
Adafruit_ADS1115 ads2;
Adafruit_ADS1115 ads3;
int16_t electrodeValues[NUM_ELECTRODES];
uint8_t digitalValues[NUM_ELECTRODES]; // For compatibility, but you may want to send int16_t for full resolution

// NRF24L01 CE and CSN pins (adjust as needed for your Mega wiring)
const int RF_CE = 8;
const int RF_CSN = 7;
RF24 radio(RF_CE, RF_CSN);

// Address for communication (must match Nano's receiver)
const byte address[6] = "00001";

void setup() {
  Wire.begin();
  ads1.begin(0x48); // First ADS1115
  ads2.begin(0x49); // Second ADS1115
  ads3.begin(0x4A); // Third ADS1115
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_LOW);
  radio.stopListening();
}

void loop() {
  // Read 4 channels from each ADS1115 (total 12)
  for (int i = 0; i < 4; i++) {
    electrodeValues[i] = ads1.readADC_SingleEnded(i);
    electrodeValues[i+4] = ads2.readADC_SingleEnded(i);
    electrodeValues[i+8] = ads3.readADC_SingleEnded(i);
  }
  // Send full 16-bit values
  radio.write(&electrodeValues, sizeof(electrodeValues));
  delay(10);
} 