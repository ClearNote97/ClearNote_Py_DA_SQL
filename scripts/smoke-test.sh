#!/usr/bin/env bash
# =============================================================================
# smoke-test.sh — ¿Está sano el proyecto? Rápido, sin red, no modifica nada.
# =============================================================================
#   Uso:  bash scripts/smoke-test.sh
#
# Corre en el host o dentro del devcontainer. Lo invoca init.sh (vía el postCreateCommand) al final
# (sin bloquear) y es parte del ritual de arranque (README_AGENTS §3). No se conecta a
# ninguna base: el guard de SQL Server revisa el string ODBC que se le entregaría al driver.
#
# Salida: ✅ ok · ⚠️ aviso (no falla) · ❌ falla (exit 1).
# =============================================================================
set -uo pipefail
cd "$(dirname "$0")/.."

pass=0; warn=0; fail=0
ok() { echo "  ✅ $*"; pass=$((pass + 1)); }
wa() { echo "  ⚠️  $*"; warn=$((warn + 1)); }
ko() { echo "  ❌ $*"; fail=$((fail + 1)); }
env_get() { grep -E "^$1=" "$2" 2>/dev/null | cut -d= -f2- | sed 's/#.*//' | tr -d '[:space:]'; }

# Intérprete: el .venv del proyecto si existe (dentro del contenedor tras uv sync).
PY=""
for c in .venv/bin/python python3 python; do
  command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }
done

echo "▶ smoke-test — $(basename "$PWD")"

# --- 1. Configuración ----------------------------------------------------------
echo "· Configuración"
if [ -f .env ]; then
  host="$(env_get MSSQL_HOST .env)"
  if [ -z "$host" ] || [ "$host" = "tu_host" ]; then
    wa "MSSQL_HOST sin configurar en .env (aún no hay a qué conectarse)"
  else
    ok ".env presente (MSSQL_HOST=$host)"
  fi
else
  wa ".env aún no existe → cp .env.example .env y completa las credenciales"
fi
if grep -qE '"name": *"clearnote' .devcontainer/devcontainer.json 2>/dev/null; then
  wa "devcontainer.json trae un nombre fijo de plantilla (debería tomar el de la carpeta)"
fi

# --- 2. Sintaxis ----------------------------------------------------------------
echo "· Sintaxis"
bad=0
for f in scripts/*.sh; do
  [ -f "$f" ] || continue
  bash -n "$f" 2>/dev/null || { ko "bash: $f"; bad=1; }
done
[ "$bad" = 0 ] && ok "scripts bash"

if [ -n "$PY" ]; then
  # ast.parse no escribe __pycache__ (py_compile sí).
  if out="$(find src scripts notebooks -name '*.py' -print0 2>/dev/null | xargs -0 "$PY" -c '
import ast, sys
for f in sys.argv[1:]:
    try:
        ast.parse(open(f, encoding="utf-8").read(), f)
    except SyntaxError as e:
        print(f"{f}:{e.lineno}: {e.msg}")
' 2>&1)" && [ -z "$out" ]; then
    ok "código Python"
  else
    ko "Python con errores de sintaxis:"; echo "$out" | sed 's/^/       /'
  fi
else
  wa "sin intérprete Python → se omite la sintaxis"
fi

# --- 3. Guard de conexión SQL Server (sin conectarse, sin dependencias) -------
# Extrae con ast el armado del string ODBC (función pura) y lo prueba con una config de
# ensayo: sin base no emite DATABASE (→ base por defecto del login) y una contraseña con
# + ; } llega intacta. Además verifica que get_engine_mssql entregue el string con
# creator= (no URL.create, que sin base cae en modo DSN → IM002).
echo "· Conexión SQL Server (sin conectarse)"
if [ -n "$PY" ] && [ -f src/db/connection.py ]; then
  if out="$("$PY" - <<'PY' 2>&1
import __future__, ast
src = open("src/db/connection.py", encoding="utf-8").read()
tree = ast.parse(src)
fns = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
for name in ("_odbc_value", "mssql_connection_string", "get_engine_mssql"):
    assert name in fns, f"falta {name}() en src/db/connection.py"
uses_creator = any(isinstance(n, ast.keyword) and n.arg == "creator" for n in ast.walk(fns["get_engine_mssql"]))
assert uses_creator, "get_engine_mssql ya no usa creator= (¿volvió a URL.create? → IM002 sin base)"
ns = {}
code = compile(ast.Module(body=[fns["_odbc_value"], fns["mssql_connection_string"]], type_ignores=[]),
               "connection.py", "exec", flags=__future__.annotations.compiler_flag, dont_inherit=True)
exec(code, ns)
class Cfg:
    MSSQL_HOST, MSSQL_USER, MSSQL_PASSWORD = "10.0.0.5", "u", "p+x;y}"
    MSSQL_DRIVER, MSSQL_NAME, MSSQL_PORT = "ODBC Driver 17 for SQL Server", None, None
    MSSQL_ENCRYPT = MSSQL_TRUST_CERT = None
ns["config"] = Cfg
s = ns["mssql_connection_string"]()
assert s.startswith("DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.0.0.5;"), f"inicio inesperado: {s}"
assert "PWD={p+x;y}}}" in s, f"la contraseña no llegó intacta: {s}"
assert "DATABASE" not in s.upper(), f"sin MSSQL_NAME no debe fijar base: {s}"
Cfg.MSSQL_NAME, Cfg.MSSQL_PORT = "Ventas", 1433
s = ns["mssql_connection_string"]()
assert "SERVER=10.0.0.5,1433;" in s and s.endswith("DATABASE={Ventas}"), f"con base/puerto: {s}"
PY
  )"; then
    ok "string ODBC correcto (sin base → default del login; + ; } intactos) · engine vía creator="
  else
    ko "conexión SQL Server rota:"; echo "$out" | tail -1 | sed 's/^/       /'
  fi
else
  wa "sin Python o sin src/db/connection.py → se omite el guard de conexión"
fi

# --- Resumen ----------------------------------------------------------------
echo "▶ $pass ok · $warn avisos · $fail fallas"
[ "$fail" -eq 0 ]
