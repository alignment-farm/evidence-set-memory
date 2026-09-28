# Natural-text neural set energy: selection and complete work

28 September 2026. **The frozen comparison is complete. A separate public
length-stop repair diagnostic is running. No useful end-to-end or EBM-specific
advantage is established.** Root review remains separate.

## What was learned, and from what

A small neural specialist learns to select four paragraphs from a supplied pool
of twenty real MuSiQue paragraphs. Its 674 trainable parameters produce unary and
pairwise coefficients from lexical/link features and frozen MiniLM similarities.
The imported encoder has 22,713,216 parameters; this is not a 674-parameter
end-to-end system. Its knowledge/pretraining and construction costs remain part
of the method. Ordinary hybrid access receives those same representations.

Benchmark support annotations supervise 253 training questions. The lexical
specialist improves training complete-support recovery 77→112/253 and development
12→20/48 from initialization. The semantic specialist improves 61→127/253 and
6→21/48. This establishes functioning acquisition rather than merely finite
gradients. All fits, the initial size assertion failure, and unsuccessful reader
interfaces remain in `runs/`. The semantic ordinary and unary alternatives also
reach 21/48 on development; a neural win was not an admission condition.

This is static supervised acquisition, **not** experience earned across continuing
sessions. Training labels are imported annotations, not the primary reader's
outcome feedback. [STATE.md](STATE.md) specifies surviving artifacts, resets and
update sources. [CLAIM.md](CLAIM.md) and [freeze.json](freeze.json) fix the developed
methods before confirmation selection and reader use. [PROVENANCE.md](PROVENANCE.md)
records gpt-6-astra/high, actual harness/version boundaries and interventions.

## Held-out evidence selection

| Method | Complete annotated support / 64 | Mean support recall | Global-score optima / 64 | Selection wall seconds |
| --- | ---: | ---: | ---: | ---: |
| Ordinary semantic/lexical/link set assembly | 15 | 0.6354 | — | 0.0082 |
| Learned unary selection | 15 | 0.6263 | — | uninstrumented |
| Exact learned set score | 26 | 0.7305 | 64 | 0.0110 |
| Beam-16 on that score | 26 | 0.7305 | 64 | 0.0619 |
| Continuous relaxation, rounded | 29 | 0.7474 | 32 | 1.8939 |
| Continuous relaxation plus swap repair | 26 | 0.7305 | 64 | 1.9037 |

These times exclude the shared representation and network-forward costs, which
are separately recorded. Each phase-2 search arm actually ran independently.
Unary sorting time was not instrumented; the raw zero must not be treated as a
measured zero cost. See [selection outcomes](runs/confirmation-selection/outcomes.json)
and [representation ledger](runs/confirmation-selection/representation.json).

Exact versus ordinary has 15 paired wins, 4 losses, 45 ties on complete support;
the difference is 11/64. The 64 questions form 55 component-connected clusters.
The descriptive cluster-resampling interval for that difference is approximately
0.048–0.295, not a population or multiple-comparison-adjusted guarantee.
Raw relaxation attains the learned global optimum on only half the questions,
yet recovers three more complete annotated sets. Improving the learned objective
therefore need not improve evidence sufficiency.

One confirmation question was already inspected in the earlier reconnaissance.
The original partitioner failed to exclude it. Retaining the freeze and excluding
all reconnaissance-related components in a sensitivity analysis leaves 63 cases:
exact 26, ordinary 15, unary 14. There are also shared source paragraphs across
partitions despite disjoint single-hop IDs. See [EXPOSURE.md](EXPOSURE.md); calling
every question or every source string wholly unseen would be incorrect.

## What “energy-based” changes here

The discrete energy is the negative of a conventional pairwise set score. Exact
or beam minimization of that energy is the same ordering as score maximization;
its sign is not an experimental treatment. The distinct tested procedure is
four-start projected gradient optimization over fractional selection variables,
followed by rounding and optional one-swap refinement. This inference does not
update persistent weights. No low energy certifies truth, authority or scope.
“Energy” here is a mathematical objective; machine electrical energy was not
measured. Search overhead alone is not an end-to-end cost advantage.

[Phase 3](../phase3/FINDINGS.md) enlarges candidate pools on seen development
material. At 160 candidates, relaxation/refinement beats exhaustive enumeration
on measured search time, but beam search finds the same optimum with less work.
[Phase 4](../phase4/FINDINGS.md) adds a term that is zero on every discrete set.
Although every discrete energy and training-pair loss is unchanged, rounded
selections can change on 41/48 development cases. This distinguishes the
continuous landscape/search procedure from a negative set score concretely.
Neither diagnostic adds fresh downstream tasks or demonstrates an EBM advantage.

## Complete-task comparison

The prespecified first 24 cases contain none of the previously inspected
reconnaissance questions. All 24 have every annotated support paragraph available
in their candidate pool. They occupy 24 separate component-connected clusters.
This establishes annotation reachability, not the presence of a valid factual
chain for every question; the label audit finds counterexamples to that inference.
One fixed reader/tag and interface serves every arm; no selector or checkpoint
changes after the freeze. These are annotation-based scores, qualified below.

