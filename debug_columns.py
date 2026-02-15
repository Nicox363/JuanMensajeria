import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE')
    try:
        worksheet = sheet.worksheet('Review fechas compraventa')
    except:
        worksheet = sheet.get_worksheet(1)
        
    data = worksheet.get_all_values()
    headers = data[0]
    print("--- COLUMNAS ENCONTRADAS (Review fechas compraventa) ---")
    for i, col in enumerate(headers):
        print(f"[{i}] '{col}'")
                
    print("\n--- BUSQUEDA 'antes de la entrega' ---")
    found = any('antes de la entrega' in h for h in headers)
    print(f"Encontrado: {found}")
    
except Exception as e:
    print(e)
