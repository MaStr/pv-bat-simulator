# PV-Batterie Simulator

Ein Simulator zur Analyse und Optimierung der Batteriesteuerung bei Photovoltaik-Anlagen mit dynamischen Strompreisen. Das Projekt vergleicht verschiedene Steuerungsstrategien und ermöglicht die Berechnung der Kosteneffekte unterschiedlicher Betriebsmodi.

## Übersicht

Dieses Projekt simuliert die Steuerung einer Batterie in einem Haushalt mit PV-Anlage unter verschiedenen Preismodellen. Es vergleicht:
- Statische Batteriesteuerung mit festem Strompreis
- Ungesteuerte Batterienutzung mit dynamischen Strompreisen
- Intelligente/optimierte Batteriesteuerung basierend auf Strompreisprognosen
- BatControl-Steuerung mit verschiedenen Modi

## Features

- **Web-Interface**: Benutzerfreundliche Oberfläche zur Eingabe von Parametern und Visualisierung der Ergebnisse
- **Mehrere Simulationsmodelle**: Vier verschiedene Modelle zum Vergleich unterschiedlicher Steuerungsstrategien
- **Flexible Parameter**: Anpassbare Batterie-, PV- und Verbrauchsparameter
- **Detaillierte Auswertung**: Stundengenaue Darstellung von Kosten, Netzbezug und Batteriestand
- **Docker-Support**: Einfache Bereitstellung über Docker

## Installation

### Voraussetzungen

- Python 3.11 oder höher
- Docker (optional, für Container-basierte Ausführung)

### Lokale Installation

1. Repository klonen:
```bash
git clone https://github.com/MaStr/pv-bat-simulator.git
cd pv-bat-simulator
```

2. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

3. BatControl-Bibliothek installieren (für Modell 4):
```bash
wget https://github.com/muexxl/batcontrol/releases/download/0.5.5/batcontrol-0.5.5-py3-none-any.whl
pip install batcontrol-0.5.5-py3-none-any.whl
```

### Docker Installation

1. Docker Image erstellen:
```bash
docker build -t pv-bat-simulator .
```

2. Container starten:
```bash
docker run -p 5000:5000 pv-bat-simulator
```

## Verwendung

### Anwendung starten

**Lokal:**
```bash
python app.py
```

