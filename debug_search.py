import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    # Abrir Tab 0 "Plan de pagos"
    sheet = client.open_by_key('1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE')
    worksheet = sheet.get_worksheet(0)
    
    # Buscar "E04"
    cell = worksheet.find("E04")
    print(f"E04 encontrado en: Fila {cell.row}, Col {cell.col}")
    
    # Buscar "E02"
    cell2 = worksheet.find("E02")
    print(f"E02 encontrado en: Fila {cell2.row}, Col {cell2.col}")

except Exception as e:
    print(e)
