# Dev Container para análisis de datos en Python CON conexión a SQL.
# Ejemplo activo: SQL Server (pyodbc + ODBC Driver 17). PostgreSQL y Oracle: ver bloques comentados.

# ✅ Imagen base ligera de Python 3.14.5 sobre Debian ("bookworm" = Debian 12)
FROM python:3.14.5-slim-bookworm

# ⚙️ Evita mensajes interactivos durante instalaciones con apt
ENV DEBIAN_FRONTEND=noninteractive

# 🔧 Dependencias de sistema base + SQL Server (msodbcsql17).
# msodbcsql17 requiere unixodbc-dev. La clave del repo de Microsoft se instala con el método
# moderno de keyring: apt-key está DEPRECADO y removido en Debian 12 (bookworm).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        gnupg \
    && install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        unixodbc-dev \
        msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 🐘 (OPCIONAL) PostgreSQL — descomentar si te conectas a Postgres.
#   - Driver Python: "psycopg[binary]" (no necesita system deps).
#   - Solo si compilas psycopg desde fuente: libpq-dev.
# RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# 🅾️ (OPCIONAL) Oracle — descomentar si te conectas a Oracle.
#   - Driver Python: "oracledb". En modo "thin" (por defecto) NO necesita nada del sistema.
#   - Solo el modo "thick" requiere Oracle Instant Client (libaio1 + descarga del client).
# RUN apt-get update && apt-get install -y --no-install-recommends libaio1 \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*

# 🔒 (OPCIONAL) Conexión por TÚNEL SSH — ver README_AGENTS §11 Caso B (por defecto usamos conexión directa).
#   sshtunnel arrastra cryptography, que puede requerir compilar:
# RUN apt-get update && apt-get install -y --no-install-recommends libffi-dev libssl-dev \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*
#     # Si cryptography compila desde fuente, agrega también: rustc cargo

# ─────────────────────────────────────────────────────────────────────────────
# 🧰 (OPCIONAL) Paquetes del sistema que han pedido proyectos reales.
#    Descomenta solo lo que tu proyecto necesite. Lo que se instala a mano dentro del
#    contenedor se pierde al recrearlo; lo que vive aquí, no.
# ─────────────────────────────────────────────────────────────────────────────
# Excel con macros o conversión a PDF (LibreOffice sin interfaz + puente UNO, que usa el
# python3 del sistema, no el de esta imagen):
# RUN apt-get update && apt-get install -y --no-install-recommends libreoffice-calc python3-uno \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*
#
# Geoespacial (solo si alguna dependencia no trae wheel para tu versión de Python):
# RUN apt-get update && apt-get install -y --no-install-recommends \
#         gdal-bin libgdal-dev libgeos-dev libproj-dev ghostscript \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*
#
# Metadatos de fotos y video:
# RUN apt-get update && apt-get install -y --no-install-recommends libimage-exiftool-perl \
#     && apt-get clean && rm -rf /var/lib/apt/lists/*
#
# Binario externo FIJADO y VERIFICADO (patrón; ejemplo con rclone):
#   - versión = la release de seguridad vigente (búscala), no la que recuerdes;
#   - el ARG se llama PIN_<HERRAMIENTA>_VERSION: rclone lee las variables RCLONE_* como
#     opciones y un ARG RCLONE_VERSION rompe el build.
# ARG PIN_RCLONE_VERSION=vX.Y.Z
# RUN apt-get update && apt-get install -y --no-install-recommends curl unzip \
#     && curl -fsSLO "https://downloads.rclone.org/${PIN_RCLONE_VERSION}/rclone-${PIN_RCLONE_VERSION}-linux-amd64.zip" \
#     && curl -fsSL "https://downloads.rclone.org/${PIN_RCLONE_VERSION}/SHA256SUMS" \
#         | grep "rclone-${PIN_RCLONE_VERSION}-linux-amd64.zip" | sha256sum -c - \
#     && unzip -q "rclone-${PIN_RCLONE_VERSION}-linux-amd64.zip" \
#     && install -m 0755 "rclone-${PIN_RCLONE_VERSION}-linux-amd64/rclone" /usr/local/bin/ \
#     && rm -rf rclone-* && apt-get clean && rm -rf /var/lib/apt/lists/*

# 📦 Instalar uv desde la imagen oficial de Astral (versión fijada)
COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /uvx /bin/
