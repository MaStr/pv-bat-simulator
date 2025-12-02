#!/usr/bin/env python3
"""Test option 4 (batcontrol) via HTTP request"""

import requests
import json

# Sample data for testing
data = {
    'modell': 4,
    'verbrauch': [500] * 24,  # 500 Wh per hour
    'pv_strom': [0] * 6 + [100, 200, 400, 600, 800, 1000, 1000, 800, 600, 400, 200, 100] + [0] * 6,
    'batterie_kapazitaet': 10000,  # 10 kWh
    'max_lade_leistung': 5000,  # 5 kW
    'max_entlade_leistung': 5000,  # 5 kW
    'anfangs_soc': 0.2,  # 20%
    'preise': [0.30, 0.28, 0.26, 0.25, 0.24, 0.23, 0.25, 0.28, 0.30, 0.32, 0.30, 0.28,
               0.26, 0.24, 0.22, 0.20, 0.22, 0.25, 0.28, 0.30, 0.32, 0.31, 0.29, 0.28],
    'min_preis_differenz': 0.05,
    'always_allow_discharge_limit': 0.9,
    'max_charging_from_grid_limit': 0.8
}

print("="*80)
print("Testing BatControl Option 4")
print("="*80)
print(f"\nSending request to http://localhost:5000/berechnen")
print(f"Model: {data['modell']}")
print(f"Battery Capacity: {data['batterie_kapazitaet']} Wh")
print(f"Initial SOC: {data['anfangs_soc']*100}%")

try:
    response = requests.post('http://localhost:5000/berechnen', json=data)
    
    print(f"\nResponse Status Code: {response.status_code}")
    
    if response.ok:
        result = response.json()
        print("\nSUCCESS!")
        print(f"Total Cost: {result.get('gesamtkosten', 'N/A')} EUR")
        print(f"Total Grid Purchase: {result.get('gesamt_netzbezug_kwh', 'N/A')} kWh")
        print(f"Weighted Price: {result.get('gewichteter_preis', 'N/A')} EUR/kWh")
        print(f"\nFirst 5 hours:")
        for i in range(5):
            print(f"  Hour {i}: Grid={result['netzbezug'][i]} Wh, Battery={result['batteriebezug'][i]} Wh, "
                  f"Mode={result['modi'][i]}, SOC={result['batterie_stand'][i]} Wh, Cost={result['kosten_pro_stunde'][i]} EUR")
    else:
        print("\nERROR!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\nEXCEPTION: {type(e).__name__}: {e}")

print("="*80)
