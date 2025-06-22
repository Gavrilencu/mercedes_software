"""
Sistem de calibrare avansat pentru OBD2 Diagnostic Tool - Advanced Version
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import threading
import time
from dataclasses import dataclass
import json
import os

@dataclass
class CalibrationPoint:
    """Punct de calibrare"""
    sensor_pid: str
    reference_value: float
    measured_value: float
    timestamp: datetime
    confidence: float
    status: str

@dataclass
class CalibrationResult:
    """Rezultat calibrare"""
    sensor_pid: str
    calibration_factor: float
    offset: float
    r_squared: float
    confidence: float
    last_calibration: datetime
    status: str

class CalibrationManager:
    """Manager pentru sistemul de calibrare"""
    
    def __init__(self, config_manager, connection_manager):
        self.config_manager = config_manager
        self.connection_manager = connection_manager
        self.calibration_data = {}
        self.calibration_results = {}
        self.is_calibrating = False
        self.calibration_thread = None
        
        # Senzori pentru calibrare
        self.calibration_sensors = {
            "010C": {  # RPM
                "name": "RPM Motor",
                "unit": "rpm",
                "min_value": 0,
                "max_value": 8000,
                "reference_points": [800, 1500, 2500, 3500, 4500, 5500, 6500, 7500]
            },
            "010D": {  # Viteză
                "name": "Viteză Vehicul",
                "unit": "km/h",
                "min_value": 0,
                "max_value": 200,
                "reference_points": [10, 30, 50, 70, 90, 110, 130, 150]
            },
            "0105": {  # Temperatură Motor
                "name": "Temperatură Motor",
                "unit": "°C",
                "min_value": 0,
                "max_value": 120,
                "reference_points": [20, 40, 60, 80, 100]
            },
            "010A": {  # Presiune Combustibil
                "name": "Presiune Combustibil",
                "unit": "kPa",
                "min_value": 0,
                "max_value": 1000,
                "reference_points": [100, 200, 300, 400, 500, 600, 700, 800]
            }
        }
        
        self.load_calibration_data()
    
    def load_calibration_data(self):
        """Încarcă datele de calibrare din baza de date"""
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                
                # Încarcă rezultatele de calibrare
                cursor.execute('''
                    SELECT sensor_pid, calibration_value, reference_value, timestamp, status
                    FROM calibration
                    ORDER BY timestamp DESC
                ''')
                
                for row in cursor.fetchall():
                    pid, cal_value, ref_value, timestamp, status = row
                    if pid not in self.calibration_results:
                        self.calibration_results[pid] = []
                    
                    self.calibration_results[pid].append({
                        'calibration_value': cal_value,
                        'reference_value': ref_value,
                        'timestamp': datetime.fromisoformat(timestamp),
                        'status': status
                    })
                    
        except Exception as e:
            logging.error(f"Eroare la încărcarea datelor de calibrare: {e}")
    
    def start_calibration(self, sensor_pid: str, callback=None) -> bool:
        """Începe procesul de calibrare pentru un senzor"""
        if self.is_calibrating:
            logging.warning("Calibrarea este deja în curs")
            return False
        
        if sensor_pid not in self.calibration_sensors:
            logging.error(f"Senzorul {sensor_pid} nu este suportat pentru calibrare")
            return False
        
        if not self.connection_manager.is_connected:
            logging.error("Nu există conexiune OBD2 activă")
            return False
        
        self.is_calibrating = True
        self.calibration_thread = threading.Thread(
            target=self._calibration_process,
            args=(sensor_pid, callback),
            daemon=True
        )
        self.calibration_thread.start()
        
        logging.info(f"Calibrarea pentru senzorul {sensor_pid} a început")
        return True
    
    def stop_calibration(self):
        """Oprește procesul de calibrare"""
        self.is_calibrating = False
        logging.info("Calibrarea a fost oprită")
    
    def _calibration_process(self, sensor_pid: str, callback=None):
        """Procesul principal de calibrare"""
        try:
            sensor_config = self.calibration_sensors[sensor_pid]
            calibration_points = []
            
            # Progresul calibrei
            total_points = len(sensor_config['reference_points'])
            current_point = 0
            
            for reference_value in sensor_config['reference_points']:
                if not self.is_calibrating:
                    break
                
                # Așteaptă stabilizarea valorii
                measured_values = []
                for _ in range(10):  # 10 măsurători pentru stabilizare
                    if not self.is_calibrating:
                        break
                    
                    value = self.connection_manager.read_sensor(sensor_pid)
                    if value is not None:
                        measured_values.append(value)
                    
                    time.sleep(0.5)
                
                if measured_values:
                    measured_value = np.mean(measured_values)
                    confidence = self._calculate_confidence(measured_values)
                    
                    calibration_point = CalibrationPoint(
                        sensor_pid=sensor_pid,
                        reference_value=reference_value,
                        measured_value=measured_value,
                        timestamp=datetime.now(),
                        confidence=confidence,
                        status='measured'
                    )
                    
                    calibration_points.append(calibration_point)
                    
                    # Actualizează progresul
                    current_point += 1
                    if callback:
                        progress = (current_point / total_points) * 100
                        callback(progress, f"Punct {current_point}/{total_points}: {reference_value} {sensor_config['unit']}")
                
                time.sleep(1)  # Pauză între puncte
            
            if calibration_points and self.is_calibrating:
                # Calculează factorul de calibrare
                result = self._calculate_calibration_factor(calibration_points)
                
                # Salvează rezultatul
                self._save_calibration_result(result)
                
                if callback:
                    callback(100, "Calibrarea completată cu succes!")
                
                logging.info(f"Calibrarea pentru {sensor_pid} completată: factor={result.calibration_factor:.4f}")
            
        except Exception as e:
            logging.error(f"Eroare în procesul de calibrare: {e}")
            if callback:
                callback(0, f"Eroare la calibrare: {str(e)}")
        finally:
            self.is_calibrating = False
    
    def _calculate_confidence(self, values: List[float]) -> float:
        """Calculează nivelul de încredere pentru o măsurătoare"""
        if len(values) < 2:
            return 0.0
        
        # Coeficientul de variație (CV = std/mean)
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        if mean_value == 0:
            return 0.0
        
        cv = std_value / mean_value
        
        # Convertește CV în nivel de încredere (0-1)
        # CV mai mic = încredere mai mare
        confidence = max(0.0, 1.0 - cv)
        
        return confidence
    
    def _calculate_calibration_factor(self, calibration_points: List[CalibrationPoint]) -> CalibrationResult:
        """Calculează factorul de calibrare din punctele măsurate"""
        if len(calibration_points) < 2:
            raise ValueError("Sunt necesare cel puțin 2 puncte de calibrare")
        
        # Extrage datele
        reference_values = [point.reference_value for point in calibration_points]
        measured_values = [point.measured_value for point in calibration_points]
        confidences = [point.confidence for point in calibration_points]
        
        # Calculează regresia liniară cu ponderi
        weights = np.array(confidences)
        
        # Normalizează ponderile
        weights = weights / np.sum(weights)
        
        # Regresie liniară ponderată
        A = np.vstack([measured_values, np.ones(len(measured_values))]).T
        w = np.sqrt(weights)
        Aw = A * w[:, np.newaxis]
        bw = np.array(reference_values) * w
        
        try:
            slope, offset = np.linalg.lstsq(Aw, bw, rcond=None)[0]
        except:
            # Fallback la regresie simplă
            slope, offset = np.polyfit(measured_values, reference_values, 1)
        
        # Calculează R-squared
        predicted_values = slope * np.array(measured_values) + offset
        ss_res = np.sum((reference_values - predicted_values) ** 2)
        ss_tot = np.sum((reference_values - np.mean(reference_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Calculează încrederea generală
        overall_confidence = np.mean(confidences) * r_squared
        
        # Determină statusul
        if overall_confidence > 0.8:
            status = "excellent"
        elif overall_confidence > 0.6:
            status = "good"
        elif overall_confidence > 0.4:
            status = "fair"
        else:
            status = "poor"
        
        return CalibrationResult(
            sensor_pid=calibration_points[0].sensor_pid,
            calibration_factor=slope,
            offset=offset,
            r_squared=r_squared,
            confidence=overall_confidence,
            last_calibration=datetime.now(),
            status=status
        )
    
    def _save_calibration_result(self, result: CalibrationResult):
        """Salvează rezultatul calibrei în baza de date"""
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO calibration (sensor_pid, calibration_value, reference_value, timestamp, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    result.sensor_pid,
                    result.calibration_factor,
                    result.offset,
                    result.last_calibration,
                    result.status
                ))
                
                # Actualizează cache-ul local
                if result.sensor_pid not in self.calibration_results:
                    self.calibration_results[result.sensor_pid] = []
                
                self.calibration_results[result.sensor_pid].append({
                    'calibration_value': result.calibration_factor,
                    'reference_value': result.offset,
                    'timestamp': result.last_calibration,
                    'status': result.status
                })
                
        except Exception as e:
            logging.error(f"Eroare la salvarea rezultatului calibrei: {e}")
    
    def get_calibrated_value(self, sensor_pid: str, raw_value: float) -> float:
        """Aplică factorul de calibrare la o valoare brută"""
        if sensor_pid not in self.calibration_results:
            return raw_value
        
        # Obține cel mai recent rezultat de calibrare
        latest_result = self.calibration_results[sensor_pid][0]
        calibration_factor = latest_result['calibration_value']
        offset = latest_result['reference_value']
        
        # Aplică calibrarea
        calibrated_value = raw_value * calibration_factor + offset
        
        return calibrated_value
    
    def get_calibration_status(self, sensor_pid: str) -> Optional[Dict]:
        """Obține statusul calibrei pentru un senzor"""
        if sensor_pid not in self.calibration_results:
            return None
        
        latest_result = self.calibration_results[sensor_pid][0]
        
        return {
            'sensor_pid': sensor_pid,
            'sensor_name': self.calibration_sensors.get(sensor_pid, {}).get('name', 'Unknown'),
            'last_calibration': latest_result['timestamp'],
            'calibration_factor': latest_result['calibration_value'],
            'offset': latest_result['reference_value'],
            'status': latest_result['status'],
            'age_hours': (datetime.now() - latest_result['timestamp']).total_seconds() / 3600
        }
    
    def needs_calibration(self, sensor_pid: str) -> bool:
        """Verifică dacă un senzor necesită calibrare"""
        status = self.get_calibration_status(sensor_pid)
        if not status:
            return True
        
        # Calibrarea este necesară dacă:
        # 1. Este mai veche de 24 ore
        # 2. Statusul este 'poor'
        # 3. Nu există calibrare
        
        config = self.config_manager.get_config()
        max_age_hours = config.calibration_interval
        
        return (status['age_hours'] > max_age_hours or 
                status['status'] == 'poor')
    
    def get_calibration_schedule(self) -> List[Dict]:
        """Obține programul de calibrare"""
        schedule = []
        
        for sensor_pid in self.calibration_sensors:
            status = self.get_calibration_status(sensor_pid)
            needs_calib = self.needs_calibration(sensor_pid)
            
            schedule.append({
                'sensor_pid': sensor_pid,
                'sensor_name': self.calibration_sensors[sensor_pid]['name'],
                'needs_calibration': needs_calib,
                'last_calibration': status['last_calibration'] if status else None,
                'status': status['status'] if status else 'none',
                'priority': 'high' if needs_calib else 'low'
            })
        
        # Sortează după prioritate
        schedule.sort(key=lambda x: (x['needs_calibration'], x['priority'] == 'high'), reverse=True)
        
        return schedule
    
    def export_calibration_data(self, sensor_pid: str = None) -> str:
        """Exportă datele de calibrare în format JSON"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'calibration_sensors': self.calibration_sensors,
                'calibration_results': {}
            }
            
            if sensor_pid:
                if sensor_pid in self.calibration_results:
                    export_data['calibration_results'][sensor_pid] = self.calibration_results[sensor_pid]
            else:
                export_data['calibration_results'] = self.calibration_results
            
            filename = f"calibration_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.config_manager.get_config().report_save_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            logging.error(f"Eroare la exportul datelor de calibrare: {e}")
            return None
    
    def import_calibration_data(self, filepath: str) -> bool:
        """Importă datele de calibrare din fișier JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'calibration_results' in import_data:
                for sensor_pid, results in import_data['calibration_results'].items():
                    self.calibration_results[sensor_pid] = results
                
                # Salvează în baza de date
                self._save_imported_calibration_data(import_data['calibration_results'])
                
                logging.info(f"Datele de calibrare au fost importate cu succes din {filepath}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Eroare la importul datelor de calibrare: {e}")
            return False
    
    def _save_imported_calibration_data(self, calibration_data: Dict):
        """Salvează datele importate în baza de date"""
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                
                for sensor_pid, results in calibration_data.items():
                    for result in results:
                        cursor.execute('''
                            INSERT OR REPLACE INTO calibration 
                            (sensor_pid, calibration_value, reference_value, timestamp, status)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            sensor_pid,
                            result['calibration_value'],
                            result['reference_value'],
                            result['timestamp'],
                            result['status']
                        ))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Eroare la salvarea datelor importate: {e}") 