# Phase 1 findings — 28 September 2026

A small learned set scorer works in this authored revision-aware task, but it
does not improve on ordinary source access. Exact search over its acquired score
and ordinary dependency closure both complete all 30 fresh executable tasks.
One-swap minimization of the same negative score completes 24/30 before repair.
The difference is search, not the name “energy.” A fixed-reader check further
shows that sufficient evidence does not guarantee a correct primary-model answer.

This closes a bounded acquisition/diagnosis phase on explanatory progress. It
does not close the broader research question. Independent root review is pending.

## Workload, acquisition and boundaries

The [protocol](PROTOCOL.md) was written before implementation/results and amended
after development, before fresh material. [CLAIM.md](CLAIM.md) records the developed
claim; [freeze.json](runs/freeze.json) pins it, code and checkpoints at
12:11:30 UTC. Six fresh histories were then generated and evaluated, finishing
12:11:31 UTC. Confirmation source identifiers do not occur in acquisition.

Each authored history starts with nine records: three items pointing to contracts,
three contracts pointing to tax records, and three tax records. Five requests
cover initial work, a repeated request after context reset, a contract-price
correction, an item-reference change, and a query over another unchanged source
chain. Old versions remain visible. There are 9–11 candidates per request and
three selected records. All correct records are reachable in every pool. This
tests selection, not gold-blind candidate discovery. Numeric values and identities
are fresh, but the schema and graph pattern are shared with development.

The complete artifact contains item, quantity, subtotal, rounded tax, total and
current source citations. Private evaluator answers are constructed from the
generator's world state; the public quote tool independently follows the supplied
records and computes the artifact. Authored formula/schema agreement and omission
checks validate this small environment, not natural-world truth. Public source
revision rules, links, requirements, code, caches and fallback remain available
to every competitor. No examiner certificate enters selection features.

Development has four histories and twenty requests. An exploration policy tries
sets and receives binary complete-outcome feedback from actual tool execution.
First it samples sets; the developed recipe also tries ordinary dependency closure
and one-record perturbations. This is outcome feedback from an authored simulator
and investigator-designed exploration, not autonomously discovered experience,
public benchmark supervision or LLM-earned feedback. Acquisition is batched after
the earlier development histories, before later confirmation. It is not online
weight improvement at every episode.

The specialist stores eight scalar coefficients over explicitly engineered
features: query item match, current-revision fraction, kind counts, resolved
reference edges and a query-root edge. Its bias cancels in pairwise differences.
This is a small trainable linear energy on non-additive set features, not a neural
representation learner. Features already encode substantial relational knowledge.
The ordinary comparator simply follows the same declared references and authority.

Across resets, archives, revisions, completed artifacts and specialist weights
survive. Selection variables and reader chat context do not. Reuse checks both
quantity and current citation lineage. All arms acquire six valid cache hits in
confirmation, including weak ablations whose earlier output was repaired. No
confirmation result changes weights. Maintenance here changes source records,
not learned parameters. The last stage, called “preservation” prospectively, checks
an unchanged chain; that exact item was not previously quoted in the same history.
It is not a test of retaining a previously mastered item-specific behavior.

## Acquisition diagnosis

| Development intervention | Feedback | Complete tasks before fallback | Interpretation |
|---|---:|---:|---|
| Random attempts, set-classification loss, 1,000 steps | 4 successes / 320 attempts | 12/20 | Learns useful relations but selects stale versions |
| Closure plus perturbations, same loss, 1,000 steps | 24/760 | 12/20 | More successful exposure alone did not fix ordering |
| Same 760 attempts, 10,000 steps | No new labels | 12/20 | Lower loss alone did not fix complete behavior |
| Within-task pairwise loss, 1,000 steps | Same 760 outcomes; 736 contrast pairs | 20/20 with exact search | A functioning acquired selector |
| Pairwise loss, interaction features removed | Same feedback | 4/20; 0/20 sufficient selected sets | Four successes come from legitimate prior repair/cache reuse |

All failed recipes, attempts, weights and losses are retained under
[runs/development](runs/development) and [runs/diagnosis-longer](runs/diagnosis-longer).
The set classifier's current-revision coefficient was negative after both 1,000
and 10,000 steps. The pairwise coefficient is positive. The pairwise intervention
changes objective and effective example weighting together; it does not isolate
which accounts for recovery or prove classification incapable of learning the
task. “Pointwise-in-set” in the frozen claim means independent classification of
candidate sets, not removal of the interaction features. The separate pointwise
ablation does remove those features.

This is evidence that earlier outcome contrasts can teach the provided small
representation a useful ranking, relative to a zero-weight control. It is not
evidence that those coefficients add value over competent ordinary memory.

