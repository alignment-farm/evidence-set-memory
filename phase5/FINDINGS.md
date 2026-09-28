# Phase 5 — compact energy selection, finite penalties and source revisions

28 September 2026. A functioning small energy learner transfers compact selection
to new authored configuration histories, but **ordinary dependency closure remains
the better complete-work method here**. The study separates three distinct failures:
missing syntax in the representation, an imperfect learned objective, and inadequate
optimization of an otherwise successful objective. No LLM or neural advantage is
established. Root scientific review remains separate.

## What was actually tested

Reuse: CPython 3.12.14's unchanged `configparser.ExtendedInterpolation`. Authored:
INI section archives, scope/revision metadata, independent expected output strings,
six chronological event types, syntax features, exploration and completion tests.
Whole current-scope sections are evidence; native rendering is the complete task.
Cross-section interpolation, DEFAULT lookup, local overrides and escaped references
exercise code semantics rather than ambiguous QA exact-match annotations.
This is a deliberately tiny controlled workload, not naturally acquired user work.

Twelve earlier histories supply 2,448 executed subset attempts: 24 random subsets
per episode plus ordinary closure, each single omission and each single superset.
Binary complete feedback enters pairwise learning; raw output/error is recorded.
The learner does not receive expected strings, evaluator dependency certificates,
confirmation feedback or future requirements. Ordinary closure supplies successful
proposals: this is investigator-designed exploration with an ordinary teacher,
not autonomous discovery of successful strategies. The three/four trainable
coefficients have no pretrained encoder or imported learned representation.

After [freezing](freeze.json) protocol, claim, code and weights at commit
`f8651b89a9ce7eb4301c363e7156a9e22348af2c`, a **new process** generated 12 fresh
histories / 72 correlated episodes. Six have new identifiers/values using existing
templates; six also add two previously unseen intermediate chain sections. The
latter have 11 eligible candidates instead of 9. Each history includes a repeat,
authoritative value correction, dependency revision, revised repeat and old-valid
obligation. Six structural template families are repeated across strata: these
are not 72 independent samples or a broad population evaluation.

Candidate discovery is deliberately complete. Scope and latest-revision filtering
are explicit shared rules, not learned authority. Code, full source access, public
repair, and validated source-answer caching are available to every policy.

## Energy and actual method differences

For selection vector z, the developed energy is

`E(z) = a(1-z_request) + b Σz_i + c Σ_(i→j) z_i(1-z_j) + d Σ_(i→j) z_i z_j`.

The public syntax graph supplies edges; binary z supplies actual delivered sections.
The features are missing request, cardinality, unresolved and resolved dependencies.
The balanced checkpoint is approximately `(8.4547, 1.3267, 1.4408, -1.1014)`.
Its negative is exactly the corresponding set score; renaming it changes nothing.
Exact search enumerates every subset. Relaxation optimizes the same multilinear
extension in `[0,1]^N`, four starts × 60 projected-gradient steps, step size .05;
initial/final threshold-rounded candidates compete by discrete energy. That search
procedure, not a score's sign, is the tested operational difference.

A diagnostic energy sets d=0 and trains the other three coefficients, yielding
approximately `(8.4129, .7203, 1.8851)`. A separate **nonlearned** hard-energy control
minimizes record count subject to including the request and resolving every selected
edge. It changes the objective and feasible domain. It is not a calibrated version
of learned energy or evidence that learning enforces correctness.

## Preserved acquisition diagnosis

1. Explicit-cross-reference features miss DEFAULT dependencies and misread escaped
   references. Exact learned selection completes 58/72 development episodes before
   repair. Native-syntax features lift this to 72/72. This improvement is authored
   representation engineering, not a learned parser and not better optimization.
2. Unbalanced pair learning completes 72/72 but delivers 36,014 bytes versus ordinary
   closure's 28,704. Reweighting success/failure and shorter/longer-success pair
   classes equally reduces this to 30,070. The same 21,677 observed pairs are reused;
   no new labels. An irrelevant connected component still attracts the energy on
   two old-valid requests, producing six sections instead of two.
