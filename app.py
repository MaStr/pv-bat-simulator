from flask import Flask, render_template, request, jsonify
import json
import pulp as pl
import numpy as np
import datetime
import pytz

# Import batcontrol logic
from batcontrol.logic.default import DefaultLogic
from batcontrol.logic.logic_interface import CalculationInput, CalculationParameters

app = Flask(__name__)

def berechne_linearer_verbrauch(statischer_preis, verbrauch, pv_strom, batterie_kapazitaet, 
                                max_lade_leistung, max_entlade_leistung, preis_abstand):
    """
    Modell 1: Linearer Verbrauch mit Batterie-Simulation und statischem Preis
    
    Parameter:
    - statischer_preis: Konstanter Strompreis (€/kWh)
    - verbrauch: Liste mit 24 Verbrauchswerten (Wh)
    - pv_strom: Liste mit 24 PV-Stromerzeugungswerten (Wh)
    - batterie_kapazitaet: Batteriekapazität (Wh)
    - max_lade_leistung: Maximale Ladeleistung (W)
    - max_entlade_leistung: Maximale Entladeleistung (W)
    - preis_abstand: Preislicher Abstand für dynamisches Nachladen (€/kWh)
    """
    
    # Initialisierung
    batterie_stand = 0  # Aktueller Batteriestand in Wh
    netzbezug = []
    batteriebezug = []
    kosten_pro_stunde = []
    batterie_stand_verlauf = []
    
    for stunde in range(24):
        bedarf = verbrauch[stunde]  # Wh
        pv = pv_strom[stunde]  # Wh
        
        # PV-Strom wird zuerst für Verbrauch verwendet
        if pv >= bedarf:
            # PV deckt Verbrauch vollständig
            ueberschuss = pv - bedarf
            
            # Überschuss in Batterie laden (wenn Platz ist)
            ladung = min(ueberschuss, 
                        batterie_kapazitaet - batterie_stand,
                        max_lade_leistung)
            batterie_stand += ladung
            
            netzbezug_stunde = 0
            batteriebezug_stunde = 0
            kosten_stunde = 0
            
        else:
            # PV deckt Verbrauch nicht vollständig
            fehlbetrag = bedarf - pv
            
            # Versuche aus Batterie zu decken
            entladung = min(fehlbetrag, 
                          batterie_stand,
                          max_entlade_leistung)
            batterie_stand -= entladung
            batteriebezug_stunde = entladung
            
            # Rest aus Netz
            netz = fehlbetrag - entladung
            netzbezug_stunde = netz
            
            # Kosten nur für Netzbezug (statischer Preis)
            kosten_stunde = (netz / 1000) * statischer_preis  # Wh -> kWh, dann * Preis
        
        netzbezug.append(round(netzbezug_stunde, 2))
        batteriebezug.append(round(batteriebezug_stunde, 2))
        kosten_pro_stunde.append(round(kosten_stunde, 4))
        batterie_stand_verlauf.append(round(batterie_stand, 2))
    
    gesamtkosten = sum(kosten_pro_stunde)
    
    return {
        'netzbezug': netzbezug,
        'batteriebezug': batteriebezug,
        'kosten_pro_stunde': kosten_pro_stunde,
        'batterie_stand': batterie_stand_verlauf,
        'gesamtkosten': round(gesamtkosten, 2)
    }


