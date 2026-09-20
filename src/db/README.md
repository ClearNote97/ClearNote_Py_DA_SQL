# src/db — Conexión a bases de datos

Fábrica de engines **SQLAlchemy** con `URL.create()`, **un engine por motor** con nombre propio
(`get_engine_mssql()`; PostgreSQL/Oracle comentados). Las consultas `.sql` viven en `data/sql/`,
no aquí. Ver la sección "Conexión a SQL" del README (incluye solución de problemas).
