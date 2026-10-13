# Informe de Verificación: Panel del Técnico, Modelo de Datos e Historial

* **Autor / Revisor:** Leyter (`leiter11447-crypto`)
* **Fecha:** 12 de octubre de 2026
* **Rama:** `docs/verificacion-tecnico-leyter`
* **Commit SHA verificado:** `1176f261a976ac8067a7fe4dc543a84a5ba5470e`
* **Incidencia de prueba auditada:** `INC-CAD3BFEB`
* **Issue de referencia:** [Issue #13 de Leyter](https://github.com/nagiberrioreales-design/reparacampus/issues/13)
* **PR de referencia:** #16 (Aprobado previamente)

---

## Objetivo
Comprobar la consistencia operativa del panel del técnico, la correcta persistencia del historial de eventos y soluciones, la integridad del modelo relacional SQLite frente al modelo UML y la cobertura de pruebas automatizadas en ReparaCampus.

---

## Tabla de Resultados

| Módulo / Criterio | Estado | Hallazgo Técnico Observado |
| :--- | :---: | :--- |
| **Panel del técnico (`assigned.html`)** | **Cumple** | Renderiza la tabla de asignaciones aislada exclusivamente al usuario en sesión (`tecnico1`). Muestra mensaje alternativo si no hay asignaciones. |
| **Inicio de atención** | **Cumple** | Botón condicionado estrictamente al estado `ASIGNADA`. Al pulsarlo ejecuta POST y realiza la transición inmediata a `EN_ATENCION`. |
| **Registro de solución** | **Cumple** | Área de texto con validación obligatoria (20 a 800 caracteres). Al registrar solución, transiciona a `PENDIENTE_VALIDACION` y desactiva nuevas acciones (`Sin acción disponible`). |
| **Permisos entre técnicos** | **Cumple** | `tecnico2` no visualiza tickets de `tecnico1`. En backend, intentos de forzar acciones ajenas son interceptados con respuesta **HTTP 403 Forbidden**. |
| **Persistencia e Historial (`history.html`)** | **Cumple** | Registro inmutable de eventos (`CREADA`, `ASIGNADA`, `INICIO_ATENCION`, `SOLUCION_PROPUESTA`). Soluciones acumulativas persistentes ante rechazo o reapertura. |
| **Consistencia Modelo SQL vs. UML** | **Cumple** | Correspondencia 100% entre entidades, tipos y cardinalidades de `modelo-datos.puml` y `schema.sql`. Claves foráneas activas (`PRAGMA foreign_keys = ON;`). |
| **Transaccionalidad en Backend** | **Cumple** | En `app/incidents.py`, los cambios de estado (`UPDATE`) y los eventos de auditoría (`INSERT`) se ejecutan atómicamente dentro del bloque `with db:`. |
| **Pruebas Automatizadas (`pytest`)** | **Cumple** | **Suite completa:** `67 passed in 55.43s`.<br>**Atención/Solución:** `13 passed in 9.95s`.<br>**Flujos de integración:** `3 passed in 6.11s`. 100% de efectividad. |

---

## Evidencias Recopiladas

1. **Capturas del flujo de asignaciones:**
   * Incidencia en estado `ASIGNADA` con botón «Iniciar atención».
   * Incidencia en estado `EN_ATENCION` con formulario de solución desplegado.
   * Incidencia en estado `PENDIENTE_VALIDACION` con restricción visual «Sin acción disponible».
2. **Captura de historial y auditoría:**
   * Tabla de eventos en `/reports/incidents/<id>/history` con la secuencia cronológica de estados y autores (`CREADA` $\rightarrow$ `ASIGNADA` $\rightarrow$ `INICIO_ATENCION` $\rightarrow$ `SOLUCION_PROPUESTA`).
   * Cuadro de soluciones registradas con texto, fecha UTC y autoría de `Técnico Uno`.
3. **Captura de permisos:**
   * Sesión de `tecnico2` confirmando aislamiento de datos sin tickets ajenos visibles.
4. **Capturas de consola y pruebas:**
   * Ejecución exitosa de `pytest` en local (67 pruebas aprobadas).
   * Ejecución del servidor Flask y trazas de peticiones HTTP en consola.

---

## Conclusión

Basado exclusivamente en las inspecciones de código, las pruebas unitarias y de integración ejecutadas en el entorno local, y la validación en vivo en el navegador:

El sistema **ReparaCampus cumple íntegramente** con las especificaciones arquitectónicas, las políticas de seguridad y control de acceso entre técnicos, y la preservación inmutable del historial de incidencias. La documentación técnica y el código se encuentran alineados y en estado óptimo.