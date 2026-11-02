---
name: hudoc
description: Use when the user wants documents from HUDOC subsites (ECHR, GREVIO, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA, COMMHR) — text from a saved RSS feed or the latest feed for searching, or the official PDF URL of a judgment to key in evid. Also use when inspecting an RSS feed's contents.
---

# hudoc

HUDOC subsite documents from a saved RSS feed or `latest`: text for searching, PDF URLs for keying.

## Rules
- Verbatim — never retype judgment text.
- Schema: `hudoc -j` / `hudoc <path> -h`.
- Commands: `download`, `list`, `latest`, `pdf`. `--limit 0` = the entire feed.
- One request at a time, 3 s apart (`--delay`, `--threads` default 1).
- The text output is for searching. It has the judgment's words but no pages.
  A quote is keyed in the official PDF.
- HUDOC can answer a script with a JavaScript challenge page (Cloudflare, 403).
  Then hudoc gets nothing. Open the documents in a browser instead.
  Don't try to get around the challenge.
- Missing from PATH → install first (below).

## Feeds
Portals: `https://hudoc.<subsite>.coe.int/eng` for `commhr` `cpt` `ecri` `ecrml` `esc` `exec` `fcnm` `greco` `greta` `grevio` `echr`.

Search on the portal → **RSS** → save → `hudoc download <file>`. Or `hudoc latest -s <subsite>` (default feed, no portal). Quick live check: `sh examples/latest.sh`.

## Into the case's evidence set

Key the official PDF, so quotes get page pinpoints:

```bash
hudoc pdf <itemid> --set <slug>                   # prints: evid --db evid doc add -s <slug> "<pdf url>"
hudoc download <feed.xml> --pdf --set <slug>      # the same, for every item in a feed
evid --db evid doc list -s <slug>                 # confirm the doc is in the set
```

`hudoc pdf` prints URLs and fetches nothing.
Check that a fetched file starts with `%PDF`.

Every evid command runs as `evid --db evid`, from the case root. Bare `evid` writes to `~/.local/share/evid`.

## Install

`uv tool install git+https://github.com/evidlabel/hudoc.git`

## Done
- The keyed PDFs appear in `evid --db evid doc list -s <slug>`.
- No judgment text was retyped.
