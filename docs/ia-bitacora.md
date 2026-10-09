# Bitácora de uso de IA

En el equipo usamos ChatGPT como apoyo, pero no copiamos toda la conversación al informe. Conservamos cuatro intervenciones que muestran momentos distintos del trabajo: especificación, código, pruebas y revisión final.

## Intervención IA-01 — Especificación antes del código

- **Fecha:** 08/10/2026
- **Autor / herramienta / modelo:** Equipo ReparaCampus / ChatGPT / GPT-5.6 Sol
- **Historia y SPEC / versión:** RF01–RF05; S01–S05 v0.1
- **Objetivo y contexto:** transformar el enunciado del examen en cinco historias y cinco SPECS sin agregar reglas nuevas.
- **Prompt o instrucción resumida:** conservar actores, permisos, estados, límites y reglas; escribir criterios Dado/Cuando/Entonces; separar las dudas reales de las decisiones del cliente.
- **Respuesta relevante:** se propusieron S01–S05, criterios, diseño, tareas y preguntas abiertas.
- **Decisión humana y justificación:** el equipo comparó la propuesta con todos los bloques del enunciado y abrió el PR #6 solo con SPECS, antes de crear código funcional.
- **Error o limitación encontrada:** en la primera lectura aparecieron como “dudas” algunas reglas que en realidad ya estaban contestadas en los bloques desplegados.
- **Corrección y verificación:** se eliminaron esas falsas dudas y quedaron tres preguntas realmente abiertas en `docs/preguntas-cliente.md`. Steven Reyes revisó y aprobó el PR #6.
- **Archivo / commit / prueba:** `specs/S01-registro.md` a `specs/S05-consulta-historial.md`; PR #6; merge `ef8fbba40abd995c83813ebe9bdc47676f279e13`.

## Intervención IA-02 — Implementación sencilla de S01 y S02

- **Fecha:** 08/10/2026
- **Autor / herramienta / modelo:** Equipo ReparaCampus / ChatGPT / GPT-5.6 Sol
- **Historia y SPEC / versión:** S01 y S02 v0.1
- **Objetivo y contexto:** convertir las SPECS revisadas en una aplicación Flask pequeña con sesión, SQLite e historial.
- **Prompt o instrucción resumida:** implementar solo las reglas escritas en S01/S02; identidad desde sesión; prioridad en servidor; operaciones con historial y pruebas.
- **Respuesta relevante:** estructura con Flask, funciones de dominio, SQLite, Jinja y pytest.
- **Decisión humana y justificación:** se mantuvo un monolito modular simple. No se agregó React ni una API separada porque no eran necesarias para demostrar el examen.
- **Error o limitación encontrada:** el primer workflow de GitHub Actions estaba únicamente en la rama de S01 y el PR no tenía todavía el archivo en la rama base.
- **Corrección y verificación:** se agregó el workflow a `main`, se volvió a ejecutar y el CI terminó correctamente. S01 y S02 se integraron solo después de revisión humana.
- **Archivo / commit / prueba:** PR #7 y #8; merges `55afad78c1fd66ff8618924a304a26f5f66cfc39` y `3541fc81fdf7e63bbfcefedd9f255f7d0f45898b`.

## Intervención IA-03 — Pruebas, límites y recorridos completos

- **Fecha:** 08/10/2026
- **Autor / herramienta / modelo:** Equipo ReparaCampus / ChatGPT / GPT-5.6 Sol
- **Historia y SPEC / versión:** S03–S05 v0.1
- **Objetivo y contexto:** comparar el comportamiento con criterios concretos y cubrir los recorridos de integración pedidos.
- **Prompt o instrucción resumida:** crear pruebas independientes para permisos, estados, 19/20, 800/801, 48 h, 48 h + 1 s, historial y los tres recorridos completos con SQLite real de prueba.
- **Respuesta relevante:** pruebas por SPEC y `tests/test_integration_flows.py`.
- **Decisión humana y justificación:** los esperados se escribieron desde las SPECS y no llamando a la misma función de producción para calcular la respuesta esperada.
- **Error o limitación encontrada:** en la revisión de cobertura vimos que S03 todavía no tenía pruebas directas para iniciar desde un estado incompatible, proponer solución antes de iniciar y mostrar una solución parecida a script.
- **Corrección y verificación:** se agregaron esas tres pruebas antes del cierre. La suite final llegó a 56 pruebas.
- **Archivo / commit / prueba:** `tests/test_s03_attention_solution.py`, `tests/test_s04_validation_reopen.py`, `tests/test_s05_query_history.py`, `tests/test_integration_flows.py`.

## Intervención IA-04 — Revisión final de trazabilidad y documentación

- **Fecha:** 08/10/2026
- **Autor / herramienta / modelo:** Equipo ReparaCampus / ChatGPT / GPT-5.6 Sol
- **Historia y SPEC / versión:** S01–S05 v0.1 y cierre del examen
- **Objetivo y contexto:** revisar que PDF/repositorio puedan demostrar la cadena requisito → SPEC → código → prueba y que no se presente como terminado algo sin evidencia.
- **Prompt o instrucción resumida:** contrastar SPECS, código, pruebas, arquitectura, riesgos, README y contribuciones; señalar contradicciones y no inventar participación de integrantes.
- **Respuesta relevante:** matriz SPEC/código, cuatro riesgos, diagramas y lista de contribuciones verificables/pendientes.
- **Decisión humana y justificación:** se decidió declarar de forma explícita las evidencias individuales que todavía deben dejar Juan, Leyter, Milton y Santiago, en vez de afirmar que ya existen.
- **Error o limitación encontrada:** aunque el PR #6 había sido aprobado antes del código, los archivos S01–S05 todavía conservaban el texto “revisor pendiente”.
- **Corrección y verificación:** se actualizó únicamente la metadata de revisión para registrar a Steven Reyes y la aprobación del PR #6, sin cambiar las reglas de las SPECS. GitHub Actions del cierre ejecutó 56 pruebas y terminó en success.
- **Archivo / commit / prueba:** `docs/matriz-spec-codigo.md`, `docs/riesgos.md`, `docs/arquitectura.md`, `docs/contribuciones.md`; PR #16.
