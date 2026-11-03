---
name: hudoc
description: Use when the user wants documents from HUDOC subsites (ECHR, GREVIO, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA, COMMHR) — text from a saved RSS feed or the latest feed for searching, or the official PDF of a judgment to key in evid. Also use when inspecting an RSS feed's contents.
---

# hudoc

HUDOC subsite documents from a saved RSS feed or `latest`: text for searching, PDFs for keying.

## Rules
- Verbatim — never retype judgment text.
- Schema: `hudoc -j` / `hudoc <path> -h`.
- Commands: `download`, `list`, `latest`, `pdf`. `--limit 0` = the entire feed.
- One request at a time, 3 s apart (`--delay`, `--threads` default 1).
- The text output is for searching. It has the judgment's words but no pages.
  A quote is keyed in the official PDF.
- Fetches go through the `curl` binary; it must be on PATH.
  HUDOC's Cloudflare answers python-requests with a 403 challenge, but serves curl.
- If curl gets a challenge page too, hudoc saves nothing.
  Then open the documents in a browser and add the saved PDFs.
  Don't try to get around the challenge.
- Missing from PATH → install first (below).

## Feeds
Portals: `https://hudoc.<subsite>.coe.int/eng` for `commhr` `cpt` `ecri` `ecrml` `esc` `exec` `fcnm` `greco` `greta` `grevio` `echr`.

Search on the portal → **RSS** → save → `hudoc download <file>`. Or `hudoc latest -s <subsite>` (default feed, no portal). Quick live check: `sh examples/latest.sh`.

## Into the case's evidence set

Key the official PDF, so quotes get page pinpoints:

```bash
hudoc pdf <itemid> -o pdf --set <slug>            # saves pdf/echr_<itemid>.pdf, prints its evid line
evid --db evid doc add -s <slug> pdf/echr_<itemid>.pdf
hudoc download <feed.xml> --pdf -o pdf --set <slug>  # the same, for every item in a feed
evid --db evid doc list -s <slug>                 # confirm the doc is in the set
```

- A saved file always starts with `%PDF`; anything else is refused.
- HUDOC answers 204, and hudoc exits 1, for an item id it does not have.
  Press releases (`003-…`) give 204 on the text route.
- A PDF added from a file has an empty `url`.
  Set it in the document's `info.yml` from `hudoc pdf <itemid> --urls`.

Every evid command runs as `evid --db evid`, from the case root. Bare `evid` writes to `~/.local/share/evid`.

## Install

`uv tool install git+https://github.com/evidlabel/hudoc.git`

## Done
- The keyed PDFs appear in `evid --db evid doc list -s <slug>`.
- No judgment text was retyped.
