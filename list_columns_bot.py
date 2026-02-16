import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
        worksheet = sheet.worksheet('BOT MENSAJES')
        print(f"Abriendo pestaña: {worksheet.title}")
        # Leer primeras 5 filas para ver estructura
        data = worksheet.get_all_values()
        print(f"Total filas: {len(data)}")
        for i, row in enumerate(data[:5]):
            print(f"Fila {i+1}: {row}")
    except Exception as e:
        print(f"Error accediendo a BOT MENSAJES: {e}")

if __name__ == '__main__':
    main()
