"""
Sistem de configurare avansat pentru OBD2 Diagnostic Tool - Advanced Version
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
import threading
import time

@dataclass
class AdvancedConfig:
    """Configurație avansată pentru aplicație"""
    
    # Setări generale
    app_name: str = "OBD2 Diagnostic Tool - Advanced"
    version: str = "3.0.0"
    debug_mode: bool = False
    auto_save: bool = True
    auto_backup: bool = True
    
    # Setări conexiune
    connection_timeout: int = 10
    retry_attempts: int = 3
    baud_rate: int = 38400
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = "N"
    
    # Setări monitorizare
    monitoring_interval: float = 0.5
    max_data_points: int = 1000
    graph_update_rate: int = 30
    sensor_timeout: int = 5
    
    # Setări logging
    log_level: str = "INFO"
    log_file: str = "obd2_advanced.log"
    log_max_size: int = 10  # MB
    log_backup_count: int = 5
    
    # Setări rapoarte
    report_format: str = "PDF"
    report_template: str = "default"
    auto_generate_reports: bool = False
    report_save_path: str = "reports/"
    
    # Setări notificări
    enable_notifications: bool = True
    notification_sound: bool = True
    email_notifications: bool = False
    email_smtp_server: str = ""
    email_username: str = ""
    email_password: str = ""
    
    # Setări calibrare
    calibration_enabled: bool = False
    calibration_sensors: list = None
    calibration_interval: int = 24  # ore
    
    # Setări securitate
    encryption_enabled: bool = False
    encryption_key: str = ""
    session_timeout: int = 30  # minute
    
    def __post_init__(self):
        if self.calibration_sensors is None:
            self.calibration_sensors = ["010C", "010D", "0105", "010A"]
        if not os.path.exists(self.report_save_path):
            os.makedirs(self.report_save_path)

class AdvancedConfigManager:
    """Manager pentru configurația avansată"""
    
    def __init__(self, config_file: str = "advanced_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        self.setup_database()
        
    def load_config(self) -> AdvancedConfig:
        """Încarcă configurația din fișier"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AdvancedConfig(**data)
            else:
                return AdvancedConfig()
        except Exception as e:
            print(f"Eroare la încărcarea configurației: {e}")
            return AdvancedConfig()
    
    def save_config(self) -> bool:
        """Salvează configurația în fișier"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Eroare la salvarea configurației: {e}")
            return False
    
    def setup_logging(self):
        """Configurează sistemul de logging"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Configurare logging avansat
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Rotare log-uri
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            self.config.log_file,
            maxBytes=self.config.log_max_size * 1024 * 1024,
            backupCount=self.config.log_backup_count,
            encoding='utf-8'
        )
        logging.getLogger().addHandler(handler)
    
    def setup_database(self):
        """Configurează baza de date SQLite"""
        self.db_file = "obd2_advanced.db"
        self.init_database()
    
    def init_database(self):
        """Inițializează baza de date cu tabelele necesare"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Tabel pentru sesiuni
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        vehicle_vin TEXT,
                        total_errors INTEGER,
                        status TEXT
                    )
                ''')
                
                # Tabel pentru date senzori
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sensor_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        timestamp TIMESTAMP,
                        sensor_pid TEXT,
                        value REAL,
                        unit TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                ''')
                
                # Tabel pentru coduri eroare
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS error_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        code TEXT,
                        description TEXT,
                        severity TEXT,
                        timestamp TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                ''')
                
                # Tabel pentru rapoarte
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        report_type TEXT,
                        file_path TEXT,
                        generated_at TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                ''')
                
                # Tabel pentru calibrare
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS calibration (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sensor_pid TEXT,
                        calibration_value REAL,
                        reference_value REAL,
                        timestamp TIMESTAMP,
                        status TEXT
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Eroare la inițializarea bazei de date: {e}")
    
    def get_config(self) -> AdvancedConfig:
        """Returnează configurația curentă"""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """Actualizează configurația cu noile valori"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Reconfigurează logging dacă s-a schimbat nivelul
            if 'log_level' in kwargs:
                self.setup_logging()
            
            return self.save_config()
        except Exception as e:
            logging.error(f"Eroare la actualizarea configurației: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """Resetează configurația la valorile implicite"""
        self.config = AdvancedConfig()
        return self.save_config()

class SessionManager:
    """Manager pentru sesiunile de diagnostic"""
    
    def __init__(self, config_manager: AdvancedConfigManager):
        self.config_manager = config_manager
        self.current_session_id = None
        self.session_start_time = None
        
    def start_session(self, vehicle_vin: str = None) -> int:
        """Începe o nouă sesiune de diagnostic"""
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sessions (start_time, vehicle_vin, status)
                    VALUES (?, ?, ?)
                ''', (datetime.now(), vehicle_vin, 'active'))
                
                self.current_session_id = cursor.lastrowid
                self.session_start_time = datetime.now()
                
                logging.info(f"Sesiune nouă începută: ID {self.current_session_id}")
                return self.current_session_id
                
        except Exception as e:
            logging.error(f"Eroare la începerea sesiunii: {e}")
            return None
    
    def end_session(self, status: str = 'completed') -> bool:
        """Termină sesiunea curentă"""
        if not self.current_session_id:
            return False
            
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sessions 
                    SET end_time = ?, status = ?
                    WHERE id = ?
                ''', (datetime.now(), status, self.current_session_id))
                
                logging.info(f"Sesiune terminată: ID {self.current_session_id}, Status: {status}")
                self.current_session_id = None
                self.session_start_time = None
                return True
                
        except Exception as e:
            logging.error(f"Eroare la terminarea sesiunii: {e}")
            return False
    
    def log_sensor_data(self, sensor_pid: str, value: float, unit: str) -> bool:
        """Înregistrează date de la senzori în baza de date"""
        if not self.current_session_id:
            return False
            
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sensor_data (session_id, timestamp, sensor_pid, value, unit)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_session_id, datetime.now(), sensor_pid, value, unit))
                
                return True
                
        except Exception as e:
            logging.error(f"Eroare la înregistrarea datelor senzor: {e}")
            return False
    
    def log_error_code(self, code: str, description: str, severity: str = 'medium') -> bool:
        """Înregistrează un cod de eroare în baza de date"""
        if not self.current_session_id:
            return False
            
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO error_codes (session_id, code, description, severity, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_session_id, code, description, severity, datetime.now()))
                
                return True
                
        except Exception as e:
            logging.error(f"Eroare la înregistrarea codului de eroare: {e}")
            return False

# Instanță globală
config_manager = AdvancedConfigManager()
session_manager = SessionManager(config_manager) 