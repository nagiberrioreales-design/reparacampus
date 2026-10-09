# Matriz SPEC versus código y pruebas

**Versión de SPECS evaluada:** 0.1  
**Revisión previa:** PR #6 aprobado por Steven Reyes antes de implementar.  
**Estado de esta matriz:** preparada para el CI final del examen. La columna de estado se actualizará con el resultado final del pipeline.

La lectura de cada fila es: requisito → criterio → comportamiento esperado → archivo que lo implementa → prueba que lo comprueba.

## S01 / RF01 — Registrar

| Criterio | Comportamiento esperado | Código | Prueba / datos | Efecto esperado en SQLite | Estado |
|---|---|---|---|---|---|
| AC-S01-01 | Datos válidos crean incidencia con código, autor de sesión, UTC y REGISTRADA | `app/incidents.py` | `test_s01_registration_persists_incident_and_history` | 1 incidencia + 1 evento CREADA | Pendiente CI final |
| AC-S01-02 | Descripción de 19 caracteres se rechaza | `app/domain.py` | `test_s01_rejects_description_outside_limits[19]` | sin alta | Pendiente CI final |
| AC-S01-03 | Descripción de 20 caracteres se acepta | `app/domain.py` | `test_s01_accepts_valid_data` | validación sin error | Pendiente CI final |
| AC-S01-04 | Más de 500 caracteres se rechaza | `app/domain.py` | `test_s01_rejects_description_outside_limits[501]` | sin alta | Pendiente CI final |
| AC-S01-05 | Ubicación/categoría/impacto fuera del catálogo se rechaza | `app/domain.py` | `test_s01_rejects_invalid_catalog_or_boolean` | sin alta | Pendiente CI final |
| AC-S01-06 | Usuario no solicitante no registra | `app/auth.py`, `app/incidents.py` | `test_s01_non_requester_cannot_register_and_database_stays_unchanged` | 0 incidencias y 0 eventos | Pendiente CI final |
| AC-S01-07 | Autor enviado por cliente no reemplaza usuario de sesión | `app/incidents.py` | `test_s01_ignores_forged_author_and_escapes_stored_text` | requester_id = usuario autenticado | Pendiente CI final |
| AC-S01-08 | Texto parecido a HTML/script no se ejecuta | Jinja + `app/templates/incidents/index.html` | misma prueba anterior | texto persiste, salida escapada | Pendiente CI final |

## S02 / RF02 — Priorizar y asignar

| Criterio | Comportamiento esperado | Código | Prueba / datos | Efecto esperado en SQLite | Estado |
|---|---|---|---|---|---|
| AC-S02-01 | Riesgo=true produce CRITICA | `calculate_priority` | `test_s02_calculates_priority_on_server` | prioridad CRITICA | Pendiente CI final |
| AC-S02-02 | Sin riesgo + ALTO produce ALTA | `calculate_priority` | misma prueba parametrizada | prioridad ALTA | Pendiente CI final |
| AC-S02-03 | Sin riesgo + BAJO produce NORMAL | `calculate_priority` | misma prueba parametrizada | prioridad NORMAL | Pendiente CI final |
| AC-S02-04 | Coordinador asigna REGISTRADA a técnico activo | `assign` | `test_s02_coordinator_assigns_active_technician_and_history` | estado ASIGNADA + evento | Pendiente CI final |
| AC-S02-05 | Actor distinto de coordinador no asigna | autorización Flask | `test_s02_non_coordinator_cannot_assign` | incidencia sigue REGISTRADA | Pendiente CI final |
| AC-S02-06 | Técnico inactivo se rechaza | consulta de técnico activo | `test_s02_inactive_technician_is_rejected_without_history_change` | no cambia estado ni historial | Pendiente CI final |
| AC-S02-07 | Incidencia ya asignada no se reasigna | condición de estado/asignación | `test_s02_second_assignment_is_rejected_and_keeps_original_technician` | conserva técnico original; 1 evento ASIGNADA | Pendiente CI final |
| AC-S02-08 | Prioridad manipulada por cliente se ignora | cálculo en servidor | `test_s02_coordinator_assigns_active_technician_and_history` envía NORMAL y espera ALTA | prioridad calculada ALTA | Pendiente CI final |

## S03 / RF03 — Atender y registrar solución

| Criterio | Comportamiento esperado | Código | Prueba / datos | Efecto esperado en SQLite | Estado |
|---|---|---|---|---|---|
| AC-S03-01 | Técnico asignado inicia ASIGNADA → EN_ATENCION | `start_attention` | `test_s03_assigned_technician_starts_attention` | estado EN_ATENCION + evento | Pendiente CI final |
| AC-S03-02 | Otro técnico recibe 403 | autorización por assigned_technician_id | `test_s03_other_technician_cannot_start_attention` | conserva ASIGNADA | Pendiente CI final |
| AC-S03-03 | Estado incompatible no permite iniciar | condición `state == ASIGNADA` | `test_s03_cannot_start_attention_from_incompatible_state` | sin evento nuevo | Pendiente CI final |
| AC-S03-04 | Solución 20–800 desde EN_ATENCION pasa a PENDIENTE_VALIDACION | `propose_solution` | `test_s03_solution_moves_to_pending_validation_and_keeps_history` | solución + evento + nuevo estado | Pendiente CI final |
| AC-S03-05 | Solución de 19 se rechaza | `validate_solution` | `test_s03_solution_limits[19-False]` | sin solución | Pendiente CI final |
| AC-S03-06 | Solución de 801 se rechaza | `validate_solution` | `test_s03_solution_limits[801-False]` | sin solución | Pendiente CI final |
| AC-S03-07 | No se registra solución antes de EN_ATENCION | condición de estado | `test_s03_cannot_propose_solution_before_starting_attention` | conserva ASIGNADA; 0 soluciones | Pendiente CI final |
| AC-S03-08 | Texto HTML/script de solución se muestra escapado | Jinja + historial | `test_s03_solution_text_is_escaped_when_shown` | texto guardado sin ejecución | Pendiente CI final |

