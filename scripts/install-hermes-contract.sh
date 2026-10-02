#!/usr/bin/env bash
# Install a Hermes checkout so contract tests can import it.
#
# Hermes rejects wheel and sdist builds. Editable installs are the supported
# development path and do not build those artifacts. Its core dependencies are
# marked for Python >= 3.14 and are not required to import the provider ABCs.
# hermes_cli.config imports hermes_yaml, which needs the ruamel.yaml pin from
# this checkout. That pin is also marked for Python >= 3.14, so install it
# explicitly on every interpreter under test.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="${HERMES_SRC:-"$root/hermes-agent"}"

if [[ ! -f "$src/pyproject.toml" ]]; then
  echo "Hermes checkout not found at $src" >&2
  echo "Clone https://github.com/NousResearch/hermes-agent (branch main) there, or set HERMES_SRC." >&2
  exit 1
fi

cd "$root"

pin="$(
  uv run --no-sync python - "$src/pyproject.toml" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
pins = sorted(set(re.findall(r"ruamel\.yaml==([^\"\s;]+)", text)))
if len(pins) != 1:
    raise SystemExit(f"expected one ruamel.yaml pin in {sys.argv[1]}, found {pins}")
print(pins[0])
PY
)"

uv pip install -e "$src" --no-deps
uv pip install "ruamel.yaml==${pin}"
