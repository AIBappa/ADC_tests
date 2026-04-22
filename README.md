Introduction:
This code demonstrates the interfacing between a Nucleo F767ZI microcontroller and an ADS1115 ADC (Analog to Digital Converter) using the Arduino framework. The code initializes the ADC, reads values from it, and prints the results to the serial monitor.

Picture of the setup noted in /pics folder.

Lessons Learnt:
1. The pin headers to fix the ADS1115 to the breadboard are not really good and can cause bad connections. It is important to ensure that the connections are secure to avoid intermittent readings. If you see the pic, I did not use them at all.

2. Platform IO extension in VSCode is one of the best ways to program this Nucleo. It provides a user-friendly interface and simplifies the process of uploading code to the microcontroller.

3. The Adafruit ADS1X15 library is a great resource for working with the ADS1115 ADC. It provides easy-to-use functions for reading values from the ADC and configuring its settings.

4. When working with ADCs, it is important to consider the reference voltage and the resolution of the ADC. The ADS1115 has a 16-bit resolution and can be configured to use different reference voltages, which can affect the accuracy of the readings.

5. It is also important to consider the sampling rate of the ADC. The ADS1115 can be configured to sample at different rates, and choosing the appropriate rate can help ensure accurate readings while minimizing noise.

Code:
main.cpp included in /src folder. It initializes the ADS1115, reads values from it, and prints the results to the serial monitor. All buttons to build, deploy and view the serial monitor have been used from platform IO extension.