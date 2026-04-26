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

---

## Python PC Application (Data Viewer)

A Python desktop application is included in the `/pc_app` directory to acquire, visualize, and export the real-time ADC data from the Nucleo board over Serial.

### Features
* **Real-time Graphing:** Smooth, 20Hz real-time updates for each selected input using `pyqtgraph`.
* **Dynamic Panels:** Independent views for each of the 4 inputs.
* **Zoom Controls:** Ability to precisely zoom into specific time periods and voltage ranges.
* **Curve Fitting:** Real-time Polynomial fitting (Degree 2 or 3) alongside point-to-point plotting.
* **Data Export:** Save acquired time and voltage data to CSV format after the acquisition completes.

### Setup and Running
Ensure you have Python installed on your system (Windows or Linux).

1. Open your terminal or command prompt.
2. Navigate to the `pc_app` directory:
   ```bash
   cd pc_app
   ```
3. (Optional but recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   python app.py
   ```

### Usage Instructions
1. Flash the Nucleo board with the updated firmware in `src/main.cpp`.
2. Launch the Python app.
3. Select the **COM Port** your Nucleo is connected to (click "Refresh" if it isn't listed).
4. Check the boxes for the inputs (`IN0` to `IN3`) you wish to visualize.
5. Set the acquisition time (in seconds, up to 10 minutes / 600s).
6. Click **Acquire**. The graphs will populate dynamically.
7. Once acquisition completes, you can use the zoom tools, toggle the curve fits, and enter a filename to export the data to a CSV.