# Arquitectura de ReparaCampus

## 1. Idea general

ReparaCampus se hizo como un **monolito modular con Flask**. Para este examen nos pareció suficiente porque el sistema es pequeño, tiene un solo servidor y las reglas principales se pueden separar por archivos sin agregar tecnologías que el equipo todavía no necesita.

La aplicación se divide en cuatro partes sencillas:

1. **Interfaz:** HTML, CSS y plantillas Jinja.
2. **Rutas Flask:** reciben formularios, comprueban sesión/rol y coordinan cada acción.
3. **Reglas de negocio:** validaciones de datos, prioridades, límites de texto y reglas de estado.
4. **Persistencia:** SQLite para usuarios, incidencias, soluciones e historial.

Las pruebas se ejecutan con pytest usando una base SQLite temporal independiente.

## 2. Dónde se ejecutan las reglas

Las reglas importantes se comprueban en el servidor, no solo en la interfaz:

- usuario y rol salen de la sesión;
- prioridad se calcula en el servidor;
- permisos de solicitante, coordinador y técnico se validan en Flask;
- cambios de estado se aceptan solo desde el estado permitido;
- la reapertura usa fecha UTC del servidor;
- incidencia e historial se guardan dentro de la misma transacción.

Ocultar un botón en HTML ayuda a la interfaz, pero no se usa como mecanismo de seguridad.

## 3. Persistencia

Se usan cuatro tablas principales:

- `users`: cuentas ficticias, hash de contraseña, rol y estado activo;
- `incidents`: datos del reporte y estado actual;
- `solutions`: soluciones registradas por técnicos;
- `events`: historial de creación y transiciones.

El historial no tiene rutas de edición o eliminación en la aplicación.

## 4. Decisión tecnológica

### Opción elegida: Flask + SQLite + Jinja + pytest

La elegimos porque coincide con la ruta recomendada del examen, el equipo puede entenderla y permite comprobar las reglas sin tener que montar varios servicios.

**Ventajas para este trabajo:**
- instalación corta;
- SQLite no necesita un servidor adicional;
- Flask permite controlar sesiones y permisos desde el servidor;
- pytest facilita probar reglas y recorridos completos;
- Jinja permite una interfaz suficiente para demostrar el caso.

**Consecuencias:**
- no está pensado para muchos usuarios concurrentes;
- SQLite es adecuado para el prototipo, no para una plataforma universitaria real a gran escala;
- la interfaz es intencionalmente sencilla.

### Alternativas consideradas

**React + API separada:** daría una interfaz más independiente, pero agrega compilación, más estructura y más puntos de falla para un examen de una semana.

**PostgreSQL:** sería más apropiado para una solución productiva con más concurrencia, pero para el prototipo SQLite permite concentrarnos en las reglas y las pruebas.

Por esas razones preferimos una solución simple que podamos explicar y verificar completa.

## 5. Diagramas

Los archivos PlantUML están en `docs/uml/`:

- `componentes.puml`
- `modelo-datos.puml`
- `estados.puml`
- `secuencia-rechazo.puml`

Estos diagramas se usarán también en el PDF final.
