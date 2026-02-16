import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
import os
import sys
import json
import base64

# Google Sheets Imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PyPDF2 import PdfReader, PdfWriter
import io

# --- CONFIGURACIÓN ---
# GOOGLE SHEETS ID
SHEET_ID = '1IrXOacbJUN8PpsWWbfzhwkNkT_VQlJfUlOw4zd3REpE' # ID de tu Hoja de Calculo
CREDS_FILE = 'credentials.json'

# MODO DE PRUEBA (True = No envia correos reales, solo simula)
# Intentar leer de variable de entorno, si no existe, False (producción)
DRY_RUN = os.getenv('DRY_RUN', 'False').lower() == 'true'

# CREDENCIALES DE CORREO
# Configurado para privodeveloper.com (asumiendo cPanel/hosting estándar)
SMTP_SERVER = 'mail.privodeveloper.com' 
SMTP_PORT = 465 
EMAIL_USER = os.getenv('EMAIL_USER', 'admin@privodeveloper.com') 
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'Privo*20') 
EMAIL_CC = os.getenv('EMAIL_CC', 'nmilano@privodeveloper.com, admin@privodeveloper.com, Jserva@gmail.com, nlamorgiabondar@gmail.com')

# LOG DE ENVÍOS
LOG_FILE = 'log_envios.txt'

# ARCHIVOS ADJUNTOS POR IDIOMA
# Estos archivos deben existir en la misma carpeta del script
ATTACHMENTS = {
    'es': 'INFORMACION BANCARIA BLH.pdf',
    'en': 'BANKING INFORMATION BLH.pdf'
}

# --- PLANTILLAS DE CORREO (Español e Inglés) ---
# --- PLANTILLAS DE CORREO (Español e Inglés) ---
TEMPLATES = {
    'es': {
        'V-7': {
            'subject': 'Aviso anticipado de vencimiento – Cuota mensual EOS VISTACANA',
            'body': """Estimado/a [Nombre]:

Reciba un cordial saludo. Le recordamos que, conforme a su plan de pagos vigente, la próxima cuota mensual correspondiente a su unidad en el proyecto EOS VISTACANA vencerá el día [FECHA].

Agradecemos que pueda programar su pago con antelación. A continuación, encontrará los detalles necesarios:

- Monto a pagar: US$ [XXX.XX]
- Fecha de vencimiento: [FECHA]
- Métodos de pago disponibles: En el archivo adjunto

Quedamos atentos ante cualquier consulta o requerimiento adicional."""
        },
        'V-2': {
            'subject': 'Aviso anticipado de vencimiento – Cuota mensual EOS VISTACANA',
            'body': """Estimado/a [Nombre]:

Le saludamos cordialmente. Le recordamos que, según lo establecido en su plan de pagos, su cuota mensual vence en 2 días, el [FECHA].

-Monto: US$ [XXX.XX]

Agradecemos su puntualidad. Quedamos a su disposición en caso de requerir asistencia."""
        },
        'V+3': {
            'subject': 'Aviso de cuota vencida – EOS VISTACANA',
            'body': """Estimado/a [Nombre]:

Nos dirigimos a usted para informarle que, hasta la fecha, no hemos recibido confirmación del pago correspondiente a su cuota mensual con vencimiento el pasado [FECHA].

Agradecemos que, en caso de haber realizado el pago, nos remita el comprobante correspondiente. Si aún no lo ha efectuado, le invitamos a regularizar la situación a la mayor brevedad posible a fin de evitar recargos o penalidades contractuales.

Quedamos atentos a su confirmación."""
        },
        'V+7': {
            'subject': 'Aviso de cuota vencida – EOS VISTACANA',
            'body': """Estimado/a [Nombre]:

Han transcurrido 7 días desde el vencimiento de su cuota correspondiente al mes en curso. Le invitamos a regularizar su situación a la brevedad, evitando así la aplicación de penalidades.

Quedamos atentos a sus comentarios o requerimientos."""
        },
        'V+15': {
            'subject': 'Notificación formal de mora – EOS VISTACANA',
            'body': """Estimado/a [Nombre]:

Le notificamos que su cuenta presenta un atraso de 15 días en el pago de la cuota correspondiente al mes en curso, con fecha de vencimiento el [FECHA].

Según lo estipulado en su contrato, esta situación puede conllevar la aplicación de recargos, así como medidas contractuales adicionales.

Le instamos a regularizar su situación a la brevedad posible para evitar mayores consecuencias."""
        }
    },
    'en': {
        'V-7': {
            'subject': 'Early Payment Notice – Monthly Installment EOS VISTACANA',
            'body': """Dear [Nombre]:

Warm regards. We would like to remind you that, in accordance with your current payment plan, the next monthly installment for your unit at EOS VISTACANA project is due on [FECHA].

We appreciate you scheduling your payment in advance. Below, you will find the necessary details:

- Amount to pay: US$ [XXX.XX]
- Due date: [FECHA]
- Available payment methods: In the attached file

We remain attentive to any questions or additional requirements."""
        },
        'V-2': {
            'subject': 'Early Payment Notice – Monthly Installment EOS VISTACANA',
            'body': """Dear [Nombre]:

Warm regards. We remind you that, according to your payment plan, your monthly installment is due in 2 days, on [FECHA].

-Amount: US$ [XXX.XX]

We appreciate your punctuality. We remain at your disposal should you require assistance."""
        },
        'V+3': {
            'subject': 'Overdue Installment Notice – EOS VISTACANA',
            'body': """Dear [Nombre]:

We are writing to inform you that, to date, we have not received confirmation of the payment corresponding to your monthly installment due on [FECHA].

We appreciate that, if you have already made the payment, you send us the corresponding proof. If you have not yet done so, we invite you to regularize the situation as soon as possible in order to avoid surcharges or contractual penalties.

We remain attentive to your confirmation."""
        },
        'V+7': {
            'subject': 'Overdue Installment Notice – EOS VISTACANA',
            'body': """Dear [Nombre]:

7 days have passed since the due date of your installment corresponding to the current month. We invite you to regularize your situation as soon as possible, thus avoiding the application of penalties.

We remain attentive to your comments or requirements."""
        },
        'V+15': {
            'subject': 'Formal Default Notification – EOS VISTACANA',
            'body': """Dear [Nombre]:

We notify you that your account shows a 15-day delay in the payment of the installment corresponding to the current month, due on [FECHA].

As stipulated in your contract, this situation may entail the application of surcharges, as well as additional contractual measures.

We urge you to regularize your situation as soon as possible to avoid further consequences."""
        }
    }
}

