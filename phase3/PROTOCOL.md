# Phase 3: candidate-pool scaling diagnostic

28 September 2026, declared while phase-2 fixed-reader confirmation is running.
No new training, no participant messages, no change to phase-2 frozen methods.
Use its frozen semantic energy to test whether the negative result for continuous
inference was merely a consequence of twenty candidates.

Use four PREVIOUSLY SEEN development questions at indices 12–15. Keep each original
twenty-paragraph pool, then add exact-text-deduplicated distractors drawn from the
other development pools, in seeded order, to reach 40, 80 and 160. This is a
constructed supplied-pool scaling stress test, not a fresh QA/transfer result.
All source paragraph IDs/hashes and borrowed embeddings remain traceable. Original
gold supports remain reachable; other paragraphs may incidentally help.

Generalize the same visible lexical features from N=20 to N candidates, retaining
their definitions and normalization by pool size. Verify N=20 features and score
coefficients against phase 2 before any comparison. Frozen query/document/title
embeddings are reused, with zero new encoder calls; this is ordinary representation
reuse, not uncharged original construction. Selection budget remains four.

Compare chunked exact enumeration, beam width 16 and the same four-restart,
80-step projected gradient procedure with discrete swap refinement. Global score
gap, annotated support recovery and native search costs are distinct. Count
enumerated subsets, partial-set scores, analytic gradient steps and swaps. Report
coefficient/feature construction separately. No LLM calls are needed to identify
a computational crossover; any such result is not a complete-task advantage.

No parameter or search tuning after results. This diagnostic uses only development
material and cannot increase the fresh confirmation sample. CPU work may run while
the serial GPU reader uses the shared host: record that circumstance and avoid
precise hardware-speedup claims from one timing pass. If a simple discrete method
matches the optimum cheaply, retain that result without searching for a neural win.
