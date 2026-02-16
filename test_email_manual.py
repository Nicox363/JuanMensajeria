
import automailer
import os

# Override CC to avoid spamming real admins during this test, 
# or set it to one of the test emails if we want to test CC specifically.
# Given the request "solo ...", I will clear the default CC and send to both as 'To' or one 'To' one 'CC'.
# Let's put both in 'To' for simplicity and clear the global CC.
print("--- CONFIGURING TEST ---")
automailer.EMAIL_CC = "" 
print(f"EMAIL_CC cleared: '{automailer.EMAIL_CC}'")

# Ensure PDF exists
pdf_path = automailer.ATTACHMENTS['es']
if not os.path.exists(pdf_path):
    print(f"ERROR: PDF not found at {pdf_path}")
    # Create a dummy one if missing for some reason
    with open(pdf_path, 'wb') as f:
        f.write(b'%PDF-1.5\n%...')
    print("Created dummy PDF for testing.")

recipients = "Jserva@gmail.com, nlamorgiabondar@gmail.com"
subject = "TEST - Fix Apple Mail (Blank Page)"
body = "Este es un correo de prueba para verificar que el PDF adjunto no se previsualiza en Apple Mail.\n\nSe ha añadido una página en blanco al final del documento."

print(f"Enviando correo a: {recipients}")
success = automailer.enviar_correo(recipients, subject, body, pdf_path)

if success:
    print("--- TEST COMPLETED SUCCESSFULLY ---")
else:
    print("--- TEST FAILED ---")
