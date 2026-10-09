# ReparaCampus

Aplicación académica para gestionar incidencias de infraestructura de la Universidad Simón Bolívar. El proyecto se desarrolla siguiendo el examen **Especifica. Construye. Verifica.**

## Estado actual

- S01–S05 fueron escritas y revisadas antes del código en el PR #6.
- S01 / RF01 — registro de incidencias: implementada y revisada.
- S02 / RF02 — priorización y asignación: implementada y revisada.
- S03 / RF03 — atención y registro de solución: implementada y revisada.
- S04 / RF04 — validación, rechazo y reapertura: implementada y revisada.
- S05 / RF05 — consulta, historial y tablero: implementada y revisada.
- El cierre del examen agrega arquitectura, riesgos, trazabilidad y tres recorridos de integración completos.

## Tecnologías y versiones

- Python 3.12
- Flask 3.1.2
- SQLite 3, incluido con Python
- pytest 8.4.2
- HTML + CSS + Jinja
- Git + GitHub Actions

## Instalación desde una copia limpia

Crear entorno virtual:

```bash
python -m venv .venv
```

Activarlo.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Inicializar la base SQLite con datos ficticios:

```bash
flask --app app init-db
```

Ejecutar la aplicación:

```bash
flask --app app run
```

Abrir:

`http://127.0.0.1:5000`

## Cuentas ficticias

Todas usan la contraseña de prueba **Campus2026!**.

| Usuario | Rol | Estado |
|---|---|---|
| solicitante1 | SOLICITANTE | activo |
| solicitante2 | SOLICITANTE | activo |
| coordinador | COORDINADOR | activo |
| tecnico1 | TECNICO | activo |
| tecnico2 | TECNICO | activo |

Son cuentas ficticias del prototipo. No se usan datos personales reales.

## Recorrido de demostración

1. Entrar como `solicitante1` y registrar una incidencia.
2. Cerrar sesión y entrar como `coordinador`.
3. Asignar el reporte a `tecnico1`; la prioridad se calcula en el servidor.
4. Entrar como `tecnico1`, iniciar atención y registrar una solución.
5. Volver a `solicitante1` y confirmar o rechazar.
6. Si se confirma, puede probarse una reapertura dentro de las 48 horas.
7. En **Consultar** se puede revisar el historial según los permisos de cada rol.
8. El coordinador puede ver filtros y métricas del tablero.

### Verificación manual de permisos

Durante la demostración se recomienda cerrar sesión antes de cambiar de rol. También se puede intentar acceder directamente a una ruta de otro rol para comprobar que los permisos se validan en el servidor y no solamente ocultando botones en la interfaz.

## Pruebas

Ejecutar:

```bash
pytest -q
```

Las pruebas usan bases SQLite temporales e independientes. Incluyen los tres recorridos de integración solicitados:

- registrar → asignar → iniciar → proponer → confirmar;
- recorrido con rechazo → nueva solución → confirmación;
- cierre → reapertura → nueva solución → nuevo cierre.

GitHub Actions ejecuta la misma suite en los pull requests.

## Estructura

- `specs/`: S01–S05 y trazabilidad.
- `docs/`: preguntas, diseño, IA, arquitectura, UML, riesgos y validación.
- `app/`: aplicación Flask.
- `tests/`: pruebas unitarias e integración.
- `.github/workflows/tests.yml`: CI con pytest.

## Forma de trabajo

La secuencia usada fue:

`RF → historia → SPEC → revisión → código → prueba → resultado`

No se integró una funcionalidad sin que su SPEC estuviera revisada y sin pruebas asociadas.

## Seguridad y límites del prototipo

- sesión y rol se verifican en servidor;
- contraseñas ficticias se guardan con hash;
- no se usa selector de rol para autorizar;
- textos se muestran con escape de Jinja;
- fechas de reapertura se calculan en UTC del servidor;
- no hay adjuntos, notificaciones, hosting obligatorio ni IA dentro del producto.

La clave de prueba `Campus2026!` es pública porque pertenece únicamente a las cinco cuentas ficticias pedidas por el examen.
