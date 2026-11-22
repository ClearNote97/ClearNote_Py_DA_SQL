#!/usr/bin/env bash
# =============================================================================
# init.sh — Deja el entorno LISTO para trabajar (idempotente).
# =============================================================================
# Lo dispara el `postCreateCommand` del devcontainer al crear el contenedor; también se
# puede correr a mano dentro del contenedor (p. ej. tras cambiar requirements.txt).
#
# Detecta el estado del proyecto (README_AGENTS §9) y actúa solo:
#   • pyproject.toml + uv.lock   → uv sync --locked      (Estado N: entorno idéntico)
#   • pyproject.toml sin uv.lock → uv lock && uv sync
#   • solo requirements.txt      → uv init + uv add -r    (Estado 0: genera pyproject.toml + uv.lock;
#                                                          commitéalos)
# Al final corre el smoke-test, que informa pero no bloquea.
#
# Vive en un archivo y no en una línea del devcontainer.json para poder leerlo, probarlo
# (`bash -n init.sh`) y crecer sin escapar comillas dentro de JSON.
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "✋ No encuentro uv. init.sh se corre DENTRO del contenedor (Reopen in Container)." >&2
  exit 1
fi

echo "▶ Dependencias (uv)"
if [ -f pyproject.toml ]; then
  if [ -f uv.lock ]; then
    uv sync --locked
  else
    uv lock && uv sync
  fi
elif [ -f requirements.txt ]; then
  uv init --no-package --no-workspace .
  rm -f main.py                       # el ejemplo que crea uv init no es del proyecto
  uv add -r requirements.txt
  echo "  ℹ️  Se generaron pyproject.toml y uv.lock: commitéalos (Estado 0 → N)."
else
  echo "✋ No se encontró ni pyproject.toml ni requirements.txt." >&2
  exit 1
fi

echo "▶ Salud del proyecto"
bash scripts/smoke-test.sh || echo "⚠️  smoke-test con hallazgos (no bloquea)"
