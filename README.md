# 🚗 OBD2 Diagnostic Tool - Mercedes Software

O aplicație modernă și user-friendly pentru diagnosticarea vehiculelor prin interfața OBD2, special concepută pentru utilizarea cu adaptoare USB CH34X.

## ✨ Caracteristici Principale

### 🎨 Interfață Modernă
- **Design Dark Mode** - Interfață elegantă cu tema întunecată
- **Iconițe Intuitive** - Navigare simplă cu iconițe descriptive
- **Layout Responsive** - Se adaptează la diferite dimensiuni de ecran
- **Animații Smooth** - Tranziții fluide între secțiuni

### 🔌 Conectare Inteligentă
- **Scanare Automată** - Detectează automat dispozitivele OBD2
- **Test Comunicare** - Verifică conectivitatea înainte de conectare
- **Status Real-time** - Afișează statusul conexiunii în timp real
- **Progress Bar** - Indică progresul scanării porturilor

### 📊 Dashboard Modern
- **Informații Vehicul** - VIN, calibrare, detalii ECU
- **Acțiuni Rapide** - Butoane pentru funcții frecvente
- **Status Cards** - Afișare clară a stării sistemului

### 📈 Monitorizare Avansată
- **Grafice Live** - Monitorizare în timp real cu matplotlib
- **Senzori Multipli** - Peste 18 senzori diferiți
- **Export Date** - Salvare în format CSV
- **Animații Smooth** - Grafice cu tranziții fluide

### ⚠️ Gestionare Coduri Eroare
- **Bază de Date Completă** - Peste 1000+ coduri de eroare în română
- **Descrieri Detaliate** - Explicații clare pentru fiecare cod
- **Export CSV** - Salvare coduri pentru analiză
- **Ștergere Sigură** - Confirmare înainte de ștergere

### ⚙️ Funcții Avansate
- **Informații ECU** - Detalii despre unitatea de control
- **Test Comunicare** - Verificare protocol OBD2
- **Reset Adaptiv** - Resetarea valorilor adaptive

## 🚀 Instalare și Utilizare

### Cerințe Sistem
- Windows 10/11
- Python 3.8+
- Adaptor USB CH34X pentru OBD2
- Vehicul cu interfață OBD2

### Instalare Dependențe
```bash
# Instalare automată cu script
install.bat

# Sau manual
pip install -r requirements.txt
```

### Pornire Aplicație

#### Interfață Modernă (Recomandată)
```bash
run_modern.bat
```

#### Interfață Clasică
```bash
run.bat
```

## 🎯 Ghid de Utilizare

### 1. Conectare
1. Conectați adaptorul USB CH34X la computer
2. Conectați adaptorul la portul OBD2 al vehiculului
3. Porniți aplicația
4. Apăsați "🔍 Scanare Porturi" pentru a detecta dispozitivul
5. Selectați portul cu "✅ OBD2" și apăsați "🔗 Conectare"

### 2. Dashboard
- **Informații Vehicul** - Afișează VIN și detalii ECU
- **Acțiuni Rapide** - Acces rapid la funcții frecvente
- **Status Sistem** - Monitorizare starea conexiunii

### 3. Senzori
- **Monitorizare Live** - Date în timp real de la senzori
- **Grafice Interactive** - Vizualizare grafică a datelor
- **Export Date** - Salvare pentru analiză ulterioară

### 4. Coduri Eroare
- **Citire Coduri** - Detectează toate codurile active
- **Descrieri Detaliate** - Explicații în română
- **Ștergere Sigură** - Eliminare coduri cu confirmare

### 5. Monitorizare Live
- **Grafice Real-time** - RPM, viteză, temperatură
- **Salvare Date** - Export în format CSV
- **Control Play/Pause** - Start/stop monitorizare

### 6. Funcții Avansate
- **Informații ECU** - Detalii tehnice despre unitatea de control
- **Test Comunicare** - Verificare protocol OBD2
- **Reset Adaptiv** - Resetarea valorilor de calibrare

## 🔧 Configurare

### Fișiere de Configurare
- `config.json` - Setări generale aplicație
- `modern_theme.json` - Configurare temă modernă
- `error_codes.json` - Bază de date coduri eroare

### Personalizare Tema
Editați `modern_theme.json` pentru a personaliza:
- Culori principale
- Iconițe
- Dimensiuni UI
- Stiluri componente

## 📁 Structura Proiectului

```
mercedes_software/
├── modern_obd2_app.py      # Aplicația principală modernă
├── modern_gui.py           # Componente GUI moderne
├── connection_manager.py   # Manager conexiuni OBD2
├── obd2_diagnostic.py     # Funcții diagnostic
├── gui_components.py      # Componente GUI clasice
├── config.json            # Configurare aplicație
├── modern_theme.json      # Configurare temă modernă
├── error_codes.json       # Bază de date coduri eroare
├── requirements.txt       # Dependențe Python
├── install.bat           # Script instalare
├── run.bat              # Script rulare clasic
├── run_modern.bat       # Script rulare modern
└── README.md            # Documentație
```

## 🎨 Caracteristici Design Modern

### Tema Dark Mode
- Fundal întunecat pentru confort vizual
- Contrast optim pentru citire
- Culori moderne și elegante

### Navigare Intuitivă
- Sidebar cu iconițe descriptive
- Tranziții smooth între secțiuni
- Butoane cu feedback vizual

### Componente Interactive
- Cards moderne cu colțuri rotunjite
- Progress bars animate
- Butoane cu hover effects
- Grafice interactive

### Responsive Design
- Se adaptează la diferite rezoluții
- Layout flexibil
- Scalare automată componente

## 🔍 Depanare

### Probleme Comune

#### Nu se detectează dispozitivul OBD2
1. Verificați că adaptorul este conectat corect
2. Asigurați-vă că vehiculul este pornit
3. Testați cu alt software OBD2
4. Verificați driverele USB

#### Eroare de comunicare
1. Verificați că vehiculul suportă protocolul OBD2
2. Asigurați-vă că motorul este pornit
3. Testați cu alt adaptor OBD2
4. Verificați setările portului COM

#### Aplicația nu pornește
1. Verificați că Python este instalat
2. Rulați `pip install -r requirements.txt`
3. Verificați că toate fișierele sunt prezente
4. Rulați cu drepturi de administrator

## 📞 Suport

Pentru suport tehnic sau întrebări:
- Verificați secțiunea de depanare
- Consultați documentația OBD2
- Testați cu vehicule diferite

## 📄 Licență

Acest proiect este dezvoltat pentru utilizare educațională și personală.

## 🔄 Actualizări

### Versiunea 2.0 - Interfață Modernă
- ✅ Design complet nou cu tema dark
- ✅ Navigare sidebar cu iconițe
- ✅ Componente moderne și responsive
- ✅ Grafice interactive cu matplotlib
- ✅ Scanare inteligentă dispozitive OBD2
- ✅ Export date îmbunătățit
- ✅ Configurare temă personalizabilă

### Versiunea 1.0 - Interfață Clasică
- ✅ Funcționalitate de bază OBD2
- ✅ Citire senzori și coduri eroare
- ✅ Interfață tkinter clasică
- ✅ Bază de date coduri eroare

---

**🚗 OBD2 Diagnostic Tool - Mercedes Software**  
*Interfață modernă pentru diagnosticarea vehiculelor* 