def berechne_linearer_verbrauch_dynamisch(preise, verbrauch, pv_strom, batterie_kapazitaet, 
                                          max_lade_leistung, max_entlade_leistung):
    """
    Modell 2: Linearer Verbrauch mit dynamischen Strompreisen (ungesteuerte Batterie)
    
    Die Batterie wird linear genutzt (wie in Modell 1), aber mit dynamischen Strompreisen.
    Am Ende wird ein nach Verbrauch gewichteter Durchschnittspreis berechnet.
    
    Parameter:
    - preise: Liste mit 24 dynamischen Strompreisen (€/kWh)
    - verbrauch: Liste mit 24 Verbrauchswerten (Wh)
    - pv_strom: Liste mit 24 PV-Stromerzeugungswerten (Wh)
    - batterie_kapazitaet: Batteriekapazität (Wh)
    - max_lade_leistung: Maximale Ladeleistung (W)
    - max_entlade_leistung: Maximale Entladeleistung (W)
    """
    
    # Initialisierung
    batterie_stand = 0  # Aktueller Batteriestand in Wh
    netzbezug = []
    batteriebezug = []
    kosten_pro_stunde = []
    batterie_stand_verlauf = []
    verwendete_preise = []  # Preise für tatsächlichen Netzbezug
    
    for stunde in range(24):
        preis = preise[stunde]
        bedarf = verbrauch[stunde]  # Wh
        pv = pv_strom[stunde]  # Wh
        
        # PV-Strom wird zuerst für Verbrauch verwendet
        if pv >= bedarf:
            # PV deckt Verbrauch vollständig
            ueberschuss = pv - bedarf
            
            # Überschuss in Batterie laden (wenn Platz ist)
            ladung = min(ueberschuss, 
                        batterie_kapazitaet - batterie_stand,
                        max_lade_leistung)
            batterie_stand += ladung
            
            netzbezug_stunde = 0
            batteriebezug_stunde = 0
            kosten_stunde = 0
            
        else:
            # PV deckt Verbrauch nicht vollständig
            fehlbetrag = bedarf - pv
            
            # Versuche aus Batterie zu decken
            entladung = min(fehlbetrag, 
                          batterie_stand,
                          max_entlade_leistung)
            batterie_stand -= entladung
            batteriebezug_stunde = entladung
            
            # Rest aus Netz
            netz = fehlbetrag - entladung
            netzbezug_stunde = netz
            
            # Kosten mit aktuellem dynamischen Preis
            kosten_stunde = (netz / 1000) * preis  # Wh -> kWh, dann * Preis
        
        netzbezug.append(round(netzbezug_stunde, 2))
        batteriebezug.append(round(batteriebezug_stunde, 2))
        kosten_pro_stunde.append(round(kosten_stunde, 4))
        batterie_stand_verlauf.append(round(batterie_stand, 2))
        verwendete_preise.append(round(preis, 4))
    
    gesamtkosten = sum(kosten_pro_stunde)
    gesamt_netzbezug_kwh = sum(netzbezug) / 1000  # Wh -> kWh
    
    # Gewichteter Durchschnittspreis berechnen
    if gesamt_netzbezug_kwh > 0:
        gewichteter_preis = gesamtkosten / gesamt_netzbezug_kwh
    else:
        gewichteter_preis = 0
    
    return {
        'netzbezug': netzbezug,
        'batteriebezug': batteriebezug,
        'kosten_pro_stunde': kosten_pro_stunde,
        'batterie_stand': batterie_stand_verlauf,
        'preise': verwendete_preise,
        'gesamtkosten': round(gesamtkosten, 2),
        'gesamt_netzbezug_kwh': round(gesamt_netzbezug_kwh, 2),
        'gewichteter_preis': round(gewichteter_preis, 4)
    }


