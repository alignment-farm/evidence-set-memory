# Phase 2: natural-text set energies, 28 September 2026

User authorized continued experimentation beyond the initial direction, ample
resources and autonomous execution. Investigator remains gpt-6-astra; active
turn metadata now records reasoning **high** (phase 1 was medium), OpenAI/Codex
0.158.0. Starting revision ad01b74421d2297356ba92bd67584e1667cb4fdf, clean.

Adopt the author-linked MuSiQue-Ans raw dev asset for a bounded natural-text
mechanism experiment. Acquire the complete file, hash it, and keep the raw file
in ignored cache. Save partition IDs, hashes and source metadata. Train, develop
and confirm on disjoint underlying single-hop IDs; exclude overlapping composed
questions. Strip support flags, decomposition, retrieval scores and answers from
selector inputs. Label files stay separate. Use a fixed four-paragraph selection
budget without gold hop count. The source pool is the public twenty paragraphs;
this does not test open-corpus candidate discovery.

This is **static benchmark supervision**, not a continuing agent life history.
It broadens the mechanism inquiry from authored explicit links to real prose.
No claims of acquired cross-session experience or maintenance follow merely by
ordering these questions. Pretraining contamination of the downstream reader is
possible; no-context and omitted-support diagnostics are required.

Fit a small neural structured energy with query-conditioned unary and pairwise
terms over visible text features. Initial representation uses lexical relevance,
query/title coverage, document overlap and title mentions; semantic representation
is an eligible diagnostic if lexical acquisition fails. Separate persistent
network training from optimizing relaxed selection variables. Compare conventional
pointwise learning, ordinary lexical/set-aware policies and global discrete search
on the same acquired energy. Explore projected gradient ascent of score (negative
energy descent), rounding, multistart and discrete repair. Count every restart,
gradient iteration, score evaluation and rounding/refinement step.

First establish training acquisition and development generalization, preserving
failures. Diagnose objective, representation or search failure separately. Use
development only to choose the ordinary policy and the neural checkpoint/search
configuration. Freeze the implementation/checkpoint/claim before loading fresh
confirmation inputs for selection. Then measure complete QA with one fixed reader
and answer/support metrics, all-evidence, no-context and omitted-support controls.
Keep ordinary broad fallback and cached identical reader contexts available.
Use supplied benchmark labels only for training/evaluation; no confirmation answer
or support annotations may enter the deployed selector or reader.

Initial bounds: up to 256 training questions, 48 development questions, 64 fresh
confirmation questions; adjust only for component-disjoint availability and record
the actual split. Reader initially uses 12 development and 24 confirmation
questions, at most 240 unique serial calls. Do not parallelize serving. Training
uses small CPU tensors and two CPU threads. Record native representation, training,
selection, reader, fallback and verification costs; unknown monetary costs remain
unknown. Preserve raw responses and source-version mappings.

Publish after an informative comparison and continue to a separately justified
chronological/correction experiment when the mechanism evidence warrants it.

Development asset amendment: first representation pass found three training rows
with 18/19 rather than 20 candidates. Preserve the failed attempt. Restrict this
fixed-size energy cohort to exactly 20 candidates AFTER the preassigned split,
recording excluded IDs. Selection is by visible size only, not labels/outcomes.

Development amendments: add frozen all-MiniLM-L6-v2 query/document/title similarities
as a representation diagnostic, also available to ordinary hybrid retrieval.
Preserve lexical code and runs. Reader's initial no-context source-only instruction
is replaced by an explicit prior-knowledge diagnostic before confirmation. Preserve
that first prompt/response version. Reader cohort is six development questions and
up to 24 confirmation questions; additional diagnostic development calls remain
charged. Adjust the cumulative call cap to 300 to accommodate the preserved first
development pass and revised development pass, with no parallel serving.

Reader development diagnosis: the 256-token free-text route sometimes ignored
the JSON instruction and truncated an explanation before its final answer.
Preserve that run; use supported JSON-object response formatting and 512 output
tokens in the next development pass. Freeze this interface before confirmation.

Second reader diagnosis: the serving route accepted but did not reliably enforce
JSON mode. Some complete responses contain valid final JSON after explanation.
The final reader extracts the last schema-valid answer/citations object without
interpreting prose; malformed/truncated objects still fail. Increase the final
allowance to 1,024 tokens. Preserve original responses and strict-parser results,
and check this public formatting repair on development before freezing.
