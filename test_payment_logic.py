
import pandas as pd
from datetime import datetime, timedelta

# Mocking the logic from automailer.py to test the conditions

def test_logic(dias_restantes, is_pagado):
    tipo_aviso = None
    action = "NONE"
    
    if dias_restantes == 7:
        tipo_aviso = 'V-7'
        action = "SEND_EARLY"
    elif dias_restantes == 2:
        tipo_aviso = 'V-2'
        action = "SEND_EARLY"
    
    elif dias_restantes < 0:
        if is_pagado:
            action = "AUTO_ADVANCE"
        else:
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

print("--- TESTING PAYMENT LOGIC ---")

scenarios = [
    # (Days, Paid?, Expected Action, Expected Aviso)
    (7, False, "SEND_EARLY", "V-7"),
    (7, True, "SEND_EARLY", "V-7"), # Should send even if paid (as per user request "siempre")
    (2, False, "SEND_EARLY", "V-2"),
    (2, True, "SEND_EARLY", "V-2"),
    (0, False, "NONE", None), # Due date, no action
    (-1, True, "AUTO_ADVANCE", None), # Paid and past due -> Advance
    (-3, False, "SEND_LATE", "V+3"), # Late and not paid -> Send
    (-3, True, "AUTO_ADVANCE", None), # Late but paid -> Advance
]

for days, paid, exp_action, exp_aviso in scenarios:
    act, av = test_logic(days, paid)
    status = "PASS" if act == exp_action and av == exp_aviso else "FAIL"
    print(f"Days: {days}, Paid: {paid} -> Got: {act}/{av} | Exp: {exp_action}/{exp_aviso} [{status}]")

