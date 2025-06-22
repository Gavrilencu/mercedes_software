"""
Sistem de notificări avansat pentru OBD2 Diagnostic Tool - Advanced Version
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import List, Dict, Any
import queue
import winsound

class NotificationType:
    """Tipuri de notificări"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CRITICAL = "critical"

class NotificationPriority:
    """Priorități pentru notificări"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Notification:
    """Clasă pentru o notificare"""
    
    def __init__(self, title: str, message: str, notification_type: str = NotificationType.INFO, 
                 priority: int = NotificationPriority.NORMAL, duration: int = 5000):
        self.title = title
        self.message = message
        self.type = notification_type
        self.priority = priority
        self.duration = duration
        self.timestamp = datetime.now()
        self.id = f"{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{hash(self.message)}"
    
    def __lt__(self, other):
        """Comparare pentru sortarea în coada de priorități"""
        if not isinstance(other, Notification):
            return False
        # Prioritate mai mare = prioritate mai mică în coadă (invers)
        return self.priority > other.priority
    
    def __eq__(self, other):
        """Egalitate pentru notificări"""
        if not isinstance(other, Notification):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Hash pentru notificare"""
        return hash(self.id)

class NotificationManager:
    """Manager pentru sistemul de notificări"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.notifications_queue = queue.PriorityQueue()
        self.active_notifications = {}
        self.notification_windows = {}
        self.is_running = False
        self.notification_thread = None
        
        # Iconițe pentru tipuri de notificări
        self.icons = {
            NotificationType.INFO: "ℹ️",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.SUCCESS: "✅",
            NotificationType.CRITICAL: "🚨"
        }
        
        # Culori pentru tipuri de notificări
        self.colors = {
            NotificationType.INFO: ("#2196F3", "#1976D2"),
            NotificationType.WARNING: ("#FF9800", "#F57C00"),
            NotificationType.ERROR: ("#F44336", "#D32F2F"),
            NotificationType.SUCCESS: ("#4CAF50", "#388E3C"),
            NotificationType.CRITICAL: ("#9C27B0", "#7B1FA2")
        }
        
        self.start_notification_system()
    
    def start_notification_system(self):
        """Pornește sistemul de notificări"""
        self.is_running = True
        self.notification_thread = threading.Thread(target=self._notification_worker, daemon=True)
        self.notification_thread.start()
        logging.info("Sistemul de notificări a fost pornit")
    
    def stop_notification_system(self):
        """Oprește sistemul de notificări"""
        self.is_running = False
        # Închide toate notificările active
        for window in self.notification_windows.values():
            try:
                window.destroy()
            except:
                pass
        logging.info("Sistemul de notificări a fost oprit")
    
    def _notification_worker(self):
        """Worker thread pentru procesarea notificărilor"""
        while self.is_running:
            try:
                # Procesează notificările din coadă
                if not self.notifications_queue.empty():
                    priority, notification = self.notifications_queue.get_nowait()
                    self._show_notification(notification)
                
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Eroare în worker-ul de notificări: {e}")
    
    def add_notification(self, title: str, message: str, notification_type: str = NotificationType.INFO,
                        priority: int = NotificationPriority.NORMAL, duration: int = 5000):
        """Adaugă o notificare în coadă"""
        notification = Notification(title, message, notification_type, priority, duration)
        self.notifications_queue.put((priority, notification))
        logging.info(f"Notificare adăugată: {title} - {message}")
    
    def _show_notification(self, notification: Notification):
        """Afișează o notificare pe ecran"""
        try:
            # Creează fereastra de notificare
            window = tk.Toplevel()
            window.title(notification.title)
            window.geometry("400x150")
            window.resizable(False, False)
            
            # Poziționează fereastra în colțul din dreapta sus
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = screen_width - 420
            y = 50 + len(self.notification_windows) * 160
            
            window.geometry(f"400x150+{x}+{y}")
            
            # Configurează stilul ferestrei
            window.configure(bg='#2b2b2b')
            window.attributes('-topmost', True)
            
            # Adaugă iconița și titlul
            icon_label = tk.Label(window, text=self.icons[notification.type], 
                                font=('Arial', 24), bg='#2b2b2b', fg='white')
            icon_label.pack(pady=(10, 5))
            
            title_label = tk.Label(window, text=notification.title, 
                                 font=('Arial', 12, 'bold'), bg='#2b2b2b', fg='white')
            title_label.pack(pady=(0, 5))
            
            # Adaugă mesajul
            message_label = tk.Label(window, text=notification.message, 
                                   font=('Arial', 10), bg='#2b2b2b', fg='#cccccc',
                                   wraplength=350, justify='center')
            message_label.pack(pady=(0, 10))
            
            # Adaugă timestamp
            timestamp_label = tk.Label(window, text=notification.timestamp.strftime('%H:%M:%S'),
                                     font=('Arial', 8), bg='#2b2b2b', fg='#888888')
            timestamp_label.pack(side='bottom', pady=(0, 5))
            
            # Adaugă buton de închidere
            close_button = tk.Button(window, text="✕", command=lambda: self._close_notification(notification.id),
                                   bg='#444444', fg='white', font=('Arial', 10), bd=0, padx=10)
            close_button.pack(side='top', anchor='ne', padx=10, pady=10)
            
            # Salvează referința la fereastră
            self.notification_windows[notification.id] = window
            self.active_notifications[notification.id] = notification
            
            # Redă sunetul dacă este activat
            if self.config_manager.get_config().notification_sound:
                self._play_notification_sound(notification.type)
            
            # Programează închiderea automată
            window.after(notification.duration, lambda: self._close_notification(notification.id))
            
            # Trimite email dacă este configurat
            if self.config_manager.get_config().email_notifications:
                self._send_email_notification(notification)
            
        except Exception as e:
            logging.error(f"Eroare la afișarea notificării: {e}")
    
    def _close_notification(self, notification_id: str):
        """Închide o notificare"""
        if notification_id in self.notification_windows:
            try:
                self.notification_windows[notification_id].destroy()
                del self.notification_windows[notification_id]
                del self.active_notifications[notification_id]
            except:
                pass
    
    def _play_notification_sound(self, notification_type: str):
        """Redă sunetul pentru notificare"""
        try:
            if notification_type == NotificationType.CRITICAL:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            elif notification_type == NotificationType.ERROR:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif notification_type == NotificationType.WARNING:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                winsound.MessageBeep(winsound.MB_OK)
        except:
            pass
    
    def _send_email_notification(self, notification: Notification):
        """Trimite notificare prin email"""
        config = self.config_manager.get_config()
        
        if not all([config.email_smtp_server, config.email_username, config.email_password]):
            return
        
        try:
            # Creează mesajul email
            msg = MIMEMultipart()
            msg['From'] = config.email_username
            msg['To'] = config.email_username  # Trimite la același email
            msg['Subject'] = f"OBD2 Notification: {notification.title}"
            
            body = f"""
            Notificare OBD2 Diagnostic Tool
            
            Titlu: {notification.title}
            Mesaj: {notification.message}
            Tip: {notification.type}
            Prioritate: {notification.priority}
            Timestamp: {notification.timestamp}
            
            Această notificare a fost generată automat de aplicația OBD2 Diagnostic Tool.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Trimite email-ul
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(config.email_smtp_server, 465, context=context) as server:
                server.login(config.email_username, config.email_password)
                server.send_message(msg)
            
            logging.info(f"Email notificare trimis pentru: {notification.title}")
            
        except Exception as e:
            logging.error(f"Eroare la trimiterea email-ului: {e}")
    
    def show_quick_notification(self, title: str, message: str, notification_type: str = NotificationType.INFO):
        """Afișează o notificare rapidă (fără coadă)"""
        self.add_notification(title, message, notification_type, NotificationPriority.HIGH, 3000)
    
    def show_critical_notification(self, title: str, message: str):
        """Afișează o notificare critică"""
        self.add_notification(title, message, NotificationType.CRITICAL, NotificationPriority.CRITICAL, 10000)
    
    def clear_all_notifications(self):
        """Șterge toate notificările active"""
        for notification_id in list(self.notification_windows.keys()):
            self._close_notification(notification_id)

