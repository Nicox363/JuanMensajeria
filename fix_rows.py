import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- CONFIGURACIÓN ---
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

def main():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet('Review fechas compraventa')
    except:
        worksheet = sheet.get_worksheet(1) 

    print(f"Abriendo pestaña: {worksheet.title}")
    
    data = worksheet.get_all_values()
    headers = data[0]
    
    # Encontrar indice de columna Villa (1-based para update_cell)
    # Headers is 0-based list. So index + 1
    try:
        villa_idx = headers.index('Villa') + 1
    except ValueError:
        print("ERROR: No se encuentra columna 'Villa'")
        return

    print(f"Columna Villa es la número: {villa_idx}")

    # Iterar y buscar
    for i, row in enumerate(data):
        # row is list of strings
        # i=0 is headers
        if i == 0: continue
        
        # Check Comprador (assuming it's column index 1 based on previous logs)
        # But safer to find index
        try:
            comp_idx_list = headers.index('Comprador')
        except:
            continue
            
        comprador = row[comp_idx_list]
        
        if 'Nicola' in comprador and 'TEST' in comprador:
            row_num = i + 1 # 1-based row index
            print(f"Fila {row_num}: {comprador} -> Actualizando Villa...")
            worksheet.update_cell(row_num, villa_idx, 'TEST-FIXED')
            print("OK")

if __name__ == '__main__':
    main()
