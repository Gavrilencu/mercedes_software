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
from modern_gui import (ModernConnectionFrame, ModernDashboardTab, 
                       ModernSensorsTab, ModernErrorCodesTab, 
                       ModernLiveMonitoringTab, ModernAdvancedTab)

# Set modern appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernOBD2Diagnostic:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🚗 OBD2 Diagnostic Tool - Mercedes Software")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
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
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
    def create_sidebar(self):
        """Create modern sidebar with navigation"""
        sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0, fg_color=("gray90", "gray20"))
        sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo and title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(logo_frame, text="🚗", font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(logo_frame, text="OBD2 Diagnostic", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(logo_frame, text="Mercedes Software", 
                    font=ctk.CTkFont(size=12), text_color=("gray", "lightgray")).pack()
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("📊", "Senzori", "sensors"),
            ("⚠️", "Coduri Eroare", "errors"),
            ("📈", "Monitorizare", "monitoring"),
            ("⚙️", "Avansat", "advanced")
        ]
        
        for i, (icon, text, key) in enumerate(nav_items):
            btn = ctk.CTkButton(sidebar, text=f"{icon} {text}",
                               command=lambda k=key: self.show_tab(k),
                               fg_color="transparent", text_color=("gray", "lightgray"),
                               hover_color=("gray70", "gray30"),
                               anchor="w", height=40, corner_radius=10)
            btn.grid(row=i+1, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Connection status at bottom
        status_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        status_frame.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkLabel(status_frame, text="Status Conectare:", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        self.sidebar_status = ctk.CTkLabel(status_frame, text="❌ Deconectat",
                                          text_color="red", font=ctk.CTkFont(size=12))
        self.sidebar_status.pack(anchor="w", pady=(5, 0))
        
    def create_main_content(self):
        """Create main content area with tabs"""
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
        
        # Create tabs
        self.tabs = {}
        self.tabs["dashboard"] = ModernDashboardTab(self.tab_container, self.connection_manager)
        self.tabs["sensors"] = ModernSensorsTab(self.tab_container, self.connection_manager)
        self.tabs["errors"] = ModernErrorCodesTab(self.tab_container, self.connection_manager, self.error_codes)
        self.tabs["monitoring"] = ModernLiveMonitoringTab(self.tab_container, self.connection_manager)
        self.tabs["advanced"] = ModernAdvancedTab(self.tab_container, self.connection_manager)
        
        # Show default tab
        self.show_tab("dashboard")
        
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
        
        # Update connection status
        self.update_connection_status()
        
    def update_connection_status(self):
        """Update connection status in sidebar"""
        if self.connection_manager.is_connected:
            self.sidebar_status.configure(text="✅ Conectat", text_color="green")
        else:
            self.sidebar_status.configure(text="❌ Deconectat", text_color="red")
        
    def run(self):
        """Run the application"""
        # Start status update loop
        self.update_status_loop()
        self.root.mainloop()
        
    def update_status_loop(self):
        """Update status periodically"""
        self.update_connection_status()
        self.root.after(1000, self.update_status_loop)  # Update every second
        
    def __del__(self):
        """Cleanup on exit"""
        if hasattr(self, 'connection_manager'):
            self.connection_manager.disconnect()

if __name__ == "__main__":
    app = ModernOBD2Diagnostic()
    app.run() 