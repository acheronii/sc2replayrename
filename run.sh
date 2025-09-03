set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Renaming eu First:"
uv --project "$SCRIPT_DIR" run "$SCRIPT_DIR/renaming.py" -s eu
echo "====================================="
echo "Renaming na Next:"
uv --project "$SCRIPT_DIR" run "$SCRIPT_DIR/renaming.py" -s na
