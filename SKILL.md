---
name: hudoc
description: Use when the user wants to download documents from HUDOC subsites (ECHR, GREVIO, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA, COMMHR) — either from a saved RSS feed file or by fetching the latest documents directly from a subsite. Also use when inspecting an RSS feed's contents.
---

# hudoc

HUDOC subsite documents from a saved RSS feed or `latest`. Fetches only.

## Rules
- Verbatim — never retype judgment text.
- Schema: `hudoc -j` / `hudoc <path> -h`.
- Commands: `download`, `list`, `latest`. `--limit 0` = the entire feed; be deliberate with `-n`.
- Missing from PATH → install first (below).

## Feeds
Portals: `https://hudoc.<subsite>.coe.int/eng` for `commhr` `cpt` `ecri` `ecrml` `esc` `exec` `fcnm` `greco` `greta` `grevio` `echr`.

Search on the portal → **RSS** → save → `hudoc download <file>`. Or `hudoc latest -s <subsite>` (default feed, no portal). Quick live check: `sh examples/latest.sh`.

## Into the case's evidence set

```bash
hudoc download <feed.xml> -o hudoc_out            # per-doc <uuid>/label.typ + info.yml
cp -r hudoc_out/<uuid> evid/sets/<slug>/docs/     # copy into the case set
evid --db evid doc list -s <slug>                 # confirm the doc is in the set
```

Every evid command runs as `evid --db evid`, from the case root. Bare `evid` writes to `~/.local/share/evid`.

## Install

`uv tool install git+https://github.com/evidlabel/hudoc.git`

## Done
- Downloaded documents appear in `evid --db evid doc list -s <slug>`.
- No judgment text was retyped.
