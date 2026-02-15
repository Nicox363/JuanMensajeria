import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'
SHEET_NAME = 'Review fechas compraventa'

def add_column():
    try:
        print("Conectando a Google Sheets...")
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(SHEET_ID)
        
        try:
            worksheet = sheet.worksheet(SHEET_NAME)
        except:
             # Fallback index 1 if name fails
            worksheet = sheet.get_worksheet(1)
            
        print(f"Accediendo a: {worksheet.title}")
        
        # Leer headers actuales (Fila 1)
        headers = worksheet.row_values(1)
        print(f"Headers actuales: {headers}")
        
        if "Monto" in headers:
            print("[INFO] La columna 'Monto' ya existe.")
            return

        # Calcular nueva columna
        new_col_index = len(headers) + 1
        
        # Escribir "Monto"
        worksheet.update_cell(1, new_col_index, "Monto")
        print(f"[EXITO] Columna 'Monto' agregada en la columna {new_col_index}")
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == '__main__':
    add_column()
