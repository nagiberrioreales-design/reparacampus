# Matriz de riesgos y controles

La idea de esta matriz no es llenar riesgos por llenar. Elegimos cuatro que realmente podían hacer que el examen quedara incorrecto: dos relacionados con el uso de IA y dos con el producto.

| ID | Riesgo | Causa | Impacto | Control aplicado | Responsable de seguimiento | Evidencia |
|---|---|---|---|---|---|---|
| R-IA-01 | La IA propone una transición que no existe, por ejemplo que el técnico cierre directamente una incidencia. | El asistente puede completar el flujo usando patrones comunes que no pertenecen al enunciado. | Se rompe RF03/RF04 y el sistema deja de respetar el modelo de estados. | SPECS revisadas antes del código; diagrama de estados; rutas limitadas a transiciones permitidas; pruebas de estados incompatibles. | Steven Reyes | PR #6 aprobado; `specs/S01...` a `S05...`; `docs/uml/estados.puml`; pruebas S03/S04. |
| R-IA-02 | Una prueba generada con ayuda de IA repite el mismo error que el código y da una falsa sensación de que todo funciona. | Esperado y observado podrían calcularse con la misma lógica. | Un defecto podría pasar aunque las pruebas estén verdes. | Los valores esperados se escriben directamente desde el requisito; se prueban límites concretos 19/20, 800/801, 48 h y 48 h + 1 s; se añaden tres recorridos completos. | Milton Ramírez | `tests/test_s01_unit.py`, `test_s03_attention_solution.py`, `test_s04_validation_reopen.py`, `test_integration_flows.py`. |
| R-PROD-01 | Un usuario consulta o modifica una incidencia que no le pertenece. | Confiar solo en botones ocultos o en datos enviados por el navegador. | Exposición de información y operaciones realizadas por el actor equivocado. | Identidad/rol desde sesión; permisos verificados en servidor; comprobación de propietario o técnico asignado; pruebas de acceso directo 403. | Juan González | `app/auth.py`, `app/reporting.py`, pruebas S01, S03, S04 y S05 de autorización. |
| R-PROD-02 | Una operación falla a mitad de camino y deja estado e historial diferentes. | Guardar primero el estado y luego el evento sin una transacción. | Historial engañoso y pérdida de trazabilidad. | Cambios de estado, soluciones y eventos se realizan dentro de la misma transacción SQLite; pruebas comprueban que entradas inválidas no cambian estado ni crean eventos/soluciones. | Leyter López | `app/incidents.py`; pruebas de rechazo, solución inválida, técnico inactivo y reasignación. |

## Comprobación

Los controles no dependen de un mensaje para la IA. Se verifican en código, pruebas o revisiones de GitHub.

En particular:

- R-IA-01 se comprueba comparando el código con el diagrama de estados y las SPECS.
- R-IA-02 se comprueba con límites escritos de forma explícita y recorridos de integración.
- R-PROD-01 se comprueba intentando acceder con usuarios distintos a los permitidos.
- R-PROD-02 se comprueba verificando la base después de operaciones rechazadas.

La matriz se volverá a revisar en el PR de cierre antes de crear la etiqueta final del examen.
