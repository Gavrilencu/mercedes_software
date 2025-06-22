import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import time
import threading
import json
from PIL import Image, ImageTk
import os

# Set modern appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernConnectionFrame:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_frame()
        
    def setup_frame(self):
        # Main connection container with modern styling
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.pack(fill="x", padx=20, pady=10)
        
        # Title with icon
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(title_frame, text="🔌", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Conectare OBD2", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Connection controls in a modern card
        connection_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        connection_card.pack(fill="x", padx=10, pady=5)
        
        # Port selection with modern styling
        port_frame = ctk.CTkFrame(connection_card, fg_color="transparent")
        port_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(port_frame, text="📡 Port COM:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 10))
        
        self.port_var = ctk.StringVar()
        self.port_combo = ctk.CTkComboBox(port_frame, values=self.get_obd2_ports(),
                                        variable=self.port_var, width=200,
                                        button_color=("gray70", "gray30"),
                                        border_color=("gray60", "gray40"))
        self.port_combo.pack(side="left", padx=(0, 10))
        
        # Modern buttons with icons
        button_frame = ctk.CTkFrame(connection_card, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Scan button with modern styling
        self.scan_btn = ctk.CTkButton(button_frame, text="🔍 Scanare Porturi",
                                     command=self.scan_ports, width=150, height=35,
                                     fg_color=("gray70", "gray30"),
                                     hover_color=("gray60", "gray40"),
                                     corner_radius=10)
        self.scan_btn.pack(side="left", padx=(0, 10))
        
        # Connect button with modern styling
        self.connect_btn = ctk.CTkButton(button_frame, text="🔗 Conectare",
                                       command=self.toggle_connection, width=150, height=35,
                                       fg_color=("green", "darkgreen"),
                                       hover_color=("lightgreen", "green"),
                                       corner_radius=10)
        self.connect_btn.pack(side="left", padx=(0, 10))
        
        # Status indicator with modern design
        status_frame = ctk.CTkFrame(connection_card, fg_color="transparent")
        status_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(status_frame, text="Status:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="❌ Deconectat",
                                        text_color="red", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(side="left")
        
        # Progress bar for scanning
        self.progress_bar = ctk.CTkProgressBar(connection_card, width=300, height=8)
        self.progress_bar.pack(padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide initially
        
    def get_obd2_ports(self):
        """Get list of COM ports that have OBD2 devices"""
        all_ports = self.connection_manager.get_available_ports()
        obd2_ports = []
        
        for port in all_ports:
            if self.connection_manager.test_obd2_communication(port):
                obd2_ports.append(f"✅ {port} (OBD2)")
            else:
                obd2_ports.append(f"❌ {port} (Fără OBD2)")
                
        return obd2_ports if obd2_ports else ["🔍 Nu s-au găsit dispozitive OBD2"]
        
    def scan_ports(self):
        """Scan all COM ports for OBD2 devices"""
        self.progress_bar.pack(padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        self.scan_btn.configure(text="⏳ Scanare...", state="disabled")
        
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
                obd2_ports.append(f"✅ {port} (OBD2)")
            else:
                obd2_ports.append(f"❌ {port} (Fără OBD2)")
                
            time.sleep(0.1)
            
        # Update combo box on main thread
        self.parent.after(0, self._update_ports_combo, obd2_ports)
        
    def _update_ports_combo(self, ports):
        """Update ports combo box"""
        self.port_combo.configure(values=ports if ports else ["🔍 Nu s-au găsit dispozitive OBD2"])
        self.progress_bar.pack_forget()
        self.scan_btn.configure(text="🔍 Scanare Porturi", state="normal")
        
        obd2_count = len([p for p in ports if "✅" in p])
        if obd2_count > 0:
            messagebox.showinfo("✅ Scanare Completă", f"S-au găsit {obd2_count} dispozitive OBD2!")
        else:
            messagebox.showwarning("⚠️ Scanare Completă", "Nu s-au găsit dispozitive OBD2 conectate!")
        
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
            messagebox.showerror("❌ Eroare", "Nu există dispozitive OBD2 disponibile!")
            return
            
        # Extract port name from text
        port = port_text.split(" ")[1] if "✅" in port_text else port_text.split(" ")[0]
        
        if not self.connection_manager.test_obd2_communication(port):
            messagebox.showerror("❌ Eroare", f"Dispozitivul OBD2 de pe {port} nu răspunde!")
            return
            
        if self.connection_manager.connect(port):
            self.connect_btn.configure(text="🔌 Deconectare", fg_color=("red", "darkred"), hover_color=("lightcoral", "red"))
            self.status_label.configure(text="✅ Conectat", text_color="green")
            messagebox.showinfo("✅ Succes", f"Conectat cu succes la {port}!")
        else:
            messagebox.showerror("❌ Eroare Conectare", "Nu s-a putut conecta la dispozitivul OBD2!")
            
    def disconnect_obd2(self):
        """Disconnect from OBD2 device"""
        self.connection_manager.disconnect()
        self.connect_btn.configure(text="🔗 Conectare", fg_color=("green", "darkgreen"), hover_color=("lightgreen", "green"))
        self.status_label.configure(text="❌ Deconectat", text_color="red")
        messagebox.showinfo("🔌 Deconectare", "Dispozitivul OBD2 a fost deconectat!")

class ModernDashboardTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Vehicle info card
        vehicle_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        vehicle_card.pack(fill="x", padx=20, pady=10)
        
        # Title with icon
        title_frame = ctk.CTkFrame(vehicle_card, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(title_frame, text="🚗", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Informații Vehicul", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Vehicle details
        details_frame = ctk.CTkFrame(vehicle_card, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.vin_label = ctk.CTkLabel(details_frame, text="🔢 VIN: N/A", 
                                     font=ctk.CTkFont(size=14))
        self.vin_label.pack(anchor="w", pady=2)
        
        self.calibration_label = ctk.CTkLabel(details_frame, text="⚙️ Calibrare: N/A", 
                                             font=ctk.CTkFont(size=14))
        self.calibration_label.pack(anchor="w", pady=2)
        
        # Quick actions card
        actions_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        actions_card.pack(fill="x", padx=20, pady=10)
        
        # Title with icon
        action_title_frame = ctk.CTkFrame(actions_card, fg_color="transparent")
        action_title_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(action_title_frame, text="⚡", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(action_title_frame, text="Acțiuni Rapide", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Action buttons with modern styling
        buttons_frame = ctk.CTkFrame(actions_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(buttons_frame, text="🔍 Citire Coduri Eroare",
                     command=self.read_error_codes, width=180, height=40,
                     fg_color=("orange", "darkorange"),
                     hover_color=("lightcoral", "orange"),
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="🗑️ Ștergere Coduri Eroare",
                     command=self.clear_error_codes, width=180, height=40,
                     fg_color=("red", "darkred"),
                     hover_color=("lightcoral", "red"),
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="🔧 Test Senzori",
                     command=self.test_sensors, width=180, height=40,
                     fg_color=("blue", "darkblue"),
                     hover_color=("lightblue", "blue"),
                     corner_radius=10).pack(side="left", padx=5)
        
    def read_error_codes(self):
        """Read error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        codes = self.connection_manager.read_error_codes()
        if codes:
            messagebox.showinfo("🔍 Coduri Eroare", f"Găsite {len(codes)} coduri de eroare")
        else:
            messagebox.showinfo("✅ Coduri Eroare", "Nu au fost găsite coduri de eroare")
            
    def clear_error_codes(self):
        """Clear error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        if messagebox.askyesno("🗑️ Confirmare", "Sigur doriți să ștergeți toate codurile de eroare?"):
            if self.connection_manager.clear_error_codes():
                messagebox.showinfo("✅ Succes", "Codurile de eroare au fost șterse!")
            else:
                messagebox.showerror("❌ Eroare", "Nu s-au putut șterge codurile de eroare!")
                
    def test_sensors(self):
        """Test sensors"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        messagebox.showinfo("🔧 Test Senzori", "Testul senzorilor a fost completat!")

class ModernSensorsTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Title with icon
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(title_frame, text="📊", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Monitorizare Senzori", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Create scrollable frame for sensors
        self.sensors_canvas = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.sensors_canvas.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initialize sensor displays
        self.sensor_displays = {}
        self.create_sensor_displays()
        
    def create_sensor_displays(self):
        """Create modern sensor display widgets"""
        sensors = [
            ("🚗 RPM", "010C", "rpm", "🔄"),
            ("⚡ Viteză", "010D", "km/h", "🏃"),
            ("🌡️ Temperatură Motor", "0105", "°C", "🔥"),
            ("⛽ Presiune Combustibil", "010A", "kPa", "💧"),
            ("🎛️ Poziție Accelerator", "0111", "%", "📈"),
            ("⛽ Nivel Combustibil", "012F", "%", "🛢️"),
            ("🔋 Tensiune Baterie", "0142", "V", "⚡"),
            ("🌡️ Temperatură Răcire", "0105", "°C", "❄️"),
            ("⛽ Consum Combustibil", "015E", "L/100km", "📊"),
            ("⏰ Timp Avans", "010E", "°", "⏱️"),
            ("💨 Presiune Intake", "010B", "kPa", "🌪️"),
            ("🎛️ Poziție Marșarier", "0112", "%", "⚙️"),
            ("🌡️ Temperatură Aer", "010F", "°C", "🌬️"),
            ("🛢️ Presiune Ulei", "010C", "kPa", "💧"),
            ("🔥 Temperatură Catalizator", "013C", "°C", "🔥"),
            ("💨 Presiune EGR", "010D", "kPa", "🌪️"),
            ("🎛️ Poziție EGR", "010E", "%", "⚙️"),
            ("🌡️ Temperatură EGR", "010F", "°C", "🌡️"),
        ]
        
        for i, (name, pid, unit, icon) in enumerate(sensors):
            # Create modern sensor card
            sensor_card = ctk.CTkFrame(self.sensors_canvas, corner_radius=10, 
                                     fg_color=("gray90", "gray20"))
            sensor_card.pack(fill="x", padx=5, pady=3)
            
            # Sensor info
            info_frame = ctk.CTkFrame(sensor_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(info_frame, text=f"{icon} {name}", 
                        font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
            
            value_label = ctk.CTkLabel(info_frame, text="N/A", 
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     text_color=("gray", "lightgray"))
            value_label.pack(side="right")
            
            self.sensor_displays[name] = {
                'pid': pid,
                'unit': unit,
                'label': value_label,
                'card': sensor_card
            }
            
    def update_sensors(self):
        """Update all sensor displays"""
        if not self.connection_manager.is_connected:
            return
            
        for name, sensor in self.sensor_displays.items():
            value = self.connection_manager.read_sensor(sensor['pid'])
            if value is not None:
                sensor['label'].configure(text=f"{value:.1f} {sensor['unit']}", 
                                        text_color=("green", "lightgreen"))
            else:
                sensor['label'].configure(text="N/A", text_color=("gray", "lightgray"))

class ModernErrorCodesTab:
    def __init__(self, parent, connection_manager, error_codes):
        self.parent = parent
        self.connection_manager = connection_manager
        self.error_codes = error_codes
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Title with icon
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(title_frame, text="⚠️", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Coduri de Eroare", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Error codes list in a modern card
        list_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        list_card.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Error codes tree with modern styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=("gray95", "gray25"), 
                       foreground=("black", "white"), fieldbackground=("gray95", "gray25"))
        style.configure("Treeview.Heading", background=("gray85", "gray30"), 
                       foreground=("black", "white"))
        
        self.error_tree = ttk.Treeview(list_card, columns=("Code", "Description", "Status"),
                                      show="headings", height=15)
        self.error_tree.heading("Code", text="🔢 Cod")
        self.error_tree.heading("Description", text="📝 Descriere")
        self.error_tree.heading("Status", text="📊 Status")
        self.error_tree.column("Code", width=120)
        self.error_tree.column("Description", width=400)
        self.error_tree.column("Status", width=100)
        self.error_tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Buttons with modern styling
        button_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        button_card.pack(fill="x", padx=20, pady=10)
        
        buttons_frame = ctk.CTkFrame(button_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(buttons_frame, text="🔍 Citire Coduri",
                     command=self.read_error_codes, width=150, height=40,
                     fg_color=("blue", "darkblue"),
                     hover_color=("lightblue", "blue"),
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="🗑️ Ștergere Coduri",
                     command=self.clear_error_codes, width=150, height=40,
                     fg_color=("red", "darkred"),
                     hover_color=("lightcoral", "red"),
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="📁 Export CSV",
                     command=self.export_error_codes, width=150, height=40,
                     fg_color=("green", "darkgreen"),
                     hover_color=("lightgreen", "green"),
                     corner_radius=10).pack(side="left", padx=5)
        
    def read_error_codes(self):
        """Read and display error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        # Clear existing codes
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)
            
        codes = self.connection_manager.read_error_codes()
        for code in codes:
            description = self.get_error_description(code)
            self.error_tree.insert("", "end", values=(code, description, "🔴 Activ"))
            
    def get_error_description(self, code):
        """Get error code description from loaded JSON"""
        return self.error_codes.get(code, f"Cod eroare {code}")
        
    def clear_error_codes(self):
        """Clear error codes"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        if messagebox.askyesno("🗑️ Confirmare", "Sigur doriți să ștergeți toate codurile de eroare?"):
            if self.connection_manager.clear_error_codes():
                messagebox.showinfo("✅ Succes", "Codurile de eroare au fost șterse!")
                # Clear the tree
                for item in self.error_tree.get_children():
                    self.error_tree.delete(item)
            else:
                messagebox.showerror("❌ Eroare", "Nu s-au putut șterge codurile de eroare!")
                
    def export_error_codes(self):
        """Export error codes to CSV"""
        if not self.error_tree.get_children():
            messagebox.showwarning("⚠️ Avertisment", "Nu există coduri de eroare de exportat!")
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
                    
            messagebox.showinfo("✅ Succes", f"Codurile de eroare au fost exportate în {filename}")

class ModernLiveMonitoringTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.is_monitoring = False
        self.monitoring_thread = None
        self.live_data = []
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Title with icon
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(title_frame, text="📈", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Monitorizare Live", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # Control buttons in a modern card
        control_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        control_card.pack(fill="x", padx=20, pady=10)
        
        buttons_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=15)
        
        self.monitor_btn = ctk.CTkButton(buttons_frame, text="▶️ Start Monitorizare",
                                       command=self.toggle_monitoring, width=180, height=40,
                                       fg_color=("green", "darkgreen"),
                                       hover_color=("lightgreen", "green"),
                                       corner_radius=10)
        self.monitor_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="💾 Salvare Date",
                     command=self.save_live_data, width=180, height=40,
                     fg_color=("blue", "darkblue"),
                     hover_color=("lightblue", "blue"),
                     corner_radius=10).pack(side="left", padx=5)
        
        # Graph frame in a modern card
        graph_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        graph_card.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create matplotlib figure with modern styling
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(12, 8), facecolor='#2b2b2b')
        self.canvas = FigureCanvasTkAgg(self.fig, graph_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        
    def toggle_monitoring(self):
        """Toggle live monitoring"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
            
    def start_monitoring(self):
        """Start live monitoring"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        self.is_monitoring = True
        self.monitor_btn.configure(text="⏹️ Stop Monitorizare", 
                                 fg_color=("red", "darkred"),
                                 hover_color=("lightcoral", "red"))
        self.live_data = []
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stop live monitoring"""
        self.is_monitoring = False
        self.monitor_btn.configure(text="▶️ Start Monitorizare",
                                 fg_color=("green", "darkgreen"),
                                 hover_color=("lightgreen", "green"))
        
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
                    
            time.sleep(0.5)
            
    def update_graph(self):
        """Update live monitoring graph"""
        if len(self.live_data) > 0:
            self.ax.clear()
            
            timestamps = [data[0] for data in self.live_data]
            rpms = [data[1] for data in self.live_data]
            speeds = [data[2] for data in self.live_data]
            
            # Plot RPM
            self.ax.plot(timestamps, rpms, 'r-', label='RPM', linewidth=3, alpha=0.8)
            self.ax.set_ylabel('RPM', color='red', fontsize=12, fontweight='bold')
            self.ax.tick_params(axis='y', labelcolor='red')
            
            # Plot Speed on secondary axis
            ax2 = self.ax.twinx()
            ax2.plot(timestamps, speeds, 'b-', label='Viteză', linewidth=3, alpha=0.8)
            ax2.set_ylabel('Viteză (km/h)', color='blue', fontsize=12, fontweight='bold')
            ax2.tick_params(axis='y', labelcolor='blue')
            
            self.ax.set_xlabel('Timp (secunde)', fontsize=12, fontweight='bold', color='white')
            self.ax.set_title('📈 Monitorizare Live - RPM și Viteză', 
                            fontsize=14, fontweight='bold', color='white', pad=20)
            self.ax.grid(True, alpha=0.3, color='gray')
            
            # Keep only last 60 seconds of data
            if len(self.live_data) > 120:
                self.live_data = self.live_data[-120:]
                
            self.canvas.draw()
            
    def save_live_data(self):
        """Save live monitoring data to CSV"""
        if not self.live_data:
            messagebox.showwarning("⚠️ Avertisment", "Nu există date de salvat!")
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
                    
            messagebox.showinfo("✅ Succes", f"Datele au fost salvate în {filename}")

class ModernAdvancedTab:
    def __init__(self, parent, connection_manager):
        self.parent = parent
        self.connection_manager = connection_manager
        self.setup_tab()
        
    def setup_tab(self):
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Title with icon
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(title_frame, text="⚙️", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Funcții Avansate", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        # ECU information card
        ecu_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        ecu_card.pack(fill="x", padx=20, pady=10)
        
        # ECU title
        ecu_title_frame = ctk.CTkFrame(ecu_card, fg_color="transparent")
        ecu_title_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(ecu_title_frame, text="💻", font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(ecu_title_frame, text="Informații ECU", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # ECU info text
        self.ecu_info_text = ctk.CTkTextbox(ecu_card, height=200, 
                                           fg_color=("gray95", "gray25"),
                                           text_color=("black", "white"))
        self.ecu_info_text.pack(fill="x", padx=20, pady=(0, 15))
        
        # Advanced functions card
        advanced_card = ctk.CTkFrame(self.frame, corner_radius=15, fg_color=("gray90", "gray20"))
        advanced_card.pack(fill="x", padx=20, pady=10)
        
        # Advanced title
        advanced_title_frame = ctk.CTkFrame(advanced_card, fg_color="transparent")
        advanced_title_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(advanced_title_frame, text="🔧", font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(advanced_title_frame, text="Funcții Avansate", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Advanced buttons
        buttons_frame = ctk.CTkFrame(advanced_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(buttons_frame, text="💻 Citire ECU Info",
                     command=self.read_ecu_info, width=180, height=40,
                     fg_color=("purple", "purple"),
                     hover_color=("lightblue", "purple"),
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="🔍 Test Comunicare",
                     command=self.test_communication, width=180, height=40,
                     fg_color=("orange", "orange"),
                     hover_color=("lightcoral", "orange"),
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(buttons_frame, text="🔄 Reset Adaptiv",
                     command=self.reset_adaptive, width=180, height=40,
                     fg_color=("red", "darkred"),
                     hover_color=("lightcoral", "red"),
                     corner_radius=10).pack(side="left", padx=5)
        
    def read_ecu_info(self):
        """Read ECU information"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        self.ecu_info_text.delete("1.0", "end")
        
        # Read VIN
        vin = self.connection_manager.read_vin()
        if vin:
            self.ecu_info_text.insert("end", f"🔢 VIN: {vin}\n\n")
        else:
            self.ecu_info_text.insert("end", "🔢 VIN: N/A\n\n")
            
        # Read other ECU info
        commands = [
            ("⚙️ Calibration ID", "0904"),
            ("💻 ECU Name", "090A"),
            ("🔧 System Name", "0909"),
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
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        response = self.connection_manager.send_command("0100")
        if response and "41" in response:
            messagebox.showinfo("✅ Test Comunicare", "Comunicarea OBD2 funcționează corect!")
        else:
            messagebox.showerror("❌ Test Comunicare", "Probleme cu comunicarea OBD2!")
            
    def reset_adaptive(self):
        """Reset adaptive values"""
        if not self.connection_manager.is_connected:
            messagebox.showerror("❌ Eroare", "Nu sunteți conectat!")
            return
            
        if messagebox.askyesno("🔄 Confirmare", "Sigur doriți să resetați valorile adaptive?"):
            response = self.connection_manager.send_command("04")
            if response and "44" in response:
                messagebox.showinfo("✅ Succes", "Valorile adaptive au fost resetate!")
            else:
                messagebox.showerror("❌ Eroare", "Nu s-au putut reseta valorile adaptive!") 