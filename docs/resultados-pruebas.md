# Resultados de pruebas del cierre

## Resultado automático

Comando ejecutado por GitHub Actions:

```bash
pytest -q
```

Resultado observado en el cierre del PR #16:

```text
..................................................... [100%]
53 passed
```

En la ejecución registrada, las 53 pruebas terminaron correctamente y no hubo fallos.

## Qué cubre la suite

La suite contiene pruebas de:

- datos válidos e inválidos de registro;
- límites de descripción;
- catálogos permitidos;
- usuario de sesión y permisos;
- prioridad CRITICA, ALTA y NORMAL;
- técnico activo e intento de reasignación;
- inicio de atención por técnico asignado;
- límites 19/20 y 800/801 para solución;
- estados incompatibles;
- texto HTML/script tratado como texto;
- confirmación y rechazo por propietario;
- motivo 9/10 y 300/301;
- reapertura exactamente a las 48 horas;
- rechazo a 48 horas + 1 segundo;
- filtros y acceso por roles;
- historial sin edición;
- tablero y porcentaje de cierre;
- caso con cero incidencias.

## Tres pruebas de integración pedidas por el examen

Además de otras pruebas que también usan SQLite real de test, el archivo `tests/test_integration_flows.py` contiene los tres recorridos completos indicados por la guía:

1. **INT-01:** registrar → asignar → iniciar → proponer → confirmar.
2. **INT-02:** rechazo → nueva solución → confirmar.
3. **INT-03:** cierre → reapertura → nueva solución → nuevo cierre.

Cada prueba usa la aplicación Flask y una base SQLite temporal creada para ese caso.

## Datos independientes

Cada fixture crea una base nueva en un directorio temporal. Por eso una prueba no depende de los datos dejados por otra.

Los valores esperados se escriben desde las reglas de las SPECS. Por ejemplo:

- exactamente 48 h debe aceptar reapertura;
- 48 h + 1 s debe rechazarla;
- 1 cerrada de 4 reportes debe mostrar 25,0 %;
- prioridad enviada como NORMAL se ignora cuando la regla exige ALTA.

Esto ayuda a que la prueba no copie simplemente el mismo cálculo del código de producción.

## Regresión

La ejecución final vuelve a correr las pruebas de S01, S02, S03, S04 y S05. Si una modificación del cierre rompe una función anterior, el workflow falla y el PR no debe integrarse.
