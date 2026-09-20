"""Fábrica de engines SQLAlchemy por motor de base de datos.

Ejemplo **activo**: SQL Server (pyodbc). PostgreSQL y Oracle quedan como referencia comentada.
El código de conexión es *código*, por eso vive en `src/`; las consultas `.sql` viven en `data/sql/`.
Un engine por motor, con nombre propio (nunca un `get_engine()` genérico).
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine

from src.config import config


def get_engine_mssql() -> Engine:
    """Crea el engine de SQL Server (pyodbc) usando `URL.create()`.

    `URL.create()` escapa solo usuario/contraseña/parámetros (sin `quote_plus` manual).
    `MSSQL_NAME` y `MSSQL_PORT` son **opcionales** (None → se omiten).

    ⚠️ SIN base de datos (`MSSQL_NAME` vacío): SQL Server **no** queda "sin contexto" —
    conecta a la base **POR DEFECTO** del login. Si esa default no es accesible, verás
    *"Cannot open database"*. Para explorar el servidor sin fijar una base, apunta a
    `master` (todo login suele poder abrirla): pon `MSSQL_NAME=master`.

    `Encrypt`/`TrustServerCertificate` salen de config (clave con Driver 18: sin
    `TrustServerCertificate=yes` contra un cert autofirmado, la conexión rompe con error TLS).
    """
    query = {"driver": config.MSSQL_DRIVER}
    if config.MSSQL_ENCRYPT:
        query["Encrypt"] = config.MSSQL_ENCRYPT
    if config.MSSQL_TRUST_CERT:
        query["TrustServerCertificate"] = config.MSSQL_TRUST_CERT
    url = URL.create(
        "mssql+pyodbc",
        username=config.MSSQL_USER,
        password=config.MSSQL_PASSWORD,
        host=config.MSSQL_HOST,
        port=config.MSSQL_PORT,
        database=config.MSSQL_NAME,   # None → base por defecto del login
        query=query,
    )
    return create_engine(url)


# --- Escape hatch: "funciona en pyodbc pero no vía URL.create" ----------------
# Si algún driver/param quisquilloso solo funciona con el string crudo de pyodbc,
# construye el string ODBC EXACTO y entrégalo por `odbc_connect`: sigues en SQLAlchemy
# (create_engine, pooling, ORM) — solo controlas el string byte a byte, no abandonas SQLAlchemy.
# def get_engine_mssql_odbc() -> Engine:
#     parts = [
#         f"DRIVER={{{config.MSSQL_DRIVER}}}",
#         "SERVER=" + config.MSSQL_HOST + (f",{config.MSSQL_PORT}" if config.MSSQL_PORT else ""),
#         f"UID={config.MSSQL_USER}",
#         f"PWD={config.MSSQL_PASSWORD}",
#         "Encrypt=yes",
#         "TrustServerCertificate=yes",
#     ]
#     if config.MSSQL_NAME:                       # omitir DATABASE = base por defecto del login
#         parts.append(f"DATABASE={config.MSSQL_NAME}")
#     return create_engine(URL.create("mssql+pyodbc", query={"odbc_connect": ";".join(parts)}))


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
