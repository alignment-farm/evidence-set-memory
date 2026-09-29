# Reproduction paths

Run at repository root on macOS with `sandbox-exec`, uv and Python 3.12.14.
Pinned dependencies are phase-local: pytest 8.3.5, click 8.1.8, sh 2.2.2,
text-unidecode 1.3; full hashes in `uv.lock`. Root dependencies are unchanged.
No new fit is performed. `phase6/runs/acquisition/model.json` is the inherited
six-weight checkpoint, with exact replay and original costs documented in phase 6.

```sh
uv sync --project phase7 --frozen
uv run --project phase7 python scripts/phase7_fetch.py
uv run --project phase7 python scripts/phase7_publish.py verify
uv run --project phase7 python scripts/phase7_assets.py --out .cache/phase7/assets-reproduction-1
uv run --project phase7 python scripts/phase7_audit.py --out .cache/phase7/audit-reproduction-1
uv run --project phase7 python scripts/phase7_check_diagnosis.py --out .cache/phase7/check-reproduction-1
uv run --project phase7 python scripts/phase7_documentation_audit.py --out .cache/phase7/documentation-reproduction-1
uv run --project phase7 python scripts/phase7_finalize.py --out .cache/phase7/final-reproduction-1
```

The source fetch clones only when absent, then checks commits, every source-manifest
hash and licenses. Existing mismatches fail rather than being overwritten. All other
commands above use saved scientific artifacts and call no participant model. Output
directories must not exist; choose fresh suffixes. The initial containment preflight
and exact failing code are preserved at `73828ad`; repaired code/asset validation at
`f7bc7f9`. Publication hashes pin the final files; comparison hashes pin the code
before the later task file exists. Historical earlier-phase manifests include their
own README revisions and should be verified at their recorded commits.

Comparison freeze is `94bc951`; later task authorship is `368a61e`. The finalizer
replays the saved reviewed-repair patch with zero model calls and checks that only
the target docstring changes. Its cost supplement references archived original
runs, not newly sampled deployment. Documentation audit is post-hoc and preserves
the frozen executable grades; see `DOCUMENTATION_AUDIT.md` and `FINDINGS.md`.

For participant reruns, first verify the available model/digest and coordinate the
shared machine. The original uses the phase-6 DMR endpoint, tag, seed, temperature,
thinking-disabled request and 4096-token cap, with eight calls per attempt. Reported
local serving binary hash/build and tool versions are in `runtime.json`; hosted
backend identity is not independently attested. A rerun may vary despite the seed.

```sh
uv run --project phase7 python scripts/phase7_edit.py --out .cache/phase7/development-rerun-1
uv run --project phase7 python scripts/phase7_transfer.py transfer --out .cache/phase7/transfer-rerun-1
```

The separately declared post-hoc public-scope repair does call the reader once:

```sh
uv run --project phase7 python scripts/phase7_review_repair.py --out .cache/phase7/review-rerun-1
```

It continues the archived ordinary conversation, not a new rerun's conversation.
It is not part of the frozen comparison, and supplies investigator-authored public
requirement review rather than private-test feedback or a reference answer.

These independently replay the published comparisons using archived phase-6 weights
and accepted source history. They do not train from new rerun outcomes. Transfer
starts the new project from pinned upstream, then advances only from complete passing
attempts in ordinary/broad/empirical/energy order. Within each run, identical request
hashes share completions while retaining logical policy costs. Scratch code is saved
in each result; invalid JSON, unmatched edits, failed public tests and wrong scratch
expectations remain evidence, not silently retried outside the budget.

To rerun repository boundary tests with root's locked Torch dependencies:

```sh
uv sync --frozen
uv run python -m unittest discover -s scripts -p 'test_*.py' -v
```

The archived test result is under `runs/boundary-tests/`. Audit outputs separate
physical versus logical inference, initial source versus added reads, representation
and proposal timers, own-check submissions/retests, public repairs and final grading.
Preflight, mutation and replay costs are separate. Initial source history, retained
accepted tests/patches and the inherited learner survive process resets; temporary
edits, conversations and scratch checks do not survive into the next episode.

Upstream licenses in `assets-v2/` also cover source embedded in raw prompts and
canonical snapshots. Downloaded repositories, environments and case directories
are ignored caches. The task wording, added evaluators, chronology and diagnostic
mutation are explicitly study-authored. Investigator labor, machine energy and
network-transfer bytes are unknown, not zero.
