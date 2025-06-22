# 🚗 Ghid Utilizare - OBD2 Diagnostic Tool Modern UI

## 📋 Cuprins

1. [Introducere](#introducere)
2. [Instalare și Configurare](#instalare-și-configurare)
3. [Primul Pas - Conectarea](#primul-pas---conectarea)
4. [Navigare în Interfață](#navigare-în-interfață)
5. [Dashboard - Panoul Principal](#dashboard---panoul-principal)
6. [Senzori - Monitorizare Date](#senzori---monitorizare-date)
7. [Coduri Eroare - Diagnostic](#coduri-eroare---diagnostic)
8. [Monitorizare Live - Grafice Real-time](#monitorizare-live---grafice-real-time)
9. [Funcții Avansate - ECU și Teste](#funcții-avansate---ecu-și-teste)
10. [Personalizare și Configurare](#personalizare-și-configurare)
11. [Depanare](#depanare)
12. [Sfaturi și Trucuri](#sfaturi-și-trucuri)

## 🎯 Introducere

OBD2 Diagnostic Tool Modern UI este o aplicație completă pentru diagnosticarea vehiculelor prin interfața OBD2, cu o interfață modernă și user-friendly. Această versiune oferă:

- **Design Dark Mode** elegant și modern
- **Navigare intuitivă** cu sidebar și iconițe
- **Grafice interactive** pentru monitorizare live
- **Scanare inteligentă** a dispozitivelor OBD2
- **Bază de date completă** de coduri eroare în română

## 🔧 Instalare și Configurare

### Cerințe Sistem
- Windows 10/11
- Python 3.8+
- Adaptor USB CH34X pentru OBD2
- Vehicul cu interfață OBD2

### Pași Instalare

1. **Descarcă și dezarhivează** proiectul
2. **Deschide Command Prompt** în directorul proiectului
3. **Rulează scriptul de instalare**:
   ```bash
   install_modern.bat
   ```
4. **Așteaptă finalizarea** instalării dependențelor

### Verificare Instalare
```bash
python -c "import customtkinter; import matplotlib; print('✅ Instalare reușită!')"
```

## 🔌 Primul Pas - Conectarea

### 1. Pregătire Hardware
- Conectează adaptorul USB CH34X la computer
- Conectează adaptorul la portul OBD2 al vehiculului
- Pornește contactul vehiculului (nu motorul)

### 2. Pornire Aplicație
```bash
run_modern.bat
```

### 3. Scanare Dispozitive
1. Apasă butonul **"🔍 Scanare Porturi"**
2. Așteaptă finalizarea scanării (progress bar)
3. Selectează portul cu **"✅ OBD2"** din listă

### 4. Conectare
1. Apasă butonul **"🔗 Conectare"**
2. Verifică că statusul arată **"✅ Conectat"** (verde)
3. Confirmă cu mesajul de succes

## 🧭 Navigare în Interfață

### Sidebar - Meniul Principal
Interfața modernă folosește un sidebar cu navigare intuitivă:

- **🏠 Dashboard** - Panoul principal cu informații generale
- **📊 Senzori** - Monitorizare date de la senzori
- **⚠️ Coduri Eroare** - Diagnostic și gestionare erori
- **📈 Monitorizare** - Grafice live și export date
- **⚙️ Avansat** - Funcții tehnice și ECU

### Status Conectare
În partea de jos a sidebar-ului:
- **❌ Deconectat** (roșu) - Nu există conexiune
- **✅ Conectat** (verde) - Conexiune activă

## 🏠 Dashboard - Panoul Principal

### Informații Vehicul
Card-ul principal afișează:
- **🔢 VIN** - Numărul de identificare vehicul
- **⚙️ Calibrare** - ID-ul de calibrare ECU

### Acțiuni Rapide
Butoane pentru operațiuni frecvente:
- **🔍 Citire Coduri Eroare** - Detectare rapidă erori
- **🗑️ Ștergere Coduri Eroare** - Curățare ECU
- **🔧 Test Senzori** - Verificare senzori

## 📊 Senzori - Monitorizare Date

### Lista Senzori Disponibili
Aplicația monitorizează peste 18 senzori:

#### Motor
- **🚗 RPM** - Turația motorului
- **🌡️ Temperatură Motor** - Temperatura motorului
- **⏰ Timp Avans** - Avansul la aprindere

#### Transmisie
- **⚡ Viteză** - Viteza vehiculului
- **🎛️ Poziție Marșarier** - Poziția marșarierului

#### Combustibil
- **⛽ Presiune Combustibil** - Presiunea în sistemul de combustibil
- **⛽ Nivel Combustibil** - Nivelul de combustibil
- **⛽ Consum Combustibil** - Consumul instantaneu

#### Electric
- **🔋 Tensiune Baterie** - Tensiunea bateriei

#### Sisteme
- **🎛️ Poziție Accelerator** - Poziția pedalei de accelerator
- **🌡️ Temperatură Răcire** - Temperatura lichidului de răcire
- **💨 Presiune Intake** - Presiunea în sistemul de admisie

### Utilizare
- Senzorii se actualizează automat când sunt conectat
- Valorile sunt afișate cu unitățile de măsură corespunzătoare
- Senzorii nefuncționali afișează "N/A"

## ⚠️ Coduri Eroare - Diagnostic

### Citire Coduri Eroare
1. Apasă **"🔍 Citire Coduri"**
2. Așteaptă scanarea ECU-ului
3. Codurile găsite apar în tabel cu:
   - **🔢 Cod** - Codul de eroare OBD2
   - **📝 Descriere** - Explicația în română
   - **📊 Status** - Starea erorii (Activ/Inactiv)

### Bază de Date Completă
Aplicația include peste 1000+ coduri de eroare cu descrieri în română:
- **P0xxx** - Probleme motor (combustibil, aprindere)
- **P1xxx** - Probleme specifice producător
- **P2xxx** - Probleme transmisie
- **P3xxx** - Probleme sisteme auxiliare
- **B0xxx** - Probleme caroserie
- **C0xxx** - Probleme chasis
- **U0xxx** - Probleme comunicare

### Ștergere Coduri Eroare
1. Apasă **"🗑️ Ștergere Coduri"**
2. Confirmă acțiunea în dialogul de confirmare
3. Așteaptă finalizarea operațiunii
4. Verifică că codurile au fost șterse

### Export Date
1. Apasă **"📁 Export CSV"**
2. Alege locația și numele fișierului
3. Datele sunt salvate în format CSV pentru analiză

## 📈 Monitorizare Live - Grafice Real-time

### Pornire Monitorizare
1. Apasă **"▶️ Start Monitorizare"**
2. Graficul începe să afișeze date în timp real
3. Butonul devine **"⏹️ Stop Monitorizare"**

### Grafice Disponibile
- **RPM vs Timp** - Turația motorului în timp
- **Viteză vs Timp** - Viteza vehiculului în timp
- **Grafice dual-axis** - RPM și viteză simultan

### Caracteristici Grafice
- **Actualizare real-time** - Date noi la fiecare 0.5 secunde
- **Istoric 60 secunde** - Ultimele 60 de secunde de date
- **Culori distincte** - RPM (roșu), Viteză (albastru)
- **Grid interactiv** - Linii de referință

### Salvare Date
1. Apasă **"💾 Salvare Date"**
2. Alege locația fișierului CSV
3. Datele includ timestamp, RPM și viteză

## ⚙️ Funcții Avansate - ECU și Teste

### Informații ECU
1. Apasă **"💻 Citire ECU Info"**
2. Aplicația citește și afișează:
   - **🔢 VIN** - Numărul de identificare vehicul
   - **⚙️ Calibration ID** - ID-ul de calibrare
   - **💻 ECU Name** - Numele unității de control
   - **🔧 System Name** - Numele sistemului

### Test Comunicare
1. Apasă **"🔍 Test Comunicare"**
2. Aplicația testează protocolul OBD2
3. Confirmă funcționarea corectă a comunicării

### Reset Adaptiv
1. Apasă **"🔄 Reset Adaptiv"**
2. Confirmă acțiunea (operațiune delicată)
3. Resetează valorile adaptive ale ECU-ului

## 🎨 Personalizare și Configurare

### Fișier de Configurare Tema
Editează `modern_theme.json` pentru personalizare:

```json
{
  "theme": {
    "mode": "dark",
    "color_theme": "blue"
  },
  "ui": {
    "corner_radius": 15,
    "button_height": 40
  },
  "colors": {
    "success": "#00ff88",
    "error": "#ff4444"
  }
}
```

### Opțiuni de Personalizare
- **Culori principale** - Schimbă paleta de culori
- **Dimensiuni UI** - Ajustează dimensiunile elementelor
- **Iconițe** - Personalizează iconițele
- **Tema** - Dark/Light mode

### Resetare la Implicite
```python
from theme_config import theme_manager
theme_manager.reset_to_default()
```

## 🔍 Depanare

### Probleme Comune

#### Nu se detectează dispozitivul OBD2
**Cauze posibile:**
- Adaptorul nu este conectat corect
- Vehiculul nu este pornit
- Driverele USB lipsesc

**Soluții:**
1. Verifică conexiunile fizice
2. Pornește contactul vehiculului
3. Reinstalează driverele USB
4. Testează cu alt software OBD2

#### Eroare de comunicare
**Cauze posibile:**
- Vehiculul nu suportă protocolul OBD2
- Motorul nu este pornit
- Adaptorul este defect

**Soluții:**
1. Verifică că vehiculul suportă OBD2 (1996+)
2. Pornește motorul pentru unele senzori
3. Testează cu alt adaptor OBD2
4. Verifică setările portului COM

#### Aplicația nu pornește
**Cauze posibile:**
- Python nu este instalat
- Dependențele lipsesc
- Fișierele sunt corupte

**Soluții:**
1. Verifică instalarea Python
2. Rulează `install_modern.bat`
3. Verifică că toate fișierele sunt prezente
4. Rulează cu drepturi de administrator

### Log-uri și Debug
Pentru probleme complexe, activați log-urile:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 💡 Sfaturi și Trucuri

### Pentru Rezultate Optime
1. **Pornește motorul** pentru citirea tuturor senzorilor
2. **Așteaptă stabilizarea** înainte de citirea codurilor
3. **Folosește monitorizarea live** pentru diagnostic dinamic
4. **Exportă datele** pentru analiză ulterioară

### Securitate
- **Nu șterge codurile** fără să înțelegi cauza
- **Fă backup** la datele importante
- **Testează pe vehiculul propriu** doar
- **Respectă legislația** locală

### Performanță
- **Închide alte aplicații** pentru performanță optimă
- **Folosește USB 3.0** pentru transfer rapid
- **Monitorizează temperatura** adaptorului
- **Actualizează driverele** periodic

### Integrare cu Alte Software
- **Export CSV** pentru analiză în Excel
- **Compatibilitate** cu software-uri de diagnostic
- **API disponibil** pentru dezvoltatori

---

**🚗 OBD2 Diagnostic Tool - Modern UI**  
*Ghid complet de utilizare pentru interfața modernă* 