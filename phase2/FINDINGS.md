# Natural-text neural set energy: selection and complete work

28 September 2026. **Publication in progress: the frozen 24-case primary-reader
run is still executing. Selection findings below are complete; no downstream
quality advantage is claimed from them.** Root review remains separate.

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

[Phase 3](../phase3/FINDINGS.md) enlarges candidate pools on seen development
material. At 160 candidates, relaxation/refinement beats exhaustive enumeration
on measured search time, but beam search finds the same optimum with less work.
[Phase 4](../phase4/FINDINGS.md) adds a term that is zero on every discrete set.
Although every discrete energy and training-pair loss is unchanged, rounded
selections can change on 41/48 development cases. This distinguishes the
continuous landscape/search procedure from a negative set score concretely.
Neither diagnostic adds fresh downstream tasks or demonstrates an EBM advantage.

## Complete-task comparison

Pending completion of the prespecified 24-case reader run. The final comparison
will report answer EM/F1, correct-answer-plus-complete-valid-citations, public
fallback, all-source access, support-only and omitted-support controls, and
prior-knowledge-only answers. Annotation-complete citations are a stricter task
proxy, not an independent causal proof that every annotated paragraph was needed.
No selection, checkpoint, parser or response allowance will change after results.

## Costs, reproduction and next boundary

Five completed development fits performed 4,800 optimizer updates and 2,428,800
contrast presentations. Their recorded training/validation/checkpoint intervals
total about 5.85 wall seconds, plus repeated feature construction. Original
benchmark annotation, imported pretraining, investigator work, installation and
some startup/diagnostic work are not fully metered and must not be assigned zero.
The final native ledger will add all actual reader calls, tokens, encoding,
repeated selection, fallback and verification work without double-counting reuse.

Exact checkpoint and non-timing selection replay succeeded; five boundary tests
pass. See [reproduction instructions](REPRODUCE.md) for pinned source/model versions,
scratch-checkout precautions, executed commands and raw-evidence audit paths.

The current phase resolves acquisition and search distinctions in a supplied-pool
natural-text mechanism task. Candidate discovery is fixed by the benchmark, not
learned. It cannot establish useful maintenance when authoritative sources change.
Any next continuing-work phase must obtain or explicitly author revision histories,
earn eligible earlier outcome feedback, compare retained versus frozen state, and
preserve ordinary source/answer reuse and complete repair. More static QA rows or
an additional winning optimizer would not by themselves close that gap.
