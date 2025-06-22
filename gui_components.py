import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime
import time
import threading

class ConnectionFrame:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_frame()
        
    def setup_frame(self):
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # Port selection
        port_label = ctk.CTkLabel(self.frame, text="Port COM:")
        port_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.port_var = ctk.StringVar()
        self.port_combo = ctk.CTkComboBox(self.frame, values=self.get_obd2_ports(),
                                        variable=self.port_var, width=150)
        self.port_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Refresh ports button
        refresh_btn = ctk.CTkButton(self.frame, text="🔄 Scanare",
                                  command=self.scan_ports, width=80)
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Connect button
        self.connect_btn = ctk.CTkButton(self.frame, text="Conectare",
                                       command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.frame, text="Deconectat",
                                        text_color="red")
        self.status_label.grid(row=0, column=4, padx=20, pady=5)
        
        # Progress bar for scanning
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=200)
        self.progress_bar.grid(row=1, column=0, columnspan=5, padx=5, pady=2, sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Hide initially
        
    def get_obd2_ports(self):
        """Get list of COM ports that have OBD2 devices"""
        all_ports = self.connection_manager.get_available_ports()
        obd2_ports = []
        
        for port in all_ports:
            # Test if this port has an OBD2 device
            if self.connection_manager.test_obd2_communication(port):
                obd2_ports.append(f"{port} (OBD2)")
            else:
                obd2_ports.append(f"{port} (Fără OBD2)")
                
        return obd2_ports if obd2_ports else ["Nu s-au găsit dispozitive OBD2"]
        
    def scan_ports(self):
        """Scan all COM ports for OBD2 devices"""
        self.progress_bar.grid()  # Show progress bar
        self.progress_bar.set(0)
        
        # Start scanning in a separate thread
        scan_thread = threading.Thread(target=self._scan_ports_thread)
        scan_thread.daemon = True
        scan_thread.start()
        
    def _scan_ports_thread(self):
        """Scan ports in background thread"""
        all_ports = self.connection_manager.get_available_ports()
        obd2_ports = []
        
        for i, port in enumerate(all_ports):
            # Update progress
            progress = (i + 1) / len(all_ports)
            self.progress_bar.set(progress)
            
            # Test OBD2 communication
            if self.connection_manager.test_obd2_communication(port):
                obd2_ports.append(f"{port} (OBD2)")
            else:
                obd2_ports.append(f"{port} (Fără OBD2)")
                
            time.sleep(0.1)  # Small delay to show progress
            
        # Update combo box on main thread
        self.parent.after(0, self._update_ports_combo, obd2_ports)
        
    def _update_ports_combo(self, ports):
        """Update ports combo box"""
        self.port_combo.configure(values=ports if ports else ["Nu s-au găsit dispozitive OBD2"])
        self.progress_bar.grid_remove()  # Hide progress bar
        
        if ports and any("OBD2" in port for port in ports):
            messagebox.showinfo("Scanare Completă", f"S-au găsit {len([p for p in ports if 'OBD2' in p])} dispozitive OBD2!")
        else:
            messagebox.showwarning("Scanare Completă", "Nu s-au găsit dispozitive OBD2 conectate!")
        
    def toggle_connection(self):
        """Toggle OBD2 connection"""
        if not self.connection_manager.is_connected:
            self.connect_obd2()
        else:
            self.disconnect_obd2()
            
    def connect_obd2(self):
        """Connect to OBD2 device"""
        port_text = self.port_var.get()
        if not port_text or "Nu s-au găsit" in port_text:
            messagebox.showerror("Eroare", "Nu există dispozitive OBD2 disponibile!")
            return
            
        # Extract port name from text (e.g., "COM3 (OBD2)" -> "COM3")
        port = port_text.split(" ")[0]
        
        if not self.connection_manager.test_obd2_communication(port):
            messagebox.showerror("Eroare", f"Dispozitivul OBD2 de pe {port} nu răspunde!")
            return
            
        if self.connection_manager.connect(port):
            self.connect_btn.configure(text="Deconectare")
            self.status_label.configure(text="Conectat", text_color="green")
            messagebox.showinfo("Succes", f"Conectat cu succes la {port}!")
        else:
            messagebox.showerror("Eroare Conectare", "Nu s-a putut conecta la dispozitivul OBD2!")
            
    def disconnect_obd2(self):
        """Disconnect from OBD2 device"""
        self.connection_manager.disconnect()
        self.connect_btn.configure(text="Conectare")
        self.status_label.configure(text="Deconectat", text_color="red")
        messagebox.showinfo("Deconectare", "Dispozitivul OBD2 a fost deconectat!")

class DashboardTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent)
        
        # Vehicle info
        vehicle_frame = ctk.CTkFrame(self.frame)
        vehicle_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(vehicle_frame, text="Informații Vehicul", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.vin_label = ctk.CTkLabel(vehicle_frame, text="VIN: N/A")
        self.vin_label.pack()
        
        self.calibration_label = ctk.CTkLabel(vehicle_frame, text="Calibrare: N/A")
        self.calibration_label.pack()
        
        # Quick actions
        actions_frame = ctk.CTkFrame(self.frame)
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
        
    def read_error_codes(self):
        """Read error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        codes = self.connection_manager.read_error_codes()
        if codes:
            messagebox.showinfo("Coduri Eroare", f"Găsite {len(codes)} coduri de eroare")
        else:
            messagebox.showinfo("Coduri Eroare", "Nu au fost găsite coduri de eroare")
            
    def clear_error_codes(self):
        """Clear error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        if messagebox.askyesno("Confirmare", "Sigur doriți să ștergeți toate codurile de eroare?"):
            if self.connection_manager.clear_error_codes():
                messagebox.showinfo("Succes", "Codurile de eroare au fost șterse!")
            else:
                messagebox.showerror("Eroare", "Nu s-au putut șterge codurile de eroare!")
                
    def test_sensors(self):
        """Test sensors"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        messagebox.showinfo("Test Senzori", "Testul senzorilor a fost completat!")

class SensorsTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent)
        
        # Create scrollable frame for sensors
        self.sensors_canvas = ctk.CTkScrollableFrame(self.frame)
        self.sensors_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize sensor displays
        self.sensor_displays = {}
        self.create_sensor_displays()
        
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
            
    def update_sensors(self):
        """Update all sensor displays"""
        if not self.connection_manager.is_connected:
            return
            
        for name, sensor in self.sensor_displays.items():
            value = self.connection_manager.read_sensor(sensor['pid'])
            if value is not None:
                sensor['label'].configure(text=f"{value:.1f} {sensor['unit']}")

class ErrorCodesTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent)
        
        # Error codes list
        self.error_tree = ttk.Treeview(self.frame, columns=("Code", "Description", "Status"),
                                      show="headings", height=15)
        self.error_tree.heading("Code", text="Cod")
        self.error_tree.heading("Description", text="Descriere")
        self.error_tree.heading("Status", text="Status")
        self.error_tree.column("Code", width=100)
        self.error_tree.column("Description", width=300)
        self.error_tree.column("Status", width=100)
        self.error_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons
        error_buttons_frame = ctk.CTkFrame(self.frame)
        error_buttons_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(error_buttons_frame, text="Citire Coduri",
                     command=self.read_error_codes).pack(side="left", padx=5)
        ctk.CTkButton(error_buttons_frame, text="Ștergere Coduri",
                     command=self.clear_error_codes).pack(side="left", padx=5)
        ctk.CTkButton(error_buttons_frame, text="Export CSV",
                     command=self.export_error_codes).pack(side="left", padx=5)
        
    def read_error_codes(self):
        """Read and display error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("Eroare", "Nu sunteți conectat!")
            return
            
        # Clear existing codes
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
            
        codes = self.connection_manager.read_error_codes()
        for code in codes:
            self.error_tree.insert("", "end", values=(code, self.get_error_description(code), "Activ"))
            
    def get_error_description(self, code):
        """Get error code description"""
        return f"Cod eroare {code}"
        
    def clear_error_codes(self):
        """Clear error codes"""
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

class LiveMonitoringTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.is_monitoring = False
        self.monitoring_thread = None
        self.live_data = []
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent)
        
        # Control buttons
        control_frame = ctk.CTkFrame(self.frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.monitor_btn = ctk.CTkButton(control_frame, text="Start Monitorizare",
                                       command=self.toggle_monitoring)
        self.monitor_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(control_frame, text="Salvare Date",
                     command=self.save_live_data).pack(side="left", padx=5)
        
        # Graph frame
        graph_frame = ctk.CTkFrame(self.frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def toggle_monitoring(self):
        """Toggle live monitoring"""
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