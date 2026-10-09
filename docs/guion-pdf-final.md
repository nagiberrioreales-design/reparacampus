# Guion del PDF final — ReparaCampus

Este archivo sirve como base para armar el PDF final. Se mantiene un lenguaje claro de estudiantes y solo se incluyen evidencias reales.

## 1. Portada

- Universidad Simón Bolívar
- Programa: Ingeniería de Sistemas
- Asignatura: Ingeniería de Software I
- Título: Examen SDD — ReparaCampus
- Equipo: Henry Berrio, Juan González, Leyter López, Milton Ramírez, Santiago Hernández, Steven Reyes
- Códigos estudiantiles: **pendientes de completar**
- Grupo: **pendiente**
- Docente: **pendiente**
- Fecha: 2026-10
- Repositorio: https://github.com/nagiberrioreales-design/reparacampus

## 2. Índice

Se generará automáticamente en Word/PDF con las 11 secciones y número de página.

## 3. Problema y alcance

Explicar con palabras sencillas:
- necesidad de registrar y dar seguimiento a daños de infraestructura;
- actores: solicitante, coordinador y técnico;
- RF01–RF05;
- ubicaciones y categorías válidas;
- cinco cuentas ficticias;
- límites del prototipo: sin adjuntos, notificaciones, hosting obligatorio ni IA dentro del producto;
- reglas que no se pueden cambiar;
- tres preguntas al cliente y supuestos pendientes documentados.

Fuente interna: `docs/preguntas-cliente.md`.

## 4. Cinco SPECS

Presentar S01–S05 con:
- historia;
- alcance;
- entradas;
- permisos;
- reglas;
- criterios de aceptación;
- tareas;
- versión 0.1;
- revisión previa por Steven Reyes en PR #6.

Fuentes:
- `specs/S01-registro.md`
- `specs/S02-priorizacion-asignacion.md`
- `specs/S03-atencion-solucion.md`
- `specs/S04-validacion-reapertura.md`
- `specs/S05-consulta-historial.md`

Evidencia clave: PR #6 aprobado antes del código.

## 5. Diseño

Incluir:
- componentes;
- modelo de datos;
- UML de estados;
- secuencia de rechazo;
- decisión Flask + SQLite + Jinja + pytest;
- alternativas consideradas y por qué no se usaron.

Fuentes:
- `docs/arquitectura.md`
- `docs/uml/componentes.puml`
- `docs/uml/modelo-datos.puml`
- `docs/uml/estados.puml`
- `docs/uml/secuencia-rechazo.puml`

## 6. IA e implementación

Explicar cuatro intervenciones reales:
1. especificación;
2. implementación sencilla;
3. pruebas y límites;
4. revisión final.

Para cada una mostrar:
- contexto;
- prompt resumido;
- respuesta útil;
- decisión humana;
- error o limitación;
- corrección;
- evidencia.

Fuente: `docs/ia-bitacora.md`.

También resumir la implementación de RF01–RF05 y enlazar PR #7 a #11.

## 7. Validación

Incluir:
- matriz RF → SPEC → AC → código → prueba;
- comando `pytest -q`;
- resultado final: 53 pruebas aprobadas, 0 fallidas;
- los 3 recorridos de integración;
- límites 19/20, 800/801, 48 h y 48 h + 1 s;
- regresión completa de S01–S05.

Fuentes:
- `docs/matriz-spec-codigo.md`
- `docs/resultados-pruebas.md`
- GitHub Actions del PR #16.

## 8. Riesgos

Mostrar los cuatro riesgos:
- R-IA-01: transición inventada por IA;
- R-IA-02: prueba que repite el mismo error del código;
- R-PROD-01: acceso a incidencias ajenas;
- R-PROD-02: estado e historial inconsistentes.

Para cada uno: causa, impacto, control, responsable y evidencia.

Fuente: `docs/riesgos.md`.

## 9. Entrega reproducible

Debe quedar:
- URL del repositorio;
- tag final `release-examen` — **se crea después del merge final**;
- SHA final — **se obtiene después del merge final**;
- instalación;
- arranque;
- seed;
- cuentas ficticias;
- `pytest -q`;
- README accesible.

Fuente: `README.md`.

## 10. Contribuciones y cierre

Explicar aportes verificables por integrante.

Estado actual:
- Henry Berrio: verificable.
- Steven Reyes: verificable.
- Milton Ramírez: verificable desde `Bellator07`.
- Juan González: pendiente de Issue #12 + revisión PR #16.
- Leyter López: pendiente de Issue #13 + revisión PR #16.
- Santiago Hernández: pendiente de Issue #15 + revisión PR #16.

Fuente: `docs/contribuciones.md`.

Cierre final del equipo:
- qué aprendimos al trabajar primero con SPEC;
- por qué las pruebas ayudaron a detectar reglas límite;
- qué dificultad tuvimos con estados, permisos y revisión;
- conclusión sobre cumplimiento del examen.

## 11. Referencias

Usar las referencias oficiales ya registradas en:
`docs/referencias.md`

Agregar como fuente principal:
- enunciado ReparaCampus entregado por el docente.

## Pendientes antes de exportar el PDF

1. Juan completa #12 + PR #16.
2. Leyter completa #13 + PR #16.
3. Santiago completa #15 + PR #16.
4. Cerrar esos issues.
5. Hacer merge del PR #16.
6. Crear tag `release-examen`.
7. Registrar SHA final.
8. Completar códigos estudiantiles, grupo y docente.
9. Generar Word y PDF.
10. Abrir el PDF final y revisar índice, enlaces, nombres, diagramas y legibilidad.
11. Cada integrante sube el mismo PDF al aula.
