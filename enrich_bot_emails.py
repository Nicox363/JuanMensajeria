import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import time

# --- CONFIGURACIÓN ---
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE'
CREDS_FILE = 'credentials.json'

SOURCE_SHEET = 'Plan de pagos'
TARGET_SHEET = 'BOT MENSAJES'

def main():
    print("Conectando a Google Sheets...")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(SHEET_ID)
    
    # 1. Leer FUENTE (Plan de pagos)
    print(f"Leyendo '{SOURCE_SHEET}'...")
    try:
        ws_source = sheet.worksheet(SOURCE_SHEET)
        data_source = ws_source.get_all_values()
    except Exception as e:
        print(f"[!] Error leyendo '{SOURCE_SHEET}': {e}")
        return

    # Crear Diccionario {Comprador: Email}
    # Asumimos headers en fila 1: Villa, Comprador, Email...
    headers_source = data_source[0]
    
    # Buscar indices
    try:
        idx_name_src = next(i for i, h in enumerate(headers_source) if 'omprador' in h) # Comprador
        idx_email_src = next(i for i, h in enumerate(headers_source) if 'mail' in h.lower()) # Email
    except StopIteration:
        print("[!] No se encontraron columnas 'Comprador' o 'Email' en Plan de pagos.")
        return

    email_map = {}
    for row in data_source[1:]:
        if len(row) > idx_name_src and len(row) > idx_email_src:
            name = row[idx_name_src].strip()
            email = row[idx_email_src].strip()
            if name and email:
                email_map[name] = email
    
    print(f"Mapa de emails creado: {len(email_map)} entradas.")

    # 2. Leer DESTINO (BOT MENSAJES)
    print(f"Leyendo '{TARGET_SHEET}'...")
    try:
        ws_target = sheet.worksheet(TARGET_SHEET)
        data_target = ws_target.get_all_values()
    except Exception as e:
        print(f"[!] Error leyendo '{TARGET_SHEET}': {e}")
        return
        
    if not data_target:
        print("[!] BOT MENSAJES está vacía.")
        return

    headers_target = data_target[0]
    # Buscar índices en destino
    try:
        # BOT MENSAJES headers: ['Villa', 'Comprador', 'Fecha_Vencimiento', 'Monto', 'Email', 'Idioma', 'Ultimo_Aviso']
        idx_name_tgt = headers_target.index('Comprador')
        idx_email_tgt = headers_target.index('Email')
    except ValueError as e:
         print(f"[!] Headers esperados no encontrados en BOT MENSAJES: {e}")
         print(f"Headers actuales: {headers_target}")
         return

    updates = []
    rows_updated = 0
    
    print("Procesando filas destino...")
    # Iterar y preparar updates
    # Google Sheets update batch usa A1 notation o update de rangos.
    # Para ser eficientes, mejor re-escribimos la columna Email entera o fila por fila si son pocas.
    # Dado que gspread update cell-by-cell es lento, re-subiremos toda la hoja updateada.
    
    new_data = [headers_target] # Start with headers
    
    for row in data_target[1:]:
        name = row[idx_name_tgt].strip()
        current_email = row[idx_email_tgt].strip()
        
        final_email = current_email
        
        # Si no tiene email, buscarlo
        if not current_email and name in email_map:
            final_email = email_map[name]
            rows_updated += 1
            # print(f"  + Encontrado email para '{name}': {final_email}")
        
        # Reconstruir fila con el email actualizado
        new_row = list(row) # Copia
        new_row[idx_email_tgt] = final_email
        new_data.append(new_row)

    if rows_updated > 0:
        print(f"Actualizando {rows_updated} filas en Google Sheets...")
        ws_target.clear()
        ws_target.update('A1', new_data)
        print("¡Hecho!")
    else:
        print("No se necesitaron actualizaciones (todos tenían email o no se encontraron coincidencias).")

if __name__ == '__main__':
    main()
