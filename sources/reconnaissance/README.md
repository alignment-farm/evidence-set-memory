# Public-asset reconnaissance records

The study-root [FEASIBILITY.md](../../FEASIBILITY.md) states findings, limits,
versions, provenance, costs and reproduction commands. This folder contains
small evidence records; upstream source/data snapshots are ignored under
`.cache/reconnaissance/`.

- `fetch-manifest.json`: pinned repository URLs/commits and exact per-file URLs,
  byte sizes, SHA-256 values, plus the bounded MuSiQue streaming procedure.
- `downloaded-file-hashes.json`: hashes of all original 57 snapshot files. One
  historical HTTP-header capture is not a reconstructible asset; it stays in
  the cache and is excluded from the 56-file fetch manifest.
- `cache-verification.json`: copied-cache verification, including all 57
  original files and zero newly downloaded bytes during packaging.
- `check-results.json`: valid combined JSON from `scripts/check_assets.py`.
- `original-check-results.txt`: the original inspection's concatenated JSON
  outputs, retained as text rather than represented as one JSON document.
- `serbench-summary.json`: Cal500 field, state-type, group and candidate audit.
- `serbench-interaction-audit.json`: exact minimum certified set sizes and
  recorded trajectory run/timestamp checks.
- `serbench-test-summary.json`: released Test500 inference fields and counts;
  no private labels were acquired or loaded.
- `serbench-hash-checks.json`: original six released-file checks against the
  publisher's compressed and uncompressed manifest hashes.

Run `uv run --no-project python scripts/fetch_assets.py --verify-only` and
`uv run --no-project python scripts/check_assets.py` from the study root.
Omit `--verify-only` to fetch missing manifest assets. Scripts emit valid JSON.
No model runs or private evaluation submissions are part of these commands.
The Google Drive source is mutable: a changed sample fails its recorded hash.

Scorer self-consistency and asset availability are not treatment performance.
SERBench's supplied-candidate certificates and MuSiQue's QA labels are distinct
from evidence earned through continuing agent sessions. Neither inspected
release provides that continuing workload. The report's downstream utility
controls are useful diagnostics; workload construction and EBM acquisition may
proceed concurrently without requiring a treatment win.
