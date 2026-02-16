import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import time

# --- CONFIGURACIÓN ---
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

SOURCE_SHEET = 'Plan de pagos'
TARGET_SHEET = 'BOT MENSAJES'

# Color objetivo (aproximado)
# BG={ red:1, green:0.92156863, blue:0.6117647 }
TARGET_COLOR = {'red': 1, 'green': 0.921, 'blue': 0.611}
TOLERANCE = 0.01

def is_target_color(bg_color):
    if not bg_color: return False
    
    r = bg_color.get('red', 0)
    g = bg_color.get('green', 0)
    b = bg_color.get('blue', 0)
    
    return (abs(r - TARGET_COLOR['red']) < TOLERANCE and
            abs(g - TARGET_COLOR['green']) < TOLERANCE and
            abs(b - TARGET_COLOR['blue']) < TOLERANCE)

def main():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    
    # 1. Obtener datos FUENTE (Plan de pagos) con FORMATO
    print(f"Descargando datos y formato de '{SOURCE_SHEET}' (esto puede tardar)...")
    token = creds.get_access_token().access_token
    headers = {'Authorization': f'Bearer {token}'}
    # Limitamos rango para no bajar todo el infinito, pero suficiente para cubrir el año
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}?ranges='{SOURCE_SHEET}'!A1:AZ200&includeGridData=true"
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Error fetching source data: {res.text}")
        return

    data_json = res.json()
    sheets_data = data_json.get('sheets', [])
    if not sheets_data:
        print("No data found.")
        return

    row_data = sheets_data[0]['data'][0].get('rowData', [])
    
    # Mapear Headers (Fila 1)
    if not row_data:
        print("Empty sheet.")
        return
        
    header_cells = row_data[0].get('values', [])
    headers = [c.get('formattedValue', '') for c in header_cells]
    
    try:
        idx_comprador = next(i for i, h in enumerate(headers) if 'omprador' in h)
        idx_email = next(i for i, h in enumerate(headers) if 'mail' in h.lower())
        idx_idioma = next(i for i, h in enumerate(headers) if 'dioma' in h)
    except StopIteration:
        print(f"No se encontraron columnas requeridas (Comprador, Email, Idioma) en {SOURCE_SHEET}")
        return

    print(f"Indices Fuente: Comprador={idx_comprador}, Email={idx_email}, Idioma={idx_idioma}")
    
    # Construir Tabla de Búsqueda
    lookup_map = {} # { "Juan Perez": { "email": "...", "idioma": "...", "fecha_pago": "..." } }
    
    for r_idx, row in enumerate(row_data[1:], start=1): # Skip header
        cells = row.get('values', [])
        if len(cells) <= idx_comprador: continue
        
        # Extraer Datos Básicos
        def get_val(idx):
            if idx < len(cells):
                return cells[idx].get('formattedValue', '').strip()
            return ''
            
        comprador = get_val(idx_comprador)
        email = get_val(idx_email)
        idioma = get_val(idx_idioma)
        
        if not comprador: continue
        
        # Buscar Fecha (Celda Amarilla)
        fecha_pago = ""
        # Empezamos a buscar despues de las columnas fijas para evitar falsos positivos
        # Adjust start column logic based on actual layout if needed.
        # Assuming dates are to the right of fixed columns.
        start_col = max(idx_comprador, idx_email, idx_idioma) + 1
        
        # Guard clause if start_col is out of bounds
        if start_col < len(cells):
            for c_idx in range(start_col, len(cells)):
                cell = cells[c_idx]
                bg = cell.get('effectiveFormat', {}).get('backgroundColor', {})
                if is_target_color(bg):
                    fecha_pago = cell.get('formattedValue', '')
                    # print(f"  -> Encontrada fecha para {comprador}: {fecha_pago} (Col {c_idx+1})")
                    break 
        
        lookup_map[comprador] = {
            'email': email,
            'idioma': idioma,
            'fecha_venc': fecha_pago # Can be empty if no yellow cell found
        }

    print(f"Mapa construido: {len(lookup_map)} entradas.")

    # 2. Actualizar DESTINO (BOT MENSAJES)
    sheet_obj = client.open_by_key(SHEET_ID)
    ws_target = sheet_obj.worksheet(TARGET_SHEET)
    
    target_vals = ws_target.get_all_values()
    if not target_vals:
        print("BOT MENSAJES vacio.")
        return
        
    headers_tgt = target_vals[0]
    # Headers esperados: ['Villa', 'Comprador', 'Fecha_Vencimiento', 'Monto', 'Email', 'Idioma', 'Ultimo_Aviso']
    try:
        i_comp = headers_tgt.index('Comprador')
        i_fecha = headers_tgt.index('Fecha_Vencimiento')
        i_email = headers_tgt.index('Email')
        i_idioma = headers_tgt.index('Idioma')
    except ValueError as e:
        print(f"Error en headers destino: {e}")
        return

    new_data = [headers_tgt]
    matches = 0
    
    for row in target_vals[1:]:
        new_row = list(row)
        # Asegurar longitud
        while len(new_row) < len(headers_tgt):
            new_row.append('')
            
        name = new_row[i_comp].strip()
        
        if name in lookup_map:
            info = lookup_map[name]
            
            # Actualizar si está vacío o forzar update? 
            # El usuario pidió "añade... tambien mapea", implica llenar/actualizar.
            
            if info['email']:
                new_row[i_email] = info['email']
            if info['idioma']:
                new_row[i_idioma] = info['idioma']
            if info['fecha_venc']:
                new_row[i_fecha] = info['fecha_venc']
                
            matches += 1
            
        new_data.append(new_row)

    print(f"Actualizando {len(new_data)-1} filas ({matches} coincidentes) en BOT MENSAJES...")
    ws_target.clear()
    ws_target.update('A1', new_data)
    print("¡Proceso completado!")

if __name__ == '__main__':
    main()
