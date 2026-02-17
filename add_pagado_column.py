
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64

SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

def add_column():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if os.path.exists(CREDS_FILE):
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    else:
        # Fallback to env var if needed (though local file is expected based on context)
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
    print(f"Headers actuales: {headers}")

    col_name = "Pagado"
    
    if col_name in headers:
        print(f"La columna '{col_name}' ya existe.")
        return

    # Encontrar siguiente columna vacía
    next_col_idx = len(headers) + 1
    print(f"Añadiendo '{col_name}' en columna {next_col_idx}...")
    
    ws.update_cell(1, next_col_idx, col_name)
    print("¡Columna añadida con éxito!")

if __name__ == "__main__":
    add_column()
