# Public length-stop repair diagnostic

Declared while the fixed 24-case run is still executing (17 cases inspected for
format/finish status only). At that point the full-source arm has four length
stops and three parse failures; exact, unary and ordinary each have one length
stop/parse failure. The original frozen 1,024-token comparison remains primary
and immutable. Do not infer a general compact-context benefit from a potentially
binding output cap.

After that run finishes, retry **every unique request whose server finish reason
is `length`**, independent of answer correctness, support labels, method or parse
success. Keep model, messages, temperature, seed and all other payload fields;
raise only `max_tokens` to 4,096. Run serially, at most 24 additional unique calls
and no more than 300 cumulative calls across phase-2 development, confirmation
and this diagnostic. A 600-second transport timeout accommodates longer outputs;
two endpoint errors terminate the diagnostic without model substitution.

This is an equally available public repair policy, not a gold-triggered retry.
No label file is read until all eligible repairs have completed. Untruncated
requests retain their original response; identical repaired contexts reuse one
response. Apply the frozen parser and answer/citation grader. After this format/
budget repair, the original public abstention/invalid-citation fallback may use
the correspondingly repaired full-source output. Charge original calls, retries,
and fallback separately in native tokens and request counts. Do not add physically
reused fallback again to actual experiment totals.

Report original and repaired results side by side. This is **post-freeze reader
diagnosis on the same cases**, not a second fresh confirmation or a new independent
sample. It neither changes the trained energy/selected evidence nor establishes
continuing-memory acquisition. If a future deployment claim uses this policy,
it needs a fresh protocol/cohort. Preserve all truncated responses and all retries.
