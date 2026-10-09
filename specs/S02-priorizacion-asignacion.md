# S02 — Priorizar y asignar incidencia

**Versión:** 0.1  
**Fecha:** 08/10/2026  
**Autor documental:** Equipo ReparaCampus  
**Revisor:** Steven Reyes  
**Fecha de revisión:** 08/10/2026  
**Requisito asociado:** RF02

## Historia
Como **coordinador**, quiero que el sistema calcule la prioridad y me permita asignar una incidencia a un técnico activo para organizar la atención según su urgencia.

## Alcance y exclusiones
Incluye cálculo de prioridad y asignación inicial de una incidencia `REGISTRADA`. No incluye reasignación, inicio de atención ni cierre.

## Entradas
- incidencia existente en estado `REGISTRADA`;
- técnico seleccionado por el coordinador;
- datos ya persistidos de `impacto` y `riesgo_para_personas`.

## Precondiciones y permisos
- Usuario autenticado con rol `COORDINADOR`.
- El técnico seleccionado debe existir y estar activo.
- La incidencia no puede estar previamente asignada.

## Reglas y proceso
1. La prioridad se calcula en servidor:
   - riesgo para personas = true → `CRITICA`;
   - riesgo = false e impacto = `ALTO` → `ALTA`;
   - riesgo = false e impacto = `BAJO` → `NORMAL`.
2. Solo el coordinador puede asignar.
3. Solo una incidencia `REGISTRADA` puede pasar a `ASIGNADA`.
4. La asignación registra técnico, prioridad calculada, autor de la acción, fecha UTC y transición.
5. No se permite reasignar una incidencia que ya está `ASIGNADA`.
6. Una operación inválida no modifica incidencia ni historial.

## Salidas y cambios persistidos
- prioridad calculada;
- técnico asignado;
- estado `ASIGNADA`;
- evento inmutable de asignación con actor, fecha, estado anterior y nuevo.

## Errores y efectos que deben evitarse
- permitir que el navegador envíe una prioridad arbitraria;
- asignar a técnico inactivo;
- asignar una incidencia en estado incompatible;
- reasignar una incidencia ya asignada;
- dejar cambios parciales si falla el historial.

## Criterios de aceptación
- **AC-S02-01:** Dada una incidencia con riesgo para personas, cuando el coordinador la procesa, entonces la prioridad calculada es `CRITICA`.
- **AC-S02-02:** Dada una incidencia sin riesgo e impacto `ALTO`, cuando se calcula su prioridad, entonces el resultado es `ALTA`.
- **AC-S02-03:** Dada una incidencia sin riesgo e impacto `BAJO`, cuando se calcula su prioridad, entonces el resultado es `NORMAL`.
- **AC-S02-04:** Dada una incidencia `REGISTRADA` y un técnico activo, cuando el coordinador confirma la asignación, entonces queda `ASIGNADA` al técnico y se registra el evento.
- **AC-S02-05:** Dado un usuario distinto de coordinador, cuando intenta asignar, entonces el servidor rechaza la operación sin cambios.
- **AC-S02-06:** Dado un técnico inactivo, cuando el coordinador intenta asignarle una incidencia, entonces se rechaza sin cambiar estado ni historial.
- **AC-S02-07:** Dada una incidencia ya `ASIGNADA`, cuando se intenta volver a asignar, entonces se rechaza y conserva técnico, estado e historial previos.
- **AC-S02-08:** Dada una prioridad manipulada desde el cliente, cuando se procesa la asignación, entonces el servidor ignora ese valor y recalcula según riesgo e impacto.

## Diseño y tareas vinculadas
- T-S02-01: función de cálculo de prioridad.
- T-S02-02: consulta de técnicos activos.
- T-S02-03: autorización exclusiva de coordinador.
- T-S02-04: transición transaccional `REGISTRADA → ASIGNADA`.
- T-S02-05: pruebas de prioridad, permisos, técnico inactivo y reasignación.

## Pruebas y resultados esperados
Cubrir las tres prioridades, asignación válida, rol incorrecto, técnico inactivo, estado incompatible y reasignación rechazada.

## Decisión de revisión
**Aprobada en el PR #6 antes de iniciar la implementación. La versión 0.1 se conserva como línea base de la SPEC.**