**Docker:**
```bash
docker run -p 5000:5000 pv-bat-simulator
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

### Web-Interface

Über das Web-Interface können Sie:
- **Systemparameter** eingeben (Batteriekapazität, Lade-/Entladeleistung)
- **Verbrauchsprofile** definieren (24 Stundenwerte in Wh)
- **PV-Erzeugung** angeben (24 Stundenwerte in Wh)
- **Strompreise** festlegen (statisch oder dynamisch mit 24 Stundenwerten)
- **Simulationen starten** und Ergebnisse vergleichen

## Simulationsmodelle

### Modell 1: Linearer Verbrauch - statischer Preis

Simuliert die grundlegende Batteriesteuerung mit einem festen Strompreis:
- PV-Strom deckt zuerst den direkten Verbrauch
- PV-Überschuss lädt die Batterie
- Bei Strombedarf wird zuerst die Batterie, dann das Netz genutzt
- Kosten werden nur für Netzbezug berechnet (statischer Preis)

**Anwendungsfall**: Referenzmodell für Haushalte ohne dynamischen Stromtarif

### Modell 2: Linearer Verbrauch - dynamischer Preis

Nutzt die gleiche Steuerungsstrategie wie Modell 1, aber mit stündlich variablen Strompreisen:
- Identische Batteriesteuerung wie Modell 1
- Kosten basieren auf stündlich wechselnden Strompreisen
- Berechnet einen verbrauchsgewichteten Durchschnittspreis

**Anwendungsfall**: Analyse der Kosteneffekte bei dynamischen Tarifen ohne aktive Preisoptimierung

### Modell 3: Aktive Steuerung - dynamischer Preis

Intelligente Batteriesteuerung mittels linearer Optimierung (PuLP):
- **Bei niedrigen Preisen**: Batterie wird auch aus dem Netz geladen
- **Bei hohen Preisen**: Batterie wird bevorzugt entladen, um Netzbezug zu minimieren
- Berücksichtigt Preisdifferenzen und optimiert über 24 Stunden
- Nutzt den CBC-Solver für optimale Entscheidungen

**Anwendungsfall**: Maximale Kostenersparnis durch vorausschauende Steuerung basierend auf Preisprognosen

### Modell 4: BatControl-Steuerung

Verwendet die [batcontrol-Bibliothek](https://github.com/muexxl/batcontrol) mit drei Modi:
- **MODE 10 (DISCHARGE ALLOWED)**: Normale Nutzung, Batterieentladung erlaubt
- **MODE 0 (AVOID DISCHARGE)**: Netzbezug statt Batterieentladung bei steigenden Preisen
- **MODE -1 (CHARGE FROM GRID)**: Batterie aus dem Netz laden bei niedrigen Preisen

**Anwendungsfall**: Realistische Simulation mit bewährter Open-Source-Steuerungslogik

## Parameter

Die Simulationen arbeiten mit folgenden Parametern:

### Zeitbasis
- **Stundenwerte**: Alle Berechnungen basieren auf 24 Stunden (1 Tag)
- **Auflösung**: 1 Stunde pro Datenpunkt

### Batterie-Parameter
- **Kapazität**: Batteriekapazität in Wh (z.B. 10.000 Wh = 10 kWh)
- **Max. Ladeleistung**: Maximale Ladeleistung in W (z.B. 5.000 W = 5 kW)
- **Max. Entladeleistung**: Maximale Entladeleistung in W (z.B. 5.000 W = 5 kW)
- **Anfangs-SOC**: Anfänglicher Ladestand der Batterie (0.0-1.0, Standard: 0.0 oder 0.2)

### Verbrauch und Erzeugung
- **Lastprofil**: 24 Verbrauchswerte in Wh pro Stunde
- **PV-Erzeugung**: 24 PV-Erzeugungswerte in Wh pro Stunde

### Preisparameter
- **Statischer Preis**: Fester Strompreis in €/kWh (z.B. 0,30 €/kWh)
- **Dynamische Preise**: 24 Börsenstrompreise + Aufschläge + MwSt. in €/kWh
- **Preis-Abstand**: Mindestpreisdifferenz für aktives Nachladen (€/kWh)

## Technische Details

### Verwendete Technologien
- **Backend**: Flask (Python Web Framework)
- **Optimierung**: PuLP (Linear Programming)
- **Numerische Berechnung**: NumPy
- **Zeitzonenverarbeitung**: pytz
- **Steuerungslogik**: batcontrol (externe Bibliothek)

### Berechnung
- Alle internen Berechnungen erfolgen in Wh bzw. kWh
- PV-Strom wird prioritär für direkten Verbrauch genutzt
- Überschüssiger PV-Strom lädt die Batterie (wenn Kapazität vorhanden)
- Batterie hat konfigurierbare Lade-/Entladegrenzen
- Kosten = Netzbezug × Strompreis

### Optimierungsansatz (Modell 3)
Das Optimierungsproblem minimiert die Gesamtstromkosten über 24 Stunden unter Berücksichtigung von:
- Energiebilanz (Verbrauch = Netzbezug + Batterie + PV - Überschuss)
- Batterie-Kapazitätsgrenzen (min/max SOC)
- Lade-/Entladeleistungsgrenzen
- Preisabhängiger Ladefreigabe (nur bei günstigen Preisen aus Netz laden)

## Ergebnisse

Für jedes Modell werden folgende Ergebnisse ausgegeben:
- **Netzbezug**: Stündlicher Bezug aus dem Netz (Wh)
- **Batteriebezug**: Stündliche Entladung der Batterie (Wh)
- **Kosten pro Stunde**: Stündliche Stromkosten (€)
- **Batteriestand**: Ladezustand nach jeder Stunde (Wh)
- **Gesamtkosten**: Summe der Stromkosten über 24 Stunden (€)
- **Gewichteter Durchschnittspreis**: Effektiver Strompreis (€/kWh, nur bei dynamischen Preisen)

## Beispiel-Szenario

Ein typisches Szenario könnte sein:
- **Batterie**: 10 kWh Kapazität, 5 kW Lade-/Entladeleistung
- **PV-Anlage**: 8 kWp, typisches Tages-Erzeugungsprofil
- **Verbrauch**: Haushalts-Lastprofil mit ca. 15 kWh/Tag
- **Preise**: Variable Börsenstrompreise (0,15-0,45 €/kWh)

Die Simulation zeigt dann, wie viel Geld durch intelligente Batteriesteuerung im Vergleich zu einfacher Nutzung gespart werden kann.

## Lizenz

Dieses Projekt verwendet die [batcontrol-Bibliothek](https://github.com/muexxl/batcontrol), die unter der MIT-Lizenz steht.

## Beiträge

Beiträge sind willkommen! Bitte öffnen Sie ein Issue oder erstellen Sie einen Pull Request.

