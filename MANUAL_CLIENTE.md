# Manual del Sistema de Cobranza Automatizado
**Proyecto:** Automatización de Envíos de Recordatorios de Pago (EOS VISTACANA)
**Fecha:** 15 de Febrero de 2026

---

## 🚀 Resumen del Proyecto

Se ha implementado con éxito la migración del sistema de recordatorios de pago a la nube, logrando una **automatización 100% desatendida y sin costos de mantenimiento de servidor**.

### ✅ Mejoras Implementadas:

1.  **Automatización Total**: Ya no requerimos que una persona ejecute el script manualmente en su computadora. El sistema "vive" en la nube y trabaja por sí solo.
2.  **Costo Cero ($0)**: Hemos utilizado **GitHub Actions**, una infraestructura profesional que permite ejecutar el código diariamente de forma gratuita, eliminando la necesidad de pagar servidores mensuales (como Render, que costaría aprox. $7-$15/mes).
3.  **Seguridad Bancaria**: Las contraseñas de correo y acceso a datos Google no están visibles en el código. Se utilizan "Secretos Encriptados" que cumplen con estándares de seguridad modernos.
4.  **Integración con Google Sheets**: El sistema lee directamente de su hoja de cálculo "en vivo". No hace falta descargar ni subir archivos Excel.

---

## ⚙️ ¿Cómo Funciona?

El sistema sigue este ciclo diario automáticamente:

1.  **9:00 AM**: El robot se despierta en la nube.
2.  **Conexión Segura**: Se conecta a su Google Sheet "Review fechas compraventa".
3.  **Análisis Inteligente**: Revisa cada cliente y calcula los días restantes para su cuota.
4.  **Toma de Decisiones**:
    *   ¿Faltan 7 días? -> Envía recordatorio preventivo.
    *   ¿Faltan 2 días? -> Envía aviso de proximidad.
    *   ¿Pasó la fecha? -> Envía reclamos (a los 3, 7 y 15 días de atraso).
5.  **Reporte**: Todo queda registrado en el historial del sistema.

---

## 📋 Instrucciones para el Administración (Usted)

Para que el sistema funcione, su única responsabilidad es **mantener la información al día en Google Sheets**:

### 1. La Hoja de Cálculo
*   Trabaje en la pestaña: **`Review fechas compraventa`**.
*   **Columna "Monto"**: Asegúrese de ingresar el valor de la cuota (ej: `1500` o `1500.00`) en la columna correspondiente.
*   **Columna "Email"**: Verifique que los correos de los clientes estén correctos.
*   **Columna "Fecha..."**: Mantenga las fechas de cuota actualizadas.

### 2. Monitoreo (Opcional)
El sistema enviará una copia oculta (BCC) de todos los correos a `nmilano@privodeveloper.com`. Si usted recibe esos correos, significa que el sistema está funcionando perfectamente.

---

## 🛡️ Soporte Técnico

Si necesita cambiar la contraseña del correo o ajustar los textos de las plantillas, contacte a su desarrollador. El sistema está diseñado para ser modular y fácil de actualizar.

---
*Sistema desarrollado para optimizar la gestión de cobranzas de EOS VISTACANA.*