def berechne_aktive_steuerung(preise, verbrauch, pv_strom, batterie_kapazitaet, 
                               max_lade_leistung, max_entlade_leistung, preis_abstand, anfangs_soc=0.0):
    """
    Modell 3: Aktive Steuerung mit dynamischen Strompreisen (PuLP-Optimierung)
    
    Basiert auf pulp_ansatz_solar.py:
    - Intelligente Batteriesteuerung basierend auf Strompreisen
    - Bei niedrigen Preisen: Batterie laden (auch aus dem Netz)
    - Bei hohen Preisen: Batterie entladen
    - PV-Überschuss wird priorisiert für Batterieladung
    
    Parameter:
    - preise: Liste mit 24 dynamischen Strompreisen (€/kWh)
    - verbrauch: Liste mit 24 Verbrauchswerten (Wh)
    - pv_strom: Liste mit 24 PV-Stromerzeugungswerten (Wh)
    - batterie_kapazitaet: Batteriekapazität (Wh)
    - max_lade_leistung: Maximale Ladeleistung (W)
    - max_entlade_leistung: Maximale Entladeleistung (W)
    - preis_abstand: Mindestpreisdifferenz für aktives Nachladen (€/kWh)
    - anfangs_soc: Anfänglicher Ladestand der Batterie um 24 Uhr (0.0-1.0, Standard: 0.0)
    """
    
    # Konvertiere Wh in kWh für die Optimierung
    verbrauch_kwh = [v / 1000 for v in verbrauch]
    pv_kwh = [pv / 1000 for pv in pv_strom]
    batterie_kapazitaet_kwh = batterie_kapazitaet / 1000
    max_lade_kwh = max_lade_leistung / 1000
    max_entlade_kwh = max_entlade_leistung / 1000
    
    # Minimale Batterieladung (15%)
    min_akku_charge = 0.0
    min_akku_charge_abs = min_akku_charge * batterie_kapazitaet_kwh
    
    time_steps = list(range(24))
    
    # Ermittle maximalen Preis für Ladefreigabe-Logik
    max_price = max(preise)
    
    # Initialisiere das Optimierungsproblem
    prob = pl.LpProblem("Aktive_Batteriesteuerung", pl.LpMinimize)
    
    # Variablen definieren (wie in pulp_ansatz_solar.py)
    P_netz = pl.LpVariable.dicts("P_netz", time_steps, lowBound=0, cat='Continuous')
    # P_akku: Negativ = Laden, Positiv = Entladen
    P_akku = pl.LpVariable.dicts("P_akku", time_steps, lowBound=-max_lade_kwh, 
                                  upBound=max_entlade_kwh, cat='Continuous')
    E_akku = pl.LpVariable.dicts("E_akku", time_steps, lowBound=min_akku_charge_abs, 
                                  upBound=batterie_kapazitaet_kwh, cat='Continuous')
    # Überschuss-Variable (PV-Strom, der nicht genutzt werden kann)
    P_ueber = pl.LpVariable.dicts("P_ueber", time_steps, lowBound=0, cat='Continuous')
    
    # Zielfunktion: Minimierung der Stromkosten
    prob += pl.lpSum([P_netz[t] * preise[t] for t in time_steps])
    
    # Ladefreigabe basierend auf Preisdifferenz
    ladefreigabe = [1 if preise[t] < max_price - preis_abstand else 0 for t in time_steps]
    
    # Nebenbedingungen
    for t in time_steps:
        # Energiebilanz: Verbrauch = Netzbezug + Akkubezug + PV-Strom - Überschuss
        # (wie in pulp_ansatz_solar.py)
        prob += verbrauch_kwh[t] == P_netz[t] + P_akku[t] + pv_kwh[t] - P_ueber[t]
        
        # Überschuss-Begrenzung: Nur möglich wenn Akku voll ist
        # (wie in pulp_ansatz_solar.py)
        if t > 0:
            prob += P_ueber[t] <= (E_akku[t-1] - batterie_kapazitaet_kwh) * max_lade_kwh * -1
        
        # Ladezustand des Akkus
        # (wie in pulp_ansatz_solar.py)
        if t == 0:
            # Anfangszustand: 20% geladen
            anfangs_ladung = anfangs_soc
            prob += E_akku[t] == (anfangs_ladung * batterie_kapazitaet_kwh) - P_akku[t]
        else:
            prob += E_akku[t] == E_akku[t-1] - P_akku[t]
        
        # Ladefreigabe für den Akku aus dem Netz
        # (wie in pulp_ansatz_solar.py)
        if ladefreigabe[t] == 0:
            if verbrauch_kwh[t] - pv_kwh[t] >= 0:
                # Kein Überschuss, also Akku darf nicht geladen werden
                prob += P_akku[t] >= 0
            else:
                # Überschuss vorhanden, Akku darf mit Überschuss geladen werden
                prob += P_akku[t] >= (verbrauch_kwh[t] - pv_kwh[t])
    
    # Problem lösen
    prob.solve(pl.PULP_CBC_CMD(msg=0))  # msg=0 unterdrückt Output
    
    # Ergebnisse extrahieren und zurück in Wh konvertieren
    netzbezug = []
    batteriebezug = []  # Positiv = Entladung
    kosten_pro_stunde = []
    batterie_stand_verlauf = []
    pv_ueberschuss = []
    
    for t in time_steps:
        # Netzbezug
        netz = P_netz[t].varValue
        netzbezug.append(round(netz * 1000, 2))  # kWh -> Wh
        
        # Batteriebezug: Wenn P_akku positiv, dann Entladung
        akku = P_akku[t].varValue
        if akku > 0:
            batteriebezug.append(round(akku * 1000, 2))
        else:
            batteriebezug.append(0.0)
        
        # Kosten für Netzbezug
        kosten_stunde = netz * preise[t]
        kosten_pro_stunde.append(round(kosten_stunde, 4))
        
        # Batteriestand
        batterie_stand_verlauf.append(round(E_akku[t].varValue * 1000, 2))
        
        # PV-Überschuss (ins Netz eingespeist)
        pv_ueberschuss.append(round(P_ueber[t].varValue * 1000, 2))
    
    gesamtkosten = sum(kosten_pro_stunde)
    gesamt_netzbezug_kwh = sum(netzbezug) / 1000
    
    # Gewichteter Durchschnittspreis
    if gesamt_netzbezug_kwh > 0:
        gewichteter_preis = gesamtkosten / gesamt_netzbezug_kwh
    else:
        gewichteter_preis = 0
    
    return {
        'netzbezug': netzbezug,
        'batteriebezug': batteriebezug,
        'kosten_pro_stunde': kosten_pro_stunde,
        'batterie_stand': batterie_stand_verlauf,
        'preise': [round(p, 4) for p in preise],
        'gesamtkosten': round(gesamtkosten, 2),
        'gesamt_netzbezug_kwh': round(gesamt_netzbezug_kwh, 2),
        'gewichteter_preis': round(gewichteter_preis, 4),
        'pv_ueberschuss': pv_ueberschuss,
        'optimierungsstatus': pl.LpStatus[prob.status]
    }


