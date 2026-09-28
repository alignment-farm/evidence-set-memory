# Development findings — published before confirmation

The natural-text extension has a working neural set energy. With 253 training
questions, the 578-parameter lexical model improves exact-search complete support
recovery from 77/253 at initialization to 112/253 after training; the pair-order
accuracy improves from 0.775 to 0.849. On 48 development questions, complete
recovery improves from 12/48 to 20/48. Labels are imported benchmark annotations,
not outcomes earned by a continuing agent. No confirmation result is available
at this publication boundary.

The strongest tried ordinary lexical/link policy and the learned unary ablation
each recover complete sets on 15/48 development questions. Exact and beam search
find the same maximum score in all 48 cases. Four-restart relaxed optimization
plus swap refinement reaches that maximum in 44/48. Relaxation alone reaches it
in 20/48, yet its complete-support count is 21/48 versus exact search's 20/48.
Thus maximizing the learned score and improving labeled sufficiency are already
empirically distinguishable. No score is a certificate.

On this twenty-candidate/four-selection problem, vectorized enumeration scores
232,560 sets across 48 questions in about 0.009 seconds; beam scores 28,507
partial sets in 0.045 seconds. Relaxation/refinement takes about 1.38 seconds,
including 15,360 analytic gradient steps and 5,632 discrete scores. These times
exclude shared coefficient-network construction and representation, are single
local measurements, and do not generalize to larger candidate pools.

Source acquisition revealed that three reserved training rows have fewer than
twenty candidates. The failed assertion is preserved. This cohort explicitly
excludes them using visible candidate count; no quality label drives exclusion.
All single-hop component IDs remain disjoint across the preassigned partitions.

Before freezing, two investigations remain: complete QA with the available larger
reader, and a frozen semantic-encoder diagnostic to test the limits of lexical
features. The latter gives embeddings to ordinary methods too and charges their
construction. The first reader pass's no-context condition still instructed
source-only answering; its zero-answer behavior is a refusal control, not a
pretraining-contamination test. A corrected no-context diagnostic explicitly
permits prior knowledge, and is fixed before confirmation. All earlier responses
and prompt revisions remain available.

See [protocol](PROTOCOL.md), [provenance](PROVENANCE.md),
[acquisition audit](runs/acquisition-audit.json), and
[seed-23 development comparison](runs/development-selection-seed23/summary.json).
