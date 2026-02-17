
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64

SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

def add_checkbox():
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
    
    try:
        ws = sheet.worksheet('BOT MENSAJES')
    except:
        print("No se encontró la hoja BOT MENSAJES")
        return

    # Encontrar indice de columna 'Pagado'
    headers = ws.row_values(1)
    try:
        col_idx = headers.index("Pagado") + 1
    except ValueError:
        print("No se encontró la columna 'Pagado'. Ejecuta primero add_pagado_column.py")
        return

    print(f"Columna 'Pagado' encontrada en índice: {col_idx}")
    
    # Obtener ID de la hoja (sheetId)
    sheet_id = ws.id
    
    # Definir rango (Desde fila 2 hasta fila 1000)
    start_row_idx = 1 # 0-indexed API (Row 2)
    end_row_idx = 1000
    col_idx_api = col_idx - 1 # 0-indexed API

    # Request body para batchUpdate
    requests = [{
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row_idx,
                "endRowIndex": end_row_idx,
                "startColumnIndex": col_idx_api,
                "endColumnIndex": col_idx_api + 1
            },
            "rule": {
                "condition": {
                    "type": "BOOLEAN"
                },
                "showCustomUi": True
            }
        }
    }]
    
    print("Aplicando validación de Checkbox...")
    sheet.batch_update({'requests': requests})
    print("¡Checkbox aplicado con éxito!")

if __name__ == "__main__":
    add_checkbox()
