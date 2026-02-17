
import pandas as pd
from datetime import datetime, timedelta

# Mocking the new toggle logic from automailer.py

def test_logic(dias_restantes, enviar_correos_checked):
    tipo_aviso = None
    action = "NONE"
    
    # 1. Toggle Check
    if not enviar_correos_checked:
        return "SKIP", None

    # 2. Date Logic (Only if checked)
    if dias_restantes == 7:
        tipo_aviso = 'V-7'
        action = "SEND_EARLY"
    elif dias_restantes == 2:
        tipo_aviso = 'V-2'
        action = "SEND_EARLY"
    
    elif dias_restantes < 0:
        if dias_restantes == -3:
            tipo_aviso = 'V+3'
            action = "SEND_LATE"
        elif dias_restantes == -7:
            tipo_aviso = 'V+7'
            action = "SEND_LATE"
        elif dias_restantes == -15:
            tipo_aviso = 'V+15'
            action = "SEND_LATE"
                
    return action, tipo_aviso

print("--- TESTING TOGGLE LOGIC ---")

scenarios = [
    # (Days, Checked?, Expected Action, Expected Aviso)
    (7, True, "SEND_EARLY", "V-7"),     # Checked + Early -> Send
    (7, False, "SKIP", None),           # Unchecked + Early -> Skip
    (2, True, "SEND_EARLY", "V-2"),     # Checked + Early -> Send
    (2, False, "SKIP", None),           # Unchecked + Early -> Skip
    (-3, True, "SEND_LATE", "V+3"),     # Checked + Late -> Send
    (-3, False, "SKIP", None),          # Unchecked + Late -> Skip (Paid/Muted)
]

for days, checked, exp_action, exp_aviso in scenarios:
    act, av = test_logic(days, checked)
    status = "PASS" if act == exp_action and av == exp_aviso else "FAIL"
    print(f"Days: {days}, Checked: {checked} -> Got: {act}/{av} | Exp: {exp_action}/{exp_aviso} [{status}]")
