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
        worksheet = sheet.get_worksheet(1) # Fallback

    print(f"Abriendo pestaña: {worksheet.title}")
    
    data = worksheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    
    df = pd.DataFrame(rows, columns=headers)
    
    print(f"Total filas: {len(df)}")
    print(f"Columnas: {df.columns.tolist()}")
    
    # Buscar Nicola
    nicola_rows = df[df['Comprador'].str.contains('Nicola', case=False, na=False)]
    
    if not nicola_rows.empty:
        print(f"Encontradas {len(nicola_rows)} filas para Nicola:")
        print(nicola_rows[['Villa', 'Comprador', 'Monto']].to_string())
        
        for idx, row in nicola_rows.iterrows():
            print(f"Fila {idx} VILLA: '{row['Villa']}'")
            col_fecha = next((c for c in df.columns if 'antes de la entrega' in str(c)), None)
            if col_fecha:
                print(f"Fila {idx} Fecha raw: '{row[col_fecha]}'")
    else:
        print("NO se encontraron filas para Nicola.")

if __name__ == '__main__':
    main()
