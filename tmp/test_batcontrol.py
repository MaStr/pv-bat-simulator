#!/usr/bin/env python3
"""Test script to debug batcontrol option 4"""

import sys
import os
import logging

# Add batcontrol to path
sys.path.insert(0, '/home/matze/projects/batcontrol/bc-git-upstream/src')

import numpy as np
import datetime
import pytz

# Import only the logic submodules directly
from batcontrol.logic.default import DefaultLogic
from batcontrol.logic.logic_interface import CalculationInput, CalculationParameters

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_batcontrol_calculation():
    """Test batcontrol calculation with sample data"""
    
    print("=" * 80)
    print("Testing BatControl Calculation")
    print("=" * 80)
    
    # Sample data
    verbrauch = [500] * 24  # 500 Wh per hour
    pv_strom = [0] * 6 + [100, 200, 400, 600, 800, 1000, 1000, 800, 600, 400, 200, 100] + [0] * 6
    preise = [0.30, 0.28, 0.26, 0.25, 0.24, 0.23, 0.25, 0.28, 0.30, 0.32, 0.30, 0.28,
              0.26, 0.24, 0.22, 0.20, 0.22, 0.25, 0.28, 0.30, 0.32, 0.31, 0.29, 0.28]
    
    batterie_kapazitaet = 10000  # 10 kWh in Wh
    max_lade_leistung = 5000  # 5 kW in W
    max_entlade_leistung = 5000  # 5 kW in W
    min_preis_differenz = 0.05
    always_allow_discharge_limit = 0.9
    max_charging_from_grid_limit = 0.8
    anfangs_soc = 0.2
    
    # Convert Wh to kWh
    verbrauch_kwh = np.array([v / 1000 for v in verbrauch])
    pv_kwh = np.array([pv / 1000 for pv in pv_strom])
    batterie_kapazitaet_kwh = batterie_kapazitaet / 1000
    
    print(f"\nInput Parameters:")
    print(f"  Battery Capacity: {batterie_kapazitaet_kwh} kWh")
    print(f"  Max Charge: {max_lade_leistung/1000} kW")
    print(f"  Max Discharge: {max_entlade_leistung/1000} kW")
    print(f"  Initial SOC: {anfangs_soc * 100}%")
    print(f"  Min Price Diff: {min_preis_differenz} EUR/kWh")
    print(f"  Always Discharge Limit: {always_allow_discharge_limit * 100}%")
    print(f"  Max Grid Charging Limit: {max_charging_from_grid_limit * 100}%")
    
    # Initialize batcontrol
    timezone = pytz.timezone('Europe/Berlin')
    logic = DefaultLogic(timezone)
    
    # Set parameters
    calc_params = CalculationParameters(
        max_charging_from_grid_limit=max_charging_from_grid_limit,
        min_price_difference=min_preis_differenz,
        min_price_difference_rel=0.0,
        max_capacity=batterie_kapazitaet_kwh
    )
    logic.set_calculation_parameters(calc_params)
    logic.common.set_always_allow_discharge_limit(always_allow_discharge_limit)
    
    print(f"\nBatControl Parameters Set:")
    print(f"  logic.calculation_parameters: {logic.calculation_parameters}")
    print(f"  common.always_allow_discharge_limit: {logic.common.always_allow_discharge_limit}")
    
    # Simulate hour 0
    batterie_stand_kwh = anfangs_soc * batterie_kapazitaet_kwh
    
    print(f"\n{'='*80}")
    print(f"Simulating Hour 0")
    print(f"{'='*80}")
    
    stunde = 0
    verbleibende_stunden = 24 - stunde
    
    future_consumption = verbrauch_kwh[stunde:stunde+verbleibende_stunden]
    future_production = pv_kwh[stunde:stunde+verbleibende_stunden]
    future_prices = {i: preise[stunde + i] for i in range(len(future_consumption))}
    
    stored_usable_energy_kwh = batterie_stand_kwh
    free_capacity_kwh = batterie_kapazitaet_kwh - batterie_stand_kwh
    
    print(f"\nHour {stunde} Inputs:")
    print(f"  Current Consumption: {verbrauch_kwh[stunde]} kWh")
    print(f"  Current Production: {pv_kwh[stunde]} kWh")
    print(f"  Current Price: {preise[stunde]} EUR/kWh")
    print(f"  Battery State: {batterie_stand_kwh} kWh ({batterie_stand_kwh/batterie_kapazitaet_kwh*100:.1f}%)")
    print(f"  Free Capacity: {free_capacity_kwh} kWh")
    print(f"  Stored Usable Energy: {stored_usable_energy_kwh} kWh")
    
    # Create CalculationInput
    calc_input = CalculationInput(
        production=future_production,
        consumption=future_consumption,
        prices=future_prices,
        stored_energy=batterie_stand_kwh,
        stored_usable_energy=stored_usable_energy_kwh,
        free_capacity=free_capacity_kwh
    )
    
    print(f"\nCalculationInput created:")
    print(f"  production length: {len(future_production)}")
    print(f"  consumption length: {len(future_consumption)}")
    print(f"  prices length: {len(future_prices)}")
    
    # Call batcontrol
    current_time = datetime.datetime.now(timezone).replace(hour=stunde, minute=0, second=0)
    
    print(f"\nCalling logic.calculate()...")
    try:
        result = logic.calculate(calc_input, current_time)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ERROR during calculate: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get inverter settings
    print(f"\nGetting inverter settings...")
    try:
        inverter_settings = logic.get_inverter_control_settings()
        print(f"  Inverter Settings: {inverter_settings}")
        print(f"  - charge_from_grid: {inverter_settings.charge_from_grid}")
        print(f"  - allow_discharge: {inverter_settings.allow_discharge}")
        print(f"  - charge_rate: {inverter_settings.charge_rate} W")
    except Exception as e:
        print(f"  ERROR getting inverter settings: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n{'='*80}")
    print("Test completed successfully!")
    print(f"{'='*80}")

if __name__ == '__main__':
    test_batcontrol_calculation()
