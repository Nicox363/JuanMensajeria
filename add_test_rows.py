import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import sys

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
    
    # Obtener encabezados
    headers = worksheet.row_values(1)
    print(f"Encabezados encontrados: {headers}")
    
    # Mapear columnas a indices (0-based en lista)
    col_map = {h.strip().replace('\n', ' '): i for i, h in enumerate(headers)}
    
    # Verificar y crear columnas faltantes si es necesario
    missing_cols = []
    if 'Email' not in col_map: missing_cols.append('Email')
    if 'Idioma' not in col_map: missing_cols.append('Idioma')
    if 'Ultimo_Aviso' not in col_map: missing_cols.append('Ultimo_Aviso')
    
    if missing_cols:
        print(f"Agregando columnas faltantes: {missing_cols}")
        # En gspread, para agregar columnas, escribimos en la fila 1, columna len(headers)+1
        # O simplemente actualizamos la celda de cabecera
        current_len = len(headers)
        for i, col_name in enumerate(missing_cols):
            worksheet.update_cell(1, current_len + 1 + i, col_name)
            
        # Re-leer headers
        headers = worksheet.row_values(1)
        col_map = {h.strip().replace('\n', ' '): i for i, h in enumerate(headers)}
    
    # Identificar columnas clave (ahora deberían estar todas)
    col_villa_idx = col_map.get('Villa')
    col_nombre_idx = col_map.get('Comprador')
    col_email_idx = col_map.get('Email')
    col_idioma_idx = col_map.get('Idioma')
    col_monto_idx = next((i for name, i in col_map.items() if name.lower() in ['monto', 'amount', 'importe', 'valor']), None)
    col_fecha_idx = next((i for name, i in col_map.items() if 'antes de la entrega' in name), None)
    
    # ... (rest of logic) ...

    # Datos a insertar
    test_rows = [
        {
            'Villa': 'TEST-UNIT-01',
            'Comprador': 'Nicola Español (TEST)',
            'Fecha': '17/02/2026', # +2 días desde 15/02
            'Email': 'nlamorgiabondar@gmail.com',
            'Monto': '100',
            'Idioma': 'Español'
        },
        {
            'Villa': 'TEST-UNIT-02',
            'Comprador': 'Nicola English (TEST)',
            'Fecha': '17/02/2026',
            'Email': 'nlamorgiabondar@gmail.com',
            'Monto': '200',
            'Idioma': 'English'
        }
    ]
    
    for row_data in test_rows:
        # Construir fila vacía del tamaño de headers
        new_row = [''] * len(headers)
        
        # Llenar datos
        if col_villa_idx is not None: new_row[col_villa_idx] = row_data['Villa']
        if col_nombre_idx is not None: new_row[col_nombre_idx] = row_data['Comprador']
        if col_fecha_idx is not None: new_row[col_fecha_idx] = row_data['Fecha']
        if col_email_idx is not None: new_row[col_email_idx] = row_data['Email']
        if col_monto_idx is not None: new_row[col_monto_idx] = row_data['Monto']
        if col_idioma_idx is not None: new_row[col_idioma_idx] = row_data['Idioma']
        
        # Append
        print(f"Agregando fila: {row_data['Comprador']}...")
        worksheet.append_row(new_row)
        print("OK.")

if __name__ == '__main__':
    main()
