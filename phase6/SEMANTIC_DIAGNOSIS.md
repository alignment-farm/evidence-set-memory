# Post-freeze semantic diagnosis of line-ending selection

Declared after the ordinary transfer attempt closed with public-pass/held-out-fail,
while the other frozen policies continued unchanged. No diagnostic information is
passed to any participant and no frozen source/prompt/weight/grade is modified.

The ordinary patch's `_detect_line_ending` checks whether CRLF appears anywhere
before checking LF. The stated requirement instead asks for the first encountered
LF/CRLF style. This predicts its recorded failure when a leading LF precedes a
later CRLF. After the transfer run ends, reconstruct that failed patch in a new
isolated copy. Change **only** this helper to inspect the first LF and whether its
preceding character is CR. Rerun all upstream, earlier/current public and held-out
tests before/after. This is an investigator-authored causal code intervention,
not another reader success, an eligible training label, or a fresh comparison.

The diagnosis can establish that this particular semantic choice explains the
observed test failure; it cannot prove exhaustive correctness or a general reader
limitation. Its native execution costs are separate from the frozen experiment.
