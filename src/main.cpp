#include <Arduino.h>

void setup() {
  // LED_BUILTIN is the Green user LED on the Nucleo-144
  pinMode(LED_BUILTIN, OUTPUT); 
  // Start serial at 115200 for your ADC data later
  Serial.begin(115200); 
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("Nucleo F767ZI Alive - LED ON");
  delay(500);
  
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Nucleo F767ZI Alive - LED OFF");
  delay(500);
}
