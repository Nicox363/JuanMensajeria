import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- CONFIGURACIÓN ---
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

OLD_SHEET_NAME = 'Review fechas compraventa'
NEW_SHEET_NAME = 'BOT MENSAJES'

NEW_HEADERS = ['Villa', 'Comprador', 'Fecha_Vencimiento', 'Monto', 'Email', 'Idioma', 'Ultimo_Aviso']

def main():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SHEET_ID)
    
    # 1. Leer datos antiguos
    print(f"Leyendo datos de '{OLD_SHEET_NAME}'...")
    try:
        ws_old = sheet.worksheet(OLD_SHEET_NAME)
    except:
        ws_old = sheet.get_worksheet(1) # Fallback index
        print(f"  (Usando índice 1: {ws_old.title})")

    data_old = ws_old.get_all_values()
    if not data_old:
        print("  [!] Hoja antigua vacía.")
        return

    headers_old = data_old[0]
    rows_old = data_old[1:]
    
    # Mapeo de columnas antiguas
    # Normalizar nombres para busqueda
    cols_map = {h.strip().replace('\n', ' '): i for i, h in enumerate(headers_old)}
    
    # Buscar índices clave
    idx_villa = cols_map.get('Villa')
    idx_comprador = cols_map.get('Comprador')
    
    # Buscar fecha (puede variar)
    idx_fecha = next((i for h, i in cols_map.items() if 'antes de la entrega' in h or 'fecha' in h.lower()), None)
    
    # Buscar monto
    idx_monto = next((i for h, i in cols_map.items() if h.lower() in ['monto', 'amount', 'importe']), None)
    
    idx_email = cols_map.get('Email')
    idx_idioma = cols_map.get('Idioma')
    idx_aviso = cols_map.get('Ultimo_Aviso')

    migrated_rows = []
    
    print(f"Procesando {len(rows_old)} filas...")
    for row in rows_old:
        # Extraer valores seguros (si el indice existe)
        villa = row[idx_villa] if idx_villa is not None and idx_villa < len(row) else ''
        comprador = row[idx_comprador] if idx_comprador is not None and idx_comprador < len(row) else ''
        
        # Filtro básico: Si no hay comprador, ignorar (a menos que sea test)
        if not comprador:
            continue
            
        fecha = row[idx_fecha] if idx_fecha is not None and idx_fecha < len(row) else ''
        monto = row[idx_monto] if idx_monto is not None and idx_monto < len(row) else ''
        email = row[idx_email] if idx_email is not None and idx_email < len(row) else ''
        idioma = row[idx_idioma] if idx_idioma is not None and idx_idioma < len(row) else 'Español' # Default
        aviso = row[idx_aviso] if idx_aviso is not None and idx_aviso < len(row) else ''
        
        migrated_rows.append([villa, comprador, fecha, monto, email, idioma, aviso])

    print(f"Filas listas para migrar: {len(migrated_rows)}")

    # 2. Preparar Hoja Nueva
    print(f"Preparando '{NEW_SHEET_NAME}'...")
    try:
        ws_new = sheet.worksheet(NEW_SHEET_NAME)
    except:
        print(f"  [!] No existe '{NEW_SHEET_NAME}', creándola...")
        ws_new = sheet.add_worksheet(title=NEW_SHEET_NAME, rows=1000, cols=20)
    
    # Borrar todo
    print("  Limpiando hoja destino...")
    ws_new.clear()
    
    # 3. Escribir Cabeceras y Datos
    print("  Escribiendo datos...")
    
    # Construir bloque completo
    all_values = [NEW_HEADERS] + migrated_rows
    
    # Update en batch
    ws_new.update(range_name=f'A1', values=all_values)
    
    print("Migración completada con éxito.")

if __name__ == '__main__':
    main()
