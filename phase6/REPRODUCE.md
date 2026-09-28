# Reproducing phase 6

Run from the repository root. macOS `sandbox-exec` is required for native test
execution; no portability to Linux is claimed for this profile. Use `uv` and Python
3.12.14. Phase-local locked dependencies include pytest 8.3.5, click 8.1.8 and sh
2.2.2. Acquisition uses the unchanged root lock: PyTorch 2.14.0, NumPy 2.5.3,
CPU float64, two threads. Model serving does not supply gradient access.

Study implementation/claim freeze commit:
`fa9f5e7db94810f017baedec7851785d88e2623f`.
Initial executable pilot: `c72b45dba7cad6557295e330f64fc6c8363fdf5a`.
Development evidence: `da0b6a69e9c289f0bd16fffc13d6cb82c94ff83d`.
Final publication exact bytes are listed in `phase6/manifest.json`; previous
publication manifests remain scoped to their historical commits, not this README.

## Offline evidence verification

```sh
uv sync --project phase6 --frozen
uv sync --frozen
uv run --project phase6 python scripts/phase6_manifest.py
uv run --project phase6 python scripts/phase6_assets.py fetch
uv run --project phase6 python scripts/phase6_audit.py --out .cache/phase6/audit-reproduction-1
uv run --project phase6 python scripts/phase6_semantic_diagnosis.py --out .cache/phase6/semantic-reproduction-1
uv run python scripts/phase6_verify.py --out .cache/phase6/verification-reproduction-1
```

Only `assets.py fetch` needs source network access if the clone is absent. It checks
the upstream commit and all 39 file hashes. All output directories must be absent;
scripts refuse overwrites. Choose a fresh suffix on subsequent runs. The audit
rebuilds valid participant edits and runs original/current/prior tests without
calling a model. The verification refits the 12 archived development examples
and both leave-one-task-out fits, requires identical coefficients/loss traces,
and runs all 22 repository tests. Its cost supplement references the archived audit
and intervention rather than overwriting them. New timing values need not match.

Three initial sandbox preflights are preserved in `phase6/assets`: `/dev/null`
denial, pseudo-terminal denial, then the passing profile. Recover their exact source:

```sh
uv run --project phase6 python scripts/phase6_restore_preflight.py --out .cache/phase6/preflight-source-reproduction-1
```

The final pilot harness has an added unused default argument relative to the
passing preflight; the recovery script restores and hash-checks exact older bytes.

## Participant execution

Verify the available local model/digest and coordinate shared-machine use first.
The experiment used serial Docker Model Runner calls to
`https://mac-studio-7hr7.taile71f88.ts.net/engines/v1/chat/completions`, reported tag
`docker.io/ai/qwen3.8:27b-q4_K_M`, digest
`f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef`.
Raw response paths include `Qwen3.8-27B-UD-Q4_K_M.gguf`; architecture/quantization
are tag-reported, not independently validated. Backend build was not captured.
No model download, external paid participant API or upstream write is needed.

```sh
uv run --project phase6 python scripts/phase6_edit.py develop --out .cache/phase6/development-rerun-1
uv run --project phase6 python scripts/phase6_packaging.py --out .cache/phase6/packaging-rerun-1
uv run python scripts/phase6_energy.py --out .cache/phase6/acquisition-rerun-1
uv run --project phase6 python scripts/phase6_prompt.py --out .cache/phase6/interface-rerun-1
uv run --project phase6 python scripts/phase6_transfer.py transfer --out .cache/phase6/transfer-rerun-1
```

Important: packaging, acquisition, interface validation and transfer intentionally
reference the **archived canonical development history**, not arbitrary new rerun
paths. These commands independently replay the published comparisons/fit; they do
not automatically train a new experiment from newly sampled outcomes. A new chained
experiment requires an explicit separate study root and lineage, never overwriting
the evidence. Temperature/seed do not guarantee bit-identical serving across backend
versions. Archived payloads, request-hash caches, responses and patches are the exact
record; delivery-equal policies share physical completions within each run.

## Artifact map and interpretation

- `assets/`: upstream hashes, all preflights and resource metadata; BSD license in
  `UPSTREAM_LICENSE.txt` also covers upstream code embedded in archived requests.
- `runs/development`, `runs/packaging`: 12 learning attempts, failures and two accepted
  canonical source revisions, unchanged upstream tests recoverable from the clone.
- `runs/acquisition`: 12 derived feature/outcome examples, six weights, fit traces,
  30 pair preferences and two development diagnostic fits.
- `freeze.json`, `CLAIM.md`: exact frozen inputs and original claim. See the final
  findings' correction: later tasks were defined before freeze, after acquisition.
- `runs/interface-validation`: two delivery-identical development attempts, one call.
- `runs/transfer`: two later task definitions, eight attempts, two retention probes,
  raw calls, accepted API-extension source and explicit rejected newline history.
- `runs/semantic-diagnosis`: authored one-helper intervention and before/after tests;
  this does not become an accepted participant revision or acquisition label.
- `runs/audit`, `runs/verification`: grade/source replay, native costs, exact fit replay,
  boundary tests and missing-cost/chronology disclosures.

Each response records request wall time and reported usage, including prefix-cache
tokens. All attempts include explicit source reads, public repair and held-out
grading. Dollars, joules, investigator work and source/task authoring cost remain
unknown, not zero. The optional IPython skip is retained throughout.
