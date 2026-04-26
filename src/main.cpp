#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads; // Use this for the 16-bit version

void setup() {
  // LED_BUILTIN is the Green user LED on the Nucleo-144
  pinMode(LED_BUILTIN, OUTPUT); 
  // Start serial at 115200 for your ADC data later
  Serial.begin(115200); 

  Serial.println("Initializing ADS1115...");
  
  // D14 (SDA) and D15 (SCL) on CN7 map to the default Wire interface
  Wire.begin();
  
  // The default I2C address for ADS1115 is 0x48 (if ADDR is tied to GND)
  if (!ads.begin()) {
    Serial.println("Failed to initialize ADS1115. Check wiring!");
    while (1);
  }
  Serial.println("ADS1115 initialized successfully.");
  
  // Optional: Adjust gain if needed (default is +/- 6.144V)
  // ads.setGain(GAIN_TWOTHIRDS); 
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  
  // Read all 4 channels
  int16_t adc0 = ads.readADC_SingleEnded(0);
  int16_t adc1 = ads.readADC_SingleEnded(1);
  int16_t adc2 = ads.readADC_SingleEnded(2);
  int16_t adc3 = ads.readADC_SingleEnded(3);

  float volts0 = ads.computeVolts(adc0);
  float volts1 = ads.computeVolts(adc1);
  float volts2 = ads.computeVolts(adc2);
  float volts3 = ads.computeVolts(adc3);
  
  // Output as CSV: V0,V1,V2,V3
  Serial.print(volts0, 4); Serial.print(",");
  Serial.print(volts1, 4); Serial.print(",");
  Serial.print(volts2, 4); Serial.print(",");
  Serial.println(volts3, 4);
  
  digitalWrite(LED_BUILTIN, LOW);
  delay(50); // 20 Hz sample rate
}