def berechne_batcontrol_steuerung(preise, verbrauch, pv_strom, batterie_kapazitaet, 
                                   max_lade_leistung, max_entlade_leistung, 
                                   min_preis_differenz, always_allow_discharge_limit, 
                                   max_charging_from_grid_limit, anfangs_soc=0.2):
    """
    Modell 4: BatControl-Steuerung mit drei Modi
    
    Verwendet die originale batcontrol-Bibliothek von muexxl:
    - MODE 10 (DISCHARGE ALLOWED): Normale Nutzung, Batterie entladen erlaubt
    - MODE 0 (AVOID DISCHARGE): Netzbezug statt Batterieentladung bei steigenden Preisen
    - MODE -1 (CHARGE FROM GRID): Batterie aus dem Netz laden bei niedrigen Preisen
    
    Parameter:
    - preise: Liste mit 24 dynamischen Strompreisen (€/kWh)
    - verbrauch: Liste mit 24 Verbrauchswerten (Wh)
    - pv_strom: Liste mit 24 PV-Stromerzeugungswerten (Wh)
    - batterie_kapazitaet: Batteriekapazität (Wh)
    - max_lade_leistung: Maximale Ladeleistung (W)
    - max_entlade_leistung: Maximale Entladeleistung (W)
    - min_preis_differenz: Mindestpreisdifferenz für Laden aus dem Netz (€/kWh)
    - always_allow_discharge_limit: SOC-Grenze ab der immer entladen werden darf (0.0-1.0)
    - max_charging_from_grid_limit: Maximaler SOC beim Laden aus dem Netz (0.0-1.0)
    - anfangs_soc: Anfänglicher Ladestand der Batterie (0.0-1.0, Standard: 0.2)
    """
    
    # Konvertiere Wh in kWh für batcontrol
    verbrauch_kwh = np.array([v / 1000 for v in verbrauch])
    pv_kwh = np.array([pv / 1000 for pv in pv_strom])
    batterie_kapazitaet_kwh = batterie_kapazitaet / 1000
    
    # Initialisiere batcontrol DefaultLogic
    timezone = pytz.timezone('Europe/Berlin')
    logic = DefaultLogic(timezone)
    
    # Setze Calculation Parameters
    calc_params = CalculationParameters(
        max_charging_from_grid_limit=max_charging_from_grid_limit,
        min_price_difference=min_preis_differenz,
        min_price_difference_rel=0.0,
        max_capacity=batterie_kapazitaet_kwh
    )
    logic.set_calculation_parameters(calc_params)
    
    # Setze always_allow_discharge_limit über common logic
    logic.common.set_always_allow_discharge_limit(always_allow_discharge_limit)
    
    # Initialisierung für Simulation
    batterie_stand_kwh = anfangs_soc * batterie_kapazitaet_kwh  # in kWh
    netzbezug = []
    netzeinspeisung = []
    batteriebezug = []
    kosten_pro_stunde = []
    batterie_stand_verlauf = []
    modi_verlauf = []
    
    # Simuliere Stunde für Stunde mit batcontrol-Logik
    for stunde in range(24):
        # Verbleibende Stunden für Forecast
        verbleibende_stunden = 24 - stunde
        
        # Erstelle Forecast-Arrays für die verbleibenden Stunden
        future_consumption = verbrauch_kwh[stunde:stunde+verbleibende_stunden]
        future_production = pv_kwh[stunde:stunde+verbleibende_stunden]
        future_prices = {i: preise[stunde + i] for i in range(len(future_consumption))}
        
        # Berechne verfügbare und genutzte Kapazität
        stored_usable_energy_kwh = batterie_stand_kwh
        free_capacity_kwh = batterie_kapazitaet_kwh - batterie_stand_kwh
        
        # Erstelle CalculationInput für batcontrol
        calc_input = CalculationInput(
            production=future_production,
            consumption=future_consumption,
            prices=future_prices,
            stored_energy=batterie_stand_kwh,
            stored_usable_energy=stored_usable_energy_kwh,
            free_capacity=free_capacity_kwh
        )
        
        # Rufe batcontrol-Logik auf
        current_time = datetime.datetime.now(timezone).replace(hour=stunde, minute=0, second=0)
        logic.calculate(calc_input, current_time)
        inverter_settings = logic.get_inverter_control_settings()
        
        # Interpretiere Entscheidung von batcontrol
        bedarf_kwh = verbrauch_kwh[stunde]
        pv_kwh_stunde = pv_kwh[stunde]
        preis = preise[stunde]
        
        # Berechne PV-Überschuss oder Fehlbetrag
        pv_bilanz = pv_kwh_stunde - bedarf_kwh
        
        # Bestimme Modus basierend auf batcontrol-Entscheidung
        if inverter_settings.charge_from_grid:
            modus = -1  # CHARGE FROM GRID
            charge_rate_kwh = inverter_settings.charge_rate / 1000  # W -> kWh
            
            # Lade Batterie mit PV-Überschuss
            if pv_bilanz > 0:
                ladung_pv = min(pv_bilanz, free_capacity_kwh)
                batterie_stand_kwh += ladung_pv
                free_capacity_kwh -= ladung_pv
                pv_ueberschuss = ladung_pv
            else:
                pv_ueberschuss = 0

            # Zusätzlich aus Netz laden (bis zum Limit)
            max_netz_ladung = min(
                charge_rate_kwh - pv_ueberschuss,
                batterie_kapazitaet_kwh * max_charging_from_grid_limit - batterie_stand_kwh
            )
            max_netz_ladung = max(0, max_netz_ladung)  # Nicht negativ
            batterie_stand_kwh += max_netz_ladung
            
            # Netzbezug: Fehlbetrag (falls vorhanden) + Netzladung
            netzbezug_kwh = max(0, -pv_bilanz) + max_netz_ladung
            netzeinspeisung_kwh = max_netz_ladung
            batteriebezug_kwh = 0
                
        elif not inverter_settings.allow_discharge:
            modus = 0  # AVOID DISCHARGE
            
            # Lade Batterie mit PV-Überschuss
            if pv_bilanz > 0:
                ladung = min(pv_bilanz, free_capacity_kwh)
                batterie_stand_kwh += ladung
                netzbezug_kwh = 0
            else:
                # Fehlbetrag aus Netz (nicht aus Batterie!)
                netzbezug_kwh = -pv_bilanz
            
            netzeinspeisung_kwh = 0
            batteriebezug_kwh = 0
                
        else:
            modus = 10  # DISCHARGE ALLOWED
            
            # Lade Batterie mit PV-Überschuss
            if pv_bilanz > 0:
                ladung = min(pv_bilanz, free_capacity_kwh)
                batterie_stand_kwh += ladung
                netzbezug_kwh = 0
                batteriebezug_kwh = 0
            else:
                # Fehlbetrag aus Batterie decken
                fehlbetrag = -pv_bilanz
                entladung = min(fehlbetrag, batterie_stand_kwh)
                batterie_stand_kwh -= entladung
                batteriebezug_kwh = entladung
                
                # Rest aus Netz
                netzbezug_kwh = fehlbetrag - entladung
            
            netzeinspeisung_kwh = 0
        
        # Kosten berechnen (nur für Netzbezug)
        kosten_stunde = netzbezug_kwh * preis
        
        # Konvertiere zurück in Wh für Ausgabe
        netzbezug.append(round(netzbezug_kwh * 1000, 2))
        netzeinspeisung.append(round(netzeinspeisung_kwh * 1000, 2))
        batteriebezug.append(round(batteriebezug_kwh * 1000, 2))
        kosten_pro_stunde.append(round(kosten_stunde, 4))
        batterie_stand_verlauf.append(round(batterie_stand_kwh * 1000, 2))
        modi_verlauf.append(modus)
    
    gesamtkosten = sum(kosten_pro_stunde)
    gesamt_netzbezug_kwh = sum(netzbezug) / 1000
    
    # Gewichteter Durchschnittspreis
    if gesamt_netzbezug_kwh > 0:
        gewichteter_preis = gesamtkosten / gesamt_netzbezug_kwh
    else:
        gewichteter_preis = 0
    
    return {
        'netzbezug': netzbezug,
        'netzeinspeisung': netzeinspeisung,
        'batteriebezug': batteriebezug,
        'kosten_pro_stunde': kosten_pro_stunde,
        'batterie_stand': batterie_stand_verlauf,
        'preise': [round(p, 4) for p in preise],
        'modi': modi_verlauf,
        'gesamtkosten': round(gesamtkosten, 2),
        'gesamt_netzbezug_kwh': round(gesamt_netzbezug_kwh, 2),
        'gewichteter_preis': round(gewichteter_preis, 4)
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/beispieldaten', methods=['GET'])
def beispieldaten():
    """
    Liefert Beispieldaten für das Frontend
    """
    return jsonify({
        'verbrauch': [300, 250, 200, 180, 200, 350, 500, 600, 400, 350, 
                      300, 350, 400, 350, 300, 400, 600, 800, 900, 700, 
                      600, 500, 400, 350],
        'pv_strom': [0, 0, 0, 0, 0, 50, 200, 400, 600, 800, 
                     900, 950, 900, 800, 600, 400, 200, 50, 0, 0, 
                     0, 0, 0, 0],
        'preise': [0.319, 0.316, 0.315, 0.315, 0.31, 0.32, 0.33, 0.38, 0.40, 0.39, 
                   0.37, 0.365, 0.36, 0.36, 0.37, 0.389, 0.42, 0.42, 0.41, 0.39, 
                   0.37, 0.35, 0.34, 0.32]
    })


@app.route('/berechnen', methods=['POST'])
def berechnen():
    try:
        data = request.json
        
        # Modell auswählen
        modell = data.get('modell', 1)
        
        # Gemeinsame Eingabedaten extrahieren
        verbrauch = [float(x) for x in data['verbrauch']]
        pv_strom = [float(x) for x in data['pv_strom']]
        batterie_kapazitaet = float(data['batterie_kapazitaet'])
        max_lade_leistung = float(data['max_lade_leistung'])
        max_entlade_leistung = float(data['max_entlade_leistung'])
        
        # Validierung
        if len(verbrauch) != 24 or len(pv_strom) != 24:
            return jsonify({'error': 'Es müssen genau 24 Werte für Verbrauch und PV-Strom angegeben werden'}), 400
        
        if modell == 1:
            # Modell 1: Statischer Preis
            statischer_preis = float(data['statischer_preis'])
            preis_abstand = float(data['preis_abstand'])
            
            ergebnis = berechne_linearer_verbrauch(
                statischer_preis, verbrauch, pv_strom, 
                batterie_kapazitaet, max_lade_leistung, 
                max_entlade_leistung, preis_abstand
            )
        elif modell == 2:
            # Modell 2: Dynamische Preise
            preise = [float(x) for x in data['preise']]
            
            if len(preise) != 24:
                return jsonify({'error': 'Es müssen genau 24 Werte für dynamische Preise angegeben werden'}), 400
            
            ergebnis = berechne_linearer_verbrauch_dynamisch(
                preise, verbrauch, pv_strom, 
                batterie_kapazitaet, max_lade_leistung, 
                max_entlade_leistung
            )
        elif modell == 3:
            # Modell 3: Aktive Steuerung mit Optimierung
            preise = [float(x) for x in data['preise']]
            preis_abstand = float(data['preis_abstand'])
            anfangs_soc = float(data.get('anfangs_soc', 0.0))
            
            if len(preise) != 24:
                return jsonify({'error': 'Es müssen genau 24 Werte für dynamische Preise angegeben werden'}), 400
            
            ergebnis = berechne_aktive_steuerung(
                preise, verbrauch, pv_strom, 
                batterie_kapazitaet, max_lade_leistung, 
                max_entlade_leistung, preis_abstand, anfangs_soc
            )
        elif modell == 4:
            # Modell 4: BatControl Steuerung
            preise = [float(x) for x in data['preise']]
            min_preis_differenz = float(data.get('min_preis_differenz', 0.05))
            always_allow_discharge_limit = float(data.get('always_allow_discharge_limit', 0.9))
            max_charging_from_grid_limit = float(data.get('max_charging_from_grid_limit', 0.8))
            anfangs_soc = float(data.get('anfangs_soc', 0.2))
            
            if len(preise) != 24:
                return jsonify({'error': 'Es müssen genau 24 Werte für dynamische Preise angegeben werden'}), 400
            
            ergebnis = berechne_batcontrol_steuerung(
                preise, verbrauch, pv_strom, 
                batterie_kapazitaet, max_lade_leistung, 
                max_entlade_leistung, min_preis_differenz,
                always_allow_discharge_limit, max_charging_from_grid_limit,
                anfangs_soc
            )
        else:
            return jsonify({'error': 'Ungültiges Modell'}), 400
        
        return jsonify(ergebnis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
