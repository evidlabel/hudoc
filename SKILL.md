---
name: hudoc
description: Use when the user wants to download documents from HUDOC subsites (ECHR, GREVIO, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA, COMMHR) — either from a saved RSS feed file or by fetching the latest documents directly from a subsite. Also use when inspecting an RSS feed's contents.
---

# hudoc

HUDOC subsite docs from a saved RSS feed or `latest`. Fetches only.

## Prior
- verbatim — never retype judgment text
- cite via **evid** (`doc add` → label → `set gather`) or **precise-quoter** on `--plain` text
- schema → `hudoc -j` / `hudoc <path> -h`
- source: <https://github.com/evidlabel/hudoc> — `uv tool install git+https://github.com/evidlabel/hudoc.git` or `uv run manage.py install`. Missing from `PATH` → point the user there first

## Downstream

| Goal | Chain |
|---|---|
| Labelled set | `hudoc download … -o dir` (default) → per-doc `<uuid>/label.typ` + `info.yml` → evid `docs/<uuid>/` → `evid doc label` → `evid set gather` |
| One-off quote | `hudoc download\|latest … --plain true -o dir` → `{subsite}_doc_*.txt` → `source_slug.py` on the HUDOC URL → `docs/<slug>.txt` → **precise-quoter** |

## Feeds
Portals: `https://hudoc.<subsite>.coe.int/eng` for `commhr` `cpt` `ecri` `ecrml` `esc` `exec` `fcnm` `greco` `greta` `grevio` `echr`.

Search on the portal → **RSS** → save → `hudoc download <file>`. Or `hudoc latest -s <subsite>` (default feed, no portal). Tiny live check: `sh examples/latest.sh`.

Leaves: `download` `list` `latest`. `--limit 0` = entire feed — be deliberate with `-n`.
