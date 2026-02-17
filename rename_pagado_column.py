
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64

SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

def rename_column():
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

    # Leer headers (Fila 1)
    headers = ws.row_values(1)
    
    old_name = "Pagado"
    new_name = "Enviar_Correos"
    
    if old_name not in headers:
        print(f"No se encontró la columna '{old_name}'.")
        if new_name in headers:
            print(f"La columna '{new_name}' ya existe. No es necesario renombrar.")
        return

    col_idx = headers.index(old_name) + 1
    print(f"Renombrando '{old_name}' a '{new_name}' en columna {col_idx}...")
    
    ws.update_cell(1, col_idx, new_name)
    print("¡Renombrado con éxito!")

if __name__ == "__main__":
    rename_column()