| Context policy | Full support selected / 24 | Answer EM / 24 | Mean answer F1 | Answer + complete valid citations / 24 | Complete after public fallback / 24 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ordinary hybrid four paragraphs | 4 | 3 | 0.254 | 0 | 1 |
| Learned unary four paragraphs | 4 | 3 | 0.247 | 1 | 2 |
| Exact learned set / relaxed+swap | 10 | 4 | 0.325 | 2 | 3 |
| All twenty source paragraphs | 24 | 9 | 0.464 | 6 | 6 |
| Annotated-support control | 24 | 11 | 0.584 | 9 | 9 |
| One annotated support removed | 0 | 3 | 0.196 | 0 | 2 |
| Prior knowledge only | 0 | 0 | 0.084 | 0 | 0 |

Exact and refined relaxation deliver identical contexts in all 24 cases and
reuse the identical reader response; they are not independent reader replications.
Exact versus ordinary has two complete-score wins, no losses and 22 ties, with
a descriptive cluster-bootstrap difference interval 0–0.208. Against all-source
access it has one win, five losses and 18 ties, interval -0.375–0. The cohort is
small, and there is no demonstrated equivalent-quality/lower-work result.

The exact selector retains complete annotated support on ten cases, but only two
pass the complete metric: seven fail answer EM and one passes EM but misses
required citations. Fourteen omit some annotated support. This separates
candidate reachability, selection and reader/metric outcomes; it does not license
calling all eight downstream metric failures reader reasoning errors.

[The source/label audit](LABEL_AUDIT.md) finds exact-match penalties for legitimate
answer variants and several mismatched-entity chains in this slice. Its inspection
is outcome-selected and does not estimate prevalence. Original scores remain
unchanged. The table is benchmark answer/citation quality, **not a validated count
of all genuinely correct complete tasks**. Even the annotated-support control is
not a truth oracle. Some source-supported answers are scored wrong, and requiring
every annotated citation can penalize a legitimate alternative evidence set.
The subsequent review of the eleven EM-passing support controls finds unsupported
bridges there too. All 24 control source bundles were eventually inspected, but
the review was post-hoc and unblinded, not an independently validated new scorer.

The original 1,024-token response cap yields 13 unique length stops, including
five all-source calls and three exact-set calls (some payloads map to multiple
arms). Public schema extraction already salvages valid trailing JSON when present.
The separately declared [budget diagnostic](READER_BUDGET_DIAGNOSTIC.md) retries
all length stops at 4,096 tokens, without correctness triggers. That is post-freeze
diagnosis on the same cases, not fresh confirmation. Its results remain pending.

Raw [outcomes](runs/confirmation-reader/outcomes.json),
[summary](runs/confirmation-reader/summary.json), and
[offline audit](runs/frozen-reader-audit.json) preserve the original result.

## Costs, reproduction and next boundary

Five completed development fits performed 4,800 optimizer updates and 2,428,800
contrast presentations. Their recorded training/validation/checkpoint intervals
total about 5.85 wall seconds, plus repeated feature construction. Original
benchmark annotation, imported pretraining, investigator work, installation and
some startup/diagnostic work are not fully metered and must not be assigned zero.
The original confirmation reader makes 166 unique calls for 192 mapped outcomes,
using 165,890 prompt and 26,529 completion tokens in 2,291 measured wall seconds,
with zero endpoint errors or missing usage fields. It reports 9,612 cached prompt
tokens; execution order and backend caching limit timing comparisons. The final
native ledger will add all development/diagnostic reader calls, tokens, encoding,
repeated selection, fallback and verification work without double-counting reuse.

For the 24-case deployment comparison, exact compact reading uses 25,590 initial
prompt+completion tokens; its seven public fallback calls add 27,664, totaling
53,254. Ordinary compact uses 25,278 plus 26,839 for seven fallbacks, totaling
52,117. All-source reading uses 89,806 tokens. These are logical policy costs,
not additional physical calls on top of reused experiment outputs. The compact
policies cost less but achieve lower recorded complete quality; shorter context
alone is not a usefulness claim.

Exact checkpoint and non-timing selection replay succeeded; six boundary tests
pass. See [reproduction instructions](REPRODUCE.md) for pinned source/model versions,
scratch-checkout precautions, executed commands and raw-evidence audit paths.

The current phase resolves acquisition and search distinctions in a supplied-pool
natural-text mechanism task. Candidate discovery is fixed by the benchmark, not
learned. It cannot establish useful maintenance when authoritative sources change.
Any next continuing-work phase must obtain or explicitly author revision histories,
earn eligible earlier outcome feedback, compare retained versus frozen state, and
preserve ordinary source/answer reuse and complete repair. It also needs validated
entity/source links and acceptance of legitimate answer/evidence alternatives;
the current annotated-support proxy cannot certify that. More static QA rows or
an additional winning optimizer would not by themselves close that gap.
