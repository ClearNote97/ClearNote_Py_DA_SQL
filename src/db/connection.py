"""Fábrica de engines SQLAlchemy por motor de base de datos.

Ejemplo **activo**: SQL Server (pyodbc). PostgreSQL y Oracle quedan como referencia comentada.
El código de conexión es *código*, por eso vive en `src/`; las consultas `.sql` viven en `data/sql/`.
Un engine por motor, con nombre propio (nunca un `get_engine()` genérico). PostgreSQL y
Oracle usan `URL.create()`; SQL Server no (ver `get_engine_mssql`).
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine  # noqa: F401 — URL lo usan los motores comentados de abajo

from src.config import config


def _odbc_value(value: object) -> str:
    """Cita un valor del string ODBC: `{…}` duplicando `}` (protege `;`, `}` y `=`)."""
    return "{" + str(value).replace("}", "}}") + "}"


def mssql_connection_string() -> str:
    """String ODBC exacto para SQL Server (función pura: testeable sin driver ni servidor).

    - Cada valor va citado `{…}` → una contraseña con `;`, `}`, `=` o `+` no rompe el string.
    - Sin `MSSQL_NAME` no se emite `DATABASE` → SQL Server usa la base **por defecto del login**
      (no "sin contexto"). Si esa base no es accesible verás *"Cannot open database"*: usa
      `MSSQL_NAME=master` para explorar el servidor.
    - `Encrypt`/`TrustServerCertificate` salen de config (con Driver 18, sin
      `TrustServerCertificate=yes` contra un cert autofirmado la conexión rompe por TLS).
    """
    server = config.MSSQL_HOST + (f",{config.MSSQL_PORT}" if config.MSSQL_PORT else "")
    parts = [
        f"DRIVER={_odbc_value(config.MSSQL_DRIVER)}",
        f"SERVER={server}",
        f"UID={_odbc_value(config.MSSQL_USER)}",
        f"PWD={_odbc_value(config.MSSQL_PASSWORD)}",
    ]
    if config.MSSQL_NAME:
        parts.append(f"DATABASE={_odbc_value(config.MSSQL_NAME)}")
    if config.MSSQL_ENCRYPT:
        parts.append(f"Encrypt={config.MSSQL_ENCRYPT}")
    if config.MSSQL_TRUST_CERT:
        parts.append(f"TrustServerCertificate={config.MSSQL_TRUST_CERT}")
    return ";".join(parts)


def get_engine_mssql() -> Engine:
    """Crea el engine de SQL Server entregándole a pyodbc el string ODBC EXACTO.

    Por qué `creator=` y no `URL.create(...)` ni `odbc_connect`:
    - `URL.create(host=..., database=None|"")` cae en la heurística DSN de `mssql+pyodbc`
      (`"host" in keys and "database" not in keys`): renderiza `dsn=<host>`, descarta el
      `DRIVER=` y falla con **IM002** cuando no hay base.
    - `odbc_connect` depende de cómo cada versión de SQLAlchemy procesa el valor (2.0 le
      aplica `unquote_plus` y un `+` de la contraseña se vuelve espacio; 2.1 ya no).
    Con `creator`, SQLAlchemy nunca toca el string: sigue manejando el pool y `pd.read_sql`,
    pero pyodbc recibe exactamente lo que arma `mssql_connection_string()`, en cualquier versión.
    """
    import pyodbc  # aquí y no arriba: el string se puede testear sin el driver instalado

    conn_str = mssql_connection_string()
    return create_engine("mssql+pyodbc://", creator=lambda: pyodbc.connect(conn_str))


# ---------------------------------------------------------------------------
# OTROS MOTORES (referencia). Para usar uno: descomenta su función, instala el
# driver (requirements.txt), agrega su grupo de variables en config.py + .env,
# y —si aplica— sus system deps en .devcontainer/Dockerfile.
# ---------------------------------------------------------------------------

# PostgreSQL — dialecto "postgresql+psycopg"; paquete: "psycopg[binary]" (uv add / requirements.txt)
# def get_engine_postgres() -> Engine:
#     url = URL.create(
#         "postgresql+psycopg",
#         username=config.PG_USER,
#         password=config.PG_PASSWORD,
#         host=config.PG_HOST,
#         port=config.PG_PORT,       # opcional
#         database=config.PG_NAME,   # opcional
#     )
#     return create_engine(url)
#
# PostgreSQL por TÚNEL SSH (conexión indirecta): ver README_AGENTS §11 Caso B.
# Se abre el túnel antes de crear el engine y se devuelve (engine, tunnel);
# hay que llamar tunnel.stop() al terminar. Se mantiene comentado a propósito:
# por defecto usamos conexión DIRECTA.

# Oracle — dialecto "oracle+oracledb"; paquete: "oracledb" (uv add / requirements.txt); modo "thin" no requiere Instant Client
# def get_engine_oracle() -> Engine:
#     url = URL.create(
#         "oracle+oracledb",
#         username=config.ORACLE_USER,
#         password=config.ORACLE_PASSWORD,
#         host=config.ORACLE_HOST,
#         port=config.ORACLE_PORT,
#         database=config.ORACLE_NAME,   # service_name / SID según tu caso
#     )
#     return create_engine(url)
