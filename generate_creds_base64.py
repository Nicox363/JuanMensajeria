import base64
import json
import os

CREDS_FILE = 'credentials.json'

if os.path.exists(CREDS_FILE):
    with open(CREDS_FILE, 'rb') as f:
        creds_content = f.read()
        encoded = base64.b64encode(creds_content).decode('utf-8')
        
    print("\n--- COPIA ESTO EN RENDER (Variable de Entorno: GOOGLE_CREDENTIALS_BASE64) ---\n")
    print(encoded)
    print("\n--------------------------------------------------------------------------------\n")
else:
    print(f"Error: No encontré el archivo {CREDS_FILE}")
