# Phase 5 reproduction

Run from this repository with `uv`; the existing `uv.lock` pins Python packages.
Use CPython 3.12.14 for exact native module identity. No remote serving, downloads
or credentials are required once the locked environment exists. All output paths
are write-once; choose unused directories rather than overwriting published runs.

```sh
uv run python -m unittest discover -s scripts -p 'test_*.py' -v
uv run python scripts/phase5_audit.py --out .cache/phase5-audit-replay --retrain
uv run python scripts/phase5_config.py confirm --out .cache/phase5-confirmation-replay
uv run python scripts/phase5_optimizer_diagnosis.py --out .cache/phase5-optimizer-replay
uv run python scripts/phase5_restore_sources.py --out .cache/phase5-source-replay
uv run python scripts/phase5_manifest.py
```

The confirmation command first verifies every frozen file hash, then regenerates
the same fresh material. Replays are not new fresh observations. Timings and
provenance timestamps differ; selected IDs, outputs and CPU-trained weights are
deterministic on the checked host. The audit reexecutes feedback/outcomes and
relearns all five saved checkpoints, asserting bit-identical coefficients.

Development algorithms can also be rerun with the final harness:

```sh
uv run python scripts/phase5_config.py develop --out .cache/phase5-development-replay
uv run python scripts/phase5_config.py refit --out .cache/phase5-balanced-replay --development phase5/runs/development
uv run python scripts/phase5_config.py compact --out .cache/phase5-constraint-replay --development phase5/runs/development
```

The final harness optimizes away unnecessary dependency-graph construction on
cache hits/full-context execution and fixes the relative-path serialization bug.
Therefore it does not reproduce those earlier bookkeeping timings or the failed
exit condition. Do not substitute new timing outputs for the saved historical runs.
To inspect the exact earlier bytes, use the source-restoration command; it verifies
each reconstructed file against the hash captured at execution. It does not alter
the worktree. Historical scripts assume their original repository `ROOT`; if
executing relocated restored modules, explicitly set their module `ROOT` to the
study root, or use the corresponding Git revision in a separate worktree.

Exact revisions:

- `f9959c3`: initial protocol, unbalanced two-representation development, code and
  outputs. Implementation SHA `9110c73785273e5e05f354d1bd878dc2bb32dfa70cf0bbb97717f162cc980a79`.
- `d263f86`: balanced refit and preserved relative-path bookkeeping failure.
  Implementation SHA `3c7da4af6fa8cfe4f99c4146aca8a22ef44c3bfb01260560504b4e546c51ff36`.
- Intermediate constraint-energy source SHA
  `91ad249437ed2a3211693433b29fb0131f6da0f121005b7d5ad9e7589359c93d`;
  balanced-final source SHA
  `8677985fbcb6a86cb2a14741c642b23c730934f87834d8cdcb237d75c3616db8`.
  Both were run between Git checkpoints; their exact source bytes are recoverable
  by the checked transformation script, not mislabeled as committed-at-run versions.
- `f8651b89a9ce7eb4301c363e7156a9e22348af2c`: frozen protocol, claim, models,
  implementation, tests, longer-chain constructor and freeze manifest before
  confirmation generation. Frozen implementation SHA
  `6e5bfa985cf1f8aa87806f6a0fe27022515c0d3dffe6ce9c64d33671dc670b00`.

`phase5/manifest.json` covers the local phase publication and associated scripts.
Phase-1 and phases-2–4 manifests remain records of their original publication
commits, not of later README edits. The native-cost ledger keeps experimental work
separate from audit replays and uninstrumented investigator/authoring overhead.
