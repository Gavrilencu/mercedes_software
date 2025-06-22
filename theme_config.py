"""
Configurare temă pentru OBD2 Diagnostic Tool - Modern UI
"""

import json
import os
from typing import Dict, Any

class ThemeManager:
    def __init__(self, theme_file: str = "modern_theme.json"):
        self.theme_file = theme_file
        self.theme_data = self.load_theme()
        
    def load_theme(self) -> Dict[str, Any]:
        """Încarcă configurația temei din fișier"""
        try:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_theme()
        except Exception as e:
            print(f"Eroare la încărcarea temei: {e}")
            return self.get_default_theme()
    
    def save_theme(self) -> bool:
        """Salvează configurația temei în fișier"""
        try:
            with open(self.theme_file, 'w', encoding='utf-8') as f:
                json.dump(self.theme_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Eroare la salvarea temei: {e}")
            return False
    
    def get_default_theme(self) -> Dict[str, Any]:
        """Returnează tema implicită"""
        return {
            "theme": {
                "mode": "dark",
                "color_theme": "blue",
                "primary_color": "#1f538d",
                "secondary_color": "#14375e",
                "accent_color": "#00ff88",
                "background_color": "#2b2b2b",
                "surface_color": "#3c3c3c",
                "text_color": "#ffffff",
                "text_color_secondary": "#b0b0b0"
            },
            "ui": {
                "corner_radius": 15,
                "border_width": 2,
                "padding": 20,
                "button_height": 40,
                "input_height": 35
            },
            "colors": {
                "success": "#00ff88",
                "warning": "#ffaa00",
                "error": "#ff4444",
                "info": "#00aaff",
                "primary": "#1f538d",
                "secondary": "#14375e"
            },
            "icons": {
                "dashboard": "🏠",
                "sensors": "📊",
                "errors": "⚠️",
                "monitoring": "📈",
                "advanced": "⚙️",
                "connection": "🔌",
                "scan": "🔍",
                "connect": "🔗",
                "disconnect": "🔌",
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️"
            }
        }
    
    def get_color(self, color_name: str) -> str:
        """Returnează o culoare din configurație"""
        return self.theme_data.get("colors", {}).get(color_name, "#ffffff")
    
    def get_ui_setting(self, setting_name: str) -> Any:
        """Returnează o setare UI din configurație"""
        return self.theme_data.get("ui", {}).get(setting_name, None)
    
    def get_icon(self, icon_name: str) -> str:
        """Returnează o iconiță din configurație"""
        return self.theme_data.get("icons", {}).get(icon_name, "📋")
    
    def update_color(self, color_name: str, color_value: str) -> bool:
        """Actualizează o culoare în configurație"""
        if "colors" not in self.theme_data:
            self.theme_data["colors"] = {}
        self.theme_data["colors"][color_name] = color_value
        return self.save_theme()
    
    def update_ui_setting(self, setting_name: str, value: Any) -> bool:
        """Actualizează o setare UI în configurație"""
        if "ui" not in self.theme_data:
            self.theme_data["ui"] = {}
        self.theme_data["ui"][setting_name] = value
        return self.save_theme()
    
    def reset_to_default(self) -> bool:
        """Resetează tema la valorile implicite"""
        self.theme_data = self.get_default_theme()
        return self.save_theme()

# Instanță globală pentru acces ușor
theme_manager = ThemeManager()

# Funcții helper pentru acces rapid
def get_color(color_name: str) -> str:
    """Helper pentru obținerea culorilor"""
    return theme_manager.get_color(color_name)

def get_ui_setting(setting_name: str) -> Any:
    """Helper pentru obținerea setărilor UI"""
    return theme_manager.get_ui_setting(setting_name)

def get_icon(icon_name: str) -> str:
    """Helper pentru obținerea iconițelor"""
    return theme_manager.get_icon(icon_name)

# Culori predefinite pentru butoane
BUTTON_COLORS = {
    "primary": ("blue", "darkblue"),
    "success": ("green", "darkgreen"),
    "warning": ("orange", "orange"),
    "error": ("red", "darkred"),
    "info": ("purple", "purple"),
    "secondary": ("gray70", "gray30")
}

# Culori hover predefinite
HOVER_COLORS = {
    "primary": ("lightblue", "blue"),
    "success": ("lightgreen", "green"),
    "warning": ("lightcoral", "orange"),
    "error": ("lightcoral", "red"),
    "info": ("lightblue", "purple"),
    "secondary": ("gray60", "gray40")
} 