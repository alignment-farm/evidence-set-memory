# Larger candidate pools: a computational crossover, not an EBM advantage

28 September 2026. The [predeclared scaling diagnostic](PROTOCOL.md) extends the
frozen phase-2 semantic energy to pools of 20, 40, 80 and 160 natural paragraphs.
Four already-seen development questions retain their original evidence and gain
deduplicated distractors from other development pools. The selection budget is
four. No weights, search hyperparameters or encoder representations were updated.
This is a constructed optimization diagnostic, not fresh task-quality evidence.

| Candidates | Exact enumeration: four cases | Beam-16 | Relaxation + swap | Global optima: beam / relaxation |
|---|---:|---:|---:|---:|
| 20 | 0.0053 s | 0.0017 s | 0.1184 s | 4/4 / 4/4 |
| 40 | 0.0896 s | 0.0040 s | 0.1206 s | 4/4 / 3/4 |
| 80 | 1.5277 s | 0.0082 s | 0.1265 s | 4/4 / 4/4 |
| 160 | 25.4574 s | 0.0178 s | 0.1443 s | 4/4 / 4/4 |

Energy minimization becomes faster than enumeration in this implementation by
80 candidates, but ordinary discrete beam search remains both faster and at least
as accurate at maximizing the identical learned score. At 160 candidates, exact
search evaluates 105,177,440 sets across four cases, beam scores 29,767 partial or
complete sets, and relaxation/refinement uses 1,280 selection-gradient steps plus
3,152 discrete scores. Counting a matrix-vector gradient as one cheap “step” would
hide its dependence on pool size; the recorded native units are not interchangeable.

All methods recover complete annotated support on 2/4 cases at 20 candidates,
1/4 at 40 and 80, and 2/4 at 160. Reaching a global energy optimum therefore does
not certify evidence sufficiency. The nonmonotonic support result may reflect
normalization changes and additional plausible distractors, and this tiny sample
cannot identify a general robustness trend. Alternative helpful evidence outside
the original annotations may also be uncredited.

Generalized N=20 lexical features match the phase-2 implementation within the
asserted numerical tolerance. Query/document/title embeddings are reused from the
fixed MiniLM cache; their original construction costs remain in phase 2. Per-pool
feature and coefficient-construction times are recorded separately in
[outcomes.json](runs/scaling/outcomes.json). The search table excludes those common
costs. Exact enumeration is chunked to bound memory; unlike phase 2's twenty-item
enumeration, combination construction is included in its timer. Do not compare
the two phases' exact-search times as if they were the same timing scope.

Timing used one CPU run while the separate phase-2 serial reader was operating
on the same host. CPU and wall times are recorded, but these are not isolated
hardware benchmarks or general speedup guarantees. The native operation counts
and exact-score comparisons support the narrower conclusion. There are no new
reader calls, no training updates, and no new encoder calls in this diagnostic.

This removes one plausible explanation for phase 2's result: the tested relaxed
method can beat brute-force enumeration at larger pools, yet still lacks an
advantage over a competent discrete search method. More restarts or optimization
would need to beat beam search on quality and total work, not just beat enumeration.
No search recipe was tuned after observing these results.

Reproduction: after rebuilding phase-2 development inputs/embeddings, run
`uv run python scripts/phase3_scaling.py --out .cache/phase3-replay` with a new
output-directory name. Existing runs are intentionally write-once.
Source pool lineage, code/protocol/checkpoint hashes, all outcomes and costs are
preserved under [runs/scaling](runs/scaling). The original execution code is in
commit dda88d9; the subsequent CLI-only change permits alternative output paths.
