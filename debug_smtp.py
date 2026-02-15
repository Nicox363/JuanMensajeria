import smtplib
from email.mime.text import MIMEText

# --- CONFIGURACIÓN A PROBAR ---
SMTP_SERVER = "mail.privodeveloper.com" # A veces es mail.tudominio.com
EMAIL_USER = "admin@privodeveloper.com"
EMAIL_PASS = "jueves16"  # OJO: Si falla, aquí va la App Password
DESTINATARIO = "nlamorgiabondar@gmail.com" # Para ver si llega

def probar_puerto_465():
    print(f"\n--- Probando Puerto 465 (SSL) en {SMTP_SERVER} ---")
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, 465, timeout=10) as server:
            print("✅ Conexión SSL exitosa.")
            server.login(EMAIL_USER, EMAIL_PASS)
            print("✅ Login exitoso.")
            msg = MIMEText("Prueba exitosa desde puerto 465")
            msg['Subject'] = "Test SMTP 465"
            msg['From'] = EMAIL_USER
            msg['To'] = DESTINATARIO
            server.sendmail(EMAIL_USER, DESTINATARIO, msg.as_string())
            print("🚀 Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ FALLÓ 465: {e}")

def probar_puerto_587():
    print(f"\n--- Probando Puerto 587 (TLS) en {SMTP_SERVER} ---")
    try:
        with smtplib.SMTP(SMTP_SERVER, 587, timeout=10) as server:
            print("✅ Conexión al puerto 587 exitosa.")
            server.starttls() # Importante para 587
            print("✅ STARTTLS iniciado.")
            server.login(EMAIL_USER, EMAIL_PASS)
            print("✅ Login exitoso.")
            msg = MIMEText("Prueba exitosa desde puerto 587")
            msg['Subject'] = "Test SMTP 587"
            msg['From'] = EMAIL_USER
            msg['To'] = DESTINATARIO
            server.sendmail(EMAIL_USER, DESTINATARIO, msg.as_string())
            print("🚀 Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ FALLÓ 587: {e}")

# Ejecutar pruebas
if __name__ == "__main__":
    probar_puerto_465()
    probar_puerto_587()