## Fresh executable comparison

| Policy | Sufficient sets | Complete before fallback | Complete after fallback | Fallbacks | Feature evaluations |
|---|---:|---:|---:|---:|---:|
| Ordinary current-source closure and reuse | 30/30 | 30/30 | 30/30 | 0 | 0 |
| Acquired set score, exhaustive search | 30/30 | 30/30 | 30/30 | 0 | 3,708 |
| Same score negated, one-swap energy minimization | 24/30 | 24/30 | 30/30 | 6 | 1,290 |
| Pairwise pointwise-feature ablation | 0/30 | 6/30 | 30/30 | 24 | 3,708 |
| No-acquisition zero weights | 0/30 | 6/30 | 30/30 | 24 | 3,708 |

The six histories, not thirty rows, are the clustered units. Every history shows
the same pattern. Ordinary and exhaustive learned selection produce identical
three-record contexts. The energy search fails after changed references in all
six histories; its other stages pass. Fallback is triggered by public missing
dependency/stale-source checks, not hidden gold. It executes ordinary closure.
Weak controls' six initial successes are cached outputs from earlier repairs.
Their zero sufficient-set count exposes that distinction.

Exhaustive score search is a serious set-aware alternative here: it considers
every three-record combination and finds the global maximum of the identical
learned function. The ordinary comparator is also set-aware. There is no claimed
replication of ParaSet or MSS-Complement; [the reading ledger](sources/phase1/README.md)
explains their methodological relevance and inspection limits.

For any set S, E(S) = -w·features(S). Changing sign preserves the ordering exactly.
One-swap descent begins from a fixed visible unary heuristic, accepts strictly
improving swaps and stops after at most ten moves. Its development failure is a
verified local optimum: score 8.553232, best one-swap neighbor 8.265635, global
best 8.840829. Moving to the corrected source chain requires crossing a worse
intermediate selection. This explains the executed bounded search failure; it
is not a general result against iterative energy inference, other restarts,
continuous relaxation or hard authority filtering. No additional search method
was tuned on confirmation.

## Fixed-reader diagnostic and complete workflow

Qwen3 8B was served by Docker Model Runner, with temperature 0, requested seed 761,
512 output-token cap and thinking disabled in both the request and instruction.
Server compliance with generation settings was not independently verified.
[Provenance](runs/provenance.json) records the model digest, quantization ambiguity,
llama.cpp backend, hardware, investigator model and actual reasoning setting.

The predeclared first fresh history supplied five reader cases. Identical
request/context pairs were executed once and mapped across arms: **17 actual
requests, 27 mapped observations**, not 27 independent calls. Reader context
resets each call. It does not use the cross-episode answer cache; this diagnostic
isolates reading. The full executable policy above does use that cache.

| Delivered context | Raw complete LLM outputs | After public tool validation/repair |
|---|---:|---:|
| Ordinary compact set | 2/5 | 5/5 |
| Exact learned compact set | 2/5, same responses as ordinary | 5/5 |
| Energy-selected compact set | 2/5 | 5/5 |
| All nine current records | 0/5 | 5/5 |
| Required tax record omitted | 0/5 | 5/5 |
| Stale source sets | 0/2 | 2/2 |

Both compact successes are the initial request and its repeated counterpart,
so the sample offers only one successful unique business calculation. With
sufficient compact evidence, stage 2 and 4 return incorrect tax/total values;
stage 3 contains an expression inside JSON and is invalid (its tax is also wrong).
Omitted-tax calls fabricate a quote in all five cases instead of reporting a
missing dependency. The all-current calls fail arithmetic despite correct source
availability. These are observed limitations of this prompt/model/sample, not a
general ranking of broad and compact contexts.

The controller independently executes public ordinary closure and arithmetic on
EVERY mapped output before returning a repaired artifact. It does not obtain
answers from the hidden evaluator. That is real extra work: 27 validation tool
calls and 271 archive-record visits, including validation of apparently successful
answers. All 27 mapped workflows complete after this work. The ordinary executable
policy completes without an LLM call, so neither learned selection nor smaller
reader prompts establish an end-to-end advantage in this regime.

## Native costs and limits of accounting

- Acquisition executed 1,080 set attempts: the first 320 random attempts were
  executed again inside the 760-attempt recipe. They are not extra independent
  evidence. Pairwise fitting constructs 736 positive/negative contrasts and their
  736 sign reversals without new labels. There are no paid teacher calls,
  embedding calls, weight downloads or remote training.
