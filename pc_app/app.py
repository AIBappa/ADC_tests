import sys
import time
import numpy as np
import pyqtgraph as pg
import serial
import serial.tools.list_ports
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QComboBox, QPushButton, 
                               QCheckBox, QSpinBox, QGroupBox, QLineEdit, QSplitter)
from PySide6.QtCore import QThread, Signal, Qt, QTimer

# --- Serial Data Acquisition Thread ---
class SerialThread(QThread):
    data_received = Signal(float, list) # time, [v0, v1, v2, v3]
    error_occurred = Signal(str)

    def __init__(self, port, baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.serial_conn = None
        self.start_time = None

    def run(self):
        self.running = True
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.serial_conn.reset_input_buffer()
            self.start_time = time.time()
            
            while self.running:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        try:
                            # Expected format: "1.23,2.34,3.45,4.56"
                            parts = line.split(',')
                            if len(parts) >= 4:
                                voltages = [float(p) for p in parts[:4]]
                                current_time = time.time() - self.start_time
                                self.data_received.emit(current_time, voltages)
                        except ValueError:
                            pass # Ignore malformed lines
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()

    def stop(self):
        self.running = False
        self.wait()


# --- Channel Panel UI (Graph + Settings) ---
class ChannelPanel(QGroupBox):
    def __init__(self, channel_id, parent=None):
        super().__init__(f"Input {channel_id}", parent)
        self.channel_id = channel_id
        
        self.time_data = []
        self.voltage_data = []
        
        # UI Layout
        layout = QHBoxLayout()
        
        # 1. Graph Area
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', 'Voltage', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_curve = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2))
        self.fit_curve = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2, style=Qt.DashLine))
        
        layout.addWidget(self.plot_widget, stretch=3)
        
        # 2. Controls Area
        controls_layout = QVBoxLayout()
        
        # Save Controls
        save_group = QGroupBox("Export Data")
        save_layout = QVBoxLayout()
        self.filename_input = QLineEdit(f"channel_{channel_id}_data.csv")
        self.save_btn = QPushButton("Save Data")
        self.save_btn.setEnabled(False) # Enabled after acquisition
        self.save_btn.clicked.connect(self.save_data)
        save_layout.addWidget(QLabel("File Name:"))
        save_layout.addWidget(self.filename_input)
        save_layout.addWidget(self.save_btn)
        save_group.setLayout(save_layout)
        controls_layout.addWidget(save_group)
        
        # Zoom Controls
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QVBoxLayout()
        
        time_zoom_layout = QHBoxLayout()
        self.t_min = QSpinBox(); self.t_min.setRange(0, 1000)
        self.t_max = QSpinBox(); self.t_max.setRange(1, 1000); self.t_max.setValue(10)
        time_zoom_layout.addWidget(QLabel("Time (s):"))
        time_zoom_layout.addWidget(self.t_min)
        time_zoom_layout.addWidget(QLabel("-"))
        time_zoom_layout.addWidget(self.t_max)
        
        volt_zoom_layout = QHBoxLayout()
        self.v_min = QSpinBox(); self.v_min.setRange(-10, 10); self.v_min.setValue(0)
        self.v_max = QSpinBox(); self.v_max.setRange(0, 10); self.v_max.setValue(5)
        volt_zoom_layout.addWidget(QLabel("Volts (V):"))
        volt_zoom_layout.addWidget(self.v_min)
        volt_zoom_layout.addWidget(QLabel("-"))
        volt_zoom_layout.addWidget(self.v_max)
        
        self.apply_zoom_btn = QPushButton("Apply Zoom")
        self.apply_zoom_btn.clicked.connect(self.apply_zoom)
        self.reset_zoom_btn = QPushButton("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        
        zoom_layout.addLayout(time_zoom_layout)
        zoom_layout.addLayout(volt_zoom_layout)
        zoom_layout.addWidget(self.apply_zoom_btn)
        zoom_layout.addWidget(self.reset_zoom_btn)
        zoom_group.setLayout(zoom_layout)
        controls_layout.addWidget(zoom_group)
        
        # Fit Controls
        fit_group = QGroupBox("Curve Fit")
        fit_layout = QVBoxLayout()
        self.fit_type = QComboBox()
        self.fit_type.addItems(["Point to Point (Direct)", "Polynomial Fit (Degree 2)", "Polynomial Fit (Degree 3)"])
        self.fit_type.currentIndexChanged.connect(self.update_plot)
        fit_layout.addWidget(self.fit_type)
        fit_group.setLayout(fit_layout)
        controls_layout.addWidget(fit_group)
        
        controls_layout.addStretch()
        
        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        layout.addWidget(controls_widget, stretch=1)
        
        self.setLayout(layout)
        
    def add_data_point(self, t, v):
        self.time_data.append(t)
        self.voltage_data.append(v)
        # Update plot every N points to save CPU if necessary, or just rely on QTimer in Main app
        
    def update_plot(self):
        if not self.time_data:
            return
            
        t_arr = np.array(self.time_data)
        v_arr = np.array(self.voltage_data)
        
        self.plot_curve.setData(t_arr, v_arr)
        
        # Handle Fit
        fit_idx = self.fit_type.currentIndex()
        if fit_idx == 0:
            self.fit_curve.setData([], []) # Clear fit
        else:
            degree = 2 if fit_idx == 1 else 3
            if len(t_arr) > degree:
                # Calculate polynomial fit
                coeffs = np.polyfit(t_arr, v_arr, degree)
                poly = np.poly1d(coeffs)
                fit_v = poly(t_arr)
                self.fit_curve.setData(t_arr, fit_v)
                
    def apply_zoom(self):
        self.plot_widget.setXRange(self.t_min.value(), self.t_max.value(), padding=0)
        self.plot_widget.setYRange(self.v_min.value(), self.v_max.value(), padding=0)
        
    def reset_zoom(self):
        self.plot_widget.enableAutoRange()
        
    def enable_saving(self):
        self.save_btn.setEnabled(True)
        
    def save_data(self):
        filename = self.filename_input.text()
        if not filename:
            filename = f"channel_{self.channel_id}_data.csv"
        try:
            with open(filename, 'w') as f:
                f.write("Time(s),Voltage(V)\n")
                for t, v in zip(self.time_data, self.voltage_data):
                    f.write(f"{t:.4f},{v:.4f}\n")
            print(f"Saved {filename}")
        except Exception as e:
            print(f"Error saving: {e}")
            
    def clear_data(self):
        self.time_data = []
        self.voltage_data = []
        self.plot_curve.setData([], [])
        self.fit_curve.setData([], [])
        self.save_btn.setEnabled(False)

# --- Main Application Window ---
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADC Data Acquisition")
        self.resize(1000, 800)
        
        self.serial_thread = None
        self.channel_panels = {}
        
        self.init_ui()
        
        # Timer for updating plots smoothly
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_plots)
        self.plot_timer.start(100) # 10 fps update
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Top Control Bar ---
        top_bar = QHBoxLayout()
        
        # COM Port
        top_bar.addWidget(QLabel("COM Port:"))
        self.port_combo = QComboBox()
        self.refresh_ports()
        top_bar.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        top_bar.addWidget(self.refresh_btn)
        
        # Channel Selection
        top_bar.addWidget(QLabel("  Inputs:"))
        self.ch_checks = []
        for i in range(4):
            chk = QCheckBox(f"IN{i}")
            if i == 0: chk.setChecked(True) # default
            self.ch_checks.append(chk)
            top_bar.addWidget(chk)
            
        # Acquisition Time
        top_bar.addWidget(QLabel("  Time (s):"))
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 600) # Max 10 minutes (600s)
        self.time_spin.setValue(10)
        top_bar.addWidget(self.time_spin)
        
        # Start Button
        self.acquire_btn = QPushButton("Acquire")
        self.acquire_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.acquire_btn.clicked.connect(self.toggle_acquisition)
        top_bar.addWidget(self.acquire_btn)
        
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        
        # --- Dynamic Panels Area ---
        self.panels_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(self.panels_splitter, stretch=1)
        
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.device)
            
    def toggle_acquisition(self):
        if self.serial_thread and self.serial_thread.running:
            self.stop_acquisition()
        else:
            self.start_acquisition()
            
    def start_acquisition(self):
        port = self.port_combo.currentText()
        if not port:
            print("No COM port selected.")
            return
            
        # 1. Setup UI Panels
        # Clear old panels
        while self.panels_splitter.count():
            widget = self.panels_splitter.widget(0)
            widget.setParent(None)
            widget.deleteLater()
            
        self.channel_panels.clear()
        
        # Create new panels for selected channels
        for i, chk in enumerate(self.ch_checks):
            if chk.isChecked():
                panel = ChannelPanel(i)
                self.channel_panels[i] = panel
                self.panels_splitter.addWidget(panel)
                
        if not self.channel_panels:
            print("No channels selected.")
            return
            
        # 2. Setup Timer for Stop
        self.acq_duration = self.time_spin.value()
        self.stop_timer = QTimer(self)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.stop_acquisition)
        self.stop_timer.start(self.acq_duration * 1000)
        
        # 3. Start Serial Thread
        self.serial_thread = SerialThread(port)
        self.serial_thread.data_received.connect(self.handle_serial_data)
        self.serial_thread.error_occurred.connect(self.handle_serial_error)
        self.serial_thread.start()
        
        # UI Updates
        self.acquire_btn.setText("Stop")
        self.acquire_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        for chk in self.ch_checks:
            chk.setEnabled(False)
        self.time_spin.setEnabled(False)
        
    def stop_acquisition(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None
            
        if hasattr(self, 'stop_timer') and self.stop_timer.isActive():
            self.stop_timer.stop()
            
        # UI Updates
        self.acquire_btn.setText("Acquire")
        self.acquire_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        for chk in self.ch_checks:
            chk.setEnabled(True)
        self.time_spin.setEnabled(True)
        
        # Enable saving
        for panel in self.channel_panels.values():
            panel.enable_saving()
            panel.update_plot() # Final update
            
    def handle_serial_data(self, current_time, voltages):
        if current_time > self.acq_duration:
            # Saftey catch if timer is delayed
            return
            
        for i, panel in self.channel_panels.items():
            if i < len(voltages):
                panel.add_data_point(current_time, voltages[i])
                
    def handle_serial_error(self, err):
        print(f"Serial Error: {err}")
        self.stop_acquisition()
        
    def update_plots(self):
        # Called periodically by QTimer to prevent UI freezing from too many updates
        if self.serial_thread and self.serial_thread.running:
            for panel in self.channel_panels.values():
                panel.update_plot()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())
