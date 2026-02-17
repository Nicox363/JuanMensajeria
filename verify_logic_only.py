
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64
import pandas as pd
from datetime import datetime

SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

def verify():
    print("--- VERIFICACION DE LOGICA (SOLO LECTURA) ---")
    
    # 1. Conectar GSheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    if os.path.exists(CREDS_FILE):
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    else:
        print("[!] Sin credenciales")
        return

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet('BOT MENSAJES')
    except:
        worksheet = sheet.get_worksheet(0)

    rows = worksheet.get_all_values()
    headers = rows.pop(0)
    df = pd.DataFrame(rows, columns=headers)

    print(f"Columnas: {list(df.columns)}")
    
    # 2. Iterar filas y aplicar lógica EXACTA de automailer.py
    for index, row in df.iterrows():
        nombre = row.get('Comprador', 'Sin Nombre')
        
        # LOGICA DEL TOGGLE
        enviar_val = str(row.get('Enviar_Correos', '')).lower().strip()
        should_send = enviar_val in ['si', 'x', 'yes', 'ok', 'verdadero', 'true']
        
        print(f"FILA {index+2}: {nombre}")
        print(f"  > Valor RAW 'Enviar_Correos': '{row.get('Enviar_Correos', '[VACIO]')}'")
        print(f"  > Valor Clean: '{enviar_val}'")
        print(f"  > Should Send? {should_send}")
        
        if not should_send:
            print(f"  RESULTADO: [SALTAR] (Correcto si está desmarcado)")
        else:
            print(f"  RESULTADO: [ENVIAR] (Correcto si está marcado)")
        print("-" * 30)

if __name__ == "__main__":
    verify()