- Six development/diagnostic fits total **12,384,000 example-gradient evaluations**
  and **13.9594 seconds** measured training wall time. The chosen pairwise model
  alone costs 1,472,000 evaluations and 1.6832 seconds, excluding exploration and
  feature construction. Full CPU reproduction adds another 12,384,000 evaluations
  and 13.9931 seconds; this verification work is search cost, not deployment cost.
- Every confirmation arm has 300 source records across its candidate snapshots,
  totaling 46,304 serialized JSON bytes. This is repeated visible-input volume,
  not unique storage or network traffic. Symbolic feature construction is charged
  through counted feature evaluations and selection wall time; no learned encoder
  is used. `index_record_visits` counts one visible-archive pass per request, not
  every internal Python scan; repeated indexing is included in timing but not
  comprehensively counted as primitive operations.
- Over thirty requests, selection time is 0.000058 seconds for ordinary closure,
  0.010434 seconds for exact scoring, and 0.004893 seconds for one-swap search.
  These single-run, tiny-operation timings are not stable hardware benchmarks.
  The stronger evidence for work is zero versus 3,708 versus 1,290 feature
  evaluations, and zero versus zero versus six fallback executions. Energy has
  30 accepted moves. All arms have 24 initial tool calls and six cache hits.
- Ordinary and exact deliver the same 13,724 serialized source bytes in total.
  Energy delivers 13,722 before fallback plus 2,746 for repair. The implementation
  still computes a selection on cache-hit episodes; charged work is not an
  optimized reuse implementation. These bytes are not tokenizer counts.
- The reader check costs **8,879 reported prompt tokens**, **2,122 completion
  tokens**, and **45.2853 seconds** total request wall time, including initial
  model loading/network time. All 17 responses report usage. Raw requests and
  responses are preserved in [runs/reader](runs/reader). No retries occurred.
- Initial development, including label generation, fitting and evaluation,
  took 2.1207 seconds jointly. Feature/label-construction time is not isolated.
  Actual CPU seconds, machine energy, investigator tokens/money, total tool/network
  overhead and amortized serving cost were not metered. Do not read unknown as
  zero. Verification and inference are separate from the 30-task deployment ledger.

## Interpretation and next bounded step

ES1 is illustrated in its explicit-access limit: learned interactions outperform
the diagnostic feature ablation, but ordinary declared links already recover the
complete set. ES2 has narrow support for changed values and references under
exact selection with frozen weights; one-swap search fails the reference change.
It does not test changed schemas, unreliable feedback, latent scope rules or
weight-update forgetting. ES3 is illustrated by a useful search-cost tradeoff:
local optimization scores fewer sets but requires repair; neither learned search
beats ordinary closure. These are local assessments, not accepted root synthesis.

Stop this phase because acquisition functions, failed recipes have an explanatory
diagnosis, fresh same-schema transfer was tested, and the ordinary solution fully
explains closure. Further optimizer tuning on this direct-addressed task would
not resolve the broader scientific question. Retain the reader errors rather
than repeatedly tuning on the fresh history.

The next bounded step is a separate development workload with source-native
prose or code in which references must be discovered, while keeping metadata,
ordinary search, reusable code, source answers and scope rules available. Use
roughly four development histories to check whether competent ordinary access
actually leaves complementary omissions, including previously completed unchanged
tasks after corrections. Develop on those histories, freeze again, then collect
fresh histories. This is a new claim opportunity, not a requirement to manufacture
an EBM win. Current confirmation records are now seen material and must not serve
as fresh evidence for a subsequently redesigned method.

## Reproduction and exact revisions

Run from this repository, using a new output name on repeats:

```sh
uv run --no-project python scripts/test_quote_study.py
uv run --no-project python scripts/audit_phase1.py --out runs/audit-replay.json
uv run --no-project python scripts/reproduce_phase1.py --out runs/reproduction-1
```

The full CPU reproduction was executed in `.cache/phase1-reproduction`; weights
and every non-timing confirmation field reproduced exactly. The tracked
[verification record](runs/verification.json) preserves its result and added
cost. The initial implementation is preserved byte-for-byte in
`scripts/snapshots/quote_study-v1.py`. The later core edit only changes freeze and
confirmation checkpoint paths. Frozen code hashes and source/claim/checkpoint
hashes are verified by the audit. [artifact-manifest.json](runs/artifact-manifest.json)
pins publication inputs and evidence. Public-asset source versions remain in
FEASIBILITY and the source ledger; no public benchmark was newly acquired.

An optional reader rerun requires an available serving window and incurs new
inference cost; original responses are sufficient for offline outcome inspection:

```sh
uv run --no-project python scripts/reader_check.py --out runs/reader-replay
```

Stochastic server/numerical behavior can differ despite a requested seed and
temperature. No remote publication, benchmark submission, root experiment edit
or unrelated study modification was performed.
