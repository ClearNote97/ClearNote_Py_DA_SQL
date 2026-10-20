# src/db — Conexión a bases de datos

Fábrica de engines **SQLAlchemy**, **un engine por motor** con nombre propio (`get_engine_mssql()`;
PostgreSQL/Oracle comentados). SQL Server le entrega a pyodbc el string ODBC exacto con `creator=` (evita el
`IM002` sin base y no depende de la versión de SQLAlchemy); PostgreSQL y Oracle, `URL.create()`. Las consultas `.sql` viven en `data/sql/`,
no aquí. Ver la sección "Conexión a SQL" del README (incluye solución de problemas).
