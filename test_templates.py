import automailer
import pandas as pd
from datetime import datetime, timedelta

# Configuración# DATOS DE PRUEBA
TEST_EMAIL = 'nlamorgiabondar@outlook.com'
TEST_NAME = 'Cliente Prueba'
TEST_AMOUNT = 1234.56
TEST_DATE = datetime.now() + timedelta(days=7) # Fecha futura

# Forzar envío real
automailer.DRY_RUN = False

print(f"--- INICIANDO ENVÍO DE 1 CORREO 'LIMPIO' A {TEST_EMAIL} ---")

# Elegimos envío V-7 en Español y luego Inglés para probar lógica de adjuntos
idiomas_prueba = ['es', 'en']

for lang in idiomas_prueba:
    print(f"\n--- Probando idioma: {lang.upper()} ---")
    tipo = 'V-7'
    template = automailer.TEMPLATES[lang][tipo]

    # Construir contenido FINAL (sin textos de prueba)
    subject = template['subject']
    monto_str = f"{TEST_AMOUNT:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    body = template['body'].replace('[Nombre]', TEST_NAME)\
                           .replace('[FECHA]', TEST_DATE.strftime('%d/%m/%Y'))\
                           .replace('[XXX.XX]', monto_str)
                           
    # Seleccionar archivo adjunto según idioma (Lógica copiada de main)
    attachment_path = automailer.ATTACHMENTS.get(lang)

    print(f"Enviando {tipo} ({lang}) con adjunto esperado: {attachment_path}")
    if automailer.enviar_correo(TEST_EMAIL, subject, body, attachment_path):
        print("  [OK] Correo enviado exitosamente.")
    else:
        print("  [ERROR] Falló el envío.")

print("\n--- PRUEBA FINALIZADA ---")
