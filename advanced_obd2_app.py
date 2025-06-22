"""
OBD2 Diagnostic Tool - Advanced Version
Aplicație completă cu funcționalități avansate pentru diagnosticarea vehiculelor
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
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
import logging

# Import our modules
from connection_manager import OBD2Connection
from modern_gui import (ModernConnectionFrame, ModernDashboardTab, 
                       ModernSensorsTab, ModernErrorCodesTab, 
                       ModernLiveMonitoringTab, ModernAdvancedTab)

# Import advanced modules
from advanced_config import AdvancedConfigManager, SessionManager
from advanced_notifications import NotificationManager, NotificationPresets
from advanced_reports import ReportGenerator
from advanced_calibration import CalibrationManager

# Set modern appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdvancedOBD2Diagnostic:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🚗 OBD2 Diagnostic Tool - Advanced Version")
        self.root.geometry("1800x1100")
        self.root.minsize(1600, 1000)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Initialize advanced managers
        self.config_manager = AdvancedConfigManager()
        self.connection_manager = OBD2Connection()
        self.session_manager = SessionManager(self.config_manager)
        self.notification_manager = NotificationManager(self.config_manager)
        self.report_generator = ReportGenerator(self.config_manager)
        self.calibration_manager = CalibrationManager(self.config_manager, self.connection_manager)
        
        # Load error codes
        self.error_codes = self.load_error_codes()
        
        # Data storage
        self.sensor_data = {}
        self.error_codes_list = []
        self.live_data = []
        self.current_session_id = None
        
        # Initialize status indicators
        self.status_indicators = {}
        
        # Initialize GUI
        self.setup_gui()
        
        # Start background tasks
        self.start_background_tasks()
        
    def load_error_codes(self):
        """Load error codes from JSON file"""
        try:
            with open('error_codes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning("error_codes.json not found, using empty dictionary")
            return {}
        except Exception as e:
            logging.error(f"Error loading error codes: {e}")
            return {}
        
    def setup_gui(self):
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        
    def create_sidebar(self):
        """Create advanced sidebar with navigation"""
        sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0, fg_color=("gray90", "gray20"))
        sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(logo_frame, text="🚗", font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(logo_frame, text="OBD2 Diagnostic", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(logo_frame, text="Advanced Version", 
                    font=ctk.CTkFont(size=12), text_color=("blue", "lightblue")).pack()
        ctk.CTkLabel(logo_frame, text="Mercedes Software", 
                    font=ctk.CTkFont(size=10), text_color=("gray", "lightgray")).pack()
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("📊", "Senzori", "sensors"),
            ("⚠️", "Coduri Eroare", "errors"),
            ("📈", "Monitorizare", "monitoring"),
            ("⚙️", "Avansat", "advanced"),
            ("🔧", "Calibrare", "calibration"),
            ("📋", "Rapoarte", "reports"),
            ("⚙️", "Configurare", "settings")
        ]
        
        for i, (icon, text, key) in enumerate(nav_items):
            btn = ctk.CTkButton(sidebar, text=f"{icon} {text}",
                               command=lambda k=key: self.show_tab(k),
                               fg_color="transparent", text_color=("gray", "lightgray"),
                               hover_color=("gray70", "gray30"),
                               anchor="w", height=40, corner_radius=10)
            btn.grid(row=i+1, column=0, padx=20, pady=3, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Session info
        session_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        session_frame.grid(row=8, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(session_frame, text="📊 Sesiune Activă:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        self.session_info = ctk.CTkLabel(session_frame, text="❌ Fără sesiune",
                                        text_color="red", font=ctk.CTkFont(size=10))
        self.session_info.pack(anchor="w", pady=(5, 0))
        
        # Connection status
        status_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        status_frame.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(status_frame, text="🔌 Status Conectare:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        self.sidebar_status = ctk.CTkLabel(status_frame, text="❌ Deconectat",
                                          text_color="red", font=ctk.CTkFont(size=10))
        self.sidebar_status.pack(anchor="w", pady=(5, 0))
        
    def create_main_content(self):
        """Create main content area with advanced tabs"""
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Connection frame at top
        self.connection_frame = ModernConnectionFrame(self.main_frame, self.connection_manager)
        self.connection_frame.frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Tab container
        self.tab_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tab_container.grid(row=1, column=0, sticky="nsew")
        
        # Create advanced tabs
        self.tabs = {}
        self.tabs["dashboard"] = AdvancedDashboardTab(self.tab_container, self)
        self.tabs["sensors"] = AdvancedSensorsTab(self.tab_container, self)
        self.tabs["errors"] = AdvancedErrorCodesTab(self.tab_container, self)
        self.tabs["monitoring"] = AdvancedLiveMonitoringTab(self.tab_container, self)
        self.tabs["advanced"] = AdvancedFunctionsTab(self.tab_container, self)
        self.tabs["calibration"] = AdvancedCalibrationTab(self.tab_container, self)
        self.tabs["reports"] = AdvancedReportsTab(self.tab_container, self)
        self.tabs["settings"] = AdvancedSettingsTab(self.tab_container, self)
        
        # Show default tab
        self.show_tab("dashboard")
        
    def create_status_bar(self):
        """Create advanced status bar"""
        status_bar = ctk.CTkFrame(self.root, height=30, fg_color=("gray85", "gray25"))
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        status_bar.grid_columnconfigure(1, weight=1)
        
        # Status indicators
        self.status_indicators = {}
        
        indicators = [
            ("🔌", "Conectare", "disconnected"),
            ("📊", "Sesiune", "no_session"),
            ("🔧", "Calibrare", "no_calibration"),
            ("📈", "Monitorizare", "not_monitoring")
        ]
        
        for i, (icon, text, key) in enumerate(indicators):
            indicator_frame = ctk.CTkFrame(status_bar, fg_color="transparent")
            indicator_frame.grid(row=0, column=i, padx=10, pady=5)
            
            ctk.CTkLabel(indicator_frame, text=icon, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))
            label = ctk.CTkLabel(indicator_frame, text=text, font=ctk.CTkFont(size=10))
            label.pack(side="left")
            
            self.status_indicators[key] = label
        
        # System info
        system_frame = ctk.CTkFrame(status_bar, fg_color="transparent")
        system_frame.grid(row=0, column=4, padx=10, pady=5)
        
        self.system_info = ctk.CTkLabel(system_frame, text="Sistem: Ready", 
                                       font=ctk.CTkFont(size=10))
        self.system_info.pack()
        
    def show_tab(self, tab_name):
        """Show selected tab and update navigation"""
        # Hide all tabs
        for tab in self.tabs.values():
            tab.frame.pack_forget()
        
        # Show selected tab
        self.tabs[tab_name].frame.pack(fill="both", expand=True)
        
        # Update navigation buttons
        for key, btn in self.nav_buttons.items():
            if key == tab_name:
                btn.configure(fg_color=("gray70", "gray30"), text_color=("black", "white"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray", "lightgray"))
        
        # Update status
        self.update_status()
        
    def update_status(self):
        """Update all status indicators"""
        # Connection status
        if self.connection_manager.is_connected:
            self.sidebar_status.configure(text="✅ Conectat", text_color="green")
            if "disconnected" in self.status_indicators:
                self.status_indicators["disconnected"].configure(text="Conectat", text_color="green")
        else:
            self.sidebar_status.configure(text="❌ Deconectat", text_color="red")
            if "disconnected" in self.status_indicators:
                self.status_indicators["disconnected"].configure(text="Deconectat", text_color="red")
        
        # Session status
        if self.current_session_id:
            self.session_info.configure(text=f"✅ Sesiune #{self.current_session_id}", text_color="green")
            if "no_session" in self.status_indicators:
                self.status_indicators["no_session"].configure(text="Activă", text_color="green")
        else:
            self.session_info.configure(text="❌ Fără sesiune", text_color="red")
            if "no_session" in self.status_indicators:
                self.status_indicators["no_session"].configure(text="Inactivă", text_color="red")
        
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        # Status update loop
        self.update_status_loop()
        
        # Auto-save loop
        if self.config_manager.get_config().auto_save:
            self.auto_save_loop()
        
        # Calibration check loop
        self.calibration_check_loop()
        
    def update_status_loop(self):
        """Update status periodically"""
        self.update_status()
        self.root.after(1000, self.update_status_loop)
        
    def auto_save_loop(self):
        """Auto-save data periodically"""
        if self.current_session_id and self.live_data:
            # Save current session data
            self.session_manager.log_sensor_data("auto_save", len(self.live_data), "points")
        
        self.root.after(30000, self.auto_save_loop)  # Every 30 seconds
        
    def calibration_check_loop(self):
        """Check calibration status periodically"""
        try:
            for sensor_pid in self.calibration_manager.calibration_sensors:
                if self.calibration_manager.needs_calibration(sensor_pid):
                    self.notification_manager.add_notification(
                        "🔧 Calibrare Necesară",
                        f"Senzorul {sensor_pid} necesită calibrare",
                        "warning",
                        3
                    )
        except Exception as e:
            logging.error(f"Eroare la verificarea calibrei: {e}")
        
        self.root.after(3600000, self.calibration_check_loop)  # Every hour
        
    def start_session(self, vehicle_vin: str = None):
        """Start a new diagnostic session"""
        if self.current_session_id:
            self.end_session()
        
        self.current_session_id = self.session_manager.start_session(vehicle_vin)
        if self.current_session_id:
            self.notification_manager.show_quick_notification(
                "📊 Sesiune Începută",
                f"Sesiunea #{self.current_session_id} a fost inițiată"
            )
            logging.info(f"Sesiune nouă începută: {self.current_session_id}")
        
    def end_session(self):
        """End current diagnostic session"""
        if self.current_session_id:
            self.session_manager.end_session()
            self.notification_manager.show_quick_notification(
                "📊 Sesiune Terminată",
                f"Sesiunea #{self.current_session_id} a fost închisă"
            )
            logging.info(f"Sesiune terminată: {self.current_session_id}")
            self.current_session_id = None
        
    def run(self):
        """Run the advanced application"""
        try:
            # Show welcome notification
            self.notification_manager.show_quick_notification(
                "🚗 OBD2 Diagnostic Tool",
                "Versiunea avansată a fost pornită cu succes!"
            )
            
            self.root.mainloop()
        except Exception as e:
            logging.error(f"Eroare în aplicația principală: {e}")
        finally:
            # Cleanup on exit
            self.cleanup()
        
    def cleanup(self):
        """Cleanup resources on exit"""
        try:
            # End current session
            if self.current_session_id:
                self.end_session()
            
            # Stop notification system
            self.notification_manager.stop_notification_system()
            
            # Disconnect OBD2
            if self.connection_manager.is_connected:
                self.connection_manager.disconnect()
            
            logging.info("Aplicația a fost închisă cu succes")
            
        except Exception as e:
            logging.error(f"Eroare la cleanup: {e}")
        
    def __del__(self):
        """Destructor"""
        self.cleanup()

# Import advanced tab classes (to be implemented)
class AdvancedDashboardTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedSensorsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedErrorCodesTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedLiveMonitoringTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedFunctionsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedCalibrationTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedReportsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

class AdvancedSettingsTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Implementation will be added

if __name__ == "__main__":
    app = AdvancedOBD2Diagnostic()
    app.run() 