# Bitácora de uso de IA

La bitácora conserva intervenciones relevantes, no la conversación completa. La IA se usa como apoyo; las reglas del examen y la comprobación humana tienen prioridad.

## Intervención IA-01 — Especificaciones y preparación de S01

- **Fecha:** 08/10/2026
- **Herramienta / modelo:** ChatGPT — GPT-5.6 Sol
- **Historia y SPEC / versión:** RF01–RF05; S01–S05 v0.1
- **Objetivo y contexto:** convertir los requisitos visibles del examen ReparaCampus en cinco SPECS antes de escribir código.
- **Prompt o instrucción resumida:** revisar el enunciado, conservar reglas, actores, estados, límites y permisos; proponer historias, criterios verificables, diseño y tareas sin inventar decisiones del cliente.
- **Respuesta relevante:** se propusieron las cinco SPECS, criterios Dado/Cuando/Entonces, tareas y preguntas abiertas.
- **Decisión humana y justificación:** se mantuvieron las reglas que aparecen en el enunciado y se creó un PR solo de SPECS para que otro integrante las revisara antes de programar.
- **Error o limitación detectada:** en una primera lectura se plantearon algunas dudas que después vimos que ya estaban respondidas por los bloques desplegados del enunciado.
- **Corrección y verificación:** se reemplazaron esas dudas por tres preguntas realmente abiertas y Steven Reyes revisó y aprobó el PR #6 antes de iniciar la implementación.
- **Archivo / commit / prueba:** `specs/S01-registro.md` a `specs/S05-consulta-historial.md`; PR #6; merge `ef8fbba40abd995c83813ebe9bdc47676f279e13`.

## Intervención IA-02 — Implementación de S01 y preparación de S02

- **Fecha:** 08/10/2026
- **Herramienta / modelo:** ChatGPT — GPT-5.6 Sol
- **Historia y SPEC / versión:** S01 v0.1 implementada; S02 v0.1 revisada.
- **Objetivo y contexto:** convertir las reglas ya revisadas en una implementación pequeña con Flask y SQLite, y después preparar la siguiente funcionalidad sin mezclar responsabilidades.
- **Prompt o instrucción resumida:** implementar solo lo que permiten S01 y S02; mantener identidad desde sesión, validación en servidor, transacciones e historial; agregar pruebas antes de integrar.
- **Respuesta relevante:** se propuso una estructura sencilla de rutas Flask, funciones de dominio, SQLite, plantillas y pytest.
- **Decisión humana y justificación:** se mantuvo una solución simple de estudiante, sin React ni capas innecesarias. S01 se integró solo después de que Steven Reyes revisó el PR #7 y el pipeline terminó correctamente.
- **Error o limitación detectada:** al principio el workflow de GitHub Actions estaba solo en la rama de S01 y no se ejecutaba de forma estable en el PR porque el archivo no existía todavía en la rama base.
- **Corrección y verificación:** se agregó el workflow también a `main`, se volvió a ejecutar el PR y GitHub Actions terminó en `success`.
- **Archivo / commit / prueba:** PR #7; revisión aprobada por Steven Reyes; merge `55afad78c1fd66ff8618924a304a26f5f66cfc39`; workflow run `37881326197` en success.