## S04 / RF04 — Validar, rechazar y reabrir

| Criterio | Comportamiento esperado | Código | Prueba / datos | Efecto esperado en SQLite | Estado |
|---|---|---|---|---|---|
| AC-S04-01 | Dueño confirma PENDIENTE_VALIDACION → CERRADA | `confirm_solution` | `test_s04_owner_confirms_pending_solution_and_closes` | closed_at UTC + evento cierre | Pendiente CI final |
| AC-S04-02 | Otro solicitante no confirma | `get_owned_incident` | `test_s04_other_requester_cannot_confirm` | conserva PENDIENTE_VALIDACION | Pendiente CI final |
| AC-S04-03 | Rechazo válido vuelve a EN_ATENCION y conserva técnico/solución | `reject_solution` | `test_s04_rejection_returns_to_attention_and_preserves_technician_and_solution` | evento de rechazo; misma asignación | Pendiente CI final |
| AC-S04-04 | Motivo 9/301 se rechaza | `validate_reason` | `test_s04_reason_limits` + `test_s04_invalid_rejection_reason_has_no_effect` | sin evento de rechazo | Pendiente CI final |
| AC-S04-05 | Exactamente 48 h permite reapertura | `reopen_incident` + reloj de servidor | `test_s04_reopen_exactly_48_hours_is_allowed` | EN_ATENCION + evento REABIERTA | Pendiente CI final |
| AC-S04-06 | 48 h + 1 s se rechaza | misma función | `test_s04_reopen_after_48_hours_is_rejected_without_changes` | conserva CERRADA | Pendiente CI final |
| AC-S04-07 | Coordinador no confirma ni reabre | autorización por rol | `test_s04_coordinator_cannot_confirm_or_reopen_for_requester` | 403; sin cambios | Pendiente CI final |
| AC-S04-08 | Cierres y soluciones previas se conservan | tablas `solutions` y `events` | `test_flow_close_reopen_new_solution_and_close_again` | 2 soluciones, 2 cierres, 1 reapertura | Pendiente CI final |
| AC-S04-09 | Operaciones inválidas no dejan efectos parciales | transacciones + validación previa | pruebas de motivo inválido y fuera de plazo | sin eventos parciales | Pendiente CI final |

## S05 / RF05 — Consultar e historizar

| Criterio | Comportamiento esperado | Código | Prueba / datos | Efecto esperado / salida | Estado |
|---|---|---|---|---|---|
| AC-S05-01 | Solicitante ve solo sus incidencias | `app/reporting.py` | `test_s05_requester_only_sees_own_incidents` | propia visible; ajena ausente | Pendiente CI final |
| AC-S05-02 | Técnico ve incidencias asignadas a él | `app/reporting.py` | `test_s05_technician_only_sees_assigned_incidents` | asignada visible; otra ausente | Pendiente CI final |
| AC-S05-03 | Coordinador combina estado y prioridad | filtros del listado | `test_s05_coordinator_combines_state_and_priority_filters` | solo coincidencia | Pendiente CI final |
| AC-S05-04 | Historial ordenado incluye eventos y soluciones | vista `history` | `test_s05_history_contains_events_solutions_and_escapes_text` | eventos/soluciones visibles | Pendiente CI final |
| AC-S05-05 | Historial no se edita ni borra | solo ruta GET | `test_s05_history_has_no_edit_operation` | POST responde 405 | Pendiente CI final |
| AC-S05-06 | Tablero cuenta estados, prioridades y críticas abiertas | `_dashboard` | `test_s05_dashboard_counts_and_close_percentage` | métricas calculadas | Pendiente CI final |
| AC-S05-07 | Porcentaje = CERRADAS/total × 100 con 1 decimal | `_dashboard` | misma prueba: 1/4 | muestra 25,0 % | Pendiente CI final |
| AC-S05-08 | Sin registros muestra 0,0 % | `_dashboard` | `test_s05_dashboard_zero_records_is_zero_percent` | 0,0 % | Pendiente CI final |
| AC-S05-09 | Texto persistido no se ejecuta como HTML/script | Jinja | `test_s05_history_contains_events_solutions_and_escapes_text` | salida escapada | Pendiente CI final |
| AC-S05-10 | Acceso directo no autorizado se rechaza | `_authorized_incident` | `test_s05_direct_history_access_respects_permissions` | 403 | Pendiente CI final |

## Recorridos de integración obligatorios

| ID | Recorrido | Prueba | Resultado esperado |
|---|---|---|---|
| INT-01 | registrar → asignar → iniciar → proponer → confirmar | `test_full_flow_register_assign_start_propose_confirm` | CERRADA e historial en orden |
| INT-02 | rechazo → nueva solución → confirmar | `test_flow_rejects_solution_and_accepts_new_solution` | 2 soluciones, 1 rechazo, CERRADA |
| INT-03 | cierre → reapertura → nueva solución → nuevo cierre | `test_flow_close_reopen_new_solution_and_close_again` | 2 cierres, 1 reapertura, 2 soluciones |

## Regresión

La suite final ejecuta también todas las pruebas de S01–S05. Una corrección del cierre no se aceptará si rompe una funcionalidad ya integrada.
