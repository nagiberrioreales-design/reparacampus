# S04 — Validar, rechazar y reabrir una incidencia

**Versión:** 0.1  
**Fecha:** 08/10/2026  
**Autor documental:** Equipo ReparaCampus  
**Revisor:** Pendiente de revisión por otro integrante antes de implementar  
**Requisito asociado:** RF04

## Historia
Como **solicitante propietario**, quiero confirmar, rechazar o reabrir la solución de mi incidencia para asegurar que el problema realmente quedó resuelto.

## Alcance y exclusiones
Incluye confirmación de solución, rechazo con motivo y reapertura dentro del plazo permitido. No incluye cierre automático, reasignación ni modificación del reporte original.

## Entradas
- incidencia propia;
- acción `confirmar`, `rechazar` o `reabrir`;
- motivo obligatorio de rechazo/reapertura de 10 a 300 caracteres después de retirar espacios externos;
- tiempo de servidor en UTC para verificar reapertura.

## Precondiciones y permisos
- Usuario autenticado con rol `SOLICITANTE`.
- El solicitante autenticado debe ser el propietario de la incidencia.
- Confirmar o rechazar requiere estado `PENDIENTE_VALIDACION`.
- Reabrir requiere estado `CERRADA`.
- El coordinador no puede confirmar ni reabrir en nombre del solicitante.

## Reglas y proceso
1. Confirmación válida: `PENDIENTE_VALIDACION → CERRADA`.
2. Rechazo válido: `PENDIENTE_VALIDACION → EN_ATENCION`.
3. Al rechazar se conserva el mismo técnico asignado y la solución anterior.
4. Cada rechazo guarda motivo, autor y fecha UTC.
5. Una incidencia `CERRADA` puede reabrirse por su propietario si el tiempo transcurrido desde el último cierre es **menor o igual a 48 horas**, calculado en servidor con UTC.
6. Reapertura válida: `CERRADA → EN_ATENCION`, conservando el mismo técnico.
7. Se conservan todos los cierres, soluciones, rechazos y reaperturas previos.
8. Una operación inválida o fuera de plazo no produce cambios parciales.

## Salidas y cambios persistidos
- cierre confirmado;
- rechazo y retorno a atención;
- reapertura dentro del plazo;
- eventos inmutables con actor, fecha, transición y motivo cuando aplica.

## Errores y efectos que deben evitarse
- permitir que otro solicitante valide una incidencia ajena;
- permitir que el coordinador confirme o reabra;
- aceptar motivos fuera de 10–300 caracteres;
- reabrir después de 48 horas;
- borrar soluciones, cierres o motivos anteriores;
- cambiar técnico durante rechazo o reapertura;
- alterar el historial si la operación falla.

## Criterios de aceptación
- **AC-S04-01:** Dada una incidencia propia `PENDIENTE_VALIDACION`, cuando el solicitante confirma la solución, entonces pasa a `CERRADA` y se registra el cierre.
- **AC-S04-02:** Dada una incidencia ajena `PENDIENTE_VALIDACION`, cuando otro solicitante intenta confirmarla, entonces se rechaza sin cambios.
- **AC-S04-03:** Dada una incidencia propia `PENDIENTE_VALIDACION` y un motivo válido de 10–300 caracteres, cuando el solicitante rechaza la solución, entonces vuelve a `EN_ATENCION`, conserva técnico y solución anterior y registra el motivo.
- **AC-S04-04:** Dado un motivo de rechazo de 9 o 301 caracteres después de trim, cuando se intenta rechazar, entonces se rechaza la operación y no cambia estado ni historial.
- **AC-S04-05:** Dada una incidencia cerrada exactamente 48 horas antes según reloj controlado del servidor, cuando su propietario la reabre con motivo válido, entonces pasa a `EN_ATENCION` con el mismo técnico.
- **AC-S04-06:** Dada una incidencia cerrada hace más de 48 horas, cuando su propietario intenta reabrirla, entonces se rechaza sin cambios.
- **AC-S04-07:** Dado un coordinador, cuando intenta confirmar o reabrir una incidencia por el solicitante, entonces el servidor rechaza la operación.
- **AC-S04-08:** Dada una secuencia de solución, cierre, reapertura y nueva solución, cuando se consulta el historial, entonces se conservan todos los cierres y soluciones anteriores en orden.
- **AC-S04-09:** Dada cualquier operación inválida de confirmación, rechazo o reapertura, cuando falla una regla, entonces no se persiste ningún efecto parcial.

## Diseño y tareas vinculadas
- T-S04-01: autorización por propiedad de incidencia.
- T-S04-02: transición `PENDIENTE_VALIDACION → CERRADA`.
- T-S04-03: rechazo con motivo y retorno a `EN_ATENCION`.
- T-S04-04: servicio de reapertura con reloj inyectable/controlado.
- T-S04-05: historial inmutable de soluciones, cierres, rechazos y reaperturas.
- T-S04-06: pruebas de propiedad, motivos y límites exactos de 48 h.

## Pruebas y resultados esperados
Cubrir confirmación válida, propietario ajeno, rechazo válido/inválido, exactamente 48 h, >48 h, coordinador no autorizado y conservación de historial.

## Decisión de revisión
**Pendiente. No implementar S04 hasta registrar una revisión humana aprobada de esta versión.**
