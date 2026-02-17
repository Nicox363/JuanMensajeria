
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64
import pandas as pd

SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

def inspect():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if os.path.exists(CREDS_FILE):
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    else:
        env_creds = os.getenv('GOOGLE_CREDENTIALS_BASE64')
        if env_creds:
             creds_dict = json.loads(base64.b64decode(env_creds))
             creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
             print("[!] No se encontraron credenciales.")
             return

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet('BOT MENSAJES')

    # Obtener todos los valores raw strings
    rows = ws.get_all_values()
    headers = rows.pop(0)

    print(f"Encabezados: {headers}")
    
    if 'Enviar_Correos' not in headers:
        print("ERROR: No se encuentra la columna 'Enviar_Correos'")
        return

    idx = headers.index('Enviar_Correos')
    print(f"Indice de columna: {idx}")

    print("\n--- PRIMERAS 5 FILAS ---")
    for i, row in enumerate(rows[:5]):
        val = row[idx]
        nombre = row[headers.index('Comprador')] if 'Comprador' in headers else '?'
        print(f"Fila {i+2} ({nombre}): Valor='{val}' (Tipo: {type(val)})")
        
        normalized = str(val).lower().strip()
        should_send = normalized in ['si', 'x', 'yes', 'ok', 'verdadero', 'true']
        print(f"  -> Should send? {should_send}")

if __name__ == "__main__":
    inspect()
