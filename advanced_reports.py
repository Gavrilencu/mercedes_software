"""
Sistem de rapoarte avansat pentru OBD2 Diagnostic Tool - Advanced Version
"""

import json
import csv
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os
import logging
from dataclasses import dataclass
import jinja2

@dataclass
class ReportData:
    """Date pentru raport"""
    session_id: int
    start_time: datetime
    end_time: datetime
    vehicle_vin: str
    total_errors: int
    sensor_data: List[Dict]
    error_codes: List[Dict]
    summary: Dict

class ReportGenerator:
    """Generator de rapoarte avansate"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.report_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, str]:
        """Încarcă template-urile pentru rapoarte"""
        return {
            "default": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Raport OBD2 - {{title}}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { background-color: #2b2b2b; color: white; padding: 20px; text-align: center; }
                    .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                    .error { background-color: #ffebee; border-left: 4px solid #f44336; }
                    .warning { background-color: #fff3e0; border-left: 4px solid #ff9800; }
                    .success { background-color: #e8f5e8; border-left: 4px solid #4caf50; }
                    .table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                    .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    .table th { background-color: #f2f2f2; }
                    .chart { text-align: center; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚗 Raport Diagnostic OBD2</h1>
                    <p>{{subtitle}}</p>
                </div>
                
                <div class="section">
                    <h2>📋 Informații Generale</h2>
                    <table class="table">
                        <tr><td><strong>VIN:</strong></td><td>{{vehicle_vin}}</td></tr>
                        <tr><td><strong>Data Început:</strong></td><td>{{start_time}}</td></tr>
                        <tr><td><strong>Data Sfârșit:</strong></td><td>{{end_time}}</td></tr>
                        <tr><td><strong>Durată Sesiune:</strong></td><td>{{duration}}</td></tr>
                        <tr><td><strong>Total Erori:</strong></td><td>{{total_errors}}</td></tr>
                    </table>
                </div>
                
                {% if error_codes %}
                <div class="section error">
                    <h2>⚠️ Coduri de Eroare Detectate</h2>
                    <table class="table">
                        <tr>
                            <th>Cod</th>
                            <th>Descriere</th>
                            <th>Severitate</th>
                            <th>Timestamp</th>
                        </tr>
                        {% for error in error_codes %}
                        <tr>
                            <td><strong>{{error.code}}</strong></td>
                            <td>{{error.description}}</td>
                            <td>{{error.severity}}</td>
                            <td>{{error.timestamp}}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% endif %}
                
                {% if sensor_summary %}
                <div class="section success">
                    <h2>📊 Sumar Senzori</h2>
                    <table class="table">
                        <tr>
                            <th>Senzor</th>
                            <th>Valoare Min</th>
                            <th>Valoare Max</th>
                            <th>Valoare Medie</th>
                            <th>Unitate</th>
                        </tr>
                        {% for sensor in sensor_summary %}
                        <tr>
                            <td>{{sensor.pid}}</td>
                            <td>{{sensor.min_value}}</td>
                            <td>{{sensor.max_value}}</td>
                            <td>{{sensor.avg_value}}</td>
                            <td>{{sensor.unit}}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% endif %}
                
                <div class="section">
                    <h2>📈 Grafice</h2>
                    <div class="chart">
                        <img src="{{rpm_chart}}" alt="Grafice RPM" style="max-width: 100%;">
                    </div>
                    <div class="chart">
                        <img src="{{speed_chart}}" alt="Grafice Viteză" style="max-width: 100%;">
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔍 Recomandări</h2>
                    <ul>
                        {% for recommendation in recommendations %}
                        <li>{{recommendation}}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <div class="section">
                    <p><em>Raport generat automat de OBD2 Diagnostic Tool - Advanced Version</em></p>
                    <p><em>Data generare: {{generation_time}}</em></p>
                </div>
            </body>
            </html>
            """,
            
            "detailed": """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Raport Detaliat OBD2 - {{title}}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { background-color: #1f538d; color: white; padding: 20px; text-align: center; }
                    .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                    .critical { background-color: #ffebee; border-left: 4px solid #f44336; }
                    .warning { background-color: #fff3e0; border-left: 4px solid #ff9800; }
                    .info { background-color: #e3f2fd; border-left: 4px solid #2196f3; }
                    .table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                    .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    .table th { background-color: #f2f2f2; }
                    .chart { text-align: center; margin: 20px 0; }
                    .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚗 Raport Detaliat Diagnostic OBD2</h1>
                    <p>{{subtitle}}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Metrici Cheie</h2>
                    <div class="metric">
                        <strong>Durată Sesiune:</strong><br>{{duration}}
                    </div>
                    <div class="metric">
                        <strong>Total Erori:</strong><br>{{total_errors}}
                    </div>
                    <div class="metric">
                        <strong>Senzori Monitorizați:</strong><br>{{sensors_count}}
                    </div>
                    <div class="metric">
                        <strong>Puncte de Date:</strong><br>{{data_points}}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Detalii Sesiune</h2>
                    <table class="table">
                        <tr><td><strong>ID Sesiune:</strong></td><td>{{session_id}}</td></tr>
                        <tr><td><strong>VIN:</strong></td><td>{{vehicle_vin}}</td></tr>
                        <tr><td><strong>Data Început:</strong></td><td>{{start_time}}</td></tr>
                        <tr><td><strong>Data Sfârșit:</strong></td><td>{{end_time}}</td></tr>
                        <tr><td><strong>Status:</strong></td><td>{{status}}</td></tr>
                    </table>
                </div>
                
                {% if error_codes %}
                <div class="section critical">
                    <h2>⚠️ Coduri de Eroare</h2>
                    <table class="table">
                        <tr>
                            <th>Cod</th>
                            <th>Descriere</th>
                            <th>Severitate</th>
                            <th>Timestamp</th>
                            <th>Recomandare</th>
                        </tr>
                        {% for error in error_codes %}
                        <tr>
                            <td><strong>{{error.code}}</strong></td>
                            <td>{{error.description}}</td>
                            <td>{{error.severity}}</td>
                            <td>{{error.timestamp}}</td>
                            <td>{{error.recommendation}}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% endif %}
                
                {% if sensor_data %}
                <div class="section info">
                    <h2>📊 Date Senzori Detaliate</h2>
                    {% for sensor in sensor_data %}
                    <h3>{{sensor.name}} ({{sensor.pid}})</h3>
                    <table class="table">
                        <tr>
                            <th>Metrică</th>
                            <th>Valoare</th>
                            <th>Unitate</th>
                        </tr>
                        <tr><td>Minim</td><td>{{sensor.min_value}}</td><td>{{sensor.unit}}</td></tr>
                        <tr><td>Maxim</td><td>{{sensor.max_value}}</td><td>{{sensor.unit}}</td></tr>
                        <tr><td>Medie</td><td>{{sensor.avg_value}}</td><td>{{sensor.unit}}</td></tr>
                        <tr><td>Deviație Standard</td><td>{{sensor.std_value}}</td><td>{{sensor.unit}}</td></tr>
                        <tr><td>Puncte de Date</td><td>{{sensor.data_points}}</td><td>-</td></tr>
                    </table>
                    {% endfor %}
                </div>
                {% endif %}
                
                <div class="section">
                    <h2>📈 Analiză Temporală</h2>
                    <div class="chart">
                        <img src="{{temporal_chart}}" alt="Analiză Temporală" style="max-width: 100%;">
                    </div>
                </div>
                
                <div class="section warning">
                    <h2>🔍 Analiză și Recomandări</h2>
                    <h3>Probleme Identificate:</h3>
                    <ul>
                        {% for issue in issues %}
                        <li>{{issue}}</li>
                        {% endfor %}
                    </ul>
                    
                    <h3>Recomandări:</h3>
                    <ul>
                        {% for recommendation in recommendations %}
                        <li>{{recommendation}}</li>
                        {% endfor %}
                    </ul>
                    
                    <h3>Acțiuni Prioritare:</h3>
                    <ol>
                        {% for action in priority_actions %}
                        <li>{{action}}</li>
                        {% endfor %}
                    </ol>
                </div>
                
                <div class="section">
                    <p><em>Raport generat automat de OBD2 Diagnostic Tool - Advanced Version</em></p>
                    <p><em>Data generare: {{generation_time}}</em></p>
                </div>
            </body>
            </html>
            """
        }
    
    def generate_session_report(self, session_id: int, report_type: str = "default") -> Optional[str]:
        """Generează un raport pentru o sesiune specifică"""
        try:
            # Obține datele sesiunii
            report_data = self._get_session_data(session_id)
            if not report_data:
                return None
            
            # Generează graficele
            charts = self._generate_charts(report_data)
            
            # Pregătește datele pentru template
            template_data = self._prepare_template_data(report_data, charts)
            
            # Generează raportul
            if report_type == "PDF":
                return self._generate_pdf_report(template_data, report_type)
            else:
                return self._generate_html_report(template_data, report_type)
                
        except Exception as e:
            logging.error(f"Eroare la generarea raportului: {e}")
            return None
    
    def _get_session_data(self, session_id: int) -> Optional[ReportData]:
        """Obține datele pentru o sesiune"""
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                
                # Informații sesiune
                cursor.execute('''
                    SELECT start_time, end_time, vehicle_vin, total_errors
                    FROM sessions WHERE id = ?
                ''', (session_id,))
                
                session_info = cursor.fetchone()
                if not session_info:
                    return None
                
                start_time, end_time, vehicle_vin, total_errors = session_info
                
                # Date senzori
                cursor.execute('''
                    SELECT sensor_pid, value, unit, timestamp
                    FROM sensor_data WHERE session_id = ?
                    ORDER BY timestamp
                ''', (session_id,))
                
                sensor_data = cursor.fetchall()
                
                # Coduri eroare
                cursor.execute('''
                    SELECT code, description, severity, timestamp
                    FROM error_codes WHERE session_id = ?
                    ORDER BY timestamp
                ''', (session_id,))
                
                error_codes = cursor.fetchall()
                
                return ReportData(
                    session_id=session_id,
                    start_time=datetime.fromisoformat(start_time),
                    end_time=datetime.fromisoformat(end_time) if end_time else datetime.now(),
                    vehicle_vin=vehicle_vin or "N/A",
                    total_errors=total_errors or 0,
                    sensor_data=sensor_data,
                    error_codes=error_codes,
                    summary=self._generate_summary(sensor_data, error_codes)
                )
                
        except Exception as e:
            logging.error(f"Eroare la obținerea datelor sesiunii: {e}")
            return None
    
    def _generate_summary(self, sensor_data: List, error_codes: List) -> Dict:
        """Generează sumarul datelor"""
        summary = {
            'sensors_count': len(set(data[0] for data in sensor_data)),
            'data_points': len(sensor_data),
            'errors_count': len(error_codes),
            'critical_errors': len([e for e in error_codes if e[2] == 'critical']),
            'session_duration': None
        }
        
        if sensor_data:
            timestamps = [datetime.fromisoformat(data[3]) for data in sensor_data]
            summary['session_duration'] = max(timestamps) - min(timestamps)
        
        return summary
    
    def _generate_charts(self, report_data: ReportData) -> Dict[str, str]:
        """Generează graficele pentru raport"""
        charts = {}
        
        try:
            # Organizează datele senzorilor
            sensor_dict = {}
            for pid, value, unit, timestamp in report_data.sensor_data:
                if pid not in sensor_dict:
                    sensor_dict[pid] = {'values': [], 'timestamps': [], 'unit': unit}
                sensor_dict[pid]['values'].append(value)
                sensor_dict[pid]['timestamps'].append(datetime.fromisoformat(timestamp))
            
            # Generează grafice pentru senzorii principali
            if '010C' in sensor_dict:  # RPM
                charts['rpm_chart'] = self._create_sensor_chart(
                    sensor_dict['010C'], 'RPM Motor', 'rpm_chart.png'
                )
            
            if '010D' in sensor_dict:  # Viteză
                charts['speed_chart'] = self._create_sensor_chart(
                    sensor_dict['010D'], 'Viteză Vehicul', 'speed_chart.png'
                )
            
            # Grafic temporal combinat
            charts['temporal_chart'] = self._create_temporal_chart(sensor_dict, 'temporal_chart.png')
            
        except Exception as e:
            logging.error(f"Eroare la generarea graficelor: {e}")
        
        return charts
    
    def _create_sensor_chart(self, sensor_data: Dict, title: str, filename: str) -> str:
        """Creează un grafic pentru un senzor"""
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(sensor_data['timestamps'], sensor_data['values'], linewidth=2)
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('Timp')
            plt.ylabel(f"Valoare ({sensor_data['unit']})")
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            chart_path = os.path.join(self.config_manager.get_config().report_save_path, filename)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logging.error(f"Eroare la crearea graficului {title}: {e}")
            return ""
    
    def _create_temporal_chart(self, sensor_dict: Dict, filename: str) -> str:
        """Creează un grafic temporal combinat"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Grafic RPM
            if '010C' in sensor_dict:
                ax1.plot(sensor_dict['010C']['timestamps'], sensor_dict['010C']['values'], 
                        'r-', linewidth=2, label='RPM')
                ax1.set_ylabel('RPM', color='red')
                ax1.tick_params(axis='y', labelcolor='red')
                ax1.grid(True, alpha=0.3)
                ax1.set_title('Monitorizare Temporală - RPM și Viteză', fontweight='bold')
            
            # Grafic Viteză
            if '010D' in sensor_dict:
                ax2.plot(sensor_dict['010D']['timestamps'], sensor_dict['010D']['values'], 
                        'b-', linewidth=2, label='Viteză')
                ax2.set_ylabel('Viteză (km/h)', color='blue')
                ax2.tick_params(axis='y', labelcolor='blue')
                ax2.grid(True, alpha=0.3)
                ax2.set_xlabel('Timp')
            
            plt.tight_layout()
            
            chart_path = os.path.join(self.config_manager.get_config().report_save_path, filename)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logging.error(f"Eroare la crearea graficului temporal: {e}")
            return ""
    
    def _prepare_template_data(self, report_data: ReportData, charts: Dict[str, str]) -> Dict:
        """Pregătește datele pentru template"""
        duration = report_data.end_time - report_data.start_time
        
        # Procesează datele senzorilor
        sensor_summary = []
        if report_data.sensor_data:
            sensor_groups = {}
            for pid, value, unit, timestamp in report_data.sensor_data:
                if pid not in sensor_groups:
                    sensor_groups[pid] = {'values': [], 'unit': unit}
                sensor_groups[pid]['values'].append(value)
            
            for pid, data in sensor_groups.items():
                values = data['values']
                sensor_summary.append({
                    'pid': pid,
                    'min_value': min(values),
                    'max_value': max(values),
                    'avg_value': sum(values) / len(values),
                    'unit': data['unit']
                })
        
        # Procesează codurile de eroare
        error_codes_processed = []
        for code, description, severity, timestamp in report_data.error_codes:
            error_codes_processed.append({
                'code': code,
                'description': description,
                'severity': severity,
                'timestamp': timestamp
            })
        
        return {
            'title': f"Sesiune {report_data.session_id}",
            'subtitle': f"Raport generat la {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            'session_id': report_data.session_id,
            'vehicle_vin': report_data.vehicle_vin,
            'start_time': report_data.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': report_data.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': str(duration).split('.')[0],
            'total_errors': report_data.total_errors,
            'sensors_count': report_data.summary['sensors_count'],
            'data_points': report_data.summary['data_points'],
            'status': 'Completat',
            'sensor_summary': sensor_summary,
            'error_codes': error_codes_processed,
            'recommendations': self._generate_recommendations(report_data),
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **charts
        }
    
    def _generate_recommendations(self, report_data: ReportData) -> List[str]:
        """Generează recomandări bazate pe datele sesiunii"""
        recommendations = []
        
        if report_data.total_errors > 0:
            recommendations.append("Verificați și rezolvați codurile de eroare detectate.")
        
        if report_data.total_errors > 5:
            recommendations.append("Numărul mare de erori indică probleme serioase care necesită atenție imediată.")
        
        # Analizează datele senzorilor pentru anomalii
        sensor_values = {}
        for pid, value, unit, timestamp in report_data.sensor_data:
            if pid not in sensor_values:
                sensor_values[pid] = []
            sensor_values[pid].append(value)
        
        # Verifică RPM pentru valori anormale
        if '010C' in sensor_values:
            rpm_values = sensor_values['010C']
            if max(rpm_values) > 8000:
                recommendations.append("RPM-ul maxim depășește limitele normale. Verificați sistemul de aprindere.")
        
        # Verifică viteză pentru valori anormale
        if '010D' in sensor_values:
            speed_values = sensor_values['010D']
            if max(speed_values) > 200:
                recommendations.append("Viteza maximă înregistrată este foarte mare. Verificați sistemul de frânare.")
        
        if not recommendations:
            recommendations.append("Toate sistemele par să funcționeze normal.")
        
        return recommendations
    
    def _generate_html_report(self, template_data: Dict, report_type: str) -> str:
        """Generează raport HTML"""
        try:
            template = jinja2.Template(self.report_templates[report_type])
            html_content = template.render(**template_data)
            
            report_filename = f"raport_obd2_{template_data['session_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            report_path = os.path.join(self.config_manager.get_config().report_save_path, report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Salvează în baza de date
            self._save_report_record(template_data['session_id'], 'HTML', report_path)
            
            return report_path
            
        except Exception as e:
            logging.error(f"Eroare la generarea raportului HTML: {e}")
            return None
    
    def _generate_pdf_report(self, template_data: Dict, report_type: str) -> str:
        """Generează raport PDF"""
        try:
            # Generează HTML mai întâi
            html_path = self._generate_html_report(template_data, report_type)
            if not html_path:
                return None
            
            # Convertește HTML la PDF (necesită wkhtmltopdf sau similar)
            pdf_filename = html_path.replace('.html', '.pdf')
            
            # Pentru moment, returnăm calea HTML (PDF-ul poate fi generat ulterior)
            return html_path
            
        except Exception as e:
            logging.error(f"Eroare la generarea raportului PDF: {e}")
            return None
    
    def _save_report_record(self, session_id: int, report_type: str, file_path: str):
        """Salvează înregistrarea raportului în baza de date"""
        try:
            with sqlite3.connect(self.config_manager.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reports (session_id, report_type, file_path, generated_at)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, report_type, file_path, datetime.now()))
        except Exception as e:
            logging.error(f"Eroare la salvarea înregistrării raportului: {e}")
    
    def export_to_csv(self, session_id: int) -> Optional[str]:
        """Exportă datele sesiunii în format CSV"""
        try:
            report_data = self._get_session_data(session_id)
            if not report_data:
                return None
            
            csv_filename = f"date_sesiune_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            csv_path = os.path.join(self.config_manager.get_config().report_save_path, csv_filename)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow(['Tip', 'Timestamp', 'PID', 'Valoare', 'Unitate', 'Descriere'])
                
                # Date senzori
                for pid, value, unit, timestamp in report_data.sensor_data:
                    writer.writerow(['Senzor', timestamp, pid, value, unit, ''])
                
                # Coduri eroare
                for code, description, severity, timestamp in report_data.error_codes:
                    writer.writerow(['Eroare', timestamp, code, '', '', description])
            
            return csv_path
            
        except Exception as e:
            logging.error(f"Eroare la exportul CSV: {e}")
            return None 