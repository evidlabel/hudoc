#!/usr/bin/env sh
# One-document live query against the ECHR HUDOC feed.
set -eu
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$root"
uv run hudoc latest -s echr -l 1 -n 1 -o examples/latest_out --plain true
