# Development self-check diagnosis: more tests are not a certificate

Declared/executed after the scratch-enabled ordinary attempt closed, while the
last development arm continued unchanged. This is an unblinded analysis of already
exposed development, with zero new participant calls and no feedback to other arms.

The ordinary scratch-enabled reader uses its eighth/final call to author 20 pytest
tests. Its final production patch passes upstream, retained, public and all six
private current checks. It does not explicitly finish because the call budget ends.
The own suite instead reports 18 passes and two failures. Both failing expectations
assume interpolation can see a variable assigned *later* in the file, which the
retained sequential interpolation behavior does not promise. They are incorrect
own expectations, not newly authorized requirements. Grading does not promote model
assertions to examiner truth.

The production patch was already complete before those checks ran: there is no
subsequent edit, and only the later private grade establishes completion. Therefore
this observed success cannot be causally credited to executing the own suite.
The changed tool-availability prompt/workflow may affect proposal generation.

Does the own suite at least distinguish the old missed clause? Reconstruct the
closed successful source from saved patches. In an isolated second copy, replace
**only** `_detect_line_ending` with the old incorrect rule: return CRLF if it appears
anywhere, otherwise LF. Execute the unchanged own suite and six private checks
against both source versions:

| Code | Reader's own checks | Private current checks |
|---|---:|---:|
| Actual successful patch | 18 pass, 2 fail | 6 pass |
| One-helper semantic mutant | 18 pass, same 2 fail | 5 pass, 1 fail |

The saved failing test IDs match exactly for the own suite. Its mixed-ending test
starts with CRLF, then LF; it does not cover the LF-first/CRLF-later case that
distinguishes the two algorithms. This explains an observed coverage gap without
claiming that all model-authored tests are useless or that six private checks prove
full correctness. No mutant becomes canonical source, a training label or a fresh
transfer result. Four native pytest invocations and their costs are retained in
`runs/check-diagnosis/`; the 20-test generation and original execution remain charged
to the development attempt.

This diagnosis motivates measuring actual test content, uptake, false expectations,
repair and complete behavior—not merely counting whether a check tool was called.
Keep the same reader/tool opportunity for all fresh comparison policies and retain
ordinary source access. Do not teach the known LF-first counterexample to the
participant and then relabel that task fresh.
