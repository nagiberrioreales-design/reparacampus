# Preguntas al cliente y supuestos pendientes

**Fecha:** 08/10/2026  
**Estado:** Pendiente de respuesta del cliente/docente.  
**Regla:** Una respuesta de IA no sustituye una decisión del cliente.

## Preguntas
1. **Formato del código de incidencia:** ¿se espera un formato específico para el código generado (por ejemplo, `INC-0001`) o basta con que sea único y legible?
2. **Técnico que se inactiva después de ser asignado:** si un técnico estaba activo al momento de la asignación y luego pasa a inactivo, ¿puede terminar las incidencias ya asignadas o debe bloquearse su actuación?
3. **Combinación de filtros:** en la consulta del coordinador, ¿los filtros por estado y prioridad deben poder aplicarse simultáneamente o basta con aplicar uno por vez?

## Supuestos pendientes si no se recibe respuesta antes de implementar
Estos supuestos **no se consideran decisiones del cliente** y deberán identificarse como tales en el PDF final si se usan:

- Para el código de incidencia, usar un identificador único generado por el servidor con formato legible.
- Un técnico debe estar activo para nuevas asignaciones; el comportamiento frente a desactivación posterior queda pendiente hasta decisión.
- La interfaz podrá combinar estado y prioridad, porque no contradice RF05, pero se marcará como decisión de diseño del equipo y no como requisito explícito.

## Preguntas ya resueltas por el enunciado
No se consideran dudas:
- el rechazo conserva el mismo técnico y la solución anterior;
- la reapertura es válida hasta **48 horas inclusive**;
- el tiempo se calcula en servidor con fechas UTC;
- no existe cierre automático;
- no se permite reasignar una incidencia ya `ASIGNADA`;
- el coordinador no confirma ni reabre en nombre del solicitante.
