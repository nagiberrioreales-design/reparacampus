# Informe de Validación Final — ReparaCampus

**Responsable:** Milton Ramírez  
**Alcance:** Pruebas automatizadas, integración, límites, permisos y evidencias de validación  
**Rama de destino:** `main`  
**Última actualización:** 13 de octubre de 2026

## 1. Resumen de ejecución de pruebas automatizadas

**Entorno:** Python 3.12, pytest y SQLite.

### 1.1. Ejecución local histórica

- **Commit verificado:** `f6768aebda09f808f43170c3c9881a01324d1328`
- **Fecha:** 12 de octubre de 2026
- **Comando:** `python -m pytest -q`
- **Resultado:** 56 pruebas aprobadas y 0 fallidas.

Este resultado corresponde exclusivamente a la versión histórica indicada. No representa el estado actual de la rama principal.

### 1.2. Validación de GitHub Actions del PR #27

Posteriormente, la ejecución automatizada de GitHub Actions asociada al PR #27 registró **67 pruebas aprobadas**, sin fallos.

Esta evidencia corresponde al entorno de integración continua del Pull Request y debe diferenciarse de la ejecución local de 56 pruebas.

### 1.3. Regresión local sobre la versión actualizada de main

Después de fusionar el PR #25, que incorporó modificaciones visuales al tablero del coordinador, se integró el PR #32 para adaptar las pruebas automatizadas a la nueva estructura HTML.

Un integrante del equipo ejecutó la suite completa sobre la rama `main` actualizada:

- **Commit:** `e47e5f89bc28b6bb93c66174b15d9d84fbbce03e`
- **Comando:** `python -m pytest -q`
- **Resultado:** 67 pruebas aprobadas, 0 fallidas.
- **Duración:** 25.86 segundos.

Este resultado confirma que la suite automatizada finalizó correctamente en esa versión del repositorio.

## 2. Validación de recorridos de integración

Se verificaron los tres recorridos principales mediante las pruebas definidas en `tests/test_integration_flows.py`:

**INT-01 — Flujo nominal:** Registro → Asignación → Inicio de atención → Solución → Cierre exitoso.

**INT-02 — Rechazo y reatención:** Registro → Asignación → Solución inicial → Rechazo por el usuario → Nueva solución → Cierre.

**INT-03 — Reapertura:** Registro → Solución → Cierre → Reapertura dentro de la ventana de 48 horas → Nueva atención → Cierre definitivo.

Los tres escenarios cuentan con pruebas automatizadas. Los porcentajes acumulativos 33 %, 66 % y 100 % se eliminan porque no representan el resultado individual de cada prueba.

## 3. Comprobación por módulos y reglas negativas

Las siguientes evidencias corresponden a las verificaciones históricas realizadas:

**S01 — Registro y límites:** Validación de descripciones entre 20 y 500 caracteres y rechazo de entradas fuera de rango. Resultado registrado: 14 pruebas aprobadas.

**S02 y S03 — Asignación y solución:** Verificación de longitudes de solución entre 20 y 800 caracteres y restricciones de transición entre estados. Resultado registrado: 11 pruebas aprobadas.

**S04 — Permisos y reapertura:** Comprobación de restricciones de acceso, respuestas HTTP 403 y ventana de reapertura de 48 horas. Resultado registrado: 11 pruebas aprobadas.

**S05 — Estadísticas, historial y seguridad:** Comprobación de consultas, historial y manejo seguro de contenido en los escenarios automatizados. Resultado registrado: 9 pruebas aprobadas.

Estos resultados respaldan los escenarios probados, pero no constituyen por sí solos una certificación de seguridad integral.

## 4. Clasificación de resultados y pendientes

**Cumplimiento verificado:** Las ejecuciones registradas finalizaron sin pruebas fallidas. Los recorridos INT-01, INT-02 e INT-03 cuentan con pruebas automatizadas y la regresión local sobre `main`, commit `e47e5f8`, obtuvo 67 pruebas aprobadas.

**Incumplimientos detectados por las pruebas ejecutadas:** No se registraron fallos en las ejecuciones citadas.

**Aspectos pendientes:** La auditoría de criterios de aceptación identificó necesidades de cobertura o evidencia adicional para AC-S01-01, AC-S01-02, AC-S01-04, AC-S01-06, AC-S03-02, AC-S04-02 y AC-S04-09. La aprobación de las pruebas existentes no demuestra automáticamente cobertura completa de todos los criterios.

## 5. Conclusión

Las evidencias disponibles muestran resultados satisfactorios en las pruebas automatizadas e integración de ReparaCampus.

La ejecución histórica de 56 pruebas, el resultado de 67 pruebas en GitHub Actions del PR #27 y la regresión local de 67 pruebas sobre el commit `e47e5f8` corresponden a verificaciones diferentes y se presentan por separado.

El proyecto dispone de una base funcional verificada para los escenarios automatizados ejecutados. Las necesidades de cobertura adicional identificadas deben conservarse como observaciones de calidad para futuras validaciones.
