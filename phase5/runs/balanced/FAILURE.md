# Completed computation; failed provenance serialization

The balanced refit completed its 400 optimizer steps and all six policy
evaluations, writing model, outcomes and summary. It then failed before writing
`provenance.json`: a relative input path was passed to `Path.relative_to` against
an absolute repository root. This is a harness bookkeeping failure, not an
acquisition or task failure. Exit status 1; outputs are retained, not overwritten.

Executed `scripts/phase5_config.py` SHA-256:
`3c7da4af6fa8cfe4f99c4146aca8a22ef44c3bfb01260560504b4e546c51ff36`.
Invocation: `uv run python scripts/phase5_config.py refit --out
phase5/runs/balanced --development phase5/runs/development`.
Runtime/investigator settings unchanged from the immediately preceding development.
No external service, new feedback acquisition, or confirmation material was used.
The code's native relative-path bug will be fixed before the final freeze.

All policies completed 72/72. Exact trained selection uses 178 noncached records
against ordinary/relaxed selection's 170. Two old-valid requests each receive six
records instead of two. The resolved-edge reward attracts an irrelevant four-node
component. Next diagnostic removes that reward while retaining missing-dependency
interactions, and reuses the same executed development feedback. This is a changed
energy parameterization, not a different name for the same scorer.
