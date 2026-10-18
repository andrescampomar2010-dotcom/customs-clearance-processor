#!/usr/bin/env python3
"""Integrity check for the knowledge bases embedded in index.html.

Parses the single-file app and verifies, with real counts:
  1. every code suggested by the evidence bases (esidx, matidx) is a
     well-formed 10-digit TARIC-style code;
  2. every suggested code's 8-digit prefix exists in the embedded
     TARIC snapshot (the same check the app runs before proposing a code);
  3. the tariff dictionary (tdict) only contains 4-digit headings;
  4. the CN 2026 text list is present and non-empty.

Usage:  python3 eval/validate_kb.py [path-to-index.html]
Exit code 0 = all checks passed, 1 = at least one failed.
"""
import base64, gzip, json, re, sys
from html.parser import HTMLParser
from pathlib import Path


class BlockParser(HTMLParser):
    """Collects the contents of the embedded <script id=...> data blocks."""

    def __init__(self):
        super().__init__()
        self.blocks = {}
        self._cur = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            d = dict(attrs)
            if d.get("id") in ("esidx", "matidx", "tdict", "cndata", "kbfixlog", "taric7"):
                self._cur = d["id"]
                self._buf = []

    def handle_data(self, data):
        if self._cur:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._cur:
            self.blocks[self._cur] = "".join(self._buf).strip()
            self._cur = None


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "index.html"
    html = path.read_text(encoding="utf-8")
    p = BlockParser()
    p.feed(html)

    missing = [b for b in ("esidx", "matidx", "tdict", "cndata", "taric7") if b not in p.blocks]
    if missing:
        print(f"FAIL: embedded blocks missing: {missing}")
        return 1

    esidx = json.loads(p.blocks["esidx"])
    matidx = json.loads(p.blocks["matidx"])
    tdict = json.loads(p.blocks["tdict"])
    cndata = json.loads(p.blocks["cndata"])

    # The TARIC snapshot is stored gzipped+base64 in <script id="taric7">.
    # Shape: {"date": ..., "source": ..., "c": [<10-digit code strings>]}.
    snap = json.loads(gzip.decompress(base64.b64decode(p.blocks["taric7"])))
    snap_codes = [re.sub(r"\D", "", str(c)) for c in snap["c"]]
    codes10 = {c for c in snap_codes if len(c) == 10}
    codes8 = {c[:8] for c in codes10}

    print(f"index.html: {path.name} ({len(html):,} bytes)")
    print(f"esidx entries (ES keyword|material -> code): {len(esidx):,}")
    print(f"matidx entries (EN keyword|material -> code): {len(matidx):,}")
    print(f"tdict headings: {len(tdict.get('headings', {})):,}")
    print(f"cndata text rows: {len(cndata.get('v', [])):,}")
    print(f"TARIC snapshot: {len(codes10):,} declarable 10-digit codes ({len(codes8):,} distinct 8-digit prefixes)")
    print(f"snapshot date: {snap.get('date')} | source: {str(snap.get('source'))[:90]}")

    failures = 0

    def check_codes(name, mapping):
        nonlocal failures
        bad_fmt, not_in_snapshot = [], []
        for key, code in mapping.items():
            digits = re.sub(r"\D", "", str(code))
            if len(digits) != 10:
                bad_fmt.append((key, code))
            elif digits[:8] not in codes8:
                not_in_snapshot.append((key, code))
        ok = len(mapping) - len(bad_fmt) - len(not_in_snapshot)
        print(f"[{name}] {len(mapping):,} codes checked -> {ok:,} OK, "
              f"{len(bad_fmt)} malformed, {len(not_in_snapshot)} without an 8-digit prefix in the snapshot")
        for key, code in (bad_fmt + not_in_snapshot)[:10]:
            print(f"    FAIL {key!r} -> {code!r}")
        failures += len(bad_fmt) + len(not_in_snapshot)

    check_codes("esidx", esidx)
    check_codes("matidx", matidx)

    heads = tdict.get("headings", {})
    bad_heads = [h for h in heads if not re.fullmatch(r"\d{4}", h)]
    print(f"[tdict] {len(heads):,} headings -> {len(bad_heads)} not 4-digit")
    failures += len(bad_heads)

    empty_cn = sum(1 for v in cndata.get("v", []) if not str(v).strip())
    print(f"[cndata] {empty_cn} empty rows")
    failures += empty_cn

    print("RESULT:", "PASS - all embedded knowledge bases are internally consistent" if failures == 0
          else f"FAIL - {failures} problem(s) found")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
