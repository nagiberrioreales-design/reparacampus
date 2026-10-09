# S03 — Atender incidencia y registrar solución

**Versión:** 0.1  
**Fecha:** 08/10/2026  
**Autor documental:** Equipo ReparaCampus  
**Revisor:** Steven Reyes  
**Fecha de revisión:** 08/10/2026  
**Requisito asociado:** RF03

## Historia
Como **técnico asignado**, quiero iniciar la atención de una incidencia y registrar una solución para dejar evidencia del trabajo realizado.

## Alcance y exclusiones
Incluye el inicio de atención y el registro de una solución por el técnico asignado. No incluye validación por el solicitante, rechazo, cierre ni reapertura.

## Entradas
- incidencia existente;
- acción de iniciar atención;
- solución obligatoria de 20 a 800 caracteres después de retirar espacios externos.

## Precondiciones y permisos
- Usuario autenticado con rol `TECNICO`.
- El técnico autenticado debe ser exactamente el técnico asignado a la incidencia.
- Para iniciar atención, la incidencia debe estar `ASIGNADA`.
- Para registrar solución, la incidencia debe estar `EN_ATENCION`.

## Reglas y proceso
1. Solo el técnico asignado puede ejecutar `ASIGNADA → EN_ATENCION`.
2. Desde `EN_ATENCION`, el mismo técnico registra una solución válida.
3. Una solución válida cambia el estado a `PENDIENTE_VALIDACION`.
4. Cada transición registra actor, fecha UTC, estado anterior, estado nuevo y acción.
5. La solución se conserva en el historial.
6. Una operación rechazada no modifica estado, solución ni historial.

## Salidas y cambios persistidos
- inicio de atención con estado `EN_ATENCION`;
- solución registrada;
- transición a `PENDIENTE_VALIDACION`;
- eventos inmutables de inicio y propuesta de solución.

## Errores y efectos que deben evitarse
- permitir que otro técnico atienda la incidencia;
- registrar solución antes de iniciar;
- aceptar solución menor de 20 o mayor de 800 caracteres;
- cambiar estado si falla el guardado de solución o historial;
- ejecutar texto almacenado como HTML o script.

## Criterios de aceptación
- **AC-S03-01:** Dada una incidencia `ASIGNADA` al técnico autenticado, cuando inicia la atención, entonces pasa a `EN_ATENCION` y se registra el evento.
- **AC-S03-02:** Dada una incidencia asignada a otro técnico, cuando un técnico diferente intenta iniciarla, entonces se rechaza sin cambios.
- **AC-S03-03:** Dada una incidencia en estado distinto de `ASIGNADA`, cuando se intenta iniciar atención, entonces se rechaza sin cambios.
- **AC-S03-04:** Dada una incidencia `EN_ATENCION` del técnico autenticado y una solución de 20–800 caracteres, cuando la registra, entonces se conserva la solución y pasa a `PENDIENTE_VALIDACION`.
- **AC-S03-05:** Dada una solución de 19 caracteres después de trim, cuando se intenta registrar, entonces se rechaza y la incidencia permanece `EN_ATENCION`.
- **AC-S03-06:** Dada una solución de 801 caracteres después de trim, cuando se intenta registrar, entonces se rechaza y no se crea evento.
- **AC-S03-07:** Dada una incidencia que no está `EN_ATENCION`, cuando se intenta registrar solución, entonces se rechaza sin efectos.
- **AC-S03-08:** Dado texto parecido a HTML o script en la solución, cuando se consulta, entonces se presenta como texto y no se ejecuta.

## Diseño y tareas vinculadas
- T-S03-01: autorización por técnico asignado.
- T-S03-02: transición `ASIGNADA → EN_ATENCION`.
- T-S03-03: validación y persistencia de solución.
- T-S03-04: transición `EN_ATENCION → PENDIENTE_VALIDACION`.
- T-S03-05: pruebas de permisos, estados y límites de solución.

## Pruebas y resultados esperados
Cubrir técnico correcto/incorrecto, estados incompatibles, solución válida, límites 19/20/800/801 y persistencia de historial.

## Decisión de revisión
**Pendiente. No implementar S03 hasta registrar una revisión humana aprobada de esta versión.**