def enviar_correo(destinatarios_str, asunto, cuerpo, attachment_path=None):
    """Envía un correo electrónico a uno o varios destinatarios (separados por coma)."""
    try:
        if not destinatarios_str or pd.isna(destinatarios_str):
            print("  [e] Email vacío, saltando.")
            return False
            
        # Separar correos por coma, limpiar espacios whitespaces
        lista_destinatarios = [e.strip() for e in str(destinatarios_str).replace(';',',').split(',') if e.strip()]
        
        if not lista_destinatarios:
             print("  [e] No hay emails válidos tras limpiar.")
             return False

        if DRY_RUN:
            print(f"  [DRY_RUN] Simulando envío a: {lista_destinatarios}")
            print(f"  [DRY_RUN] CC: {EMAIL_CC}")
            print(f"  [DRY_RUN] Asunto: {asunto}")
            print(f"  [DRY_RUN] Adjunto: {attachment_path if attachment_path else 'Ninguno'}")
            print(f"  [DRY_RUN] Cuerpo (truncado): {cuerpo[:50]}...")
            return True


        msg = MIMEMultipart('mixed')
        msg['From'] = EMAIL_USER
        msg['To'] = ", ".join(lista_destinatarios)
        msg['Cc'] = EMAIL_CC
        msg['Subject'] = asunto

        # Estructura:
        # MIXED (Root)
        #  |-- RELATED (Contenido visual)
        #  |    |-- ALTERNATIVE (Texto)
        #  |    |    |-- HTML
        #  |    |-- IMAGE (Logo CID)
        #  |-- APPLICATION (PDF Adjunto)

        msg_related = MIMEMultipart('related')
        msg.attach(msg_related)

        # Construir contenido HTML
        # Reemplazar saltos de línea por <br>
        cuerpo_html = cuerpo.replace('\n', '<br>')
        
        # HTML Template
        html_content = f"""
        <html>
          <body>
            <div style="font-family: Arial, sans-serif; color: #333;">
              <div style="padding: 20px; background-color: #f9f9f9; border-radius: 5px;">
                <p>{cuerpo_html}</p>
              </div>
              <div style="margin-top: 30px; border-top: 1px solid #ccc; padding-top: 10px; text-align: left; color: #555;">
                <p><strong>Marialis Muro</strong><br>
                admin@privodeveloper.com</p>
                <div style="margin-top: 15px;">
                    <img src="cid:logo_img" alt="EOS VISTACANA" width="80" style="width: 80px; max-width: 80px; height: auto;">
                </div>
              </div>
            </div>
          </body>
        </html>
        """

        # Adjuntar parte HTML al contenedor RELATED
        msg_related.attach(MIMEText(html_content, 'html'))

        # Adjuntar Imagen (Logo) al contenedor RELATED
        logo_path = 'logo.jpg'
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=os.path.basename(logo_path))
                image.add_header('Content-ID', '<logo_img>')
                image.add_header('Content-Disposition', 'inline', filename=os.path.basename(logo_path)) # Inline explícito
                msg_related.attach(image)
        else:
            print("  [!] Advertencia: No se encontró logo.jpg")

        # Adjuntar PDF (Metodos de Pago) al contenedor raíz MIXED
        # Adjuntar PDF (Metodos de Pago) al contenedor raíz MIXED
        if attachment_path and os.path.exists(attachment_path):
            try:
                # ESTRATEGIA: Añadir página en blanco para forzar vista de icono en Apple Mail
                pdf_bytes = io.BytesIO()
                
                with open(attachment_path, 'rb') as f:
                    reader = PdfReader(f)
                    writer = PdfWriter()
                    
                    # Copiar páginas originales
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    # Añadir página en blanco (mismo tamaño que la ultima o default)
                    if len(reader.pages) > 0:
                        last_page = reader.pages[-1]
                        width = last_page.mediabox.width
                        height = last_page.mediabox.height
                        writer.add_blank_page(width=width, height=height)
                    else:
                        writer.add_blank_page()
                        
                    writer.write(pdf_bytes)
                
                pdf_bytes.seek(0)
                file_content = pdf_bytes.read()
                file_name = os.path.basename(attachment_path)
                
                # Usar application/pdf normal, ya que el multipage debería ser suficiente
                attach = MIMEApplication(file_content, _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=file_name)
                msg.attach(attach)
                
                # Mantener truco de texto vacío por si acaso
                msg.attach(MIMEText('', 'plain')) 
                
            except Exception as e:
                print(f"  [!] Error adjuntando/modificando PDF {attachment_path}: {e}")
                # Fallback: adjuntar original si falla PyPDF2
                try:
                    with open(attachment_path, 'rb') as f:
                        attach = MIMEApplication(f.read(), _subtype="pdf")
                        attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                        msg.attach(attach)
                except:
                    pass
        elif attachment_path:
             # Si se especificó un adjunto pero no existe
             print(f"  [!] Advertencia: No se encontró el archivo adjunto '{attachment_path}'")
             
        # Conexión al servidor
        # Configuración SSL/TLS según imagen del cliente (Puerto 465)
        try:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            # server.starttls() # No necesario para SSL en 465
        except:
             # Fallback genérico por si acaso
            server = smtplib.SMTP(SMTP_SERVER, 587)
            server.starttls()
            
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        
        # Enviar a todos los destinatarios Y al CC (soporte multiples CC)
        # EMAIL_CC puede ser "a@b.com, c@d.com" -> separar
        lista_cc = [e.strip() for e in str(EMAIL_CC).replace(';',',').split(',') if e.strip()]
        
        # Actualizar header CC en el mensaje para que se vea bonito
        if lista_cc:
             msg.replace_header('Cc', ", ".join(lista_cc))

        all_recipients = lista_destinatarios + lista_cc
        server.sendmail(EMAIL_USER, all_recipients, text)
        server.quit()
        return True
    except Exception as e:
        print(f"  [e] Error enviando correo a {destinatarios_str}: {e}")
        return False