3. Removing the resolved-edge reward avoids that attraction but reduces exact
   completion to 64/72: satisfying a chain can cost more than its learned finite
   omission penalty. For example, three additional records cost `3 × .7203`, greater
   than the `1.8851` penalty removed. Exact minimization can deliberately omit them.

All attempts remain under `runs/`. A balanced-run provenance serialization bug
occurred **after** model/outcome files were written; its exit failure, code hash and
outputs are retained in [FAILURE.md](runs/balanced/FAILURE.md). Fixing the relative
path handling and rerunning produced the bit-identical balanced checkpoint. The
final freeze selected the balanced learner, while retaining the finite-penalty
variant as a diagnostic rather than quietly replacing it with a successful recipe.

## Fresh complete outcomes

Each policy has 48 actual selections/executions plus 24 validated cache hits. A
cached answer can come from an earlier ordinary repair; it must not be credited
as a newly successful learned selection. Both denominators are shown below.
Bytes include failed delivery and public repair, excluding zero-delivery cache hits.
They are serialized evidence bytes, **not model tokens**.

| Frozen policy | Noncache complete | All episodes before repair | Public repairs | Delivered bytes | Selection seconds |
|---|---:|---:|---:|---:|---:|
| Ordinary syntax-aware closure | 48/48 | 72/72 | 0 | 34,442 | .000111 |
| Full current-scope access | 48/48 | 72/72 | 0 | 80,240 | no subset search |
| Untrained four-coefficient energy, exact | 48/48 | 72/72 | 0 | 73,082 | .00446 |
| Trained four-coefficient energy, exact | 48/48 | 72/72 | 0 | 35,111 | .00428 |
| Same trained energy, relaxation | 34/48 | 58/72 | 14 | 39,476 | .0962 |
| Trained three-coefficient energy, exact | 29/48 | 53/72 | 19 | 41,316 | .00430 |
| Hard feasibility + minimum cardinality | 48/48 | 72/72 | 0 | 34,442 | .00738 |

Every policy ends at 72/72 **after** public runtime-error repair. No hidden wrong-
answer grade triggers repair. Every selected set uses eligible current-scope records.
The [expanded summary](runs/audit/confirmation-expanded-summary.json) includes native
execution, representations and repair timings, not just search. Timings are tiny
single-host observations, not isolated benchmarks or stable speedup estimates.
Full native access is also very cheap: its measured filtering plus execution is
about .00336 seconds across the sequence, versus about .00393 for ordinary closure
including graph construction. Compact evidence is not intrinsically useful to
this tiny native executor; no overall runtime saving over full access is claimed.

On the six same-template histories, the balanced energy's exact and relaxed search
both complete 24/24 noncache selections. On the six longer-chain histories, exact
remains 24/24 while relaxation falls to 10/24. The three-coefficient exact variant
falls from 20/24 to 9/24. Thus complete-pool reachability is not the issue; soft-objective
insufficiency and optimizer failure have separable evidence.

All methods record 24 valid repeat hits and 24 source-revision invalidations. Frozen
weights are unchanged across the later sequence. Source updates invalidate stale
answers through ordinary ID/revision rules, not gradient feedback. Old-valid requests
are new requests against unaffected sources, not repeated cached requests. There is
no learned online maintenance update in this phase.

## Why the gradient recipe failed

The [post-confirmation diagnosis](OPTIMIZER_DIAGNOSIS.md) is unblinded reuse, not a
second fresh test. On the same 48 noncached opportunities:

| Diagnostic | Complete | Global energy optimum | Gradient steps | Search seconds |
|---|---:|---:|---:|---:|
| Original four starts × 60 steps | 34/48 | 33/48 | 11,520 | .105 |
| Four starts × 240 steps | 48/48 | 48/48 | 46,080 | .351 |
| Sixteen starts × 60 steps | 48/48 | 48/48 | 46,080 | .380 |
| Original search + single-flip repair | 34/48 | 33/48 | 11,520 | .0885 |

