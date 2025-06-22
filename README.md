# OBD2 Diagnostic Tool - Mercedes Software

O aplicație completă de diagnosticare OBD2 pentru Windows, creată în Python, care permite citirea și ștergerea codurilor de eroare, monitorizarea senzorilor în timp real și accesarea informațiilor despre vehicul.

## Caracteristici

### 🔧 Funcționalități Principale
- **Conectare OBD2**: Suport pentru adaptoare OBD2 USB CH34X
- **Citire Coduri Eroare**: Detectarea și afișarea codurilor de eroare DTC
- **Ștergere Coduri Eroare**: Ștergerea codurilor de eroare din ECU
- **Monitorizare Senzori**: Citirea datelor de la toți senzorii mașinii
- **Monitorizare Live**: Grafice în timp real pentru RPM și viteză
- **Informații Vehicul**: Citirea VIN și informațiilor despre ECU
- **Export Date**: Salvare date în format CSV

### 📊 Senzori Suportați
- **Motor**: RPM, temperatură motor, presiune combustibil, timp avans
- **Transmisie**: Viteză, poziție marșarier
- **Combustibil**: Nivel combustibil, consum, presiune
- **Electric**: Tensiune baterie
- **Sisteme**: Poziție accelerator, presiune EGR, temperatură catalizator
- **Și multe altele...**

### 🎨 Interfață Modernă
- Design dark mode modern
- Interfață intuitivă cu tab-uri organizate
- Grafice interactive pentru monitorizare
- Tabel cu coduri de eroare sortabile

## Instalare

### Cerințe Sistem
- Windows 10/11
- Python 3.8 sau mai nou
- Adaptor OBD2 USB CH34X

### Pași Instalare

1. **Clonează repository-ul**:
```bash
git clone <repository-url>
cd mercedes_software
```

2. **Instalează dependențele**:
```bash
pip install -r requirements.txt
```

3. **Conectează adaptorul OBD2**:
   - Conectează adaptorul OBD2 la portul USB
   - Conectează celălalt capăt la portul OBD2 al mașinii
   - Pornește contactul mașinii (nu motorul)

4. **Rulează aplicația**:
```bash
python obd2_diagnostic.py
```

## Utilizare

### 1. Conectare
- Selectează portul COM corect din listă
- Apasă butonul "Conectare"
- Verifică că statusul arată "Conectat" (verde)

### 2. Dashboard
- **Informații Vehicul**: Afișează VIN și calibrarea ECU
- **Acțiuni Rapide**: Butoane pentru operațiuni comune

### 3. Senzori
- Afișează toate senzorii disponibili
- Valorile se actualizează automat
- Apasă "Test Senzori" pentru a citi toate datele

### 4. Coduri Eroare
- **Citire Coduri**: Detectează toate codurile de eroare
- **Ștergere Coduri**: Șterge codurile de eroare din ECU
- **Export CSV**: Salvează codurile în fișier CSV

### 5. Monitorizare Live
- **Start Monitorizare**: Începe monitorizarea în timp real
- **Grafice**: Afișează RPM și viteză în timp real
- **Salvare Date**: Salvează datele în fișier CSV

### 6. Avansat
- **Informații ECU**: Citește informații detaliate despre ECU
- **Test Comunicare**: Testează comunicarea OBD2
- **Reset Adaptiv**: Resetează valorile adaptive

## Structura Proiectului

```
mercedes_software/
├── obd2_diagnostic.py      # Aplicația principală
├── connection_manager.py    # Manager pentru conexiunea OBD2
├── gui_components.py       # Componente GUI
├── requirements.txt        # Dependențe Python
└── README.md              # Acest fișier
```

## Protocol OBD2 Suportat

Aplicația suportă următoarele comenzi OBD2:

### Mode 01 - Date Curente
- `0100` - Test comunicare
- `010C` - RPM motor
- `010D` - Viteză vehicul
- `0105` - Temperatură motor
- `010A` - Presiune combustibil
- `0111` - Poziție accelerator
- `012F` - Nivel combustibil
- `0142` - Tensiune baterie

### Mode 03 - Coduri Eroare
- `03` - Citire coduri eroare curente
- `07` - Citire coduri eroare în așteptare

### Mode 04 - Ștergere Coduri
- `04` - Ștergere coduri eroare

### Mode 09 - Informații Vehicul
- `0902` - VIN
- `0904` - ID Calibrare
- `090A` - Nume ECU

## Depanare

### Probleme Comune

1. **Nu se poate conecta**:
   - Verifică că adaptorul OBD2 este conectat corect
   - Verifică că contactul mașinii este pornit
   - Încearcă un port COM diferit

2. **Nu se citesc datele**:
   - Verifică că motorul este pornit (pentru unele senzori)
   - Verifică că mașina suportă protocolul OBD2
   - Încearcă să resetezi conexiunea

3. **Erori de comunicare**:
   - Verifică cablurile OBD2
   - Verifică că adaptorul este compatibil
   - Încearcă să reinstalezi driverele USB

### Log-uri și Debug

Pentru a activa log-urile de debug, editează `connection_manager.py` și adaugă:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contribuții

Contribuțiile sunt binevenite! Pentru a contribui:

1. Fork repository-ul
2. Creează un branch pentru feature-ul tău
3. Fă commit-urile
4. Creează un Pull Request

## Licență

Acest proiect este licențiat sub MIT License.

## Suport

Pentru suport și întrebări:
- Creează un issue pe GitHub
- Contactează dezvoltatorul

## Changelog

### v1.0.0
- Versiunea inițială
- Suport complet pentru OBD2
- Interfață grafică modernă
- Monitorizare în timp real
- Export date CSV

---

**Notă**: Această aplicație este destinată doar pentru diagnosticarea propriilor vehicule. Folosiți-o cu responsabilitate și respectați legislația locală. 