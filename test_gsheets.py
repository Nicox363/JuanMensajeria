import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Config
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = 'credentials.json'
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE' # Extracted from URL

def test_connection():
    print("--- PROBANDO CONEXIÓN A GOOGLE SHEETS ---")
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
        client = gspread.authorize(creds)
        print("  [OK] Autenticación correcta.")
        
        sheet = client.open_by_key(SHEET_ID)
        print(f"  [OK] Hoja encontrada: {sheet.title}")
        
        # Intentar leer la primera hoja workhseet
        # ! IMPORTANTE: Usar la pestaña "Review fechas compraventa" (Index 1)
        try:
            worksheet = sheet.worksheet('Review fechas compraventa')
        except:
            worksheet = sheet.get_worksheet(1)
            
        print(f"  [OK] Accediendo a pestaña: {worksheet.title}")
            
        # Usar get_all_values es más robusto para hojas con celdas combinadas o headers sucios
        data = worksheet.get_all_values()
        headers = data[0]
        rows = data[1:]
        
        # Buscar índice de "Monto"
        try:
             idx_monto = headers.index("Monto")
             print(f"\n--- COLUMNA MONTO ENCONTRADA (Índice {idx_monto}) ---")
             print("Primeros 5 valores:")
             for i, r in enumerate(rows[:5]):
                 val = r[idx_monto] if len(r) > idx_monto else "VACIO"
                 print(f"  Fila {i+1}: {val}")
        except ValueError:
             print("\n[!] AUN NO VEO LA COLUMNA 'Monto'.")
        
        # Asumimos que la primera fila son los headers
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        if 'Monto' in headers:
            idx = headers.index('Monto')
            print("\n--- VALORES COLUMNA 'Monto' (Primeras 5 filas) ---")
            for i, row in enumerate(rows[:5]):
                val = row[idx] if len(row) > idx else "N/A"
                print(f"Fila {i}: '{val}'")
        else:
            print("\n[!] NO SE ENCUENTRA LA COLUMNA 'Monto'")
            
        print("\n[ÉXITO] La conexión funciona correctamente.")
        return True
    except Exception as e:
        print(f"\n[ERROR] Falló la conexión: {e}")
        return False

if __name__ == '__main__':
    test_connection()
