import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import serial
import serial.tools.list_ports
import threading
import time
import json
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import os

# Import our modules
from connection_manager import OBD2Connection
from gui_components import ConnectionFrame

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OBD2Diagnostic:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("OBD2 Diagnostic Tool - Mercedes Software")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize connection manager
        self.connection_manager = OBD2Connection()
        
        # Load error codes
        self.error_codes = self.load_error_codes()
        
        # Data storage
        self.sensor_data = {}
        self.error_codes_list = []
        self.live_data = []
        
        # Initialize GUI
        self.setup_gui()
        
    def load_error_codes(self):
        """Load error codes from JSON file"""
        try:
            with open('error_codes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("error_codes.json not found, using empty dictionary")
            return {}
        except Exception as e:
            print(f"Error loading error codes: {e}")
            return {}
        
    def setup_gui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="OBD2 Diagnostic Tool", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10)
        
        # Connection frame
        self.connection_frame = ConnectionFrame(main_frame, self.connection_manager)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_dashboard_tab()
        self.setup_sensors_tab()
        self.setup_error_codes_tab()
        self.setup_live_monitoring_tab()
        self.setup_advanced_tab()
        
    def setup_dashboard_tab(self):
        dashboard_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")
        
        # Vehicle info
        vehicle_frame = ctk.CTkFrame(dashboard_frame)
        vehicle_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(vehicle_frame, text="Informații Vehicul", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.vin_label = ctk.CTkLabel(vehicle_frame, text="VIN: N/A")
        self.vin_label.pack()
        
        self.calibration_label = ctk.CTkLabel(vehicle_frame, text="Calibrare: N/A")
        self.calibration_label.pack()
        
        # Quick actions
        actions_frame = ctk.CTkFrame(dashboard_frame)
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(actions_frame, text="Acțiuni Rapide", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        buttons_frame = ctk.CTkFrame(actions_frame)
        buttons_frame.pack(pady=5)
        
        ctk.CTkButton(buttons_frame, text="Citire Coduri Eroare",
                     command=self.read_error_codes).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Ștergere Coduri Eroare",
                     command=self.clear_error_codes).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Test Senzori",
                     command=self.test_sensors).pack(side="left", padx=5)
        
    def setup_sensors_tab(self):
        sensors_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(sensors_frame, text="Senzori")
        
        # Create scrollable frame for sensors
        self.sensors_canvas = ctk.CTkScrollableFrame(sensors_frame)
        self.sensors_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize sensor displays
        self.sensor_displays = {}
        self.create_sensor_displays()
        
    def setup_error_codes_tab(self):
        error_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(error_frame, text="Coduri Eroare")
        
        # Error codes list
        self.error_tree = ttk.Treeview(error_frame, columns=("Code", "Description", "Status"),
                                      show="headings", height=15)
        self.error_tree.heading("Code", text="Cod")
        self.error_tree.heading("Description", text="Descriere")
        self.error_tree.heading("Status", text="Status")
        self.error_tree.column("Code", width=100)
        self.error_tree.column("Description", width=300)
        self.error_tree.column("Status", width=100)
        self.error_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons
        error_buttons_frame = ctk.CTkFrame(error_frame)
        error_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(error_buttons_frame, text="Citire Coduri",
                     command=self.read_error_codes).pack(side="left", padx=5)
        ctk.CTkButton(error_buttons_frame, text="Ștergere Coduri",
                     command=self.clear_error_codes).pack(side="left", padx=5)
        ctk.CTkButton(error_buttons_frame, text="Export CSV",
                     command=self.export_error_codes).pack(side="left", padx=5)
        
    def setup_live_monitoring_tab(self):
        monitoring_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(monitoring_frame, text="Monitorizare Live")
        
        # Control buttons
        control_frame = ctk.CTkFrame(monitoring_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.monitor_btn = ctk.CTkButton(control_frame, text="Start Monitorizare",
                                       command=self.toggle_monitoring)
        self.monitor_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame, text="Salvare Date",
                     command=self.save_live_data).pack(side="left", padx=5)
        
        # Graph frame
        graph_frame = ctk.CTkFrame(monitoring_frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def setup_advanced_tab(self):
        advanced_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(advanced_frame, text="Avansat")
        
        # ECU information
        ecu_frame = ctk.CTkFrame(advanced_frame)
        ecu_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ecu_frame, text="Informații ECU", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.ecu_info_text = ctk.CTkTextbox(ecu_frame, height=200)
        self.ecu_info_text.pack(fill="x", padx=10, pady=5)
        
        # Advanced functions
        advanced_buttons_frame = ctk.CTkFrame(advanced_frame)
        advanced_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(advanced_buttons_frame, text="Citire ECU Info",
                     command=self.read_ecu_info).pack(side="left", padx=5)
        ctk.CTkButton(advanced_buttons_frame, text="Test Comunicare",
                     command=self.test_communication).pack(side="left", padx=5)
        ctk.CTkButton(advanced_buttons_frame, text="Reset Adaptiv",
                     command=self.reset_adaptive).pack(side="left", padx=5)
        
    def create_sensor_displays(self):
        """Create sensor display widgets"""
        sensors = [
            ("RPM", "010C", "rpm"),
            ("Viteză", "010D", "km/h"),
            ("Temperatură Motor", "0105", "°C"),
            ("Presiune Combustibil", "010A", "kPa"),
            ("Poziție Accelerator", "0111", "%"),
            ("Nivel Combustibil", "012F", "%"),
            ("Tensiune Baterie", "0142", "V"),
            ("Temperatură Lichid Răcire", "0105", "°C"),
            ("Consum Combustibil", "015E", "L/100km"),
            ("Timp Avans", "010E", "°"),
            ("Presiune Intake", "010B", "kPa"),
            ("Poziție Marșarier", "0112", "%"),
            ("Temperatură Aer Intake", "010F", "°C"),
            ("Presiune Ulei", "010C", "kPa"),
            ("Temperatură Catalizator", "013C", "°C"),
            ("Presiune EGR", "010D", "kPa"),
            ("Poziție EGR", "010E", "%"),
            ("Temperatură EGR", "010F", "°C"),
        ]
        
        for i, (name, pid, unit) in enumerate(sensors):
            frame = ctk.CTkFrame(self.sensors_canvas)
            frame.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(frame, text=name, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
            
            value_label = ctk.CTkLabel(frame, text="N/A", font=ctk.CTkFont(size=16))
            value_label.pack(side="right", padx=10)
            
            self.sensor_displays[name] = {
                'pid': pid,
                'unit': unit,
                'label': value_label,
                'frame': frame
            }
            
    def read_sensor_data(self):
        """Read all sensor data"""
        if not self.connection_manager.is_connected:
            return
            
        for name, sensor in self.sensor_displays.items():
            value = self.connection_manager.read_sensor(sensor['pid'])
            if value is not None:
                sensor['label'].configure(text=f"{value:.1f} {sensor['unit']}")
                self.sensor_data[name] = value
                
    def read_error_codes(self):
        """Read diagnostic trouble codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        # Clear existing codes
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
            
        codes = self.connection_manager.read_error_codes()
        for code in codes:
            description = self.get_error_description(code)
            self.error_tree.insert("", "end", values=(code, description, "Activ"))
            
    def get_error_description(self, code):
        """Get error code description from loaded JSON"""
        return self.error_codes.get(code, f"Cod eroare {code}")
        
    def clear_error_codes(self):
        """Clear diagnostic trouble codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        if messagebox.askyesno("Confirmare", "Sigur doriți să ștergeți toate codurile de eroare?"):
            if self.connection_manager.clear_error_codes():
                messagebox.showinfo("Succes", "Codurile de eroare au fost șterse!")
                # Clear the tree
                for item in self.error_tree.get_children():
                    self.error_tree.delete(item)
            else:
                messagebox.showerror("Eroare", "Nu s-au putut șterge codurile de eroare!")
                
    def test_sensors(self):
        """Test all sensors"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        self.read_sensor_data()
        messagebox.showinfo("Test Senzori", "Testul senzorilor a fost completat!")
        
    def toggle_monitoring(self):
        """Toggle live monitoring"""
        if not hasattr(self, 'is_monitoring'):
            self.is_monitoring = False
            
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start live monitoring"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        self.is_monitoring = True
        self.monitor_btn.configure(text="Stop Monitorizare")
        self.live_data = []
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop live monitoring"""
        self.is_monitoring = False
        self.monitor_btn.configure(text="Start Monitorizare")
        
    def monitoring_loop(self):
        """Live monitoring loop"""
        start_time = time.time()
        
        while self.is_monitoring:
            if self.connection_manager.is_connected:
                # Read RPM and Speed for graph
                rpm = self.connection_manager.read_sensor("010C")
                speed = self.connection_manager.read_sensor("010D")
                
                if rpm is not None and speed is not None:
                    timestamp = time.time() - start_time
                    self.live_data.append((timestamp, rpm, speed))
                    
                    # Update graph
                    self.update_graph()
                    
            time.sleep(0.5)  # Update every 500ms
            
    def update_graph(self):
        """Update live monitoring graph"""
        if len(self.live_data) > 0:
            self.ax.clear()
            
            timestamps = [data[0] for data in self.live_data]
            rpms = [data[1] for data in self.live_data]
            speeds = [data[2] for data in self.live_data]
            
            # Plot RPM
            self.ax.plot(timestamps, rpms, 'r-', label='RPM', linewidth=2)
            self.ax.set_ylabel('RPM', color='red')
            self.ax.tick_params(axis='y', labelcolor='red')
            
            # Plot Speed on secondary axis
            ax2 = self.ax.twinx()
            ax2.plot(timestamps, speeds, 'b-', label='Viteză', linewidth=2)
            ax2.set_ylabel('Viteză (km/h)', color='blue')
            ax2.tick_params(axis='y', labelcolor='blue')
            
            self.ax.set_xlabel('Timp (secunde)')
            self.ax.set_title('Monitorizare Live - RPM și Viteză')
            self.ax.grid(True, alpha=0.3)
            
            # Keep only last 60 seconds of data
            if len(self.live_data) > 120:  # 60 seconds at 0.5s intervals
                self.live_data = self.live_data[-120:]
                
            self.canvas.draw()
            
    def save_live_data(self):
        """Save live monitoring data to CSV"""
        if not self.live_data:
            messagebox.showwarning("Avertisment", "Nu există date de salvat!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timp (s)', 'RPM', 'Viteză (km/h)'])
                for data in self.live_data:
                    writer.writerow(data)
                    
            messagebox.showinfo("Succes", f"Datele au fost salvate în {filename}")
            
    def export_error_codes(self):
        """Export error codes to CSV"""
        if not self.error_tree.get_children():
            messagebox.showwarning("Avertisment", "Nu există coduri de eroare de exportat!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Cod', 'Descriere', 'Status'])
                for item in self.error_tree.get_children():
                    values = self.error_tree.item(item)['values']
                    writer.writerow(values)
                    
            messagebox.showinfo("Succes", f"Codurile de eroare au fost exportate în {filename}")
            
    def read_ecu_info(self):
        """Read ECU information"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        self.ecu_info_text.delete("1.0", "end")
        
        # Read VIN
        vin = self.connection_manager.read_vin()
        if vin:
            self.ecu_info_text.insert("end", f"VIN: {vin}\n")
            self.vin_label.configure(text=f"VIN: {vin}")
        else:
            self.ecu_info_text.insert("end", "VIN: N/A\n")
            
        # Read other ECU info
        commands = [
            ("Calibration ID", "0904"),
            ("ECU Name", "090A"),
            ("System Name", "0909"),
        ]
        
        for name, command in commands:
            response = self.connection_manager.send_command(command)
            if response:
                self.ecu_info_text.insert("end", f"{name}: {response}\n")
            else:
                self.ecu_info_text.insert("end", f"{name}: N/A\n")
                
    def test_communication(self):
        """Test OBD2 communication"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        response = self.connection_manager.send_command("0100")
        if response and "41" in response:
            messagebox.showinfo("Test Comunicare", "Comunicarea OBD2 funcționează corect!")
        else:
            messagebox.showerror("Test Comunicare", "Probleme cu comunicarea OBD2!")
            
    def reset_adaptive(self):
        """Reset adaptive values"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        if messagebox.askyesno("Confirmare", "Sigur doriți să resetați valorile adaptive?"):
            response = self.connection_manager.send_command("04")
            if response and "44" in response:
                messagebox.showinfo("Succes", "Valorile adaptive au fost resetate!")
            else:
                messagebox.showerror("Eroare", "Nu s-au putut reseta valorile adaptive!")
                
    def run(self):
        """Run the application"""
        self.root.mainloop()
        
    def __del__(self):
        """Cleanup on exit"""
        if hasattr(self, 'connection_manager'):
            self.connection_manager.disconnect()

if __name__ == "__main__":
    app = OBD2Diagnostic()
    app.run() 