class NotificationPresets:
    """Preset-uri pentru notificări comune"""
    
    @staticmethod
    def connection_success(notification_manager: NotificationManager):
        notification_manager.show_quick_notification(
            "✅ Conectare Reușită",
            "Dispozitivul OBD2 a fost conectat cu succes!",
            NotificationType.SUCCESS
        )
    
    @staticmethod
    def connection_error(notification_manager: NotificationManager, error_msg: str):
        notification_manager.add_notification(
            "❌ Eroare Conectare",
            f"Nu s-a putut conecta la dispozitivul OBD2: {error_msg}",
            NotificationType.ERROR,
            NotificationPriority.HIGH
        )
    
    @staticmethod
    def error_codes_found(notification_manager: NotificationManager, count: int):
        notification_manager.add_notification(
            "⚠️ Coduri Eroare Detectate",
            f"S-au găsit {count} coduri de eroare în ECU.",
            NotificationType.WARNING,
            NotificationPriority.HIGH
        )
    
    @staticmethod
    def sensor_anomaly(notification_manager: NotificationManager, sensor: str, value: float):
        notification_manager.add_notification(
            "🚨 Anomalie Senzor",
            f"Senzorul {sensor} raportează o valoare anormală: {value}",
            NotificationType.CRITICAL,
            NotificationPriority.CRITICAL
        )
    
    @staticmethod
    def calibration_complete(notification_manager: NotificationManager):
        notification_manager.show_quick_notification(
            "🔧 Calibrare Completă",
            "Procesul de calibrare a fost finalizat cu succes!",
            NotificationType.SUCCESS
        )
    
    @staticmethod
    def report_generated(notification_manager: NotificationManager, report_path: str):
        notification_manager.add_notification(
            "📊 Raport Generat",
            f"Raportul a fost salvat în: {report_path}",
            NotificationType.INFO,
            NotificationPriority.NORMAL
        ) 