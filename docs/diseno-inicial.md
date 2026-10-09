# Diseño inicial del prototipo ReparaCampus

**Fecha:** 08/10/2026  
**Estado:** Diseño previo a la implementación de S01.  
**Base:** SPECS S01–S05 revisadas en el PR #6.

## Idea general
Para el examen vamos a usar una aplicación web sencilla con Flask. La intención es separar la interfaz, las reglas y la base de datos para que sea más fácil probar cada parte.

## Componentes
1. **Interfaz web:** plantillas HTML de Flask y CSS. Muestra formularios y datos según el rol.
2. **Rutas Flask:** reciben las acciones del usuario, verifican sesión y rol y llaman las reglas del sistema.
3. **Lógica de dominio:** valida datos, estados y reglas antes de guardar.
4. **Persistencia SQLite:** guarda usuarios, incidencias, soluciones e historial.
5. **Pruebas pytest:** validan reglas aisladas y recorridos contra una base SQLite de prueba.

## Datos principales
- **users:** cuentas ficticias, contraseña con hash, rol y estado activo.
- **incidents:** reporte, solicitante, ubicación, categoría, impacto, riesgo, prioridad, estado y técnico.
- **solutions:** soluciones que se agreguen durante la atención.
- **events:** historial de creación y transiciones. No se usa como tabla editable por la aplicación.

## Estados previstos
`REGISTRADA → ASIGNADA → EN_ATENCION → PENDIENTE_VALIDACION → CERRADA`

Transiciones adicionales permitidas por el enunciado:
- `PENDIENTE_VALIDACION → EN_ATENCION` por rechazo del solicitante.
- `CERRADA → EN_ATENCION` por reapertura válida dentro de 48 h.

No se agregarán otras transiciones.

## Decisiones iniciales
- La identidad y el rol salen de la sesión del servidor.
- Las fechas efectivas se generan en UTC en el servidor.
- Incidencia e historial se guardan dentro de la misma transacción.
- Las plantillas de Jinja mantienen el escape automático; no se marcará texto del usuario como seguro.
- Las contraseñas ficticias se almacenan con hash de Werkzeug.
- Para S01 el código de incidencia se genera en servidor con prefijo `INC-`. El formato exacto sigue documentado como supuesto de diseño mientras no exista una respuesta del cliente.

## Primera funcionalidad
S01 se implementará primero porque es la entrada del flujo. Después de sus pruebas y revisión se integrará antes de avanzar a S02.
