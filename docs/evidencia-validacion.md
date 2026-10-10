# Evidencia resumida de validación

**Fecha de ejecución:** 09/10/2026  
**Comando:** `pytest -q`  
**GitHub Actions:** run 37889058972  
**SHA probado:** `1ee06039666905a24dc02c2c43028c7e071339f6`  
**Resultado global:** **56 passed, 0 failed**

Esta tabla reúne escenarios representativos. La suite completa contiene más casos y se relaciona con todos los criterios en `docs/matriz-spec-codigo.md`.

| ID | SPEC / AC | Entrada o situación | Esperado definido antes de ejecutar | Observado | Resultado |
|---|---|---|---|---|---|
| V-01 | S01 / AC-S01-02 | descripción con 19 caracteres después de trim | rechazar; no crear incidencia | la validación devuelve error | Cumple |
| V-02 | S01 / límite superior | descripción con exactamente 500 caracteres | aceptar | validación sin error | Cumple |
| V-03 | S01 / persistencia | registrar incidencia y crear una nueva instancia Flask con el mismo archivo SQLite | incidencia e historial siguen guardados | 1 incidencia y 1 evento después del reinicio | Cumple |
| V-04 | S02 / AC-S02-08 | cliente intenta enviar prioridad NORMAL para incidencia que por regla es ALTA | ignorar valor del cliente y calcular ALTA | prioridad persistida ALTA | Cumple |
| V-05 | S02 / AC-S02-07 | intentar asignar por segunda vez una incidencia ASIGNADA | rechazar y conservar técnico original | mismo técnico y un solo evento ASIGNADA | Cumple |
| V-06 | S03 / AC-S03-07 | intentar registrar solución antes de iniciar atención | rechazar; conservar ASIGNADA; 0 soluciones | estado ASIGNADA y 0 soluciones | Cumple |
| V-07 | S03 / AC-S03-04/06 | solución de 800 y 801 caracteres | 800 acepta; 801 rechaza | resultados coinciden | Cumple |
| V-08 | S04 / AC-S04-05 | reapertura exactamente 48 h después del cierre | aceptar y volver a EN_ATENCION | reapertura aceptada y mismo técnico | Cumple |
| V-09 | S04 / AC-S04-06 | reapertura 48 h + 1 s después del cierre | rechazar sin cambios | permanece CERRADA y no crea REABIERTA | Cumple |
| V-10 | S05 / AC-S05-10 | solicitante intenta abrir historial de incidencia ajena | responder 403 | respuesta 403 | Cumple |
| V-11 | S05 / AC-S05-07 | 1 incidencia cerrada de 4 | mostrar 25,0 % | tablero muestra 25,0 % | Cumple |
| V-12 | S04+S05 | reabrir la única incidencia cerrada | porcentaje baja de 100,0 % a 0,0 % y se conserva el cierre anterior | tablero baja a 0,0 %; historial conserva 1 cierre y agrega 1 reapertura | Cumple |

## Tres recorridos de integración

| ID | Recorrido | Resultado observado |
|---|---|---|
| INT-01 | registrar → asignar → iniciar → proponer → confirmar | termina CERRADA con eventos en el orden esperado |
| INT-02 | registrar → asignar → iniciar → proponer → rechazar → nueva solución → confirmar | termina CERRADA, conserva dos soluciones y un rechazo |
| INT-03 | registrar → asignar → iniciar → proponer → cerrar → reabrir → nueva solución → cerrar | termina CERRADA, conserva dos cierres, una reapertura y dos soluciones |

## Regresión

El mismo comando volvió a ejecutar las pruebas de S01–S05. El run citado terminó en verde con 56 pruebas. Las actualizaciones posteriores en la rama fueron únicamente documentales; antes del merge final se volverá a comprobar el CI y se registrará el SHA definitivo.