One example (`transfer-6-916853/0`) selects an incomplete two-record set at energy
2.99286; the complete six-record optimum is 2.45330. Three starts eventually settle
in the worse basin, while the all-ones start reaches the correct optimum with more
steps. Additional random starts also find it. One-flip repair cannot add the needed
coordinated chain. This supports both convergence-budget and basin explanations;
it does **not** imply intrinsic impossibility of the tested continuous extension.
More work repairs the recipe, but exact search and ordinary closure remain cheaper
here. No improved recipe is retroactively reported as fresh-confirmation performance.

## State, costs, provenance and verification

Persistent: source records/revisions; frozen learned coefficients; a separate
per-policy answer/source-ID cache within each history. Reset: native parser and
selection variables on every episode; cache between histories. Episode resets are
logical fresh function invocations, not separate OS processes. Confirmation does
run in a separate process from development. Training feedback comes only from
earlier executed attempts checked against authored expected strings. Confirmation
outputs are never used to update weights.

[Native costs](runs/audit/native-costs.json): 2,448 acquisition executions, five
actual fits including the bookkeeping-failed run and identical rerun, 2,000 Adam
steps, 43,354,000 pair presentations, 3.334 seconds of fit/feature/pair construction;
4,481 total experimental native executions, 241,920 inference gradient steps and
501,360 discrete subset evaluations across development, transfer and diagnosis.
Acquisition wall time .123 seconds includes .111 seconds of native execution.
Zero external participant/teacher/reader calls, embeddings or weight downloads.
Ordinary closure has no label/training cost. The selected learner alone needs one
fit plus the shared exploration; total search costs include all five attempts.

The [audit](runs/audit/audit.json) separately spends 6,185 native replay executions
and five weight replays (1.851 seconds) to check 2,448 feedback rows, 2,520 policy
outcomes, 192 post-hoc outputs, and all 144 development/confirmation episode pools
and omission controls. All five checkpoints reproduce bit-for-bit on this host.
All 18 repository boundary tests pass. Historical source hashes reconstruct exactly.
Unknown costs are not zero: investigator tokens/dollars, authored task/label design,
power, startup/import/serialization, uninstrumented constructor/evaluator graph
overhead and earlier unit-test work. Saved timings are nested in places and must
not be summed as if independent end-to-end wall measurements.

Investigator: observed `gpt-6-astra`, reasoning **high**, OpenAI, Codex CLI 0.158.0,
session `01a0e7e4-68e2-7fb2-9a5d-2ea6873b86b8`. No independent backend fingerprint or
delegated reviewer. Runtime: Python 3.12.14, NumPy 2.5.3, PyTorch 2.14.0 CPU with two
threads, macOS 27.0 arm64. Native module SHA-256:
`cf5318e0c45a2e206b4ec74d4d66493185ed26c3736a86b0ebdf8f3a3e365a1a`.
Frozen experiment implementation SHA-256:
`6e5bfa985cf1f8aa87806f6a0fe27022515c0d3dffe6ce9c64d33671dc670b00`.
See [sources and limits](SOURCES.md), [reproduction](REPRODUCE.md), and the
[phase manifest](manifest.json). No other study or serving resource was touched.

## Interpretation and stopping point

The earlier-experience contrast supports learned **compactness relative to this
untrained initialization**, not a new completion capability: both exact versions
complete every later task. Ordinary closure is slightly more compact still, needs
no learned parameters or labeling, and avoids enumeration/gradient work. Hard
feasibility yields its same evidence at greater selection cost. Explicit revision
rules explain maintenance; learned energies do not establish authority.

ES1 is locally narrowed by a cheap exact dependency solution. ES2 has limited
support for stable selection under new values and stronger exact-search transfer
to longer chains, but no acquired source-authority or online-update benefit. ES3
is illustrated by the tested gradient recipe's extra work and sensitivity.

This phase closes on explanatory progress, not a neural win or a first failed
recipe. More sweeps of this transparent graph workload would not establish useful
assistant memory. The next bounded step is a source-native configuration/code edit
pilot with executable tests and a fixed primary reader, retaining ordinary code,
full access and repair. First establish what complete edit work and legitimate
earlier feedback actually exist; do not promote this renderer's results to LLM
reading or complete repository repair. The broader investigation remains open.
