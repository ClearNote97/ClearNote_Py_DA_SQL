# `data/` — datos del proyecto

Raíz de los insumos de datos del análisis.

- **`sql/`** → el **catálogo de consultas** (`.sql`), y nada de código Python.
- **`other/`** → los **archivos de datos en formatos no-SQL** (`.csv`, `.parquet`, `.xlsx`, `.json`, …).
- El **diccionario de datos** no vive aquí, sino en `docs/`.

> **Una carga verde no es una carga buena.** Después de cada extracción o carga, valida **conteos y
> cobertura** (filas esperadas, columnas con datos, rango de fechas): una consulta que devuelve 0 filas
> "sin error" es una bandera roja, y un `try/except` que no explota no prueba nada. Antes de dar una
> fuente por lista, haz un **piloto con datos reales**, no solo con ejemplos de juguete.
