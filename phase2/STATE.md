# Persistent state, feedback and eligibility

This phase is a supervised mechanism test, not a simulated continuing life.
The first phase's authored executed-attempt/revision experiment is separate.

| State | Survives an investigator/session reset? | Updated by what? |
| --- | --- | --- |
| Versioned source identifiers, split manifests and raw reader traces | Yes, published files | Explicit acquisition and experiment scripts |
| Raw downloaded source archive and partition input/label files | Yes locally, ignored cache; recoverable by pinned hashes | Source acquisition/conversion, not the selector |
| MiniLM representations | Yes locally; rebuildable cache | Frozen encoder applied to visible question/title/body strings |
| Small specialist weights | Yes, published JSON checkpoints | Training support labels from the imported benchmark; selected with development annotations |
| Current selection variables and gradients | No persistent adaptation | Per-question inference on frozen coefficients; reset for every question |
| Primary-model conversation | No previous messages supplied | Independent requests with the current question and selected sources |
| Reader payload-reuse map | Only within the running process | Identical request hashes; raw requests/responses persist on disk |
| Serving KV cache and pretrained knowledge | Backend state/weights may persist | Not controlled as learned study memory; no claimed reset of physical serving caches |
| Investigator analysis and protocol revisions | Published notes, scripts, commits and traces persist | Human-equivalent study development, not participant-earned feedback |

Training consumes benchmark support annotations on 253 questions. Positive and
negative sets are constructed from these annotations and visible ordinary/random
proposals; their supervision is not the downstream reader's own success/failure.
Development annotations choose checkpoints and ordinary link weight. Reader
development traces motivate a public format parser and longer response allowance.
All such intervention predates the frozen confirmation methods.

Confirmation gold answers/support enter only evaluation and explicitly labeled
oracle/omission controls. They never update specialist weights, encoder weights,
ordinary hyperparameters, or deployable selected sets. The primary request for
each deployable arm has visible question/sources and shared scope instructions;
it contains no gold answer or support flags. The full-source fallback is triggered
by public inability/format/citation validity, not hidden evaluator correctness.

The whole published comparison can be replayed after an investigator reset
because its working artifacts persist. That reproducibility is **not** evidence
of experience-driven participant improvement across episodes. An earlier/later
experiment would additionally need eligible feedback acquired before the later
requirements, a frozen/no-new-feedback control, and outcomes on genuinely later
work or source revisions. This phase deliberately does not manufacture that
claim by ordering static questions.

The imported source paragraphs, ordinary representations, answer reuse where
available, full-context reading and public repair remain legitimate. No competitor
is denied current requirements, source code or scope rules to make learning win.
This source-pool QA task has no continuing answer artifact or revision log to
reuse; that is a workload limitation, not a prohibition on reuse in the study.
