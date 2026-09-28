# Phase 2 developed claim and frozen fresh comparison

28 September 2026. Confirmation representations and selections have not been
generated. All development changes and unsuccessful reader interfaces are retained.

The lexical neural energy functions: training complete-support recovery improves
77→112/253 and development 12→20/48 from seed-23 initialization. Adding frozen
MiniLM similarities gives a 674-parameter trainable energy, improving 61→127/253
on training and 6→21/48 on development. This is acquisition of benchmark set
supervision given imported representations; no continuing-memory claim follows.

Semantic ordinary hybrid retrieval and the semantic learned unary alternative
also reach 21/48 development completion. Exact search and beam-16 achieve the
same score on all development cases; relaxed search often misses that optimum.
Relaxation/refinement is slower than exact enumeration at this candidate size.
Higher score does not always mean more complete annotated support. No EBM-specific
quality advantage is developed or presumed.

Freeze semantic pairwise seed 23 epoch 60, semantic unary seed 11 epoch 20, and
ordinary hybrid link weight 1.0 (chosen from 0, .25, .5, 1 by development complete
recovery then recall). The models use different random seeds and architectures;
the unary comparison is a serious alternative, not a perfectly isolated causal
interaction ablation. Exact, beam, relaxed and relaxed-plus-swap search all use
identical fixed pairwise coefficients. Their different procedures are the EBM
inference contrast, not positive versus negative sign.

Evaluate every eligible question in the preassigned 64-row confirmation partition;
exclude non-20 pools by the same visible-size rule. Complete support recovery,
recall, global-score attainment, gradients, scores and wall time are separate
outcomes. No weights, representations, baseline tuning or search settings change.
Run complete QA on the first 24 eligible IDs in that fixed order, not cases chosen
by retrieval success. All primary models use the same available Qwen3.8 27b tag.
Include ordinary, unary, exact, relaxed+swap, all-source, support-only oracle,
one-support-removed and prior-knowledge-only diagnostic arms. Oracle conditions
use labels only as explicit controls, never as deployable selection.

Reader outputs must contain answer plus source citations. Report official-style
answer EM/F1 and a stricter complete measure requiring correct answer and all
annotated support citations, with every citation actually delivered. This is
annotation-based sufficiency, not an independent proof of necessary reasoning.
Full-context output is available for fallback on public abstention, malformed
output or invalid citations; wrong confident outputs cannot be oracle-repaired.
No-context permits pretrained knowledge and cannot attain complete citation score;
use its answer metrics to diagnose knowledge availability, not as a production arm.

Development found ignored JSON-mode requests and explanatory output before final
JSON. Final parsing extracts the last schema-valid object; output cap is 1,024,
temperature 0, requested seed 761. Deterministic format repair is available equally
to all methods. Earlier 256/512-token responses and strict-parser results remain.
Formatting extraction tests pass; no confirmation result developed the repair.

Use paired differences, with component-connected clusters within confirmation
reported rather than treating every row or model call as independent. Source
paragraph overlap across splits must be reported in addition to disjoint component
IDs. Pretraining overlap remains possible. Any quality/work advantage is limited
to this supplied-pool benchmark cohort and reader. It cannot establish adaptation
to source revisions, independent discovery or lifelong improvement.
