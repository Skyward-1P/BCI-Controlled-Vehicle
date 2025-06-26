#include <SPI.h>
#include <RF24.h>

#define NUM_ELECTRODES 12
int16_t receivedValues[NUM_ELECTRODES];

// NRF24L01 CE and CSN pins
const int RF_CE = 8;
const int RF_CSN = 7;
RF24 radio(RF_CE, RF_CSN);

// Addresses for communication (must match Mega's transmitter)
const byte address[6] = "00001";

void setup() {
  Serial.begin(115200); // For PC communication
  radio.begin();
  radio.openReadingPipe(0, address);
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();
}

void loop() {
  if (radio.available()) {
    radio.read(&receivedValues, sizeof(receivedValues));
    // Send received data to PC
    for (int i = 0; i < NUM_ELECTRODES; i++) {
      Serial.print(receivedValues[i]);
      if (i < NUM_ELECTRODES - 1) Serial.print(",");
    }
    Serial.println();
  }
} 
