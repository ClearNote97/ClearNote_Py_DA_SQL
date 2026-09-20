# src/ — Código del proyecto

Código Python del análisis con acceso a SQL. Separado por responsabilidad:

| Carpeta | Rol |
|---|---|
| `config/` | Carga de credenciales/parámetros desde `.env` (prefijo por motor, p. ej. `MSSQL_`). |
| `db/` | Fábrica de engines **SQLAlchemy** por motor (`get_engine_mssql()`, …). |
| `pipelines/` | Flujos de extracción/transformación/carga y de análisis. |
| `utils/` | Utilidades transversales (limpieza, formateo) sobre **pandas**. |
