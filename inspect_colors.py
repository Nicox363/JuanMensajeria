import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN ---
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'
SHEET_NAME = 'Plan de pagos'

def main():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.worksheet(SHEET_NAME)
    
    print(f"Inspeccionando colores en '{SHEET_NAME}' (Fila 5)...")
    
    # Obtener formatos de la fila 5 (asumiendo que hay datos ahi)
    # gspread > 6.0 formatting methods
    # Usaremos raw API access si es necesario, pero intentemos format info
    
    # Range A5:Z5
    formats = ws.get('A5:Z5', maintain_size=True) # get_all_values no trae formato.
    
    # Para formato necesitamos formatting. O usar spreadsheet.values().get con includeGridData=True (muy pesado).
    # GSpread tiene user_entered_format en versiones recientes o format().
    
    # Mejor enfoque: Usar client.request para fetch raw data de una fila y ver el JSON
    
    # Usar client.request para fetch raw data de primeras filas
    # Rows 2 to 5 (indices 1 to 4)
    # Fetch cols A to Z (assuming dates are there)
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?ranges='{SHEET_NAME}'!A2:Z5&includeGridData=true"
    
    try:
        # Access the underlying authorized session/request method
        if hasattr(client, 'session'):
            res = client.session.request('get', url)
        elif hasattr(client, 'auth') and hasattr(client.auth, 'request'): # oauth2client
             import requests
             token = client.auth.get_access_token().access_token
             headers = {'Authorization': f'Bearer {token}'}
             res = requests.get(url, headers=headers)
        else:
             import requests
             token = creds.get_access_token().access_token
             headers = {'Authorization': f'Bearer {token}'}
             res = requests.get(url, headers=headers)

        rows_data = res.json()
        
        sheets = rows_data.get('sheets', [])
        if not sheets:
            print("No se encontraron sheets.")
            return
            
        row_data_list = sheets[0]['data'][0].get('rowData', [])
        
        print(f"Propiedades de celdas (Filas 2-5):")
        
        for r_idx, row_data in enumerate(row_data_list):
            cells = row_data.get('values', [])
            for i, cell in enumerate(cells):
                val = cell.get('formattedValue', 'EMPTY')
                eff_fmt = cell.get('effectiveFormat', {})
                bg = eff_fmt.get('backgroundColor', {})
                
                # Check if white (empty or all 1s)
                is_white = (not bg) or (bg.get('red',0)==1 and bg.get('green',0)==1 and bg.get('blue',0)==1)
                
                if not is_white:
                    bg_str = ", ".join([f"{k}:{v}" for k,v in bg.items()])
                    print(f"Row {r_idx+2} Col {i+1} ('{val}'): BG={{ {bg_str} }}")

    except Exception as e:
        print(f"Error requesting colors: {e}")

if __name__ == '__main__':
    main()
