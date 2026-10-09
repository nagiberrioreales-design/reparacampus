# ReparaCampus

Aplicación académica para gestionar incidencias de infraestructura de la Universidad Simón Bolívar. El proyecto se desarrolla siguiendo el examen **Especifica. Construye. Verifica.**

## Estado actual

- S01–S05 fueron escritas y revisadas antes del código en el PR #6.
- S01 / RF01 — registro de incidencias: implementada y revisada.
- S02 / RF02 — priorización y asignación: implementada y revisada.
- S03 / RF03 — atención y registro de solución: en implementación.
- S04–S05: todavía no se consideran implementadas.

## Tecnologías

- Python 3.12
- Flask 3.1.2
- SQLite 3 (incluido con Python)
- pytest 8.4.2
- HTML + CSS
- Git + GitHub Actions

## Instalación desde una copia limpia

```bash
python -m venv .venv
```

Activar el entorno:

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

Ejecutar:

```bash
flask --app app run --debug
```

Abrir `http://127.0.0.1:5000`.

## Cuentas ficticias del seed

Todas usan la contraseña de prueba **Campus2026!**.

| Usuario | Rol |
|---|---|
| solicitante1 | SOLICITANTE |
| solicitante2 | SOLICITANTE |
| coordinador | COORDINADOR |
| tecnico1 | TECNICO activo |
| tecnico2 | TECNICO activo |

Estas cuentas y contraseñas son únicamente datos ficticios del prototipo.

## Pruebas

```bash
pytest -q
```

Las pruebas usan una base SQLite temporal independiente. La suite irá creciendo con cada SPEC.

## Estructura

- `specs/`: S01–S05 y trazabilidad.
- `docs/`: preguntas al cliente, diseño y bitácora de IA.
- `app/`: aplicación Flask, reglas y persistencia.
- `tests/`: pruebas automatizadas.
- `.github/workflows/tests.yml`: ejecución automática de pytest.

## Forma de trabajo

La secuencia acordada es:

`RF → historia → SPEC → revisión → código → prueba → resultado`

No se integra una funcionalidad sin revisión de su SPEC y sin pruebas asociadas.
