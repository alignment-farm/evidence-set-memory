# Reproducing the continuation

Use a scratch checkout for rebuilding downloaded representations: the frozen
encoder script writes new timing ledgers to `phase2/runs/encoding-*.json`.
Do not overwrite publication evidence in your working copy. All training and
selection output paths below are write-once; use new paths for additional runs.
No serving access is needed for training, selection, optimizer diagnostics or
offline regrading. Serving is needed only to obtain new primary-model responses.

## Assets and environment

```sh
uv sync --frozen
uv run --no-project python scripts/fetch_assets.py
uv run python scripts/phase2_assets.py --rebuild-cache
uv run python scripts/phase2_encode.py --split train
uv run python scripts/phase2_encode.py --split development
uv run python scripts/phase2_encode.py --split confirmation
```

Skip encoding for an already constructed cache; the script rejects existing
embedding files. Asset rebuilding validates the original data and partition
hashes. The source object is recoverable only if it still matches the recorded
hash. The encoder revision is pinned in `phase2/encoder.json`. Archive and weight
downloads are ignored by git. Public source attribution and all model/version
qualifications are in [PROVENANCE.md](PROVENANCE.md).

## Learned parameters and held-out selection

These are the paths used for the executed exact-replay audit:

```sh
uv run python scripts/phase2_energy.py train --semantic --seed 23 --out .cache/phase2/verification-training
uv run python scripts/phase2_energy.py evaluate --split confirmation --checkpoint phase2/runs/semantic-pairwise/checkpoint.json --unary-checkpoint phase2/runs/semantic-unary/checkpoint.json --ordinary-weight 1.0 --out .cache/phase2/verification-selection
uv run python scripts/phase3_scaling.py --out .cache/phase3-replay
uv run python scripts/phase4_relaxation.py --out .cache/phase4-replay
uv run python -m unittest discover -s scripts -p 'test_phase2_*.py'
```

The fixed ordinary policy is not retrained. To reproduce the unary specialist,
train with `--semantic --unary --seed 11` into another new output directory.
Lexical attempts omit `--semantic`; both pairwise seeds 11 and 23 and unary seed
11 were executed. Defaults are 60 epochs, with checkpoint selection on development.
The seed-11 initial size assertion failure is retained separately.

The phase-2 freeze hashes the methods, checkpoints and split manifests. It does
not certify novelty, absence of pretraining contamination, or source truth. See
[EXPOSURE.md](EXPOSURE.md) before treating the holdout as wholly uninspected.

## Complete QA and offline audit

```sh
uv run python scripts/phase2_reader.py --split confirmation --out .cache/new-reader --selection phase2/runs/confirmation-selection/outcomes.json --ordinary-arm ordinary_1.0 --limit 24
uv run python scripts/audit_continuation.py --out .cache/new-audit.json --require-reader
```

The separate post-freeze public length-stop diagnostic is:

```sh
uv run python scripts/phase2_reader_budget.py --out .cache/new-budget-diagnostic
```

It reads the completed **published** original run, not `.cache/new-reader`, and
opens evaluation labels only after collecting all public-triggered retries.
The published diagnostic is `phase2/runs/reader-budget-diagnostic`; the final
audit checks it when present. Its changed response cap is not part of the original
freeze and must not be relabeled as a fresh confirmation.

The audit checks the **published** `phase2/runs/confirmation-reader` raw responses,
not `.cache/new-reader`; independent new completions can differ despite requested
temperature zero and seed. Audit first requires the three verification paths
above. It verifies frozen file hashes, training/selection replay, split/exposure
boundaries, request hashes, raw-answer grading, fallback grading and cohort size.
It makes no endpoint calls. Every published request and raw response is retained,
including development failures; requests contain attributed benchmark source text.

The serving tag/digest, requested API options and observed interface failures
are documented in provenance. Coordinate use of the shared machine before new
serving. The reader issues serial calls and caches identical payloads. Logical
per-policy costs are not the same as the deduplicated physical experiment total.

Phase-1 publication is commit `ad01b74421d2297356ba92bd67584e1667cb4fdf`.
Phase-2 lexical development publication is `2c55bdf`; the semantic freeze and
phase-3 results are `dda88d9`; phase-4 results are `53f1d7f`. The final continuation
publication manifest will pin all current evidence without rewriting these
earlier publication boundaries.
