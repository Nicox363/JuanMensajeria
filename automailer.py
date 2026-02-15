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
EMAIL_CC = os.getenv('EMAIL_CC', 'nmilano@privodeveloper.com')

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
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, 'rb') as f:
                    attach = MIMEApplication(f.read(), _subtype="pdf")
                    attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                    msg.attach(attach)
            except Exception as e:
                print(f"  [!] Error adjuntando {attachment_path}: {e}")
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
        
        # ! IMPORTANTE: Usar la pestaña "Review fechas compraventa"
        try:
            worksheet = sheet.worksheet('Review fechas compraventa')
        except:
            print("[!] No se encontró la pestaña 'Review fechas compraventa', intentando índice 1")
            worksheet = sheet.get_worksheet(1)
        
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

    # 2. Convertir Encabezados de Fecha (Strings -> Datetime objects)
    new_columns = {}
    for col in df.columns:
        # Intentar convertir si parece fecha (simple check)
        try:
             # Si el header tiene numeros y / o -
             if isinstance(col, str) and any(c.isdigit() for c in col):
                 # Intentar parsear
                 dt = pd.to_datetime(col, dayfirst=True, errors='coerce')
                 if pd.notna(dt):
                     new_columns[col] = dt
        except:
             pass
    
    if new_columns:
        df = df.rename(columns=new_columns)
        print(f"Encabezados de fecha detectados: {len(new_columns)}")

    # 3. Validar y Limpiar
    
    # Verificar columnas requeridas
    # Mapeo similar al anterior
    col_nombre = 'Comprador'
    col_fecha = 'Fecha última cuota\nantes de la entrega' # Header original puede ser sucio
    col_email = 'Email'
    col_idioma = 'Idioma'
    
    # Limpiar nombres de columnas (quitar saltos de linea)
    clean_cols = {c: str(c).replace('\n', ' ') for c in df.columns}
    df = df.rename(columns=clean_cols)
    
    # Re-definir nombres esperados tras limpieza
    col_email = 'Email'
    col_idioma = 'Idioma'
    col_nombre = 'Comprador'
    # Buscar columna que contenga "antes de la entrega" si no es exacta
    col_fecha_clean = next((c for c in df.columns if 'antes de la entrega' in str(c)), None)

    if not col_fecha_clean:
         # Fallback a buscar 'Fecha' simplemente?
         print("[!] No se encontró columna de fecha de entrega.")
         print(f"Columnas: {df.columns.tolist()}")
         return

    # FILTRO: Eliminar filas donde Comprador o Villa estén vacíos 
    if 'Villa' in df.columns:
        df = df[df['Villa'] != '']
    if col_nombre in df.columns:
         df = df[df[col_nombre] != '']

    print(f"Filas tras limpieza: {len(df)}")
    
    # Normalizar columna de fecha de entrega (si la usamos para algo)
    # Aunque la lógica principal itera sobre columnas que SON fechas (cuotas)
    
    fecha_hoy = pd.Timestamp.now().normalize()
    print(f"Fecha de hoy: {fecha_hoy.strftime('%d/%m/%Y')}")

    correos_enviados_count = 0

    # Crear columnas faltantes en memoria si no existen (Email e Idioma deberían estar en Excel ahora)
    if col_email not in df.columns:
        df[col_email] = '' 
    if col_idioma not in df.columns:
        df[col_idioma] = 'Español' # Default
    if 'Ultimo_Aviso' not in df.columns:
        df['Ultimo_Aviso'] = ''

    count_processed = 0
    for index, row in df.iterrows():
        # if count_processed >= 5:
        #     print("--- DEBUG: Deteniendo tras 5 filas ---")
        #     break
        count_processed += 1

        nombre = row[col_nombre]
        email = row.get(col_email, '')
        idioma_raw = str(row.get(col_idioma, 'Español')).lower()
        
        # Detectar idioma
        lang_code = 'es' # Default
        if 'ingl' in idioma_raw or 'english' in idioma_raw:
            lang_code = 'en'
        
        # Si no hay email, loguear para el usuario
        if (not email or pd.isna(email)) and not DRY_RUN:
             # Si no es dry run, saltamos. Si es dry run, quizás simulemos si queremos probar fechas.
             continue
        
        # Si en DRY RUN no hay email, usamos dummy para probar
        if (not email or pd.isna(email)) and DRY_RUN:
             email = "cliente_sin_email@demo.com"

        # Filtro de Estado: El excel tiene 'Status', usaremos eso si existe
        estado = 'Pendiente' # Default
        if 'Status' in df.columns:
             estado_val = str(row['Status'])
             # Ajustar lógica según lo que haya en 'Status' del excel real
             # Por ahora asumimos todo pendiente si no dice 'Pagado'
             if 'Pagado' in estado_val: 
                 estado = 'Pagado'

        # Parsear fecha usando helper
        fecha_orig = row[col_fecha_clean]
        fecha_venc = parse_spanish_date(str(fecha_orig))
        
        if pd.isna(fecha_venc):
            # print(f"  [i] Fecha inválida para {nombre}: {fecha_orig}")
            continue
        
        # Buscar columna de Monto
        col_monto = next((c for c in df.columns if str(c).lower() in ['monto', 'amount', 'importe', 'valor', 'cuota', 'precio']), None)
        
        monto = 0.0
        if col_monto:
            val_monto = str(row[col_monto]).strip()
            # Limpiar formato (asumiendo 1.500,00 o 1500.00 o $1,500.00)
            # Eliminar simbolos de moneda
            val_monto = val_monto.replace('$', '').replace('US', '').strip()
            
            # Intentar convertir
            try:
                # Si tiene punto y coma, determinar cual es decimal
                # Caso español: 1.234,56 -> Quitar punto, cambiar coma por punto
                if ',' in val_monto and '.' in val_monto:
                    if val_monto.rfind(',') > val_monto.rfind('.'): # 1.234,56
                         val_monto = val_monto.replace('.', '').replace(',', '.')
                    else: # 1,234.56
                         val_monto = val_monto.replace(',', '')
                elif ',' in val_monto: # 124,56 o 1,234 (Ambiguo, pero asumimos decimal si es español)
                     # Si es '1,234' podría ser mil. Si es '123,45' es decimal.
                     # ASUMIMOS formato europeo para este proyecto (basado en templates)
                     val_monto = val_monto.replace('.', '').replace(',', '.')
                
                monto = float(val_monto)
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
        if dias_restantes == 7:
            tipo_aviso = 'V-7'
        elif dias_restantes == 2:
            tipo_aviso = 'V-2'
        elif dias_restantes == -3:
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
