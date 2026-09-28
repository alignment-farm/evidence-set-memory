The executed reader implementation is preserved in
`scripts/snapshots/phase2_reader-v1.py`. Its costs.json computed the code hash at
process completion, after the source file had been revised for the next run.
Therefore that single code-hash field describes the later on-disk revision, not
the executing process. Raw request/response files are the authoritative executed
prompt evidence. New reader revisions capture their source hash at import time.

This first run used source-only no-context instructions and max_tokens=256,
without response_format. Several responses ignored the JSON instruction and hit
the output limit while explaining their answer. Preserve these acquisition/
reader failures. The next development run adds JSON-object response formatting
and a 512-token cap; it is a declared reader intervention before confirmation.
No successful completion or improved retrieval claim is inferred from this fix.
