# Knowledge-base validation results

Measured on 2026-10-18 by running `python3 eval/validate_kb.py index.html`
(Python 3, no dependencies). Reproduce: clone the repo and run the same command.

```
index.html: index.html (2,029,190 bytes)
esidx entries (ES keyword|material -> code): 95
matidx entries (EN keyword|material -> code): 24
tdict headings: 69
cndata text rows: 1,146
TARIC snapshot: 16,632 declarable 10-digit codes (9,791 distinct 8-digit prefixes)
snapshot date: 2026-10-01 | source: TARIC oficial UE (DG TAXUD, DDS2 ec.europa.eu/taxation_customs/dds2/taric)
[esidx] 95 codes checked -> 95 OK, 0 malformed, 0 without an 8-digit prefix in the snapshot
[matidx] 24 codes checked -> 24 OK, 0 malformed, 0 without an 8-digit prefix in the snapshot
[tdict] 69 headings -> 0 not 4-digit
[cndata] 0 empty rows
RESULT: PASS - all embedded knowledge bases are internally consistent
```

What this measures: every code the app can suggest from its evidence bases
(119 in total) is well-formed and backed by an existing 8-digit heading in the
embedded TARIC snapshot (16,632 declarable codes, DG TAXUD, 2026-10-01).
It does not measure classification accuracy on real invoices - that needs
human-reviewed clearances, which are not public.
