# S05 — Consultar e historizar incidencias

**Versión:** 0.1  
**Fecha:** 08/10/2026  
**Autor documental:** Equipo ReparaCampus  
**Revisor:** Pendiente de revisión por otro integrante antes de implementar  
**Requisito asociado:** RF05

## Historia
Como **usuario autorizado**, quiero consultar incidencias e historial según mis permisos para conocer su estado y mantener trazabilidad verificable.

## Alcance y exclusiones
Incluye listados, filtros, historial inmutable y tablero del coordinador. No incluye edición o eliminación del reporte ni notificaciones.

## Entradas
- filtros opcionales por estado y prioridad;
- identidad y rol obtenidos de la sesión;
- incidencia seleccionada para consultar historial.

## Precondiciones y permisos
- Usuario autenticado.
- Solicitante: solo consulta sus propias incidencias e historial.
- Técnico: consulta las incidencias que le hayan sido asignadas.
- Coordinador: consulta todas las incidencias y el tablero.
- Los permisos se validan en servidor; ocultar botones no constituye autorización.

## Reglas y proceso
1. Listar incidencias aplicando permisos y filtros.
2. Cada creación y transición exitosa conserva autor, fecha UTC, estado anterior/nuevo y acción.
3. El historial no se edita ni se borra.
4. El historial incluye soluciones, motivos, cierres y reaperturas.
5. El tablero del coordinador muestra cantidades por estado y prioridad.
6. Las incidencias `CRITICA` no cerradas se contabilizan aparte.
7. Porcentaje de cierre = `CERRADAS / total × 100`, con un decimal.
8. Con cero registros, porcentaje de cierre = `0,0 %`.
9. Los textos almacenados se muestran escapados y no se ejecutan como HTML/scripts.

## Salidas y cambios persistidos
Las consultas no modifican datos. Devuelven listados autorizados, historial y métricas calculadas desde la información persistida.

## Errores y efectos que deben evitarse
- exponer incidencias de otros solicitantes;
- exponer incidencias no asignadas a un técnico;
- permitir edición o eliminación del historial;
- calcular porcentaje con división por cero;
- ejecutar texto almacenado como HTML/script;
- alterar estado o historial por una consulta fallida.

## Criterios de aceptación
- **AC-S05-01:** Dado un solicitante autenticado, cuando lista incidencias, entonces solo ve las incidencias de su propiedad.
- **AC-S05-02:** Dado un técnico autenticado, cuando lista incidencias, entonces solo ve las que están o estuvieron asignadas a ese técnico según el alcance autorizado.
- **AC-S05-03:** Dado un coordinador, cuando lista incidencias con filtros por estado y/o prioridad, entonces obtiene únicamente las que cumplen los filtros.
- **AC-S05-04:** Dada una incidencia con varias transiciones, cuando un usuario autorizado consulta el historial, entonces aparecen en orden creación, estados, acciones, autores y fechas, incluyendo soluciones, rechazos, cierres y reaperturas.
- **AC-S05-05:** Dado un intento de editar o eliminar un evento de historial mediante la interfaz o endpoint, cuando se procesa, entonces la operación no está disponible o es rechazada.
- **AC-S05-06:** Dado un conjunto de incidencias, cuando el coordinador consulta el tablero, entonces se muestran cantidades correctas por estado y prioridad y el total de `CRITICA` no cerradas.
- **AC-S05-07:** Dado un total mayor que cero, cuando se calcula el porcentaje de cierre, entonces se obtiene `CERRADAS / total × 100` con un decimal.
- **AC-S05-08:** Dado que no existen incidencias, cuando se consulta el tablero, entonces el porcentaje de cierre mostrado es `0,0 %`.
- **AC-S05-09:** Dado texto persistido similar a HTML o script, cuando se visualiza en listado o historial, entonces se presenta como texto y no se ejecuta.
- **AC-S05-10:** Dado un usuario no autorizado para una incidencia, cuando intenta acceder directamente a su URL o endpoint, entonces el servidor rechaza la consulta.

## Diseño y tareas vinculadas
- T-S05-01: consultas por rol y propiedad/asignación.
- T-S05-02: filtros de estado y prioridad.
- T-S05-03: vista de historial inmutable.
- T-S05-04: consultas agregadas del tablero.
- T-S05-05: cálculo de porcentaje con caso cero.
- T-S05-06: pruebas de autorización, filtros, historial, métricas y XSS almacenado.

## Pruebas y resultados esperados
Cubrir permisos por rol, filtros, acceso directo no autorizado, historial completo, no edición/borrado, conteos, porcentaje normal y caso cero.

## Decisión de revisión
**Pendiente. No implementar S05 hasta registrar una revisión humana aprobada de esta versión.**