def registrar_log(mensaje):
    """Registra el evento en un archivo de log."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {mensaje}\n")

# Función auxiliar para fechas en español (ej: 15-ago-27)
def parse_spanish_date(date_str):
    if not isinstance(date_str, str):
        return pd.NaT
    
    date_str = date_str.lower().strip()
    replacements = {
        'ene': 'jan', 'feb': 'feb', 'mar': 'mar', 'abr': 'apr', 'may': 'may', 'jun': 'jun',
        'jul': 'jul', 'ago': 'aug', 'sep': 'sep', 'oct': 'oct', 'nov': 'nov', 'dic': 'dec',
        'sept': 'sep' # Caso especial
    }
    
    for es, en in replacements.items():
        if es in date_str:
            date_str = date_str.replace(es, en)
            break
            
    try:
        # Intentar formatos comunes
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        return pd.NaT

def main():
    print("--- INICIANDO AUTOMAILER (Google Sheets) ---")
    
    # 1. Leer Google Sheet
    try:
        print(f"Conectando a Google Sheets (ID: {SHEET_ID})...")
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Intentar leer credenciales de Variable de Entorno (Render)
        env_creds = os.getenv('GOOGLE_CREDENTIALS_BASE64')
        if env_creds:
            print("  [i] Usando credenciales de variable de entorno (BASE64)")
            creds_dict = json.loads(base64.b64decode(env_creds))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        elif os.path.exists(CREDS_FILE):
             print(f"  [i] Usando archivo de credenciales local: {CREDS_FILE}")
             creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        else:
             raise Exception("No se encontraron credenciales de Google (ni archivo ni ENV).")

        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(SHEET_ID)
        
        # ! IMPORTANTE: Usar la pestaña "BOT MENSAJES"
        try:
            worksheet = sheet.worksheet('BOT MENSAJES')
        except:
            print("[!] No se encontró la pestaña 'BOT MENSAJES', intentando índice 0")
            worksheet = sheet.get_worksheet(0)
        
        print(f"Accediendo a pestaña: {worksheet.title}")
        
        # Leer todos los valores (devuelve lista de listas, todo string)
        data = worksheet.get_all_values()
        
        if not data:
             print("[!] La hoja está vacía.")
             return

        headers = data[0]
        rows = data[1:]
        
        # Crear DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        print(f"Datos cargados: {len(df)} filas.")
        
    except Exception as e:
        print(f"[!] Error leyendo Google Sheet: {e}")
        return

    # 3. Validar columnas esperadas (BOT MENSAJES structure)
    # 3. Validar columnas esperadas (BOT MENSAJES structure)
    # Se añade 'Pagado' como opcional/esperada
    expected_cols = ['Comprador', 'Email', 'Fecha_Vencimiento', 'Monto', 'Idioma', 'Ultimo_Aviso']
    # column 'Pagado' is checked dynamically later
    current_cols = df.columns.tolist()
    
    missing = [c for c in expected_cols if c not in current_cols]
    if missing:
        print(f"[!] Faltan columnas en 'BOT MENSAJES': {missing}")
        return

    # Asignar nombres directos
    col_nombre = 'Comprador'
    col_email = 'Email'
    col_fecha = 'Fecha_Vencimiento'
    col_monto = 'Monto'
    col_idioma = 'Idioma'
    col_aviso = 'Ultimo_Aviso'

    # FILTRO: Eliminar filas vacías
    df = df[df[col_nombre] != '']
    print(f"Filas tras limpieza: {len(df)}")
    
    fecha_hoy = pd.Timestamp.now().normalize()
    print(f"Fecha de hoy: {fecha_hoy.strftime('%d/%m/%Y')}")

    correos_enviados_count = 0

    count_processed = 0
    for index, row in df.iterrows():
        count_processed += 1

        nombre = row[col_nombre]
        email = str(row.get(col_email, '')).strip()
        idioma_raw = str(row.get(col_idioma, 'Español')).lower()
        
        # Detectar idioma
        lang_code = 'es' # Default
        if 'ingl' in idioma_raw or 'english' in idioma_raw:
            lang_code = 'en'
        
        # Si no hay email, loguear
        if not email or pd.isna(email) or email == '':
             if not DRY_RUN:
                 print(f"  [!] Saltando {nombre} (No Email)")
                 continue
             else:
                 email = "cliente_sin_email@demo.com" # Dummy for dry run testing logic

        # Filtro de Estado: Asumimos 'Pendiente' si está en la lista de cobros
        estado = 'Pendiente' 

        # Parsear fecha
        fecha_orig = row[col_fecha]
        
        # Intentar parseo directo o con helper
        try:
             fecha_venc = pd.to_datetime(fecha_orig, dayfirst=True)
        except:
             fecha_venc = parse_spanish_date(str(fecha_orig))
        
        if pd.isna(fecha_venc):
            # print(f"  [i] Fecha inválida para {nombre}: {fecha_orig}")
            continue
        
        # Monto
        val_monto = str(row[col_monto]).strip()
        # Limpieza básica de monto
        val_monto = str(row[col_monto]).strip()
        val_monto_clean = val_monto.replace('$', '').replace('US', '').strip()
        monto = 0.0
        
        try:
             # Si tiene punto y coma, determinar cual es decimal
             if ',' in val_monto_clean and '.' in val_monto_clean:
                 if val_monto_clean.rfind(',') > val_monto_clean.rfind('.'): # 1.234,56 (Euro/Latam)
                      val_monto_clean = val_monto_clean.replace('.', '').replace(',', '.')
                 else: # 1,234.56 (US)
                      val_monto_clean = val_monto_clean.replace(',', '')
             elif ',' in val_monto_clean: 
                  # Caso ambiguo: 124,56 o 1,234
                  # Si tiene decimales (2 chars al final), es decimal
                  if len(val_monto_clean.split(',')[-1]) == 2:
                      val_monto_clean = val_monto_clean.replace(',', '.')
                  else:
                      val_monto_clean = val_monto_clean.replace(',', '')
             
             monto = float(val_monto_clean)
        except:
             monto = 0.0
        
        ultimo_aviso = str(row['Ultimo_Aviso']) if pd.notna(row['Ultimo_Aviso']) else ""

        if pd.isna(fecha_venc):
            continue

        # Asegurar tipos compatibles (pd.Timestamp)
        if not isinstance(fecha_venc, pd.Timestamp):
            fecha_venc = pd.to_datetime(fecha_venc)
            
        if not isinstance(fecha_hoy, pd.Timestamp):
            fecha_hoy = pd.to_datetime(fecha_hoy)

        # Asegurar naive
        if fecha_venc.tzinfo is not None:
            fecha_venc = fecha_venc.tz_localize(None)
        if fecha_hoy.tzinfo is not None:
             fecha_hoy = fecha_hoy.tz_localize(None)

        # Calcular días restantes
        delta = fecha_venc - fecha_hoy
        dias_restantes = delta.days

        print(f"Calculando para {nombre}: Vence {fecha_venc.strftime('%d/%m/%Y')} ({dias_restantes} días) - Monto: {monto}")

        tipo_aviso = None
        
        # Reglas de negocio
        # Reglas de negocio
        
        # 1. Chequeo de Pagado
        pagado_val = str(row.get('Pagado', '')).lower().strip()
        is_pagado = pagado_val in ['si', 'x', 'yes', 'ok', 'verdadero', 'true']
        
        if dias_restantes == 7:
            tipo_aviso = 'V-7'
            # SIEMPRE SE ENVIA (Solicitud Usuario)
        elif dias_restantes == 2:
            tipo_aviso = 'V-2'
            # SIEMPRE SE ENVIA (Solicitud Usuario)
        
        # Lógica para fechas pasadas (Vencido)
        elif dias_restantes < 0:
            if is_pagado:
                # AUTO-ADVANCE: Si ya pagó y la fecha venció, avanzar al próximo mes
                try:
                    # Calcular nueva fecha (+1 mes)
                    nueva_fecha = fecha_venc + pd.DateOffset(months=1)
                    nueva_fecha_str = nueva_fecha.strftime('%d/%m/%Y')
                    
                    if not DRY_RUN:
                        print(f"  [AUTO-ADVANCE] {nombre} pagó. Avanzando fecha de {fecha_venc.strftime('%d/%m/%Y')} a {nueva_fecha_str}")
                        
                        # Actualizar Google Sheet (Fila = index + 2)
                        # Asumimos que 'Fecha_Vencimiento' está en columna C (3) y 'Pagado' en alguna otra.
                        # Mejor buscar indices por encabezado
                        idx_fecha_col = headers.index(col_fecha) + 1
                        idx_pagado_col = -1
                        if 'Pagado' in headers:
                             idx_pagado_col = headers.index('Pagado') + 1
                        
                        sheet_row = index + 2
                        
                        # Actualizar Fecha
                        worksheet.update_cell(sheet_row, idx_fecha_col, nueva_fecha_str)
                        
                        # Limpiar Pagado
                        if idx_pagado_col != -1:
                            worksheet.update_cell(sheet_row, idx_pagado_col, "")
                            
                        registrar_log(f"AUTO-ADVANCE: {nombre} - Fecha actualizada a {nueva_fecha_str}")
                    else:
                        print(f"  [DRY_RUN] [AUTO-ADVANCE] Se avanzaría fecha a {nueva_fecha_str} y limpiaría 'Pagado'")
                        
                except Exception as e:
                    print(f"  [!] Error en Auto-Advance para {nombre}: {e}")
                
                # No enviar correo de atraso si ya pagó
                tipo_aviso = None 
                
            else:
                # NO ha pagado y está vencido -> Reclamos
                if dias_restantes == -3:
                    tipo_aviso = 'V+3'
                elif dias_restantes == -7:
                    tipo_aviso = 'V+7'
                elif dias_restantes == -15:
                    tipo_aviso = 'V+15'

        
        # Omitir validación de 'Ultimo_Aviso' por simplicidad (según código previo)
        
        if tipo_aviso:
            print(f"  -> Corresponde enviar aviso {tipo_aviso} ({lang_code})")
            
            # Seleccionar plantilla por Idioma y Tipo
            try:
                template = TEMPLATES[lang_code][tipo_aviso]
            except KeyError:
                print(f"  [!] No existe plantilla para {lang_code}/{tipo_aviso}. Usando Español.")
                template = TEMPLATES['es'][tipo_aviso]

            # Formato español para correo: 1.234,56
            monto_str = f"{monto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            cuerpo_final = template['body'].replace('[Nombre]', str(nombre))\
                                           .replace('[FECHA]', fecha_venc.strftime('%d/%m/%Y'))\
                                           .replace('[XXX.XX]', monto_str)
                                           
            asunto_final = template['subject']
            
            # Seleccionar archivo adjunto según idioma
            attachment_path = ATTACHMENTS.get(lang_code)

            # Enviar correo (pasa 'email' que puede tener comas)
            if enviar_correo(email, asunto_final, cuerpo_final, attachment_path):
                log_msg = f"Enviado {tipo_aviso} ({lang_code}) a {email} ({nombre}) [Adjunto: {attachment_path}]"
                registrar_log(log_msg)
                print(f"  [v] Correo enviado exitosamente.")
                
                # Actualizar columna Ultimo_Aviso en memoria (y luego guardar)
                df.at[index, 'Ultimo_Aviso'] = f"{tipo_aviso} ({fecha_hoy.strftime('%Y-%m-%d')})"
                correos_enviados_count += 1
            else:
                log_msg = f"FALLO envio {tipo_aviso} ({lang_code}) a {email} ({nombre})"
                registrar_log(log_msg)
        else:
            pass # No corresponde aviso hoy

    # Guardar cambios en Excel (para actualizar Ultimo_Aviso)
    if correos_enviados_count > 0:
        try:
            df.to_excel(EXCEL_FILE, index=False)
            print(f"Archivo Excel actualizado con {correos_enviados_count} registros de aviso.")
        except Exception as e:
            print(f"[!] Error guardando Excel: {e}")
    else:
        print("No se enviaron correos, no es necesario actualizar el Excel.")

    print("--- PROCESO TERMINADO ---")

if __name__ == '__main__':
    main()
