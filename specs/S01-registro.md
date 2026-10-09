# S01 — Registrar incidencia

**Versión:** 0.1  
**Fecha:** 08/10/2026  
**Autor documental:** Equipo ReparaCampus  
**Revisor:** Steven Reyes  
**Fecha de revisión:** 08/10/2026  
**Requisito asociado:** RF01

## Historia
Como **solicitante**, quiero registrar una incidencia de infraestructura para que la Universidad pueda conocer y gestionar el daño reportado.

## Alcance y exclusiones
Incluye la creación de una incidencia por un solicitante autenticado. No incluye asignación, atención, validación, reapertura, adjuntos ni notificaciones.

## Entradas
- ubicación obligatoria: `LAB-01`, `AULA-201` o `BIB-01`;
- categoría obligatoria: `ELECTRICIDAD`, `HIDRAULICA`, `MOBILIARIO` o `TIC`;
- descripción obligatoria de 20 a 500 caracteres después de retirar espacios externos;
- impacto obligatorio: `BAJO` o `ALTO`;
- riesgo para personas: booleano.

## Precondiciones y permisos
- Usuario autenticado con rol `SOLICITANTE`.
- El autor se obtiene de la sesión del servidor, nunca de un selector o campo editable del cliente.

## Reglas y proceso
1. El servidor normaliza los límites de texto retirando espacios externos.
2. Valida catálogos, obligatoriedad y longitud.
3. Si todo es válido, genera código, autor, fecha UTC y estado inicial `REGISTRADA`.
4. La incidencia y el evento inicial del historial se guardan en una misma operación consistente.
5. Una operación rechazada no crea incidencia ni evento parcial.

## Salidas y cambios persistidos
- incidencia nueva en estado `REGISTRADA`;
- código generado;
- autor autenticado;
- fecha UTC;
- evento inmutable de creación en historial.

## Errores y efectos que deben evitarse
- aceptar valores fuera de catálogo;
- aceptar descripción fuera de 20–500 caracteres;
- confiar en un autor enviado por el navegador;
- ejecutar texto almacenado como HTML/JavaScript;
- persistir incidencia sin su evento o viceversa.

## Criterios de aceptación
- **AC-S01-01:** Dado un solicitante autenticado y datos válidos, cuando registra la incidencia, entonces se crea con código generado, autor de sesión, fecha UTC y estado `REGISTRADA`.
- **AC-S01-02:** Dada una descripción de 19 caracteres después de trim, cuando intenta registrar, entonces se rechaza sin cambios persistidos.
- **AC-S01-03:** Dada una descripción de exactamente 20 caracteres después de trim y los demás campos válidos, cuando registra, entonces se acepta.
- **AC-S01-04:** Dada una descripción de más de 500 caracteres después de trim, cuando intenta registrar, entonces se rechaza sin cambios persistidos.
- **AC-S01-05:** Dada una ubicación, categoría o impacto fuera del catálogo, cuando intenta registrar, entonces el servidor rechaza la operación.
- **AC-S01-06:** Dado un usuario no autenticado o con rol distinto de `SOLICITANTE`, cuando intenta crear una incidencia, entonces la operación es rechazada.
- **AC-S01-07:** Dado un intento de enviar otro identificador de autor desde el cliente, cuando se registra la incidencia, entonces el autor persistido es exclusivamente el usuario de la sesión.
- **AC-S01-08:** Dado texto parecido a HTML o scripts en la descripción, cuando se consulta posteriormente, entonces se presenta como texto y no se ejecuta.

## Diseño y tareas vinculadas
- T-S01-01: esquema de incidencia y evento.
- T-S01-02: validaciones de dominio y catálogos.
- T-S01-03: servicio transaccional de creación.
- T-S01-04: formulario y mensajes de validación.
- T-S01-05: pruebas unitarias e integración para AC-S01.

## Pruebas y resultados esperados
Cubrir caso válido, 19/20/500/501 caracteres, catálogos inválidos, permisos, autor manipulado y texto no ejecutable.

## Decisión de revisión
**Pendiente. No implementar S01 hasta registrar una revisión humana aprobada de esta versión.**
